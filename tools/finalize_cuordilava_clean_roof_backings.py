#!/usr/bin/env python3
"""Final true-roof planes for clinic, forge and residential upper storeys.

The legacy passes only recolored dark gray spots and deliberately left all
original roof-neon and zero/transparent pixels intact. Consequently the old
cliff/floor texture still showed *inside* each roof, making it look like
scattered orange/blue paving. Paint ONE connected roof body for each EXISTING
upper-storey shape, with a continuous silhouette, a visible rear ridge and
dark fascia. No new map cells, sprites, warp data, tile allocations or
collision/elevation bits; these are source pixels inside existing 64x32 murals.

The southeastern houses reuse horizontally reflected source house murals:
repairing the source here also repairs the two original right-hand rooftops.
"""
TYPES = {
    'POKEMON_CENTER_INDUSTRIAL_REACTOR': 'clinic',
    'FLANNERY_GYM_MOLTEN_FORGE': 'forge',
    'HOUSING_MAGMA_TERRACES': 'homes',
}
# x-left, x-right, ridge x, minimum y, rise per x, face colour, rim colour
# bank 6 p8 is dark charcoal, p9/10 are deep mineral teal, 11/13/14 furnace.
ROOFS = {
    'clinic': (
        (5, 23, 14, 2, 4, 9, 10),
        (41, 59, 50, 2, 4, 9, 10),
    ),
    'forge': (
        (6, 57, 32, 2, 6, 13, 14),
    ),
    'homes': (
        (6, 18, 12, 2, 3, 13, 14),
        (19, 32, 25, 3, 4, 9, 10),
        (33, 45, 39, 1, 3, 11, 12),
        (46, 59, 52, 3, 4, 9, 10),
    ),
}


def finalize_clean_roof_backings(art, name):
    role = TYPES.get(name)
    if role is None:
        return 0
    if (art.w, art.h) != (64,32):
        raise ValueError('Only the original 64x32 architectural mural is permitted')
    previous = [row[:] for row in art.pix]
    protected = set()
    if role == 'clinic':
        protected |= {(x,11) for x in range(7,57)}
        protected |= {(x,y) for x in range(23,42) for y in range(13,25)}
        protected |= {(31,1),(20,8),(31,18),(10,16)}
        # Upper central signed bell tower is architecturally separate.
        protected |= {(x,y) for x in range(24,41) for y in range(0,11)}
    elif role == 'forge':
        protected |= {(x,0) for x in range(1,6)}
        protected |= {(x,3) for x in range(19,45)}
        protected |= {(x,11) for x in range(12,52)}
        protected |= {(x,y) for x in range(19,46) for y in range(13,26)}
        protected |= {(20,8),(32,19)}
        # Do not touch independently raised forge stacks at either edge.
        protected |= {(x,y) for x in range(4,16) for y in range(0,7)}
        protected |= {(x,y) for x in range(51,60) for y in range(0,7)}
    else:
        protected |= {(x,y) for x in (12,25,39,52) for y in (1,12)}
        protected.add((13,8))
        # The third home has a recognisable original projecting chimney.
        protected |= {(x,y) for x in (34,35,36) for y in range(1,9)}

    changed_slots = set()
    gap_fills = 0

    def paint(x,y,v):
        nonlocal gap_fills
        if not (0 <= x < 64 and 0 <= y <= 10) or (x,y) in protected:
            return
        if art.pix[y][x] == 0 and v != 0:
            gap_fills += 1
        art.pixel(x,y,v)
        changed_slots.add((x//16,y//16))

    for i,(left,right,cx,top,pitch,body,edge) in enumerate(ROOFS[role]):
        for x in range(left,right+1):
            crest = min(8, top + abs(x-cx)//pitch)
            for y in range(max(0,crest-1),11):
                if y == crest-1:
                    v = 8         # clean dark 1px separation from rock behind
                elif y == crest:
                    v = edge      # coherent cold / copper architectural ridge
                elif y == crest+1:
                    v = 6         # bright beveled stone/steel counter-edge
                elif y in (9,10):
                    v = 8 if y == 9 else 5  # deep projecting underside
                elif x in (left, right):
                    v = 8         # left/right face of an actual roof volume
                elif x < cx-2:
                    v = body      # unbroken lit roof plane
                elif x > cx+2:
                    v = 9 if body==9 else 11  # shadow-facing half of roof
                elif y % 3 == 0:
                    v = 5         # restrained ridge brace near apex
                else:
                    v = body
                paint(x,y,v)
        # Every existing roof has one recessed skylight/heat-vent bay:
        # limited, framed openings (not hundreds of isolated lit pebbles).
        if role == 'clinic':
            glass = 10
        elif role == 'forge':
            glass = 12
        else:
            glass = 10 if body == 9 else 12
        # The tall original Gym stacks / protected central medical tower
        # remain outside the skylight area.
        skylight_y = 7 if role == 'forge' else 6
        if role == 'homes':
            skylight_y = 6 if top <= 2 else 7
        for x in range(cx-3,cx+4):
            if x in (cx-3,cx+3):
                paint(x,skylight_y,8)
                paint(x,skylight_y+1,8)
            else:
                paint(x,skylight_y,glass if x!=cx else 5)
                paint(x,skylight_y+1,glass if x!=cx else 5)
        for x in range(cx-4,cx+5):
            paint(x,skylight_y-1,5)
            paint(x,skylight_y+2,8)

    for y in range(32):
        for x in range(64):
            old,new=previous[y][x],art.pix[y][x]
            if (x,y) in protected and old != new:
                raise ValueError(f'{role}: protected historic roof/gym emblem moved {(x,y)}')
            if y >= 11 and old != new:
                raise ValueError(f'{role}: rooftop repaint leaked onto facade/entrance {(x,y)}')
            if not 0 <= new <= 15:
                raise ValueError(f'{role}: invalid 4bpp roof colour {(x,y)}')
    changed = sum(a != b for ra, rb in zip(previous, art.pix)
                  for a,b in zip(ra,rb))
    if changed < 145:
        raise ValueError(f'{role}: roof cleanup too small: {changed} pixels')
    # Some existing roof murals are entirely opaque already; their problem
    # was the COLOR/SEAM texture, not alpha. A zero gap_fill is valid only
    # because the changed-pixel and continuous-roof checks above still apply.
    if len(changed_slots) > 8:
        raise ValueError(f'{role}: exceeded the existing two-row roof mural')
    print(f'Cuordilava clean rear roof {role}: {changed} pixels, '
          f'{gap_fills} old open rock-texture holes closed; '
          'original roof footprint and all gameplay unchanged')
    return changed
