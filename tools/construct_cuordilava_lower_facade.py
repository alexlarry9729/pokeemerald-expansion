#!/usr/bin/env python3
"""Continuous 112x16 warm-glass housing facade for south-east Cuordilava.

This is an eighth *architectural volume*, not a recolour of stock houses:
seven existing ground-floor 16x16 cells become one connected steel/copper
facade with seven inset glowing windows and distinct service infrastructure.

The 20x20 map, elevation/collision bits, event/warp objects and moonlight code
remain unchanged in meaning. Reuses precisely 28 demonstrably unused 8x8
secondary graphics and seven inactive secondary metatiles. No ROM graphics
capacity increase and no shared tilesets are modified.

Run AFTER the existing sculpture, scenery and thermal-basin passes.
"""
from pathlib import Path
import json
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

Y = 14
XS = tuple(range(11, 18))
NEW_METAS = tuple(range(430, 437))
ART_TILES = (
    204,205,206,207,220,221,222,223,230,231,232,233,246,247,
    248,249,262,263,278,279,396,397,398,399,412,413,414,415,
)
EXPECTED_SOURCE_METAS = (24,25,11,26,24,25,11)
assert len(XS) == len(NEW_METAS) == 7 and len(ART_TILES) == 28


class Facade:
    W, H = 112, 16
    def __init__(self):
        self.pix = [[0]*self.W for _ in range(self.H)]
    def p(self,x,y,c):
        if 0 <= x < self.W and 0 <= y < self.H:
            self.pix[y][x] = c
    def box(self,x0,y0,x1,y1,c):
        for y in range(max(y0,0),min(y1+1,self.H)):
            for x in range(max(x0,0),min(x1+1,self.W)):
                self.p(x,y,c)
    def line(self,x0,y0,x1,y1,c):
        dx,dy=abs(x1-x0),-abs(y1-y0)
        sx,sy=(1 if x0<x1 else -1),(1 if y0<y1 else -1)
        err=dx+dy
        while True:
            self.p(x0,y0,c)
            if (x0,y0)==(x1,y1):break
            e=err*2
            if e>=dy:err+=dy;x0+=sx
            if e<=dx:err+=dx;y0+=sy


def illustration():
    a=Facade()
    # Multilevel cornice is drawn continuously across all seven metatiles.
    a.box(0,0,111,15,8)  # private palette 6 near-black iron
    for y,col in ((0,5),(1,6),(2,13),(3,8),(13,5),(14,11),(15,8)):
        a.line(0,y,111,y,col)
    for x in range(3,112,8):
        a.p(x,1,3);a.p(x+1,2,14)
    # Tall recesses create a clearly readable ground-floor windowscape,
    # with orange-lit panes and shadowed steel mullions.
    for i in range(7):
        left=16*i
        a.box(left+2,4,left+13,12,5)
        a.box(left+3,5,left+12,11,8)
        a.box(left+4,5,left+11,11,12)
        for y in (6,8,10):
            a.line(left+5,y,left+10,y,14)
        a.line(left+8,5,left+8,11,5)
        a.line(left+4,9,left+11,9,6)
        a.line(left+3,12,left+12,12,11)
        for x in (left+1,left+14):
            a.line(x,3,x,13,5)
            a.line(x+1,4,x+1,11,6)
        a.p(left+2,3,13);a.p(left+13,3,14)
        # Layered panel pilasters connect visually to the gabled roof above.
        a.box(left,3,left,14,5)
        a.line(left+15,3,left+15,14,5)
        for y in (5,11):
            a.p(left,y,13);a.p(left+15,y,14)
    # Differentiate the storefront-style central service bay from housing:
    # contained cool readout and a short violet vertical conduit.
    a.box(47,4,49,12,8)
    a.line(48,5,48,11,9)
    a.p(48,6,10);a.p(48,10,15)
    a.box(94,4,96,12,8)
    a.line(95,5,95,11,15)
    a.p(95,6,9);a.p(95,10,10)
    # Additional warm copper vents make the building read as occupied.
    for x in (7,23,39,55,71,87,103):
        a.p(x,0,11);a.p(x+1,0,13)
        a.p(x,14,14)
    return a.pix


def project(root):
    root=Path(root)
    return {
        'town': root/'data/layouts/LavaridgeTown/map.bin',
        'meta': root/'data/tilesets/secondary/cuordilava/metatiles.bin',
        'attrs': root/'data/tilesets/secondary/cuordilava/metatile_attributes.bin',
        'primary_meta': root/'data/tilesets/primary/general/metatiles.bin',
        'primary_attrs': root/'data/tilesets/primary/general/metatile_attributes.bin',
        'tiles': root/'data/tilesets/secondary/cuordilava/tiles.png',
        'events': root/'data/maps/LavaridgeTown/map.json',
    }


def index(data, offset):
    return struct.unpack_from('<H',data,offset)[0]


def validate_built(root):
    p=project(root)
    layout=p['town'].read_bytes()
    metas=p['meta'].read_bytes()
    attrs=p['attrs'].read_bytes()
    primary=p['primary_meta'].read_bytes()
    primary_attrs=p['primary_attrs'].read_bytes()
    if (len(layout),len(metas),len(attrs))!=(800,8192,1024):
        raise ValueError('Town dimensions/metatile budget changed')
    used={}
    for i in range(400):
        raw=index(layout,i*2)
        used.setdefault(raw&1023,[]).append((i%20,i//20))
    for mid,x,source_mid in zip(NEW_METAS,XS,EXPECTED_SOURCE_METAS):
        value=index(layout,(Y*20+x)*2)
        if (value&1023)!=512+mid or used[512+mid]!=[(x,Y)]:
            raise ValueError('Private lower facade has leaked or been moved')
        prior_attr=index(primary_attrs,source_mid*2)
        if index(attrs,mid*2)!=prior_attr:
            raise ValueError('House wall behavior not preserved')
        expected_base=primary[source_mid*16:source_mid*16+8]
        if metas[mid*16:mid*16+8]!=expected_base:
            raise ValueError('Lower-floor background layer changed')
        for quad in range(4):
            new_tile=ART_TILES[(x-XS[0])*4+quad]
            entry=index(metas,mid*16+8+quad*2)
            if entry != (6<<12)|(512+new_tile):
                raise ValueError('Missing private facade 4bpp graphics')
    image=p['tiles']
    width,height,rows=png_indexed(image)
    if (width,height)!=(128,256):
        raise ValueError('Unexpected town tileset size')
    warm=0
    for tile in ART_TILES:
        sx,sy=(tile%16)*8,(tile//16)*8
        warm+=sum(c in (11,12,13,14) for row in rows[sy:sy+8] for c in row[sx:sx+8])
    if warm<350:
        raise ValueError(f'Ground-floor windows insufficiently incandescent: {warm}')


def run(root):
    p=project(root)
    layout=bytearray(p['town'].read_bytes())
    metas=bytearray(p['meta'].read_bytes())
    attrs=bytearray(p['attrs'].read_bytes())
    primary=p['primary_meta'].read_bytes()
    primary_attrs=p['primary_attrs'].read_bytes()
    if (len(layout),len(metas),len(attrs))!=(800,8192,1024):
        raise ValueError('Must run facade pass after full secondary tileset generation')
    events=json.loads(p['events'].read_text(encoding='utf-8'))
    reserved={(e['x'],e['y']) for name in
              ('warp_events','coord_events','bg_events','object_events')
              for e in events.get(name,[]) if 'x' in e and 'y' in e}
    if reserved.intersection((x,Y) for x in XS):
        raise ValueError('An NPC, warp, or sign occupies a proposed facade cell')
    known={index(layout,2*i)&1023 for i in range(400)}
    if any(512+mid in known for mid in NEW_METAS):
        raise ValueError('A selected secondary metatile is already active')
    used_tiles={((index(metas,i)&1023)-512) for i in range(0,len(metas),2)
                if (index(metas,i)&1023)>=512}
    occupied=set(ART_TILES)&used_tiles
    if occupied:
        raise ValueError(f'Facade cannot overwrite active tile graphics: {sorted(occupied)}')
    atlas=p['tiles'];width,height,rows=png_indexed(atlas)
    if (width,height)!=(128,256):
        raise ValueError('8x8 atlas is not the expected 512-tile format')
    plte=atlas.read_bytes()
    plte=plte[plte.index(b'PLTE')+4:plte.index(b'PLTE')+52]
    if len(plte)!=48:
        raise ValueError('Indexed 16-colour source palette required')
    pixels=illustration()
    before_layout=bytes(layout)
    before_meta=bytes(metas)
    before_attrs=bytes(attrs)
    for cell,x in enumerate(XS):
        pos=Y*20+x
        raw=index(layout,pos*2)
        old_id=raw&1023
        if old_id!=EXPECTED_SOURCE_METAS[cell]:
            raise ValueError(f'Ground floor target {x},{Y} moved: {old_id}')
        base=primary[old_id*16:old_id*16+8]
        if len(base)!=8:
            raise ValueError('Invalid primary facade base layer')
        mid=NEW_METAS[cell]
        entries=bytearray(base)
        for q in range(4):
            tile=ART_TILES[cell*4+q]
            src_x=16*cell+(q%2)*8
            src_y=(q//2)*8
            dst_x=(tile%16)*8
            dst_y=(tile//16)*8
            for yy in range(8):
                for xx in range(8):
                    rows[dst_y+yy][dst_x+xx]=pixels[src_y+yy][src_x+xx]
            entries+=struct.pack('<H',0x6000|(512+tile))
        metas[mid*16:(mid+1)*16]=entries
        attrs[mid*2:mid*2+2]=primary_attrs[old_id*2:old_id*2+2]
        struct.pack_into('<H',layout,pos*2,(raw&~0x3ff)|(512+mid))
    for i in range(400):
        a=index(before_layout,i*2)
        b=index(layout,i*2)
        if (a>>10)!=(b>>10) or (i//20!=Y or i%20 not in XS) and a!=b:
            raise ValueError('Background/elevation/collision changed elsewhere')
    if len(metas)!=len(before_meta) or len(attrs)!=len(before_attrs):
        raise ValueError('4bpp and metatile allocation exceeded GBA budget')
    touched=set(NEW_METAS)
    if any(metas[i*16:(i+1)*16]!=before_meta[i*16:(i+1)*16]
           for i in range(512) if i not in touched):
        raise ValueError('Attempted to modify an unrelated metatile')
    if any(attrs[i*2:(i+1)*2]!=before_attrs[i*2:(i+1)*2]
           for i in range(512) if i not in touched):
        raise ValueError('Attempted to modify unrelated collision attributes')
    write_png(atlas,128,256,rows,plte)
    p['town'].write_bytes(layout)
    p['meta'].write_bytes(metas)
    p['attrs'].write_bytes(attrs)
    validate_built(root)
    print('Cuordilava: new connected 112x16 bottom-right furnace-glass storefront; '
          '7 private metatiles, 28 reused 8x8 tiles; original door/warp/collision preserved')


if __name__=='__main__':
    run(Path(__file__).resolve().parents[1])
