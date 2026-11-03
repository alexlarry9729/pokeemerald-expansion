#!/usr/bin/env python3
"""Restore the ORIGINAL elevated hot-spring access and its four step panels.

The genuinely walkable, elevation-3 corridor behind the mineral pool is
LavaridgeTown x=6..9, y=1. ALL FOUR cells originally used metatile 174
(map ID 686), not roof-metatile 72/73/74/77 at y3 (those are BLOCKED).
A prior "rear Center roof" operation mistook these accessible original steps
for roof windows and put opaque roof paintings over the corridor.

Restore the original metatile 174's exact eight GBA tile-reference words from
vanilla secondary/lavaridge/metatiles.bin (master). No new graphics or metatile
slots. All original game-world map, elevation, warp, passage collision,
scripts, animated water, and unrelated artwork remain byte-identical.
"""
from pathlib import Path
import json
import struct

# This is the original raised path between the spa and rear Center warp at 9,2.
STAIR_CELLS = {(6,1), (7,1), (8,1), (9,1)}
STAIR_META = 174
STAIR_MAP_ID = 512 + STAIR_META
ORIGINAL_STAIRS = (
    (10 << 12) | 82, (10 << 12) | 83,
    (10 << 12) | 98, (10 << 12) | 99,
    (8 << 12) | 827, (8 << 12) | 827,
    (8 << 12) | 843, (8 << 12) | 843,
)
# Original Cuordilava redesign replaced these with industrialized facade art.
REDESIGNED_SCAFFOLD = tuple(
    (6 << 12) | (512 + tid)
    for tid in (164,165,180,181,166,167,182,183)
)
assert len(ORIGINAL_STAIRS) == len(REDESIGNED_SCAFFOLD) == 8


def u16(buf, pos):
    return struct.unpack_from('<H', buf, pos)[0]


def files(root):
    root = Path(root)
    return (
        root / 'data/layouts/LavaridgeTown/map.bin',
        root / 'data/tilesets/secondary/cuordilava/metatiles.bin',
        root / 'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        root / 'data/maps/LavaridgeTown/map.json',
    )


def inspect_access(m, attrs, events):
    if len(m) != 800 or len(attrs) != 1024:
        raise ValueError('Original 20x20 map or collision/behavior budget changed')
    observed = {
        (pos%20,pos//20) for pos in range(400)
        if (u16(m, 2*pos) & 1023) == STAIR_MAP_ID
    }
    if observed != STAIR_CELLS:
        raise ValueError(
            f'Original elevated spa steps replaced by roof graphics: {observed}'
        )
    for x,y in STAIR_CELLS:
        raw = u16(m, 2*(20*y+x))
        if (raw & 1023) != STAIR_MAP_ID or ((raw >> 10) & 3) != 0 or raw >> 12 != 3:
            raise ValueError(f'Raised hot-spring walkway changed access at {(x,y)}')
    if u16(attrs, STAIR_META*2) != 0x1000:
        raise ValueError('Original spring-step metatile behavior changed')
    warps = events['warp_events']
    if len(warps) != 6 or not any(
        w.get('x')==9 and w.get('y')==2
        and w.get('dest_map')=='MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F'
        and int(w.get('elevation',-1))==3 for w in warps
    ):
        raise ValueError('Pokémon Center rear hot-spring warp no longer works')
    if not any(e.get('x')==6 and e.get('y')==3 and
               int(e.get('elevation',-1))==3 for e in
               events.get('coord_events',[])):
        raise ValueError('Original elevated hot-spring trigger is missing')


def validate_built(root):
    map_path, meta_path, attrs_path, events_path = files(root)
    m, meta, attrs = (p.read_bytes() for p in
                      (map_path, meta_path, attrs_path))
    if len(meta) != 8192:
        raise ValueError('Original 512-metatile graphic budget changed')
    events = json.loads(events_path.read_text(encoding='utf-8'))
    inspect_access(m, attrs, events)
    graphics = struct.unpack_from('<8H', meta, STAIR_META*16)
    if graphics != ORIGINAL_STAIRS:
        raise ValueError('Raised steps are not the original Pokémon Emerald art')
    return True


def run(root):
    map_path, meta_path, attrs_path, events_path = files(root)
    m, meta, attrs = (p.read_bytes() for p in
                      (map_path, meta_path, attrs_path))
    if len(meta) != 8192:
        raise ValueError('Original fixed Cuordilava metatile capacity was changed')
    original_events = events_path.read_bytes()
    inspect_access(m, attrs, json.loads(original_events))
    before = struct.unpack_from('<8H', meta, STAIR_META*16)
    if before != REDESIGNED_SCAFFOLD:
        raise ValueError(f'Unexpected stair source: {before}')
    replacement = bytearray(meta)
    struct.pack_into('<8H', replacement, STAIR_META*16, *ORIGINAL_STAIRS)
    for mid in range(512):
        if mid != STAIR_META and (
            replacement[mid*16:mid*16+16] != meta[mid*16:mid*16+16]
        ):
            raise ValueError('Restoring original spring access changed another metatile')
    meta_path.write_bytes(replacement)
    validate_built(root)
    if (map_path.read_bytes()!=m or attrs_path.read_bytes()!=attrs
            or events_path.read_bytes()!=original_events):
        raise ValueError('Spring-step pixel recovery modified gameplay data')
    print('Cuordilava: restored original 4-cell elevated hot-spring steps '
          '(x6..9,y1) and exact vanilla palette-8 stone tiles; '
          'Center rear warp, step elevation and terrain collision unchanged')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
