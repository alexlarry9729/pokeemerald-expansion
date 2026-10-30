#!/usr/bin/env python3
"""Reference-led, bold roof identities within the ORIGINAL Cuordilava footprints.

Replaces muted, uniform high roof planes with a broad red-copper medical hip,
a cobalt/turquoise workshop roof, a furnace-black Gym crown and four different
house ridges. All edits are INDEXED 4bpp pixels on the four-by-two ORIGINAL
roof murals, never new buildings/metatiles/palettes, nor map/collision edits.

Apply AFTER the generic roof and wall sculpting, preserving protected iconic
pixels, the lower facades and the existing uninterrupted structural girders.
"""


def stamp_original_landmark_roof_identities(art, name):
    if not any(k in name for k in ("POKEMON_CENTER", "POKE_MART", "FLANNERY_GYM", "HOUSING")):
        return
    if (art.w, art.h) != (64, 32):
        raise ValueError(f"Unrecognized town landmark footprint {name}")
    old = [r[:] for r in art.pix]
    blocked = set()
    if "POKEMON_CENTER" in name:
        role = "center"
        blocked.update(((31,1),(20,8),(31,16),(31,18),(10,16)))
        blocked.update((x,11) for x in range(7,57))
        blocked.update((x,y) for x in range(24,41) for y in range(14,25))
    elif "POKE_MART" in name:
        role = "mart"
        blocked.update(((20,8),(32,20),(9,16)))
        blocked.update((x,11) for x in range(11,53))
        blocked.update((x,27) for x in range(16,48))
        blocked.update((x,y) for y in range(15,25) for x in range(20,45))
    elif "FLANNERY_GYM" in name:
        role = "gym"
        blocked.update(((20,8),(32,19)))
        blocked.update((x,0) for x in range(1,6))
        blocked.update((x,3) for x in range(19,45))
        blocked.update((x,11) for x in range(12,52))
        blocked.update((x,y) for y in range(14,26) for x in range(19,46))
    else:
        role = "housing"
        blocked.update((x,y) for x in (12,25,39,52) for y in (1,12))
        blocked.add((13,8))
    # Never modify the central emblem/canopy or any original landmark wall,
    # and do not let a bold roof recolor compromise the supporting fascias.
    if role != "housing":
        blocked.update((x,9) for x in range(7,57))
    else:
        blocked.update((x,10) for x in (11,25,39,52))
        blocked.add((13,8))

    def dot(x,y,c):
        if 0 <= x < 64 and 0 <= y < 32 and (x,y) not in blocked:
            art.pixel(x,y,c)
    def row(a,b,y,c):
        for x in range(a,b+1):dot(x,y,c)
    def roof(left,right,peak,eave,base,copper,midline,light):
        """Connected stepped hip, coursework, dark iron rails and dormers."""
        middle=(left+right)//2
        # Mass of roof is continuous at each x: no floating neon or panels.
        for x in range(left,right+1):
            shoulder=abs(x-middle)
            y0=min(eave-3,peak+shoulder//13)
            for y in range(y0,eave):
                if y == y0: c=5
                elif y == y0+1: c=copper
                elif y == eave-1: c=6
                elif (x//5+y)%7==0: c=midline
                else:c=base
                dot(x,y,c)
        # At the bottom of the roof, broad continuous half-toned piping.
        row(left,right,eave,5)
        row(left+1,right-1,eave+1,6)
        # Two real inset clerestories, framed in visible iron around glass.
        for cx in (left+10,right-10):
            if cx-4<left or cx+4>right:continue
            top=peak+3
            row(cx-4,cx+4,top,5)
            row(cx-3,cx+3,top+1,6)
            for x in range(cx-2,cx+3):
                dot(x,top+2,light if x!=cx else 5)
            row(cx-3,cx+3,top+3,5)
        # Copper bolt stripes are sparse, on the same roof, not floating.
        for x in range(left+3,right-2,8):
            dot(x,eave,13 if copper in (11,12,13,14) else 10)
            dot(x+1,eave+1,3)

    if role == "center":
        # Warm iconic medical roof: red copper as the PRIMARY broad material.
        # The historical roof cross and lower storefront remain untouched.
        roof(8,55,2,8,11,13,5,12)
        for left,right in ((11,21),(43,53)):
            row(left,right,6,13)
            row(left+1,right-1,7,11)
        for x in range(11,54,11):
            dot(x,4,14)
        # Red/gold shoulders under the raised medical crest.
        row(26,38,6,11)
        row(27,37,7,13)
        row(28,36,8,5)
    elif role == "mart":
        # Clearly different: near-black cobalt roof with luminous turquoise
        # ventilation glazing and an uninterrupted cold-metal perimeter.
        roof(11,52,3,8,8,6,5,10)
        for left,right in ((13,24),(40,51)):
            row(left,right,5,5)
            row(left+1,right-1,6,9)
            row(left+2,right-2,7,10)
        # Metal ventilation drumlets connect to, not cover, the shop badge.
        for cx in (18,46):
            row(cx-3,cx+3,3,5)
            row(cx-2,cx+2,4,10)
    elif role == "gym":
        # Molten forge terrace with robust black basalt shoulders. Keep the
        # single existing flame emblem and the original copper gallery.
        roof(12,51,4,8,8,13,2,12)
        for left,right in ((12,18),(46,52)):
            row(left,right,5,5)
            row(left+1,right-1,6,11)
            row(left+1,right-1,7,13)
        for cx in (16,48):
            dot(cx,4,14)
            dot(cx-1,5,12)
            dot(cx+1,5,12)
    else:
        # Four existing houses: intentionally unequal copper/graphite hips,
        # never a single uniform 64px-wide boilerplate roof.
        configs=((12,6,3,8,8,13,12),
                 (25,5,4,8,2,6,9),
                 (39,6,3,8,8,13,11),
                 (52,5,4,8,2,6,12))
        for cx,half,peak,eave,base,copper,light in configs:
            left,right=cx-half,cx+half
            # On small homes, a single well-supported attic skylight.
            for x in range(left,right+1):
                y0=min(eave-2,peak+abs(cx-x)//4)
                for y in range(y0,eave):
                    dot(x,y,5 if y==y0 else copper if y==y0+1 else base)
            row(left,right,eave,5)
            row(left+1,right-1,eave+1,copper)
            row(cx-3,cx+3,peak+2,5)
            row(cx-2,cx+2,peak+3,light)
            dot(cx,peak+3,6)
            row(cx-3,cx+3,peak+4,5)

    changed=sum(a!=b for p,q in zip(old,art.pix) for a,b in zip(p,q))
    if changed < 90:
        raise ValueError(f"Cuordilava landmark roof identity unchanged: {name} {changed}")
    if any(art.pix[y][x]!=old[y][x] for x,y in blocked):
        raise ValueError(f"Landmark original sign, roof support or entrance overwritten: {name}")
    if any(c < 0 or c > 15 for line in art.pix for c in line):
        raise ValueError(f"Invalid indexed 4bpp roof color {name}")
    if role=="center":
        roof_palette={art.pix[y][x] for y in range(3,8) for x in range(10,54)}
        if not {11,13}.issubset(roof_palette):
            raise ValueError("Clinic must retain obvious broad copper/red hip")
    if role=="mart":
        if sum(art.pix[y][x] in (9,10) for y in range(4,8)
               for x in range(11,53)) < 18:
            raise ValueError("Market must retain substantial cool-turquoise upper glass")
