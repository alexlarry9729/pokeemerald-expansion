#!/usr/bin/env python3
"""Late-stage Cuordilava roof depth, preserving all previous landmark identities.

Use a restrained bas-relief treatment, not additional map geometry. Work in the
four existing 64x32 town-private mural graphics. Only indices 1..8 (unlit
basalt/steel) may be modified: all window glass, furnace heat, teal neon and
magenta signs (indices 9..15), plus protected landmarks, remain byte-identical.
Never write the exterior/transparent border or introduce map/event changes.
"""


def relief_existing_roof_massing(art, name):
    civic = (
        "POKEMON_CENTER" in name
        or "POKE_MART" in name
        or ("FLANNERY_GYM" in name and "FACADE" not in name)
    )
    housing = "HOUSING_MAGMA_TERRACES" in name
    if not (civic or housing):
        return 0
    if (art.w, art.h) != (64, 32):
        raise ValueError(f"{name}: expected original 64x32 roof mural")

    before = [row[:] for row in art.pix]
    protected = set()
    if "POKEMON_CENTER" in name:
        protected |= {(x, 11) for x in range(7, 57)}
        protected |= {(x, y) for y in range(12, 26) for x in range(23, 42)}
        protected |= {(31, 1), (20, 8)}
    elif "POKE_MART" in name:
        protected |= {(x, 11) for x in range(11, 53)}
        protected |= {(x, 27) for x in range(16, 48)}
        protected |= {(x, y) for y in range(12, 26) for x in range(19, 46)}
        protected |= {(20, 8), (32, 20)}
    elif "FLANNERY_GYM" in name:
        protected |= {(x, 3) for x in range(19, 45)}
        protected |= {(x, 11) for x in range(12, 52)}
        protected |= {(x, y) for y in range(12, 26) for x in range(19, 46)}
        protected |= {(x, 0) for x in range(1, 6)}
        protected |= {(20, 8), (32, 19)}
    else:
        protected |= {(x, 1) for x in (12, 25, 39, 52)}
        protected |= {(x, 12) for x in (12, 25, 39, 52)}
        protected |= {(13, 8)}

    def stone(x, y, colour):
        if not (2 <= x <= 61 and 2 <= y <= 29):
            return
        if (x, y) in protected:
            return
        # This preserves all existing furnace-glass and neon pixels without
        # needing any knowledge of earlier artist passes.
        if 1 <= art.pix[y][x] <= 8:
            art.pixel(x, y, colour)

    if civic:
        # Twin sloping basalt roofs on the original outer wings. Stepped
        # illumination follows each roof plane, instead of random rivets.
        # Their inner tips stop before the Center cross/Market cart/Gym flame.
        for left, right in ((8, 21), (43, 56)):
            middle = (left + right) // 2
            for x in range(left, right + 1):
                distance = abs(x - middle)
                ridge = 4 + (distance // 4)
                for y in range(ridge, 11):
                    if y == ridge:
                        colour = 6
                    elif y == ridge + 1:
                        colour = 5
                    elif y == 10:
                        colour = 8
                    elif (x + 2 * y) % 6 == 0:
                        colour = 3
                    else:
                        colour = 4 if x <= middle else 2
                    stone(x, y, colour)
                # One restrained shingle joint per four source pixels.
                if x % 4 == 0:
                    stone(x, 9, 5)
            # A deeper lateral overhang ends before the preserved y=11 fascia.
            for x in range(left - 1, right + 2):
                stone(x, 12, 8)
                if x % 5 in (1, 2):
                    stone(x, 13, 6)

        # Heavy shadowed original-side supports: larger vertical masses tie
        # the roof silhouette to the existing wall and break the floating look.
        for x0 in (4, 57):
            for y in range(15, 27):
                for dx, color in enumerate((8, 5, 6, 8)):
                    stone(x0 + dx, y, color)
                if y in (17, 23):
                    stone(x0 + 1, y, 7)
            for x in range(x0 - 1, x0 + 5):
                stone(x, 27, 5)
                stone(x, 28, 8)
    else:
        # Four occupied original homes; each receives a subtly different
        # oblique roof slope, not a repeated square neon rooftop motif.
        for index, cx in enumerate((12, 25, 39, 52)):
            half = (6, 5, 6, 5)[index]
            for x in range(cx - half, cx + half + 1):
                distance = abs(x - cx)
                start = 4 + distance // (2 if index % 2 else 3)
                for y in range(start, 11):
                    if y == start:
                        colour = 6
                    elif y == start + 1:
                        colour = 5
                    elif y == 10:
                        colour = 8
                    else:
                        colour = (2, 4, 3, 7)[index]
                    stone(x, y, colour)
                if (x + index) % 5 == 0:
                    stone(x, 9, 5)
            # The existing vertical eave pillars get a visible cast shadow,
            # leaving all furnace-lit windows and frontages untouched.
            for y in range(15, 25):
                for dx, color in ((-6, 8), (-5, 5), (5, 6), (6, 8)):
                    stone(cx + dx, y, color)
            for x in range(cx - half, cx + half + 1):
                stone(x, 25, 5 if index % 2 else 6)

    changed = sum(
        before[y][x] != art.pix[y][x]
        for y in range(32)
        for x in range(64)
    )
    if changed < 75:
        raise ValueError(f"{name}: roof depth pass unexpectedly ineffective ({changed} pixels)")
    for x, y in protected:
        if before[y][x] != art.pix[y][x]:
            raise ValueError(f"{name}: landmark identity overwritten at {x},{y}")
    for y in range(32):
        for x in range(64):
            if before[y][x] != art.pix[y][x]:
                if not (1 <= before[y][x] <= 8 and 1 <= art.pix[y][x] <= 8):
                    raise ValueError(f"{name}: luminous or transparent pixel changed at {x},{y}")
    return changed
