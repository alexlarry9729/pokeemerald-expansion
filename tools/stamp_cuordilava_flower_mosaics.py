#!/usr/bin/env python3
"""Small, FLAT flowering basalt beds on already open Cuordilava paving.

The reference has many green/orange islands rather than an empty industrial
forecourt. Reuse exactly two presently unreferenced GBA 8x8 tiles (510, 511)
with vertical flips in one inactive town-private metatiles (438, 422). Map remains
EXACTLY 20x20. This does not create trees, objects, buildings, blocked paths,
warps, scripts, or a new palette. It runs LAST in the art generation chain.
"""
from pathlib import Path
import json
import struct

from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

METATILE = 438
MIRROR_METATILE = 422
METATILES = (METATILE, MIRROR_METATILE)
GRAPHICS = (510, 511)
ORIGINAL_FLOOR = 1
# These are already WALKABLE original floor cells, away from doorways,
# signage, objects, the player-facing entrance lanes and the hot pool.
CELLS = (
    (18, 8), (19, 8), (18, 11), (19, 11),
    (3, 16), (17, 16),
    (3, 17), (5, 17), (8, 17), (11, 17), (15, 17), (17, 17),
)
assert len(CELLS) == len(set(CELLS)) == 12


def read16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def image():
    """Two irregular terraced flower beds on the *existing* clear 16x16 floor.

    Palette 9 supplies deep volcanic soil (12/13), three natural foliage
    shades (9/10/15) and copper-orange blossoms (11/14). The upper left and
    upper right halves are different drawings; full metatiles alternate
    horizontal orientations, so bottom courtyards don't look like one
    duplicated fluorescent square. A 0 pixel leaves the old floor visible.
    """
    a = [[0] * 16 for _ in range(16)]

    def p(x, y, c):
        if 0 <= x < 16 and 0 <= y < 8:
            a[y][x] = c

    # Basalt soil islands with irregular scalloped outlines; expose clear
    # cobblestones between their edges and around the plot.
    for y in range(1, 8):
        for x in range(1, 15):
            west = (x - 5) ** 2 * 2 + (y - 6) ** 2 * 3 < 49
            east = (x - 11) ** 2 * 3 + (y - 5) ** 2 * 2 < 37
            if (west or east) and (x * 11 + y * 7) % 9 != 0:
                p(x, y, 12 if (x + y) % 4 else 13)

    # Serrated leaves grow in two separate masses. Thin transparent gaps
    # and cooler shadow leaves separate each frond at original GBA scale.
    for y in range(1, 8):
        for x in range(1, 15):
            west = 2 * (x - 5) ** 2 + 3 * (y - 5) ** 2 < 30
            east = 3 * (x - 11) ** 2 + 2 * (y - 5) ** 2 < 28
            if (west or east) and ((x * 7 + y * 3) % 8 not in (0, 1)):
                shade = 9 if (x + 2 * y) % 3 == 0 else 10
                if (x * 5 + y * 7) % 11 == 0:
                    shade = 15
                p(x, y, shade)

    # Individual stems reach toward the outer soil, increasing natural depth.
    for x, y in ((3,2), (4,1), (6,1), (7,3), (8,6),
                 (9,3), (10,2), (12,2), (13,3), (14,6),
                 (2,5), (4,7), (6,7), (10,7), (12,7)):
        p(x, y, 9)
        if y < 7:
            p(x, y + 1, 15 if x % 3 == 0 else 10)

    # Blossom centers are NOT placed in a repeated circular border.
    # Two flower colours give four alternating mosaics after the H-flips.
    for x, y in ((3,5), (5,3), (7,6), (9,5), (11,3), (13,6),
                 (4,7), (12,7)):
        p(x, y, 11)
        p(x + 1, y, 14)
        p(x, y - 1, 14)
        if (x + y) % 2:
            p(x - 1, y, 15)

    # Hardware V-flip in the metatile creates its lower half. This leaves
    # every border transparent in the same way as the validated base floor.
    for y in range(8, 16):
        a[y] = a[15 - y][:]

    foliage = sum(c in (9, 10, 15) for row in a for c in row)
    flowers = sum(c in (11, 14) for row in a for c in row)
    if foliage < 70 or flowers < 12:
        raise ValueError(f"Volcanic flower beds became sparse: {foliage=}, {flowers=}")
    if any(c < 0 or c > 15 for row in a for c in row):
        raise ValueError("Volcanic flower beds exceed indexed 4bpp colours")
    return a


def paths(root):
    r = Path(root)
    return {
        "map": r / "data/layouts/LavaridgeTown/map.bin",
        "meta": r / "data/tilesets/secondary/cuordilava/metatiles.bin",
        "attr": r / "data/tilesets/secondary/cuordilava/metatile_attributes.bin",
        "primary": r / "data/tilesets/primary/general/metatiles.bin",
        "primary_attr": r / "data/tilesets/primary/general/metatile_attributes.bin",
        "atlas": r / "data/tilesets/secondary/cuordilava/tiles.png",
        "events": r / "data/maps/LavaridgeTown/map.json",
        "layouts": r / "data/layouts/layouts.json",
    }


def ensure_events_clear(root):
    q = paths(root)
    layout = json.loads(q["layouts"].read_text(encoding="utf-8"))["layouts"]
    city = next(item for item in layout if item["id"] == "LAYOUT_LAVARIDGE_TOWN")
    if (city["width"], city["height"]) != (20, 20):
        raise ValueError("Flower beds cannot enlarge Cuordilava")
    events = json.loads(q["events"].read_text(encoding="utf-8"))
    protected = {
        (int(item["x"]), int(item["y"]))
        for category in ("warp_events", "object_events", "coord_events", "bg_events")
        for item in events.get(category, [])
        if "x" in item and "y" in item
    }
    if protected & set(CELLS):
        raise ValueError(f"Flower overlays would hide active events: {protected & set(CELLS)}")


def mosaic_metatile(x,y):
    return MIRROR_METATILE if (x+y)%2 else METATILE


def expected_overlay(mirrored=False):
    a,b=GRAPHICS
    if mirrored:
        a,b=b,a
    flip=0x0400 if mirrored else 0
    return (
        (9<<12)|flip|(512+a), (9<<12)|flip|(512+b),
        (9<<12)|flip|0x0800|(512+a),
        (9<<12)|flip|0x0800|(512+b),
    )


def validate_built(root):
    q = paths(root)
    ensure_events_clear(root)
    m, met, attrs = (q[k].read_bytes() for k in ("map", "meta", "attr"))
    pri, pattrs = (q[k].read_bytes() for k in ("primary", "primary_attr"))
    if (len(m), len(met), len(attrs)) != (800, 8192, 1024):
        raise ValueError("Flower bed exceeds fixed 20x20 GBA map budget")
    used = {(i%20,i//20) for i in range(400)
            if (read16(m,2*i)&1023) in (512+METATILE,512+MIRROR_METATILE)}
    if used != set(CELLS):
        raise ValueError(f"Flower-bed safe cells changed: {used^set(CELLS)}")
    for mid in METATILES:
        if met[mid*16:mid*16+8]!=pri[ORIGINAL_FLOOR*16:ORIGINAL_FLOOR*16+8]:
            raise ValueError("Original cobbles beneath the flowers changed")
        if attrs[mid*2:mid*2+2]!=pattrs[ORIGINAL_FLOOR*2:ORIGINAL_FLOOR*2+2]:
            raise ValueError("Flower mosaics changed original collision")
        if tuple(read16(met,mid*16+8+2*q) for q in range(4)) != expected_overlay(mid==MIRROR_METATILE):
            raise ValueError("Flower mosaic 8x8 mirror / flip seam")
    for x,y in CELLS:
        if read16(m,2*(20*y+x))&1023 != 512+mosaic_metatile(x,y):
            raise ValueError(f"Flower mosaic mirrored cell mismatch: {(x,y)}")
    if any((read16(m, 2*(20*y+x)) >> 10) & 3 for x,y in CELLS):
        raise ValueError("Flower-beds must remain exactly walkable")
    w,h,pix = png_indexed(q["atlas"])
    if (w,h) != (128,256):
        raise ValueError("Flowerbeds exceed 4bpp tile atlas")
    art = image()
    for qid, tid in enumerate(GRAPHICS):
        sx,sy = (tid%16)*8,(tid//16)*8
        ox = qid*8
        if any(pix[sy+y][sx+x] != art[y][ox+x]
               for y in range(8) for x in range(8)):
            raise ValueError("Flowerbed indexed art is not reproducible")
    counts = [sum(color in colours for row in art for color in row)
              for colours in ((9,10,15), (11,14))]
    if counts[0] < 70 or counts[1] < 12:
        raise ValueError(f"Insufficient reference flora: {counts}")


def run(root):
    q = paths(root)
    ensure_events_clear(root)
    raw = bytearray(q["map"].read_bytes())
    meta = bytearray(q["meta"].read_bytes())
    attrs = bytearray(q["attr"].read_bytes())
    pri, pattrs = (q[k].read_bytes() for k in ("primary", "primary_attr"))
    if (len(raw),len(meta),len(attrs)) != (800,8192,1024):
        raise ValueError("Flower beds require the completed town-private tileset")
    occupied={read16(raw,2*i)&1023 for i in range(400)}
    if any(512+mid in occupied for mid in METATILES):
        raise ValueError("Flower-bed donor metatiles already occupied")
    if any((read16(meta,off)&1023) in (512+GRAPHICS[0],512+GRAPHICS[1])
           for off in range(0,len(meta),2)):
        raise ValueError("The two final atlas tiles are no longer free; refusing art corruption")
    for x,y in CELLS:
        original = read16(raw,2*(20*y+x))
        if (original & 1023) != ORIGINAL_FLOOR or ((original >> 10)&3):
            raise ValueError(f"Flower bed {x,y} is not a spare, flat original floor cell")
    w,h,pixels = png_indexed(q["atlas"])
    if (w,h) != (128,256):
        raise ValueError("Unexpected indexed 4bpp atlas")
    b = q["atlas"].read_bytes()
    plte = b[b.index(b"PLTE")+4:b.index(b"PLTE")+52]
    if len(plte) != 48:
        raise ValueError("Town-private PNG must retain 16 indexed colours")
    original_map, original_meta, original_attr = bytes(raw), bytes(meta), bytes(attrs)
    design = image()
    for quadrant,tid in enumerate(GRAPHICS):
        tx,ty=(tid%16)*8,(tid//16)*8
        for y in range(8):
            for x in range(8):
                pixels[ty+y][tx+x] = design[y][8*quadrant+x]
    for mid in METATILES:
        entries=bytearray(pri[ORIGINAL_FLOOR*16:ORIGINAL_FLOOR*16+8])
        entries+=struct.pack("<4H",*expected_overlay(mid==MIRROR_METATILE))
        meta[mid*16:(mid+1)*16]=entries
        attrs[mid*2:mid*2+2]=pattrs[ORIGINAL_FLOOR*2:ORIGINAL_FLOOR*2+2]
    for x,y in CELLS:
        off=2*(20*y+x)
        old=read16(raw,off)
        struct.pack_into("<H",raw,off,(old&~1023)|(512+mosaic_metatile(x,y)))
    for i in range(400):
        old,new=read16(original_map,2*i),read16(raw,2*i)
        if (old>>10)!=(new>>10) or (
            (i%20,i//20) not in CELLS and old!=new):
            raise ValueError("Flower bed changed a gameplay map cell")
    if any(meta[16*i:16*i+16]!=original_meta[16*i:16*i+16]
           for i in range(512) if i not in METATILES):
        raise ValueError("Flowerbed overwritten unrelated metatile graphics")
    if any(attrs[2*i:2*i+2]!=original_attr[2*i:2*i+2]
           for i in range(512) if i not in METATILES):
        raise ValueError("Flowerbed overwritten another metatile's collision")
    write_png(q["atlas"],w,h,pixels,plte)
    q["map"].write_bytes(raw)
    q["meta"].write_bytes(meta)
    q["attr"].write_bytes(attrs)
    validate_built(root)
    print("Cuordilava: 12 walkable floral mosaics, two alternating mirrored private "
          "metatiles, 2 reused 8x8 graphics, six doors/events unchanged.")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
