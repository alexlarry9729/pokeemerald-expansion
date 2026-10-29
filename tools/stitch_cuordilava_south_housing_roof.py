#!/usr/bin/env python3
"""Close the visible roof discontinuity across the EXISTING south housing row.

The original Lavaridge roofing covers x=11..18, y=12..13. Previously a custom
mural decorated ONLY x=11..14, leaving a visibly different unmodified right
half. Mirror the existing authored *roof graphics* across the right four cells
using the same 32 source 8x8 art tiles and six UNUSED town-private metatiles.

The code never creates buildings, game objects, extra roof cells, passable
cells, graphics tiles or scripts. Base-layer graphics, exact per-cell terrain,
original 20x20 map size and all six door warps are retained unchanged.
Run at the very end of the town-only graphic pipeline (after existing roofs).
"""
from pathlib import Path
import json
import struct

SRC_X = (11, 12, 13, 14)
DST_X = (15, 16, 17, 18)
YS = (12, 13)
# Existing rooftop scenery has functional chimney motifs at (15,13) and
# (17,13). Never replace either with additional slate: stitch around them.
CHIMNEYS = {(15, 13): 499, (17, 13): 500}
TARGETS = ((15,12), (16,12), (17,12), (18,12), (16,13), (18,13))
NEW_METAS = tuple(range(416, 422))
EXPECTED_OLD = ((8, 9, 9, 10), (16, 17, 17, 18))
assert len(NEW_METAS) == len(TARGETS) == 6


def word(data, off):
    return struct.unpack_from("<H", data, off)[0]


def paths(root):
    root = Path(root)
    return {
        "map": root/"data/layouts/LavaridgeTown/map.bin",
        "meta": root/"data/tilesets/secondary/cuordilava/metatiles.bin",
        "attr": root/"data/tilesets/secondary/cuordilava/metatile_attributes.bin",
        "primary": root/"data/tilesets/primary/general/metatiles.bin",
        "primary_attr": root/"data/tilesets/primary/general/metatile_attributes.bin",
        "events": root/"data/maps/LavaridgeTown/map.json",
        "layouts": root/"data/layouts/layouts.json",
    }


def event_guard(p):
    layouts = json.loads(p["layouts"].read_text(encoding="utf-8"))["layouts"]
    selected = [row for row in layouts
                if row.get("secondary_tileset") == "gTileset_CuordilavaLavaridge"]
    if len(selected) != 1 or selected[0]["id"] != "LAYOUT_LAVARIDGE_TOWN":
        raise ValueError("Town roof graphics must remain exclusive to Cuordilava")
    if (selected[0]["width"], selected[0]["height"]) != (20, 20):
        raise ValueError("Original 20x20 Lavaridge roof grid has changed")
    events = json.loads(p["events"].read_text(encoding="utf-8"))
    reserved = {(int(e["x"]), int(e["y"]))
                for kind in ("object_events", "bg_events",
                             "coord_events", "warp_events")
                for e in events.get(kind, [])
                if "x" in e and "y" in e}
    roof = set(TARGETS)
    if reserved & roof:
        raise ValueError(f"Protected house event below the roof: {reserved & roof}")
    if len(events["warp_events"]) != 6:
        raise ValueError("Town entrances changed")


def mirrored_overlay(sec, src_mid):
    if src_mid < 512 or src_mid-512 not in range(477, 485):
        raise ValueError(f"Original house roof mural was displaced: {src_mid}")
    original = struct.unpack_from("<4H", sec, (src_mid-512)*16+8)
    for entry in original:
        if entry >> 12 != 6 or (entry & 0xc00) != 0 or (entry & 1023) < 512:
            raise ValueError("Roof tiles must use unflipped 4bpp mural art")
    # On each destination 16x16 cell, swap left/right source quadrants and
    # H-flip each GBA 8x8 tile. The two halves meet at a mirrored pixel seam.
    return tuple(original[q ^ 1] | 0x0400 for q in range(4))


def validate_built(root):
    p = paths(root)
    event_guard(p)
    m, sec, attr = (p[key].read_bytes() for key in ("map","meta","attr"))
    pri, priattr = (p[key].read_bytes() for key in ("primary","primary_attr"))
    if (len(m),len(sec),len(attr)) != (800,8192,1024):
        raise ValueError("Housing seam changes 20x20 or GBA metatile budget")
    used = {}
    for i in range(400):
        mid = word(m,i*2) & 1023
        used.setdefault(mid,[]).append((i%20,i//20))
    for n,(x,y) in enumerate(TARGETS):
            row,col=YS.index(y),DST_X.index(x)
            mid=NEW_METAS[n]
            old = EXPECTED_OLD[row][col]
            src_x = SRC_X[3-col]
            src_mid = word(m,(20*y+src_x)*2) & 1023
            current = word(m,(20*y+x)*2)
            if current & 1023 != 512+mid or used[512+mid] != [(x,y)]:
                raise ValueError(f"South housing roof still separated at {x},{y}")
            if sec[mid*16:mid*16+8] != pri[old*16:old*16+8]:
                raise ValueError(f"Original housing roof base replaced at {x},{y}")
            if attr[mid*2:mid*2+2] != priattr[old*2:old*2+2]:
                raise ValueError(f"Roof terrain behavior altered at {x},{y}")
            overlay = tuple(word(sec,mid*16+8+2*q) for q in range(4))
            if overlay != mirrored_overlay(sec,src_mid):
                raise ValueError(f"Mirrored 8x8 quadrants misregistered at {x},{y}")
            if current >> 10 != word(m,(20*y+SRC_X[col])*2) >> 10:
                # Source and destination are two sides of same existing roof
                # but must retain their original elevation layer.
                raise ValueError(f"Mirrored roof has inconsistent elevation at {x},{y}")


def run(root):
    p = paths(root)
    event_guard(p)
    m, sec, attr = (bytearray(p[key].read_bytes())
                    for key in ("map","meta","attr"))
    pri, priattr = (p[key].read_bytes()
                    for key in ("primary","primary_attr"))
    if (len(m),len(sec),len(attr)) != (800,8192,1024):
        raise ValueError("Stitch after full Cuordilava tileset generation")
    occupied = {word(m,i*2)&1023 for i in range(400)}
    if any(512+mid in occupied for mid in NEW_METAS):
        raise ValueError("Chosen private roof registration metas are already used")
    original_map, original_meta, original_attr = bytes(m), bytes(sec), bytes(attr)
    # Before painting, verify the two physical chimneys are still present.
    for (x,y),expected in CHIMNEYS.items():
        actual=word(m,2*(20*y+x))&1023
        if actual!=512+expected:
            raise ValueError(f"Protected town chimney moved at {x},{y}: {actual}")
    for n,(x,y) in enumerate(TARGETS):
            row,col=YS.index(y),DST_X.index(x)
            pos = (20*y+x)*2
            oldword = word(m,pos)
            oldid = oldword & 1023
            if oldid != EXPECTED_OLD[row][col]:
                raise ValueError(f"Original untouched house roof moved {x},{y}: {oldid}")
            src_x = SRC_X[3-col]
            src_mid = word(m,(20*y+src_x)*2)&1023
            donor = mirrored_overlay(sec,src_mid)
            newmid = NEW_METAS[n]
            background = pri[oldid*16:oldid*16+8]
            if len(background) != 8:
                raise ValueError("Original housing roof background is invalid")
            sec[newmid*16:newmid*16+16] = background + struct.pack("<4H",*donor)
            attr[newmid*2:newmid*2+2] = priattr[oldid*2:oldid*2+2]
            struct.pack_into("<H",m,pos,(oldword&~1023)|(512+newmid))
    targets = set(TARGETS)
    for i in range(400):
        old,new = word(original_map,2*i),word(m,2*i)
        if (old>>10)!=(new>>10) or (
            (i%20,i//20) not in targets and old!=new):
            raise ValueError("South housing roof edit leaked into movement/map cell")
    if any(sec[mid*16:mid*16+16] != original_meta[mid*16:mid*16+16]
           for mid in range(512) if mid not in NEW_METAS):
        raise ValueError("Roof alignment changed other existing metatiles")
    if any(attr[mid*2:mid*2+2] != original_attr[mid*2:mid*2+2]
           for mid in range(512) if mid not in NEW_METAS):
        raise ValueError("Roof alignment changed unrelated terrain behavior")
    p["meta"].write_bytes(sec)
    p["attr"].write_bytes(attr)
    p["map"].write_bytes(m)
    validate_built(root)
    print("Cuordilava south roof: joined six free east roof cells around "
          "the two original chimney cells, with mirrored 4bpp art; "
          "six unused private metatiles, "
          "zero new tiles, entrances, buildings or collision changes.")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
