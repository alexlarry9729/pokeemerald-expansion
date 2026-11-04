#!/usr/bin/env python3
"""Non-repeating roof silhouettes for original Cuordilava buildings ONLY.

Final 64x32 indexed-art pass: sculpt a pitched basalt roof and deep overhang
within each ALREADY OCCUPIED architectural mural. Preserve center red cross,
market shopping cart/cyan canopy, Gym single flame/emblem and old chimney
identity pixels, and all four existing residential gable peaks. Never alters
the 20x20 map, original warps, NPCs, metatile/collision data or palettes.
"""


def reprofile_existing_roofs(a, name):
    if not any(k in name for k in
               ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")):
        return
    before = [row[:] for row in a.pix]
    locked = set()

    if "POKEMON_CENTER" in name:
        locked.update((x,11) for x in range(7,57))
        locked.update((x,y) for y in range(14,25) for x in range(24,41))
        locked.update(((31,1),(20,8),(31,18),(31,16),(10,16)))
    elif "POKE_MART" in name:
        locked.update((x,11) for x in range(11,53))
        locked.update((x,27) for x in range(16,48))
        locked.update((x,y) for y in range(15,25) for x in range(20,45))
        locked.update(((20,8),(32,20),(9,16)))
    elif "FLANNERY_GYM" in name:
        locked.update((x,11) for x in range(12,52))
        locked.update((x,0) for x in range(1,6))
        locked.update((x,3) for x in range(19,45))
        locked.update((x,y) for y in range(14,26) for x in range(19,46))
        locked.update(((20,8),(32,19)))
    else:
        locked.update((x,1) for x in (12,25,39,52))
        locked.update((x,12) for x in (12,25,39,52))
        locked.add((13,8))

    def pix(x,y,c):
        if 0 <= x < a.w and 0 <= y < a.h and (x,y) not in locked:
            a.pixel(x,y,c)

    def line(x0,x1,y,c):
        for x in range(x0,x1+1):
            pix(x,y,c)

    def vertical(x,y0,y1,c):
        for y in range(y0,y1+1):
            pix(x,y,c)

    def pitch(left,right,tip,eave,slope,slate_course,hot_trim):
        """Stepped roof plane with shaped eaves and offset slate joints."""
        center=(left+right)//2
        for x in range(left,right+1):
            top=min(eave-3,tip+abs(x-center)//slope)
            for y in range(top,eave):
                pix(x,y,8 if y % 3 else 1)
            pix(x,top,6 if x<center else 5)
            if top+1<eave:
                pix(x,top+1,3 if x<center else 2)
        for y in range(tip+3,eave-1,3):
            staggering=((y-tip)//3)%2*(slate_course//2)
            for x in range(left+3+staggering,right-3,slate_course):
                line(x,min(x+slate_course-3,right-2),y,5)
                line(x+1,min(x+slate_course-4,right-2),y+1,2)
        line(left,right,eave-1,5)
        line(left+1,right-1,eave,hot_trim)
        # Under eaves, a black shadow reveals roof projection above walls.
        line(left+2,right-2,eave+1,1)
        for x in range(left+4,right-4,9):
            pix(x,eave,14 if hot_trim==13 else 10)

    def side_bracket(x,y0,y1):
        vertical(x,y0,y1,5)
        vertical(x+1,y0+1,y1-1,6)
        vertical(x+2,y0+1,y1-1,13)
        for yy in range(y0+3,y1-2,5):
            pix(x,yy,11)
            pix(x+2,yy,14)

    def thermal_light(cx,top,width=5):
        left=cx-width//2
        for y in range(top,top+5):
            line(left,left+width-1,y,12)
        line(left,left+width-1,top,11)
        for y in (top+1,top+3):
            line(left+1,left+width-2,y,14)
        vertical(cx,top,top+4,5)
        line(left-1,left+width,top+5,6)

    if "POKEMON_CENTER" in name:
        # A high, central pitched roof with two inset copper side chambers.
        pitch(9,54,1,9,6,7,13)
        for x in (6,55):
            side_bracket(x,13,25)
        for cx in (15,49):
            thermal_light(cx,18,7)
            line(cx-6,cx+6,15,5)
            line(cx-5,cx+5,16,13)
        # Small recessed heat valves along outer wall, red center untouched.
        for cx in (11,53):
            for y in (25,27):
                line(cx-3,cx+3,y,5)
            line(cx-2,cx+2,28,12)
            pix(cx,28,14)

    elif "POKE_MART" in name:
        # The shop is deliberately shallow and wide, not another temple.
        pitch(13,50,4,10,8,6,9)
        for cx in (12,52):
            side_bracket(cx-3,13,23)
            thermal_light(cx,17,5)
        # A side coolant riser wraps behind the existing cyan storefront.
        for x in (5,57):
            vertical(x,10,24,5)
            vertical(x+1,12,23,9)
            for y in (13,20):
                pix(x+1,y,10)
        # Preserve the continuous cyan strip at y27 and shop cart icon.

    elif "FLANNERY_GYM" in name:
        # The shrine receives a steep peak and independent dual blast stacks.
        pitch(13,50,3,10,5,5,13)
        for x in (3,55):
            side_bracket(x,7,25)
            for y in (10,15,20):
                line(x+1,x+3,y,12)
                pix(x+2,y-1,14)
        for cx in (12,52):
            thermal_light(cx,19,5)
        line(9,18,28,5)
        line(46,57,28,5)
        line(10,17,29,13)
        line(47,56,29,13)
        # One central flame sign and upper gallery remain untouched.

    else:  # Existing housing, four roofs within the same 64x32 terrace.
        for i,cx in enumerate((12,25,39,52)):
            half_width=(6,5,6,5)[i]
            tip=(2,3,2,4)[i]
            pitch(cx-half_width,cx+half_width,tip,10,
                  (2,3,2,3)[i],(3,4,5,4)[i],
                  13 if i in (0,2) else 6)
            for side in (cx-half_width,cx+half_width-2):
                side_bracket(side,14,22)
            thermal_light(cx,17,5)
            line(cx-5,cx+5,24,5)
            line(cx-4,cx+4,25,13 if i%2 else 6)
            # Each household has a slightly different copper vent height.
            vertical(cx+4,15,17+i%3,13)
            pix(cx+4,17+i%3,14)
        line(3,60,29,5)

    changes=sum(x!=y for row,prev in zip(a.pix,before)
                for x,y in zip(row,prev))
    if changes < 80:
        raise ValueError(f"Roof silhouette modification unexpectedly small "
                         f"for {name}: {changes} pixels")
    if any(a.pix[y][x]!=before[y][x] for (x,y) in locked):
        raise ValueError("Protected original building signage was overwritten")
