#!/usr/bin/env python3
"""Make Cuordilava roofs unmistakably different from the rocky backdrop.

A palette-6 roof painted with the same gray indices as the cliffs/ground
appears fused to the terrain. Give the *existing* 64x32 private roof murals a
clear rear silhouette, large uninterrupted material planes and a thick eave.

The second pair of houses to the southeast is composed of H-flipped copies
of the south housing mural (stitch_cuordilava_south_housing_roof.py). This
pass acts on that SOURCE mural, so the reflected roofs are fixed too.

No map cells, warps, object events, metatiles, collision flags, transparent
pixels, roof chimneys, neon glass, medical emblem, Gym flame or palette
indices are reassigned. Run after add_building_depth and before atlas export.
"""

ROLES = {
    "POKEMON_CENTER_INDUSTRIAL_REACTOR": "clinic",
    "FLANNERY_GYM_MOLTEN_FORGE": "gym",
    "HOUSING_MAGMA_TERRACES": "housing",
}

# left, right, ridge center, top, pitch, main roof tone, high/edge tone
# 9/10 = mineral blue (clinic / two residential roofs), 11/13/14 = kiln
# copper, 8 = the actual charcoal rear silhouette, never pavement slate.
PROFILE = {
    "clinic": (
        (6, 23, 14, 2, 4, 9, 10),
        (40, 58, 50, 3, 4, 9, 10),
    ),
    "gym": (
        (7, 57, 32, 2, 6, 11, 14),
    ),
    "housing": (
        (6, 18, 12, 2, 3, 13, 14),
        (19, 32, 25, 3, 4, 9, 10),
        (33, 45, 39, 1, 3, 11, 12),
        (46, 59, 52, 3, 4, 9, 10),
    ),
}


def separate_roof_planes(art, name):
    role = ROLES.get(name)
    if role is None:
        return 0
    if (art.w, art.h) != (64, 32):
        raise ValueError("Rear roof repair needs the existing 64x32 mural")

    before = [row[:] for row in art.pix]
    protected = set()
    if role == "clinic":
        protected.update((x, 11) for x in range(7, 57))
        protected.update((x, y) for x in range(23, 42)
                         for y in range(13, 25))
        protected.update(((31, 1), (20, 8), (31, 18), (10, 16)))
    elif role == "gym":
        protected.update((x, 0) for x in range(1, 6))
        protected.update((x, 3) for x in range(19, 45))
        protected.update((x, 11) for x in range(12, 52))
        protected.update((x, y) for x in range(19, 46)
                         for y in range(13, 26))
        protected.update(((20, 8), (32, 19)))
    else:
        protected.update((x, 1) for x in (12, 25, 39, 52))
        protected.update((x, 12) for x in (12, 25, 39, 52))
        protected.add((13, 8))

    def roof_pixel(x, y, new):
        if not (0 <= x < 64 and 0 <= y <= 10):
            return
        if (x, y) in protected:
            return
        old = art.pix[y][x]
        # Keep transparency and heat / skylights / neon. The dark stone
        # pixels are the ONLY ones that can look like the rear pavement.
        if 1 <= old <= 8:
            art.pixel(x, y, new)

    coloured_area = []
    for group, (left, right, center, apex, pitch, face, highlight) in enumerate(
            PROFILE[role]):
        touched = 0
        for x in range(left, right + 1):
            ridge = min(8, apex + abs(x-center)//pitch)

            # Uniform dark edge separating the exposed rear roof plane
            # from the cliff/background. No tiled stone noise on this line.
            roof_pixel(x, ridge-1, 8)

            for y in range(ridge, 11):
                if y == ridge:
                    tone = highlight
                elif y == ridge + 1:
                    tone = 8                       # raised beveled lip
                elif y == 9:
                    tone = 8                       # thick overhanging eave
                elif y == 10:
                    tone = 5                       # front steel fascia
                elif (x-left)//6 % 4 == 3:
                    tone = 3                       # broad structural seam
                elif y == ridge + 2:
                    tone = face                    # contiguous colored slope
                elif (y-ridge)//3 % 2 == 0:
                    tone = face
                else:
                    tone = 5 if face == 9 else 13  # shadowed material face
                old = art.pix[y][x]
                if 1 <= old <= 8 and (x, y) not in protected:
                    if tone in (9, 10, 11, 12, 13, 14):
                        touched += 1
                    roof_pixel(x, y, tone)
        coloured_area.append(touched)

    # A single horizontal copper-blue roof-to-facade transition stops the
    # clinic feeling like several pieces glued onto the cliff. Preserve
    # its important original medical parapet on y11.
    if role == "clinic":
        for x in range(24, 41):
            for y in (9, 10):
                roof_pixel(x, y, 8 if y == 9 else 6)
        # The two wings stay separate from the raised central clinic tower.
        for x in (23, 41):
            for y in range(6, 10):
                roof_pixel(x, y, 8)

    # Gym is one massive orange-and-charcoal smelting hall, not an ash-gray
    # continuation of the paving. Chimney caps and copper y3 are protected.
    if role == "gym":
        for x in range(19, 46):
            roof_pixel(x, 10, 8 if x in (19, 45) else 5)

    # Both eastern houses inherit the corrected source via horizontal flips.
    # Separate party-wall shadows between the four authored house gables.
    if role == "housing":
        for x in (19, 33, 46):
            for y in range(5, 10):
                roof_pixel(x, y, 8)

    # Reproducible invariants, also protecting all luminous old pixels.
    for y in range(32):
        for x in range(64):
            old, new = before[y][x], art.pix[y][x]
            if (x, y) in protected and old != new:
                raise ValueError(f"{role}: landmark emblem moved {(x,y)}")
            if old == 0 and new != 0:
                raise ValueError(f"{role}: transparent border filled {(x,y)}")
            if old >= 9 and old != new:
                raise ValueError(f"{role}: roof pass erased luminous art {(x,y)}")
            if y >= 11 and old != new:
                raise ValueError(f"{role}: roof repair leaked into a facade {(x,y)}")
            if not 0 <= new <= 15:
                raise ValueError(f"{role}: roof colour is not 4bpp {(x,y)}")

    changed = sum(old != new for row0, row1 in zip(before, art.pix)
                  for old, new in zip(row0, row1))
    if changed < 75 or any(n < 4 for n in coloured_area):
        raise ValueError(
            f"{role}: roof still resembles the cliffs: changed={changed}, "
            f"roof faces={coloured_area}"
        )
    print(f"Cuordilava roof vs rock: {role}, {changed} pixels shaped, "
          f"roof material spans {coloured_area}; protected all original symbols")
    return changed
