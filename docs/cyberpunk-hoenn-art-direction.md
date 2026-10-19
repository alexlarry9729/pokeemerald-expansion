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

The architecture pass rebuilds the large four-metatile roof as a continuous iron roofline with left/right edge caps, two differently ribbed service panels, and a custom raised roof cap with twin exhausts. Four town-exclusive roof-corner/edge metatiles (72, 73, 74, 77) now carry matching dark-iron eave overlays with rivets, cyan maintenance lamps and furnace-red seams, tying the roof silhouette into the facade modules without repainting their underlying walkable or collision data. A low ventilation intake spans two adjacent instances of town-exclusive metatile 285 with ribbed steel slats and amber/cyan status lights; the source roof base and cell attributes remain unchanged. The separate rooftop metatile 162 now has an offset single-stack exhaust with its own glowing heat slots, so the adjacent roof silhouette no longer relies on the stock blank overlay. Other custom elements include paired illuminated windows, a service hatch, a louvered ventilation wall, a furnace awning, a hot-core machine facade, an industrial corner/conduit and a thermal exchanger service panel. All use reserved palette 6 for daytime structure and controlled orange/cyan accents; palette 15 is the brighter night companion. Cuordilava uses a layout-scoped background grade at palette-load time and reapplies that grade after the engine blends ordinary day/night palettes. It turns the source magenta toward furnace-wine, cyan toward dark teal, and neutral surfaces toward charcoal without modifying shared palette files or any other map. Reserved palette 6 is exempt so the custom architecture remains readable; palette 15 is its stronger nighttime companion. The eleven architectural metatiles (75, 76, 78, 79, 165, 170, 173, 174, 179, 181, 187) and rooftop metatiles 162 and 163 are validated as Cuordilava-specific. The two rooftop variants use secondary-only indexed tiles and palette 6; both existing metatile definitions retain their original attribute bytes. Only overlay slots 4–7 of metatile 162 are replaced; slots 0–3, the layout's cell placements, and the collision attribute byte are retained. Shared metatile 50 remains unchanged because validation found it is also used by Mt. Chimney. Shared palette files 07/08 and all other town map objects remain unchanged. Legacy palette-6 entries used by original Lavaridge metatiles are remapped to palette 13, a byte-for-byte copy of original palette 06, so other maps retain their original colours. Only the custom architectural slots listed by the validator use the private palette 6 daytime ramp and palette 15 night companion. Original palettes 05 and 12 are restored to their master values. The original LavaridgeTown layout binary is retained so cell placement, collision semantics, warps and walkable routes do not change; the art pass modifies only tiles and visual entries in verified town-specific metatiles.

## Current scope and caveat

The redesign now changes real architectural tile art and the active town metatiles rather than recolouring shared palette files. A local day/night palette pair is reserved for the custom building pieces. Global Lavaridge palettes 07 and 08 have been restored to master values, and unrelated city map-event JSON files have been restored so sign-light additions remain specific to Cuordilava.

The work preserves map geometry, collision/metatile-attribute bytes, warps, object events, signs and triggers. The custom architecture remains modular: existing building footprints are retained while roof edges, windows, vents, hatches, furnace panels and conduits acquire a consistent iron/charcoal, furnace-orange and cyan visual language.

Do not mark the town visually complete solely on successful compilation. The final candidate must pass the full validator and ROM build, then be reviewed in the target emulator for both daytime and nighttime; any remaining tile seams or map-specific overlap should be corrected before release.



The ROM artifact workflow also renders two layout-only PNGs from the current map, primary/secondary tile atlases and JASC palettes. These previews reproduce the custom BG colour-grade and private day/night palette, but intentionally omit NPC/event sprites, shadows, weather and emulator effects; they are a fast map-layout review, not a substitute for in-emulator verification.


## Reference-driven palette pass — 2026-10-19

The supplied city reference is a mood and density target, adapted to the existing GBA top-down tiles rather than copied literally. The visual hierarchy is deliberately constrained:

- **Primary:** charcoal/iron structure with furnace red and incandescent orange on windows, seams and vents.
- **Secondary:** low-energy teal service LEDs; cyan must not dominate the ground or the building faces.
- **Night:** brighten the accent ramp while keeping structural indices 1–8 dark; the night palette is still blended only for the Cuordilava layout.
- **Scope:** this pass changes only the private palette 6 / night companion 15 used by Cuordilava's custom metatiles. Shared Lavaridge palettes and global RGB grading remain untouched.
- **Regression guard:** the asset validator now checks that palette 6/15 warm accents stay red/orange-led and that the teal accent ramp remains restrained.
