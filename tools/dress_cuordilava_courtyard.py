#!/usr/bin/env python3
"""Add volcanic cobblestones to the original 20x20 Cuordilava thermal courtyard.

Palette 9 and four unused private 8x8 tiles provide a warm basalt pavement.
No water pixels, warp, map cell, NPC, event, collision or night blend is changed.
This town-private secondary tileset is used only by LavaridgeTown.
Run AFTER the building texture phase and BEFORE 48 sculpted landmark murals.
"""
from pathlib import Path
import json
import struct
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png

BASALT_COLORS = {
    9: (33, 82, 94), 10: (59, 116, 116),
    11: (179, 102, 68), 12: (91, 76, 77),
    13: (124, 95, 89), 14: (150, 107, 83),
    15: (88, 121, 76),
}
# IDs in Cuordilava's original thermal-sand court; never shared with other maps.
SAND_METATILES = (680, 664, 672, 697, 698, 650, 652, 657, 658)
PAVEMENT_BASES = (680, 664, 672, 697, 698)


def run(root: Path) -> None:
    root = Path(root)
    layouts = json.loads((root / "data/layouts/layouts.json").read_text())["layouts"]
    found = [x for x in layouts if x["secondary_tileset"] == "gTileset_CuordilavaLavaridge"]
    assert len(found) == 1 and found[0]["id"] == "LAYOUT_LAVARIDGE_TOWN"
    town = (root / "data/layouts/LavaridgeTown/map.bin").read_bytes()
    assert len(town) == 800
    meta_path = root / "data/tilesets/secondary/cuordilava/metatiles.bin"
    meta = bytearray(meta_path.read_bytes())
    assert len(meta) == 7056, "Dress thermal courtyard before sculpted landmarks"
    art_path = root / "data/tilesets/secondary/cuordilava/tiles.png"
    width, height, pix = png_indexed(art_path)
    assert (width, height) == (128, 232)
    raw = art_path.read_bytes()
    palette = raw[raw.index(b"PLTE")+4:raw.index(b"PLTE")+52]
    assert len(palette) == 48

    usage = {}
    for y in range(20):
        for x in range(20):
            mid = struct.unpack_from("<H", town, 2 * (y * 20 + x))[0] & 1023
            if mid in SAND_METATILES:
                usage.setdefault(mid, []).append((x, y))
    for mid in SAND_METATILES:
        positions = usage.get(mid, [])
        if not positions or any(not (2 <= x <= 7 and 7 <= y <= 10) for x, y in positions):
            raise ValueError(f"Sand metatile {mid} used outside courtyard: {positions}")

    used = set()
    for off in range(0, len(meta), 2):
        t = struct.unpack_from("<H", meta, off)[0] & 1023
        if t >= 512:
            used.add(t - 512)
    # Avoid active animated tile ranges; reserve 192 for the existing sculptor.
    candidates = list(range(0,160)) + list(range(172,288)) + list(range(296,512))
    free = [t for t in candidates if t not in used]
    if len(free) < 196:
        raise ValueError(f"Need 4 courtyard + 192 architecture graphics; found {len(free)}")
    new_tiles = [t for t in free if t < 464][:4]
    if len(new_tiles) != 4:
        raise ValueError("Missing writable original atlas positions")
    for corner, tid in enumerate(new_tiles):
        bx, by = (tid % 16) * 8, (tid // 16) * 8
        for y in range(8):
            for x in range(8):
                pix[by+y][bx+x] = 12
        for xx in range(1, 7):
            if xx not in (3, 4):
                pix[by+1+corner%2][bx+xx] = 13
            if xx % 2 == 0:
                pix[by+6][bx+xx] = 13
        for yy in range(2, 6):
            pix[by+yy][bx+(1 if corner%2 == 0 else 6)] = 14
        for x,y,color in (
            (2,3,13),(4,5,11),(6,4,14),
            (5,2,15),(6,2,15),(5,3,9),
        ):
            if (corner+x+y)%3 != 0:
                pix[by+y][bx+x] = color
        pix[by][bx] = 8
        pix[by+7][bx+7] = 8

    for mid in SAND_METATILES:
        origin = (mid - 512) * 16
        for slot in range(8):
            pos = origin + 2 * slot
            entry = struct.unpack_from("<H",meta,pos)[0]
            if (entry >> 12) == 8:
                new = (entry & 0x0fff) | 0x9000
                if mid in PAVEMENT_BASES and slot < 4:
                    new = (9<<12)|(512+new_tiles[slot])
                struct.pack_into("<H",meta,pos,new)
    meta_path.write_bytes(meta)
    write_png(art_path,width,height,pix,palette)
    pal_path=root/"data/tilesets/secondary/cuordilava/palettes/09.pal"
    rows=pal_path.read_text().splitlines()
    assert rows[:3] == ["JASC-PAL","0100","16"]
    colors=[list(map(int,row.split())) for row in rows[3:]]
    for index,color in BASALT_COLORS.items():
        colors[index]=list(color)
    pal_path.write_text("\n".join(rows[:3]+[" ".join(map(str,x)) for x in colors])+"\n")
    print("Cuordilava basalt courtyard: 9 isolated metatiles, 4 unique graphic tiles; 20x20 map unchanged")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
