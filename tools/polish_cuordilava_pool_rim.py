#!/usr/bin/env python3
"""Pixel-level cleanup of the EXISTING volcanic rock rim around the hot pool.

Why the old border looked wrong:
- vertical H+V flipped west pieces produced inverted bright stone caps;
- the shared original rock graphics have isolated pure-white/yellow pixels,
  making edges seem disconnected even when map/metatile shape is correct.

This pass runs ONLY after the town art and six preserved entrance warps have
been generated. It audits every *live* use of an 8x8 graphics tile, then
softens ONLY genuinely pool-perimeter-exclusive palette-8 rock characters.

It never changes metatiles, map, palette, events, collision, animation,
turquoise water, original stair graphics, nor the hash-protected hot-spring
water/stone tiles. The 20x20 map and 512 8x8 tile budget remain identical.
"""

from pathlib import Path
import struct

from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

# The pool consists of turquoise cells x3..6/y3..5. RIM is the already
# existing *blocking* stone edge around them, including the three special
# restored west cells and the upper/lower/eastern granite contours.
RIM = (
    {(x, 2) for x in range(2, 8)}
    | {(x, 6) for x in range(2, 8)}
    | {(2, y) for y in range(3, 6)}
    | {(7, y) for y in range(3, 6)}
)
WATER = {(x, y) for y in range(3, 6) for x in range(3, 7)}
# 12 exact, historic splash/shore characters are protected by a hard SHA256
# validation. 182/183 are the freshly restored ORIGINAL stairs; 320/321/336
# are the current isolated turquoise mineral water.
PROTECTED = {
    168, 169, 180, 181, 182, 183, 184, 185, 200, 201, 202, 203,
    392, 393, 320, 321, 336,
}

def word(data, off):
    return struct.unpack_from("<H", data, off)[0]


def paths(root):
    root = Path(root)
    return (
        root / "data/layouts/LavaridgeTown/map.bin",
        root / "data/tilesets/primary/general/metatiles.bin",
        root / "data/tilesets/secondary/cuordilava/metatiles.bin",
        root / "data/tilesets/secondary/cuordilava/tiles.png",
        root / "data/tilesets/secondary/cuordilava/metatile_attributes.bin",
        root / "data/maps/LavaridgeTown/map.json",
    )


def exclusive_rock_tiles(map_data, primary, secondary, px):
    """Find rock 8x8 sources *only* visible as palette-8 perimeter stones."""
    uses = {}
    for i in range(400):
        raw = word(map_data, 2*i)
        mid = raw & 1023
        bank, m = (secondary, mid-512) if mid >= 512 else (primary, mid)
        xy = (i%20, i//20)
        for slot in range(8):
            entry = word(bank, m*16+2*slot)
            char = entry&1023
            if char < 512:
                continue
            tid = char-512
            uses.setdefault(tid,set()).add((xy,entry>>12))
    result = []
    for tid,refs in uses.items():
        if tid in PROTECTED:
            continue
        if not refs or any(pal != 8 or xy not in RIM
                           for xy,pal in refs):
            continue
        ox,oy = (tid%16)*8,(tid//16)*8
        block = [px[oy+y][ox+x] for y in range(8) for x in range(8)]
        # Do not touch water, cliff transparency or shimmering spray.
        # Gray 4..8 are the FIVE colors of the existing perimeter stones.
        if sum(4 <= c <= 8 for c in block) < 12:
            continue
        if any(c in (9, 10) for c in block):
            continue
        result.append(tid)
    return tuple(sorted(result))


def softened(block):
    """Keep stone silhouettes but eliminate isolated gold/white rogue pixels."""
    out=[row[:] for row in block]
    for y in range(8):
        for x in range(8):
            old = block[y][x]
            if old in (11,12,13,14,15):
                out[y][x] = 5 if (x+y)%4 < 2 else 6
            elif old == 1:
                # A pure-white pixel on granite is not turquoise foam.
                out[y][x] = 4 if (x+y)%3 == 0 else 5
            elif old == 4:
                # Keep broad pale granite faces. Remove single-pixel
                # highlights not connected to another light-colored stone.
                near=sum(
                    block[ny][nx] == 4
                    for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1))
                    if 0<=nx<8 and 0<=ny<8
                )
                if near == 0:
                    out[y][x] = 5
    return out


def run(root):
    mpath, primary_path, secondary_path, atlas_path, attrs_path, events_path = paths(root)
    m, pri, sec = mpath.read_bytes(),primary_path.read_bytes(),secondary_path.read_bytes()
    attrs,events=attrs_path.read_bytes(),events_path.read_bytes()
    if (len(m),len(sec),len(attrs)) != (800,8192,1024):
        raise ValueError("Pool pixel polish must preserve original 20x20 world/512 metatiles")
    w,h,px=png_indexed(atlas_path)
    if (w,h)!=(128,256):
        raise ValueError("Pool polish cannot change 4bpp atlas dimensions")
    src=atlas_path.read_bytes()
    palette=src[src.index(b"PLTE")+4:src.index(b"PLTE")+52]
    if len(palette)!=48:
        raise ValueError("Pool polish cannot touch the 16-color shared palette")
    ids=exclusive_rock_tiles(m,pri,sec,px)
    before=[row[:] for row in px]
    altered=0
    for tid in ids:
        ox,oy=(tid%16)*8,(tid//16)*8
        part=[px[oy+y][ox:ox+8] for y in range(8)]
        adjusted=softened(part)
        for y in range(8):
            for x in range(8):
                if px[oy+y][ox+x]!=adjusted[y][x]:
                    px[oy+y][ox+x]=adjusted[y][x]
                    altered+=1
    # Every visible rock or mineral character OTHER THAN the explicitly
    # audited local stone faces must stay 100% byte-identical.
    for y in range(h):
        for x in range(w):
            tid=(y//8)*16+(x//8)
            if tid not in ids and before[y][x]!=px[y][x]:
                raise ValueError("Rim cleanup escaped its exclusive pool rock characters")
    if altered:
        write_png(atlas_path,w,h,px,palette)
    if (mpath.read_bytes()!=m or secondary_path.read_bytes()!=sec
            or attrs_path.read_bytes()!=attrs or events_path.read_bytes()!=events):
        raise ValueError("Rim cleanup inadvertently changed water or gameplay geometry")
    print(f"Cuordilava full original stone rim: {len(ids)} exclusively owned "
          f"granite characters checked, {altered} isolated white/yellow pixels "
          "softened across north/west/east/south; zero changes to water/stairs/warps")
    return altered


if __name__=="__main__":
    run(Path(__file__).resolve().parents[1])
