#!/usr/bin/env python3
"""Architectural volcanic court on Cuordilava's original 4x2 plaza mural.

The source 64x32 transparent artwork is drawn into eight *existing* map cells
with inherited exact collision/elevation/warps. The result is a terraced basalt
seal with coherent copper rim and a small incandescent magma heart, not a flat
neon circle. No artwork is allocated outside the original landmark.
"""


def sculpt_volcanic_terrace(art, name):
    if name != "CENTRAL_VOLCANIC_PLAZA_CREST":
        return 0
    if (art.w, art.h) != (64, 32):
        raise ValueError("The original plaza must remain exactly 4x2 cells")
    previous = [row[:] for row in art.pix]
    # Unobstructed underlying original town paving is shown at the outer edge:
    # palette index 0 is transparent ONLY on the overlay layer.
    art.pix = [[0 for _ in range(64)] for _ in range(32)]

    def pixel(x, y, c):
        if 0 <= x < 64 and 0 <= y < 32:
            art.pixel(x, y, c)

    def bounded_line(x0, x1, y, colour):
        for x in range(max(0, x0), min(63, x1) + 1):
            pixel(x, y, colour)

    # Broad six-sided old-lava slab. These horizontal courses create a readable
    # low retaining wall without stacking additional collision layers.
    edges = {}
    for y in range(2, 30):
        taper = max(0, 6 - min(y - 2, 29 - y))
        left, right = 4 + taper, 59 - taper
        edges[y] = (left, right)
        for x in range(left, right + 1):
            # Basalt blocks: calm dark fields, broad horizontal courses,
            # occasional light ash mortar, NOT a uniform luminous grid.
            if y in (2, 3, 27, 28, 29):
                tone = 5 if y in (2, 27) else 8
            elif x in (left, right):
                tone = 6
            elif y % 6 == 1:
                tone = 5
            elif ((x + (y // 6) * 7) % 15) == 0:
                tone = 7
            elif ((x * 3 + y * 5) % 19) == 0:
                tone = 4
            else:
                tone = 2 if ((x // 8 + y // 7) % 3 == 0) else 3
            pixel(x, y, tone)

    # Left and right terraces frame the central seal and restore a visible
    # foreground/shadow separation rather than a bright rectangular platform.
    for x0, x1 in ((5, 19), (44, 58)):
        for y in (6, 7, 22, 23):
            bounded_line(x0, x1, y, 8 if y in (7, 23) else 6)
        for y in (10, 15, 19):
            bounded_line(x0 + 2, x1 - 2, y, 5)
        for x in range(x0 + 3, x1 - 2, 6):
            pixel(x, 9, 13)
            pixel(x + 1, 9, 8)
            pixel(x, 24, 11)
            pixel(x + 1, 24, 6)
        # Recessed planters / mineral drains form two pairs of real masses.
        for y in (12, 17):
            for x in range(x0 + 4, x1 - 3):
                if (x + y) % 4:
                    pixel(x, y, 8)
            for x in (x0 + 4, x1 - 4):
                pixel(x, y - 1, 5)
                pixel(x, y + 1, 6)

    # Shield-shaped volcanic insignia: faceted outer slab, copper shoulder,
    # deep obsidian well, and a small glowing lava-furnace icon in its center.
    # The sculpted hexagon occupies the same existing four central cells.
    for y in range(4, 28):
        taper = abs(y - 16)
        half_width = 17 - (taper // 3)
        for x in range(32 - half_width, 33 + half_width):
            distance = abs(x - 32)
            border = half_width - distance
            top = y in (4, 5, 26, 27)
            if border <= 1:
                c = 8 if y >= 20 else 6
            elif border == 2 or top:
                c = 13 if y < 19 else 5
            elif border in (3, 4):
                c = 11 if y < 20 else 12
            elif distance >= 8:
                c = 5 if (x + y) % 4 else 8
            else:
                c = 1 if y < 14 else 3
            pixel(x, y, c)

    # Ash-dark inner furnace, with a clearly separated copper rim and flames.
    for y in range(9, 24):
        half = 8 - abs(y - 16) // 3
        for x in range(32 - half, 33 + half):
            pixel(x, y, 8 if abs(x - 32) >= half - 1 else 2)
    for y in range(10, 23):
        half = 7 - abs(y - 16) // 3
        if half > 0:
            pixel(32 - half, y, 13)
            pixel(32 + half, y, 13)

    for x0, y0, x1, y1, c in (
        (31, 10, 28, 16, 12), (28, 16, 31, 22, 11),
        (31, 22, 36, 18, 14), (36, 18, 34, 12, 12),
        (34, 12, 32, 15, 14), (32, 15, 31, 18, 11),
    ):
        art.line(x0, y0, x1, y1, c)
    for x, y in ((31, 14), (32, 15), (32, 16), (33, 17), (34, 18), (32, 19)):
        pixel(x, y, 14)

    # Eight tiny perimeter vents make the town functional and volcanic,
    # keeping teal and magenta as SECONDARY accents.
    for x, y in ((9, 7), (54, 7), (9, 24), (54, 24),
                 (17, 5), (46, 5), (17, 26), (46, 26)):
        pixel(x, y, 8)
        pixel(x + 1, y, 9)
        pixel(x, y + 1, 6)
    for x, y in ((11, 8), (52, 8), (11, 23), (52, 23)):
        pixel(x, y, 15)

    # Above/below bridge-like copper trim; intentionally broken by gate gaps.
    for y in (3, 28):
        for x in list(range(12, 22)) + list(range(43, 53)):
            pixel(x, y, 13 if x % 3 else 11)

    changed = sum(a != b for old_row, new_row in zip(previous, art.pix)
                  for a, b in zip(old_row, new_row))
    hot = sum(c in (11, 12, 13, 14) for row in art.pix for c in row)
    neon = sum(c in (9, 10, 15) for row in art.pix for c in row)
    dark = sum(c in (1, 2, 3, 4, 5, 6, 7, 8) for row in art.pix for c in row)
    if changed < 850 or hot < 100 or dark < 700 or neon >= hot // 2:
        raise ValueError(f"Terrace lost its material hierarchy: {changed=}, {hot=}, {dark=}, {neon=}")
    if any(art.pix[y][x] for y in (0, 31) for x in range(64)):
        raise ValueError("Terrace touches the top/bottom map-cell seam")
    if any(art.pix[y][x] for x in (0, 63) for y in range(32)):
        raise ValueError("Terrace overflows the original 4x2 mural")
    if any(not 0 <= c <= 15 for row in art.pix for c in row):
        raise ValueError("Terrace violates GBA indexed palette limits")
    return changed
