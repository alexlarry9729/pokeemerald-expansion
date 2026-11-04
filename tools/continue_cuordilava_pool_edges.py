#!/usr/bin/env python3
"""Join the west hot-spring rock boundary to the existing north/east stones.

The previous exterior waterfall repair left three original western cliff
cells as featureless mountain-wall textures. Reuse the already-authored
NORTH rim rock caps and the EAST wall's dry rock feet, with horizontal
mirror flags. Behind them retain a real, dark, pre-existing mountain
underlay (instead of old yellow mineral sand).

This edits ONLY three town-private metatiles' four bottom and top art
entries. Map, attributes, collision, events, animated water, and all 512
GBA character images remain completely unchanged.
"""
from pathlib import Path
import struct

WEST = {161: (2, 3), 509: (2, 4), 511: (2, 5)}
NORTH_RIM = 154    # (3, 2): existing granite crest
EAST_RIM = 165     # (7, 3) and (7, 4): existing granite edge
DRY_CLIFF = 114   # shared mountain wall, source for the dark lower layer
HFLIP = 0x0400
PALETTE_WATER_ROCK = 8
PALETTE_MOUNTAIN = 10


def read16(buf, offset):
    return struct.unpack_from("<H", buf, offset)[0]


def paths(root):
    root = Path(root)
    return (
        root / "data/layouts/LavaridgeTown/map.bin",
        root / "data/tilesets/secondary/cuordilava/metatiles.bin",
        root / "data/tilesets/secondary/cuordilava/metatile_attributes.bin",
        root / "data/tilesets/secondary/cuordilava/tiles.png",
    )


def places(layout, mid):
    return {(pos % 20, pos // 20) for pos in range(400)
            if (read16(layout, pos * 2) & 1023) == 512 + mid}


def intended_graphics(metas):
    """Splice existing 8x8 rock silhouettes; no new atlas pixels or colors."""
    north = struct.unpack_from("<8H", metas, NORTH_RIM * 16)
    east = struct.unpack_from("<8H", metas, EAST_RIM * 16)
    dark = struct.unpack_from("<8H", metas, DRY_CLIFF * 16)
    # top: the two mirrored northern stone caps; bottom: the two
    # established eastern-side dry rock feet, continuing down the cliff.
    # Upper junction keeps the already present north-west crest. The lower
    # two west-wall panels instead reuse the EXISTING east rock feet with
    # alternate north-rock caps; copying the same crest everywhere created
    # three disconnected stone squares along the left of the pool.
    upper = (north[5], north[4], east[6], east[7])
    # The upper overlay characters of EAST_RIM include actual turquoise
    # pool pixels and cannot be mirrored onto the dry west bank. Compose
    # only from the audited dry north caps and east rock feet instead.
    side = (north[4], north[5], east[7], east[6])
    # An upright lower corner must meet the existing SOUTH rim; turning
    # the middle panel vertically upside-down created isolated, seemingly
    # floating white stones at the southwest bend. Use four upright,
    # bank-owned rock pieces instead, with staggered light/dark courses.
    southwest = (north[5], east[7], east[6], north[4])
    if any((item >> 12) != PALETTE_WATER_ROCK
           or not 512 <= (item & 1023) < 1024
           or item & 0x0c00 for item in (*upper, *side, *southwest)):
        raise ValueError("Existing pool stone donors no longer have clean palette-8 rock tiles")
    if any((item >> 12) != PALETTE_MOUNTAIN for item in dark[:4]):
        raise ValueError("Original dark mountain backing palette was changed")
    if any(item & 0x0c00 for item in dark[:4]):
        raise ValueError("Unexpected flipped lower-level mountain donor")
    backing = tuple(dark[:4])
    return {
        161: backing + tuple(item ^ HFLIP for item in upper),
        509: backing + tuple(item ^ HFLIP for item in side),
        # Turn the lower bank's dry cap over so its geological seam does
        # not reproduce the middle cell's perfectly repeated outline.
        511: backing + tuple(item ^ HFLIP for item in southwest),
    }


def validate_built(root):
    layout_path, meta_path, attr_path, atlas_path = paths(root)
    layout, metas, attrs = (p.read_bytes() for p in
                            (layout_path, meta_path, attr_path))
    if (len(layout), len(metas), len(attrs)) != (800, 8192, 1024):
        raise ValueError("Thermal edges altered Cuordilava's fixed 20x20 / 512-metatile budget")
    if places(layout, NORTH_RIM) != {(3, 2)}:
        raise ValueError("Upper-left original thermal stones are no longer in place")
    if places(layout, EAST_RIM) != {(7, 3), (7, 4)}:
        raise ValueError("Right-hand original thermal stones are no longer in place")
    if (1, 3) not in places(layout, DRY_CLIFF):
        raise ValueError("Dark mountain backing is no longer adjacent to the west pool")
    from render_cuordilava_preview import png_indexed
    width, height, pixels = png_indexed(atlas_path)
    if (width, height) != (128, 256):
        raise ValueError("Pool bank extended the fixed GBA indexed atlas")
    expected = intended_graphics(metas)
    for mid, xy in WEST.items():
        if places(layout, mid) != {xy}:
            raise ValueError(f"West edge {mid} is reused outside its protected cliff cell")
        old_behaviour = read16(attrs, mid * 2)
        raw = read16(layout, 2 * (xy[1] * 20 + xy[0]))
        if (raw >> 10) & 3 != 1 or old_behaviour != 0x1000:
            raise ValueError(f"West edge {xy} no longer has its original blocking mountain behaviour")
        actual = struct.unpack_from("<8H", metas, mid * 16)
        if actual != expected[mid]:
            raise ValueError(f"Western pool metatile {mid} is not joined to the north/east rock border")
        for entry in actual[4:]:
            tid = (entry & 1023) - 512
            tx, ty = (tid % 16) * 8, (tid // 16) * 8
            seen = {pixels[ty + dy][tx + dx] for dy in range(8) for dx in range(8)}
            if seen & {1, 9, 10, 11, 12, 13, 14, 15}:
                raise ValueError(f"West rock edge {mid} has white foam, turquoise, or gold pixels")
    return True


def run(root):
    root = Path(root)
    map_path, meta_path, attrs_path, atlas_path = paths(root)
    before_map = map_path.read_bytes()
    before_attrs = attrs_path.read_bytes()
    before_atlas = atlas_path.read_bytes()
    original = meta_path.read_bytes()
    if (len(before_map), len(original), len(before_attrs)) != (800, 8192, 1024):
        raise ValueError("Expected the completed, fixed-size private town tileset")
    expected = intended_graphics(original)
    edited = bytearray(original)
    for mid, xy in WEST.items():
        if places(before_map, mid) != {xy}:
            raise ValueError(f"Cannot safely replace shared western cliff {mid}")
        struct.pack_into("<8H", edited, mid * 16, *expected[mid])
    for mid in range(512):
        if mid not in WEST and edited[mid*16:(mid+1)*16] != original[mid*16:(mid+1)*16]:
            raise ValueError("Thermal edge change escaped its three designated metatiles")
    meta_path.write_bytes(edited)
    validate_built(root)
    if (map_path.read_bytes() != before_map
            or attrs_path.read_bytes() != before_attrs
            or atlas_path.read_bytes() != before_atlas):
        raise ValueError("Thermal edge pass changed map, collision or original rock graphics")
    print("Cuordilava pool: north-west crest continues into a mirrored eastern stone sidewall; "
          "water, geometry, tile graphics and collision remain unchanged")


if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1])
