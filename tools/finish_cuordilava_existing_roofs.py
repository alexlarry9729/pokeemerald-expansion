#!/usr/bin/env python3
"""Reference-based rooftop silhouette and material pass, ORIGINAL Cuordilava only.

Four landmarks receive distinct, *connected* roof profiles and facades: a
layered volcanic clinic, cool low-profile market, central blast furnace and
asymmetric terraced homes. Rather than repainting common tiles or enlarging
the map, this final architectural pass paints inside the existing 48 protected
town-specific metatile murals BEFORE those metatiles are allocated.

Palette is the original town-private indexed bank 6 (night companion bank 15).
No added graphic/metatile indices, object events, warps, collision, or 20x20
map cells. Keep existing water, animated tiles, plants and global night light.
"""


def finish_existing_architecture(a, name):
    p, line, rect = a.pixel, a.line, a.rect

    def lintel(x0, x1, y, accent=13):
        """Four-tone undercut steel/copper cornice with support rivets."""
        line(x0, y, x1, y, 3)
        line(x0, y+1, x1, y+1, 5)
        line(x0+1, y+2, x1-1, y+2, accent)
        line(x0+2, y+3, x1-2, y+3, 8)
        for x in range(x0+5, x1-2, 9):
            p(x,y+2,14)

    def heater(cx, y, width=7, height=7):
        """Recessed orange window. Large contiguous light, not point specks."""
        x0, x1 = cx-width//2, cx+width//2
        rect(x0-2,y-2,x1+2,y+height,8)
        rect(x0-1,y-1,x1+1,y+height-1,5,False)
        rect(x0,y,x1,y+height-2,12)
        for yy in range(y+1,y+height-2):
            line(x0+1,yy,x1-1,yy,14 if yy%3 else 11)
        line(cx,y,cx,y+height-2,6)
        line(x0-1,y+height-1,x1+1,y+height-1,13)
        p(cx-1,y+1,11)

    def roof_slope(cx, apex, left, right, eave, slate=8):
        """Joined trapezoid/hip, shadows on right and copper ridge on left."""
        for x in range(left,right+1):
            top=min(eave-3,apex+abs(x-cx)//5)
            for y in range(top,eave):
                c=slate if (x+y)%7 else 2
                p(x,y,c)
            p(x,top,6 if x<=cx else 5)
            if top+1 < eave:
                p(x,top+1,3 if x<cx else 1)
            if (x-cx)%11==0:
                for yy in range(top+3,eave-1):
                    if yy%3: p(x,yy,2)
        line(left,eave-1,right,eave-1,5)
        line(left+1,eave,right-1,eave,13)
        for x in range(left+4,right-2,8):
            p(x,eave,11)

    def riveted_column(x,y0,y1):
        rect(x,y0,x+4,y1,8)
        line(x,y0,x,y1,5)
        line(x+1,y0+1,x+1,y1-1,6)
        line(x+3,y0+1,x+3,y1-1,13)
        for y in range(y0+3,y1,6):
            line(x,y,x+4,y,5)
            p(x+2,y,14)

    if 'POKEMON_CENTER' in name:
        # Broad steep basalt roof on a two-step copper thermal gallery.
        roof_slope(31,1,9,54,10)
        lintel(8,56,11,13)
        # Central relief includes a monumental inset glass crest. Preserve
        # the famous red cross (visual identity) in a deep iron octagon.
        rect(24,14,40,24,8)
        for x0,y0,x1,y1 in ((26,14,38,14),(23,18,41,18),
                            (24,23,40,23)):
            line(x0,y0,x1,y1,5)
        a.ring(32,19,10,6,2)
        a.ring(32,19,8,13,1)
        rect(29,14,34,23,11)
        rect(25,17,39,20,11)
        rect(30,15,33,22,12)
        rect(26,18,38,19,12)
        line(31,16,31,21,14)
        line(27,18,37,18,14)
        # Side cooling towers visually connect to a vaulted gallery.
        for x in (5,54):
            riveted_column(x,5,25)
            for y in (8,14,20):
                p(x+2,y,11)
        for cx in (13,51):
            heater(cx,18,5,6)
        lintel(2,61,26,14)
        for cx in (11,24,40,53):
            rect(cx-5,29,cx+4,30,12)
            line(cx-4,29,cx+3,29,14)
            p(cx,30,11)

    elif 'MART' in name:
        # SHOP: restrained horizontal tech slab rather than a copy of the
        # clinic. Shallow roof with a cold cyan strip and orange side service.
        roof_slope(31,3,12,51,10)
        lintel(10,53,11,9)
        for x in (6,53):
            riveted_column(x,10,25)
        for cx in (13,51):
            heater(cx,15,7,9)
        # Center is distinctly a glass shopping frontage/cart display.
        rect(20,14,44,24,8)
        rect(21,15,43,23,9,False)
        line(24,17,28,20,10)
        line(28,20,40,20,10)
        line(40,20,42,17,10)
        line(26,17,41,17,9)
        for x in (29,38):
            a.ring(x,23,2,10,1)
        # Deliberately continuous cool storefront canopy (test checks row27).
        line(15,25,48,25,5)
        line(16,26,47,26,10)
        line(16,27,47,27,9)
        line(16,28,47,28,10)
        line(17,29,46,29,6)
        for x in (19,27,35,43):
            p(x,27,10)
            p(x+1,28,9)

    elif 'FLANNERY_GYM' in name:
        # Blacksmith shrine: copper spires and a peaked furnace hall.
        # Legacy regression guard: y0,x1..5=13 and y3,x19..44=14.
        roof_slope(32,1,14,49,10)
        for x in (1,57):
            riveted_column(x,1,26)
            line(x,0,x+4,0,13)
            for y in (7,13,19):
                rect(x+1,y,x+3,y+2,12)
                line(x+2,y,x+2,y+1,14)
        line(19,3,44,3,14)
        lintel(16,47,10,13)
        # Carve a single raised volcanic-fire emblem into the furnace face.
        rect(19,14,45,25,8)
        a.ring(32,19,10,6,2)
        a.ring(32,19,8,13,1)
        for x0,y0,x1,y1 in ((28,23,27,18),(27,18,30,14),
                             (30,14,33,20),(33,20,36,15),
                             (36,15,39,22),(39,22,34,24)):
            line(x0,y0,x1,y1,12)
        for x,y in ((31,19),(31,20),(32,20),(33,20),(32,21),
                    (33,21),(34,21),(33,22)):
            p(x,y,14)
        # Staggered kiln windows under a continuous mechanical shelf.
        for cx in (11,21,43,53):
            heater(cx,24,5,6)
        lintel(7,56,28,14)
        for x in range(12,54,7):
            p(x,31,12)
        line(1,0,5,0,13)  # non-negotiable left chimney cap

    elif 'HOUSING' in name:
        # Existing residential terrace, but NOT four identical rectangles:
        # high/low masonry pediments, differentiated window bays and pipes.
        for i,cx in enumerate((12,25,39,52)):
            apex=(2,4,2,3)[i]
            roof_slope(cx,apex,cx-7,cx+6,11)
            p(cx,1,6)  # recognizable four original house-gable peaks
            p(cx,2,6)
            line(cx-6,12,cx+6,12,13 if i%2==0 else 5)
            riveted_column(cx-7,13,25)
            if i in (0,3):
                heater(cx,17,7,7)
                line(cx-4,26,cx+4,26,13)
            elif i==1:
                heater(cx-2,17,5,8)
                line(cx+3,14,cx+3,24,15)
                for y in (16,20,24):p(cx+3,y,10)
            else:
                heater(cx,16,7,9)
                line(cx-4,25,cx+4,25,11)
            for yy in (14,23):
                p(cx+5,yy,12)
        lintel(1,62,27,13)
        for cx in (12,25,39,52):
            line(cx-4,30,cx+3,30,12)
            p(cx,29,14)

    elif 'GYM_FORGE_FACADE' in name:
        # Existing ground-floor four-window facade; preserve exactly the
        # old warm-glass pixels required by the gameplay/art regression tests.
        lintel(0,63,0,13)
        for x in (1,62):
            line(x,4,x,14,5)
            p(x,7,13)

    # The existing civic plaza, spa water and natural scenery are deliberately
    # untouched by this building-only pass.
