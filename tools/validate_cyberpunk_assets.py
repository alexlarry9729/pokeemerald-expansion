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


def validate_indexed_tileset_png(path: Path) -> None:
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
    for row in range(height):
        filter_type = raw[row * row_stride]
        if filter_type not in range(5):
            raise ValueError(f"{path}: invalid PNG filter {filter_type} on row {row}")


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


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_lavaridge_light_events(root))
    palette_dir = root / "data/tilesets/secondary/lavaridge/palettes"
    object_palette_dir = root / "graphics/object_events/palettes"
    tiles_png = root / "data/tilesets/secondary/lavaridge/tiles.png"

    palette_paths = sorted(palette_dir.glob("*.pal"))
    mask_paths = sorted(palette_dir.glob("*.pla"))
    neon_night = object_palette_dir / "neon_light.pal"
    neon_day = object_palette_dir / "neon_light_day.pal"

    try:
        validate_indexed_tileset_png(tiles_png)
    except (OSError, ValueError, struct.error) as exc:
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
    if not mask_paths:
        errors.append(f"No Lavaridge palette masks found under {palette_dir}")

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
        "Cyberpunk asset validation passed: indexed Lavaridge PNG, palettes/masks, "
        "day/night ramps, and Lavaridge facade-light placements look valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
