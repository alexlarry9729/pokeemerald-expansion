#!/usr/bin/env python3
"""Deep basalt, inset glazing and connected copper piers for ORIGINAL Cuordilava houses.

A deterministic 4bpp final paint pass over the already-allocated 64x32 roof/
facade murals. Its geometry stays on existing 4x2 metatile footprints.
No new sprites, buildings, interactive signs, palettes, tiles, paths or warps.
The protected clinic cross, market cart/cyan awning, gym flame, and home gable
peaks are deliberately excluded before any pixel is changed.
"""


def articulate_original_volcanic_facades(art, name):
    roles = ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")
    if not any(r in name for r in roles):
        return
    if (art.w, art.h) != (64, 32):
        raise ValueError(f"Unexpected original Cuordilava mural footprint: {name}")
    before = [r[:] for r in art.pix]
    protected = set()
    if "POKEMON_CENTER" in name:
        role = "clinic"
        protected.update(((31, 1), (20, 8), (31, 16), (31, 18), (10, 16)))
        protected.update((x, 11) for x in range(7, 57))
        protected.update((x, y) for x in range(24, 41) for y in range(14, 25))
        wings = ((7, 22), (42, 57))
        glass, glow, metal = (12, 14, 13)
    elif "POKE_MART" in name:
        role = "market"
        protected.update(((20, 8), (32, 20), (9, 16)))
        protected.update((x, 11) for x in range(11, 53))
        protected.update((x, 27) for x in range(16, 48))
        protected.update((x, y) for x in range(20, 45) for y in range(15, 25))
        wings = ((7, 19), (45, 57))
        glass, glow, metal = (9, 10, 10)
    elif "FLANNERY_GYM" in name:
        role = "forge"
        protected.update(((20, 8), (32, 19)))
        protected.update((x, 0) for x in range(1, 6))
        protected.update((x, 3) for x in range(19, 45))
        protected.update((x, 11) for x in range(12, 52))
        protected.update((x, y) for x in range(19, 46) for y in range(14, 26))
        wings = ((6, 18), (46, 58))
        glass, glow, metal = (12, 14, 13)
    else:
        role = "housing"
        protected.update((x, y) for x in (12, 25, 39, 52) for y in (1, 12))
        protected.add((13, 8))
        wings = ((6, 18), (19, 31), (33, 45), (46, 58))
        glass, glow, metal = (12, 14, 13)

    def dot(x, y, c):
        if 0 <= x < 64 and 0 <= y < 32 and (x, y) not in protected:
            art.pixel(x, y, c)

    def horizontal(x0, x1, y, c):
        for x in range(x0, x1 + 1):
            dot(x, y, c)

    def vertical(x, y0, y1, c):
        for y in range(y0, y1 + 1):
            dot(x, y, c)

    def stone_course(left, right, top, bottom, shift):
        """Rough masonry courses: no isolated bright specks or flat gray slabs."""
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                c = 8 if (x // 5 + y // 3) % 3 else 2
                if y % 4 == 0:
                    c = 5
                elif (x + shift + (y // 4) * 3) % 9 == 0:
                    c = 6
                dot(x, y, c)
        # Full-width stone plinth reads as a structural beam across 16px joins.
        horizontal(left, right, bottom, 5)

    def recessed_window(left, right, upper, lower, cold=False):
        """A fully built-in kiln-glass panel with jambs and a proper sill."""
        if right - left < 4:
            return
        for x in range(left, right + 1):
            for y in range(upper, lower + 1):
                if x in (left, right) or y in (upper, lower):
                    color = 5
                elif x == (left + right) // 2 or y == upper + 2:
                    color = 6
                else:
                    color = (9 if (x + y) % 4 else 10) if cold else (
                        12 if (x + y) % 4 else 14)
                dot(x, y, color)
        horizontal(left - 1, right + 1, upper - 1, 8)
        horizontal(left - 1, right + 1, upper, 5)
        horizontal(left - 1, right + 1, lower + 1, 5)
        horizontal(left, right, lower + 2, 13 if not cold else 10)

    def pier(x, top, bottom, color):
        for y in range(top, bottom + 1):
            dot(x, y, 5)
            dot(x + 1, y, 6 if y % 4 else 8)
            if y in (top + 1, top + 5, bottom - 2):
                dot(x + 1, y, color)
        horizontal(x - 1, x + 2, top, 5)

    if role != "housing":
        for i, (left, right) in enumerate(wings):
            # A single masonry mass runs uninterrupted under each existing
            # shadowed roof, with the opening recessed into the stone.
            stone_course(left + 1, right - 1, 18, 26, shift=2 * i + (3 if role == "forge" else 0))
            pier(left, 16, 28, metal)
            pier(right - 1, 16, 28, metal)
            # Each landmark owns its own material language and proportions.
            if role == "clinic":
                l, r, upper, lower = left + 4, right - 4, 18, 23
            elif role == "market":
                l, r, upper, lower = left + 3, right - 3, 18, 23
            else:
                l, r, upper, lower = left + 3, right - 3, 19, 24
            recessed_window(l, r, upper, lower, cold=(role == "market"))
            # Real projecting eaves connect columns to their foundation,
            # which remains on exactly the existing metatile row.
            horizontal(left, right, 27, 5)
            horizontal(left + 2, right - 2, 28, 5)
            horizontal(left + 3, right - 3, 29, metal)
            for x in range(left + 4, right - 3, 6):
                dot(x, 29, glow if role != "market" else 9)
        # The unpainted center contains the original clinic, store or gym icon.
    else:
        # Unlike the civic facilities these are four *separate* old houses.
        # Distinct windows and masonry tints are built inside unchanged cells.
        for i, (left, right) in enumerate(wings):
            stone_course(left + 1, right - 1, 17, 26, shift=i * 2)
            pier(left, 16, 28, 13 if i % 2 == 0 else 6)
            pier(right - 1, 16, 28, 13 if i % 2 == 0 else 6)
            cold = (i == 1)
            width = (6, 5, 6, 5)[i]
            center = (left + right) // 2
            upper = (18, 19, 18, 19)[i]
            recessed_window(center - width // 2, center + width // 2,
                            upper, upper + 5, cold=cold)
            horizontal(left + 1, right - 1, 27, 5)
            horizontal(left + 2, right - 2, 28, 13 if i % 2 == 0 else 6)
            for x in (left + 3, right - 3):
                dot(x, 29, 11 if i in (0, 2) else 10)
            # Keep visible gap between individual dwellings.
            if i != 3:
                vertical(right, 17, 25, 8)

    # No municipality, graphic allocation or gameplay can change in this pass.
    changes = sum(a != b for old, new in zip(before, art.pix)
                  for a, b in zip(old, new))
    if changes < 100:
        raise ValueError(f"Cuordilava facade relief too weak: {name}: {changes}")
    if any(art.pix[y][x] != before[y][x] for x, y in protected):
        raise ValueError(f"Existing building sign/emblem overwritten: {name}")
    if any(c not in range(16) for row in art.pix for c in row):
        raise ValueError(f"Invalid 4bpp facade pixel: {name}")
    if role != "housing":
        for left, right in wings:
            if any(art.pix[27][x] != 5 for x in range(left, right + 1)
                   if (x, 27) not in protected):
                raise ValueError(f"Cuordilava facade eave lost alignment: {name}")
