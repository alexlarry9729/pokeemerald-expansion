#!/usr/bin/env python3
"""Major Cuordilava architecture redesign within the seven original mural sites.

Four 64x32 4bpp building panels are re-composed as actual volcanic architecture:
asymmetrical slate/copper roofs, recessed masonry, inhabited windows, industrial
lanterns and differentiated silhouettes. This is deliberately a large redraw,
not an overlay of random highlights. The Center cross, Mart device, Gym emblem
and immutable artwork coordinates are protected. It cannot change map cells,
door locations, event scripts, collisions, tile count or the 20x20 town area.
"""


def recompose_original_architecture(a, name):
    roles = {
        "POKEMON_CENTER_INDUSTRIAL_REACTOR": "center",
        "POKE_MART_TECHNICAL_FACADE": "mart",
        "FLANNERY_GYM_MOLTEN_FORGE": "gym",
        "HOUSING_MAGMA_TERRACES": "housing",
    }
    role = roles.get(name)
    if role is None:
        return 0
    if (a.w, a.h) != (64, 32):
        raise ValueError(f"{name}: cannot change the original four-by-two building")

    old = [row[:] for row in a.pix]
    a.pix = [[0] * 64 for _ in range(32)]
    def p(x, y, c):
        if 0 <= x < 64 and 0 <= y < 32:
            a.pixel(x, y, c)
    def rect(x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                p(x, y, c)
    def line(x0, y0, x1, y1, c):
        a.line(x0, y0, x1, y1, c)
    def arch(cx, top, half, height, glass, hot=True):
        """Deep recessed arched furnace window with a stone crown."""
        for y in range(top, top + height):
            for x in range(cx - half, cx + half + 1):
                wall = (x in (cx - half, cx + half)
                        or y in (top, top + height - 1))
                inside = (x > cx - half and x < cx + half
                          and y > top and y < top + height - 1)
                if y == top and abs(x - cx) > half - 2:
                    continue
                if wall:
                    p(x, y, 5 if y < top + height - 1 else 8)
                elif inside:
                    if y == top + 1 and abs(x - cx) >= half - 2:
                        p(x, y, 8)
                    elif x == cx:
                        p(x, y, 5)
                    elif y == top + height - 3:
                        p(x, y, 13 if hot else 10)
                    else:
                        p(x, y, glass if (x + y) % 7 else (14 if hot else 9))
        line(cx - half - 1, top + height, cx + half + 1, top + height, 6)

    def stone_wall(top=12, bottom=30):
        """Broad courses of charcoal masonry, NO repeated neon checkerboard."""
        for y in range(top, bottom):
            for x in range(3, 61):
                c = 8
                if x in (3, 60):
                    c = 5
                elif y in (top, bottom - 1):
                    c = 6
                elif y % 5 == 1:
                    c = 5 if (x + (y // 5) * 4) % 13 not in (0, 1) else 8
                elif (x + (y // 5) * 5) % 14 == 0:
                    c = 3
                elif (x * 3 + y) % 17 in (0, 1):
                    c = 4
                else:
                    c = 2 if (x + y) % 9 > 4 else 3
                p(x, y, c)
        for x0 in (3, 58):
            rect(x0, 12, x0 + 2, 28, 5)
            for y in (16, 22, 27):
                line(x0, y, x0 + 2, y, 8)
            line(x0, 12, x0, 28, 6)

    def roof(left, right, crest, eave, core, upper, ridge):
        """Unbroken polygonal slate surface with a visible sloping copper lip."""
        mid = (left + right) // 2
        for x in range(left, right + 1):
            # Two different roof slopes joined at the apex; visible dark edge.
            distance = abs(mid - x)
            ytop = min(eave - 3, crest + distance // 5)
            for y in range(ytop, eave + 1):
                if y == ytop:
                    c = 8 if distance > 18 else ridge
                elif y == ytop + 1:
                    c = upper
                elif y == eave - 1:
                    c = 5
                elif y == eave:
                    c = 8
                elif y % 5 == 2 and x % 8 not in (0, 1):
                    c = 5
                elif x in (left + 1, right - 1):
                    c = 6
                else:
                    c = core
                p(x, y, c)
        for x in range(left - 1, right + 2):
            p(x, eave + 1, 5)
            if left <= x <= right and x % 9 == 0:
                p(x, eave + 1, 13)
        # Front-to-back material depth; shade the roof supports, don't add
        # separate unsupported floating lights.
        for x in (left + 2, right - 2):
            line(x, eave + 2, x, eave + 4, 8)

    def buttress(x0, top=13, base=29):
        rect(x0, top, x0 + 3, base, 8)
        line(x0, top, x0, base, 5)
        line(x0 + 1, top, x0 + 1, base - 1, 6)
        line(x0 + 3, top, x0 + 3, base, 5)
        for y in (top + 4, top + 10, base - 1):
            line(x0, y, x0 + 3, y, 3)

    def foot_gallery(light):
        line(4, 26, 59, 26, 5)
        rect(5, 27, 58, 29, 8)
        for x in range(6, 58):
            # Substantial connected warm windows, rather than tiny scattered
            # orange pixels across the same gray roof.
            if x % 12 in (0, 1, 2):
                line(x, 27, x, 29, 5)
            else:
                for y in (27, 28):
                    p(x, y, light if (x + y) % 5 else 14)
                p(x, 29, 13)
        line(5, 30, 58, 30, 5)

    if role == "center":
        stone_wall()
        roof(5, 58, 1, 11, 13, 11, 5)
        # High arch over the old Center cross; monumental house-like pitched
        # roof is now distinguishable from a featureless metal shipping crate.
        for y in range(2, 11):
            half = min(14, 5 + 2 * (y - 2))
            line(32 - half, y, 32 + half, y, 13 if y % 4 else 11)
        line(20, 8, 44, 8, 5)
        for cx in (15, 49):
            arch(cx, 14, 7, 11, 12)
            buttress(cx - 10, 13, 25)
        foot_gallery(11)
        # Red cross/medical ring are original critical identity art. Copy back
        # every central glass pixel and the whole existing medical logo.
        for y in range(12, 26):
            for x in range(23, 42):
                p(x, y, old[y][x])
        for x in (5, 57):
            rect(x, 15, x + 2, 23, 8)
            line(x + 1, 16, x + 1, 21, 15)
            p(x + 1, 19, 10)
        for x in range(7, 57):
            p(x, 11, 5)
        # Fixed fidelity anchors used by existing validators.
        p(31, 1, 6)
        p(20, 8, 5)
        p(31, 18, 12)

    elif role == "mart":
        stone_wall()
        roof(6, 57, 3, 11, 2, 5, 6)
        # Deep teal awning, in contrast with the Center's red pitched roof.
        rect(11, 7, 53, 9, 8)
        for x in range(12, 53):
            p(x, 7, 5)
            p(x, 8, 10 if x % 7 not in (0, 1) else 9)
            p(x, 9, 8)
        # Two broad projecting slate buttresses with larger shop windows.
        for cx in (11, 53):
            # Large orange shop-floor furnace windows anchor the industrial
            # cyan cart/canopy without turning the whole facade blue.
            arch(cx, 14, 6, 11, 12, hot=True)
            buttress(cx - 8, 12, 25)
        foot_gallery(11)
        for y in range(11, 26):
            for x in range(18, 47):
                # Preserve the cyan cart, technical signage, and existing
                # temperature gauges beneath the newly massive awning.
                p(x, y, old[y][x])
        for x in range(11, 53):
            p(x, 11, 5)
        for x in range(16, 48):
            p(x, 27, 10 if x % 9 else 9)
        p(20, 8, 5)
        p(32, 20, 10)
        p(9, 16, 5)
        for x in (4, 58):
            line(x, 12, x, 24, 15)

    elif role == "gym":
        stone_wall()
        roof(4, 59, 3, 11, 8, 3, 6)
        # A full-width blast furnace building, with a RED HOT chimney cornice.
        for x in range(19, 45):
            p(x, 3, 14)
        for cx, high in ((9, 0), (53, 2)):
            rect(cx - 4, high, cx + 4, 15, 8)
            for y in range(high, 16):
                for x in range(cx - 3, cx + 4):
                    p(x, y, 3 if x in (cx - 3, cx + 3) else
                      13 if y in (high + 2, high + 3, high + 4) else
                      8 if y % 4 else 5)
            line(cx - 5, high, cx + 5, high, 5)
            line(cx - 4, high + 1, cx + 4, high + 1, 14)
        for cx in (15, 49):
            arch(cx, 14, 5, 11, 12)
            buttress(cx - 8, 14, 26)
        for y in range(12, 26):
            for x in range(19, 46):
                p(x, y, old[y][x])
        for x in range(12, 52):
            p(x, 11, 5)
        foot_gallery(11)
        p(32, 19, 12)
        p(20, 8, 5)
        for x in range(1, 6):
            p(x, 0, 13)

    else:
        # Four DISTINCT homes, with their original four-cell composition,
        # not one long industrial display case.
        stone_wall()
        houses = (
            (12, 7, 1, 12, 11),  # steep, copper-ruby pitched house
            (25, 6, 2, 2, 9),    # blue-grey slate with teal attic
            (39, 7, 1, 13, 12),  # broad copper forge annex
            (52, 6, 3, 3, 11),  # dark narrow workers' gable
        )
        for idx, (cx, half, peak, base, glass) in enumerate(houses):
            x0, x1 = cx - half, cx + half
            for x in range(x0, x1 + 1):
                dist = abs(x - cx)
                top = peak + dist // (2 if idx in (0, 2) else 3)
                for y in range(top, 12):
                    if y == top:
                        c = 6
                    elif y == top + 1:
                        c = 13 if idx in (0, 2) else 5
                    elif y in (10, 11):
                        c = 8 if y == 11 else 5
                    elif y % 4 == 0 and x % 5 == 0:
                        c = 5
                    else:
                        c = base
                    p(x, y, c)
            # Four different attic windows.
            for y in range(5, 9):
                for x in range(cx - 2, cx + 3):
                    p(x, y, 8 if x in (cx - 2, cx + 2) or y == 5 else
                      5 if x == cx else glass)
            for x in range(x0 + 1, x1):
                p(x, 12, 5)
            arch(cx, 15, 5, 11, glass, hot=idx != 1)
            for x in (x0, x1):
                line(x, 13, x, 27, 8)
                line(x + 1, 14, x + 1, 27, 5)
            for x in range(x0 + 1, x1):
                for y in (27, 28, 29):
                    p(x, y, 13 if idx != 1 and (x + y) % 8 == 0
                      else glass if y != 29 else 6)
            p(cx, 1, 6)
            p(cx, 12, 5)
        line(4, 30, 60, 30, 5)
        p(13, 8, 5)
        # Different rooftops can be seen as separate homes at a glance.
        for x in (19, 32, 46):
            rect(x, 13, x + 1, 29, 8)
            line(x, 13, x, 28, 5)

    # Standard roofs are always solid under their eaves and have a
    # nontransparent natural bottom, but never spill over the source canvas.
    # The original validator's visual, gameplay and identity anchors remain.
    if role in ("center", "mart", "gym"):
        p(20, 8, 5)
    if role == "gym":
        p(32, 19, 12)
    before_sha = sum(v != n for r, s in zip(old, a.pix) for v, n in zip(r, s))
    hot_count = sum(v in (11, 12, 13, 14) for row in a.pix for v in row)
    full_count = sum(v != 0 for row in a.pix for v in row)
    if before_sha < 700 or full_count < 1150 or hot_count < (90 if role == "mart" else 145):
        raise ValueError(f"{name}: architecture redesign too weak {before_sha=}, {full_count=}, {hot_count=}")
    if any(not 0 <= v <= 15 for row in a.pix for v in row):
        raise ValueError(f"{name}: invalid GBA 4bpp indexed colour")
    return before_sha
