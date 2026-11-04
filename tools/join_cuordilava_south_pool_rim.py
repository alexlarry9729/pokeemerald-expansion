#!/usr/bin/env python3
"""Replace the two orange vents beneath Lavaridge's hot spring with true rock.

Map y=6, x=3..6 is the SOUTH rim of the 4x3 mineral basin. Before this
fix, secondary metatile 179 (used twice, x4/5) was still an eight-character
industrial orange grille, between genuine palette-8 stone corners at x3/6.
Changing only a few bright stone pixels cannot fix that discontinuity.

Build the southwest corner and middle southern ledge entirely from already
validated, dry palette-8 rock donors on the WEST and EAST sides. Preserve
the existing right stone corner and the lower-level mountain backing of the
left corner. There are no new graphic characters, metatiles, map cells,
warp/event edits, palette edits, nor collision/elevation changes.
"""
from pathlib import Path
import struct

# Town-private secondary metatile indices (NOT absolute 512-based map IDs).
SOUTH = {178: ((3, 6),), 179: ((4, 6), (5, 6)), 180: ((6, 6),)}
WEST_LOWER = 511  # southwest joint, x2,y5
EAST = 165        # x7,y3/4 existing naturally shaded granite edge
ROCK_PALETTE = 8
SOURCE_GRILLE_PALETTE = 6

def word(buf,off):
    return struct.unpack_from('<H',buf,off)[0]

def paths(root):
    root=Path(root)
    return (
        root/'data/layouts/LavaridgeTown/map.bin',
        root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        root/'data/maps/LavaridgeTown/map.json',
    )

def metatile(buf,mid):
    return struct.unpack_from('<8H',buf,mid*16)

def occupancy(layout,mid):
    return {(i%20,i//20) for i in range(400)
            if word(layout,2*i)&1023==512+mid}

def expected(meta):
    corner=metatile(meta,178)
    east=metatile(meta,EAST)
    west=metatile(meta,WEST_LOWER)
    # All four pieces are dry edge rock, NEVER the aqua upper part of the
    # east bank. West pieces are already correctly oriented for the SW bend.
    left=(west[7],east[6],west[6],east[7])
    middle=(east[6],east[7],east[7],east[6])
    if any(w>>12!=ROCK_PALETTE or (w&1023)<512
           for w in (*left,*middle)):
        raise ValueError('Southern stone donor is no longer a palette-8 rock')
    if any(w>>12!=ROCK_PALETTE for w in corner[:4]):
        raise ValueError('Original southwest stone underlay disappeared')
    return {
        178: corner[:4]+left,
        179: corner[:4]+middle,
    }

def validate_built(root):
    map_path,metas_path,attrs_path,events_path=paths(root)
    layout,meta,attrs=(p.read_bytes() for p in (map_path,metas_path,attrs_path))
    if (len(layout),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError('South hot-spring rim exceeded fixed GBA data sizes')
    for mid,positions in SOUTH.items():
        if occupancy(layout,mid)!=set(positions):
            raise ValueError(f'Southern rock {mid} moved or became shared')
        if word(attrs,mid*2)!=0x1000:
            raise ValueError(f'Southern stone {mid} changed terrain behavior')
        for x,y in positions:
            raw=word(layout,2*(20*y+x))
            if (raw>>10)&3!=1 or raw>>12!=0:
                raise ValueError(f'Southern pool bank is no longer blocking at {(x,y)}')
    target=expected(meta)
    for mid,desired in target.items():
        if metatile(meta,mid)!=desired:
            raise ValueError(f'South-bank rock at {mid} is disconnected from west/east')
    # Right corner is intentionally not reauthored; its original existing
    # mineral-stone cap already joins the right-hand perimeter.
    if any(w>>12!=ROCK_PALETTE for w in metatile(meta,180)):
        raise ValueError('Preserved southeast granite corner contains factory metal')
    return True

def run(root):
    map_path,metas_path,attrs_path,events_path=paths(root)
    layout,original,attrs,events=(p.read_bytes() for p in
                                  (map_path,metas_path,attrs_path,events_path))
    if (len(layout),len(original),len(attrs))!=(800,8192,1024):
        raise ValueError('Apply the south-rim fix only after city assembly')
    for mid,positions in SOUTH.items():
        if occupancy(layout,mid)!=set(positions):
            raise ValueError(f'Unsafe reused pool perimeter metatile {mid}')
        if word(attrs,mid*2)!=0x1000:
            raise ValueError('Unexpected new pool-bank collision')
    old_grille=metatile(original,179)
    if not all((v>>12)==SOURCE_GRILLE_PALETTE for v in old_grille):
        raise ValueError('Original factory vent changed: refuse blind south-rim edit')
    target=expected(original)
    new=bytearray(original)
    for mid,desired in target.items():
        struct.pack_into('<8H',new,mid*16,*desired)
    for mid in range(512):
        if mid not in target and new[mid*16:mid*16+16]!=original[mid*16:mid*16+16]:
            raise ValueError(f'South-rim fix changed unrelated architecture {mid}')
    metas_path.write_bytes(new)
    validate_built(root)
    if (map_path.read_bytes()!=layout or attrs_path.read_bytes()!=attrs
            or events_path.read_bytes()!=events):
        raise ValueError('Pool rim changed stairs, collision or game events')
    print('Cuordilava mineral spa: replaced two southern industrial grille '
          'panels with continuous west/east granite; rejoined southwest '
          'stone corner. Preserved southeast rocks, water, stairs and gameplay.')

if __name__=='__main__':
    run(Path(__file__).resolve().parents[1])
