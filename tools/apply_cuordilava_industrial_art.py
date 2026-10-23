#!/usr/bin/env python3
"""Reproducible town-private 4bpp architectural redraw, first industrial pass.

These deltas are absolute pixel indices from the audited original Cuordilava
atlases, not palette edits. The map, warps, collisions and metatile code stay
unchanged. Black alloy roofs, ribbed vents, furnace slats and neon windows
approximate the user's first volcano-cyberpunk reference within 8x8 GBA art.
Run before validating, rendering and compiling the town test ROM.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import struct
import zlib
from pathlib import Path

from render_cuordilava_preview import png_indexed

PATCHES = {
    "primary": (
        "21cc88bb43166f370085db207dbbc2b0c6b3782f",
        362,
        "eNoNyslu2mwUANDV/e7ifr6szSSxQbUbk9qpnUCA/m2A2qyxwUYJ78Qk0aaR8CSFQNad0iFt2tf6e9Zn8wyvn+HNMyxqMNdwoeFSw5UGaw1jDRMNUw0zDXINVZ2KOpV0KutU0amq00KnpU4rndY6xTolOqU6ZTrl/+ZzWXkO1edyc4TXR3hzhKohiwaUDFk2ZMWQVUPODVwYuDRwZcDawNjAxMDUwMyA3MByg+YNWjRo2aBVg9YNihuUNChtUNagvEHqsSwey9KxLB/LyjFUj+XmBV6/wJsXqJqyaELJlGVTVkxZNeXcxIWJSxNXJqxNjE1MTExNzEzITVQtKlpUsqhsUcWiqkVzixYWLS1aWbS2KLYosSi1KLMot0g9kcUTWTqR5RNZOYHqidy8xOuXePMSVVsWbSjZsmzLii2rtpzbuLBxaePKhrWNsY2JjamNmQ25japDRYdKDpUdqjhUdWju0MKhpUMrh9YOxQ4lDqUOZQ7lDqmnsngqS6eyfCorp1A9leoZbs5QbWKxKUtNWW7KSlNWm3LTxPdN+NAEtYWbFr5ryfcted2SH1rypiXVc9yc4482/WzTY5t+tel3m57a9KdNf9v0uqNcdJR+R3nbUd50+aLLvS73u/zYLTx1Cx979KlHn3v0pUdfe/TQo289+t6js77S7CvnfaXdVzp9pdtXXvWV1oDPB9wecGfAnweFh0Hho0ufXPrs0heXvrr04NI3l7679MOlny49uvTLpd8uPbn0x6W/Lp15SstTzj2l7SkdT+l6yitP+c9TXnvKG0+58JSep/Q9ZeApb/+1IbeH3BnymyFfDLk35P6QH4aFx2HhaVjYjjgecTLidMTZiPMR3454N+K7Ee9HfBhxzYe6D5oPDR+2PsS+SHxMfZH5Ivfh1oedL+583Pvi4ItaAPUAtAC2AcSBSAKRBpgFIg/gNoBdIO4CsQ/wEIjaGOpj0MYQjzkdcz7m3Zj3Yz6M+X7M8YTTCecT3k14P+HDhO8nXAuhHoIWwjaEOBRJiGkoslDkIdyGsAvFXYj7UBxCUYugHoEWwTaCOBJJJNIIs0jkEdxGsIvEXST2ER4iUZtCfQraFOIpp1POp7yb8n7KhynfTzm+FMklppciuxTbK4ivRHIlsiuRX0FtBvUZbGcczziZcTrjbMb5jP8HHr0WAg==",
    ),
    "secondary": ("dbdbef86d49b78e7527d08f7a5292438ecfffd1d", 663, ""),
}

def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xffffffff)

def write_png(path: Path, width: int, height: int, pixels: list[list[int]], palette: bytes) -> None:
    assert width == 128 and len(palette) == 48
    raw = bytearray()
    for row in pixels:
        assert len(row) == width and all(0 <= color < 16 for color in row)
        raw.append(0)  # PNG filter 0: preserve all 4bpp palette indices
        for x in range(0, width, 2):
            raw.append((row[x] << 4) | row[x + 1])
    ihdr = struct.pack(">IIBBBBB", width, height, 4, 3, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"PLTE", palette)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b"")
    )

def protected_spring_secondary_tiles(root: Path) -> frozenset[int]:
    """Protect water, cliff and thermal-sand art reused by the thermal basin.

    Factory tile IDs also occur in the original spring water and basalt border.
    Repainting them introduced red metal grids in the water. Audit the exact
    Lavaridge layout instead of assuming every factory-looking tile is unique.
    """
    layout = (root / "data/layouts/LavaridgeTown/map.bin").read_bytes()
    primary = (root / "data/tilesets/primary/general/metatiles.bin").read_bytes()
    secondary = (root / "data/tilesets/secondary/cuordilava/metatiles.bin").read_bytes()
    assert len(layout) == 800
    forbidden: set[int] = set()
    for y in range(11):
        for x in range(8):
            cell = struct.unpack_from("<H", layout, 2 * (20 * y + x))[0] & 1023
            data, mid = (secondary, cell - 512) if cell >= 512 else (primary, cell)
            assert 16 * (mid + 1) <= len(data)
            for slot in range(8):
                tile = struct.unpack_from("<H", data, 16 * mid + slot * 2)[0] & 1023
                if tile >= 512:
                    forbidden.add(tile - 512)
    return frozenset(forbidden)


def redesign_secondary(rows: list[list[int]], forbidden_tiles: frozenset[int]) -> None:
    """Town-only cyberpunk industry: four families of reusable facade details."""
    def paint(ids, kind):
        for tid in ids:
            if tid in forbidden_tiles:
                continue  # The same art appears in the pool or thermal paths.
            ox, oy = (tid % 16) * 8, (tid // 16) * 8
            def dot(x,y,c):
                if 0 <= x < 8 and 0 <= y < 8 and rows[oy+y][ox+x]:
                    rows[oy+y][ox+x] = c
            def line(a,b,x,y,c):
                dx=abs(x-a); dy=-abs(y-b); sx=1 if a<x else -1;sy=1 if b<y else -1;err=dx+dy
                while True:
                    dot(a,b,c)
                    if (a,b)==(x,y):break
                    e=2*err
                    if e>=dy:err+=dy;a+=sx
                    if e<=dx:err+=dx;b+=sy
            if kind==0:  # dark roof alloy louvres
                for y in (2,5):line(1,y,6,y,12)
                for x in (2,5):dot(x,1,9);dot(x,6,14)
                line(0,7,7,7,13)
            elif kind==1:  # fiery shutter/air intake
                line(1,1,6,1,6)
                for y in (2,4,6):line(2,y,5,y,13 if y==4 else 12)
                for x in (1,6):line(x,2,x,6,7)
                dot(3,3,14);dot(4,5,14)
            elif kind==2:  # edge windows (respect alpha)
                for y in (2,4):line(2,y,5,y,13)
                dot(3,5,14);dot(4,5,14)
            elif kind==3:  # cyber storefront panels
                for y in (1,5):line(1,y,6,y,11)
                for x in (2,5):line(x,2,x,4,7)
                dot(3,3,10);dot(4,6,14)
            elif kind==4:  # metallic roof braces
                line(0,0,7,0,8);line(0,7,7,7,6)
                for x in (1,3,5,7):line(x,2,x,5,12)
                dot(1,1,10);dot(6,6,14)
    paint([136,137,138,139,152,153,154,155],0)
    paint([200,201,204,205,220,221,232,233,248,249],1)
    paint([202,203,206,207,222,223,246,247,262,263,278,279],2)
    paint([168,169,180,181,184,185,208,209,210,211,392,393,396,397,412,413],3)
    paint([390,391,401,402,404,405,406,407,416,417,418,420,421,422,423],4)


def transform(root: Path, kind: str) -> None:
    path = root / "data/tilesets" / kind / "cuordilava" / "tiles.png"
    source = path.read_bytes()
    signature = hashlib.sha1(b"blob " + str(len(source)).encode() + b"\x00" + source).hexdigest()
    expected, total, encoded = PATCHES[kind]
    if signature != expected:
        raise ValueError(f"{path}: source atlas changed; refusing to apply stale pixel offsets")
    width, height, rows = png_indexed(path)
    assert width == 128 and height == (256 if kind == "primary" else 232)
    start = source.index(b"PLTE") + 4
    palette = source[start:start + 48]
    assert len(palette) == 48
    if kind == "secondary":
        previous = [row[:] for row in rows]
        redesign_secondary(rows, protected_spring_secondary_tiles(root))
        count = sum(a != b for ra, rb in zip(previous, rows) for a, b in zip(ra, rb))
        assert count == total, (count, total)
    else:
        edits = zlib.decompress(base64.b64decode(encoded))
        assert len(edits) == total * 3
        for i in range(total):
            offset, color = struct.unpack_from("<HB", edits, i * 3)
            assert 0 <= offset < width * height and 0 <= color <= 15
            y, x = divmod(offset, width)
            assert rows[y][x] != color  # no no-op or stale pixels
            rows[y][x] = color
    write_png(path, width, height, rows, palette)
    width2, height2, result = png_indexed(path)
    assert (width2, height2, result) == (width, height, rows)
    print(f"{kind}: recolored {total} indexed pixels, {path.stat().st_size} bytes")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args()
    for kind in ("primary", "secondary"):
        transform(args.root, kind)
    # Phase II overlays town-private industrial roof/facade features on validated first-pass art.
    from generate_cuordilava_architecture import main as apply_architecture_phase2
    apply_architecture_phase2(args.root)
    from dress_cuordilava_courtyard import run as dress_thermal_courtyard
    dress_thermal_courtyard(args.root)
    # Color/texture correction is restricted to pool-only secondary tiles 320/321/336.
    from refine_cuordilava_water import run as refine_hot_spring_water
    refine_hot_spring_water(args.root)
    from sculpt_cuordilava_city import run as sculpt_town_landmarks
    sculpt_town_landmarks(args.root)
    from dress_cuordilava_scenery import run as dress_scenery
    dress_scenery(args.root)
    # Last pass: mineral-water surface and organic bank reuse existing graphics.
    from soften_cuordilava_springs import run as soften_thermal_springs
    soften_thermal_springs(args.root)
    from deindustrialize_cuordilava_spa import run as deindustrialize_spa
    deindustrialize_spa(args.root)
    from construct_cuordilava_lower_facade import run as build_lower_facade
    build_lower_facade(args.root)
    from dress_cuordilava_gym_ground_floor import run as build_gym_ground_floor
    build_gym_ground_floor(args.root)

if __name__ == "__main__":
    main()
