#!/usr/bin/env python3
"""Restore the four ORIGINAL, connected hot-spring stair/landing panels.

Lavaridge map row y=3, x=8..11 is the original raised path between the
hot springs and Pokémon Center's rear entrance. The cyberpunk first-stage
architecture pass inadvertently replaced all four distinct ORIGINAL
upper-layer metatiles with an identical industrial roof scaffold.

Restore the exact four 8x8 overlay WORDS from the original LavaridgeTown
secondary tileset for metatiles 74/72/73/77. The first four lower-layer
words, all tile graphics, every metatile attribute, map flags, sprites,
water, terrain collision and all warps are left byte-identical.

This is not an approximation of stairs: it uses the GBA original staircase
tile references and their original palettes/directional registration.
"""
from pathlib import Path
import struct

# (x,y): original, unchanged secondary metatile index.
STAIR_CELLS = {
    (8, 3): 74,  # original west upper stair landing
    (9, 3): 72,  # first pair of real stone step courses
    (10, 3): 73, # original mirror of adjacent stair courses
    (11, 3): 77, # east platform and Center rear path
}
# Identical to the original Pokémon Emerald LavaridgeTown metatiles.bin
# from data/tilesets/secondary/lavaridge (master branch).
ORIGINAL_OVERLAYS = {
    74: ((0, 0), (8, 859), (1, 272), (1, 273)),
    72: ((1, 259), (1, 260), (1, 275), (1, 276)),
    73: ((1, 260), (1, 259), (1, 276), (1, 275)),
    77: ((0, 0), (0, 0), (1, 273), (1, 274)),
}
# Source compiler's four repeated copper scaffolding quadrants:
# these must disappear from all four live stair cells.
DISPLACED_TILE_IDS = (258, 259, 260, 261)
EXPECTED_SCAFFOLD = tuple((6 << 12) | (512 + x)
                          for x in DISPLACED_TILE_IDS)
assert set(STAIR_CELLS.values()) == set(ORIGINAL_OVERLAYS)


def word(buf, off):
    return struct.unpack_from('<H', buf, off)[0]


def expected(mid):
    return tuple((pal << 12) | tile
                 for pal, tile in ORIGINAL_OVERLAYS[mid])


def paths(root):
    root = Path(root)
    return (root / 'data/layouts/LavaridgeTown/map.bin',
            root / 'data/tilesets/secondary/cuordilava/metatiles.bin',
            root / 'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
            root / 'data/maps/LavaridgeTown/map.json',
            root / 'data/tilesets/primary/general/metatiles.bin')


def validate_built(root):
    import json
    map_path, meta_path, attrs_path, events_path, primary_path = paths(root)
    m, metas, attrs = (f.read_bytes() for f in
                      (map_path, meta_path, attrs_path))
    if (len(m), len(metas), len(attrs)) != (800, 8192, 1024):
        raise ValueError('Original elevated stair footprint/graphics budget changed')
    if len(primary_path.read_bytes()) != 8192:
        raise ValueError('Original primary stair graphic references no longer exist')
    events = json.loads(events_path.read_text(encoding='utf-8'))
    access = {(int(w['x']), int(w['y']), w['dest_map'])
              for w in events['warp_events']}
    if (9, 2, 'MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F') not in access:
        raise ValueError('The hot springs must still enter the Center at (9,2)')
    trigger = [e for e in events.get('coord_events', [])
               if (e.get('x'), e.get('y')) == (6, 3)]
    if len(trigger) != 1 or int(trigger[0]['elevation']) != 3:
        raise ValueError('Original raised hot-spring access lost its trigger')
    for (x, y), mid in STAIR_CELLS.items():
        raw = word(m, 2 * (y * 20 + x))
        if (raw & 1023) != mid + 512 or ((raw >> 10) & 3) != 0:
            raise ValueError(f'Original raised steps moved at {(x, y)}')
        found = {(i % 20, i // 20) for i in range(400)
                 if (word(m, 2*i) & 1023) == mid + 512}
        if found != {(x, y)}:
            raise ValueError(f'Stair source metatile is shared unexpectedly: {mid}')
        overlay = struct.unpack_from('<4H', metas, mid * 16 + 8)
        if overlay != expected(mid):
            raise ValueError(f'Not the original Pokémon Emerald stair tiles: {mid}')
        if (word(attrs, mid * 2) & 0xC000) != 0:
            raise ValueError('Restored stair source changed its background behavior')
    return True


def run(root):
    root = Path(root)
    map_path, meta_path, attrs_path, events_path, primary_path = paths(root)
    layout, old_metatiles, attrs = (
        f.read_bytes() for f in (map_path, meta_path, attrs_path)
    )
    if (len(layout), len(old_metatiles), len(attrs)) != (800,8192,1024):
        raise ValueError('Run the original stair recovery only after atlas assembly')
    new_metatiles = bytearray(old_metatiles)
    for (x,y),mid in STAIR_CELLS.items():
        raw = word(layout, 2*(y*20+x))
        if raw&1023 != mid+512 or ((raw>>10)&3) != 0:
            raise ValueError(f'Refuse to alter unknown raised stair cell {(x,y)}')
        before = struct.unpack_from('<4H', old_metatiles, mid*16+8)
        if before != EXPECTED_SCAFFOLD:
            raise ValueError(f'Stair {mid} source changed; refuse stale restore: {before}')
        struct.pack_into('<4H', new_metatiles, mid*16+8, *expected(mid))
    for mid in range(512):
        if mid not in STAIR_CELLS.values() and (
            new_metatiles[mid*16:mid*16+16] !=
            old_metatiles[mid*16:mid*16+16]
        ):
            raise ValueError(f'Stair restoration leaked into metatile {mid}')
        if mid in STAIR_CELLS.values() and (
            new_metatiles[mid*16:mid*16+8] !=
            old_metatiles[mid*16:mid*16+8]
        ):
            raise ValueError(f'Original stair lower-layer geometry changed {mid}')
    meta_path.write_bytes(new_metatiles)
    validate_built(root)
    if (map_path.read_bytes() != layout
            or attrs_path.read_bytes() != attrs):
        raise ValueError('Restoring original stairs unexpectedly changed gameplay')
    print('Cuordilava: four ORIGINAL Pokemon Emerald hot-spring stair panels '
          '(x8..11,y3) restored; identical GBA map, warp, collision and palette')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
