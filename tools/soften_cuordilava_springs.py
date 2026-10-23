#!/usr/bin/env python3
"""Town-only late pass: soften the Cuordilava hot springs without new tiles.

After the scenery pass, replace four visually metallic spring cells with
existing mineral-water metatiles. Transform three single-use industrial rim
metatiles into a continuous basalt / palm / basalt bank. Copy only graphics:
behavior attributes, collisions, events, palettes, warps, lighting and the
20x20 footprint are not altered. Source prerequisites are fail-closed.
"""
from pathlib import Path
import struct

POOL = (((4, 4), 48, 56), ((5, 4), 49, 57),
        ((6, 4), 50, 58), ((7, 4), 51, 59))
RIM = (((2, 3), 75, 'rocks'), ((3, 3), 76, 'palm'),
       ((4, 3), 79, 'mirrored_rocks'))
BASALT, ROCK, PALM = 626 - 512, 690 - 512, 489

def u16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]

def tiles(data, metatile):
    return list(struct.unpack_from('<8H', data, 16 * metatile))

def files(root):
    root = Path(root)
    return (root / 'data/layouts/LavaridgeTown/map.bin',
            root / 'data/tilesets/secondary/cuordilava/metatiles.bin',
            root / 'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
            root / 'data/tilesets/primary/general/metatile_attributes.bin')

def expected_rim(meta):
    floor = tiles(meta, BASALT)[:4]
    rocks = tiles(meta, ROCK)[4:]
    palm = tiles(meta, PALM)[4:]
    if not (len(floor) == len(rocks) == len(palm) == 4):
        raise ValueError('Missing existing spring stone/palm graphics')
    if not all(v >> 12 == 8 for v in rocks):
        raise ValueError('Expected palette-8 shoreline rocks')
    if not all(v >> 12 == 9 for v in palm):
        raise ValueError('Expected palette-9 flowering palm')
    mirrored = [rocks[1] ^ 0x400, rocks[0] ^ 0x400,
                rocks[3] ^ 0x400, rocks[2] ^ 0x400]
    return {'rocks': floor + rocks, 'palm': floor + palm,
            'mirrored_rocks': floor + mirrored}

def run(root):
    layout_path, meta_path, attr_path, primary_attr_path = files(root)
    layout = bytearray(layout_path.read_bytes())
    meta = bytearray(meta_path.read_bytes())
    secondary_attrs, primary_attrs = attr_path.read_bytes(), primary_attr_path.read_bytes()
    if (len(layout), len(meta), len(secondary_attrs)) != (800, 8192, 1024):
        raise ValueError('Unexpected Cuordilava map/metatile size')
    before, original = bytes(layout), bytes(meta)
    all_ids = [u16(layout, 2 * i) & 1023 for i in range(400)]
    designs = expected_rim(original)
    for (x, y), index, kind in RIM:
        cell = y * 20 + x
        if all_ids.count(512 + index) != 1 or all_ids[cell] != 512 + index:
            raise ValueError('Spring-only metatile moved or reused: ' + str(index))
        if (u16(layout, 2 * cell) >> 10) & 3 != 1:
            raise ValueError('Spring rocks lost collision')
        if u16(secondary_attrs, 2 * index) != 0x000C:
            raise ValueError('Rim behavior changed')
        struct.pack_into('<8H', meta, 16 * index, *designs[kind])
    for (x, y), previous, substitute in POOL:
        cell = y * 20 + x
        old = u16(layout, 2 * cell)
        if (old & 1023) != previous or ((old >> 10) & 3) != 1:
            raise ValueError('Unexpected spring pool layout')
        if u16(primary_attrs, previous * 2) != 0 or u16(primary_attrs, substitute * 2) != 0:
            raise ValueError('Pool water behavior must remain identical')
        struct.pack_into('<H', layout, cell * 2, (old & ~1023) | substitute)
    changed = {y * 20 + x for (x, y), _, _ in POOL}
    for i in range(400):
        old, new = u16(before, 2 * i), u16(layout, 2 * i)
        if old >> 10 != new >> 10 or (i not in changed and old != new):
            raise ValueError('Unexpected change of geometry/collision')
    for i in range(512):
        if i not in {75, 76, 79} and meta[i*16:(i+1)*16] != original[i*16:(i+1)*16]:
            raise ValueError('Unexpected metatile edit outside pool rim')
    layout_path.write_bytes(layout)
    meta_path.write_bytes(meta)
    validate_built(root)
    print('Cuordilava thermal spring: organic rock-palm-rock rim + four mineral-water cells; '
          'collision/elevation, event positions and 512-metatile limit unchanged')

def validate_built(root):
    layout_path, meta_path, attr_path, primary_attr_path = files(root)
    layout, meta = layout_path.read_bytes(), meta_path.read_bytes()
    sa, pa = attr_path.read_bytes(), primary_attr_path.read_bytes()
    if len(layout) != 800 or len(meta) != 8192:
        raise ValueError('Spa map/metatile size changed')
    designs = expected_rim(meta)
    for (x, y), index, kind in RIM:
        value = u16(layout, 2 * (20 * y + x))
        if (value & 1023) != 512 + index or (value >> 10) & 3 != 1:
            raise ValueError('Organic rim misplaced')
        if tiles(meta, index) != designs[kind] or u16(sa, 2 * index) != 0x000C:
            raise ValueError('Organic rim art or original behavior corrupted')
    for (x, y), _, new in POOL:
        value = u16(layout, 2 * (20 * y + x))
        if (value & 1023) != new or (value >> 10) & 3 != 1 or u16(pa, 2 * new) != 0:
            raise ValueError('Mineral-water cells or original collision corrupted')

if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
