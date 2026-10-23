#!/usr/bin/env python3
"""Four flat, copper-traced thermal vents set into Cuordilava's civic pavement.

This stage reuses four remaining unreferenced 8x8 indexed graphics (506..509)
and one inactive town-only secondary metatile (424), placing the SAME compact
16x16 inlaid ground ornament at four verified open plaza cells. The graphic is
a flush pavement motif, not a new obstacle. Its underlay and behavior are exact
copies of the original primary floor and all map collision/elevation bits stay.

Runs after housing/Gym facade construction, never edits any sprite or script.
"""
from pathlib import Path
import json
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

CELLS = ((8,8),(16,8),(8,11),(16,11))
METATILE = 424
FLOOR_METATILE = 1
TILES = (506,507,508,509)


def u16(v,off):
    return struct.unpack_from('<H',v,off)[0]


def paths(root):
    root=Path(root)
    return {
        'map':root/'data/layouts/LavaridgeTown/map.bin',
        'meta':root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        'attr':root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        'primary':root/'data/tilesets/primary/general/metatiles.bin',
        'primary_attr':root/'data/tilesets/primary/general/metatile_attributes.bin',
        'img':root/'data/tilesets/secondary/cuordilava/tiles.png',
        'events':root/'data/maps/LavaridgeTown/map.json',
    }


def drawing():
    """Inset iron grille, dark basalt joints and a single small molten core."""
    pix=[[0]*16 for _ in range(16)]
    def p(x,y,c):
        if 0<=x<16 and 0<=y<16:pix[y][x]=c
    # No full opaque rectangle: original path cobbles show at four corners.
    for y in range(2,14):
        for x in range(2,14):
            if x in (2,13) or y in (2,13):
                p(x,y,5 if (x+y)%4 else 13)
            else:
                p(x,y,8)
    # Louvered surface lies flat on the basalt paving.
    for yy in (4,6,8,10,12):
        for xx in range(4,12):
            p(xx,yy,6)
            if xx in (4,11):p(xx,yy,5)
    for xx in (4,11):
        for yy in range(3,13):p(xx,yy,5)
    # Copper tracery draws attention to the inlaid small flame.
    for x,y in ((5,3),(10,3),(3,5),(12,5),(3,10),(12,10),(5,12),(10,12)):
        p(x,y,11);p(x+1,y,13)
    for y,xs in ((5,(7,8)),(6,(6,7,8,9)),(7,(6,7,8,9)),
                 (8,(7,8)),(9,(7,8))):
        for x in xs:p(x,y,12 if y%2 else 14)
    p(7,4,11);p(8,4,14)
    # A handful of tiny teal/cyan maintenance studs, not an entire blue grid.
    for x,y in ((3,3),(12,3),(3,12),(12,12)):
        p(x,y,9)
    return pix


def validate_built(root):
    p=paths(root)
    layout=p['map'].read_bytes()
    meta=p['meta'].read_bytes()
    attr=p['attr'].read_bytes()
    pri=p['primary'].read_bytes()
    pattr=p['primary_attr'].read_bytes()
    if (len(layout),len(meta),len(attr))!=(800,8192,1024):
        raise ValueError('Town dimensions or tile capacity changed')
    used={(i%20,i//20) for i in range(400)
          if (u16(layout,i*2)&1023)==512+METATILE}
    if used!=set(CELLS):
        raise ValueError('Civic hot-vent placement has leaked to another map cell')
    if meta[METATILE*16:METATILE*16+8]!=pri[FLOOR_METATILE*16:FLOOR_METATILE*16+8]:
        raise ValueError('Original walkable cobble base not preserved')
    if u16(attr,METATILE*2)!=u16(pattr,FLOOR_METATILE*2):
        raise ValueError('Civic hot vents altered movement or interaction')
    for q,tile in enumerate(TILES):
        actual=u16(meta,METATILE*16+8+q*2)
        if actual != (6<<12)|(512+tile):
            raise ValueError('Inlaid copper grille lost its original 4bpp art')
    for x,y in CELLS:
        if (u16(layout,(y*20+x)*2)>>10)&3:
            # Every selected original floor is flat/elevation zero.
            raise ValueError('An inlaid civic vent became collidable/elevated')
    w,h,pix=png_indexed(p['img'])
    if (w,h)!=(128,256):
        raise ValueError('Invalid private city indexed GBA atlas size')
    pixels=[pix[(tid//16)*8+dy][(tid%16)*8+dx]
            for tid in TILES for dy in range(8) for dx in range(8)]
    if sum(c in (11,12,13,14) for c in pixels)<25:
        raise ValueError('Copper/magma crest has become invisible')


def run(root):
    p=paths(root)
    layout=bytearray(p['map'].read_bytes())
    meta=bytearray(p['meta'].read_bytes())
    attrs=bytearray(p['attr'].read_bytes())
    pri=p['primary'].read_bytes()
    pattr=p['primary_attr'].read_bytes()
    if (len(layout),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError('Run plaza pass on fully generated city')
    events=json.loads(p['events'].read_text(encoding='utf-8'))
    reserved={(e['x'],e['y']) for kind in
              ('warp_events','coord_events','bg_events','object_events')
              for e in events.get(kind,[]) if 'x' in e and 'y' in e}
    if reserved.intersection(CELLS):
        raise ValueError('Cannot place a floor inlay under an event actor/warp')
    used={u16(layout,i*2)&1023 for i in range(400)}
    if 512+METATILE in used:
        raise ValueError('Selected town-only vent metatile is already occupied')
    for x,y in CELLS:
        old=u16(layout,(y*20+x)*2)
        if (old&1023)!=FLOOR_METATILE or old>>10:
            raise ValueError(f'Plaza cobbles moved at {x},{y}')
    used_tiles={(u16(meta,i)&1023)-512 for i in range(0,len(meta),2)
                if (u16(meta,i)&1023)>=512}
    if used_tiles.intersection(TILES):
        raise ValueError('Private atlas vent graphics are already in use')
    src=p['img'];w,h,pix=png_indexed(src)
    if (w,h)!=(128,256):
        raise ValueError('Unexpected 4bpp indexed atlas dimensions')
    png=src.read_bytes()
    palette=png[png.index(b'PLTE')+4:png.index(b'PLTE')+52]
    if len(palette)!=48:
        raise ValueError('Expected 16-index palette')
    before_map=bytes(layout)
    before_meta=bytes(meta)
    before_attr=bytes(attrs)
    a=drawing()
    overlay=bytearray(pri[FLOOR_METATILE*16:FLOOR_METATILE*16+8])
    for q,tid in enumerate(TILES):
        overlay+=struct.pack('<H',(6<<12)|(512+tid))
        x0,y0=(tid%16)*8,(tid//16)*8
        x1,y1=(q%2)*8,(q//2)*8
        for y in range(8):
            for x in range(8):
                pix[y0+y][x0+x]=a[y1+y][x1+x]
    meta[METATILE*16:METATILE*16+16]=overlay
    attrs[METATILE*2:METATILE*2+2]=pattr[FLOOR_METATILE*2:FLOOR_METATILE*2+2]
    for x,y in CELLS:
        raw=u16(layout,(y*20+x)*2)
        struct.pack_into('<H',layout,(y*20+x)*2,(raw&~1023)|(512+METATILE))
    for i in range(400):
        prev,now=u16(before_map,i*2),u16(layout,i*2)
        if prev>>10!=now>>10 or ((i%20,i//20) not in CELLS and prev!=now):
            raise ValueError('Unexpected civic path or collision edit')
    if any(meta[i*16:i*16+16]!=before_meta[i*16:i*16+16]
           for i in range(512) if i!=METATILE):
        raise ValueError('Civic inlay altered another metatile')
    if any(attrs[i*2:i*2+2]!=before_attr[i*2:i*2+2]
           for i in range(512) if i!=METATILE):
        raise ValueError('Civic inlay altered other terrain attributes')
    write_png(src,128,256,pix,palette)
    p['map'].write_bytes(layout)
    p['meta'].write_bytes(meta)
    p['attr'].write_bytes(attrs)
    validate_built(root)
    print('Cuordilava civic plaza: four flat magma-copper floor inlays; '
          'all original events, walking tiles and collision retained')


if __name__=='__main__':
    run(Path(__file__).resolve().parents[1])
