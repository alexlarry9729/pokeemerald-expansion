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
    # Natural volcanic garden: mossy joints and properly green flowering
    # palms instead of bluish, almost black crowns.
    9: (34, 87, 53), 10: (55, 139, 78),
    11: (237, 112, 54), 12: (91, 76, 77),
    13: (124, 95, 89), 14: (244, 141, 66),
    15: (100, 168, 87),
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
    # Reference-led flowering basalt terraces, painted within the four
    # private 8x8 tiles already allocated for the original courtyard.
    # Only the appearance changes; animated water and map geometry do not.
    # Four 8x8 donor tiles join into ONE coherent 16x16 volcanic garden
    # pavement. Slab seams extend across quadrants; flowers form two
    # irregular organic islands instead of eight identically repeated
    # neon-orange targets. Existing metatile placements stay untouched.
    for corner, tid in enumerate(new_tiles):
        bx, by = (tid % 16) * 8, (tid // 16) * 8
        quad_x, quad_y = (corner % 2) * 8, (corner // 2) * 8

        def p(x, y, c):
            if 0 <= x < 8 and 0 <= y < 8:
                pix[by + y][bx + x] = c

        for y in range(8):
            for x in range(8):
                gx, gy = quad_x + x, quad_y + y
                # Connected copper-brown basalt courses with irregular
                # rectangular joints instead of fine fluorescent noise.
                colour = 12
                if gy in (3, 8, 13) and (gx + gy // 3) % 7 not in (0, 1):
                    colour = 13
                elif (gx + 4 * (gy // 5)) % 9 == 0:
                    colour = 8
                elif (gx * 3 + gy * 7) % 29 == 0:
                    colour = 13

                # Moss covers two asymmetrical terrace pockets. Their dark
                # borders sit in the cobblestones, never the actual water.
                west = (gx - 4) ** 2 * 2 + (gy - 5) ** 2 * 3 < 44
                east = (gx - 11) ** 2 * 2 + (gy - 11) ** 2 * 3 < 40
                if (west or east) and (gx * 5 + gy * 3) % 7:
                    colour = 9 if (gx + gy) % 4 < 2 else 10
                    if (gx + 3 * gy) % 11 == 0:
                        colour = 15
                p(x, y, colour)

        # Copper flowers are concentrated within the two moss islands,
        # avoiding uniform every-cell checkerboard orange dots.
        flowers = (
            (3, 4), (5, 6), (4, 8),
            (10, 10), (12, 11), (11, 13),
        )
        for gx, gy in flowers:
            x, y = gx - quad_x, gy - quad_y
            if 0 <= x < 8 and 0 <= y < 8:
                p(x, y, 11)
                p(x + 1, y, 14)
                p(x, y - 1, 15)
        # Edge stone remains continuous in full 16x16 metatile composition.

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
