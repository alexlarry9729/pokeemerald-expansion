#!/usr/bin/env python3
"""Build a connected volcanic civic promenade on existing Cuordilava ground.

Replace selected *walkable* plaza and street-ground metatiles with 12 genuinely
new 16x16 pavements, drawn in 48 previously unreferenced private 8x8 graphics.
Primary base-layer tiles, original ground behavior attributes, map elevation
flags, NPC/event cells, springs, original six warps and 20x20 footprint stay
unchanged. No extension to the already full 512-metatile private tileset.

This late pass runs after all housing, landscape, spa and flower sources have
been assembled; visible GBA tile occupancy is checked at runtime before each
new pixel is written. All map replacements are checked against event positions.
"""
from pathlib import Path
import json
import struct
from collections import Counter
from cuordilava_layers import player_above_walkable_art, validate_covered
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

META_START = 400
FLOOR_SOURCE = 1
AVENUE_SOURCES = (288, 290, 281, 289, 296, 297)
# Original terraced square cell IDs, never a town water/bank character.
PRIVATE_METAS = tuple(range(META_START, META_START + 12))
ANIMATION_IDS = frozenset(range(160, 172)) | frozenset(range(288, 296))
PALETTE = 9


def u16(buf, offset):
    return struct.unpack_from('<H', buf, offset)[0]


def files(root):
    root = Path(root)
    return {
        'map': root/'data/layouts/LavaridgeTown/map.bin',
        'metas': root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        'attrs': root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        'primary': root/'data/tilesets/primary/general/metatiles.bin',
        'primary_attrs': root/'data/tilesets/primary/general/metatile_attributes.bin',
        'atlas': root/'data/tilesets/secondary/cuordilava/tiles.png',
        'events': root/'data/maps/LavaridgeTown/map.json',
    }


def source_for(x, y, raw):
    """Choose exactly one of twelve private paving patterns, or None."""
    mid = raw & 1023
    # Southern GYM approach: extend the same massive stone courses over
    # already walkable original floor at x4..7,y16..18. These cells are far
    # below the spa (y<11). Event cells are excluded by find_changes and all
    # flower-beds already installed have another source metatile ID, so they
    # are untouched. This makes the southwestern quarter a real continuation
    # of the redesigned central promenade, not an abrupt rock-carpet edge.
    if mid == FLOOR_SOURCE and 4 <= x <= 7 and 16 <= y <= 18:
        return ((x * 7 + y * 3) % 6, mid)
    # Already existing original walkable floor in the town center, southern
    # arcade and walkway. Keep thermal basin x<8 and all building cells away.
    if mid == FLOOR_SOURCE and 8 <= x <= 18 and 7 <= y <= 18:
        return ((x * 7 + y * 3) % 6, mid)
    # West-east town street: six exact original brown floor IDs. New basalt
    # paving connects the existing landmark square, rather than changing the
    # gym, thermal pool or water's animated graphics.
    if mid in AVENUE_SOURCES and 8 <= x <= 18 and 6 <= y <= 10:
        return (6 + AVENUE_SOURCES.index(mid), mid)
    return None


def drawing(kind):
    """Calm large-slab basalt rather than the previous repeating noisy carpet.

    Twelve original-footprint 16x16 tiles remain distinct. All share broad,
    continuous slate courses, one recessed structural joint and a much less
    aggressive lighting palette. The engineering road adds a shallow copper
    service rail, while pedestrian stones stay quiet.
    """
    if kind not in range(12):
        raise ValueError(f"Unsupported Cuordilava pavement motif {kind}")
    art = [[12] * 16 for _ in range(16)]
    road = kind >= 6
    v = kind % 6

    def p(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            art[y][x] = c

    # Stone courses are deliberately aligned at y7/14 for ALL 12 motifs,
    # allowing their long seams to read as a connected roadway at map scale.
    # Each course contains only two large mineral slabs, not a field of dots.
    for y in range(16):
        seam = 7 if y < 8 else 14
        cut = (4 + (v % 3) * 2) if y < 8 else (10 - (v % 3) * 2)
        for x in range(16):
            if y == seam:
                c = 5
            elif y == seam + 1:
                c = 6
            elif x == cut and 1 <= y <= 13:
                c = 8
            elif x == cut + 1 and 1 <= y <= 13:
                c = 6
            else:
                # A continuous broad slab with very subtle shade changes,
                # never per-pixel procedural neon/black confetti.
                c = 12 if (y < 8 or x < cut) else 13
                if (v in (2, 5)) and y in (2, 3) and 3 <= x <= 11:
                    c = 13
            p(x, y, c)

    # Small asymmetric chipped masonry is enough to make each stone unique.
    # These marks are sparse and bounded by the quiet slate materials.
    chips = (
        ((2, 2), (12, 5), (3, 12)),
        ((4, 3), (13, 4), (7, 11)),
        ((3, 4), (11, 2), (9, 13)),
        ((2, 5), (12, 3), (5, 10)),
        ((3, 2), (10, 4), (8, 12)),
        ((4, 5), (13, 2), (6, 11)),
    )
    for x,y in chips[v]:
        p(x, y, 6)
        p(x + 1, y, 13)

    if road:
        # One broad continuous buried thermal-service channel connects
        # contiguous east-west road metatiles at the SAME exact y offsets.
        for x in range(16):
            p(x, 9, 5)
            p(x, 10, 13)
            p(x, 11, 11 if x % 6 not in (0, 1) else 13)
        # Two embedded low-profile rivets per segment, never square
        # flashing signal lights occupying the pedestrian path.
        for x in (3 + v % 3, 12 - v % 3):
            p(x, 9, 8)
            p(x, 10, 14)
    elif v in (1, 4):
        # Only two of six pedestrian designs have genuinely tiny
        # herb-filled fissures. They do NOT spawn new blocking plants.
        for x,y in ((11, 3), (12, 3), (12, 4), (3, 11), (4, 11)):
            p(x, y, 9 if (x + y) % 2 else 10)
    elif v in (2, 5):
        for x,y in ((3, 5), (4, 5), (12, 12)):
            p(x, y, 13)

    # A few chipped corners expose the original underlying cobble.
    for x,y in ((0,0),(15,0),(0,15),(15,15)):
        if (v + x + y) % 3 == 0:
            p(x, y, 0)

    stone = sum(c in (5,6,12,13) for row in art for c in row)
    copper = sum(c in (11,14) for row in art for c in row)
    moss = sum(c in (9,10,15) for row in art for c in row)
    dark = sum(c == 8 for row in art for c in row)
    filled = sum(c != 0 for row in art for c in row)
    if stone < (195 if road else 215) or copper > 36 or moss > 12 or dark > 34:
        raise ValueError(f"Volcanic street motif {kind} has excessive visual noise: "
                         f"{stone=},{copper=},{moss=},{dark=}")
    if filled < 248 or any(not 0 <= c < 16 for row in art for c in row):
        raise ValueError("Invalid original-capacity 4bpp walkable road art")
    return art


def find_changes(map_bytes, event_cells):
    old = {}
    for y in range(20):
        for x in range(20):
            xy = (x,y)
            raw = u16(map_bytes, (y*20+x)*2)
            source = source_for(x,y,raw)
            if source is None or xy in event_cells:
                continue
            if ((raw>>10)&3) != 0:
                raise ValueError(f'Civic pavement would occupy impassable terrain {xy}')
            old[xy] = source
    if len(old) < 48:
        raise ValueError(f'Not enough original safe civic path positions: {len(old)}')
    if len({kind for kind, _ in old.values()}) != 12:
        raise ValueError('The original six promenade + six pavement patterns disappeared')
    return old


def event_cells(root):
    data=json.loads(files(root)['events'].read_text(encoding='utf-8'))
    return {
        (int(e['x']),int(e['y']))
        for k in ('object_events','warp_events','coord_events','bg_events')
        for e in data.get(k,[]) if 'x' in e and 'y' in e
    }


def referenced_art(meta, map_bytes, primary):
    """Precisely avoid any private 8x8 art used by any visible map cell."""
    used=set()
    for i in range(400):
        value=u16(map_bytes,i*2)&1023
        bank=meta if value>=512 else primary
        index=value-512 if value>=512 else value
        for q in range(8):
            tid=u16(bank,index*16+q*2)&1023
            if tid>=512:
                used.add(tid-512)
    return used


def run(root):
    p=files(root)
    root=Path(root)
    terrain=bytearray(p['map'].read_bytes())
    meta=bytearray(p['metas'].read_bytes())
    attrs=bytearray(p['attrs'].read_bytes())
    primary=p['primary'].read_bytes()
    pattrs=p['primary_attrs'].read_bytes()
    if (len(terrain),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError('Cuordilava paving must use the FULL original 20x20 map / 512 private metatiles')
    changes=find_changes(terrain,event_cells(root))
    already={u16(terrain,i*2)&1023 for i in range(400)}
    if any(512+mid in already for mid in PRIVATE_METAS):
        raise ValueError('Paving donor metatile ID already used by an existing building/feature')
    # No overwriting any tile which is visible anywhere in the map, even
    # through unrelated roof/metatile assemblies.
    occupied=referenced_art(meta,terrain,primary)
    free=sorted(set(range(512))-occupied-ANIMATION_IDS)
    if len(free)<48:
        raise ValueError(f'Insufficient isolated private GBA 8x8 tiles: {len(free)}')
    graphic_ids=free[:48]
    atlas=p['atlas']
    w,h,rows=png_indexed(atlas)
    if (w,h)!=(128,256):
        raise ValueError('Expected 512 private 4bpp graphic characters')
    png=atlas.read_bytes()
    palette=png[png.index(b'PLTE')+4:png.index(b'PLTE')+52]
    if len(palette)!=48:
        raise ValueError('Expected a 16-index private palette')
    old_map,old_meta,old_attrs=bytes(terrain),bytes(meta),bytes(attrs)
    for kind in range(12):
        source_mid = FLOOR_SOURCE if kind<6 else AVENUE_SOURCES[kind-6]
        mid = PRIVATE_METAS[kind]
        graphic=drawing(kind)
        overlay=bytearray(primary[source_mid*16:source_mid*16+8])
        for q in range(4):
            tid=graphic_ids[kind*4+q]
            tx,ty=(tid%16)*8,(tid//16)*8
            sx,sy=(q%2)*8,(q//2)*8
            for yy in range(8):
                for xx in range(8):
                    rows[ty+yy][tx+xx]=graphic[sy+yy][sx+xx]
            overlay += struct.pack('<H',(PALETTE<<12)|(512+tid))
        meta[mid*16:(mid+1)*16]=overlay
        # The original ground source has NORMAL BG1 overlays. Our NEW
        # opaque upper graphics would hide an elevation-3 player there.
        # Covered keeps the same behavior but composites art on BG2.
        ground_attr=u16(pattrs,source_mid*2)
        struct.pack_into('<H',attrs,mid*2,
                         player_above_walkable_art(ground_attr))
    for (x,y),(kind,source_mid) in changes.items():
        off=2*(20*y+x)
        raw=u16(terrain,off)
        if (raw&1023)!=source_mid:
            raise ValueError('Civic floor source changed during assembly')
        struct.pack_into('<H',terrain,off,(raw&~1023)|(512+PRIVATE_METAS[kind]))
    allowed=set(PRIVATE_METAS)
    for i in range(400):
        before,after=u16(old_map,2*i),u16(terrain,2*i)
        if before>>10!=after>>10:
            raise ValueError('Civic paving modified original map layer/elevation flags')
        if ((i%20,i//20) not in changes) and before!=after:
            raise ValueError('Civic paving changed another town map cell')
    if any(meta[i*16:(i+1)*16]!=old_meta[i*16:(i+1)*16]
           for i in range(512) if i not in allowed):
        raise ValueError('Civic paving modified another private GBA metatile')
    if any(attrs[i*2:(i+1)*2]!=old_attrs[i*2:(i+1)*2]
           for i in range(512) if i not in allowed):
        raise ValueError('Civic paving modified unrelated collision data')
    write_png(atlas,w,h,rows,palette)
    p['map'].write_bytes(terrain)
    p['metas'].write_bytes(meta)
    p['attrs'].write_bytes(attrs)
    validate_built(root)
    print(f'Cuordilava: rebuilt {len(changes)} old civic ground cells as 12 '
          f'original-attribute-preserving volcanic walkway motifs, using '
          '48 isolated 8x8 GBA tiles, zero new space or obstacles')


def validate_built(root):
    root=Path(root)
    p=files(root)
    terrain=p['map'].read_bytes()
    meta=p['metas'].read_bytes()
    attrs=p['attrs'].read_bytes()
    primary=p['primary'].read_bytes()
    pattrs=p['primary_attrs'].read_bytes()
    if (len(terrain),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError('Volcanic path map/collision bytes changed size')
    actual=Counter()
    for y in range(20):
        for x in range(20):
            mid=u16(terrain,2*(y*20+x))&1023
            if 512+META_START <= mid < 512+META_START+12:
                if (x,y) in event_cells(root):
                    raise ValueError(f'Civic paving unexpectedly covers a warp/NPC/sign {(x,y)}')
                if ((u16(terrain,2*(y*20+x))>>10)&3)!=0:
                    raise ValueError('Civic walkway made impassable')
                actual[mid-512-META_START]+=1
    if sum(actual.values())<48 or len(actual)!=12:
        raise ValueError(f'Volcanic paving lost its 12 motifs or coverage {actual}')
    w,h,rows=png_indexed(p['atlas'])
    if (w,h)!=(128,256):
        raise ValueError('Paved town atlas not original 512x8x8')
    ids=set()
    for kind in range(12):
        source=FLOOR_SOURCE if kind<6 else AVENUE_SOURCES[kind-6]
        mid=PRIVATE_METAS[kind]
        validate_covered(u16(pattrs,2*source),u16(attrs,2*mid),
                         f'Volcanic promenade metatile {mid}')
        if meta[16*mid:16*mid+8]!=primary[16*source:16*source+8]:
            raise ValueError('Volcanic promenade changed original ground underlay')
        desired=drawing(kind)
        for q in range(4):
            encoded=u16(meta,16*mid+8+2*q)
            tid=(encoded&1023)-512
            if encoded>>12!=PALETTE or not 0<=tid<512 or tid in ANIMATION_IDS:
                raise ValueError('Pavement graphic uses invalid GBA 4bpp tile or palette')
            if tid in ids:
                raise ValueError('Pavement graphics are accidentally shared between different motifs')
            ids.add(tid)
            x0,y0=(tid%16)*8,(tid//16)*8
            xs,ys=(q%2)*8,(q//2)*8
            for y in range(8):
                for x in range(8):
                    if rows[y0+y][x0+x]!=desired[ys+y][xs+x]:
                        raise ValueError('Original civic paving pixel/quadrant misregistration')
    if len(ids)!=48:
        raise ValueError('The twelve pavement panels require 48 unique tile graphics')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
