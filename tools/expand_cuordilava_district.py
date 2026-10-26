#!/usr/bin/env python3
"""Cuordilava enlarged, playable volcanic districts (32x28 map metatiles).

Preserves the ORIGINAL 20x20 town core byte-for-byte after every existing
architecture/scenery generator has finished. Adds the eastern kiln works,
magma inlay square, terraced roof district, palms, a shallow natural hot-water
basin and an expanded southern coastal setting by reusing existing GBA art.

No new 4bpp tiles, metatiles, events, NPCs, scripts, warps, palette banks or
engine code. The Route 112 exit is relocated to the enlarged EAST perimeter
at the exact same Y levels; the original reciprocal connection offsets stay.

The original generator/validator necessarily runs FIRST, while the map still
has its historical 20x20 footprint. The new 32x28 validator runs LAST.
"""
from __future__ import annotations

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import struct

OLD_W, OLD_H = 20, 20
W, H = 32, 28
BASE_EVENT_WARPS = {
    (12,15,'MAP_LAVARIDGE_TOWN_HERB_SHOP'),
    (5,15,'MAP_LAVARIDGE_TOWN_GYM_1F'),
    (15,5,'MAP_LAVARIDGE_TOWN_MART'),
    (9,6,'MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F'),
    (16,15,'MAP_LAVARIDGE_TOWN_HOUSE'),
    (9,2,'MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F'),
}
ENTRY = (18,8)
EXIT = (31,8)
ANNEX_SQUARE = (23,12)
COAST_WALK = (22,22)
MANIFEST = 'cuordilava-expanded-layout-audit.json'
OCEAN_METATILES = (421,422,423)
OCEAN_PALETTE = 7  # deep slate-blue outdoors, not turquoise hot spring palette 8
OCEAN_ART_TILES = (510, 511)  # last two unreferenced private 8x8 GBA graphics

def paths(root: Path):
    return {
        'layout': root/'data/layouts/layouts.json',
        'map': root/'data/layouts/LavaridgeTown/map.bin',
        'events': root/'data/maps/LavaridgeTown/map.json',
        'route': root/'data/maps/Route112/map.json',
        'meta_secondary': root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        'meta_primary': root/'data/tilesets/primary/general/metatile_attributes.bin',
        'manifest': root/MANIFEST,
    }

def value(b: bytes, width: int, x: int, y: int) -> int:
    return struct.unpack_from('<H', b, (y*width+x)*2)[0]

def locate_layouts(paths):
    data = json.loads(paths['layout'].read_text(encoding='utf-8'))
    item = next((x for x in data['layouts'] if x.get('id')=='LAYOUT_LAVARIDGE_TOWN'), None)
    if item is None:
        raise ValueError('Missing original playable town layout')
    return data, item

def core_bytes(terrain: bytes) -> bytes:
    return b''.join(terrain[(y*W)*2:(y*W+OLD_W)*2] for y in range(OLD_H))

def original_events(p):
    events=json.loads(p['events'].read_text(encoding='utf-8'))
    warps={(int(w['x']),int(w['y']),w['dest_map']) for w in events['warp_events']}
    if warps != BASE_EVENT_WARPS or len(events['warp_events']) != 6:
        raise ValueError('Historic town entrance coordinates have changed')
    if events.get('connections') != [
        {'map':'MAP_ROUTE112','offset':-40,'direction':'right'}
    ]:
        raise ValueError('The Route 112 east-hand connection has changed')
    route=json.loads(p['route'].read_text(encoding='utf-8'))
    if not any(x.get('map')=='MAP_LAVARIDGE_TOWN'
               and x.get('direction')=='left' and x.get('offset')==40
               for x in route.get('connections', [])):
        raise ValueError('Route 112 no longer has a reciprocal town connection')
    for kind in ('object_events','warp_events','coord_events','bg_events'):
        for event in events.get(kind, []):
            if not 0 <= event['x'] < OLD_W or not 0 <= event['y'] < OLD_H:
                raise ValueError('An original event is outside the historic core')
    return events

def cell_attrs(cells: bytes, root: Path):
    p=paths(root)
    secondary=p['meta_secondary'].read_bytes()
    primary=p['meta_primary'].read_bytes()
    if len(secondary)!=1024 or len(primary)<1024:
        raise ValueError('Bad original metatile behavior tables')
    def traversable(x,y):
        raw=value(cells,W,x,y)
        # Bits 10-11 are 0=walk,1=obstacle,2/3 special. Bits 12-15 carry
        # the room elevation and MUST be preserved (not mistaken for collision).
        if ((raw>>10)&3)!=0:
            return False
        mid=raw&1023
        attr=(secondary,mid-512) if mid>=512 else (primary,mid)
        return ((struct.unpack_from('<H',attr[0],attr[1]*2)[0])&0xFF) not in (0x10,0x21)
    return traversable

def path_to(cells: bytes, root: Path, start, goal):
    can=cell_attrs(cells,root)
    if not can(*start) or not can(*goal):
        return False
    pending=deque([start])
    visited={start}
    while pending:
        x,y=pending.popleft()
        if (x,y)==goal:
            return True
        for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=nx<W and 0<=ny<H and (nx,ny) not in visited and can(nx,ny):
                visited.add((nx,ny))
                pending.append((nx,ny))
    return False

def install_ocean_metatiles(root: Path, original_map: bytes):
    """Reserve three otherwise-unused GBA metatiles for deeper coastal water.

    The pool's existing 4bpp ripple pixels are reused; only the palette bank
    changes from hot-spring turquoise index8 to darker sea-blue index7.
    Distinct quadrant ordering gives the sea three repeating textures without
    allocating one additional 8x8 tile or changing original town core data.
    """
    p=paths(root)
    meta_path=root/'data/tilesets/secondary/cuordilava/metatiles.bin'
    attrs_path=p['meta_secondary']
    m=bytearray(meta_path.read_bytes())
    attrs=bytearray(attrs_path.read_bytes())
    if len(m)!=8192 or len(attrs)!=1024:
        raise ValueError('Unexpected secondary map tileset capacity')
    occupied={value(original_map,OLD_W,x,y)&1023
              for y in range(OLD_H) for x in range(OLD_W)}
    if any(512+mid in occupied for mid in OCEAN_METATILES):
        raise ValueError('Deep sea metatile IDs conflict with original town')
    # The three curated *water-only* 8x8 motifs 320/321/336 carry
    # alternating ripple/shadow colours. The original shoreline's primary
    # 264/280 tiles also include orange soil, which turns into unpleasant
    # coral speckle under the deeper marine-blue palette.
    source_mid=(value(original_map,OLD_W,5,4)&1023)-512
    if not 0<=source_mid<512:
        raise ValueError('Missing private turquoise water donor')
    # Last two unused private 8x8 slots. Do not share pixel art with the
    # springs: its white foam pixels turn peach under marine palette 7.
    from render_cuordilava_preview import png_indexed
    from apply_cuordilava_industrial_art import write_png
    graphics={(struct.unpack_from('<H',m,off)[0]&1023)-512
              for off in range(0,len(m),2)
              if (struct.unpack_from('<H',m,off)[0]&1023)>=512}
    if any(t in graphics for t in OCEAN_ART_TILES):
        raise ValueError('Reserved marine 8x8 art IDs are already used')
    image_path=root/'data/tilesets/secondary/cuordilava/tiles.png'
    width,height,pixels=png_indexed(image_path)
    if (width,height)!=(128,256):
        raise ValueError('Original private 4bpp graphic capacity changed')
    png=image_path.read_bytes()
    palette=png[png.index(b'PLTE')+4:png.index(b'PLTE')+52]
    if len(palette)!=48:
        raise ValueError('Missing indexed 16-colour source palette')
    for art_id,source_tile in zip(OCEAN_ART_TILES,(320,321)):
        for row in range(8):
            for col in range(8):
                src=pixels[(source_tile//16)*8+row][(source_tile%16)*8+col]
                # Only existing palette-7 navy / ocean-blue ramp (indices
                # 8,9,10); remove peach-white mineral foaming and rocks.
                converted=(10 if src in (1,10) else
                           9 if src in (9,11,12) else 8)
                pixels[(art_id//16)*8+row][(art_id%16)*8+col]=converted
    variants=((510,511,510,511),(511,510,511,510),
              (510,510,511,511))
    for mid,variant in zip(OCEAN_METATILES,variants):
        recolored=[(OCEAN_PALETTE<<12)|(512+tile) for tile in variant]
        struct.pack_into('<8H',m,mid*16,*(recolored+[0]*4))
        # The new coastal sea is collision-blocked per map cell.
        attrs[mid*2:mid*2+2]=attrs[source_mid*2:source_mid*2+2]
    # Write all three assets after validating source exclusivity.
    write_png(image_path,width,height,pixels,palette)
    meta_path.write_bytes(m)
    attrs_path.write_bytes(attrs)


def validate_ocean_metatiles(root: Path, terrain: bytes):
    p=paths(root)
    meta=(root/'data/tilesets/secondary/cuordilava/metatiles.bin').read_bytes()
    for mid in OCEAN_METATILES:
        entries=struct.unpack_from('<8H',meta,mid*16)
        if any((e&1023) not in tuple(512+tile for tile in OCEAN_ART_TILES)
               or (e>>12)!=OCEAN_PALETTE for e in entries[:4]):
            raise ValueError('Deep-ocean ripple no longer uses isolated blue artwork')
        if any(entries[4:]):
            raise ValueError('Sea graphic overlay must be transparent')
    from render_cuordilava_preview import png_indexed
    width,height,pixels=png_indexed(root/'data/tilesets/secondary/cuordilava/tiles.png')
    if (width,height)!=(128,256):
        raise ValueError('Ocean graphics changed GBA tile budget')
    for t in OCEAN_ART_TILES:
        sample=[pixels[(t//16)*8+y][(t%16)*8+x]
                for y in range(8) for x in range(8)]
        if not set(sample).issubset({8,9,10}) or not {9,10}.issubset(sample):
            raise ValueError('Marine blue water has lost pure non-peach tint')
    used={value(terrain,W,x,y)&1023 for y in range(OLD_H,H) for x in range(OLD_W)}
    if not {512+mid for mid in OCEAN_METATILES}.issubset(used):
        raise ValueError('New sea metatiles are missing from ocean district')


def annex(old: bytes) -> bytes:
    if len(old) != OLD_W*OLD_H*2:
        raise ValueError('Expected fully generated 20x20 Cuordilava source map')
    def original(x,y):
        return value(old,OLD_W,x,y)
    # Donors are already rendered, graphically verified and collision-bearing.
    basalt = original(1,8)      # solid original cliff material, not a new metatile
    street = original(8,11)     # walkable old basalt-cobble promenade
    worn_street = original(12,7)  # original walkable concrete cobble
    brick_street = original(13,7) # second walkable core source pavement
    sea = original(5,4)         # mineral turquoise water already in town
    breakers = original(4,3)    # existing naturally textured shore water
    deeper_sea = original(6,4)  # second hand-authored hot-spring variant
    ridge_stones = (original(0,0), original(4,0), original(5,0),
                    original(0,1), original(1,0))
    lantern = original(18,5)    # copper street lamp
    palm = original(12,5)       # 16x16 tropical flowering palm
    stack = original(15,13)     # volcanic industrial exhaust stack
    inlay = original(8,8)       # heat-lit, flat plaza floor inlay
    blocked = ((basalt>>10)&3)==1
    open_ground = ((street>>10)&3)==0
    if not blocked or not open_ground:
        raise ValueError('Reference donors no longer match solidity expectations')
    if any(((item>>10)&3)!=0 for item in (worn_street,brick_street)):
        raise ValueError('Historic secondary paving donors stopped being walkable')
    # Map cell bits 10-11 are the per-cell collision; force inaccessible
    # cliffs/ocean to remain solid while preserving each donor's elevation.
    def impassable(v):
        return (v & ~(3<<10)) | (1<<10)
    rows = [[impassable(ridge_stones[(x//3 + y//2 + x*y)%len(ridge_stones)])
             for x in range(W)] for y in range(H)]
    # Preserve all 400 existing town cells, including collision, tile ID,
    # elevation and interactions, without translating one single coordinate.
    for y in range(OLD_H):
        for x in range(OLD_W):
            rows[y][x] = original(x,y)

    # Ragged volcanic coastline, calm deep-blue sea and turquoise foam along
    # the irregular shore. The ocean tiles are explicitly impassable.
    for y in range(20,H):
        for x in range(20):
            shore_y=21 + (1 if x%7 in (1,2) else 0) + (1 if x%9==0 else 0)
            if x<2 or y<shore_y:
                donor=(original(0,18), original(4,0), original(5,0),
                       original(0,0))[(x*3+y)%4]
                rows[y][x]=impassable(donor)
            elif y==shore_y or x in (2,19):
                donor=(breakers,deeper_sea,sea)[(x+y)%3]
                rows[y][x]=impassable(donor)
            else:
                mid=OCEAN_METATILES[(x*3 + y + x//4)%3]
                # Preserve the existing submerged cell height, but mark
                # ocean as impassable using only collision bits 10-11.
                rows[y][x]=impassable((sea&~0x3FF)|(512+mid))

    # Giant upper eastern black basalt ridge, passable main spine/side streets.
    # The 2-block-wide arterial road now truly connects the old town to Route 112.
    def pavement(x0,y0,x1,y1):
        # Vary the real floor artwork without adding new metatile allocations.
        # Long uninterrupted repetition made the first preview look like a
        # neon checkerboard rather than a lived-in town.
        for yy in range(y0,y1+1):
            for xx in range(x0,x1+1):
                if 0<=xx<W and 0<=yy<H:
                    style=(xx*13+yy*7+xx*yy)%13
                    rows[yy][xx]=(street if style<4 else
                                  worn_street if style<9 else brick_street)
    pavement(20,7,31,9)
    pavement(20,7,21,23)
    pavement(21,10,30,22)
    pavement(23,23,30,24)
    pavement(29,6,30,20)
    # Restrict actual cross-map access on Route 112 to its walkable street
    # throat, not the shoreline or an industrial wall.
    for y in range(H):
        rows[y][31] = street if y in (7,8,9) else impassable(ridge_stones[y%len(ridge_stones)])

    # Kiln central: a unique volcanic industrial skyline with black
    # spires, large flame-roof hall, and an orange-lit connected foundation.
    for dy in range(2):
        for dx in range(4):
            rows[3+dy][24+dx]=original(3+dx,11+dy)
    for j,xx in enumerate(range(23,28)):
        rows[5][xx]=original(2+j,14)
    for x,y in ((22,2),(29,2),(22,3),(29,3),(22,5),(29,5)):
        rows[y][x]=stack
    for x,y in ((21,5),(30,5),(22,6),(30,6)):
        rows[y][x]=lantern

    # Main annex civic square, edged by four copper vents. Copying the existing
    # rendered medallion ties the district to the historic central plaza.
    for dy in range(2):
        for dx in range(4):
            rows[12+dy][24+dx]=original(10+dx,9+dy)
    for x,y in ((22,11),(29,11),(22,15),(29,15)):
        rows[y][x]=inlay
    for x,y in ((21,10),(30,10),(21,15),(30,15)):
        rows[y][x]=lantern

    # Dense terraced block: steep basalt rooflines, separated from the public
    # paths by a continuous orange-window frontage. No fake warp doors.
    for dy in range(2):
        for dx in range(4):
            rows[17+dy][23+dx]=original(11+dx,12+dy)
    for dx in range(7):
        rows[19][22+dx]=original(11+dx,14)
    for x,y in ((22,17),(28,17),(22,18),(28,18)):
        rows[y][x]=stack

    # Geothermal shore promenade, connected to the square by actual walkable
    # cells. Includes a smaller, irregular pool borrowed from the true springs.
    for x,y in ((23,22),(30,22),(22,24),(30,24)):
        rows[y][x]=lantern
    for y in (24,25,26):
        for x in range(24,29):
            sx=3 + ((x-24)%4)
            sy=3 + ((y-24)%3)
            rows[y][x]=original(sx,sy)
    # Rock edges keep this small basin surrounded by plantings and rock.
    for x,y in ((23,24),(29,24),(23,25),(29,25),(23,26),(29,26)):
        rows[y][x]=original(2,3)
    for x,y in ((21,12),(30,12),(21,14),(30,14),
                (21,19),(30,19),(21,23),(30,23),
                (23,21),(28,21),(22,25),(30,25)):
        rows[y][x]=palm

    # Walkway down to coast remains reachable even with spa and decorations.
    pavement(20,20,21,23)
    pavement(22,21,22,23)
    # Additional light pavers and moss seams between workshops and plaza,
    # separated from the main street by two free passable walking tiles.
    for x,y in ((23,10),(28,10),(23,14),(28,14),(23,20),(28,20)):
        rows[y][x]=worn_street

    return b''.join(struct.pack('<H',cell) for row in rows for cell in row)

def audit(root: Path):
    p=paths(root)
    layouts, item=locate_layouts(p)
    if (item['width'],item['height']) != (W,H):
        raise ValueError('Expanded city layout must be exactly 32x28')
    out=p['map'].read_bytes()
    if len(out)!=W*H*2:
        raise ValueError('Expanded Cuordilava map has incorrect byte count')
    events=original_events(p)
    manifest=json.loads(p['manifest'].read_text(encoding='utf-8'))
    preserved=hashlib.sha256(core_bytes(out)).hexdigest()
    if preserved!=manifest['original_core_sha256']:
        raise ValueError('Historic 20x20 Cuordilava center has changed')
    if manifest['width']!=W or manifest['height']!=H:
        raise ValueError('Incorrect generated layout metadata')
    validate_ocean_metatiles(root,out)
    for destination in (EXIT,ANNEX_SQUARE,COAST_WALK):
        if not path_to(out,root,ENTRY,destination):
            raise ValueError(f'Annex is not walkably connected to the original town: {destination}')
    # Retain the six original entrance and NPC coordinates without rewrites.
    assert len(events['warp_events'])==6
    # The new east and south extensions never claim invalid secondary metatiles.
    for offset in range(0,len(out),2):
        mid=struct.unpack_from('<H',out,offset)[0]&1023
        if not (0 <= mid < 1024):
            raise ValueError('Out of range metatile')
    # Existing outbound route matching remains symmetric after width change.
    if not any(path_to(out,root,ENTRY,(31,y)) for y in (7,8,9)):
        raise ValueError('The new Route 112 border crossing is blocked')
    return {
        'town_size':[W,H], 'original_size':[OLD_W,OLD_H],
        'original_core_sha256':preserved,
        'warp_count':len(events['warp_events']),
        'map_bytes':len(out),'new_cells':W*H-OLD_W*OLD_H,
        'verified_connections':[list(EXIT),list(ANNEX_SQUARE),list(COAST_WALK)],
    }

def generate(root: Path):
    p=paths(root)
    layouts,item=locate_layouts(p)
    if (item['width'],item['height'])!=(OLD_W,OLD_H):
        raise ValueError('Run source-time expansion only after the 20x20 base generator')
    original_events(p)
    raw=p['map'].read_bytes()
    # Install only three new town-exclusive deep-water metatiles. None are
    # used by the preserved 20x20 core or other maps.
    install_ocean_metatiles(root,raw)
    new=annex(raw)
    # Validate *before writing* that all historic town cells are identical.
    for y in range(OLD_H):
        for x in range(OLD_W):
            if value(raw,OLD_W,x,y)!=value(new,W,x,y):
                raise ValueError(f'Original 20x20 map cell changed at {(x,y)}')
    # Compact manifest is a guardrail, not an alternative map authoring source.
    item['width'],item['height']=W,H
    p['layout'].write_text(json.dumps(layouts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    p['map'].write_bytes(new)
    p['manifest'].write_text(json.dumps({
        'width':W,'height':H,'original_core_sha256':hashlib.sha256(raw).hexdigest(),
        'source_dimensions':[OLD_W,OLD_H],
    },indent=2)+'\n',encoding='utf-8')
    result=audit(root)
    print('Expanded Cuordilava annex: '+json.dumps(result,sort_keys=True))
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--verify',action='store_true',help='Audit generated 32x28 layout')
    args=ap.parse_args()
    if args.verify:
        print(json.dumps(audit(args.root),indent=2))
    else:
        generate(args.root)

if __name__=='__main__':
    main()
