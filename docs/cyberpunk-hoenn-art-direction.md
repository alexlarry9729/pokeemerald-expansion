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

The current incremental art pass reworks five Cuordilava-only metatiles into illuminated industrial windows, a furnace control panel, a service hatch with cyan conduit indicators, a louvered thermal vent, and a pipe/conduit insert. It also restyles the four overlay tiles of the Cuordilava-only metatile 50 into a repeatable dark-iron fascia with furnace slats and restrained cyan service lights, while retaining the original four base tiles and the original metatile attribute/collision byte. The art uses reserved atlas tiles with palette 08 and a transparent overlay layer, keeping the established day/night palette workflow intact. The five custom metatile definitions (165, 173, 174, 179 and 181), plus fascia metatile 50, were checked against all layouts that share the Lavaridge tileset; they are used by Cuordilava only. Map geometry, collision/metatile attributes, warps, object events and triggers are not changed by this art pass. The validator now guards the exact tile/palette wiring and checks that these metatiles are not reused by other shared-tileset layouts.

## Current scope and caveat

The current branch establishes the day/night light-sprite behaviour, map sign-light placements and an early architectural-detail pass in the Cuordilava/Lavaridge tileset. The active secondary tiles include warm window/panel pixels, dark window mullions, a furnace-orange roof seam and restrained cyan service lights on conduit pieces; the asset validator checks that these tile IDs are actually referenced by the town layout instead of passing on unused atlas tiles.

The Lavaridge tileset now declares `SWAP_PAL(8)`, so the facade palette in `08.pal` blends toward its `01.pal` companion at night. The paired palette keeps the structural tones controlled while strengthening the cyan highlight and warm orange/red ramp after dark. Object sign-lights also retain their separate subdued-day / vivid-night sprite palettes. The architectural surfaces using palette `07.pal` now use a charcoal/iron structural ramp with amber, furnace-orange and red highlights; the magenta-heavy structural tones were removed from that building palette while cyan remains the cool counterpoint.

This is still **not** a complete architectural tileset redesign. The current changes are local detail accents, not replacement silhouettes for every roof, facade, chimney and structure in the reference. Keep the existing map geometry and access events intact while the artwork is expanded. The automated checks cover indexed PNG integrity, palette/mask structure, day/night palette intensity, active facade pixels, light-sprite wiring and key map access invariants.

Do not mark the pilot visually complete until the larger facade/roof/window redesign is in place and screenshots from a compiled build have been inspected in an emulator in both daylight and night conditions. A successful palette validator alone is not sufficient.
