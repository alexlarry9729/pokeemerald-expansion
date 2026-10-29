#!/usr/bin/env python3
"""Small, FLAT flowering basalt beds on already open Cuordilava paving.

The reference has many green/orange islands rather than an empty industrial
forecourt. Reuse exactly two presently unreferenced GBA 8x8 tiles (510, 511)
with vertical flips in one inactive town-private metatile (438). Map remains
EXACTLY 20x20. This does not create trees, objects, buildings, blocked paths,
warps, scripts, or a new palette. It runs LAST in the art generation chain.
"""
from pathlib import Path
import json
import struct

from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

METATILE = 438
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
    """An oval, low-growing moss/ember flower island on a transparent floor."""
    a = [[0] * 16 for _ in range(16)]
    def p(x, y, c):
        if 0 <= x < 16 and 0 <= y < 8:
            a[y][x] = c
    # Deliberately transparent outskirts: paths still appear between plants.
    for y in range(1, 8):
        for x in range(1, 15):
            d = abs(2*x - 15) + abs(2*y - 15)
            if d < 19 and (x+y) % 7 != 0:
                p(x, y, 9 if (x*3+y) % 4 else 10)
            if d < 11 and (x+y) % 5 == 0:
                p(x, y, 15)
    # Rich foliage is legible from above, but does not resemble a raised wall.
    for x,y in ((3,5),(4,3),(5,4),(6,2),(7,4),(8,2),
                (9,5),(10,3),(11,4),(12,6),(4,7),(11,7)):
        p(x,y,10)
        p(x+1,y,15)
    # Warm volcanic blossoms lead visually, not a flat green orb. Their
    # arrangement differs between left/right halves and is interleaved with
    # dark leaves; the low-growing island stays flat and traversable.
    for x,y in ((2,6),(4,4),(6,2),(7,6),(9,3),(11,5),(13,3)):
        p(x,y,11)
        p(x+1,y,14)
        p(x,y+1,14)
        if (x+y)%2:
            p(x+1,y+1,13)
    for x,y in ((3,2),(8,5),(12,2)):
        p(x,y,12)
        p(x+1,y,9)
    # Reuse the top two 8x8 tiles upside-down on the lower half.
    for y in range(8, 16):
        a[y] = a[15-y][:]
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


def expected_overlay():
    a, b = GRAPHICS
    # bottom: flip the corresponding TOP graphic vertically, not the
    # quadrant positions. Both halves join into a single oval flower bed.
    return (
        (9 << 12) | (512+a), (9 << 12) | (512+b),
        (9 << 12) | 0x0800 | (512+a),
        (9 << 12) | 0x0800 | (512+b),
    )


def validate_built(root):
    q = paths(root)
    ensure_events_clear(root)
    m, met, attrs = (q[k].read_bytes() for k in ("map", "meta", "attr"))
    pri, pattrs = (q[k].read_bytes() for k in ("primary", "primary_attr"))
    if (len(m), len(met), len(attrs)) != (800, 8192, 1024):
        raise ValueError("Flower bed exceeds fixed 20x20 GBA map budget")
    used = {(i % 20, i // 20) for i in range(400)
            if (read16(m, 2*i) & 1023) == 512+METATILE}
    if used != set(CELLS):
        raise ValueError(f"Flower-beds changed their exact safe cells: {used ^ set(CELLS)}")
    if met[METATILE*16:METATILE*16+8] != pri[ORIGINAL_FLOOR*16:ORIGINAL_FLOOR*16+8]:
        raise ValueError("Original cobble underlay no longer intact")
    if attrs[METATILE*2:METATILE*2+2] != pattrs[ORIGINAL_FLOOR*2:ORIGINAL_FLOOR*2+2]:
        raise ValueError("Flower beds changed ground behavior/collision")
    if tuple(read16(met, METATILE*16+8+2*i) for i in range(4)) != expected_overlay():
        raise ValueError("Flowerbed GBA graphics / flips are not correctly assembled")
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
    if 512+METATILE in {read16(raw,2*i)&1023 for i in range(400)}:
        raise ValueError("Flower-bed donor metatile already used in map")
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
    entries = bytearray(pri[ORIGINAL_FLOOR*16:ORIGINAL_FLOOR*16+8])
    entries += struct.pack("<4H", *expected_overlay())
    meta[METATILE*16:(METATILE+1)*16] = entries
    attrs[METATILE*2:METATILE*2+2] = pattrs[ORIGINAL_FLOOR*2:ORIGINAL_FLOOR*2+2]
    for x,y in CELLS:
        off = 2*(20*y+x)
        old=read16(raw,off)
        struct.pack_into("<H",raw,off,(old&~1023)|(512+METATILE))
    for i in range(400):
        old,new=read16(original_map,2*i),read16(raw,2*i)
        if (old>>10)!=(new>>10) or (
            (i%20,i//20) not in CELLS and old!=new):
            raise ValueError("Flower bed changed a gameplay map cell")
    if any(meta[16*i:16*i+16]!=original_meta[16*i:16*i+16]
           for i in range(512) if i!=METATILE):
        raise ValueError("Flowerbed overwritten unrelated metatile graphics")
    if any(attrs[2*i:2*i+2]!=original_attr[2*i:2*i+2]
           for i in range(512) if i!=METATILE):
        raise ValueError("Flowerbed overwritten another metatile's collision")
    write_png(q["atlas"],w,h,pixels,plte)
    q["map"].write_bytes(raw)
    q["meta"].write_bytes(meta)
    q["attr"].write_bytes(attrs)
    validate_built(root)
    print("Cuordilava: 12 walkable volcanic flower mosaics, 1 private metatile, "
          "2 recycled 8x8 atlas graphics; all six doors/events unchanged.")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
