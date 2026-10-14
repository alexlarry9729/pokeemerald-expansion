#!/usr/bin/env python3
"""Validate palette files and the indexed art for the cyberpunk Lavaridge pass.

Run from the repository root:
    python3 tools/validate_cyberpunk_assets.py
"""
from __future__ import annotations

import argparse
from pathlib import Path
import struct
import sys


def parse_palette(path: Path) -> list[tuple[int, int, int]]:
    lines = path.read_text(encoding="ascii").splitlines()
    if len(lines) < 3 or lines[0] != "JASC-PAL" or lines[1] != "0100":
        raise ValueError(f"{path}: expected a JASC-PAL 0100 header")

    try:
        expected = int(lines[2])
    except ValueError as exc:
        raise ValueError(f"{path}: invalid colour count {lines[2]!r}") from exc

    rows = [line.split() for line in lines[3:] if line.strip()]
    if len(rows) != expected:
        raise ValueError(
            f"{path}: header declares {expected} colours but found {len(rows)}"
        )

    colours: list[tuple[int, int, int]] = []
    for index, row in enumerate(rows):
        if len(row) != 3:
            raise ValueError(f"{path}: colour {index} must have exactly 3 channels")
        try:
            rgb = tuple(int(channel) for channel in row)
        except ValueError as exc:
            raise ValueError(f"{path}: colour {index} contains a non-integer") from exc
        if any(channel < 0 or channel > 255 for channel in rgb):
            raise ValueError(f"{path}: colour {index} has a channel outside 0..255")
        colours.append(rgb)  # type: ignore[arg-type]
    return colours


def parse_palette_mask(path: Path) -> list[int]:
    values: list[int] = []
    for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), 1):
        value = line.partition("#")[0].strip()
        if not value:
            continue
        try:
            index = int(value, 10)
        except ValueError as exc:
            raise ValueError(f"{path}:{line_number}: expected a decimal palette index") from exc
        if not 0 <= index <= 15:
            raise ValueError(f"{path}:{line_number}: palette index {index} is outside 0..15")
        values.append(index)
    return values


def validate_indexed_tileset_png(path: Path) -> None:
    """Check the PNG signature, IHDR and indexed 4bpp format expected by GBA tiles."""
    data = path.read_bytes()
    if len(data) < 45 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: file is not a complete PNG")
    if data[12:16] != b"IHDR" or struct.unpack(">I", data[8:12])[0] != 13:
        raise ValueError(f"{path}: missing or malformed IHDR chunk")

    width, height = struct.unpack(">II", data[16:24])
    bit_depth, colour_type = data[24], data[25]
    if (width, height) != (128, 232):
        raise ValueError(
            f"{path}: expected 128×232 tile atlas, found {width}×{height}"
        )
    if bit_depth != 4 or colour_type != 3:
        raise ValueError(
            f"{path}: expected a 4-bit indexed PNG, found bit depth {bit_depth}, "
            f"colour type {colour_type}"
        )
    if b"IDAT" not in data or b"IEND" not in data:
        raise ValueError(f"{path}: missing image data or PNG end chunk")


def luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = rgb
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    palette_dir = root / "data/tilesets/secondary/lavaridge/palettes"
    object_palette_dir = root / "graphics/object_events/palettes"
    tiles_png = root / "data/tilesets/secondary/lavaridge/tiles.png"

    palette_paths = sorted(palette_dir.glob("*.pal"))
    mask_paths = sorted(palette_dir.glob("*.pla"))
    neon_night = object_palette_dir / "neon_light.pal"
    neon_day = object_palette_dir / "neon_light_day.pal"

    try:
        validate_indexed_tileset_png(tiles_png)
    except (OSError, ValueError, struct.error) as exc:
        errors.append(str(exc))

    for path in palette_paths + [p for p in (neon_night, neon_day) if p.exists()]:
        try:
            colours = parse_palette(path)
            if path in (neon_night, neon_day) and len(colours) != 16:
                raise ValueError(f"{path}: object-event light palettes must have 16 colours")
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    for path in mask_paths:
        try:
            parse_palette_mask(path)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if not neon_night.is_file():
        errors.append(f"Missing expected night palette: {neon_night}")
    if not neon_day.is_file():
        errors.append(f"Missing expected day palette: {neon_day}")

    if neon_night.is_file() and neon_day.is_file():
        try:
            night = parse_palette(neon_night)
            day = parse_palette(neon_day)
            # Entries 1..6 form the cool neon ramp; 8..12 form the hot glow ramp.
            for index in (*range(1, 7), *range(8, 13)):
                if luminance(day[index]) >= luminance(night[index]):
                    errors.append(
                        f"{neon_day}: colour {index} is not dimmer than its night counterpart"
                    )
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if not palette_paths:
        errors.append(f"No Lavaridge palette files found under {palette_dir}")
    if not mask_paths:
        errors.append(f"No Lavaridge palette masks found under {palette_dir}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="pokeemerald-expansion repository root",
    )
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Cyberpunk asset validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(
        "Cyberpunk asset validation passed: indexed Lavaridge PNG, palettes/masks, "
        "and day/night ramps look valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
