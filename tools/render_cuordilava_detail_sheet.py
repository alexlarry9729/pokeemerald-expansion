#!/usr/bin/env python3
"""Inspect Cuordilava landmark seams at the original 16-pixel map-cell joins.

The input PNGs are diagnostic renders, NOT emulator screenshots. This tool
produces a side-by-side day/night close-up of the seven existing murals,
with a one-map-cell margin, subtle cell grid and orange mural outlines.
No gameplay, palette, metatile or ROM asset is changed.
"""
from __future__ import annotations

import argparse
import json
import struct
import zlib
from pathlib import Path

from render_cuordilava_preview import pack_png
from sculpt_cuordilava_city import LANDMARKS

CELL = 16 * 3
GAP = 10
PADDING = 1


def rgb_png(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    i, stream, width, height = 8, bytearray(), None, None
    while i < len(data):
        length = struct.unpack_from(">I", data, i)[0]
        tag = data[i + 4:i + 8]
        chunk = data[i + 8:i + 8 + length]
        if len(chunk) != length or zlib.crc32(tag + chunk) & 0xffffffff != struct.unpack_from(">I", data, i + 8 + length)[0]:
            raise ValueError(f"{path}: invalid PNG chunk")
        if tag == b"IHDR":
            width, height, depth, color, compression, filt, interlace = struct.unpack(">IIBBBBB", chunk)
            if (depth, color, compression, filt, interlace) != (8, 2, 0, 0, 0):
                raise ValueError(f"{path}: only non-interlaced RGB8 previews are supported")
        elif tag == b"IDAT":
            stream.extend(chunk)
        elif tag == b"IEND":
            break
        i += length + 12
    if width is None or height is None:
        raise ValueError(f"{path}: missing dimensions")
    raw = zlib.decompress(stream)
    stride = width * 3
    if len(raw) != height * (stride + 1):
        raise ValueError(f"{path}: truncated RGB image")
    pixels = bytearray(width * height * 3)
    for y in range(height):
        offset = y * (stride + 1)
        if raw[offset] != 0:
            raise ValueError(f"{path}: unexpected PNG scanline filter")
        pixels[y * stride:(y + 1) * stride] = raw[offset + 1:offset + stride + 1]
    return width, height, pixels


def put(canvas, sheet_w, x, y, rgb):
    offset = (y * sheet_w + x) * 3
    canvas[offset:offset + 3] = rgb


def generate(source_dir: Path, out_dir: Path):
    previews = {mode: rgb_png(source_dir / f"cuordilava-{mode}.png") for mode in ("day", "night")}
    if any((w, h) != (20 * CELL, 20 * CELL) for w, h, _ in previews.values()):
        raise ValueError("Expected identical 960x960 previews from the original 20x20 map")
    tile_w = (4 + 2 * PADDING) * CELL
    sheet_w = tile_w * 2 + GAP
    rows = [(name, bx, by, w, h, (h + 2 * PADDING) * CELL)
            for name, bx, by, w, h in LANDMARKS]
    sheet_h = sum(entry[5] for entry in rows) + GAP * (len(rows) - 1)
    canvas = bytearray(bytes((29, 31, 39)) * (sheet_w * sheet_h))
    manifest = []
    out_y = 0
    for name, bx, by, w, h, crop_h in rows:
        if not (PADDING <= bx and PADDING <= by and bx + w + PADDING <= 20 and by + h + PADDING <= 20):
            raise ValueError(f"{name}: cannot inspect mural with a one-cell safety margin")
        source_x, source_y = (bx - PADDING) * CELL, (by - PADDING) * CELL
        for col, mode in enumerate(("day", "night")):
            src_w, _, pixels = previews[mode]
            x0 = col * (tile_w + GAP)
            for dy in range(crop_h):
                left = ((source_y + dy) * src_w + source_x) * 3
                dst = ((out_y + dy) * sheet_w + x0) * 3
                canvas[dst:dst + tile_w * 3] = pixels[left:left + tile_w * 3]
            # Thin, sampled guidelines. Only the diagnostic sheet shows these.
            for gx in range(0, 4 + 2 * PADDING + 1):
                xx = x0 + gx * CELL
                if xx >= x0 + tile_w:
                    continue
                for yy in range(out_y, out_y + crop_h, 3):
                    put(canvas, sheet_w, xx, yy, (173, 179, 185))
            for gy in range(0, h + 2 * PADDING + 1):
                yy = out_y + gy * CELL
                if yy >= out_y + crop_h:
                    continue
                for xx in range(x0, x0 + tile_w, 3):
                    put(canvas, sheet_w, xx, yy, (173, 179, 185))
            # Orange border marks the actual 4x1 / 4x2 landmark mural bounds.
            border = (238, 148, 79)
            x1 = x0 + PADDING * CELL
            x2 = x1 + w * CELL - 1
            y1 = out_y + PADDING * CELL
            y2 = y1 + h * CELL - 1
            for xx in range(x1, x2 + 1):
                put(canvas, sheet_w, xx, y1, border)
                put(canvas, sheet_w, xx, y2, border)
            for yy in range(y1, y2 + 1):
                put(canvas, sheet_w, x1, yy, border)
                put(canvas, sheet_w, x2, yy, border)
        manifest.append({
            "name": name, "map_origin": [bx, by], "metatiles": [w, h],
            "sheet_top_px": out_y, "sheet_row_height_px": crop_h,
            "columns": ["day", "night"], "grid_cell_px": CELL
        })
        out_y += crop_h + GAP
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / "cuordilava-landmark-alignment.png"
    pack_png(output, sheet_w, sheet_h, canvas)
    (out_dir / "cuordilava-landmark-alignment.json").write_text(
        json.dumps({
            "note": "Diagnostic only: orange mural bounds and 16x16 map-cell joins are not ROM graphics",
            "landmarks": manifest
        }, indent=2) + "\n", encoding="utf-8")
    print(f"Landmark seams: {len(rows)} day/night crops, {sheet_w}x{sheet_h}: {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("build-preview"))
    parser.add_argument("--output-dir", type=Path, default=Path("build-preview"))
    args = parser.parse_args()
    generate(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
