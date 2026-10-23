#!/usr/bin/env python3
"""Reference-led 3D roof massing for Cuordilava's already allocated civic murals.

Only repaints 4bpp pixels inside the 48 collision-preserving metatiles created
by sculpt_cuordilava_city.py. No extra map cells, warps, NPCs, water graphics,
palette banks or world-wide moonlight adjustments. Intended to be a visible
architectural pass (large structural forms), not scattered neon dots.
"""


def add_reference_massing(a, name):
    """Build stepped iron roofs, furnace stacks and shop canopies in 64px murals."""
    def line(x0, y0, x1, y1, color):
        a.line(x0, y0, x1, y1, color)

    def rect(x0, y0, x1, y1, color, fill=True):
        a.rect(x0, y0, x1, y1, color, fill)

    def pixel(x, y, color):
        a.pixel(x, y, color)

    if "POKEMON_CENTER" in name:
        # Reactor hall: broad three-tier roof behind the recognizable cross.
        # A solid charcoal mass carries copper cornices and recessed thermal vents.
        rect(21, 0, 42, 3, 8)
        rect(18, 3, 45, 6, 5)
        rect(16, 6, 47, 8, 8)
        for x0, x1, y in ((21, 42, 1), (18, 45, 4), (16, 47, 7)):
            line(x0, y, x1, y, 6)
            line(x0 + 2, y + 1, x1 - 2, y + 1, 11)
        for x in (23, 29, 35, 41):
            rect(x, 3, x + 2, 5, 8)
            line(x, 3, x + 2, 3, 14)
            pixel(x + 1, 4, 12)
        # Full-height heat risers frame rather than obscure the central emblem.
        for x in (12, 49):
            rect(x, 11, x + 3, 26, 8)
            line(x, 12, x, 25, 5)
            line(x + 2, 12, x + 2, 25, 13)
            line(x + 3, 12, x + 3, 25, 14)
            for y in (13, 18, 23):
                line(x, y, x + 3, y, 6)
                pixel(x + 1, y + 1, 11)
        # Under-roof suspended gangway; the red-cross region y=10..23 stays open.
        line(18, 27, 45, 27, 5)
        line(19, 28, 44, 28, 14)

    elif "MART" in name:
        # Different building language: low technical roof, not a second temple.
        rect(17, 1, 46, 4, 8)
        line(16, 2, 47, 2, 5)
        line(18, 5, 45, 5, 6)
        for x in range(19, 46, 6):
            rect(x, 2, x + 3, 4, 5)
            line(x + 1, 2, x + 1, 4, 9)
            pixel(x + 2, 4, 10)
        for x in (12, 49):
            rect(x, 5, x + 2, 25, 8)
            line(x, 6, x, 24, 6)
            line(x + 1, 6, x + 1, 24, 12)
            for y in (10, 16, 22):
                line(x, y, x + 2, y, 14)
        # A single connected 34px wide blue storefront canopy;
        # shop identity contrasts with the red-hot Gym and Center.
        rect(15, 25, 48, 30, 8)
        line(16, 26, 47, 26, 5)
        line(16, 27, 47, 27, 10)
        line(17, 28, 46, 28, 9)
        line(18, 29, 45, 29, 6)
        for x in range(19, 46, 6):
            pixel(x, 27, 9)
            pixel(x + 1, 28, 10)

    elif "FLANNERY_GYM" in name:
        # The town's tallest visual landmark: double exhaust spires connected
        # by a heavy stepped blast-furnace gallery ABOVE the fire medallion.
        rect(21, 0, 42, 2, 8)
        rect(19, 2, 44, 4, 5)
        rect(17, 4, 46, 7, 8)
        line(21, 1, 42, 1, 6)
        line(19, 3, 44, 3, 14)
        line(17, 6, 46, 6, 6)
        for x in range(22, 43, 5):
            rect(x, 4, x + 2, 5, 5)
            line(x + 1, 4, x + 1, 5, 12)
        for x in (0, 57):
            rect(x, 3, x + 6, 25, 8)
            rect(x + 1, 1, x + 5, 4, 5)
            line(x + 1, 0, x + 5, 0, 13)
            line(x + 2, 5, x + 2, 24, 6)
            line(x + 3, 5, x + 3, 24, 12)
            line(x + 4, 5, x + 4, 24, 14)
            for y in (7, 13, 19, 24):
                line(x, y, x + 6, y, 5)
            for y in (8, 14, 20):
                pixel(x + 3, y, 11)
        # Copper pipe under the crest, with a rim of furnace-orange rivets.
        line(11, 28, 52, 28, 13)
        line(13, 29, 50, 29, 5)
        for x in range(15, 50, 7):
            pixel(x, 28, 14)

    elif "HOUSING" in name:
        # Four connected steep, overlapping basalt gables; each peaked roof
        # has a hot upper vent above its own separate residential window bay.
        for cx in (12, 25, 39, 52):
            for step in range(7):
                left, right = cx - step, cx + step
                y = 1 + step
                pixel(left, y, 6)
                pixel(right, y, 6)
                for x in range(left + 1, right):
                    pixel(x, y, 8)
                if step >= 4:
                    pixel(cx, y, 13)
                    pixel(cx + 1, y, 11)
            line(cx - 7, 9, cx + 7, 9, 5)
            line(cx - 6, 10, cx + 6, 10, 14)
            for x in (cx - 5, cx + 5):
                line(x, 11, x, 24, 5)
                pixel(x, 17, 12)
            # Hollow chimney caps intentionally break the repeating roofline.
            for x in (cx - 7,):
                rect(x, 2, x + 2, 6, 8)
                line(x, 2, x + 2, 2, 13)
                pixel(x + 1, 3, 11)

    elif "PLAZA" in name:
        # Four diagonal copper-inlaid basalt approaches toward the existing
        # volcanic seal; never create apparent walls on the walkable court.
        for origin_x, direction in ((2, 1), (61, -1)):
            for k in range(9):
                x = origin_x + k * direction
                for y in (2 + k // 3, 29 - k // 3):
                    pixel(x, y, 5)
                    pixel(x, y + 1, 13 if k % 3 == 0 else 6)
        for x, y in ((5, 5), (58, 5), (5, 26), (58, 26)):
            rect(x, y, x + 1, y + 1, 8)
            pixel(x, y, 14)
            pixel(x + 1, y + 1, 11)

    elif "THERMAL_BASIN" in name:
        # Sparse arched wrought-iron railing with open negative space over water.
        for x in (8, 24, 40, 56):
            line(x - 4, 7, x - 2, 5, 5)
            line(x - 2, 5, x + 2, 5, 6)
            line(x + 2, 5, x + 4, 7, 5)
            pixel(x, 5, 14)

    # The Gym's independent ground-floor facade deliberately remains untouched:
    # its four incandescent windows are protected by the existing regression test.
