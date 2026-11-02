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
    """Twelve massive connected original-footprint civic pavement motifs.

    Each 16x16 tile now contains 2-3 LARGE dressed basalt slabs instead of
    pseudo-random noisy speckles. Long horizontal joints line up at y=5/12
    across ALL neighbouring pavement cells. In six existing road variants,
    the broad buried mineral service channel stays continuous across x=0..15,
    with occasional copper rivets. Pedestrian flagstones have crosscuts with
    deliberately staggered construction-joint positions. The two families
    share material and scale but are recognizable at map scale.

    Palette9 is already in-game: charcoal/ashen reddish stone (5,6,12,13),
    natural copper (11,14), moss (9,10,15), dark grout (8). Pixel 0 is
    original terrain: limited to a handful of outer corner dents.
    """
    if not 0 <= kind < 12:
        raise ValueError(f'No Cuordilava road tile family for {kind}')
    a = [[0] * 16 for _ in range(16)]
    street = kind >= 6
    variant = kind % 6

    def p(x, y, c):
        if 0 <= x < 16 and 0 <= y < 16:
            a[y][x] = c

    for y in range(16):
        # The same y=5/12 long stone courses across every urban district
        # tile produce readable joined paving even if unrelated road variants
        # are neighbours. Recessed ends create real long slabs.
        course = 0 if y < 5 else 1 if y < 12 else 2
        crosscut = (3 + variant * 3 + course * 6) % 16
        if crosscut in (0, 15):
            crosscut = 4 if crosscut == 0 else 11
        for x in range(16):
            if y in (5, 12):
                # Broad but visually thin matte grout course.
                c = 6 if (x + variant) % 5 == 0 else 5
            elif y in (6, 13):
                # Beveled underside catches pale volcanic mineral light.
                c = 13 if (x + variant) % 6 else 6
            elif x in (crosscut, crosscut + 1) and y not in (0, 5, 6, 12, 13, 15):
                c = 8 if x == crosscut else 6
            elif x in (crosscut - 1, crosscut + 2) and y not in (0, 5, 6, 12, 13, 15):
                c = 5
            else:
                # Large smooth, connected slate faces with limited low-
                # frequency natural mineral color variation (NOT confetti).
                slab = ((x // 7) + (y // 5) + variant) % 4
                c = (12, 13, 12, 6)[slab]
                if (x + 2 * y + variant * 5) % 23 == 0:
                    c = 5
            p(x, y, c)

    if street:
        # Continuous recessed copper steam-service trough across the SIX
        # original east-west roadway graphic variants. All x edges join.
        for x in range(16):
            p(x, 8, 8 if x % 9 == 0 else 6)
            p(x, 9, 11 if x % 7 not in (0, 1) else 13)
            p(x, 10, 13 if x % 4 else 5)
        # Massive copper riveting, a few underlit insets, instead of a
        # ribbon of evenly spaced orange specks along every paving seam.
        for x in (3 + variant % 3, 12 - variant % 3):
            p(x, 8, 13)
            p(x, 9, 14)
            p(x + 1, 9, 11)
        # An occasional recessed obsidian drain or moss corner gives
        # functional road identity without suggesting standing pool water.
        if variant in (2, 5):
            for y in (2, 3, 4):
                for x in (11, 12, 13):
                    p(x, y, 8 if (x+y) % 3 else 6)
            p(12, 2, 13)
            p(12, 3, 5)
        elif variant in (1, 4):
            for x, y in ((2, 2), (3, 2), (2, 3), (4, 3)):
                p(x, y, 9 if (x+y)%2 else 10)
    else:
        # Pedestrian lanes use the same heavy flagstone scale, without
        # engineering rail. Wide 2px chamfered masonry ridge instead.
        for x in range(1, 15):
            if (x + variant) % 9 in (0, 1, 2):
                p(x, 2, 5)
                p(x, 3, 6)
        for x0 in (1, 13):
            for y in (4, 10, 15):
                p(x0, y, 6 if (y+variant)%2 else 5)
        # Small, organically irregular green mineral seams on only two of
        # six variants: adjacent to other stone they read as scattered
        # vegetation, not repeated pool-green stains.
        if variant in (1, 4):
            for x, y in ((10, 2), (11, 2), (11, 3), (12, 2),
                         (9, 10), (10, 10), (10, 11)):
                p(x, y, 9 if (x+y) % 3 else 10)
            p(11, 3, 15)
        if variant in (2, 5):
            # Sparse copper mineral inclusions rather than road neon.
            for x, y in ((3, 3), (4, 3), (10, 9), (11, 9)):
                p(x, y, 11 if (x+y)%2 else 13)
            p(4, 4, 14)

    # Use the original cobbled underlay at a FEW chipped corners to
    # eliminate the rectangular carpet/square-tile visual border.
    for x, y in ((0, 0), (15, 0), (0, 15), (15, 15)):
        if (x + 3*y + variant) % 3 == 0:
            p(x, y, 0)

    # Appearance guards go beyond valid 4bpp: reject bright confetti and
    # accidental full-neon streets. Tested against the final composited
    # preview as well, while source-level guards are deterministic.
    counts = {v: sum(pixel == v for row in a for pixel in row)
              for v in range(16)}
    stone = sum(counts[v] for v in (5, 6, 12, 13))
    copper = counts[11] + counts[14]
    moss = counts[9] + counts[10] + counts[15]
    dark = counts[8]
    if stone < (166 if street else 195):
        raise ValueError(f'Insufficient continuous basalt on tile {kind}: {stone}')
    if dark > 35 or moss > 18 or copper > 36:
        raise ValueError(f'Tile {kind} overdecorated: {dark=}, {moss=}, {copper=}')
    if sum(c != 0 for row in a for c in row) < 248:
        raise ValueError(f'Tile {kind} did not fill the flagstone surface')
    if any(c < 0 or c >= 16 for row in a for c in row):
        raise ValueError('Invalid indexed 4bpp Cuordilava road color')
    return a

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
        attrs[mid*2:(mid+1)*2]=pattrs[source_mid*2:source_mid*2+2]
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
        if attrs[2*mid:2*mid+2]!=pattrs[2*source:2*source+2]:
            raise ValueError('Volcanic promenade no longer has original ground movement')
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
