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
- **Glow-mask invariant:** for every index listed in `data/tilesets/secondary/cuordilava/palettes/08.pla`, the paired night value in `01.pal` must be brighter than the daytime value in `08.pal`; the asset validator checks the full mask, not only selected colours.
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

- **Secondary tileset isolation:** `LAYOUT_LAVARIDGE_TOWN` now uses a dedicated copy at `data/tilesets/secondary/cuordilava/` for Cuordilava's industrial metatiles, tiles and day/night palette. The shared `data/tilesets/secondary/lavaridge/` files used by Route 112, Mt. Chimney, Jagged Pass, Fiery Path and Magma Hideout remain at the upstream baseline and are guarded by the asset validator.

The supplied city reference is a mood and density target, adapted to the existing GBA top-down tiles rather than copied literally. The visual hierarchy is deliberately constrained:

- **Primary:** charcoal/iron structure with furnace red and incandescent orange on windows, seams and vents.
- **Secondary:** low-energy teal service LEDs; cyan must not dominate the ground or the building faces.
- **Night:** brighten the accent ramp while keeping structural indices 1–8 dark; the night palette is still blended only for the Cuordilava layout.
- **Scope:** Cuordilava's layout uses a private primary/general palette set under `data/tilesets/primary/cuordilava`, while reusing the existing primary tiles, metatiles and collision attributes. Only the town layout selects the new palette set. The private secondary palette 6 / night companion 15 remains reserved for custom architecture; shared Lavaridge palettes and global RGB grading remain untouched. Companion banks 10–14 provide a brighter night pass for the primary stone, path and facade colours.
- **Regression guard:** the asset validator now checks that palette 6/15 warm accents stay red/orange-led and that the teal accent ramp remains restrained.

## Pixel-art fixture pass (2026-10-19)

The facade-light object now uses a dedicated 16×16 indexed pixel-art fixture: dark iron mounting, a vertical incandescent red/orange core, and a single restrained teal status light. The existing day/night object palettes still control its luminosity, so the sprite art is shared while the daytime ramp stays subdued and the nighttime ramp becomes vivid. The preview renderer composites these actual light-object sprites at their authored town coordinates and chooses the corresponding object palette for each preview; it still intentionally omits NPCs, weather, shadows, and engine effects. This improves visual review without changing town coordinates, warps, collision attributes, or the event anchor placements.

## Rifinitura della gerarchia cromatica diurna (2026-10-19)

Le due rampe primarie locali che controllano i dettagli caldi sono state ulteriormente attenuate di giorno: i toni rosso-arancio rimangono riconoscibili, ma la loro luminanza è più contenuta sulle superfici estese. Le companion notturne restano più brillanti, così l'effetto di fornace si concentra maggiormente su finestre, bordi e condotti al calare della luce. La modifica riguarda solo `data/tilesets/primary/cuordilava/palettes/03.pal` e `05.pal`; non modifica palette condivise, coordinate della mappa o attributi dei metatiles.

## Refinement pass: magma furnace windows and industrial roofs (2026-10-21)

This pass uses the supplied Lavaridge/Cuordilava volcanic cyberpunk reference as an *art-direction target*, not an importable GBA map. It changes indexed pixel artwork in `data/tilesets/secondary/cuordilava/tiles.png`, while retaining its original dimensions (128×232), palette-indexed 4bpp format, transparency index and existing metatile placement.

- Reinforce red furnace glints in the four repeated building-face modules, thermal panels, window banks and roof bulkheads.
- Replace selected high-energy cyan control-panel highlights with hot red/orange, keeping the teal LEDs as a restrained secondary signal.
- Introduce tiny incandescent accents in rooftop corners, ventilation-intake grilles and service conduits without redrawing their silhouettes or transparency edges.
- Preserve the window mullions, cooling-pipe status LEDs and palette-6 industrial metatile references protected by `tools/validate_cyberpunk_assets.py`.
- The town map's `map.bin`, collision data, warp points, NPC positions, primary tileset and all globally shared tilesets are unchanged.

**Review gate:** re-run the dedicated asset validator and Pokémon Emerald build, then inspect both day/night previews and test walkability, signs, warm/cool contrast and tile layering in an emulator before calling the city finished. CI build success is necessary but not a complete in-game visual review.

## Correzione delle anteprime delle terme (2026-10-21)

Le palette GBA della mappa non vanno selezionate in base all'origine grafica della tile: gli slot 0–5 sono caricati dal tileset primario, mentre gli slot 6–15 provengono dal secondario. Alcuni metatile delle terme usano grafica primaria con palette secondaria 8; la vecchia scelta per origine della tile li mostrava falsamente neri. `tools/render_cuordilava_preview.py` ora sceglie lo slot effettivamente caricato dal motore e il validatore verifica l'instradamento delle palette sia di giorno sia di notte. È una correzione alle anteprime diagnostiche; le risorse grafiche, la mappa e la ROM rimangono inalterate da questo specifico intervento.

## Separazione reale tra giorno e notte (2026-10-21)

Le precedenti anteprime mostravano un falso night pass per i banchi primari: la palette alternativa era renderizzata, ma `gTileset_CuordilavaGeneral` non aveva i `swapPalettes` abilitati in-game. La città ora attiva i banchi primari 1–5 nel proprio tileset isolato, usando le companion 10–14 a seconda del blend temporale del motore. Di giorno metallo, basalto e strade hanno toni più leggibili; di notte la parte strutturale si oscura, mentre soltanto gli indici emissivi delle finestre, delle tubazioni e delle insegne raggiungono il massimo. La coppia privata secondaria 06/15 segue la stessa regola di contrasto. Il validatore controlla i flag runtime e la gerarchia giorno/notte, anziché imporre (erroneamente) che ogni colore notturno fosse più chiaro. Nessuna modifica a `map.bin`, collisioni, warps, personaggi, mappe esterne o tileset condivisi. La preview rappresenta due condizioni estreme: la transizione oraria effettiva va ancora testata in emulatore.

### Controllo di contaminazione luminosa: strade e tetti

La prima preview del nuovo pass aveva acceso intere strade e superfici dei tetti perché i banchi condivisi di materiali (01/10 e 05/14) usavano la stessa rampa fluorescente delle finestre. L'ispezione delle anteprime ha rivelato il difetto; i banchi 10 e 14 restano ora scuri anche sugli indici 9–14. Il bagliore notturno forte rimane riservato alle palette 03/12, 04/13 e alla coppia industriale secondaria 06/15. Il validatore controlla entrambe le categorie, impedendo che le rampe dei materiali non emissivi diventino neon per errore.

### Intervento sui metatile architettonici (2026-10-21)

Il tileset industriale secondario privato ora incorpora una forma di fiamma incandescente nel pannello-fornace 170/181, una cucitura termica a segmenti nei pannelli metallici 441–444 e piccole spie calore nelle prese di ventilazione 262/263/278/279. L'intervento ridisegna 36 pixel indicizzati nei tile attivamente utilizzati dalla città. È un intervento sulla grafica degli edifici, non una regolazione cromatica. Metatile, dimensioni dei tetti, trasparenze esterne, collisioni, mappa, eventi e porte rimangono invariati; sono da ispezionare entrambe le anteprime e l'emulatore.

## Night accessibility: ambient volcanic visibility (2026-10-21)

The latest in-emulator feedback confirmed that unlit routes and façades disappear into black even though the ROM plays correctly. This pass raises only town-private ambient material colours, separating luminance from actual glowing sources: primary banks 10/11/12/13/14 now preserve a readable mid-dark floor for unlit roofs, stone, pathways and building outlines, and bank 15 recovers depth on dark steel. Daytime material banks 01/02/05 are strengthened where necessary to keep time-of-day contrast, without adding luminous stripes to streets. The bright furnace, lava and neon ramp indices remain allocated to dedicated emissive materials, so night still reads as night. The validator now guards the darkest navigational indices to prevent a regression to near-black values. All warps, map cells, collision attributes, object events and shared non-Cuordilava palettes remain unchanged. A hardware/emulator playtest remains required to tune the practical threshold.

## Industrial roof/facade texture pass (2026-10-21)

The previous city still showed broad flat tiles on the main building roof and standard residential roofing. This pass edits the real, town-private primary indexed atlas `data/tilesets/primary/cuordilava/tiles.png` (128×256, GBA 4bpp palette indices) to add iron ribs, recessed rivets, edge bracing and geometric service struts to roof IDs 248/264/279/280/295/296, to six terraced house roof IDs 162–164/178–180, and to the primary facade trim 340/341/356/357. All changed IDs are used by the current town map; no tile was inserted or removed, and the primary metatile layout and collision attributes remain unchanged. A dedicated validator now checks atlas format, selected roof-rib pixel indices and live town references. This texture pass is still only one stage of the more substantial building-shape redesign needed to match the detailed reference.

## Isolation fix: gym roofs versus hot springs (2026-10-21)

Visual review detected an overlap: the roof pattern applied directly to original General tile IDs 264/280 was visible across hot-spring sand and walkable terrain. The fix reserves **primary tile IDs 400..405** for industrial roof graphics in `data/tilesets/primary/cuordilava/tiles.png`. Their artwork is copied from the modified roofs; the original IDs 248/264/279/280/295/296 are restored byte-for-byte to their previous art. Only a Cuordilava-private copy of the 512-cell General metatile array redirects four existing roof metatiles (281/289/296/297) to the reserved art. The game's tileset header uses the town-private metatile pointer, but still uses **the original General metatile attributes** and original layout map. The diagnostic renderer now reads these cloned primary metatiles, matching the actual ROM. Added a validator to ensure every non-roof metatile remains byte-for-byte identical to General, that only the intended tile slots differ, and that source tile IDs 400..405 do not conflict with original definitions. Shared metatiles and hot-spring terrain are preserved.

## Correzione conflitto tetti primari (2026-10-21)

Il tentativo sperimentale di allocare i nuovi tile 400–405 ai tetti del tileset primario non superava la validazione: gli indici 403 e 404 sono già raggiungibili attraverso metatile attivi. Questo passaggio specifico è stato ritirato, tornando alla grafica e ai riferimenti primari precedenti. Restano attive la correzione della leggibilità notturna nei banchi palette locali, le architetture industriali del tileset secondario e la relativa validazione. Non considerare il passaggio ai tetti primari implementato: prima di riprenderlo occorre riservare slot davvero liberi per entrambi i namespace primario/secondario e verificarne ogni utilizzo nella mappa.

## Seconda revisione della leggibilità notturna (21 ottobre 2026)

A seguito del test della ROM, la prima correzione notturna risultava ancora insufficiente sulle strade e sui contorni non illuminati. Questo passaggio applica il piano A concordato al commit `b5ddc25`: 71 colori ritoccati esclusivamente nelle palette notturne primarie `10.pal`–`14.pal` e nella palette secondaria privata `15.pal`, mantenendo invariati indici 0, palette diurne, emissivi dei banchi 12/13 (9–14) e neon/magma della secondaria (9–15). Il livello base dei materiali non emissivi viene innalzato con passi di +2 fino a +12 RGB, preservando le differenze tra le superfici e la notte. Un ulteriore guard sul pavimento, sulle sagome architettoniche e sull'acciaio impedisce regressioni verso il nero illeggibile; rimangono i controlli che mantengono la notte meno luminosa del giorno e isolano tutte le modifiche dalla altre mappe. Le anteprime sono diagnostiche, non un test in emulatore: solo compilazione, controllo in gioco e feedback sulla navigazione notturna permetteranno di considerarla definitiva.
