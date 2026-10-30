#!/usr/bin/env python3
"""Calm the original mineral basin without repainting its boundary or terrain.

Runs after foam polishing, but touches ONLY the three proven-isolated town
private 8x8 water characters 320/321/336. Pool dimensions, metatiles, source
water palette, animation, collision, warps and rocks remain unchanged.

The old pool was visually speckled with repeated white foam. These three
8x8 motifs instead build smooth broad turquoise channels, with a few short,
connected hot-mineral reflections and genuine deep-water shadows.
"""
from pathlib import Path

from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png
from refine_cuordilava_water import assert_spa_tile_isolation

WATER_TILES = (320, 321, 336)
# Three distinct calm water textures; '1' is white foam, '9' luminous
# turquoise and 'A' deeper turquoise (indexed colour 10). Each symbol is
# exactly one GBA pixel, not a rendered RGB colour.
DESIGN = {
    320: (
        '99999999',
        '9999AAAA',
        '99A999AA',
        '99119999',
        '99999999',
        'AAA99999',
        '999AAAA9',
        '99999999',
    ),
    321: (
        '99A99999',
        '9AAA9999',
        '99999999',
        '999AA999',
        '99911A99',
        '99999999',
        '9999AAAA',
        '99999999',
    ),
    336: (
        '99999999',
        '999A9999',
        '9AAAA999',
        '99999999',
        '99999119',
        '99999999',
        'AAA99999',
        '99999999',
    ),
}
PAINT = {'9': 9, 'A': 10, '1': 1}
assert set(DESIGN) == set(WATER_TILES)


def tile_region(tid):
    return (tid % 16) * 8, (tid // 16) * 8


def validate_built(root):
    root = Path(root)
    references = assert_spa_tile_isolation(root)
    if set(references) != set(WATER_TILES):
        raise ValueError('The original pool-owned GBA tile IDs were displaced')
    atlas = root / 'data/tilesets/secondary/cuordilava/tiles.png'
    w, h, pix = png_indexed(atlas)
    if (w, h) != (128, 256):
        raise ValueError('Invalid indexed town-only 4bpp water atlas')
    for tid, lines in DESIGN.items():
        ox, oy = tile_region(tid)
        if len(lines) != 8 or any(len(row) != 8 for row in lines):
            raise ValueError('The new water currents must remain exactly 8x8')
        actual = [pix[oy+y][ox+x] for y in range(8) for x in range(8)]
        # Unmodified bank pixels can be retained, but on actual water pixels
        # expect a strong majority of smooth blue, and sparse white ribbons.
        counts = {c: actual.count(c) for c in (1, 9, 10)}
        if counts[9] < 30 or counts[10] < 8 or not 1 <= counts[1] <= 7:
            raise ValueError(f'Water {tid}: texture/foam balance lost {counts}')


def run(root):
    root = Path(root)
    references = assert_spa_tile_isolation(root)
    if len(references) != 3 or any(not coords for coords in references.values()):
        raise ValueError('Pool-water graphics lost their isolated uses')
    atlas = root / 'data/tilesets/secondary/cuordilava/tiles.png'
    w,h,pix = png_indexed(atlas)
    if (w,h) != (128,256):
        raise ValueError('Run only after the post-scenery atlas generation')
    source = atlas.read_bytes()
    plte = source[source.index(b'PLTE')+4:source.index(b'PLTE')+52]
    if len(plte) != 48:
        raise ValueError('Not a valid 16-colour GBA palette')
    before = [row[:] for row in pix]
    changed = 0
    for tid, lines in DESIGN.items():
        ox,oy = tile_region(tid)
        for y in range(8):
            for x in range(8):
                former = pix[oy+y][ox+x]
                if former not in (1,9,10):
                    continue  # mineral stones and transparent banks preserved
                new = PAINT[lines[y][x]]
                if former != new:
                    pix[oy+y][ox+x] = new
                    changed += 1
    if changed < 35:
        raise ValueError(f'New thermal water currents not applied: {changed=}')
    # Exact scope: all original pixels outside these three 8x8 characters
    # remain byte-for-byte untouched, not even another town graphics tile.
    changed_tiles = set(WATER_TILES)
    for y in range(h):
        for x in range(w):
            if (x//8 + (y//8)*16) not in changed_tiles:
                if pix[y][x] != before[y][x]:
                    raise ValueError('New mineral currents repainted unrelated city art')
    write_png(atlas,w,h,pix,plte)
    validate_built(root)
    print(f'Cuordilava thermal pool: {changed} water/foam pixels reshaped into '
          'three coherent turquoise flow motifs; original rim and map safe')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
