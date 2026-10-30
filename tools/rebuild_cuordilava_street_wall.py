#!/usr/bin/env python3
"""One coherent lower-storey rebuild across the seven original house wall cells.

The same seven existing 16x16 tiles are also the pool of noninteractive wall
panels for the Center and Mart; the two reused images consequently inherit a
proper functional furnace-glass facade. No extra GBA graphic, palette, metatile,
map cell, roof, object or collision is allocated.

Within the original 112x16 panel, three adjoining architectural sections have
unequal widths (2, 2, 3 bays): a forge annex, a mineral engineering workshop
and an inhabited copper residential arcade. Material planes and copper pipes
cross every 16px boundary, rather than wallpapering seven identical windows.
"""


def rebuild_existing_street_wall(previous):
    if len(previous) != 16 or any(len(row) != 112 for row in previous):
        raise ValueError("Existing seven-cell wall is not 112x16")
    art = [[0] * 112 for _ in range(16)]

    def p(x, y, c):
        if 0 <= x < 112 and 0 <= y < 16:
            art[y][x] = c

    def line(x0, x1, y, c):
        for x in range(max(0, x0), min(111, x1) + 1):
            p(x, y, c)

    def column(x, y0, y1, left=5, right=6):
        for y in range(y0, y1 + 1):
            p(x, y, left)
            p(x + 1, y, right)
            if y in (5, 9, 12):
                p(x, y, 13)

    # Continuous charcoal/dark copper facade. Horizontal stone courses align
    # across all seven former cells; three color planes separate real wings.
    for y in range(16):
        for x in range(112):
            wing = 0 if x < 32 else 1 if x < 64 else 2
            c = (2, 3, 8)[wing]
            if y in (0, 13):
                c = 5
            elif y == 1:
                c = 6
            elif y == 2:
                c = 13 if x % 6 else 5
            elif y == 14:
                c = 11
            elif y == 15:
                c = 8
            elif (y + wing) % 5 == 0 and (x // 5) % 3 == 0:
                c = 4
            elif x % 11 == (wing + 2):
                c = 6
            p(x, y, c)

    # Irregular but joined upper industrial portico. The original four-tile
    # roof is above this street-wall row: this is an under-roof lintel, not an
    # extra building placed on top of a street or doorway.
    for x0, x1, top in ((1, 30, 3), (33, 62, 4), (65, 110, 3)):
        for y in range(top, 5):
            line(x0, x1, y, 5 if y == top else 6)
        line(x0, x1, 5, 8)
        for x in range(x0 + 2, x1, 6):
            p(x, 2, 13)

    # Seven different large furnace/inhabited glass bays. Their widths,
    # mullions, arched crowns and materials shift with each room type.
    # Each window contributes ~45+ warm pixels, rather than scattered dots.
    variations = (
        # (frame-left, frame-right, glass colour, frame scheme, crossbar row)
        (3, 13, 12, 0, 9),
        (18, 29, 11, 1, 8),
        (35, 46, 12, 2, 10),
        (50, 61, 12, 3, 8),
        (67, 78, 11, 1, 9),
        (83, 94, 12, 0, 10),
        (99, 108, 11, 2, 8),
    )
    for bay, (left, right, glass, frame, crossbar) in enumerate(variations):
        center = (left + right) // 2
        line(left - 1, right + 1, 5, 5)
        line(left - 1, right + 1, 12, 6)
        for y in range(6, 12):
            for x in range(left, right + 1):
                if x in (left, right):
                    color = 5 if bay % 2 else 8
                elif y == 6 and abs(x - center) > (right-left)//2 - 3:
                    color = 8
                elif (frame == 0 and x == center) or (
                    frame == 1 and x == center - 2
                ) or (frame == 2 and x == center + 2) or (
                    frame == 3 and x in (center - 2, center + 2)
                ):
                    color = 5
                elif y == crossbar:
                    color = 13
                elif (x * 7 + y * 3 + bay) % 11 == 0:
                    color = 14
                else:
                    color = glass
                p(x, y, color)
        for x in range(left + 1, right):
            p(x, 12, 13 if (x + bay) % 4 != 0 else 8)
        # Deep copper sill, not a wafer-thin colored window rectangle.
        p(left - 1, 11, 8)
        p(right + 1, 11, 6)
        p(left, 4, 13)
        p(right, 4, 13)

    # Three big masonry abutments divide the old seven-panels into adjacent
    # buildings; thicker than repeated one-pixel wallpaper seams.
    for x0 in (0, 31, 63, 109):
        for y in range(4, 13):
            for x in (x0, x0 + 1, x0 + 2):
                p(x, y, 8 if x == x0 else 5 if x == x0 + 1 else 6)
        for y in (5, 9):
            p(x0 + 1, y, 13)

    # Long functional steam/copper conduits join side wings, partially
    # reflecting the lights but never becoming prominent magenta grids.
    for start, end, y in ((3, 28, 3), (35, 59, 3), (67, 106, 3)):
        line(start, end, y, 5)
        for x in range(start + 2, end, 7):
            p(x, y, 13)
            if y + 1 < 5:
                p(x, y + 1, 11)
    for x0 in (16, 47, 79, 96):
        for y in range(3, 12):
            p(x0, y, 6)
            if y in (5, 8, 11):
                p(x0, y, 14)
    # Third wing is lived in: three small shadowed copper wall lamps.
    for x in (73, 88, 104):
        p(x, 3, 5)
        p(x, 4, 13)
        p(x + 1, 4, 11)

    # Keep the original exact soldered seams (and the paving/plinth belt);
    # these are invariants of the existing metatile validator.
    for y, c in ((0, 5), (13, 5), (14, 11), (15, 8)):
        line(0, 111, y, c)
    for seam in range(16, 112, 16):
        for y in range(4, 13):
            p(seam - 1, y, 5)
            p(seam, y, 6)
        for y in (5, 9, 12):
            p(seam - 1, y, 13)
            p(seam, y, 11)

    # Enforce art budget AND visual significance. The old 7-bay facade is
    # *completely* redrawn, but every original collision bit is still owned
    # by the unchanged world and attribute generator.
    changed = sum(
        before != after for old, new in zip(previous, art)
        for before, after in zip(old, new)
    )
    warm = sum(c in (11, 12, 13, 14) for row in art for c in row)
    if changed < 900 or warm < 350:
        raise ValueError(f"Cuordilava street wall not substantially rebuilt: {changed=}, {warm=}")
    if len(set(tuple(v for row in art for v in row[16*i:16*i+16]) for i in range(7))) != 7:
        raise ValueError("Street wall contains duplicated housing bays")
    if any(not 0 <= c <= 15 for row in art for c in row):
        raise ValueError("Street wall breaks GBA 4bpp palette")
    return art
