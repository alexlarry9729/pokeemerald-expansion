#!/usr/bin/env python3
"""Turn four noisy rear-Center copper scaffolds into ONE readable slate roof.

The original industrial redraw painted orange ladders on the *upper-layer*
graphics of blocked x8..11,y3, directly behind the Center's main building.
They visually merged with the cliff/pavement and looked like broken roof
pixels. These four metatiles already use the SAME four unique, private,
palette-6 8x8 characters 258..261. Re-author those exact four characters
into a calm 16x16 parapet/roof plane. No graphics or metatiles are added.

Crucially, this is NOT the (6..9,y1) raised hot-spring staircase: it keeps
the original stairs restored and independently checked by the previous pass.
"""
from pathlib import Path
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

CELL_SET={(8,3),(9,3),(10,3),(11,3)}
METATILES={72,73,74,77}
CHARS=(258,259,260,261)

def art():
    rows=[[8]*16 for _ in range(16)]
    def dot(x,y,c):
        if 0<=x<16 and 0<=y<16:rows[y][x]=c
    def line(x0,x1,y,c):
        for x in range(x0,x1+1):dot(x,y,c)

    # 3-pixel dark roof ridge against dark mountain, followed by a broad
    # SLATE plane rather than four vertical gold ladders.
    line(0,15,0,8)
    line(1,14,1,5)
    line(1,14,2,6)
    for y in range(3,12):
        for x in range(1,15):
            if y in (3,4):
                c=6 if x not in (1,14) else 8
            elif y in (10,11):
                c=5 if y==10 else 6
            else:
                c=3 if x in (1,14) else 5
            dot(x,y,c)
    # Just two shallow recessed vents, spaced on a uniform field.
    for x0 in (3,10):
        for y in range(6,10):
            for x in range(x0,x0+3):
                dot(x,y,8)
        dot(x0+1,7,9) # teal distant light, never orange grid
        dot(x0+1,8,10)
    # A physically thick eave makes the roof read above, not as another
    # layer of pavement. Small copper anchor bolts are intentional.
    line(0,15,12,7)
    line(0,15,13,8)
    line(0,15,14,5)
    line(0,15,15,8)
    for x in (2,13):dot(x,14,12)
    return rows


def paths(root):
    root=Path(root)
    return (
        root/"data/layouts/LavaridgeTown/map.bin",
        root/"data/tilesets/secondary/cuordilava/metatiles.bin",
        root/"data/tilesets/secondary/cuordilava/tiles.png",
        root/"data/tilesets/secondary/cuordilava/metatile_attributes.bin",
        root/"data/maps/LavaridgeTown/map.json",
    )


def word(data,off):
    return struct.unpack_from("<H",data,off)[0]


def check_ownership(m,meta):
    hits={}
    for i in range(400):
        mid=word(m,i*2)&1023
        if mid<512:continue
        row=meta[(mid-512)*16:(mid-511)*16]
        for j in range(8):
            w=word(row,j*2)
            tid=(w&1023)-512
            if tid in CHARS:
                hits.setdefault(tid,set()).add((i%20,i//20))
                if (i%20,i//20) not in CELL_SET or ((w>>12)!=6):
                    raise ValueError(f"Center roof tile {tid} is also used outside its four private cells")
    if set(hits)!=set(CHARS):
        raise ValueError(f"Some of the four private roof tile characters are missing: {hits}")
    if any(hits[t]!=CELL_SET for t in CHARS):
        raise ValueError(f"Rear-Center slate source is shared with other buildings: {hits}")
    for (x,y) in CELL_SET:
        mid=word(m,(20*y+x)*2)&1023
        if mid-512 not in METATILES or (word(m,(20*y+x)*2)>>10)&3 != 1:
            raise ValueError(f"Original blocked rear Center roof shifted at {(x,y)}")


def validate_built(root):
    m,meta,atlas,attrs,events=paths(root)
    a,b=m.read_bytes(),meta.read_bytes()
    if (len(a),len(b),len(attrs.read_bytes()))!=(800,8192,1024):
        raise ValueError("Rear roof would change original map/metatile capacity")
    check_ownership(a,b)
    w,h,px=png_indexed(atlas)
    if (w,h)!=(128,256):
        raise ValueError("No new GBA tiles can be allocated to the rear roof")
    art16=art()
    for j,tid in enumerate(CHARS):
        tx,ty=(tid%16)*8,(tid//16)*8
        ox=(j%2)*8;oy=(j//2)*8
        for y in range(8):
            for x in range(8):
                if px[ty+y][tx+x]!=art16[oy+y][ox+x]:
                    raise ValueError(f"Rear Center roof {tid} still has old fragmented scaffold graphics")
    return True


def run(root):
    mp,metap,atlas,attrp,eventp=paths(root)
    m,meta,attrs,events=(p.read_bytes() for p in (mp,metap,attrp,eventp))
    if (len(m),len(meta),len(attrs))!=(800,8192,1024):
        raise ValueError("Roof cleanup requires all original slots and collisions")
    check_ownership(m,meta)
    w,h,px=png_indexed(atlas)
    if (w,h)!=(128,256):
        raise ValueError("Unexpected private GBA graphics dimensions")
    data=atlas.read_bytes()
    palette=data[data.index(b'PLTE')+4:data.index(b'PLTE')+52]
    if len(palette)!=48:
        raise ValueError("Roof palette must stay 16 indexed colours")
    old=[row[:] for row in px]
    design=art()
    changed=0
    for i,tid in enumerate(CHARS):
        tx,ty=(tid%16)*8,(tid//16)*8
        ox,oy=(i%2)*8,(i//2)*8
        for y in range(8):
            for x in range(8):
                new=design[oy+y][ox+x]
                if px[ty+y][tx+x]!=new:
                    changed+=1
                px[ty+y][tx+x]=new
    if changed<80:
        raise ValueError(f"Old orange grid roof was not replaced: only {changed} changes")
    for y in range(h):
        for x in range(w):
            if ((y//8)*16+x//8) not in CHARS and old[y][x]!=px[y][x]:
                raise ValueError("Center roof treatment leaked to unrelated atlas art")
    write_png(atlas,w,h,px,palette)
    validate_built(root)
    if mp.read_bytes()!=m or metap.read_bytes()!=meta or attrp.read_bytes()!=attrs or eventp.read_bytes()!=events:
        raise ValueError("Rear roof pixel cleanup modified events, collision or terrain")
    print(f"Cuordilava rear Center: {changed} scaffold pixels replaced by "
          "continuous slate/teal eaves using exactly 4 preexisting 8x8 "
          "characters, with original hot-spring stairs untouched")


if __name__=='__main__':
    run(Path(__file__).resolve().parents[1])
