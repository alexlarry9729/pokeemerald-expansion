#!/usr/bin/env python3
"""Depth composition for already-existing Cuordilava buildings, 20x20 only.

This paints structural roof-to-facade joins inside the 48 allocated private
architectural mural metatiles. No map cell, entrance, tileset bank, palette,
collision, NPC, warp or moonlight engine changes. The public spa and square
are intentionally excluded.
"""

def connect_roofs_to_walls(a, name):
    p, line, rect = a.pixel, a.line, a.rect

    def truss(x0, y0, x1, y1, dark=5, highlight=13):
        # Diagonal solid shadow brace backed by a narrow warm copper edge.
        line(x0, y0, x1, y1, dark)
        line(x0+1, y0, x1+1, y1, highlight)
        p(x0, y0, 6)
        p(x1, y1, 11)

    def roof_underside(left, right, y, drops):
        """One continuous projecting eave; below is deep black air-space."""
        line(left, y, right, y, 6)
        line(left, y+1, right, y+1, 5)
        line(left+1, y+2, right-1, y+2, 8)
        for x in drops:
            rect(x-1, y+2, x+2, y+5, 8)
            line(x, y+3, x, y+5, 6)
            line(x+2, y+3, x+2, y+5, 13)
            p(x+1, y+4, 11)

    def light_grille(left, top, w, h=6):
        """Connected kiln vent: large illuminated area behind iron lattice."""
        rect(left-1,top-1,left+w,top+h,8)
        rect(left,top,left+w-1,top+h-1,12)
        for y in range(top+1,top+h-1):
            line(left+1,y,left+w-2,y,14 if y%3 else 11)
        for x in range(left+2,left+w-1,4):
            line(x,top,x,top+h-1,5)
        line(left-1,top+h,left+w,top+h,6)

    def side_foundation(x0, y0, x1, y1):
        # Thick basalt side wall, a deep undercut, then its outer copper edge.
        rect(x0,y0,x1,y1,8)
        line(x0,y0,x0,y1,5)
        line(x0+1,y0+1,x0+1,y1-1,6)
        line(x1,y0,x1,y1,13)
        for y in range(y0+4,y1,6):
            line(x0+1,y,x1-1,y,5)
            p(x1-1,y+1,11)

    if 'POKEMON_CENTER' in name:
        # Uninterrupted center emblem at x24..40 y14..24 is protected.
        roof_underside(7,56,10,(12,20,44,52))
        side_foundation(3,15,8,25)
        side_foundation(55,15,60,25)
        for x in (12,46):
            light_grille(x,17,7,7)
        for x0,y0,x1,y1 in ((9,14,14,18),(54,14,49,18),
                             (8,23,13,26),(55,23,50,26)):
            truss(x0,y0,x1,y1)
        # Large raised service-window lintel joins the side wings as a
        # single occupied structure, without painting over the cross.
        line(10,25,22,25,5)
        line(42,25,54,25,5)
        line(11,26,21,26,13)
        line(43,26,53,26,13)

    elif 'MART' in name:
        # Shop is deliberately lower / cooler; no furnace temple duplicate.
        roof_underside(11,52,10,(16,23,41,48))
        side_foundation(4,15,9,24)
        side_foundation(54,15,59,24)
        for x in (11,47):
            light_grille(x,16,6,7)
        truss(9,13,15,17)
        truss(54,13,48,17)
        # The shopping cart/blue service display x20..44,y15..24 and
        # 34px continuous turquoise canopy at y27 are never overwritten.
        line(5,25,14,25,5)
        line(49,25,58,25,5)
        for x in (7,56):
            p(x,23,10)

    elif 'FLANNERY_GYM' in name:
        # A projecting iron temple roof held by furnace buttresses.
        # Preserve chimney y0,x1..5 and copper gallery y3,x19..44.
        roof_underside(12,51,10,(18,25,38,46))
        side_foundation(7,15,13,24)
        side_foundation(50,15,56,24)
        for x in (9,50):
            light_grille(x,18,5,5)
        for a0,b0,a1,b1 in ((13,13,18,17),(50,13,45,17),
                             (14,24,19,27),(49,24,44,27)):
            truss(a0,b0,a1,b1)
        # Flame emblem occupies x19..45, y14..25 and stays entirely free.
        # Full-width dark furnace plinth anchors the roof to the lower forge.
        line(9,28,55,28,5)
        line(11,29,53,29,13)
        for x in (17,47):
            rect(x,26,x+3,28,8)
            p(x+2,27,14)

    elif 'HOUSING' in name:
        # Existing terrace keeps four unequal homes on the same four roof
        # cells. Each upper floor gets separate load-bearing diagonal woodwork.
        for i,cx in enumerate((12,25,39,52)):
            left,right=cx-6,cx+6
            roof_underside(left,right,11,(cx-3,cx+2))
            # Deep masonry footings separate the houses without new doors.
            for x in (left,right-2):
                side_foundation(x,14,x+2,22)
            if i%2==0:
                truss(left+1,14,left+4,17,5,13)
                truss(right-1,14,right-4,17,5,13)
            else:
                truss(left+2,15,left+5,19,6,13)
                truss(right-2,15,right-5,19,6,13)
            # Balcony underhang casts a true dark void, not neon wallpaper.
            line(left+2,23,right-2,23,5)
            line(left+3,24,right-3,24,13 if i%2 else 6)
            p(cx,1,6)  # original pointed gable kept
        line(2,28,61,28,5)
        line(4,29,59,29,13)

    # GYM_FORGE_FACADE is intentionally not repainted. Its four windows
    # have exact protected indices and the previous deep-arch pass is complete.
    # Plaza and spa visuals are also untouched.
