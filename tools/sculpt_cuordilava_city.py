#!/usr/bin/env python3
"""Cuordilava: structural city landmarks, not metal pixels on stock houses.

Creates 48 new 16x16 graphical metatiles and uses them to construct connected
multi-metatile architectural murals on roofs, a volcanic plaza crest and a
thermae guardrail. The 20x20 town dimensions, warps, NPCs, special triggers,
collision attributes and day/night engine are protected. Operates only on the
private Cuordilava secondary tileset and LavaridgeTown layout.
Run AFTER apply_cuordilava_industrial_art.py in an unmodified source checkout.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

# Each panel forms ONE continuous 64x32 (or 64x16) illustration.
# All locations are existing roof/terrace/plaza cells, never doors or warps.
LANDMARKS = (
    ("POKEMON_CENTER_INDUSTRIAL_REACTOR", 8, 4, 4, 2),
    ("POKE_MART_TECHNICAL_FACADE", 14, 3, 4, 2),
    ("FLANNERY_GYM_MOLTEN_FORGE", 3, 11, 4, 2),
    ("CENTRAL_VOLCANIC_PLAZA_CREST", 10, 9, 4, 2),
    ("THERMAL_BASIN_BRIDGE_RAIL", 3, 10, 4, 1),
    ("HOUSING_MAGMA_TERRACES", 11, 12, 4, 2),
    ("GYM_FORGE_FACADE", 3, 13, 4, 1),
)
assert sum(w*h for _,_,_,w,h in LANDMARKS)==48

def rgb_readable(rows):
    return all(0 <= p <= 15 for row in rows for p in row)

class Art:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.pix=[[0]*w for _ in range(h)]
    def pixel(self,x,y,c):
        if 0<=x<self.w and 0<=y<self.h:
            self.pix[y][x]=c
    def rect(self,x0,y0,x1,y1,c,fill=True):
        for y in range(max(y0,0),min(y1+1,self.h)):
            for x in range(max(x0,0),min(x1+1,self.w)):
                if fill or y in (y0,y1) or x in (x0,x1):
                    self.pixel(x,y,c)
    def line(self,x0,y0,x1,y1,c):
        dx=abs(x1-x0);dy=-abs(y1-y0)
        sx=1 if x0<x1 else -1;sy=1 if y0<y1 else -1
        err=dx+dy
        while True:
            self.pixel(x0,y0,c)
            if x0==x1 and y0==y1: break
            t=err*2
            if t>=dy:err+=dy;x0+=sx
            if t<=dx:err+=dx;y0+=sy
    def ring(self,cx,cy,r,c,width=2):
        for y in range(cy-r-1,cy+r+2):
            for x in range(cx-r-1,cx+r+2):
                d=(x-cx)*(x-cx)+(y-cy)*(y-cy)
                if (r-width)**2<=d<=r*r:self.pixel(x,y,c)
    def tube(self,x0,y0,x1,y1):
        self.line(x0,y0,x1,y1,5)
        if x0==x1:
            self.line(x0+1,y0,x1+1,y1,14)
            self.line(x0+2,y0,x1+2,y1,12)
        else:
            self.line(x0,y0+1,x1,y1+1,14)
            self.line(x0,y0+2,x1,y1+2,12)

def roof_base(a,mode):
    a.rect(0,0,a.w-1,a.h-1,8)
    # An intentional unified silhouette across the full building width.
    a.rect(2,3,a.w-3,a.h-2,1)
    a.rect(2,3,a.w-3,a.h-2,5,False)
    a.rect(4,5,a.w-5,a.h-4,8)
    # Large dark steel plates with inset seams and bolt heads, not noisy pixels.
    for x in range(8,a.w-6,12):
        a.line(x,4,x,a.h-5,2)
        for y in (7,a.h-7):
            a.pixel(x-2,y,4);a.pixel(x+2,y,4)
    a.line(4,a.h-6,a.w-5,a.h-6,6)
    a.line(4,a.h-4,a.w-5,a.h-4,14 if mode!="mart" else 10)
    for x in range(6,a.w-6,7):
        a.pixel(x,a.h-4,11 if mode!="mart" else 9)
    for x in (5,a.w-8):
        a.tube(x,3,x,a.h-6)

def magenta_sign(a: Art, x: int, y: int, tall: int = 15) -> None:
    """Purple thermal sign in an iron cage, visually secondary to magma."""
    a.rect(x, y, x+7, y+tall, 8)
    a.rect(x+1, y+1, x+6, y+tall-1, 15, False)
    a.line(x+2, y+2, x+2, y+tall-2, 10)
    a.line(x+5, y+2, x+5, y+tall-2, 15)
    for off in range(4,tall-2,4):
        a.line(x+3,y+off,x+4,y+off+1,15)
        a.pixel(x+4,y+off,11)


from polish_cuordilava_monuments import polish_monument
from relief_cuordilava_landmarks import add_reference_massing
from engrave_cuordilava_details import add_dense_reference_details
from finish_cuordilava_existing_roofs import finish_existing_architecture
from layer_cuordilava_reference_materials import layer_reference_materials
from deepen_cuordilava_facades import deepen_existing_facades
from join_cuordilava_roof_facades import connect_roofs_to_walls
from compose_cuordilava_existing_volumes import compose_existing_volumes
from reprofile_cuordilava_original_roofs import reprofile_existing_roofs
from finish_cuordilava_foundations import deepen_existing_foundations


def draw(name,w,h):
    a=Art(w*16,h*16)
    if "POKEMON_CENTER" in name:
        roof_base(a,"center")
        # Giant ruby industrial medallion over the Center: plus sign within reactor.
        a.ring(32,16,12,6,3);a.ring(32,16,9,14,2)
        a.rect(29,9,34,23,11);a.rect(24,14,39,18,11)
        a.rect(30,10,33,22,12);a.rect(25,15,38,17,12)
        for xx in (10,54):
            a.rect(xx-4,0,xx+4,12,8)
            a.rect(xx-3,1,xx+3,11,5,False)
            a.rect(xx-2,2,xx+2,7,13)
            a.tube(xx-1,7,xx-1,23)
    elif "MART" in name:
        roof_base(a,"mart")
        # Cyber-market cart symbol + distinctive cyan canopy and furnace pipes.
        a.rect(19,10,45,23,8);a.rect(19,10,45,23,10,False)
        a.line(23,14,27,19,9);a.line(27,19,42,19,9)
        a.line(42,19,44,13,9);a.line(44,13,23,13,9)
        for x in (29,40):a.ring(x,23,2,10,1)
        for xx in (8,55):
            a.rect(xx-3,0,xx+3,14,8)
            a.tube(xx-2,3,xx-2,24)
            a.rect(xx-1,3,xx+1,11,13)
        for x in (17,47):a.line(x,7,x,26,14)
    elif "GYM" in name and "FACADE" not in name:
        roof_base(a,"gym")
        # Broad stepped blast-furnace mass + large flame crest.
        a.rect(14,4,49,27,8)
        a.rect(14,4,49,27,6,False)
        a.ring(32,16,11,14,2)
        for x0,y0,x1,y1 in [
            (31,24,25,17),(25,17,29,12),(29,12,28,6),
            (28,6,37,15),(37,15,39,10),(39,10,40,21),
            (40,21,35,25),
        ]:a.line(x0,y0,x1,y1,12)
        for x,y in [(32,18),(33,17),(34,18),(34,19),(32,20),(31,21)]:a.pixel(x,y,11)
        for xx in (6,56):
            a.rect(xx-4,0,xx+3,18,8)
            a.rect(xx-3,0,xx+2,17,5,False)
            a.tube(xx,1,xx,24)
            for y in (3,8,13):a.line(xx-3,y,xx+3,y,12)
        a.line(0,27,63,27,12)
        a.line(4,29,59,29,14)
    elif "HOUSING" in name:
        roof_base(a,"housing")
        # Multiple town-house modules share a single industrial eave.
        a.rect(4,4,59,27,8)
        a.rect(4,4,59,27,5,False)
        for center in (12,25,39,52):
            a.rect(center-5,10,center+5,23,6)
            a.rect(center-4,11,center+4,21,8)
            a.rect(center-3,12,center+3,19,13)
            a.rect(center-2,13,center+2,18,12)
            a.line(center,12,center,20,6)
            a.line(center-4,20,center+4,20,10)
            for yy in (6,24):a.line(center-6,yy,center+6,yy,14)
        a.line(2,28,61,28,12);a.line(4,30,59,30,14)
        for x in (3,60):
            a.tube(x,4,x,28)
    elif "GYM_FORGE_FACADE" in name:
        a.rect(0,0,63,15,8)
        a.rect(1,1,62,14,5,False)
        for center in (11,26,40,55):
            a.rect(center-5,3,center+5,12,6)
            a.rect(center-4,4,center+4,11,8)
            a.rect(center-3,5,center+3,9,12)
            a.line(center-2,6,center+2,6,14)
            a.line(center,4,center,11,5)
            for x in (center-5,center+5):a.line(x,2,x,13,11)
        a.line(2,14,61,14,14)
    elif "PLAZA" in name:
        # Dark paved court with embossed, copper-traced volcanic seal.
        a.rect(0,0,63,31,0)
        for y in range(0,32,4):
            for x in range(0,64,8):
                a.pixel(x+(y%8)//4*3,y,5)
                a.line(x+2,y+1,x+4,y+1,7)
        a.ring(31,16,15,6,1)
        a.ring(31,16,13,13,2)
        a.ring(31,16,9,14,1)
        for x0,y0,x1,y1 in [(31,7,31,24),(20,16,42,16),(24,9,39,23),(38,9,24,23)]:
            a.line(x0,y0,x1,y1,12)
        a.rect(27,13,35,19,8)
        a.line(28,18,31,10,14)
        a.line(31,10,35,18,14)
        a.line(35,18,31,22,11)
        for x in (5,58):
            a.rect(x,4,x+1,27,6)
            for y in (6,24):a.pixel(x,y,12)
    else:
        # Pierced wrought-iron balcony on the *lower* edge of the water basin.
        # Pixel 0 stays transparent to keep waterfall and pool animated below.
        for x in range(0,64):
            a.pixel(x,9,5);a.pixel(x,10,7)
            a.pixel(x,13,8);a.pixel(x,14,6)
        for x in (1,13,26,39,51,62):
            a.rect(x,5,x+1,14,8)
            a.rect(x,5,x+1,7,12)
            a.pixel(x,4,11);a.pixel(x+1,4,14)
        for x in range(6,61,9):
            a.pixel(x,11,10)
    # Magenta is a selective secondary accent in the volcanic reference.
    # Keep the dominant glowing orange-red furnace and warm windows intact.
    if "POKEMON_CENTER" in name:
        magenta_sign(a, 4, 11, 15)
        magenta_sign(a, 52, 11, 15)
    elif "MART" in name:
        magenta_sign(a, 5, 12, 13)
        a.line(18,8,46,8,15)
        for x in range(22,44,5):a.pixel(x,7,10)
    elif "GYM" in name and "FACADE" not in name:
        magenta_sign(a, 9, 7, 19)
        magenta_sign(a, 47, 7, 19)
    elif "HOUSING" in name:
        for x in (17,31,44):
            a.line(x,12,x,22,15)
            a.pixel(x,11,10)
    elif "GYM_FORGE_FACADE" in name:
        for x in (4,60):
            a.line(x,2,x,12,15)
    elif "THERMAL_BASIN" in name:
        for x in (2,52):
            a.pixel(x,3,15)
            a.pixel(x+1,3,10)
    polish_monument(a, name)
    add_reference_massing(a, name)
    add_dense_reference_details(a, name)
    finish_existing_architecture(a, name)
    layer_reference_materials(a, name)
    deepen_existing_facades(a, name)
    connect_roofs_to_walls(a, name)
    compose_existing_volumes(a, name)
    reprofile_existing_roofs(a, name)
    deepen_existing_foundations(a, name)
    assert rgb_readable(a.pix)
    return a

def audit_layout(map_bytes,attributes):
    if len(map_bytes)!=800:raise ValueError("Unexpected town map size")
    if len(attributes)%2:raise ValueError("Invalid attributes data")
    # No entrance, script trigger, event actor, or sign can be covered.
    reserved={(12,15),(5,15),(15,5),(9,6),(16,15),(9,2),
              (8,7),(5,1),(5,8),(10,13),(4,4),(5,4),(6,16),
              (4,7),(11,6),(17,5),(8,6),(14,5),(4,15),
              (6,15),(11,15),(13,15),(15,15),(17,15)}
    covered=set()
    for label,bx,by,w,h in LANDMARKS:
        for dy in range(h):
            for dx in range(w):
                xy=(bx+dx,by+dy)
                if xy in covered or xy in reserved:
                    raise ValueError(f"Repeated or reserved landmark tile {label}: {xy}")
                covered.add(xy)
    assert len(covered)==48

def assert_fixed_town_footprint(root: Path) -> None:
    """Protect the original 20x20 world map and all six entrance warps."""
    import json
    layouts=json.loads((root/"data/layouts/layouts.json").read_text(encoding="utf-8"))["layouts"]
    layout=next((layout for layout in layouts if layout["id"]=="LAYOUT_LAVARIDGE_TOWN"),None)
    if layout is None or (layout["width"],layout["height"])!=(20,20):
        raise ValueError("Cuordilava must stay EXACTLY 20x20 map blocks")
    events=json.loads((root/"data/maps/LavaridgeTown/map.json").read_text(encoding="utf-8"))
    required={
        (12,15,"MAP_LAVARIDGE_TOWN_HERB_SHOP"),
        (5,15,"MAP_LAVARIDGE_TOWN_GYM_1F"),
        (15,5,"MAP_LAVARIDGE_TOWN_MART"),
        (9,6,"MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F"),
        (16,15,"MAP_LAVARIDGE_TOWN_HOUSE"),
        (9,2,"MAP_LAVARIDGE_TOWN_POKEMON_CENTER_1F"),
    }
    actual={(warp["x"],warp["y"],warp["dest_map"]) for warp in events["warp_events"]}
    if actual!=required or len(events["warp_events"])!=len(required):
        raise ValueError("Cuordilava entrances / connections are not the original six")
    if not any(link.get("map")=="MAP_ROUTE112" and link.get("direction")=="right"
               for link in events.get("connections",[])):
        raise ValueError("The original Route 112 entrance must remain connected")
    if len((root/"data/layouts/LavaridgeTown/map.bin").read_bytes())!=20*20*2:
        raise ValueError("Cuordilava map data must stay exactly 800 bytes")
    print("Footprint locked: original 20x20 map, six warps, Route 112 connection")


def run(root: Path):
    root=Path(root)
    assert_fixed_town_footprint(root)
    tiles=root/"data/tilesets/secondary/cuordilava/tiles.png"
    metas=root/"data/tilesets/secondary/cuordilava/metatiles.bin"
    attrs=root/"data/tilesets/secondary/cuordilava/metatile_attributes.bin"
    pri=root/"data/tilesets/primary/general/metatiles.bin"
    pri_attrs=root/"data/tilesets/primary/general/metatile_attributes.bin"
    town=root/"data/layouts/LavaridgeTown/map.bin"
    m=bytearray(town.read_bytes())
    sec=bytearray(metas.read_bytes())
    secattr=bytearray(attrs.read_bytes())
    p=pri.read_bytes()
    pattr=pri_attrs.read_bytes()
    width,height,pix=png_indexed(tiles)
    if (width,height)!=(128,232):raise ValueError("Town atlas height already changed: use clean checkout")
    if len(sec)!=7056 or len(secattr)!=882 or len(p)%16 or len(pattr)%2:
        raise ValueError("Base metatile sources changed; review atlas capacity")
    source=tiles.read_bytes()
    palette=source[source.index(b"PLTE")+4:source.index(b"PLTE")+52]
    assert len(palette)==48
    audit_layout(m,secattr)
    used=set()
    for offset in range(0,len(sec),2):
        t=struct.unpack_from("<H",sec,offset)[0]&1023
        if t>=512:used.add(t-512)
    # Avoid the active animated tile bands (lava 160..171, steam 288..295).
    # These other IDs are unused by every existing metatile in the town tileset.
    safe_bands=list(range(0,160))+list(range(172,288))+list(range(296,512))
    spare=[t for t in safe_bands if t not in used]
    if len(spare)<48*4:raise ValueError(f"Not enough 4bpp tiles: {len(spare)}")
    spare=spare[:48*4]
    assert max(spare)<512 and min(spare)>=0
    pix.extend([[0]*128 for _ in range(256-height)])
    count=0
    previous=[struct.unpack_from("<H",m,n*2)[0] for n in range(400)]
    changed={}
    for name,bx,by,w,h in LANDMARKS:
        mural=draw(name,w,h)
        for dy in range(h):
            for dx in range(w):
                x,y=bx+dx,by+dy
                i=y*20+x
                raw=struct.unpack_from("<H",m,i*2)[0]
                oldmeta=raw&1023
                oldbank=sec if oldmeta>=512 else p
                oldidx=oldmeta-512 if oldmeta>=512 else oldmeta
                oldattrs=secattr if oldmeta>=512 else pattr
                if (oldidx+1)*16>len(oldbank) or (oldidx+1)*2>len(oldattrs):
                    raise ValueError(f"Invalid old {x},{y}: {oldmeta}")
                # Four existing base-layer tiles + custom roof/court overlay.
                oldbase=oldbank[oldidx*16:oldidx*16+8]
                new_entries=bytearray(oldbase)
                for sub in range(4):
                    tid=spare[count*4+sub]
                    px=(dx*2+(sub%2))*8
                    py=(dy*2+(sub//2))*8
                    for oy in range(8):
                        for ox in range(8):
                            tx,ty=(tid%16)*8+ox,(tid//16)*8+oy
                            pix[ty][tx]=mural.pix[py+oy][px+ox]
                    new_entries+=struct.pack("<H",0x6000 | (512+tid))
                newidx=len(sec)//16
                if newidx>=512:raise ValueError("Secondary metatile ID overflow")
                sec+=new_entries
                secattr+=oldattrs[oldidx*2:oldidx*2+2]
                struct.pack_into("<H",m,i*2,(raw&~1023)|(512+newidx))
                changed[(x,y)]=(oldmeta,512+newidx,name)
                count+=1
    assert count==48 and len(sec)==(441+48)*16
    assert len(secattr)==(441+48)*2
    assert len(m)==len(previous)*2
    for idx,before in enumerate(previous):
        after=struct.unpack_from("<H",m,idx*2)[0]
        if (idx%20,idx//20) not in changed:
            assert after==before,("Unintended map edit",idx)
        else:
            assert (after>>10)==(before>>10)
    # The critical invariant: every new tile has EXACTLY the former collision
    # and behavior byte pair; no layout warp/event file is edited at all.
    for (x,y),(oldmeta,newmeta,label) in changed.items():
        oldbuf=secattr[:882] if oldmeta>=512 else pattr
        oldindex=oldmeta-512 if oldmeta>=512 else oldmeta
        assert secattr[(newmeta-512)*2:(newmeta-512)*2+2]==oldbuf[oldindex*2:oldindex*2+2],(label,x,y)
    write_png(tiles,128,256,pix,palette)
    w,h,check=png_indexed(tiles)
    assert (w,h,check)==(128,256,pix)
    metas.write_bytes(sec)
    attrs.write_bytes(secattr)
    town.write_bytes(m)
    print(f"Sculpted {count} custom, collision-preserving metatiles; extended 4bpp atlas to 512 tiles")
    print("Architectural landmarks:",[name for name,*_ in LANDMARKS])
    print("Day/night palettes and map objects preserved")

if __name__=="__main__":
    run(Path(__file__).resolve().parents[1])
