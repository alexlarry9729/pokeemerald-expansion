# Cyberpunk Hoenn — Lavaridge visual direction

## Reference target

Use the supplied cyberpunk town image as the mood and density reference, adapted to the existing top-down Pokémon Emerald tile scale rather than copying its isometric perspective.

- **Architecture first:** rework complete building fronts, roof silhouettes, windows, vents, pipes, door surrounds and corner details. Neon signs alone are not a substitute for redesigned buildings.
- **Volcanic base:** charcoal basalt, dark iron, warm stone edges, steam and hot-spring water. Keep walkable paving and water boundaries clearly readable.
- **Light hierarchy:** lava-orange / furnace-red is the primary light family; cyan is the cool counterpoint; magenta is reserved for a smaller number of premium signs and trims.
- **Day and night:** neon elements must remain visible during daylight, but use a lower-energy palette and normal sprite rendering. At night, use the vivid palette and blend mode. Avoid washing out the terrain or obscuring collision-relevant edges.
- **Living town:** retain the contrast of palms, dense planting, flowers, waterfalls and thermal pools against metal and stone. These are important parts of the reference, not filler to remove.

## Implementation order

1. Complete Lavaridge as the pilot: building facades and roof/window tile art, industrial pipe details, palette assignment, then controlled placement in the town map.
2. Preserve every existing warp, connection, sign, hidden item, trigger, NPC and collision/metatile attribute unless a deliberate and separately tested layout change is needed.
3. Run `python3 tools/validate_cyberpunk_assets.py`, then the repository CI build. Inspect Lavaridge in an emulator during daytime and at night; the automated palette checks do not replace this visual test.
4. Only after the pilot is visually and functionally approved, port the same art language to other Hoenn towns with local colour variations.

## Current scope and caveat

The current branch establishes the day/night light-sprite behaviour, map sign-light placements and the start of palette work. The warmed orange palette is a lighting refinement, **not** a complete architectural tileset redesign. The pilot should not be marked visually complete until the facade/roof/window tiles are substantially reauthored and an in-game screenshot confirms the result.
