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
    """Large irregular volcanic plates with low-contrast broken mineral joints.

    Previous source art laid strong straight joint lines at y=7 and y=14 in
    EVERY 16x16 metatile; across 84 city cells this formed an overwhelming
    repeated brick wall and distracted from the buildings. These twelve
    existing motifs make 2-3 broad ASYMMETRIC polygon plates each instead.
    A low, inset copper service rail survives only on street variants.
    Same 48 already-allocated 8x8 characters and 12 metatiles, no extra
    palette, no map edits; gameplay flags and COVERED/BG2 remain intact.
    """
    if not 0 <= kind < 12:
        raise ValueError("Unexpected volcanic district paving motif")
    road=kind>=6
    v=kind%6
    a=[[12]*16 for _ in range(16)]

    def p(x,y,c):
        if 0<=x<16 and 0<=y<16:
            a[y][x]=c

    # Different angles prevent aligned horizontal tile/row grids.
    # The seams stop before the border and bevel into the actual slab:
    # finished tiles look like a local stone terrace, not a wallpaper.
    s1=(4,6,9,5,10,7)[v]
    slope=(-1,1,2,-2,1,-1)[v]
    for y in range(16):
        main_cut=s1+(slope*(y-7))//8
        main_cut=max(2,min(13,main_cut))
        for x in range(16):
            # Four broad colors, selected per plate not per pixel.
            c=(12 if x<main_cut else 13)
            if v in (2,5) and y>=9 and x>4:
                c=3
            if v in (1,4) and x<5 and y>11:
                c=12
            if (x,y) in ((0,0),(15,0),(0,15),(15,15)):
                c=12
            if 2<=y<=13:
                if x==main_cut:
                    c=5
                elif x==main_cut+1:
                    c=6
            p(x,y,c)

    # A diagonal shale rift crosses PART of a slab, not every entire row.
    # Vary the height/length in each variant to avoid periodic striping.
    for x in range(2,14):
        if v in (0,3):
            fracture=5 + (x//5) + (1 if v==3 else 0)
        elif v in (1,4):
            fracture=11-(x//4)+(1 if v==4 else 0)
        else:
            fracture=7+(x//6)
        if 2<=fracture<14:
            p(x,fracture,5)
            if x%3!=0:
                p(x,fracture+1,6)

    # Broken edges, low-frequency stone flakes and very few mineral colors.
    for x,y in (
        ((3,2),(11,11),(6,14)),
        ((4,3),(12,6),(8,13)),
        ((2,4),(12,12),(8,3)),
        ((3,13),(10,4),(5,7)),
        ((4,11),(11,3),(13,8)),
        ((3,3),(9,12),(13,5)),
    )[v]:
        p(x,y,6)
        p(x+1,y,13)

    if road:
        # One engineered geothermal service rail, clearly smaller than
        # the pavement itself; its tiny copper core is physically inset.
        for x in range(16):
            p(x,9,5)
            p(x,10,13)
            p(x,11,6)
            if x in range(4,12) and (x+v)%4 not in (0,1):
                p(x,10,11)
        # A single low rivet instead of repeated glowing orange pixels.
        p(3+v%4,9,8)
        p(3+v%4,10,14)
    elif v in (1,4):
        # Living cliff grass appears only in two of the six sidewalks,
        # subdued and embedded in fine stone fissures.
        for x,y in ((3,3),(4,3),(4,4),(12,12)):
            p(x,y,9 if (x+y)%2 else 10)

    # Rare chipped corners expose the original cobbles without creating
    # a hard rectilinear border around all the different pavement cells.
    for x,y in ((0,0),(15,0),(0,15),(15,15)):
        if (x+3*y+v)%5==0:
            p(x,y,0)

    counts={v:sum(c==v for row in a for c in row) for v in range(16)}
    stone=sum(counts[c] for c in (3,5,6,12,13))
    copper=counts[11]+counts[14]
    moss=counts[9]+counts[10]+counts[15]
    if stone<220 or copper>12 or moss>8 or counts[8]>16:
        raise ValueError(
            f"Paving kind {kind} lost broad matte basalt plates: "
            f"stone={stone}, copper={copper}, moss={moss}, shadow={counts[8]}"
        )
    if sum(c!=0 for row in a for c in row)<250:
        raise ValueError("Volcanic paving left the original floor exposed")
    if any(not 0<=c<16 for row in a for c in row):
        raise ValueError("Invalid 4bpp indexed color in large volcanic paving")
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
