#!/usr/bin/env python3
"""Scenic 20x20 Lavaridge dressing: palms, furnace chimneys, magma lamps, cascade.

23 new collision-preserving private secondary metatiles (489..511), produced
AFTER the 48 civic landmarks. No global or shared graphics are modified.
"""
from pathlib import Path
import json
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

PLACEMENTS = {
    "palm": ((19,1),(18,3),(12,5),(13,5),(12,6),(13,6),(18,6),(1,7)),
    "chimney": ((2,12),(7,12),(15,13),(17,13),(15,1),(8,2)),
    "lamp": ((18,5),(18,14),(7,13),(1,11),(0,8)),
    "cascade": ((1,4),(2,4),(1,5),(2,5)),
}
assert sum(map(len, PLACEMENTS.values()))==23

def illustration(kind):
    art=[[0]*16 for _ in range(16)]
    def p(x,y,c):
        if 0<=x<16 and 0<=y<16:art[y][x]=c
    def rect(x0,y0,x1,y1,c):
        for yy in range(y0,y1+1):
            for xx in range(x0,x1+1):p(xx,yy,c)
    def line(x0,y0,x1,y1,c):
        dx,dy=abs(x1-x0),-abs(y1-y0)
        sx,sy=(1 if x0<x1 else -1),(1 if y0<y1 else -1)
        err=dx+dy
        while True:
            p(x0,y0,c)
            if (x0,y0)==(x1,y1):break
            e=2*err
            if e>=dy:err+=dy;x0+=sx
            if e<=dx:err+=dx;y0+=sy
    if kind=="palm":
        rect(7,7,8,14,8);line(7,8,7,14,11);line(8,9,8,14,13)
        for x,y in ((6,14),(9,14),(6,15),(9,15)):p(x,y,8)
        for x,y in ((1,7),(3,3),(6,1),(9,1),(13,3),(15,7),(13,10),(2,10)):
            line(8,6,x,y,15)
        for x0,y0,x1,y1 in ((1,7,4,8),(3,3,5,5),(5,2,7,4),
                             (9,2,11,4),(12,3,14,6),(12,8,15,9),
                             (2,9,5,10),(10,9,13,11)):
            line(x0,y0,x1,y1,10)
        rect(7,5,9,7,15);p(8,6,11);p(9,5,14)
        for x,y in ((2,12),(13,13),(4,14),(11,12)):
            p(x,y,11);p(x+1,y,14)
    elif kind=="chimney":
        rect(4,4,12,15,8)
        for y in range(5,15):
            p(5,y,5);p(11,y,5)
            for x in (7,8,9):p(x,y,12 if y%3 else 14)
            p(6,y,11)
        rect(3,2,13,4,8);line(3,2,13,2,6);line(4,3,12,3,5)
        rect(5,0,11,1,8);line(6,0,10,0,13)
        for x,y in ((3,0),(13,0),(2,2),(14,3)):
            p(x,y,12);p(x,y+1,11)
        for y in (6,11):line(3,y,13,y,6)
        p(4,6,15);p(12,11,15)
    elif kind=="cascade":
        # Transparent outer pixels show the original cliff behind teal flow.
        for y in range(16):
            p(3,y,7);p(12,y,7)
            for x in range(4,12):p(x,y,9 if (x+y)%4 else 10)
            for x in (4,7,10):
                if (y*3+x)%7 in (0,1):p(x,y,1)
            if y in (0,7,15):
                for x in (5,8,11):p(x,y,10)
        for x in (2,13):
            for y in (0,6,12):p(x,y,6)
    else:
        rect(7,6,8,15,8)
        line(6,14,9,14,5);line(4,15,11,15,8)
        rect(5,3,10,7,8);rect(6,4,9,6,12)
        p(7,4,14);p(8,5,11);p(7,6,13)
        line(4,3,11,3,6)
        p(7,0,12);p(7,1,14);p(7,2,13)
        p(3,5,13);p(12,5,13);line(4,7,11,7,5)
        p(6,11,15);p(9,11,10)
    from polish_cuordilava_scenery import polish_scenery
    return polish_scenery(art,kind)

def run(root:Path):
    root=Path(root)
    town=root/"data/layouts/LavaridgeTown/map.bin"
    metap=root/"data/tilesets/secondary/cuordilava/metatiles.bin"
    attrp=root/"data/tilesets/secondary/cuordilava/metatile_attributes.bin"
    primary=root/"data/tilesets/primary/general/metatiles.bin"
    priattr=root/"data/tilesets/primary/general/metatile_attributes.bin"
    atlas=root/"data/tilesets/secondary/cuordilava/tiles.png"
    m=bytearray(town.read_bytes());meta=bytearray(metap.read_bytes());attr=bytearray(attrp.read_bytes())
    pri=primary.read_bytes();pa=priattr.read_bytes()
    width,height,pixels=png_indexed(atlas)
    assert len(m)==800 and len(meta)==489*16 and len(attr)==489*2
    assert (width,height)==(128,256)
    raw=atlas.read_bytes()
    palette=raw[raw.index(b"PLTE")+4:raw.index(b"PLTE")+52]
    assert len(palette)==48
    events=json.loads((root/"data/maps/LavaridgeTown/map.json").read_text())
    reserved={(int(e["x"]),int(e["y"])) for group in
              ("object_events","warp_events","coord_events","bg_events")
              for e in events.get(group,[]) if "x" in e and "y" in e}
    positions={xy for cells in PLACEMENTS.values() for xy in cells}
    assert len(positions)==23 and not positions.intersection(reserved)
    prior=bytes(m)
    visible=set()
    for off in range(0,len(m),2):
        mid=struct.unpack_from("<H",m,off)[0]&1023
        bank,index=(meta,mid-512) if mid>=512 else (pri,mid)
        for slot in range(8):
            tile=struct.unpack_from("<H",bank,index*16+slot*2)[0]&1023
            if tile>=512:visible.add(tile-512)
    avoid=set(range(160,172))|set(range(288,296))
    spare=[tid for tid in range(512) if tid not in visible and tid not in avoid]
    assert len(spare)>=16, "No more safely unused Cuordilava graphics"
    images={}
    for group,kind in enumerate(("palm","chimney","lamp","cascade")):
        art=illustration(kind)
        ids=spare[group*4:(group+1)*4];images[kind]=ids
        for quadrant,tid in enumerate(ids):
            dx=(quadrant%2)*8;dy=(quadrant//2)*8
            ox=(tid%16)*8;oy=(tid//16)*8
            for y in range(8):
                for x in range(8):pixels[oy+y][ox+x]=art[dy+y][dx+x]
    for kind,cells in PLACEMENTS.items():
        for placement_index,(x,y) in enumerate(cells):
            index=y*20+x
            previous=struct.unpack_from("<H",m,index*2)[0]
            assert ((previous>>10)&3)==1,(kind,x,y,"must be impassable")
            oldid=previous&1023
            bank,attributes,idx=(meta,attr,oldid-512) if oldid>=512 else (pri,pa,oldid)
            body=bytearray(bank[idx*16:idx*16+8])
            old_attribute=attributes[idx*2:idx*2+2]
            colour_bank=9 if kind=="palm" else 8 if kind=="cascade" else 6
            # Mirror each alternate *whole* 16x16 palm crown, not each
            # quadrant in place: swap left/right source quadrants and apply
            # GBA H-flip to both. This supplies two distinct canopy shapes
            # without spending a single extra 8x8 tile or metatile.
            mirrored = kind=="palm" and placement_index%2==1
            for quadrant in range(4):
                source_quadrant = quadrant ^ 1 if mirrored else quadrant
                tid = images[kind][source_quadrant]
                entry = (colour_bank<<12) | (512+tid)
                if mirrored:
                    entry |= 0x0400
                body += struct.pack("<H",entry)
            newid=len(meta)//16
            assert newid<512
            meta+=body;attr+=old_attribute
            struct.pack_into("<H",m,index*2,(previous&~1023)|(512+newid))
            assert attr[newid*2:newid*2+2]==old_attribute
    assert len(meta)==512*16 and len(attr)==512*2
    for cell in range(400):
        before=struct.unpack_from("<H",prior,cell*2)[0]
        after=struct.unpack_from("<H",m,cell*2)[0]
        assert (before>>10)==(after>>10),("Collision/elevation changed",cell)
        if (cell%20,cell//20) not in positions:assert before==after
    write_png(atlas,128,256,pixels,palette)
    assert png_indexed(atlas)==(128,256,pixels)
    town.write_bytes(m);metap.write_bytes(meta);attrp.write_bytes(attr)
    print("Cuordilava scenery: 8 palms, 6 rooftop chimneys, 5 magma lamps, 4 waterfall cells;")
    print("23 additional private metatiles, fixed 20x20 and exact original collision/warps.")

if __name__=="__main__":run(Path(__file__).resolve().parents[1])
