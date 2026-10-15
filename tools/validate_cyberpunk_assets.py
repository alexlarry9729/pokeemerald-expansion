#!/usr/bin/env python3
"""Validate palette files and the indexed art for the cyberpunk Lavaridge pass.

Run from the repository root:
    python3 tools/validate_cyberpunk_assets.py
"""
from __future__ import annotations

import argparse
from pathlib import Path
import binascii
import json
import struct
import sys
import zlib


def parse_palette(path: Path) -> list[tuple[int, int, int]]:
    lines = path.read_text(encoding="ascii").splitlines()
    if len(lines) < 3 or lines[0] != "JASC-PAL" or lines[1] != "0100":
        raise ValueError(f"{path}: expected a JASC-PAL 0100 header")

    try:
        expected = int(lines[2])
    except ValueError as exc:
        raise ValueError(f"{path}: invalid colour count {lines[2]!r}") from exc

    rows = [line.split() for line in lines[3:] if line.strip()]
    if len(rows) != expected:
        raise ValueError(
            f"{path}: header declares {expected} colours but found {len(rows)}"
        )

    colours: list[tuple[int, int, int]] = []
    for index, row in enumerate(rows):
        if len(row) != 3:
            raise ValueError(f"{path}: colour {index} must have exactly 3 channels")
        try:
            rgb = tuple(int(channel) for channel in row)
        except ValueError as exc:
            raise ValueError(f"{path}: colour {index} contains a non-integer") from exc
        if any(channel < 0 or channel > 255 for channel in rgb):
            raise ValueError(f"{path}: colour {index} has a channel outside 0..255")
        colours.append(rgb)  # type: ignore[arg-type]
    return colours


def parse_palette_mask(path: Path) -> list[int]:
    values: list[int] = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        value = line.partition("#")[0].strip()
        if not value:
            continue
        try:
            index = int(value, 10)
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: expected a decimal palette index") from exc
        if not 0 <= index <= 15:
            raise ValueError(f"{path}:{line_number}: palette index {index} is outside 0..15")
        values.append(index)
    return values


def validate_indexed_tileset_png(path: Path) -> list[list[int]]:
    """Validate PNG chunks, CRCs, data stream and the expected indexed 4bpp format."""
    data = path.read_bytes()
    if len(data) < 45 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: file is not a complete PNG")
    if data[12:16] != b"IHDR" or struct.unpack(">I", data[8:12])[0] != 13:
        raise ValueError(f"{path}: missing or malformed IHDR chunk")

    width, height = struct.unpack(">II", data[16:24])
    bit_depth, colour_type, compression, filter_method, interlace = data[24:29]
    if (width, height) != (128, 232):
        raise ValueError(
            f"{path}: expected 128×232 tile atlas, found {width}×{height}"
        )
    if bit_depth != 4 or colour_type != 3:
        raise ValueError(
            f"{path}: expected a 4-bit indexed PNG, found bit depth {bit_depth}, "
            f"colour type {colour_type}"
        )
    if (compression, filter_method, interlace) != (0, 0, 0):
        raise ValueError(f"{path}: unsupported PNG compression/filter/interlace mode")

    offset = 8
    palette_entries: int | None = None
    idat_chunks: list[bytes] = []
    found_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError(f"{path}: truncated PNG chunk header")
        chunk_length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        chunk_end = offset + 12 + chunk_length
        if chunk_end > len(data):
            raise ValueError(f"{path}: truncated {chunk_type.decode('ascii', 'replace')} chunk")
        chunk_data = data[offset + 8:offset + 8 + chunk_length]
        expected_crc = struct.unpack(">I", data[offset + 8 + chunk_length:chunk_end])[0]
        actual_crc = binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"{path}: CRC mismatch in {chunk_type.decode('ascii', 'replace')} chunk")

        if chunk_type == b"PLTE":
            if chunk_length % 3 or chunk_length // 3 != 16:
                raise ValueError(f"{path}: expected exactly 16 indexed palette colours")
            palette_entries = chunk_length // 3
        elif chunk_type == b"IDAT":
            idat_chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            if chunk_length != 0:
                raise ValueError(f"{path}: IEND chunk must be empty")
            found_iend = True
            offset = chunk_end
            break
        offset = chunk_end

    if not found_iend or offset != len(data):
        raise ValueError(f"{path}: missing IEND chunk or contains trailing data")
    if palette_entries != 16:
        raise ValueError(f"{path}: missing 16-colour PLTE chunk")
    if not idat_chunks:
        raise ValueError(f"{path}: missing PNG image data")

    try:
        raw = zlib.decompress(b"".join(idat_chunks))
    except zlib.error as exc:
        raise ValueError(f"{path}: invalid compressed image data: {exc}") from exc

    row_bytes = (width * bit_depth + 7) // 8
    row_stride = row_bytes + 1  # one PNG filter byte per row
    if len(raw) != height * row_stride:
        raise ValueError(
            f"{path}: decoded image data has {len(raw)} bytes; "
            f"expected {height * row_stride}"
        )
    # Reverse PNG's byte-wise row filters, then unpack each 4bpp byte into two indices.
    # The atlas is indexed: these indices are later mapped through the per-map .pal files.
    pixels: list[list[int]] = []
    previous = bytearray(row_bytes)
    for row in range(height):
        raw_offset = row * row_stride
        filter_type = raw[raw_offset]
        if filter_type not in range(5):
            raise ValueError(f"{path}: invalid PNG filter {filter_type} on row {row}")
        scanline = bytearray(raw[raw_offset + 1:raw_offset + 1 + row_bytes])
        for i in range(row_bytes):
            left = scanline[i - 1] if i else 0
            up = previous[i]
            upper_left = previous[i - 1] if i else 0
            if filter_type == 1:  # Sub
                predictor = left
            elif filter_type == 2:  # Up
                predictor = up
            elif filter_type == 3:  # Average
                predictor = (left + up) // 2
            elif filter_type == 4:  # Paeth
                estimate = left + up - upper_left
                distance_left = abs(estimate - left)
                distance_up = abs(estimate - up)
                distance_upper_left = abs(estimate - upper_left)
                if distance_left <= distance_up and distance_left <= distance_upper_left:
                    predictor = left
                elif distance_up <= distance_upper_left:
                    predictor = up
                else:
                    predictor = upper_left
            else:  # None
                predictor = 0
            scanline[i] = (scanline[i] + predictor) & 0xFF

        decoded_row: list[int] = []
        for packed in scanline:
            decoded_row.extend((packed >> 4, packed & 0x0F))
        pixels.append(decoded_row)
        previous = scanline
    return pixels


def luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = rgb
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue



# The two original points illuminate the Centre and Mart signage. The added
# points give each Lavaridge building a restrained facade/window glow anchor.
EXPECTED_LAVARIDGE_LIGHTS = {
    (11, 6): "LIGHT_TYPE_PKMN_CENTER_SIGN",
    (17, 5): "LIGHT_TYPE_POKE_MART_SIGN",
    (8, 6): "LIGHT_TYPE_FACADE",
    (14, 5): "LIGHT_TYPE_FACADE",
    (4, 15): "LIGHT_TYPE_FACADE",
    (6, 15): "LIGHT_TYPE_FACADE",
    (11, 15): "LIGHT_TYPE_FACADE",
    (13, 15): "LIGHT_TYPE_FACADE",
    (15, 15): "LIGHT_TYPE_FACADE",
    (17, 15): "LIGHT_TYPE_FACADE",
}


def validate_lavaridge_light_events(root: Path) -> list[str]:
    errors: list[str] = []
    map_path = root / "data/maps/LavaridgeTown/map.json"
    layouts_path = root / "data/layouts/layouts.json"

    try:
        map_data = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{map_path}: unable to parse Lavaridge map JSON: {exc}"]

    try:
        layouts_data = json.loads(layouts_path.read_text(encoding="utf-8"))
        layout = next(
            item for item in layouts_data["layouts"]
            if item.get("id") == map_data.get("layout")
        )
        width, height = int(layout["width"]), int(layout["height"])
    except (OSError, json.JSONDecodeError, KeyError, StopIteration, TypeError, ValueError) as exc:
        errors.append(f"{layouts_path}: unable to resolve Lavaridge layout dimensions: {exc}")
        width = height = 0

    object_events = map_data.get("object_events")
    if not isinstance(object_events, list):
        return errors + [f"{map_path}: object_events must be a list"]

    lights = [
        event for event in object_events
        if event.get("graphics_id") == "OBJ_EVENT_GFX_LIGHT_SPRITE"
    ]
    seen: dict[tuple[int, int], dict] = {}
    valid_types = {"LIGHT_TYPE_PKMN_CENTER_SIGN", "LIGHT_TYPE_POKE_MART_SIGN", "LIGHT_TYPE_FACADE"}

    for event in lights:
        x, y = event.get("x"), event.get("y")
        if not isinstance(x, int) or not isinstance(y, int):
            errors.append(f"{map_path}: light event has non-integer coordinates")
            continue
        coord = (x, y)
        if coord in seen:
            errors.append(f"{map_path}: duplicate light sprites at ({x}, {y})")
        seen[coord] = event
        if not (0 <= x < width and 0 <= y < height):
            errors.append(
                f"{map_path}: light at ({x}, {y}) is outside the {width}x{height} layout"
            )
        light_type = event.get("trainer_sight_or_berry_tree_id")
        if light_type not in valid_types:
            errors.append(f"{map_path}: unsupported light type {light_type!r} at ({x}, {y})")
        if event.get("movement_type") != "MOVEMENT_TYPE_NONE" or event.get("script") != "NULL":
            errors.append(
                f"{map_path}: visual light at ({x}, {y}) must be stationary and script-free"
            )

    expected_coords = set(EXPECTED_LAVARIDGE_LIGHTS)
    observed_coords = set(seen)
    for coord, expected_type in EXPECTED_LAVARIDGE_LIGHTS.items():
        event = seen.get(coord)
        if event is None:
            errors.append(f"{map_path}: missing facade/window light at {coord}")
        elif event.get("trainer_sight_or_berry_tree_id") != expected_type:
            errors.append(
                f"{map_path}: light at {coord} should use {expected_type}, "
                f"found {event.get('trainer_sight_or_berry_tree_id')!r}"
            )
    for coord in sorted(observed_coords - expected_coords):
        errors.append(f"{map_path}: unexpected light event at {coord}; update the expected placement set")

    if len(lights) != len(EXPECTED_LAVARIDGE_LIGHTS):
        errors.append(
            f"{map_path}: expected {len(EXPECTED_LAVARIDGE_LIGHTS)} light events, found {len(lights)}"
        )
    return errors


SIGN_LIGHT_TYPES = {
    "LIGHT_TYPE_PKMN_CENTER_SIGN",
    "LIGHT_TYPE_POKE_MART_SIGN",
    "LIGHT_TYPE_FACADE",
}


def validate_sign_light_placements(root: Path) -> list[str]:
    """Ensure town-sign/facade light anchors resolve to visible map cells."""
    errors: list[str] = []
    layouts_path = root / "data/layouts/layouts.json"
    try:
        layouts_data = json.loads(layouts_path.read_text(encoding="utf-8"))
        layouts = {
            item.get("id"): item
            for item in layouts_data.get("layouts", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        return [f"{layouts_path}: unable to load layouts for sign-light placement checks: {exc}"]

    maps_root = root / "data/maps"
    for map_path in sorted(maps_root.rglob("map.json")):
        try:
            map_data = json.loads(map_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{map_path}: unable to inspect sign-light placements: {exc}")
            continue

        object_events = map_data.get("object_events", [])
        if not isinstance(object_events, list):
            continue
        lights = [
            event for event in object_events
            if isinstance(event, dict)
            and event.get("graphics_id") == "OBJ_EVENT_GFX_LIGHT_SPRITE"
            and event.get("trainer_sight_or_berry_tree_id") in SIGN_LIGHT_TYPES
        ]
        if not lights:
            continue

        layout_id = map_data.get("layout")
        layout = layouts.get(layout_id)
        if layout is None:
            errors.append(f"{map_path}: cannot resolve layout {layout_id!r} for sign-light placements")
            continue
        try:
            width, height = int(layout["width"]), int(layout["height"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"{map_path}: invalid layout dimensions for {layout_id!r}: {exc}")
            continue

        seen: set[tuple[int, int]] = set()
        for event in lights:
            x, y = event.get("x"), event.get("y")
            if type(x) is not int or type(y) is not int:
                errors.append(f"{map_path}: sign/facade light has non-integer coordinates ({x!r}, {y!r})")
                continue
            coord = (x, y)
            if coord in seen:
                errors.append(f"{map_path}: duplicate sign/facade lights at ({x}, {y})")
            seen.add(coord)
            if not (0 <= x < width and 0 <= y < height):
                errors.append(
                    f"{map_path}: sign/facade light at ({x}, {y}) is outside the {width}x{height} layout"
                )
            if event.get("movement_type") != "MOVEMENT_TYPE_NONE" or event.get("script") != "NULL":
                errors.append(
                    f"{map_path}: sign/facade light at ({x}, {y}) must be stationary and script-free"
                )
    return errors


def validate_lavaridge_map_access(root: Path) -> list[str]:
    """Guard the town's original exits, hot-spring trigger, and hidden item."""
    errors: list[str] = []
    map_path = root / "data/maps/LavaridgeTown/map.json"
    try:
        map_data = json.loads(map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{map_path}: unable to parse map for access checks: {exc}"]

    expected_warps = {
        (12, 15, "MAP_LAVARIDGE_TOWN_HERB_SHOP", "0"),
        (5, 15, "MAP_LAVARIDGE_TOWN_GYM_1F", "0"),
        (15, 5, "MAP_LAVARIDGE_TOWN_MART", "0"),
        (9, 6, "MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F", "0"),
        (16, 15, "MAP_LAVARIDGE_TOWN_HOUSE", "0"),
        (9, 2, "MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F", "3"),
    }
    actual_warps = {
        (event.get("x"), event.get("y"), event.get("dest_map"), str(event.get("dest_warp_id")))
        for event in map_data.get("warp_events", [])
        if isinstance(event, dict)
    }
    if actual_warps != expected_warps:
        errors.append(f"{map_path}: original Lavaridge warp set changed; review exits before changing this baseline")

    expected_connections = [{"map": "MAP_ROUTE112", "offset": -40, "direction": "right"}]
    if map_data.get("connections") != expected_connections:
        errors.append(f"{map_path}: original Route 112 connection changed")

    triggers = [
        event for event in map_data.get("coord_events", [])
        if isinstance(event, dict)
        and event.get("script") == "LavaridgeTown_EventScript_HotSpringsTrigger"
    ]
    if len(triggers) != 1 or (triggers[0].get("x"), triggers[0].get("y")) != (6, 3):
        errors.append(f"{map_path}: original hot-springs trigger at (6, 3) is missing or moved")

    object_events = map_data.get("object_events", [])
    non_light_events = [
        event for event in object_events
        if isinstance(event, dict) and event.get("graphics_id") != "OBJ_EVENT_GFX_LIGHT_SPRITE"
    ] if isinstance(object_events, list) else []
    if len(non_light_events) != 9:
        errors.append(
            f"{map_path}: expected the 9 original non-light NPC/object events, found {len(non_light_events)}"
        )

    bg_events = map_data.get("bg_events", [])
    if not any(
        isinstance(event, dict)
        and event.get("type") == "hidden_item"
        and event.get("item") == "ITEM_ICE_HEAL"
        and (event.get("x"), event.get("y")) == (4, 5)
        for event in bg_events
    ):
        errors.append(f"{map_path}: original hidden Ice Heal at (4, 5) is missing")
    return errors


def validate_facade_light_wiring(root: Path) -> list[str]:
    """Catch source/asset regressions that a successful atlas check cannot see."""
    errors: list[str] = []
    required_markers = {
        "include/constants/event_objects.h": ("LIGHT_TYPE_FACADE",),
        "src/event_object_movement.c": (
            "case LIGHT_TYPE_FACADE:",
            "OBJ_EVENT_PAL_TAG_NEON_LIGHT_DAY",
            "OBJ_EVENT_PAL_TAG_NEON_LIGHT",
        ),
        "src/data/field_effects/field_effect_objects.h": (
            "gFieldEffectObjectTemplate_FacadeLight",
            "&gFieldEffectObjectTemplate_FacadeLight",
        ),
        "src/data/object_events/object_event_graphics.h": (
            "graphics/object_events/pics/misc/facade_light.png",
        ),
    }
    for relative_path, markers in required_markers.items():
        path = root / relative_path
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{path}: unable to read facade-light wiring source: {exc}")
            continue
        for marker in markers:
            if marker not in source:
                errors.append(f"{path}: missing required facade-light wiring marker {marker!r}")

    sprite_path = root / "graphics/object_events/pics/misc/facade_light.png"
    if not sprite_path.is_file():
        errors.append(f"{sprite_path}: missing generic facade/window light sprite")
    return errors


def validate_cuordilava_palette_pair(root: Path) -> list[str]:
    """Validate the private palette pair reserved for Cuordilava architecture."""
    errors: list[str] = []
    header_path = root / "src/data/tilesets/headers.h"
    palette_dir = root / "data/tilesets/secondary/lavaridge/palettes"
    try:
        header = header_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{header_path}: unable to inspect local palette-swap declaration: {exc}"]
    start = header.find("const struct Tileset gTileset_Lavaridge")
    end = header.find("\n};", start) if start >= 0 else -1
    block = header[start:end] if start >= 0 and end >= 0 else ""
    if ".swapPalettes = SWAP_PAL(12)," not in block:
        errors.append(f"{header_path}: reserved palette 12 must swap to palette 05 at night")
    if ".swapPalettes = SWAP_PAL(8)," in block:
        errors.append(f"{header_path}: shared palette 08 must not be globally swapped for this feature")
    try:
        day = parse_palette(palette_dir / "12.pal")
        night = parse_palette(palette_dir / "05.pal")
        for index in range(1, 9):
            if max(day[index]) > 110:
                errors.append(f"{palette_dir / '12.pal'}: structural colour {index} must stay dark")
        for index in range(9, 16):
            if luminance(night[index]) <= luminance(day[index]):
                errors.append(f"{palette_dir / '05.pal'}: local neon colour {index} must be brighter at night")
    except (OSError, ValueError, IndexError) as exc:
        errors.append(f"{palette_dir}: invalid Cuordilava day/night palette pair: {exc}")

    shared_baselines = {
        "07.pal": [
            (49, 49, 255), (238, 180, 139), (230, 148, 82), (197, 131, 74),
            (172, 98, 49), (131, 131, 139), (98, 98, 123), (65, 74, 106),
            (41, 49, 90), (131, 156, 197), (148, 180, 222), (246, 238, 238),
            (230, 222, 222), (197, 197, 148), (180, 172, 115), (115, 197, 164),
        ],
        "08.pal": [
            (49, 49, 255), (255, 255, 255), (0, 0, 0), (0, 0, 0),
            (197, 197, 172), (148, 148, 139), (98, 98, 123), (65, 74, 106),
            (41, 49, 90), (139, 205, 246), (115, 189, 238), (255, 230, 139),
            (222, 189, 98), (180, 156, 74), (139, 123, 32), (115, 82, 41),
        ],
    }
    for filename, expected in shared_baselines.items():
        path = palette_dir / filename
        try:
            if parse_palette(path) != expected:
                errors.append(f"{path}: shared palette changed; keep its original colours")
        except (OSError, ValueError) as exc:
            errors.append(f"{path}: unable to validate shared palette integrity: {exc}")
    return errors


def validate_facade_art_tiles(root: Path, path: Path, pixels: list[list[int]]) -> list[str]:
    """Check the warm windows and cool pipe trims on secondary tiles used by Lavaridge."""
    errors: list[str] = []
    window_tiles = (345, 346)
    facade_panel_tiles = (308, 326, 327, 338, 339)
    roof_seam_tiles = (343,)
    pipe_tiles = (312, 328, 344, 347)
    architecture_base_tiles = (164, 165, 180, 181, 168, 169, 184, 185, 348, 349, 360, 361, 376, 377, 392, 393, 396, 397, 412, 413)
    architecture_overlay_tiles = (166, 167, 182, 183, 170, 171, 186, 187, 230, 231, 246, 247, 350, 351, 362, 363, 378, 379, 394, 395, 398, 399, 414, 415)
    target_tiles = window_tiles + facade_panel_tiles + roof_seam_tiles + pipe_tiles + architecture_base_tiles + architecture_overlay_tiles

    # Ensure the art check covers tiles actually referenced by this map, not
    # unrelated atlas tiles that happen to contain neon-colored pixels.
    map_path = root / "data/layouts/LavaridgeTown/map.bin"
    metatiles_path = root / "data/tilesets/secondary/lavaridge/metatiles.bin"
    try:
        map_bytes = map_path.read_bytes()
        metatiles_bytes = metatiles_path.read_bytes()
    except OSError as exc:
        return [f"{path}: unable to inspect active Lavaridge metatiles: {exc}"]

    layouts_path = root / "data/layouts/layouts.json"
    map_json_path = root / "data/maps/LavaridgeTown/map.json"
    try:
        map_json = json.loads(map_json_path.read_text(encoding="utf-8"))
        layouts = json.loads(layouts_path.read_text(encoding="utf-8"))["layouts"]
        layout = next(item for item in layouts if item.get("id") == map_json.get("layout"))
        width, height = int(layout["width"]), int(layout["height"])
    except (OSError, json.JSONDecodeError, KeyError, StopIteration, TypeError, ValueError) as exc:
        return [f"{path}: unable to resolve Lavaridge layout for facade-art check: {exc}"]

    required_map_bytes = width * height * 2
    if len(map_bytes) < required_map_bytes:
        return [f"{map_path}: expected at least {required_map_bytes} bytes for {width}x{height} layout"]
    if len(metatiles_bytes) % 16:
        return [f"{metatiles_path}: metatile data length is not a multiple of 16 bytes"]

    active_secondary_tiles: set[int] = set()
    secondary_metatile_count = len(metatiles_bytes) // 16
    for cell_index in range(width * height):
        metatile_id = struct.unpack_from("<H", map_bytes, cell_index * 2)[0] & 0x3FF
        if metatile_id < 512:
            continue
        secondary_metatile_id = metatile_id - 512
        offset = secondary_metatile_id * 16
        if secondary_metatile_id >= secondary_metatile_count or offset + 16 > len(metatiles_bytes):
            errors.append(
                f"{map_path}: secondary metatile {secondary_metatile_id} at cell {cell_index} is out of range"
            )
            continue
        for tile_slot in range(8):
            tile_entry = struct.unpack_from("<H", metatiles_bytes, offset + tile_slot * 2)[0]
            tile_id = tile_entry & 0x3FF
            if tile_id >= 512:
                active_secondary_tiles.add(tile_id - 512)

    for tile_id in target_tiles:
        if tile_id not in active_secondary_tiles:
            errors.append(
                f"{path}: facade tile {tile_id} is not referenced by LavaridgeTown; check the art target"
            )
            continue
        tile_x = (tile_id % 16) * 8
        tile_y = (tile_id // 16) * 8
        indices = [
            pixels[y][x]
            for y in range(tile_y, tile_y + 8)
            for x in range(tile_x, tile_x + 8)
        ]
        if not any(index in range(9, 16) for index in indices):
            errors.append(f"{path}: active facade tile {tile_id} has no neon accent pixels (indices 9..15)")
        if tile_id in window_tiles + facade_panel_tiles and not any(index in (11, 12, 13, 14) for index in indices):
            errors.append(f"{path}: active window/panel tile {tile_id} is missing warm orange/red pixels")
        if tile_id in window_tiles + facade_panel_tiles and not any(index in (9, 10, 15) for index in indices):
            errors.append(f"{path}: active window/panel tile {tile_id} is missing cyan/purple trim pixels")
        if tile_id in window_tiles + facade_panel_tiles and 11 not in indices:
            errors.append(f"{path}: active window/panel tile {tile_id} is missing a warm amber highlight (index 11)")
        if tile_id in pipe_tiles and not any(index in (9, 10, 15) for index in indices):
            errors.append(f"{path}: pipe tile {tile_id} is missing a cool neon accent")
        if tile_id in (312, 328, 344) and 9 not in indices:
            errors.append(f"{path}: conduit tile {tile_id} is missing a bright cyan service LED (index 9)")
        if tile_id in roof_seam_tiles and 11 not in indices:
            errors.append(f"{path}: roof seam tile {tile_id} is missing a bright furnace-orange seam pixel (index 11)")

    # Keep the window mullions as visible dark breaks between repeated lit panes.
    mullion_columns = {345: 3, 346: 4}
    for tile_id, column in mullion_columns.items():
        tile_x = (tile_id % 16) * 8
        tile_y = (tile_id // 16) * 8
        rows = range(tile_y + 2, tile_y + 8) if tile_id == 315 else (
            range(tile_y + 1, tile_y + 6) if tile_id == 331 else range(tile_y + 2, tile_y + 6)
        )
        if any(pixels[y][tile_x + column] != 7 for y in rows):
            errors.append(f"{path}: window tile {tile_id} lost its dark metal mullion")

    # Two cool pixels define the maintenance LEDs on the exhaust-pipe tile.
    pipe_x = (347 % 16) * 8 + 4
    pipe_y = (347 // 16) * 8
    if pixels[pipe_y + 2][pipe_x] != 10 or pixels[pipe_y + 4][pipe_x] != 10:
        errors.append(f"{path}: exhaust-pipe tile 347 lost its cyan service LEDs")

    return errors


def validate_cuordilava_architecture_metatiles(root: Path) -> list[str]:
    """Protect the five custom Cuordilava facades from atlas/metatile regressions.

    These metatile IDs are unique to LavaridgeTown among layouts sharing the
    Lavaridge secondary tileset. Keep the shared Route 112 / Mt. Chimney /
    Magma Hideout architecture unaffected.
    """
    errors: list[str] = []
    metatiles_path = root / "data/tilesets/secondary/lavaridge/metatiles.bin"
    layouts_path = root / "data/layouts/layouts.json"
    expected_tiles = {
        165: (396, 397, 412, 413, 398, 399, 414, 415),
        173: (348, 349, 360, 361, 350, 351, 362, 363),
        174: (164, 165, 180, 181, 166, 167, 182, 183),
        179: (376, 377, 392, 393, 378, 379, 394, 395),
        181: (168, 169, 184, 185, 170, 171, 186, 187),
    }
    try:
        data = metatiles_path.read_bytes()
    except OSError as exc:
        return [f"{metatiles_path}: unable to inspect Cuordilava architecture metatiles: {exc}"]
    if len(data) % 16:
        errors.append(f"{metatiles_path}: metatile data length is not a multiple of 16 bytes")
        return errors

    for metatile_id, tile_ids in expected_tiles.items():
        offset = metatile_id * 16
        if offset + 16 > len(data):
            errors.append(f"{metatiles_path}: missing custom Cuordilava metatile {metatile_id}")
            continue
        for slot, expected_tile in enumerate(tile_ids):
            entry = struct.unpack_from("<H", data, offset + slot * 2)[0]
            encoded_tile = entry & 0x3FF
            palette_index = (entry >> 12) & 0xF
            if encoded_tile < 512 or encoded_tile - 512 != expected_tile or palette_index != 12:
                errors.append(
                    f"{metatiles_path}: Cuordilava metatile {metatile_id} slot {slot} "
                    f"must use secondary tile {expected_tile} with palette 12"
                )

    try:
        layouts = json.loads(layouts_path.read_text(encoding="utf-8"))["layouts"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return errors + [f"{layouts_path}: unable to inspect layouts for custom Cuordilava metatiles: {exc}"]

    counts = {metatile_id: 0 for metatile_id in expected_tiles}
    for layout in layouts:
        if not isinstance(layout, dict) or layout.get("secondary_tileset") != "gTileset_Lavaridge":
            continue
        layout_id = layout.get("id")
        name = layout.get("name", "")
        directory_name = name[:-7] if isinstance(name, str) and name.endswith("_Layout") else name
        map_path = root / "data/layouts" / directory_name / "map.bin"
        try:
            map_data = map_path.read_bytes()
            width, height = int(layout["width"]), int(layout["height"])
        except (OSError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{map_path}: unable to check custom Cuordilava metatile reuse: {exc}")
            continue
        required_bytes = width * height * 2
        if len(map_data) < required_bytes:
            errors.append(f"{map_path}: expected at least {required_bytes} bytes for {width}x{height} layout")
            continue
        for cell in range(width * height):
            map_entry = struct.unpack_from("<H", map_data, cell * 2)[0] & 0x3FF
            if map_entry < 512:
                continue
            metatile_id = map_entry - 512
            if metatile_id not in expected_tiles:
                continue
            if layout_id != "LAYOUT_LAVARIDGE_TOWN":
                errors.append(
                    f"{map_path}: custom Cuordilava metatile {metatile_id} is also used by {layout_id}"
                )
            else:
                counts[metatile_id] += 1

    for metatile_id, count in counts.items():
        if count == 0:
            errors.append(
                f"{root / 'data/layouts/LavaridgeTown/map.bin'}: custom architecture metatile {metatile_id} "
                "is not used by Cuordilava"
            )
    return errors


def validate_cuordilava_roof_vent_metatiles(root: Path) -> list[str]:
    """Guard the Cuordilava-only rooftop exhaust overlay on metatile 163."""
    errors: list[str] = []
    metatiles_path = root / "data/tilesets/secondary/lavaridge/metatiles.bin"
    layouts_path = root / "data/layouts/layouts.json"
    expected = (230, 231, 246, 247)
    try:
        data = metatiles_path.read_bytes()
    except OSError as exc:
        return [f"{metatiles_path}: unable to inspect Cuordilava rooftop vents: {exc}"]

    for metatile_id in (163,):
        offset = metatile_id * 16
        if offset + 16 > len(data):
            errors.append(f"{metatiles_path}: missing rooftop metatile {metatile_id}")
            continue
        for local_slot, tile_id in enumerate(expected, start=4):
            entry = struct.unpack_from("<H", data, offset + local_slot * 2)[0]
            encoded_tile = entry & 0x3FF
            palette_index = (entry >> 12) & 0xF
            if encoded_tile < 512 or encoded_tile - 512 != tile_id or palette_index != 12:
                errors.append(
                    f"{metatiles_path}: roof metatile {metatile_id} overlay slot {local_slot} "
                    f"must use secondary tile {tile_id} with palette 12"
                )

    try:
        layouts = json.loads(layouts_path.read_text(encoding="utf-8"))["layouts"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return errors + [f"{layouts_path}: unable to inspect shared layouts for rooftop vent reuse: {exc}"]

    counts = {metatile_id: 0 for metatile_id in (163,)}
    for layout in layouts:
        if not isinstance(layout, dict) or layout.get("secondary_tileset") != "gTileset_Lavaridge":
            continue
        name = layout.get("name", "")
        directory = name[:-7] if isinstance(name, str) and name.endswith("_Layout") else name
        map_path = root / "data/layouts" / directory / "map.bin"
        try:
            map_data = map_path.read_bytes()
            width, height = int(layout["width"]), int(layout["height"])
        except (OSError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"{map_path}: unable to check rooftop vent metatile reuse: {exc}")
            continue
        if len(map_data) < width * height * 2:
            errors.append(f"{map_path}: map data is too short for {width}x{height} layout")
            continue
        for cell in range(width * height):
            encoded = struct.unpack_from("<H", map_data, cell * 2)[0] & 0x3FF
            if encoded < 512 or encoded - 512 not in counts:
                continue
            mid = encoded - 512
            if layout.get("id") != "LAYOUT_LAVARIDGE_TOWN":
                errors.append(
                    f"{map_path}: Cuordilava-only rooftop metatile {mid} is also used by {layout.get('id')}"
                )
            else:
                counts[mid] += 1
    for mid, count in counts.items():
        if not count:
            errors.append(f"{root / 'data/layouts/LavaridgeTown/map.bin'}: rooftop metatile {mid} is not used by Cuordilava")
    return errors


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_lavaridge_light_events(root))
    errors.extend(validate_sign_light_placements(root))
    errors.extend(validate_lavaridge_map_access(root))
    errors.extend(validate_cuordilava_palette_pair(root))
    errors.extend(validate_cuordilava_architecture_metatiles(root))
    errors.extend(validate_cuordilava_roof_vent_metatiles(root))
    errors.extend(validate_facade_light_wiring(root))
    palette_dir = root / "data/tilesets/secondary/lavaridge/palettes"
    object_palette_dir = root / "graphics/object_events/palettes"
    tiles_png = root / "data/tilesets/secondary/lavaridge/tiles.png"

    palette_paths = sorted(palette_dir.glob("*.pal"))
    mask_paths = sorted(palette_dir.glob("*.pla"))
    neon_night = object_palette_dir / "neon_light.pal"
    neon_day = object_palette_dir / "neon_light_day.pal"

    try:
        decoded_pixels = validate_indexed_tileset_png(tiles_png)
        errors.extend(validate_facade_art_tiles(root, tiles_png, decoded_pixels))
    except (OSError, ValueError, struct.error, IndexError) as exc:
        errors.append(str(exc))

    for path in palette_paths + [p for p in (neon_night, neon_day) if p.exists()]:
        try:
            colours = parse_palette(path)
            if path in (neon_night, neon_day) and len(colours) != 16:
                raise ValueError(f"{path}: object-event light palettes must have 16 colours")
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    for path in mask_paths:
        try:
            parse_palette_mask(path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if not neon_night.is_file():
        errors.append(f"Missing expected night palette: {neon_night}")
    if not neon_day.is_file():
        errors.append(f"Missing expected day palette: {neon_day}")

    if neon_night.is_file() and neon_day.is_file():
        try:
            night = parse_palette(neon_night)
            day = parse_palette(neon_day)
            # Entries 1..6 form the cool neon ramp; 8..12 form the hot glow ramp.
            for index in (*range(1, 7), *range(8, 13)):
                if luminance(day[index]) >= luminance(night[index]):
                    errors.append(
                        f"{neon_day}: colour {index} is not dimmer than its night counterpart"
                    )
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if not palette_paths:
        errors.append(f"No Lavaridge palette files found under {palette_dir}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="pokeemerald-expansion repository root",
    )
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Cyberpunk asset validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(
        "Cyberpunk asset validation passed: indexed Lavaridge PNG, reserved Cuordilava palettes, "
        "day/night ramps, and Lavaridge facade-light placements look valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
