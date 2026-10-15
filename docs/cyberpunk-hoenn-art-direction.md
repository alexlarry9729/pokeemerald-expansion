# Cyberpunk Hoenn — Cuordilava (Lavaridge Town) visual direction

## Italian naming and ROM identifiers

- **Cuordilava** is the Italian name of the town; its internal map identifier stays `LavaridgeTown` and the English ROM may display `Lavaridge Town`.
- **Fiammetta** is the Gym Leader associated with Cuordilava, not the name of the town.
- Keep code paths, map IDs, event scripts and upstream identifiers unchanged unless a technical change explicitly requires it. Use the Italian names in Italian-facing documentation and communication.

## Reference target

Use the supplied cyberpunk town image as the mood and density reference, adapted to the existing top-down Pokémon Emerald tile scale rather than copying its isometric perspective.

- **Architecture first:** rework complete building fronts, roof silhouettes, windows, vents, pipes, door surrounds and corner details. Neon signs alone are not a substitute for redesigned buildings.
- **Volcanic base:** charcoal basalt, dark iron, warm stone edges, steam and hot-spring water. Keep walkable paving and water boundaries clearly readable.
- **Light hierarchy:** lava-orange / furnace-red is the primary light family; cyan is the cool counterpoint; magenta is reserved for a smaller number of premium signs and trims.
- **Day and night:** neon elements must remain visible during daylight, but use a lower-energy palette and normal sprite rendering. At night, use the vivid palette and blend mode. Avoid washing out the terrain or obscuring collision-relevant edges.
- **Glow-mask invariant:** for every index listed in `data/tilesets/secondary/lavaridge/palettes/08.pla`, the paired night value in `01.pal` must be brighter than the daytime value in `08.pal`; the asset validator checks the full mask, not only selected colours.
- **Living town:** retain the contrast of palms, dense planting, flowers, waterfalls and thermal pools against metal and stone. These are important parts of the reference, not filler to remove.

## Implementation order

1. Complete Cuordilava (internal map ID `LavaridgeTown`) as the pilot: building facades and roof/window tile art, industrial pipe details, palette assignment, then controlled placement in the town map.
2. Preserve every existing warp, connection, sign, hidden item, trigger, NPC and collision/metatile attribute unless a deliberate and separately tested layout change is needed.
3. Run `python3 tools/validate_cyberpunk_assets.py`, then the repository CI build. Inspect Lavaridge in an emulator during daytime and at night; the automated palette checks do not replace this visual test.
4. Only after the pilot is visually and functionally approved, port the same art language to other Hoenn towns with local colour variations.

## Cuordilava facade pass (2026-10-15)

The current art pass reworks five Cuordilava-only metatiles into illuminated industrial windows, a furnace control panel, a service hatch with cyan conduit indicators, a louvered thermal vent, and a pipe/conduit insert. It also adds twin exhaust stacks and maintenance LEDs to overlay slots 4–7 of rooftop metatile 163, which is used by Cuordilava. These custom pieces use reserved palette 12 by day and palette 13 at night. Indices 9–15 in the custom palette provide furnace orange/red and cool cyan/teal accents without changing shared route or town palettes. Shared metatile 50 and non-town layouts are not repurposed. Map geometry, collision/metatile attributes, warps, object events and triggers for Cuordilava remain intact.

## Current scope and caveat

The branch keeps the original shared Lavaridge palette colours intact. The original metatile definitions do not use palettes 12 or 13, so this pair is reserved for the five custom Cuordilava architecture metatiles and the town-used rooftop exhaust overlay. The Lavaridge tileset swaps only palette 12 to its palette 13 night companion; existing buildings, paths and the shared Mt. Chimney/Magma Hideout environments continue to use their original palettes.

Sign and facade lights use their dedicated object-event palette pair for subdued daylight and stronger nighttime colours. Added light events are confined to Cuordilava; map JSON for other towns is not part of this feature. Validation checks that palettes 07/08 remain at baseline, that local palette 12/13 has a readable day/night ramp, that active custom art references the reserved pair, and that the town's access events remain intact.

This is still an incremental architectural pass, not yet a complete replacement of every roof and facade from the reference. Do not mark the town visually complete until a fresh compiled ROM has been inspected in an emulator in both daylight and night conditions.

