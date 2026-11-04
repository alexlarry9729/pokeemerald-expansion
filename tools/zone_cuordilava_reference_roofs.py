#!/usr/bin/env python3
"""Reference-led colour zoning inside Cuordilava's EXISTING 64x32 buildings.

The medical roof uses warm copper/ruby lighting; the market roof gets a coherent
cyan canopy, the Gym a furnace crown, and the homes distinct slate dormers.
This is the last purely decorative *mural* pass. It allocates no maps, sprites,
metatiles or tiles and cannot alter warps, collision or the 20x20 footprint.
"""


def zone_reference_roofs(art, name):
    if not any(part in name for part in
               ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")):
        return
    if (art.w, art.h) != (64, 32):
        raise ValueError("Unexpected dimensions of original Cuordilava roof mural")
    before = [row[:] for row in art.pix]
    locked = set()
    if "POKEMON_CENTER" in name:
        locked.update((x, 11) for x in range(7, 57))
        locked.update((x, y) for x in range(24, 41) for y in range(14, 25))
        locked.update(((31,1), (20,8), (31,16), (31,18), (10,16)))
    elif "POKE_MART" in name:
        locked.update((x, 11) for x in range(11, 53))
        locked.update((x, 27) for x in range(16, 48))
        locked.update((x, y) for x in range(20, 45) for y in range(15, 25))
        locked.update(((20, 8), (32, 20), (9, 16)))
    elif "FLANNERY_GYM" in name:
        locked.update((x, 11) for x in range(12, 52))
        locked.update((x, 0) for x in range(1, 6))
        locked.update((x, 3) for x in range(19, 45))
        locked.update((x, y) for x in range(19, 46) for y in range(14, 26))
        locked.update(((20,8), (32,19)))
    else:
        locked.update((x, y) for x in (12,25,39,52) for y in (1,12))
        locked.update(((13,8),))
    def p(x,y,c):
        if 0 <= x < 64 and 0 <= y < 32 and (x,y) not in locked:
            art.pixel(x,y,c)
    def h(x0,x1,y,c):
        for x in range(x0,x1+1):p(x,y,c)
    def v(x,y0,y1,c):
        for y in range(y0,y1+1):p(x,y,c)
    def roof_glass(x0,x1,y,colour):
        # Continuous metal bounding rails and a translucent strip below.
        h(x0,x1,y,5)
        h(x0+1,x1-1,y+1,6)
        h(x0+2,x1-2,y+2,colour)
        for x in range(x0+4,x1-3,6):
            p(x,y+2,8)
            p(x+1,y+2,3)
        h(x0+1,x1-1,y+3,5)
    if "POKEMON_CENTER" in name:
        # Warm, distinctive curved medical crown over the already-present
        # cross medallion. The broad warm roof evokes the reference's red cap.
        for left,right,top in ((24,40,3),(26,38,4),(28,36,5)):
            h(left,right,top,5)
            h(left+1,right-1,top+1,13)
        h(26,38,7,12)
        for left,right in ((9,21),(43,55)):
            roof_glass(left,right,4,12)
            h(left+2,right-2,9,13)
            h(left+3,right-3,10,5)
            for x in range(left+3,right-2,4):
                p(x,8,14)
        for x in (7,56):
            v(x,14,22,5)
            v(x+1,15,21,13)
            for y in (17,20):p(x+2,y,14)
        # Horizontal roof/facade shadows prevent neon from looking pasted on.
        for x0,x1 in ((9,21),(43,55)):
            h(x0,x1,25,5)
            h(x0+1,x1-1,26,13)
    elif "POKE_MART" in name:
        # Physically coherent blue technical cap and two cold-store wings.
        # The original shopping-cart crest and continuous lower canopy stay.
        roof_glass(14,50,4,9)
        h(16,48,8,10)
        for x0,x1 in ((12,25),(39,52)):
            h(x0,x1,9,5)
            h(x0+1,x1-1,10,10)
        for x in (10,52):
            v(x,15,22,5)
            v(x+1,16,21,9)
            for y in (17,20):p(x+2,y,10)
        for x0,x1 in ((8,18),(46,56)):
            h(x0,x1,24,5)
            h(x0+1,x1-1,25,9)
    elif "FLANNERY_GYM" in name:
        # The existing flame crest stays singular; only its upper kiln roof
        # receives a layered molten-orange ridge and industrial bracing.
        for left,right,y,col in ((20,44,5,5),(22,42,6,13),
                                 (24,40,7,12),(26,38,8,14)):
            h(left,right,y,col)
        for x0,x1 in ((9,18),(46,55)):
            roof_glass(x0,x1,4,12)
            h(x0+1,x1-1,10,13)
        for x in (6,57):
            v(x,12,25,5)
            v(x+1,13,24,13)
            for y in (15,20,24):p(x+2,y,14)
        for x0,x1 in ((9,17),(47,55)):
            h(x0,x1,27,5)
            h(x0+1,x1-1,28,13)
    else:
        # Four existing houses: unequal attic rooflights and disconnected
        # architectural masses, avoiding the former uniform glowing strip.
        for i,cx in enumerate((12,25,39,52)):
            widths=(5,4,5,4)
            x0,x1=cx-widths[i],cx+widths[i]
            top=(3,4,3,4)[i]
            for y in range(top,9):
                inset=min(3,(9-y)//2)
                h(x0+inset,x1-inset,y,8 if y%3 else 2)
            h(x0+2,x1-2,top,5)
            h(x0+3,x1-3,top+1,13 if i in (0,2) else 6)
            h(cx-2,cx+2,top+2,12 if i==0 else 9 if i==1 else 11 if i==2 else 13)
            p(cx,top+2,5)
            h(x0,x1,10,5)
            h(x0+1,x1-1,11,13 if i%2==0 else 6)
            for x in (cx-5,cx+4):
                v(x,16,22,5)
                p(x+1,19,13 if i%2==0 else 10)
            h(cx-5,cx+5,25,5)
            h(cx-4,cx+4,26,13 if i%2==0 else 6)
    changed=sum(a!=b for old,new in zip(before,art.pix)
                for a,b in zip(old,new))
    if changed<65:
        raise ValueError(f"Reference roof zoning too sparse: {name}: {changed}")
    if any(art.pix[y][x]!=before[y][x] for x,y in locked):
        raise ValueError(f"Reference roof repaint touched protected pixels: {name}")
    if any(c < 0 or c > 15 for row in art.pix for c in row):
        raise ValueError("Town-private 4bpp colour out of range")
