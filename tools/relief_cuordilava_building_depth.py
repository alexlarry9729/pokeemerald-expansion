#!/usr/bin/env python3
"""Give the four fixed Cuordilava 64x32 building murals actual visual depth.

The citywide basalt pavement already uses a deliberately quiet slate texture.
The missing depth is within the architecture itself: light hits roof ridges
and west-facing masonry, with separate under-eaves, recessed windows, deep
east walls and foundations casting a dark contact shadow.

Only the EXISTING roof/facade mural's 4bpp pixels are touched. No map,
metatiles, doorways, script triggers, palettes, walkability, or tile allocations
are changed. Run strictly AFTER carve_architecture.
"""

BUILDINGS = {
    "POKEMON_CENTER_INDUSTRIAL_REACTOR": "clinic",
    "POKE_MART_TECHNICAL_FACADE": "market",
    "FLANNERY_GYM_MOLTEN_FORGE": "foundry",
    "HOUSING_MAGMA_TERRACES": "houses",
}

def add_building_depth(art, name):
    role = BUILDINGS.get(name)
    if role is None:
        return 0
    if (art.w, art.h) != (64, 32):
        raise ValueError("Building depth requires original 4x2 GBA murals")
    before = [row[:] for row in art.pix]

    # The medical cross, shopping cart, Gym flame and structural eaves are
    # established landmark identity. Never paint over protected indices.
    protect = set()
    if role == "clinic":
        protect.update((x, 11) for x in range(7, 57))
        protect.update((x, y) for x in range(23, 42)
                       for y in range(13, 25))
        protect.update(((31, 1), (20, 8), (31, 18), (10, 16)))
        wings = ((5, 22, 14, 16, 4, 12),
                 (42, 59, 51, 16, 4, 12))
        roofs = ((6, 22, 14, 1, 4), (42, 58, 50, 2, 4))
        footing = ((5, 21), (23, 41), (43, 59))
    elif role == "market":
        protect.update((x, 11) for x in range(11, 53))
        protect.update((x, 27) for x in range(16, 48))
        protect.update((x, y) for x in range(20, 45)
                       for y in range(14, 26))
        protect.update(((20, 8), (32, 20), (9, 16)))
        wings = ((6, 19, 13, 15, 4, 10),
                 (45, 58, 51, 15, 4, 10))
        roofs = ((6, 20, 13, 2, 5), (44, 58, 51, 3, 5))
        footing = ((6, 19), (20, 44), (45, 58))
    elif role == "foundry":
        protect.update((x, 0) for x in range(1, 6))
        protect.update((x, 3) for x in range(19, 45))
        protect.update((x, 11) for x in range(12, 52))
        protect.update((x, y) for x in range(19, 46)
                       for y in range(13, 26))
        protect.update(((20, 8), (32, 19)))
        wings = ((5, 18, 12, 15, 4, 12),
                 (47, 59, 52, 15, 4, 12))
        roofs = ((6, 18, 11, 3, 5), (47, 59, 53, 4, 5))
        footing = ((5, 18), (19, 45), (47, 59))
    else:
        protect.update((x, 1) for x in (12, 25, 39, 52))
        protect.update((x, 12) for x in (12, 25, 39, 52))
        protect.add((13, 8))
        wings = ((6, 18, 12, 17, 3, 12),
                 (19, 32, 25, 16, 3, 9),
                 (33, 45, 39, 17, 3, 14),
                 (46, 59, 52, 17, 3, 10))
        roofs = ((6, 18, 12, 1, 3),
                 (19, 32, 25, 3, 5),
                 (33, 45, 39, 0, 3),
                 (46, 59, 52, 2, 5))
        footing = ((6, 18), (19, 32), (33, 45), (46, 59))

    def pixel(x, y, colour):
        if 0 <= x < 64 and 0 <= y < 32 and (x, y) not in protect:
            art.pixel(x, y, colour)

    def hline(left, right, y, c):
        for x in range(left, right + 1):
            pixel(x, y, c)

    def vline(x, top, bottom, c):
        for y in range(top, bottom + 1):
            pixel(x, y, c)

    # First plane: angled roof. The existing silhouettes stay, but the
    # north-west lip catches cool mineral daylight while the eastern
    # roof falls away through two darker, recessed slate grades.
    for left, right, cx, peak, pitch in roofs:
        for x in range(left+1, right):
            y = min(9, peak + abs(x-cx) // pitch)
            if y <= 8:
                pixel(x, y, 7 if x <= cx else 6)
                if y + 1 <= 9:
                    pixel(x, y+1, 5 if x <= cx else 3)
        for x in range(left+2, right-1):
            if x % 5 == 0 and (x, 8) not in protect:
                pixel(x, 8, 2)     # widely spaced raised roof seam
        # Real REAR roof silhouette: a continuous charcoal cap immediately
        # behind the sloping ridge. Previously those source pixels fell
        # through to the old stock roof/cliff, visually welding the two
        # unrelated depths together. Protect furnace glass and all emblems;
        # the next pixel row is the already-bright structural roof lip.
        for x in range(left+1, right):
            ridge = min(9, peak + abs(x-cx)//pitch)
            behind = ridge-1
            if 0 <= behind < 9 and art.pix[behind][x] < 9:
                pixel(x, behind, 8)

    # Second plane: strongly projecting eave has three distinct layers.
    # y=11 is deliberately protected for the three iconic civic buildings.
    # The dark 12px underside is the vertical gap between roof and wall.
    # On housing, the four narrow separate eaves keep four clear silhouettes.
    for left, right in footing:
        hline(left+1, right-1, 10, 6)
        hline(left, right, 12, 8)
        hline(left+1, right-1, 13, 2)
        pixel(left, 12, 7)
        pixel(right, 12, 1)

    # Third plane: substantial front walls, each with a directional
    # highlight on the LEFT and a shaded side face on the RIGHT.
    # Do not paint across glass; these accents live outside the openings.
    for left, right, cx, top, half, glass in wings:
        window_left, window_right = cx-half-2, cx+half+2
        for y in range(15, 28):
            for x in range(left+3, right-2):
                if window_left-1 <= x <= window_right+1:
                    continue
                old = art.pix[y][x]
                if old in (2, 3, 4, 5):
                    pixel(x, y, 5 if x < cx else 4)
        # Thick west buttress and dark right return create sidewall volume.
        vline(left, 15, 28, 7)
        vline(left+1, 16, 27, 5)
        vline(right-1, 15, 28, 2)
        vline(right, 15, 29, 1)
        # Light on projecting west lintel; offset shadow below each window.
        hline(window_left, window_right, top-2, 1)
        hline(window_left+1, window_right-1, top-1, 7)
        vline(window_left, top, top+9, 8)
        vline(window_right, top, top+9, 2)
        hline(window_left, window_right, top+10, 5)
        hline(window_left+1, window_right-1, top+11,
              13 if glass in (12, 14) else 6)

    # Fourth plane: long two-tone basalt foundation. The deepest last row
    # reads as a CONTACT SHADOW against the already-existing paved street,
    # rather than a repeated stone line in the pavement itself.
    for i, (left, right) in enumerate(footing):
        hline(left+1, right-1, 29, 6 if i % 2 == 0 else 5)
        hline(left, right, 30, 8)
        hline(left+1, right-1, 31, 1)
        for x in (left, right):
            pixel(x, 30, 2)
            pixel(x, 31, 8)
        # Separated foundation courses add weight without neon outlines.
        for x in range(left+4, right-3, 7):
            pixel(x, 29, 7)

    # Architectural-specific silhouettes: not four interchangeable boxes.
    if role == "clinic":
        # Emergency cantilever under the cross, with a clean horizontal
        # hospital identity and a strong lower shadow behind the stone ledge.
        hline(23, 41, 25, 6)
        hline(24, 40, 26, 8)
        hline(27, 37, 27, 2)
        for x in (7, 57):
            vline(x, 15, 26, 7)
            vline(x+1, 16, 26, 5)
    elif role == "market":
        # Horizontal warehouse canopy projecting across the storefront.
        # Keep its original cyan strip on y27 intact.
        hline(19, 45, 12, 6)
        hline(20, 44, 13, 8)
        hline(20, 44, 26, 8)
        for x in (8, 56):
            vline(x, 15, 25, 6)
    elif role == "foundry":
        # Massive kiln shoulder and visibly darker thermal flue returns.
        hline(20, 44, 12, 8)
        hline(21, 43, 13, 1)
        for x in (7, 57):
            vline(x, 15, 27, 7)
            vline(x+2, 17, 27, 1)
    else:
        # Individual shadowed party walls stop the terrace reading as one
        # uninterrupted glass conveyor: no new doors or blocking objects.
        for x in (19, 33, 46):
            vline(x, 14, 28, 1)
            vline(x+1, 15, 28, 5)
        for left, right in footing:
            hline(left+2, right-2, 14, 6)

    # Recessed interior glow is the COUNTERPOINT to dark load-bearing stone.
    # Early depth drafts blanked too many lit glazing pixels with dark eaves.
    # Restore believable ground-floor glass behind thick structural mullions,
    # instead of weakening the exterior contact shadows.
    if role == "clinic":
        for left, right in ((8, 21), (43, 56)):
            hline(left, right, 25, 5)
            hline(left+2, right-2, 25, 13)  # emergency bay backlight
            for y in (26, 27, 28):
                for x in range(left, right + 1):
                    if x in (left, right, (left+right)//2):
                        colour = 8  # structural glass divider, behind facade
                    else:
                        colour = 12 if (x+2*y)%5 else 13
                    pixel(x, y, colour)
            hline(left, right, 29, 6)
    elif role == "houses":
        # Warm inhabited first-floor glazing, separated by four shadowed
        # door-height plinths; the 30/31px contact-shadow line stays intact.
        for cx in (12, 25, 39, 52):
            for x in range(cx-3, cx+4):
                pixel(x, 28, 12 if x != cx else 8)
                if x not in (cx-3, cx, cx+3):
                    pixel(x, 29, 13)

    # A regression here means that volumetric relief hid the actual windows.
    if role in ("clinic", "houses"):
        floor_start, floor_end, threshold = (
            (25, 31, 100) if role == "clinic" else (12, 30, 85)
        )
        warm = sum(c in (11, 12, 13, 14)
                   for row in art.pix[floor_start:floor_end] for c in row)
        if warm < threshold:
            raise ValueError(
                f"{role}: eave shadows swallowed occupied glazing: {warm}"
            )

    if any(art.pix[y][x] != before[y][x] for x, y in protect):
        raise ValueError(f"{role}: roof emblem or architectural anchor was lost")
    if any(not 0 <= colour < 16 for row in art.pix for colour in row):
        raise ValueError("Building relief exceeded 4-bit indexed graphics")
    changed = sum(a != b for old, new in zip(before, art.pix)
                  for a, b in zip(old, new))
    if changed < 160:
        raise ValueError(f"{role}: facade still too flat ({changed} changed pixels)")
    print(f"Cuordilava relief depth: {role}, {changed} pixels; "
          "pitched roof highlights, deep eaves, recessed glazing, "
          "side-face shading and contact-shadow foundation")
    return changed
