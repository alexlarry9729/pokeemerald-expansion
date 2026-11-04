#!/usr/bin/env python3
"""Readable building-footings on existing Cuordilava roof/facade murals.

This pass joins the already drawn eaves to heavy stonework and segmented
copper-lit ground levels. No new building, map cell, warp or atlas graphic.
"""
def deepen_existing_foundations(a, name):
    if not any(t in name for t in ("POKEMON_CENTER", "POKE_MART",
                                    "FLANNERY_GYM", "HOUSING")):
        return
    previous=[r[:] for r in a.pix]
    def p(x,y,c):
        if 0<=x<a.w and 0<=y<a.h:
            a.pixel(x,y,c)
    def beam(x0,x1,y):
        for x in range(x0,x1+1):
            p(x,y,5)
            if x0+1<=x<=x1-1:p(x,y+1,13 if x%7 not in (0,1) else 6)
    def arch(cx,y,width=9):
        left=cx-width//2
        for x in range(left-2,left+width+2):
            if x in (left-2,left+width+1):
                for yy in range(y+2,min(y+9,31)):p(x,yy,5)
            elif x in (left-1,left+width):
                for yy in range(y+1,min(y+9,31)):p(x,yy,6)
            else:
                p(x,y,5);p(x,y+1,13)
        for yy in range(y+2,min(y+7,31)):
            for x in range(left,left+width):
                p(x,yy,12 if (x+yy)%5 else 11)
        for x in range(left+1,left+width-1,3):
            p(x,y+3,14);p(x,y+5,14)
        for yy in range(y+2,min(y+7,31)):p(cx,yy,5)
    if "POKEMON_CENTER" in name:
        for x in (6,54):
            for y in range(16,27):p(x,y,5);p(x+1,y,6)
            for y in (18,23):p(x+2,y,13)
        for cx in (15,49):arch(cx,19,7)
        for l,r in ((8,22),(42,56)):beam(l,r,27)
    elif "POKE_MART" in name:
        for cx in (12,51):arch(cx,17,7)
        for x in (6,56):
            for y in range(14,25):p(x,y,5)
            for y in (16,22):p(x+1,y,10)
        # Preserve cyan canopy y27 x16..47 and cart display x20..44.
        for left,right in ((5,15),(49,58)):beam(left,right,26)
    elif "FLANNERY_GYM" in name:
        for cx in (12,52):arch(cx,18,7)
        for x in (5,55):
            for y in range(14,27):
                p(x,y,5);p(x+1,y,6)
            for y in (17,23):p(x+2,y,14)
        for l,r in ((7,18),(46,57)):beam(l,r,28)
        # The flame emblem (x19..45,y14..25) remains untouched.
    else:
        for i,cx in enumerate((12,25,39,52)):
            # Four individual houses: different glass/balcony dimensions.
            width=(5,7,5,7)[i]
            arch(cx,17,width)
            for x in (cx-6,cx+5):
                for y in range(14,25):p(x,y,5)
            beam(cx-5,cx+5,26)
            p(cx-3,28,13 if i%2==0 else 11)
        # Four original gable peaks (row 1) remain untouched.
    if previous==a.pix:
        raise ValueError("Existing facade foundation pass made no artwork change")
