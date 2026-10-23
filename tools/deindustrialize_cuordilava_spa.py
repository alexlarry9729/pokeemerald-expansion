#!/usr/bin/env python3
"""Convert spring-only industrial art to mineral water and natural basalt.

A late source-only graphics patch for Cuordilava's existing, private metatiles.
The target IDs are located *exclusively* in the hot spring area. No layout cells,
collision/elevation bits, behavior attributes, events, palettes, or 8x8 art
sheets change. Other towns continue using their untouched shared tilesets.
"""
from pathlib import Path
import struct

# Each target is one secondary metatile and its precise allowed map locations.
POOL = {
    163: {(3, 3), (5, 3), (6, 3), (4, 5)},
    187: {(3, 4), (6, 4)},
    188: {(4, 3), (5, 5)},
    285: {(4, 4), (5, 4)},
}
BASALT = {165: {(7, 3), (7, 4)}}
TILES = (320, 321, 336)  # dedicated existing hot-spring water graphics
# Distinct 2x2 water currents, reusing existing turquoise/foam 8x8 tiles.
WATER_ARRANGEMENTS = {
    163: (336, 320, 321, 336),
    187: (320, 336, 336, 321),
    188: (336, 321, 320, 336),
    285: (321, 336, 336, 320),
}


def paths(root):
    root = Path(root)
    return (root / 'data/layouts/LavaridgeTown/map.bin',
            root / 'data/tilesets/secondary/cuordilava/metatiles.bin',
            root / 'data/tilesets/secondary/cuordilava/metatile_attributes.bin')


def u16(data, off):
    return struct.unpack_from('<H', data, off)[0]


def actual_places(layout, mid):
    return {(i % 20, i // 20) for i in range(400)
            if (u16(layout, i * 2) & 0x3FF) == 512 + mid}


def expected_graphics(meta):
    # A single verified rock-boundary donor, already in the existing pool
    # bank at x=6 y=6 (secondary metatile 180).
    rocks = list(struct.unpack_from('<8H', meta, 180 * 16))
    if any(value >> 12 != 8 for value in rocks):
        raise ValueError('Natural shoreline donor no longer uses water/rock palette 8')
    result = {165: rocks}
    for mid, order in WATER_ARRANGEMENTS.items():
        result[mid] = [(8 << 12) | (512 + tid) for tid in order] + [0, 0, 0, 0]
    return result


def validate_built(root):
    layout_path, meta_path, attr_path = paths(root)
    layout, meta, attrs = (p.read_bytes() for p in (layout_path, meta_path, attr_path))
    if (len(layout), len(meta), len(attrs)) != (800, 8192, 1024):
        raise ValueError('Cuordilava must retain exactly 20x20 cells and 512 private metatiles')
    shapes = expected_graphics(meta)
    for mid, coords in {**POOL, **BASALT}.items():
        if actual_places(layout, mid) != coords:
            raise ValueError(f'Hot-spring metatile {mid} leaked outside its expected cells')
        values = list(struct.unpack_from('<8H', meta, mid * 16))
        if values != shapes[mid]:
            raise ValueError(f'Hot-spring metatile {mid} lost turquoise/rock scenery')


def run(root):
    layout_path, meta_path, attr_path = paths(root)
    layout, original, attrs = (p.read_bytes() for p in (layout_path, meta_path, attr_path))
    if (len(layout), len(original), len(attrs)) != (800, 8192, 1024):
        raise ValueError('Unexpected Cuordilava geometry / tileset size')
    graphics = expected_graphics(original)
    for mid, coords in {**POOL, **BASALT}.items():
        actual = actual_places(layout, mid)
        if actual != coords:
            raise ValueError(f'Unsafe spring art reuse for metatile {mid}: {sorted(actual)}')
        if len(graphics[mid]) != 8:
            raise ValueError('Invalid 16x16 art length')
    art = bytearray(original)
    for mid, graphic in graphics.items():
        struct.pack_into('<8H', art, mid * 16, *graphic)
    # Other 507 metatiles must be exactly byte-for-byte unchanged.
    for mid in range(512):
        if mid not in graphics and art[mid*16:(mid+1)*16] != original[mid*16:(mid+1)*16]:
            raise ValueError('Unexpected spill outside thermal district')
    meta_path.write_bytes(art)
    validate_built(root)
    if layout_path.read_bytes() != layout or attr_path.read_bytes() != attrs:
        raise ValueError('Thermal art pass must NEVER change walkability / map cells')
    print('Cuordilava thermal basin: 4 water metatiles and one basalt-bank '
          'metatile redrawn only via existing indexed graphics; zero map/collision changes')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
