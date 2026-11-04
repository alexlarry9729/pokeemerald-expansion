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

    # Reference matching: broad hot windows and vertical violet signage,
    # drawn on the ALREADY occupied wall/roof cells. This replaces isolated
    # speckles with recognizable whole luminous surfaces, not new buildings.
    def glass_bay(left, top, width, height, cold=False):
        """Framed furnace glazing with real shadow, mullion and copper sill."""
        for y in range(top - 1, top + height + 1):
            for x in range(left - 1, left + width + 1):
                border = x in (left - 1, left + width) or y in (top - 1, top + height)
                if border:
                    dot(x, y, 5 if y != top + height else 13)
                elif x == left + width // 2 or y == top + 1:
                    dot(x, y, 6)
                else:
                    dot(x, y, (9 if (x + y) % 3 else 10) if cold
                        else (12 if (x + y) % 3 else 14))
        horizontal(left, left + width - 1, top + height + 1, 6)

    def suspended_neon(x, top, height, violet=True):
        """A dark-backed vertical sign: bright core, glass border, foot bracket."""
        for y in range(top, top + height):
            for xx in range(x, x + 5):
                edge = xx in (x, x + 4) or y in (top, top + height - 1)
                dot(xx, y, 5 if edge else 8)
        for y in range(top + 2, top + height - 2):
            dot(x + 1, y, 13 if y % 4 == 0 else 15 if violet else 10)
            dot(x + 2, y, 15 if violet else 9)
            dot(x + 3, y, 15 if y % 3 else 11)
        horizontal(x + 1, x + 3, top + 1, 14)
        horizontal(x + 1, x + 3, top + height - 2, 13)

    if "POKEMON_CENTER" in name:
        for left in (10, 46):
            glass_bay(left, 18, 7, 5)
        suspended_neon(2, 14, 11)
        suspended_neon(57, 14, 11)
        for a0, b0 in ((9, 21), (43, 55)):
            horizontal(a0, b0, 27, 5)
            horizontal(a0 + 1, b0 - 1, 28, 13)
    elif "POKE_MART" in name:
        for left in (10, 47):
            glass_bay(left, 17, 6, 5, cold=True)
        suspended_neon(3, 13, 11)
        suspended_neon(57, 13, 11, violet=False)
        # Keep the intact 32px-wide cyan canopy and storefront symbol.
        for a0, b0 in ((10, 18), (46, 54)):
            horizontal(a0, b0, 24, 5)
            horizontal(a0 + 1, b0 - 1, 25, 10)
    elif "FLANNERY_GYM" in name:
        for left in (9, 49):
            glass_bay(left, 17, 6, 6)
        suspended_neon(2, 14, 12)
        suspended_neon(57, 14, 12)
        # Orange forge pilot lights are mounted on continuous basalt plinths.
        for a0, b0 in ((8, 18), (46, 56)):
            horizontal(a0, b0, 28, 5)
            horizontal(a0 + 1, b0 - 1, 29, 13)
    else:
        # Four different lived-in facades with clear dark gaps between units.
        for i, cx in enumerate((12, 25, 39, 52)):
            glass_bay(cx - 3, 17 + (i % 2), 6, 5, cold=(i == 1))
            for y in range(15, 26):
                dot(cx - 7, y, 5)
                dot(cx + 6, y, 8)
            horizontal(cx - 5, cx + 5, 27, 5)
            horizontal(cx - 4, cx + 4, 28, 13 if i % 2 == 0 else 6)
            # Low, legible magenta illuminated house number.
            for y in range(17, 22):
                dot(cx + 5, y, 15 if i in (1, 3) else 11)
        # Hard vertical separation between the existing dwellings, no new ones.
        for x in (18, 32, 45):
            for y in range(17, 26):
                dot(x, y, 1)
            for y in (18, 22, 25):
                dot(x + 1, y, 13)

    changed = sum(a != b for old, new in zip(before, art.pix)
                  for a, b in zip(old, new))
    if changed < 70:
        raise ValueError(f"Copper-gable relief too sparse: {name}: {changed} pixels")
    if any(art.pix[y][x] != before[y][x] for x, y in locked):
        raise ValueError(f"Cuordilava landmark identity was overwritten: {name}")
    if any(pixel < 0 or pixel > 15 for row in art.pix for pixel in row):
        raise ValueError(f"Cuordilava palette overflow in {name}")
