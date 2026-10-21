#!/usr/bin/env python3
"""Render a layout-only Cuordilava day/night preview from the real 4bpp tilesets.

Palette RGB values are rendered as authored; no global colour grading is applied,
so the preview cannot make unrelated tiles look cyberpunk by recolouring them.
This is a diagnostic renderer, not an emulator screenshot: animation frame zero is
composited for water, lava, steam and flowers, and the Pokémon Center, Poké Mart and
facade light sprites use their real day/night palettes. NPCs, weather, shadows and
engine scanline effects are intentionally omitted.
"""
from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


def png_indexed(path: Path) -> tuple[int, int, list[list[int]]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos = 8
    width = height = depth = colour_type = None
    compressed = bytearray()
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError(f"{path}: truncated PNG chunk")
        length = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        if len(payload) != length:
            raise ValueError(f"{path}: truncated {kind!r} chunk")
        crc_expected = struct.unpack_from(">I", data, pos + 8 + length)[0]
        crc_actual = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if crc_actual != crc_expected:
            raise ValueError(f"{path}: CRC mismatch in {kind.decode('ascii', 'replace')}")
        if kind == b"IHDR":
            width, height, depth, colour_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if compression != 0 or filtering != 0 or interlace != 0:
                raise ValueError(f"{path}: unsupported PNG compression/filter/interlace")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
        pos += 12 + length
    if width is None or height is None or depth != 4 or colour_type != 3:
        raise ValueError(f"{path}: expected 4bpp indexed PNG, got depth={depth}, type={colour_type}")
    row_bytes = (width * depth + 7) // 8
    stride = row_bytes + 1
    raw = zlib.decompress(bytes(compressed))
    if len(raw) != height * stride:
        raise ValueError(f"{path}: decompressed length {len(raw)} != {height * stride}")
    pixels: list[list[int]] = []
    previous = bytearray(row_bytes)
    for y in range(height):
        off = y * stride
        method = raw[off]
        scan = bytearray(raw[off + 1:off + stride])
        if method not in (0, 1, 2, 3, 4):
            raise ValueError(f"{path}: invalid row filter {method}")
        for x in range(row_bytes):
            left = scan[x - 1] if x else 0
            above = previous[x]
            upper_left = previous[x - 1] if x else 0
            if method == 1:
                predictor = left
            elif method == 2:
                predictor = above
            elif method == 3:
                predictor = (left + above) // 2
            elif method == 4:
                estimate = left + above - upper_left
                dl, da, dul = abs(estimate - left), abs(estimate - above), abs(estimate - upper_left)
                predictor = left if dl <= da and dl <= dul else above if da <= dul else upper_left
            else:
                predictor = 0
            scan[x] = (scan[x] + predictor) & 0xFF
        row: list[int] = []
        for byte in scan:
            row.extend((byte >> 4, byte & 0x0F))
        pixels.append(row[:width])
        previous = scan
    return width, height, pixels


def overlay_animation_tiles(
    atlas: tuple[int, int, list[list[int]]],
    frame_path: Path,
    start_tile: int,
) -> None:
    """Apply an engine animation frame to an 8x8 tile atlas for faithful previews.

    Animation PNGs are packed tightly in their source image, while the runtime writes
    their individual tiles sequentially into the GBA character block. Copy tile-by-tile
    instead of pasting the source rectangle into the atlas.
    """
    atlas_width, atlas_height, atlas_pixels = atlas
    frame_width, frame_height, frame_pixels = png_indexed(frame_path)
    if frame_width % 8 or frame_height % 8 or atlas_width % 8 or atlas_height % 8:
        raise ValueError(f"{frame_path}: animation and atlas dimensions must be multiples of 8")
    source_tiles_w = frame_width // 8
    tile_count = source_tiles_w * (frame_height // 8)
    atlas_tiles_w = atlas_width // 8
    for tile_offset in range(tile_count):
        destination_tile = start_tile + tile_offset
        destination_x = (destination_tile % atlas_tiles_w) * 8
        destination_y = (destination_tile // atlas_tiles_w) * 8
        if destination_y + 8 > atlas_height:
            raise ValueError(f"{frame_path}: animation exceeds atlas at tile {destination_tile}")
        source_x = (tile_offset % source_tiles_w) * 8
        source_y = (tile_offset // source_tiles_w) * 8
        for row in range(8):
            atlas_pixels[destination_y + row][destination_x:destination_x + 8] = (
                frame_pixels[source_y + row][source_x:source_x + 8]
            )


def read_palette(path: Path) -> list[tuple[int, int, int]]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    if len(lines) < 19 or lines[0] != "JASC-PAL" or lines[1] != "0100" or int(lines[2]) != 16:
        raise ValueError(f"{path}: expected a 16-colour JASC-PAL")
    result = []
    for line in lines[3:19]:
        fields = line.split()
        if len(fields) != 3:
            raise ValueError(f"{path}: invalid palette entry {line!r}")
        rgb = tuple(int(value) for value in fields)
        if any(value < 0 or value > 255 for value in rgb):
            raise ValueError(f"{path}: RGB value outside 0..255")
        result.append(rgb)
    return result


def pack_png(path: Path, width: int, height: int, rgb: bytearray) -> None:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    scanlines = bytearray()
    stride = width * 3
    for y in range(height):
        scanlines.append(0)
        scanlines.extend(rgb[y * stride:(y + 1) * stride])
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    content = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(scanlines), 9)) + chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def select_bg_palette(
    index: int,
    primary_palettes: dict[int, list[tuple[int, int, int]]],
    secondary_palettes: dict[int, list[tuple[int, int, int]]],
) -> list[tuple[int, int, int]]:
    """Select the globally loaded GBA background palette bank, not the tile art source.

    Emerald loads palette banks 0..5 from the primary tileset and 6..15
    from the secondary tileset. A secondary metatile can legitimately
    reference primary tile artwork with palette bank 8 (the hot springs);
    switching palette *source* on the tile's 512 boundary makes it black.
    """
    if not 0 <= index < 16:
        raise ValueError(f"Invalid BG palette bank {index}")
    return (primary_palettes if index < 6 else secondary_palettes)[index]


def palettes_for(mode: str, palette_dir: Path, tileset: str) -> dict[int, list[tuple[int, int, int]]]:
    """Load palette colours from the matching tileset, never mix primary and secondary palettes."""
    palettes: dict[int, list[tuple[int, int, int]]] = {}
    for index in range(16):
        source_index = index
        if tileset == "secondary" and index == 6 and mode == "night":
            source_index = 15
        elif tileset == "primary" and mode == "night" and 1 <= index <= 5:
            # General palette companion banks (x + 9) supply Cuordilava's warm night pass.
            source_index = index + 9
        palettes[index] = read_palette(palette_dir / f"{source_index:02d}.pal")
    return palettes


def render(mode: str, output: Path, layout: dict, root: Path) -> None:
    primary_dir = root / "data/tilesets/primary/general"
    primary_palette_dir = root / "data/tilesets/primary/cuordilava/palettes"
    secondary_dir = root / "data/tilesets/secondary/cuordilava"
    primary_png = png_indexed(primary_palette_dir.parent / "tiles.png")
    secondary_png = png_indexed(secondary_dir / "tiles.png")

    # These tile ranges are rewritten by the game engine's animation callbacks.
    # A static atlas leaves water/lava/steam placeholders looking black, so render
    # a real source frame into the matching sequential tile IDs for the preview.
    for animation, tile_start in (
        ("flower", 508),
        ("water", 432),
        ("sand_water_edge", 464),
        ("land_water_edge", 480),
        ("waterfall", 496),
    ):
        overlay_animation_tiles(
            primary_png,
            primary_dir / "anim" / animation / "0.png",
            tile_start,
        )
    overlay_animation_tiles(
        secondary_png,
        root / "data/tilesets/secondary/cave/anim/lava/0.png",
        160,
    )
    overlay_animation_tiles(
        secondary_png,
        secondary_dir / "anim/steam/0.png",
        288,
    )
    overlay_animation_tiles(
        secondary_png,
        secondary_dir / "anim/steam/2.png",
        292,
    )
    primary_metatiles = (primary_dir / "metatiles.bin").read_bytes()
    secondary_metatiles = (secondary_dir / "metatiles.bin").read_bytes()
    layout_dir = root / "data/layouts" / layout["name"].removesuffix("_Layout")
    map_data = (layout_dir / "map.bin").read_bytes()
    width, height = int(layout["width"]), int(layout["height"])
    cell_count = width * height
    if len(map_data) < cell_count * 2:
        raise ValueError(f"{layout_dir / 'map.bin'}: too short for {width}x{height}")
    primary_palettes = palettes_for(mode, primary_palette_dir, "primary")
    secondary_palettes = palettes_for(mode, secondary_dir / "palettes", "secondary")
    out_w, out_h = width * 16, height * 16
    canvas = bytearray(out_w * out_h * 3)

    for cell in range(cell_count):
        map_entry = struct.unpack_from("<H", map_data, cell * 2)[0]
        encoded_meta = map_entry & 0x3FF
        meta_is_secondary = encoded_meta >= 512
        meta_id = encoded_meta - 512 if meta_is_secondary else encoded_meta
        meta_bytes = secondary_metatiles if meta_is_secondary else primary_metatiles
        if (meta_id + 1) * 16 > len(meta_bytes):
            raise ValueError(f"Invalid metatile {meta_id} at cell {cell}")
        cell_x, cell_y = cell % width, cell // width
        for slot in range(8):
            encoded = struct.unpack_from("<H", meta_bytes, meta_id * 16 + slot * 2)[0]
            tile_code = encoded & 0x3FF
            tile_is_secondary = tile_code >= 512
            tile_id = tile_code - 512 if tile_is_secondary else tile_code
            atlas_width, atlas_height, pixels = secondary_png if tile_is_secondary else primary_png
            if (tile_id + 1) * 8 > (atlas_width // 8) * atlas_height:
                raise ValueError(f"Invalid tile {tile_id} at metatile {meta_id}, slot {slot}")
            palette_index = (encoded >> 12) & 0xF
            # Palette bank assignment is independent from tile graphics origin.
            palette = select_bg_palette(palette_index, primary_palettes, secondary_palettes)
            hflip, vflip = bool(encoded & 0x400), bool(encoded & 0x800)
            origin_x = cell_x * 16 + (slot % 2) * 8
            origin_y = cell_y * 16 + ((slot % 4) // 2) * 8
            overlay = slot >= 4
            for py in range(8):
                sy = 7 - py if vflip else py
                atlas_y = (tile_id // 16) * 8 + sy
                if atlas_y >= atlas_height:
                    raise ValueError(f"Tile {tile_id} exceeds atlas height")
                for px in range(8):
                    sx = 7 - px if hflip else px
                    atlas_x = (tile_id % 16) * 8 + sx
                    colour_index = pixels[atlas_y][atlas_x]
                    if overlay and colour_index == 0:
                        continue
                    colour = palette[colour_index]
                    offset = ((origin_y + py) * out_w + origin_x + px) * 3
                    canvas[offset:offset + 3] = bytes(colour)

    # Composite the actual day/night light-object sprites. The Pokémon Center,
    # Poké Mart and facade use distinct indexed images in the game.
    map_name = layout["name"].removesuffix("_Layout")
    event_map = json.loads((root / "data/maps" / map_name / "map.json").read_text(encoding="utf-8"))
    light_sprite_paths = {
        "LIGHT_TYPE_PKMN_CENTER_SIGN": root / "graphics/object_events/pics/misc/poke_center_light.png",
        "LIGHT_TYPE_POKE_MART_SIGN": root / "graphics/object_events/pics/misc/mart_light.png",
        "LIGHT_TYPE_FACADE": root / "graphics/object_events/pics/misc/facade_light.png",
    }
    light_sprites = {
        light_type: png_indexed(path)
        for light_type, path in light_sprite_paths.items()
    }
    light_palette_name = "neon_light_day.pal" if mode == "day" else "neon_light.pal"
    light_palette = read_palette(root / "graphics/object_events/palettes" / light_palette_name)
    for event in event_map.get("object_events", []):
        if event.get("graphics_id") != "OBJ_EVENT_GFX_LIGHT_SPRITE":
            continue
        light_type = event.get("trainer_sight_or_berry_tree_id")
        sprite_data = light_sprites.get(light_type)
        if sprite_data is None:
            continue
        light_width, light_height, light_pixels = sprite_data
        light_x = int(event.get("x", 0)) * 16
        light_y = int(event.get("y", 0)) * 16
        for py in range(light_height):
            dest_y = light_y + py
            if dest_y < 0 or dest_y >= out_h:
                continue
            for px in range(light_width):
                colour_index = light_pixels[py][px]
                if colour_index == 0:
                    continue
                dest_x = light_x + px
                if dest_x < 0 or dest_x >= out_w:
                    continue
                colour = light_palette[colour_index]
                offset = (dest_y * out_w + dest_x) * 3
                canvas[offset:offset + 3] = bytes(colour)

    scale = 3
    scaled = bytearray(out_w * scale * out_h * scale * 3)
    scaled_w = out_w * scale
    for y in range(out_h):
        src_row = y * out_w * 3
        for sy in range(scale):
            dst_row = (y * scale + sy) * scaled_w * 3
            for x in range(out_w):
                colour = canvas[src_row + x * 3:src_row + x * 3 + 3]
                for sx in range(scale):
                    dst = dst_row + (x * scale + sx) * 3
                    scaled[dst:dst + 3] = colour
    pack_png(output, scaled_w, out_h * scale, scaled)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("build-preview"))
    args = parser.parse_args()
    layouts = json.loads((ROOT / "data/layouts/layouts.json").read_text(encoding="utf-8"))["layouts"]
    layout = next(item for item in layouts if item.get("id") == "LAYOUT_LAVARIDGE_TOWN")
    render("day", args.output_dir / "cuordilava-day.png", layout, ROOT)
    render("night", args.output_dir / "cuordilava-night.png", layout, ROOT)
    print(f"Rendered Cuordilava day/night layout previews (including light sprites) for {layout['id']} to {args.output_dir}")


if __name__ == "__main__":
    main()
