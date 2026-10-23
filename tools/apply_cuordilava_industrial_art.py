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
        416,
        "eNoNyklv2loUAODVvWdx7j2sGaVsUE1rUju1EwhQwAOGNWZUwn8Kg8RrGglPUgh03SltEjL8rdftp2/9Dq7fwc07yCjsSoG5AgsFlgpbKRAoECoQKRArLFEgXcJMCbMlzJUwX8JCCeclXJRwWcJVCYMShiWMShiXMPk334v8e1Z4L9Yf4PoD3HyAtCoyKsuqIqeKvCoKqrhSYa7CQoWlylYqBCqEKkQqxCpLVMiV8aqM8zIuyrgs46qMQRnDMkZljMuYlDF9LDLHInsscscif8wKx2L9Ea4/ws1HSGsio7GsJnKayGuioIkrDeYaLDRYamylQaBBqEGkQayxRIO0jhkdszrmdMzrWNDxSse5jgsdlzqudAx0DHWMdIx1THRMn4jMicieiNyJyJ+wwolYf4LrT3DzCdKGyBgsa4icIfKGKBjiyoC5AQsDlgZbGRAYEBoQGRAbLDEgbWLGxKyJORPzJhZMvDJxbuLCxKWJKxMDE0MTIxNjExMT06cicyqypyJ3KvKnrHAq0mewPoN0BTIVka2IXEXkK6JQEesKfKmwrxWWrsK6Cv9VxZequK6Kr1VxUxXpc1ifw0MNH2v4VMNDDZ9r+FLD1xq+1bBVl1ZdOnXZqct2g6wG2Q1yGvTUSL00Us0mtZrUbpLVJLtJTpPcJnWadGhiq0VWC90WHVpotdFupx7bdGjja5ssCx8s+WjJJ0seLPlsyRdLvlryzZJNm1o2tW2ybLJtcmxyberY9N3GHzb+tPGXjb9tvLfxj41/bTzYeObIiiPPHVlzZN2RDUd+dmTLIctB16GDg1WXzl2quVR3yXLRdlM/3dS9m3p06eDi6z/s4ENHPnbkU0ceOvK5I1868rUj3zryu4c/PPzp4S8Pf3t47+EfD/96+ODho4dPHh48fPbwxcNXD988POvKaleed2WtK+td2ejKz13Z7MpWV7a70upKuyudrnS7svOv9ajWo3qP2j2yemT3yOnRfS/11Eu99FKbPgV9CvsU9SnuU9Kn2z5t+3TXp12f9n068lnRZ4rPyj7b+CzweehD5PPY54nPbn229fmdDzuf731+NGDFAVMGbDNgwYCHAx4NIB7wZMBuB2w74HcDvhvAfsCPhqw4ZMqQBUOKhpQMaTuk3ZD2Q/o2pGBE0YiSEW1HtBvRfkTfRnQ0ZsUxU8ZsM2bBmIdjiMY8HvNkzG7HbDvmd2PYjfl+zI8mrDhhyoRtJiyY8HDCownEE55M2O2EbSf8bsJ3E9hP+NGUFadMmbJgStGUkiltp7Sb0n5K36YUXPDwAqILHl/wzSULLnl4yeNLnlyyoxkrzthmRsGMwhlFM4pnlMzof9LDQjo=",
    ),
    "secondary": ("dbdbef86d49b78e7527d08f7a5292438ecfffd1d", 1248, ""),
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

def redesign_secondary(rows: list[list[int]]) -> None:
    """Town-only cyberpunk industry: four families of reusable facade details."""
    def paint(ids, kind):
        for tid in ids:
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
        redesign_secondary(rows)
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

if __name__ == "__main__":
    main()
