#!/usr/bin/env python3
"""Distinctive deep-set facade details on EXISTING Cuordilava buildings.

Only paints existing private 64x16 / 64x32 mural graphics after the other
reference material passes. Never adds metatiles, buildings, map cells or
overworld objects. Flannery's original four hot-glass windows remain exactly
present and still readable, with the same palette/color identifiers.
"""

def deepen_existing_facades(a, name):
    p, line, rect = a.pixel, a.line, a.rect

    def jointed_column(x, top, bottom):
        """A buttress with a solid face and lit copper trailing edge."""
        rect(x, top, x+3, bottom, 8)
        line(x, top, x, bottom, 5)
        line(x+1, top+1, x+1, bottom-1, 6)
        line(x+3, top+1, x+3, bottom-1, 13)
        for y in range(top+3, bottom, 5):
            line(x, y, x+3, y, 5)
            p(x+2, y, 11)

    def deep_lintel(left, right, y):
        line(left, y, right, y, 2)
        line(left, y+1, right, y+1, 5)
        line(left+1, y+2, right-1, y+2, 13)
        for x in range(left+3, right-2, 8):
            p(x, y+2, 14)

    def stained_panel(x, y, width):
        """Recessed kiln glass with dark mullions and a shadowed sill."""
        rect(x-1, y-1, x+width, y+6, 8)
        rect(x, y, x+width-1, y+4, 12)
        line(x+1, y+1, x+width-2, y+1, 14)
        line(x+1, y+3, x+width-2, y+3, 11)
        line(x+width//2, y, x+width//2, y+4, 5)
        line(x-1, y+5, x+width, y+5, 6)

    if "GYM_FORGE_FACADE" in name:
        # Four black-stone kiln arches. Deliberately different from housing.
        # DO NOT touch mandatory window glass at (center±2, y=7/9):
        # the legacy validator compares those exact pixel indices to 12.
        for i,cx in enumerate((10,25,40,55)):
            left, right = cx-6, cx+6
            # Arch crown and thick lintel sit safely above window glass.
            line(left+2, 2, right-2, 2, 5)
            line(left+1, 3, right-1, 3, 6)
            line(left, 4, left+2, 4, 13)
            line(right-2, 4, right, 4, 13)
            # Thermal flues between each arch, not over the windows.
            for xx in (left, right):
                line(xx, 5, xx, 12, 5)
                line(xx+1, 5, xx+1, 12, 13)
                p(xx, 6, 11)
            # Deep sill with a low furnace heat channel.
            line(left+2, 12, right-2, 12, 5)
            line(left+3, 13, right-3, 13, 13)
            for x in range(left+4,right-3,3):
                p(x,13,14 if i%2==0 else 11)
            # The four furnace modules are intentionally not clones.
            if i==0:
                line(left+2, 5, left+4, 5, 14)
            elif i==1:
                line(right-4, 5, right-2, 5, 11)
            elif i==2:
                p(cx,3,14)
            else:
                p(cx,2,13)
            # Vertical vitrified-brick joints, outside glazed window center.
            for xx in (left+1, right-1):
                p(xx,10,6)
                p(xx,11,5)
        deep_lintel(1,62,0)
        # Low continuous iron sill makes the four modules read as one forge.
        line(1,14,62,14,5)
        line(3,15,60,15,13)

    elif "POKEMON_CENTER" in name:
        # Functional red-cross central emblem is intentionally untouched.
        # Service arcade and inset thermal glow on two side wings.
        for x in (9,50):
            jointed_column(x,14,25)
        for x in (15,46):
            stained_panel(x,18,5)
        deep_lintel(5,59,26)
        # Forge-bronze modular corbels below the original high roof.
        for x in (7,24,40,56):
            rect(x,12,x+2,14,8)
            line(x+1,12,x+1,14,13)
        # High ridge marks are small enough not to replace the clinic gable.
        for x in (18,25,39,46):
            p(x,5,6)
            p(x+1,6,5)

    elif "MART" in name:
        # Stay cyan-forward, as in the original shop: recessed side windows
        # and restrained copper framing rather than another red temple.
        for x in (8,52):
            jointed_column(x,13,24)
        for x in (13,47):
            stained_panel(x,16,5)
        # Protect original cyan shopping cart display center x20..44.
        # These short glass slits are on either side of that graphic.
        for x in (11,49):
            line(x,7,x+3,7,5)
            line(x+1,8,x+2,8,13)
        line(11,24,18,24,11)
        line(46,24,53,24,11)
        # Protect the continuous cyan canopy at y27 x16..47 unchanged.

    elif "HOUSING" in name:
        # Domestic balcony structures are timber/copper, not kiln arches.
        # Distinct heights hint at individual homes without extra footprints.
        for i,cx in enumerate((12,25,39,52)):
            height=(4,6,5,7)[i]
            for x in (cx-5,cx+4):
                line(x,17,x,17+height,5)
                line(x+1,18,x+1,17+height,6)
                p(x,17+height,13)
            line(cx-5,18+height,cx+5,18+height,13)
            for dx in (-3,0,3):
                p(cx+dx,19+height,11)
        # Roof gable peaks on y1 stay unchanged.

    # Plaza, baths, waterfalls and all global palette/light code untouched.
