#!/usr/bin/env python3
"""High-density volcanic cyberpunk relief for Lavaridge's private civic murals.

The source painting is generated inside the SAME 48 preallocated 16x16
collision-preserving metatiles as the earlier sculptor; this layer makes
the black-iron structures read as whole inhabited buildings with orange
furnace galleries, warm windows, coolant risers and substantial eaves.
Zero changes to map footprint, objects, doors, reserved metatiles or world
day/night light. Coordinates below are local pixels within 64x32 roofs.
"""


def add_dense_reference_details(a, name):
    p, ln, box = a.pixel, a.line, a.rect
    def point(x, y, c):
        p(x, y, c)

    def window(cx, y, w=9, h=7):
        """Deep glazed furnace window, framed in basalt with a copper lip."""
        left, right = cx - w//2, cx + w//2
        box(left-2, y-2, right+2, y+h+1, 8)
        box(left-1, y-1, right+1, y+h, 5, False)
        box(left, y, right, y+h-1, 12)
        ln(left+1, y+1, right-1, y+1, 11)
        for yy in range(y+2,y+h-1):
            if yy % 3 != 0:
                ln(left+1,yy,right-1,yy,14)
        ln(cx,y,cx,y+h-1,5)
        ln(left-1,y+h,right+1,y+h,6)
        point(left, y+h, 13);point(right,y+h,13)

    def bolted_beam(x1,y,x2,heat=False):
        ln(x1,y,x2,y,5)
        ln(x1,y+1,x2,y+1,14 if heat else 6)
        for xx in range(x1+3,x2,7):
            point(xx,y,3)
            point(xx,y+1,11 if heat else 7)

    def furnace_grille(x0,y0,w=8,h=5):
        box(x0-1,y0-1,x0+w,y0+h,8)
        box(x0,y0,x0+w-1,y0+h-1,12)
        for y in range(y0,y0+h):
            if y%2 == 0:
                ln(x0+1,y,x0+w-2,y,14)
        for x in (x0+2,x0+w-3):
            ln(x,y0,x,y0+h-1,5)
        ln(x0-1,y0+h,x0+w,y0+h,6)

    if "POKEMON_CENTER" in name:
        # Broad continuous thermal gallery in front of the high reactor roof.
        # Keep center cross area x=24..40, y=11..23 unobscured.
        for x in (8,18,46,56):
            box(x-3,11,x+3,24,8)
            ln(x-2,12,x-2,23,6)
            ln(x+2,12,x+2,23,14)
            for y in (13,17,21):
                ln(x-2,y,x+2,y,12)
                point(x,y,11)
        for x in (21,27,33,39):
            furnace_grille(x,3,5,3)
        bolted_beam(5,26,59,True)
        for cx in (12,24,40,52):
            # The lower edge of the roof is an orange, windowed factory cornice.
            box(cx-5,28,cx+5,30,8)
            ln(cx-4,28,cx+4,28,12)
            for xx in range(cx-3,cx+4,2):
                point(xx,29,14)
        for x in (3,60):
            ln(x,5,x,25,5)
            ln(x+1,6,x+1,24,13)

    elif "MART" in name:
        # Cool signage is kept, surrounded by *orange* service windows.
        for cx in (11,53):
            window(cx,13,7,8)
        for cx in (22,31,40):
            furnace_grille(cx-4,3,6,4)
        for x in (3,60):
            ln(x,5,x,25,5)
            ln(x+1,6,x+1,24,11)
            for y in (9,15,21):
                point(x+1,y,14)
        bolted_beam(5,23,58,True)
        # Show three repeated riveted ribs above the unbroken teal storefront.
        for x in (18,32,46):
            box(x-1,8,x+1,12,8)
            ln(x,8,x,12,13)
            point(x,9,14)

    elif "FLANNERY_GYM" in name:
        # Two six-pixel-wide columns become roaring brick furnaces; flame sign
        # remains the singular medallion on the main pitched black roof.
        for cx in (11,53):
            for y in (11,17,23):
                furnace_grille(cx-4,y,9,5)
            ln(cx-6,8,cx-6,26,6)
            ln(cx+6,8,cx+6,26,13)
        # Horizontal fire chamber below the glyph.
        for x in (21,29,37):
            furnace_grille(x,25,7,5)
        bolted_beam(8,30,55,True)
        # Copper piping makes both chimneys structurally connect to the roof.
        for x in (6,57):
            ln(x,8,x,29,11)
            ln(x+1,9,x+1,29,14)

    elif "HOUSING" in name:
        # Four steep gables now have actual dwelling windows, glowing orange
        # against charcoal rather than looking like blank abstract chevrons.
        for cx in (12,25,39,52):
            box(cx-4,5,cx+4,7,8)
            ln(cx-3,5,cx+3,5,6)
            ln(cx-2,6,cx+2,6,13)
            point(cx,6,14)
            window(cx,14,7,7)
            for xx in (cx-7,cx+7):
                ln(xx,11,xx,26,5)
                point(xx,12,13)
                point(xx,20,14)
        bolted_beam(2,27,61,True)

    elif "GYM_FORGE_FACADE" in name:
        # Existing four warm panes are protected by the fixed validator:
        # add a surrounding molten-copper lintel and riveted end braces.
        bolted_beam(1,0,62,True)
        for cx in (10,25,40,55):
            point(cx-4,3,14)
            point(cx+4,3,14)
            ln(cx-4,12,cx+4,12,5)
            ln(cx-4,13,cx+4,13,13)
        for x in (1,62):
            ln(x,3,x,14,6)

    elif "PLAZA" in name:
        # Symmetric octagonal civic volcano seal with small kiln lanterns in
        # the corners; stays flush on ground (no false solid-looking walls).
        for cx,cy in ((6,5),(57,5),(6,25),(57,25)):
            box(cx-2,cy-2,cx+2,cy+2,8)
            ln(cx-1,cy-1,cx+1,cy-1,6)
            point(cx,cy-1,14)
            point(cx,cy,11)
            ln(cx-1,cy+2,cx+1,cy+2,13)
        for radius in (13,11):
            a.ring(31,16,radius,6 if radius==13 else 13,1)
        for x in range(12,52,5):
            if x not in range(23,41):
                point(x,2,14)
                point(x,29,11)
        for y in (7,13,19,25):
            point(5,y,13)
            point(58,y,14)

    elif "THERMAL_BASIN" in name:
        # Decorative open-work balustrade above the still-visible water.
        for x in range(5,59,8):
            point(x,8,13)
            point(x+1,8,11)
            ln(x,9,x+5,9,5)
            point(x+3,10,14)
