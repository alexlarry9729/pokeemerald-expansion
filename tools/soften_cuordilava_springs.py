#!/usr/bin/env python3
"""Finish Cuordilava's isolated mineral-water pixels with small white foam arcs.

The entire original 20x20 town, six entrances, original spring people and
collision data are unchanged. This pass touches only three already isolated
8x8 hot-spring water graphics in the private Cuordilava secondary atlas.
Run LAST, after the 48 landmarks and 23 scenery tiles have been generated.
"""
from pathlib import Path
from render_cuordilava_preview import png_indexed
from apply_cuordilava_industrial_art import write_png
from refine_cuordilava_water import assert_spa_tile_isolation

WATER_TILES = (320, 321, 336)
# A few short linked white-foam highlights rather than unrelated white noise.
HIGHLIGHT_STEPS = ((2, 1), (3, 1), (5, 4), (5, 5), (4, 6))


def cells_for(tid):
    x0, y0 = (tid % 16) * 8, (tid // 16) * 8
    return x0, y0


def run(root):
    root = Path(root)
    if set(assert_spa_tile_isolation(root)) != set(WATER_TILES):
        raise ValueError('Spring graphics are no longer isolated')
    atlas = root / 'data/tilesets/secondary/cuordilava/tiles.png'
    width, height, pix = png_indexed(atlas)
    if (width, height) != (128, 256):
        raise ValueError('Unexpected post-sculpture 4bpp atlas size')
    src = atlas.read_bytes()
    plte = src[src.index(b'PLTE') + 4:src.index(b'PLTE') + 52]
    if len(plte) != 48:
        raise ValueError('Cuordilava indexed palette must have 16 colours')
    changed = 0
    for tid in WATER_TILES:
        x0, y0 = cells_for(tid)
        for x, y in HIGHLIGHT_STEPS:
            # Preserve existing stones and shoreline. Only surface water is
            # eligible for the new shallow glimmer.
            original = pix[y0 + y][x0 + x]
            if original in (9, 10):
                pix[y0 + y][x0 + x] = 1
                changed += 1
        # Keep a deeper turquoise channel below the thin foam highlights.
        for x, y in ((2, 4), (3, 4), (4, 5)):
            if pix[y0 + y][x0 + x] == 9:
                pix[y0 + y][x0 + x] = 10
                changed += 1
    if changed < 6:
        raise ValueError('Unexpectedly sparse hot spring surface; abort art pass')
    write_png(atlas, width, height, pix, plte)
    validate_built(root)
    print(f'Cuordilava springs: {changed} additional mineral ripples / foam pixels; '
          'no changes to map cells, events, metatiles, collision or lighting.')


def validate_built(root):
    root = Path(root)
    positions = assert_spa_tile_isolation(root)
    if any(not v for v in positions.values()):
        raise ValueError('Spring water graphic lost its dedicated cells')
    path = root / 'data/tilesets/secondary/cuordilava/tiles.png'
    width, height, pix = png_indexed(path)
    if (width, height) != (128, 256):
        raise ValueError('Post-pass water graphics have wrong dimensions')
    for tid in WATER_TILES:
        x0, y0 = cells_for(tid)
        sample = [pix[y0 + y][x0 + x] for y in range(8) for x in range(8)]
        if not all(col in sample for col in (1, 9, 10)):
            raise ValueError(f'Water tile {tid} lost its foam or turquoise channels')


if __name__ == '__main__':
    run(Path(__file__).resolve().parents[1])
