#!/usr/bin/env python3
"""Natural mineral-water ripples, only on Cuordilava's three unique hot-pool tiles.

Uses the existing secondary atlas and water palette 08. Preserves original
20x20 map data, metatile attributes, water animation, entrances, NPCs and
approved day/night settings. Run after spa courtyard and before city sculpture.
"""
from __future__ import annotations
from pathlib import Path
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

WATER_TILES = (320, 321, 336)
DAY_WATER = {9: (79, 181, 195), 10: (48, 156, 173)}
SPRING_BOUNDS = (2, 7, 2, 6)

def assert_spa_tile_isolation(root: Path) -> dict[int, set[tuple[int, int]]]:
    layout=(root/"data/layouts/LavaridgeTown/map.bin").read_bytes()
    primary=(root/"data/tilesets/primary/general/metatiles.bin").read_bytes()
    secondary=(root/"data/tilesets/secondary/cuordilava/metatiles.bin").read_bytes()
    if len(layout)!=800: raise ValueError("Town must remain original 20x20 blocks")
    seen={tid:set() for tid in WATER_TILES}
    for y in range(20):
        for x in range(20):
            index=struct.unpack_from("<H",layout,(y*20+x)*2)[0]&1023
            bank=secondary if index>=512 else primary
            index=index-512 if index>=512 else index
            if len(bank)<(index+1)*16:raise ValueError("Invalid original map metatile")
            for entry in struct.unpack_from("<8H",bank,index*16):
                tile=(entry&1023)-512
                if tile in seen and entry>>12==8:seen[tile].add((x,y))
    xmin,xmax,ymin,ymax=SPRING_BOUNDS
    for tid,positions in seen.items():
        if not positions or any(not (xmin<=x<=xmax and ymin<=y<=ymax) for x,y in positions):
            raise ValueError(f"Water tile {tid} is missing or reused outside the hot pool: {sorted(positions)}")
    return seen

def run(root: Path) -> None:
    root=Path(root)
    positions=assert_spa_tile_isolation(root)
    atlas=root/"data/tilesets/secondary/cuordilava/tiles.png"
    width,height,rows=png_indexed(atlas)
    if (width,height)!=(128,232):raise ValueError("Apply water before city atlas expansion")
    raw=atlas.read_bytes()
    palette=raw[raw.index(b"PLTE")+4:raw.index(b"PLTE")+52]
    if len(palette)!=48:raise ValueError("Town-private 16-colour 4bpp PNG expected")
    changed=0
    for tid in WATER_TILES:
        ox,oy=(tid%16)*8,(tid//16)*8
        for y in range(8):
            for x in range(8):
                old=rows[oy+y][ox+x]
                if old not in (9,10):
                    continue  # retain existing foam, rocks and shoreline
                wave=(x*29+y*11+tid*3+x*y*7)%37
                new=10 if wave<=5 else 1 if wave==6 and tid!=336 else 9
                if new!=old:
                    rows[oy+y][ox+x]=new
                    changed+=1
    if changed<10:raise ValueError("Unexpected change in source water art")
    write_png(atlas,width,height,rows,palette)
    if png_indexed(atlas)!=(width,height,rows):
        raise ValueError("Repainted hot-spring atlas did not round-trip as 4bpp")
    pal=root/"data/tilesets/secondary/cuordilava/palettes/08.pal"
    lines=pal.read_text(encoding="ascii").splitlines()
    if lines[:3]!=["JASC-PAL","0100","16"] or len(lines)!=19:
        raise ValueError("Unexpected Cuordilava palette format")
    colors=[tuple(map(int,l.split())) for l in lines[3:]]
    expected={9:(139,205,246),10:(115,189,238)}
    if any(colors[i]!=expected[i] for i in expected):
        raise ValueError("Spa palette already altered; review before reapplying water pass")
    for index,value in DAY_WATER.items():colors[index]=value
    pal.write_text("\n".join(lines[:3]+[" ".join(map(str,c)) for c in colors])+"\n",encoding="ascii")
    print(f"Turquoise hot springs: {changed} ripple pixels, unchanged town/collisions; "
          f"{sum(map(len,positions.values()))} pool-only tile references.")

if __name__=="__main__":
    run(Path(__file__).resolve().parents[1])
