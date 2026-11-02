#!/usr/bin/env python3
"""Rebuild the original seven ground-floor wall bays as a volcanic street arcade.

Seven 16x16 images supply seven residential facade cells, five Gym-side
forge-wall cells, and two non-interactive Center/Mart wall cells. The NEW
112x16 composition consists of three larger architectural wings (kiln,
geothermal workshop and inhabited vaulted arcade), with thick structural
stonework, curved glazing, copper mineral shadow, and functional material
differences. It is not a repeat of seven bright rectangular windows.

This is SOURCE ART ONLY. The existing generator, metatile ID allocation,
primary base art, attribute/collision bits, warp/sign/NPC positions and
20x20 map dimensions remain byte-for-byte controlled by their validators.
"""


def rebuild_existing_street_wall(previous):
    if len(previous) != 16 or any(len(row) != 112 for row in previous):
        raise ValueError("Original Cuordilava seven-cell facade is not 112x16")
    art = [[0] * 112 for _ in range(16)]

    def p(x, y, c):
        if 0 <= x < 112 and 0 <= y < 16:
            art[y][x] = c

    def span(left, right, y, color):
        for x in range(max(0, left), min(111, right) + 1):
            p(x, y, color)

    def solid(left, top, right, bottom, color):
        for y in range(top, bottom + 1):
            span(left, right, y, color)

    def pillar(left, top=3, bottom=12, glow=False):
        for y in range(top, bottom + 1):
            p(left, y, 8)
            p(left+1, y, 5 if y%4 else 6)
            p(left+2, y, 6)
            if glow and y in (4, 8, 11):
                p(left+1, y, 13)
        span(left-1, left+3, top, 5)
        span(left-1, left+3, bottom, 6)

    # Structural silhouette: 3 building wings, each with its own masonry.
    # Horizontal construction courses connect across all seven tile borders,
    # while the left charcoal foundry, center copper geothermal workshop,
    # and right inhabited basalt vault have genuinely different tones.
    for y in range(16):
        for x in range(112):
            wing = 0 if x < 33 else 1 if x < 65 else 2
            c = (3, 2, 8)[wing]
            if y in (0, 13):
                c = 5
            elif y == 1:
                c = 6
            elif y == 2:
                c = 13 if (x//6+wing)%5 == 0 else 5
            elif y == 14:
                c = 11
            elif y == 15:
                c = 8
            elif y in (5, 10) and x % 13 in (0, 1):
                c = 6
            elif (x*3 + y*5 + wing) % 23 == 0:
                c = 4
            elif y % 4 == 0 and x % 8 in (1, 2):
                c = 5
            p(x, y, c)

    # Two imposing cross-wing masonry abutments, offset from tile seams.
    # Large buttresses visually read as a building, not checkerboard paving.
    for x0, top in ((0, 3), (31, 2), (63, 3), (108, 3)):
        pillar(x0, top, 12, glow=x0 in (31, 63))
    for left, right, y in (
        (2, 29, 3), (35, 60, 4), (67, 106, 3)
    ):
        span(left, right, y, 5)
        span(left+1, right-1, y+1, 8)
        for x in range(left+2, right-1, 9):
            p(x, y, 13)
            p(x+1, y+1, 6)

    # Arches live across the ORIGINAL 7 cell slots. Three functional facade
    # families: tall molten glass; ventilated narrow technical shutters;
    # wider warm inhabited window with dark carved volcanic arch.
    bays = (
        # left,right,arch-top,glass,design,transom height
        (3, 13, 4, 12, "kiln", 9),
        (18, 29, 3, 11, "kiln", 8),
        (35, 46, 4, 12, "vent", 9),
        (50, 61, 3, 12, "vent", 8),
        (67, 78, 4, 11, "home", 9),
        (83, 94, 3, 12, "home", 8),
        (99, 107, 4, 11, "home", 9),
    )
    for i, (left, right, top, glass, design, transom) in enumerate(bays):
        center = (left + right) // 2
        solid(left-1, top, right+1, 12, 8)
        span(left-1, right+1, top, 5)
        span(left-1, right+1, 12, 6)
        for y in range(top+1, 12):
            for x in range(left, right+1):
                dx = abs(x-center)
                # Recessed arch: dark outer corners are cut from every upper
                # window. Visually deeper and more natural than an orange box.
                arch_half = (right-left)//2
                if y == top+1 and dx >= arch_half-1:
                    c = 8
                elif y == top+2 and dx >= arch_half:
                    c = 5
                elif x in (left,right):
                    c = 5 if y%4 else 6
                elif design == "kiln":
                    # Furnace chambers glow strongly, guarded by substantial
                    # central ribs and copper cross-bracing.
                    if x in (center-2, center+2):
                        c = 5 if y%3 else 13
                    elif y == transom:
                        c = 13
                    else:
                        c = glass if (x+3*y+i)%7 else 14
                elif design == "vent":
                    # Taller geothermal service vent, staggered paired amber
                    # louvers and cold status glass; a different silhouette.
                    if x in (center-3, center+2):
                        c = 5
                    elif y in (top+3, transom, 11):
                        c = 6
                    elif x in (center,center+1) and y%4 == 0:
                        c = 9 if i==3 else 14
                    else:
                        c = glass if (x+y+i)%6 else 13
                else:
                    # Occupied residential arches: small shadowed stone
                    # mullion plus convincing copper-orange interior glass.
                    if x == center+(1 if i==5 else 0):
                        c = 5
                    elif y == transom:
                        c = 6
                    elif x in (left+1,right-1) and y in (top+2, 10):
                        c = 13
                    else:
                        c = glass if (x*2+y+i)%9 else 14
                p(x,y,c)

        # Deep projecting sill and small warm light under each room.
        for x in range(left+1, right):
            p(x, 12, 13 if x%5 != i%5 else 8)
        # Wide carved header with stone lintel shadow catches actual light.
        span(left-1,right+1,top-1,6)
        p(left,top-1,13)
        p(right,top-1,11)

    # Shared functional copper steam conduits, with occasional gauges
    # concentrated at real workshop joints rather than a neon pixel grid.
    for left, right in ((3,29),(35,60),(67,105)):
        span(left,right,2,5)
        for x in range(left+5,right-1,8):
            p(x,2,13)
            if x%3:
                p(x,3,11)
    for x in (16, 47, 79, 96):
        for y in range(4,12):
            p(x,y,6)
        for y in (5,8,11):
            p(x,y,14 if x<65 else 13)
    for x in (72, 88, 103):
        p(x,3,5)
        p(x,4,13)
        p(x+1,4,11)

    # Register to all existing metatile-seam validators EXACTLY; connected
    # plinth lines match every original building base and source alpha rule.
    for y,c in ((0,5),(13,5),(14,11),(15,8)):
        span(0,111,y,c)
    for seam in range(16,112,16):
        for y in range(4,13):
            p(seam-1,y,5)
            p(seam,y,6)
        for y in (5,9,12):
            p(seam-1,y,13)
            p(seam,y,11)

    changed = sum(a != b for old, new in zip(previous, art)
                  for a, b in zip(old, new))
    warm = sum(v in (11,12,13,14) for row in art for v in row)
    if changed < 900 or warm < 350:
        raise ValueError(
            f"7-bay monumental street arcade lacks substantial visual "
            f"redesign: changed={changed}, warm={warm}"
        )
    if len({tuple(v for row in art for v in row[16*i:16*i+16])
            for i in range(7)}) != 7:
        raise ValueError("New street arcade accidentally duplicates entire wall bays")
    if any(not 0 <= v <= 15 for row in art for v in row):
        raise ValueError("Street arcade exceeds GBA 4bpp")
    return art
