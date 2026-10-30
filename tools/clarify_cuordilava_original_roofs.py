#!/usr/bin/env python3
"""Unify the pre-existing Cuordilava roofs into clear basalt/copper silhouettes.

This pass REPAINTS ONLY 4x2 roof mural pixels created by the existing
sculpt_cuordilava_city renderer. No new building, map cell, sprite,
atlas tile, palette, warp, encounter, collision or gameplay object is made.

The original four 16x16 roof columns stay exactly aligned to the GBA grid.
Protected historic icons and the still-navigable ground are never touched.
"""


def clarify_original_roof_massing(art, name):
    keys = ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")
    if not any(key in name for key in keys):
        return
    if (art.w, art.h) != (64, 32):
        raise ValueError(f"Unexpected Cuordilava roof dimensions: {name}")

    before = [r[:] for r in art.pix]
    locks = set()
    if "POKEMON_CENTER" in name:
        locks.update(((31, 1), (20, 8), (31, 16), (31, 18), (10, 16)))
        locks.update((x, 11) for x in range(7, 57))
        locks.update((x, y) for x in range(24, 41) for y in range(14, 25))
        role = "center"
    elif "POKE_MART" in name:
        locks.update(((20, 8), (32, 20), (9, 16)))
        locks.update((x, 11) for x in range(11, 53))
        locks.update((x, 27) for x in range(16, 48))
        locks.update((x, y) for x in range(20, 45) for y in range(15, 25))
        role = "market"
    elif "FLANNERY_GYM" in name:
        locks.update(((20, 8), (32, 19)))
        locks.update((x, 0) for x in range(1, 6))
        locks.update((x, 3) for x in range(19, 45))
        locks.update((x, 11) for x in range(12, 52))
        locks.update((x, y) for x in range(19, 46) for y in range(14, 26))
        role = "gym"
    else:
        locks.update((x, y) for x in (12, 25, 39, 52) for y in (1, 12))
        locks.update(((13, 8),))
        role = "housing"

    def dot(x, y, colour):
        if 0 <= x < art.w and 0 <= y < art.h and (x, y) not in locks:
            art.pixel(x, y, colour)

    def line(left, right, y, colour):
        for x in range(left, right + 1):
            dot(x, y, colour)

    def register_slate_roof(left, right, top, bottom, tint, cold=False):
        """A single connected pitched roof, not disjoint neon stippling."""
        middle = (left + right) // 2
        for x in range(left, right + 1):
            # Shallow pitched shoulder: roof rises toward the central ridge.
            shoulder = abs(x - middle)
            rise = shoulder // 12
            roof_top = min(bottom - 2, top + rise)
            for y in range(roof_top, bottom):
                # Broad graphite plane, offset courses and shaded underside.
                colour = 8 if (x // 7 + y // 3) % 3 else 2
                if y >= bottom - 2:
                    colour = 3 if (x + y) % 4 else 2
                dot(x, y, colour)
            dot(x, roof_top, 5)
            if roof_top + 1 < bottom:
                dot(x, roof_top + 1, 6)
        # Full-width copper or cool-metal gutter, interrupted only by emblem
        # locks defined above.
        line(left, right, bottom, 5)
        line(left + 1, right - 1, bottom + 1, tint)
        for y in range(top + 3, bottom - 2, 3):
            offset = ((y - top) // 3) % 2 * 4
            for x in range(left + 4 + offset, right - 5, 9):
                line(x, x + 5, y, 5)
                dot(x + 2, y + 1, 3)
        # Suspended short skylights have physical support rails instead of
        # unsupported pixels hovering above the roof plane.
        centers = (left + 9, right - 9)
        for i, cx in enumerate(centers):
            glazing_y = top + 3
            line(cx - 4, cx + 4, glazing_y, 5)
            line(cx - 3, cx + 3, glazing_y + 1, 6)
            line(cx - 2, cx + 2, glazing_y + 2, 9 if cold else 12)
            dot(cx, glazing_y + 2, 5)
            line(cx - 3, cx + 3, glazing_y + 3, 5)
            dot(cx - 2, glazing_y + 1, tint)
            if i == 1:
                dot(cx + 2, glazing_y + 1, 11 if cold else 14)
        # Re-seat the gutter after the glass treatment. On the taller Gym
        # roof, the lowest skylight row coincides with the structural y=9
        # plane; without this, it splits the 4-cell horizontal fascia.
        line(left, right, bottom, 5)

    if role == "center":
        # Clinic: long, warm ruby/copper hip over the existing medical cross.
        register_slate_roof(7, 56, 2, 9, 13)
        for left, right in ((9, 21), (43, 55)):
            line(left, right, 10, 5)
            line(left + 1, right - 1, 14, 13)
        # Keep the clinic's established 16px-wide medical insignia clear.
    elif role == "market":
        # Mart: recognizably lower, cooler commercial roof, same exact body.
        register_slate_roof(11, 52, 3, 9, 10, cold=True)
        for left, right in ((11, 24), (40, 53)):
            line(left, right, 10, 5)
            line(left + 1, right - 1, 13, 10)
        # Do not touch the central shopping panel or turquoise lower canopy.
    elif role == "gym":
        # Gym: one blast-furnace roof with separately retained gallery/chimney.
        register_slate_roof(12, 51, 4, 9, 13)
        for left, right in ((12, 18), (46, 52)):
            line(left, right, 10, 5)
            line(left + 1, right - 1, 13, 13)
        # Preserve original top copper gallery and singular magma emblem.
    else:
        # Four distinct, already-present house gables, with actual low-slope
        # slate planes instead of identical flat rectangle billboards.
        houses = ((12, 6, 3, 9, 13),
                  (25, 5, 4, 9, 6),
                  (39, 6, 3, 9, 13),
                  (52, 5, 4, 9, 6))
        for i, (cx, half, top, base, tint) in enumerate(houses):
            left, right = cx - half, cx + half
            register_slate_roof(left, right, top, base, tint, cold=(i == 1))
            line(left, right, 10, 5)
            line(left + 1, right - 1, 11, tint)
            line(left + 2, right - 2, 13, 6)
            # Dark shadow under each dormer; no extra house or doorway.
            line(left + 3, right - 3, 14, 8)

    altered = sum(old != new for row, original in zip(art.pix, before)
                  for old, new in zip(row, original))
    if altered < 100:
        raise ValueError(f"Cuordilava roof remains too flat: {name}: {altered} pixels")
    if any(art.pix[y][x] != before[y][x] for x, y in locks):
        raise ValueError(f"Protected Cuordilava emblem changed: {name}")
    if any(c not in range(16) for row in art.pix for c in row):
        raise ValueError(f"4bpp overflow in Cuordilava roof: {name}")
    # Check that the uninterrupted support rim crosses all four GBA columns.
    if role == "housing":
        if any(art.pix[10][x] != 5 for x in (11, 25, 39, 52)):
            raise ValueError("Housing roof support lost 16px registration")
    else:
        left, right = ((7, 56) if role == "center" else
                       (11, 52) if role == "market" else (12, 51))
        if any(art.pix[9][x] != 5 for x in range(left, right + 1)):
            raise ValueError("Civic roof structural lower fascia is split")
