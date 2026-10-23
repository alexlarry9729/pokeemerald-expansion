#!/usr/bin/env python3
"""Cuordilava industrial architecture, phase II.

Reworks only dedicated town-private indexed 4bpp graphics. No changes to map,
metatiles, collision flags, doors, event objects or the approved night engine.
Deterministic second pass: call AFTER apply_cuordilava_industrial_art.py.
"""
from pathlib import Path
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

PRIMARY = {
    # These primary building tiles are used ONLY on the bottom-right houses.
    "home steel roofs": [162,163,164,178,179,180,194,195,196,210,211,212],
    "home molten window seams": [226,227,228,229,230,231,242,243,244],
    # These tiles are confined to the bottom-left civic roof.
    "civic thermal shutters": [340,341,356,357,372],
}
SECONDARY = {
    # Gym/upper-right factory has a dedicated 4bpp tile set.
    "gym blast roof": [424,425,426,427],
    "gym furnace marquee": [428,429,430,431,441,442,443,444,445,446,447],
    "gym copper facades": [448,449,450,451,452,453,454,455,457],
    # Custom overlay on the upper-center building only.
    "upper-center roof conduits": [258,259,260,261],
}

def paint(rows, tiles, pattern):
    changed = 0
    for tid in tiles:
        ox,oy = tid%16*8,tid//16*8
        assert oy+8<=len(rows),tid
        original = [[rows[oy+y][ox+x] for x in range(8)] for y in range(8)]
        def dot(x,y,color):
            nonlocal changed
            if 0<=x<8 and 0<=y<8 and original[y][x]!=0:
                if rows[oy+y][ox+x]!=color:
                    changed+=1
                rows[oy+y][ox+x]=color
        def seg(a,b,c,d,color):
            dx=abs(c-a);dy=-abs(d-b);sx=1 if a<c else -1
            sy=1 if b<d else -1;err=dx+dy
            while True:
                dot(a,b,color)
                if (a,b)==(c,d):break
                e2=2*err
                if e2>=dy:err+=dy;a+=sx
                if e2<=dx:err+=dx;b+=sy
        pattern(dot,seg,tid)
    return changed

def cassette(dot,seg,t):
    # Near-black bolted steel cassettes with broken magma/cyan seams.
    for y in range(1,7):
        for x in range(1,7):dot(x,y,8)
    for x in range(1,7):dot(x,1,6);dot(x,6,6)
    for y in range(2,6):dot(1,y,5);dot(6,y,5)
    for x in (2,5):
        for y in (2,5):dot(x,y,3)
    if t%3==0:seg(3,2,3,5,12);seg(4,2,4,5,11)
    elif t%3==1:seg(2,3,5,3,14);seg(2,4,5,4,12)
    else:seg(3,3,4,4,9);dot(4,3,10)

def furnace(dot,seg,t):
    # Hot, shuttered furnace lights framed by black steel, never flat orange.
    for y in range(1,7):
        for x in range(1,7):dot(x,y,8)
    for x in range(1,7):dot(x,1,6);dot(x,6,6)
    for y in range(2,6):dot(1,y,5);dot(6,y,5)
    seg(2,3,5,3,12);seg(2,4,5,4,14)
    dot(3,2,13);dot(4,5,13);dot(3,4,11);dot(4,3,11)

def alloy(dot,seg,t):
    for y in range(1,7):
        for x in range(1,7):dot(x,y,7)
    for y in (1,6):seg(1,y,6,y,5)
    for x in (1,6):seg(x,2,x,5,8)
    for y in (2,5):seg(2,y,5,y,8)
    if t%4==0:seg(2,3,5,3,12);dot(4,4,11)
    elif t%4==1:seg(3,2,3,5,9);seg(4,2,4,5,10)
    elif t%4==2:seg(2,4,5,4,12)
    else:dot(2,3,3);dot(5,3,3)

def glow(dot,seg,t):
    for y in (2,3,4):seg(2,y,5,y,12 if y!=3 else 14)
    for x in (1,6):seg(x,1,x,6,7)
    for y in (1,6):seg(1,y,6,y,5)
    dot(3,3,11);dot(5,5,10)

def hotfacade(dot,seg,t):
    for y in range(1,7):
        for x in range(1,7):dot(x,y,8)
    seg(1,1,6,1,5);seg(1,6,6,6,6)
    for x in (1,6):seg(x,2,x,5,7)
    for y in (2,4):seg(2,y,5,y,14);dot(3,y,12)
    for x in (2,5):dot(x,5,10)

def pipes(dot,seg,t):
    for x in (2,3,4):seg(x,0,x,7,7 if x!=3 else 11)
    seg(3,0,3,7,14)
    for y in (1,6):seg(1,y,5,y,12)
    dot(5,3,10);dot(5,4,9)

def process(path,groups):
    source=path.read_bytes()
    width,height,rows=png_indexed(path)
    assert width==128 and height in (232,256)
    palette=source[source.index(b"PLTE")+4:source.index(b"PLTE")+52]
    assert len(palette)==48
    original=[line[:] for line in rows]
    ops={
        "home steel roofs":alloy,
        "home molten window seams":glow,
        "civic thermal shutters":cassette,
        "gym blast roof":cassette,
        "gym furnace marquee":furnace,
        "gym copper facades":hotfacade,
        "upper-center roof conduits":pipes,
    }
    total=0
    for role,ids in groups.items():
        total+=paint(rows,ids,ops[role])
    changed=sum(1 for old,new in zip(original,rows) for a,b in zip(old,new) if a!=b)
    assert total>=250 and changed>=250, (path,total,changed)
    write_png(path,width,height,rows,palette)
    width2,height2,check=png_indexed(path)
    assert (width2,height2,check)==(width,height,rows)
    print(f"Cuordilava {path} phase II: {changed} changed 4bpp pixels")
    return changed

def assert_building_only(root,groups,part):
    """No active building tile may also color the town's paths or hot springs."""
    import struct
    m=(root/"data/layouts/LavaridgeTown/map.bin").read_bytes()
    p=(root/"data/tilesets/primary/general/metatiles.bin").read_bytes()
    s=(root/"data/tilesets/secondary/cuordilava/metatiles.bin").read_bytes()
    assert len(m)==800 and len(p)%16==0 and len(s)%16==0
    active={}
    for y in range(20):
        for x in range(20):
            encoded=struct.unpack_from("<H",m,2*(y*20+x))[0]&1023
            table=s if encoded>=512 else p
            mi=encoded-512 if encoded>=512 else encoded
            assert (mi+1)*16<=len(table),(mi,x,y)
            for slot in range(8):
                entry=struct.unpack_from("<H",table,mi*16+slot*2)[0]&1023
                source="secondary" if entry>=512 else "primary"
                tid=entry-512 if entry>=512 else entry
                active.setdefault((source,tid),set()).add((x,y))
    def allowed(role,x,y):
        if role.startswith("home "):
            return 11<=x<19 and 12<=y<16
        if role.startswith("civic "):
            return 2<=x<9 and 11<=y<16
        if role.startswith("gym "):
            return 14<=x<19 and 1<=y<7
        if role.startswith("upper-center "):
            return 8<=x<12 and 2<=y<8
        return False
    for role,ids in groups.items():
        for tid in ids:
            locations=active.get((part,tid),set())
            if not locations:
                raise ValueError(f"{part} tile {tid} for {role} unused by Cuordilava")
            foreign=[(x,y) for x,y in locations if not allowed(role,x,y)]
            if foreign:
                raise ValueError(f"{part} tile {tid} for {role} contaminates paths/terme {foreign}")
    print(f"{part}: all {sum(map(len,groups.values()))} tiles used exclusively on their buildings")


def main(root=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parents[1]
    out=[]
    for part,groups in (("primary",PRIMARY),("secondary",SECONDARY)):
        assert_building_only(root,groups,part)
        p=root/f"data/tilesets/{part}/cuordilava/tiles.png"
        out.append((part,process(p,groups)))
    print("Cuordilava architecture phase II - indexed pixels changed:",out)

if __name__=="__main__":
    main()
