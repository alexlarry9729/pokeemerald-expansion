#!/usr/bin/env python3
"""Connected copper/obsidian detailing on Cuordilava's existing roof silhouettes.

Pixel-only late mural stage; keeps the same four original 64x32 murals,
their center/market/gym emblems, all map/event records and original 20x20 map.
This deliberately adds architectural masses rather than random bright pixels.
"""
def accent_existing_roof_geometry(a, name):
    if not any(k in name for k in ("POKEMON_CENTER","POKE_MART","FLANNERY_GYM","HOUSING")):
        return
    old=[row[:] for row in a.pix]
    preserve=set()
    if "POKEMON_CENTER" in name:
        preserve|={(x,11) for x in range(7,57)}
        preserve|={(x,y) for y in range(14,25) for x in range(24,41)}
        preserve|={(20,8),(31,1),(31,16),(31,18)}
    elif "POKE_MART" in name:
        preserve|={(x,11) for x in range(11,53)}
        preserve|={(x,27) for x in range(16,48)}
        preserve|={(x,y) for y in range(15,25) for x in range(20,45)}
        preserve|={(20,8),(32,20)}
    elif "FLANNERY_GYM" in name:
        preserve|={(x,11) for x in range(12,52)}
        preserve|={(x,0) for x in range(1,6)}
        preserve|={(x,3) for x in range(19,45)}
        preserve|={(x,y) for y in range(14,26) for x in range(19,46)}
        preserve|={(20,8),(32,19)}
    else:
        preserve|={(x,1) for x in (12,25,39,52)}
        preserve|={(x,12) for x in (12,25,39,52)}
        preserve.add((13,8))
    def dot(x,y,c):
        if 0<=x<a.w and 0<=y<a.h and (x,y) not in preserve:
            a.pixel(x,y,c)
    def horiz(x0,x1,y,c):
        for x in range(x0,x1+1):dot(x,y,c)
    def post(x,top,bottom):
        for y in range(top,bottom+1):
            dot(x,y,5);dot(x+1,y,6);dot(x+2,y,13)
        for y in range(top+2,bottom,4):dot(x+1,y,14)
    def recess(x0,x1,top,bottom):
        for y in range(top,bottom+1):
            for x in range(x0,x1+1):dot(x,y,8)
        horiz(x0+1,x1-1,top,6)
        horiz(x0+2,x1-2,top+1,13)
        for x in range(x0+2,x1-1,4):
            dot(x,top+2,11)
    if "POKEMON_CENTER" in name:
        # Black stepped attic over both connected medical/thermal wings.
        for left,right in ((9,22),(42,55)):
            recess(left,right,5,8)
            horiz(left+1,right-1,9,5)
            horiz(left+2,right-2,10,13)
        for x in (6,55):post(x,13,26)
        for x in (13,49):
            horiz(x-4,x+4,25,5)
            horiz(x-3,x+3,26,13)
    elif "POKE_MART" in name:
        # Shop gets wide shallow vent galleries, with small cool filaments.
        for left,right in ((12,26),(38,52)):
            recess(left,right,5,8)
            for x in range(left+2,right-2,5):
                dot(x,7,9);dot(x+1,7,10)
        for x in (5,56):post(x,13,24)
        for left,right in ((8,17),(46,56)):
            horiz(left,right,24,5)
            horiz(left+1,right-1,25,10)
    elif "FLANNERY_GYM" in name:
        # Vertical lava conduits and thick protruding shrine roof segments.
        for left,right in ((12,18),(46,52)):
            recess(left,right,5,9)
            horiz(left,right,10,13)
        for x in (4,55):
            post(x,11,26)
            for yy in (14,19,24):
                dot(x+1,yy,12);dot(x+2,yy,14)
        for left,right in ((8,18),(46,56)):
            horiz(left,right,27,5)
            horiz(left+1,right-1,28,13)
    else:
        # Four existing dwellings each receive a DIFFERENT pitched skylight:
        # none is copied identically from its neighbour.
        for i,cx in enumerate((12,25,39,52)):
            width=(7,5,9,6)[i]
            l=cx-width//2;r=l+width-1
            recess(l,r,5+i%2,8+i%2)
            for x in range(l+2,r-1,3):
                dot(x,7+i%2,11 if i%2 else 13)
            post(cx-6,14,23)
            horiz(cx-5,cx+5,26,5)
            horiz(cx-4,cx+4,27,13 if i%2 else 6)
    # Final material hierarchy: heavy basalt ridge, connected copper flashing
    # and short vertical shadow ribs. All coordinates live INSIDE the four
    # existing building murals and pass through the protected-pixel dot guard.
    if "POKEMON_CENTER" in name:
        for left,right in ((10,22),(42,54)):
            horiz(left,right,4,5)
            horiz(left+1,right-1,5,6)
            for x in range(left+3,right-2,5):
                dot(x,6,3);dot(x+1,7,2)
        for x in (11,51):
            horiz(x-3,x+3,23,5)
            horiz(x-2,x+2,24,13)
    elif "POKE_MART" in name:
        for left,right in ((13,25),(39,51)):
            horiz(left,right,4,5)
            horiz(left+1,right-1,5,6)
            for x in range(left+2,right-1,4):
                dot(x,6,3)
        for x in (9,53):
            horiz(x-3,x+3,22,5)
            horiz(x-2,x+2,23,10)
    elif "FLANNERY_GYM" in name:
        for left,right in ((11,17),(47,53)):
            horiz(left,right,4,5)
            horiz(left+1,right-1,5,13)
            for x in range(left+1,right-1,3):
                dot(x,6,3);dot(x,7,2)
        for x in (10,52):
            horiz(x-3,x+3,25,5)
            horiz(x-2,x+2,26,13)
    else:
        for i,cx in enumerate((12,25,39,52)):
            half=(5,4,6,4)[i]
            horiz(cx-half,cx+half,4+i%2,5)
            horiz(cx-half+1,cx+half-1,5+i%2,6)
            for x in range(cx-half+2,cx+half-1,3):
                dot(x,8,2 if i%2 else 3)
            horiz(cx-half,cx+half,23,5)
            horiz(cx-half+1,cx+half-1,24,13 if i%2 else 6)
    changed=sum(a.pix[y][x]!=old[y][x] for y in range(a.h) for x in range(a.w))
    if changed<45:
        raise ValueError(f"Roof massing changes too small: {name}: {changed}")
    if any(a.pix[y][x]!=old[y][x] for x,y in preserve):
        raise ValueError(f"Protected civic logo or original gable changed: {name}")
