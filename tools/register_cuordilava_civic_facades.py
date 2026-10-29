#!/usr/bin/env python3
"""Register Cuordilava's three ORIGINAL civic rooftops to shared structural grids.

This final visual pass removes floating strips and one-pixel disconnected trim
inside the pre-existing 64x32 Poke Center / Mart / Gym murals. It changes
neither map size, entrances, events, tile allocation, collision, nor global
lighting. Protected emblem and chimney pixels are never repainted.
"""


def register_civic_roof_facades(art, name):
    roles=("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM")
    if not any(k in name for k in roles):
        return
    if (art.w,art.h)!=(64,32):
        raise ValueError("Only the original four-by-two civic roof murals may be registered")

    before=[row[:] for row in art.pix]
    protected=set()
    if "POKEMON_CENTER" in name:
        protected.update((x,11) for x in range(7,57))
        protected.update((x,y) for x in range(24,41) for y in range(14,25))
        protected.update(((20,8),(31,1),(31,16),(31,18),(10,16)))
        wing_ranges=((7,22),(42,57))
        trim=13
        glazing=(12,14,11)
    elif "POKE_MART" in name:
        protected.update((x,11) for x in range(11,53))
        protected.update((x,27) for x in range(16,48))
        protected.update((x,y) for x in range(20,45) for y in range(15,25))
        protected.update(((20,8),(32,20),(9,16)))
        wing_ranges=((7,19),(45,57))
        trim=10
        glazing=(9,10,9)
    else:
        protected.update((x,11) for x in range(12,52))
        protected.update((x,0) for x in range(1,6))
        protected.update((x,3) for x in range(19,45))
        protected.update((x,y) for x in range(19,46) for y in range(14,26))
        protected.update(((20,8),(32,19)))
        wing_ranges=((6,18),(46,58))
        trim=13
        glazing=(12,14,11)

    def p(x,y,c):
        if 0<=x<64 and 0<=y<32 and (x,y) not in protected:
            art.pixel(x,y,c)
    def h(a,b,y,c):
        for x in range(a,b+1):
            p(x,y,c)
    def v(x,a,b,c):
        for y in range(a,b+1):
            p(x,y,c)

    # Two continuous, roof-to-wall stone/copper girders across all four
    # 16px art quadrants. Preserve the original top medallion and y11 fascia.
    fascia = (7,56) if "POKEMON_CENTER" in name else (
        (11,52) if "POKE_MART" in name else (12,51))
    h(*fascia,12,5)
    h(fascia[0]+1,fascia[1]-1,13,6)
    for x in range(fascia[0]+4,fascia[1]-2,8):
        p(x,13,trim)
        p(x+1,13,11 if trim!=10 else 9)

    # Two true inhabited side wings, with a separate inset luminous wall,
    # lintel, copper plinth and weight-bearing corner. All fit original
    # already-painted pixels; no building body is shifted on the map.
    for index,(left,right) in enumerate(wing_ranges):
        h(left,right,15,5)
        h(left+1,right-1,16,6)
        h(left+2,right-2,17,trim)
        for xx in (left,left+1,right-1,right):
            v(xx,18,27,8 if xx in (left+1,right-1) else 5)
        inner_l,inner_r=left+4,right-4
        # A full glass rectangle behind iron mullions, not floating sparks.
        for y in range(19,25):
            h(inner_l,inner_r,y,glazing[(y-19)%3])
        for x in range(inner_l,inner_r+1,5):
            v(x,19,24,5)
            p(x+1,20,14 if trim==13 else 10)
        h(inner_l-1,inner_r+1,18,5)
        h(inner_l-1,inner_r+1,25,5)
        h(inner_l,inner_r,26,trim)
        # Grounded support is repeated at exactly the same y in both wings.
        h(left,right,28,5)
        h(left+1,right-1,29,6)
        for x in range(left+3,right-2,6):
            p(x,29,trim)
            p(x+1,29,11 if trim!=10 else 9)
        # Shadow under eaves, masonry at both 16-pixel cell joins.
        for x in (left+2,right-2):
            v(x,24,28,5)
            p(x+1,26,trim)
        # Individual identity is only in the glazing, not in alignment.
        if index==0:
            h(left+4,left+6,21,6)
        else:
            h(right-6,right-4,22,6)

    if "POKEMON_CENTER" in name:
        # Side wings must not join over the emblem: an uninterrupted
        # cast-iron base supports its original red-cross medallion.
        h(7,22,30,5)
        h(42,57,30,5)
    elif "POKE_MART" in name:
        # Cyan signage is aligned with, not replaced by, the existing 32px
        # shopping canopy at row 27.
        for x0,x1 in wing_ranges:
            h(x0+2,x1-2,30,5)
            h(x0+3,x1-3,31,10)
    else:
        h(6,18,30,5)
        h(46,58,30,5)

    if any(art.pix[y][x] != before[y][x] for x,y in protected):
        raise ValueError(f"Cuordilava emblem or civic sign overwritten: {name}")
    changed=sum(a!=b for old,new in zip(before,art.pix)
                for a,b in zip(old,new))
    if changed<110:
        raise ValueError(f"Civic structural registration had too little effect: {name}: {changed}")
    if any(not 0<=pixel<=15 for row in art.pix for pixel in row):
        raise ValueError("A registered civic pixel is not a legal 4bpp palette index")
    if any(art.pix[12][x]!=5 for x in range(fascia[0],fascia[1]+1)):
        raise ValueError("One continuous four-cell civic eave is visually fractured")
    for left,right in wing_ranges:
        if any(art.pix[28][x]!=5 for x in range(left,right+1)):
            raise ValueError("Left/right civic foundation band is misregistered")
