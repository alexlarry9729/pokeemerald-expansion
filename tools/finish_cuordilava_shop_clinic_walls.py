#!/usr/bin/env python3
"""Four original storefront/clinic wall bays, NOT new buildings.

Repaint just two existing non-door exterior wall cells below the Pokemon Center
and two existing non-door wall cells below the Mart. Reuse seven already-painted
private 16x16 housing-glass facade panels: zero new 8x8 pixels, 4bpp graphics,
palettes or atlas capacity. Exactly four previously unused, private secondary
metatiles 437..440 copy their original primary graphics and terrain behavior.

Doors at (9,6) and (15,5), all six town warps, NPCs, map size and collision/
elevation flags are preserved. This is an explicit four-cell, fail-closed edit.
"""
from pathlib import Path
import json
import struct
from construct_cuordilava_lower_facade import ART_TILES

WIDTH = HEIGHT = 20
# (x,y, existing primary metatile, new private metatile, 7-bay atlas index)
WALL_BAYS = (
    (8, 6, 96, 437, 0),  # Center: basalt-framed heated window
    (10, 6, 98, 438, 2), # Center: divided copper thermal glazing
    (14, 5, 96, 439, 3), # Mart: cyan service-panel glass
    (16, 5, 66, 440, 5), # Mart: purple/cyan narrow technical conduit
)
DOORS = ((9, 6), (15, 5))


def loc(root):
    r=Path(root)
    return {
      "town":r/"data/layouts/LavaridgeTown/map.bin",
      "secondary":r/"data/tilesets/secondary/cuordilava/metatiles.bin",
      "secondary_attr":r/"data/tilesets/secondary/cuordilava/metatile_attributes.bin",
      "primary":r/"data/tilesets/primary/general/metatiles.bin",
      "primary_attr":r/"data/tilesets/primary/general/metatile_attributes.bin",
      "events":r/"data/maps/LavaridgeTown/map.json",
      "layout":r/"data/layouts/layouts.json",
    }


def word(b,offset):
    return struct.unpack_from("<H",b,offset)[0]


def event_guard(paths):
    events=json.loads(paths["events"].read_text(encoding="utf-8"))
    # Only existing, non-interactive light-anchor sprites are allowed on the
    # decorated wall tiles: the lit wall is their exact intended backdrop.
    # Never overwrite a door, sign, NPC, coordinate event or real trigger.
    occupied=set()
    for kind in ("warp_events","coord_events","bg_events","object_events"):
        for e in events.get(kind,[]):
            if "x" not in e or "y" not in e:
                continue
            if (kind=="object_events"
                    and e.get("graphics_id")=="OBJ_EVENT_GFX_LIGHT_SPRITE"
                    and e.get("script")=="NULL"):
                continue
            occupied.add((e["x"],e["y"]))
    target={(x,y) for x,y,_,_,_ in WALL_BAYS}
    if occupied & target:
        raise ValueError(f"Existing interactive event overlaps an architectural wall: {occupied & target}")
    doors={(e["x"],e["y"]) for e in events["warp_events"]}
    if not set(DOORS).issubset(doors) or len(events["warp_events"])!=6:
        raise ValueError("Original Center/Mart doorway or other building warps moved")


def validate_built(root):
    p=loc(root)
    town,secondary,attrs,primary,priat=(
        p["town"].read_bytes(),p["secondary"].read_bytes(),
        p["secondary_attr"].read_bytes(),p["primary"].read_bytes(),
        p["primary_attr"].read_bytes())
    if (len(town),len(secondary),len(attrs)) != (800,8192,1024):
        raise ValueError("Cuordilava no longer has original 20x20 map or 512 private metatiles")
    layout=json.loads(p["layout"].read_text(encoding="utf-8"))
    entry=next(x for x in layout["layouts"] if x["id"]=="LAYOUT_LAVARIDGE_TOWN")
    if (entry["width"],entry["height"]) != (20,20):
        raise ValueError("Cuordilava layout expanded or shrunk")
    event_guard(p)
    used={}
    for idx in range(400):
        used.setdefault(word(town,idx*2)&1023,[]).append((idx%20,idx//20))
    for x,y,old,mid,panel in WALL_BAYS:
        cell=word(town,(y*20+x)*2)
        if cell&1023 != 512+mid or used[512+mid] != [(x,y)]:
            raise ValueError(f"Original wall bay {x,y} was displaced or duplicated")
        if attrs[mid*2:mid*2+2] != priat[old*2:old*2+2]:
            raise ValueError(f"Wall bay {x,y} changed its terrain behavior")
        if secondary[mid*16:mid*16+8] != primary[old*16:old*16+8]:
            raise ValueError(f"Wall bay {x,y} changed original background/collision graphics")
        for q in range(4):
            expected=(6<<12)|(512+ART_TILES[4*panel+q])
            if word(secondary,mid*16+8+q*2)!=expected:
                raise ValueError(f"Missing original 4bpp wall-panel art at {x,y}")
    for x,y in DOORS:
        if (word(town,(20*y+x)*2)&1023) >= 512+437:
            raise ValueError("A doorway was covered by a wall-panel metatile")


def run(root):
    p=loc(root)
    mapbuf=bytearray(p["town"].read_bytes())
    meta=bytearray(p["secondary"].read_bytes())
    attr=bytearray(p["secondary_attr"].read_bytes())
    primary=p["primary"].read_bytes()
    priat=p["primary_attr"].read_bytes()
    if (len(mapbuf),len(meta),len(attr)) != (800,8192,1024):
        raise ValueError("Run clinic/shop edit only AFTER the protected 20x20 mural generator")
    event_guard(p)
    present={word(mapbuf,i*2)&1023 for i in range(400)}
    if any(512+mid in present for _,_,_,mid,_ in WALL_BAYS):
        raise ValueError("Selected clinic/shop private metatiles already in use")
    # Never consume or overwrite a new 8x8 GBA graphical tile.
    if len(ART_TILES)!=28 or any(t<0 or t>=512 for t in ART_TILES):
        raise ValueError("Original housing glass 4bpp source atlas changed")
    before_map,before_meta,before_attrs=bytes(mapbuf),bytes(meta),bytes(attr)
    targets={(x,y) for x,y,_,_,_ in WALL_BAYS}
    for x,y,old,mid,panel in WALL_BAYS:
        offset=2*(20*y+x)
        before=word(mapbuf,offset)
        if before&1023 != old:
            raise ValueError(f"Existing Center/Mart wall moved at {x,y}: {before&1023}")
        new=bytearray(primary[old*16:old*16+8])
        if len(new)!=8:
            raise ValueError("Damaged original wall underlay")
        for q in range(4):
            new+=struct.pack("<H",(6<<12)|(512+ART_TILES[panel*4+q]))
        meta[mid*16:mid*16+16]=new
        attr[mid*2:mid*2+2]=priat[old*2:old*2+2]
        struct.pack_into("<H",mapbuf,offset,(before&~1023)|(512+mid))
    for i in range(400):
        before,after=word(before_map,i*2),word(mapbuf,i*2)
        if (before>>10)!=(after>>10) or (
            (i%20,i//20) not in targets and before != after):
            raise ValueError("Unexpected 20x20 map/position/collision change")
    for mid in range(512):
        if mid not in (437,438,439,440) and (
            meta[mid*16:(mid+1)*16] != before_meta[mid*16:(mid+1)*16]
            or attr[mid*2:(mid+1)*2] != before_attrs[mid*2:(mid+1)*2]):
            raise ValueError("Wall edit leaked into an unrelated metatile/terrain attribute")
    p["town"].write_bytes(mapbuf)
    p["secondary"].write_bytes(meta)
    p["secondary_attr"].write_bytes(attr)
    validate_built(root)
    print("Cuordilava lower walls: four unique, door-safe, shadowed Center/Mart "
          "window panels; no new buildings, pixels, warp/collision or size changes")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
