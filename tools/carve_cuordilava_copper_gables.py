#!/usr/bin/env python3
"""Final architectural relief for Cuordilava's four EXISTING rooftop murals.

All pixels fit the original 64x32 art panels. This pass changes neither the
20x20 town, collision, warp/event data, metatile count nor day/night palettes.
Roof ribs and copper gable infills deliberately form connected silhouettes;
storefronts, original Pokemon emblems and home peaks remain protected.
"""


def carve_existing_copper_gables(art, name):
    roles = ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")
    if not any(role in name for role in roles):
        return
    if (art.w, art.h) != (64, 32):
        raise ValueError(f"Unexpected Cuordilava roof art size: {name}")
    before = [row[:] for row in art.pix]
    locked = set()
    if "POKEMON_CENTER" in name:
        locked.update((x, 11) for x in range(7, 57))
        locked.update((x, y) for x in range(24, 41) for y in range(14, 25))
        locked.update(((20, 8), (31, 1), (31, 16), (31, 18)))
    elif "POKE_MART" in name:
        locked.update((x, 11) for x in range(11, 53))
        locked.update((x, 27) for x in range(16, 48))
        locked.update((x, y) for x in range(20, 45) for y in range(15, 25))
        locked.update(((20, 8), (32, 20)))
    elif "FLANNERY_GYM" in name:
        locked.update((x, 11) for x in range(12, 52))
        locked.update((x, 0) for x in range(1, 6))
        locked.update((x, 3) for x in range(19, 45))
        locked.update((x, y) for x in range(19, 46) for y in range(14, 26))
        locked.update(((20, 8), (32, 19)))
    else:
        locked.update((x, y) for x in (12, 25, 39, 52) for y in (1, 12))
        locked.add((13, 8))

    def dot(x, y, color):
        if 0 <= x < 64 and 0 <= y < 32 and (x, y) not in locked:
            art.pixel(x, y, color)

    def horizontal(left, right, y, color):
        for x in range(left, right + 1):
            dot(x, y, color)

    def gable(cx, half_width, apex, eave, edge, pane):
        """Contiguous pitched basalt volume, recessed glazing and copper eave."""
        left, right = cx - half_width, cx + half_width
        for x in range(left, right + 1):
            shoulder = abs(x - cx)
            top = apex + shoulder // 4
            if top >= eave:
                continue
            for y in range(top, eave):
                shade = 8 if y < eave - 2 else (2 if x % 3 else 3)
                dot(x, y, shade)
            dot(x, top, 6 if x <= cx else 5)
            if top + 1 < eave:
                dot(x, top + 1, 3)
        # The copper ridge is an actual uninterrupted supporting fascia.
        horizontal(left + 1, right - 1, eave, 5)
        horizontal(left + 2, right - 2, eave + 1, edge)
        # Recessed two-tone dormer in the basalt plane, never a plain neon dot.
        glazing_top = max(apex + 3, eave - 4)
        horizontal(cx - 3, cx + 3, glazing_top, 5)
        horizontal(cx - 2, cx + 2, glazing_top + 1, pane)
        horizontal(cx - 2, cx + 2, glazing_top + 2, 11 if pane != 10 else 9)
        dot(cx, glazing_top + 1, 5)
        horizontal(cx - 3, cx + 3, glazing_top + 3, 6)

    def eave_support(left, right, y, cool=False):
        # A real shadow line and bolted frame beneath the extended roof.
        horizontal(left, right, y, 8)
        horizontal(left + 1, right - 1, y + 1, 6)
        for x in range(left + 3, right - 2, 6):
            dot(x, y + 1, 13)
            dot(x, y + 2, 10 if cool else 11)

    if "POKEMON_CENTER" in name:
        # Twin tall thermal clerestories flank the preserved medical emblem.
        gable(15, 7, 2, 8, 13, 12)
        gable(49, 7, 2, 8, 13, 12)
        for a, b in ((8, 22), (42, 56)):
            eave_support(a, b, 12)
            horizontal(a + 2, b - 2, 16, 5)
            for x in range(a + 4, b - 2, 6):
                dot(x, 17, 13)
                dot(x + 1, 18, 14)
    elif "POKE_MART" in name:
        # Lower, cooler ventilation caps distinguish the marketplace.
        gable(18, 7, 3, 8, 10, 9)
        gable(46, 7, 3, 8, 10, 9)
        for a, b in ((11, 25), (39, 53)):
            eave_support(a, b, 12, cool=True)
            horizontal(a + 2, b - 2, 15, 5)
            horizontal(a + 3, b - 3, 16, 10)
            for x in range(a + 4, b - 3, 4):
                dot(x, 17, 9)
    elif "FLANNERY_GYM" in name:
        # Two shoulders of a forge temple, no second flame insignia.
        gable(14, 6, 2, 9, 13, 12)
        gable(50, 6, 2, 9, 13, 12)
        for a, b in ((8, 18), (46, 56)):
            eave_support(a, b, 12)
            horizontal(a + 1, b - 1, 16, 5)
            horizontal(a + 2, b - 2, 17, 13)
            for x in (a + 3, b - 3):
                dot(x, 18, 12)
                dot(x, 19, 14)
    else:
        # Each house gets its own gable pitch, dormer light and wooden sill.
        for i, cx in enumerate((12, 25, 39, 52)):
            gable(cx, (5, 4, 6, 5)[i], (2, 3, 2, 3)[i],
                  (9, 9, 10, 9)[i], (13, 6, 13, 6)[i],
                  (12, 11, 12, 11)[i])
            left, right = cx - 5, cx + 5
            eave_support(left, right, 13, cool=(i == 1))
            horizontal(left + 1, right - 1, 22, 5)
            horizontal(left + 2, right - 2, 23, 13 if i % 2 == 0 else 6)
            dot(cx - 3, 24, 11)
            dot(cx + 3, 24, 14 if i % 2 == 0 else 10)

    changed = sum(a != b for old, new in zip(before, art.pix)
                  for a, b in zip(old, new))
    if changed < 70:
        raise ValueError(f"Copper-gable relief too sparse: {name}: {changed} pixels")
    if any(art.pix[y][x] != before[y][x] for x, y in locked):
        raise ValueError(f"Cuordilava landmark identity was overwritten: {name}")
    if any(pixel < 0 or pixel > 15 for row in art.pix for pixel in row):
        raise ValueError(f"Cuordilava palette overflow in {name}")
