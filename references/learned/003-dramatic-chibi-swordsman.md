# Study: Dramatic chibi swordsman with jewel-tone shading

- **source**: user-provided 400x300 screenshot · studied: 2026-07-11
- **true size**: screenshot 400x300; non-background subject bbox 93x114 (display-upscaled pixel art) · **colors**: 26 art/background colors + black · **palette saved as**: not saved
- **subject**: three-quarter-view chibi swordsman with swept hair, scarf, buckler, and glowing blade

## Measurements (from report.json)
- ramps: hair uses 5–7 warm red/pink steps; cloth uses 3–4 blue/violet steps; metal uses dark teal → cyan → near-white
- outline: black/dark plum external outline; analyzer reports 100% dark edge against the flat #313842 background
- dithering: effectively none (0.01%); forms are built with deliberate solid clusters
- value range: 0.0–0.982; very high contrast concentrated at face, hair highlight, and sword edge

## Observations (from LOOKING at zoom.png — pixel-level, specific)
- The head/hair mass is oversized and asymmetrical, roughly half the visible character height before the cast shadow.
- Hair silhouette uses large stepped spikes and one lifted rear tuft; highlights are 2–4 connected warm clusters, never scattered noise.
- Face is a small pale wedge partially occluded by fringe; a few dark pixels imply the eye rather than drawing a full face.
- Torso is narrow and dark, while scarf, buckler rim, hair, and cyan blade create four strong silhouette breaks.
- Shadow hues move toward navy/purple; highlights move toward salmon/peach, producing richer volume than straight RGB darkening.
- The sword is deliberately brighter than every other material: dark border, teal body, pale cyan core, near-white glint.
- Limbs overlap in a compact three-quarter stance; near limbs use brighter ramps and far limbs collapse into purple-black masses.
- A broad irregular cast shadow grounds the small feet and prevents the dark lower costume from floating.

## Rules to apply (imperative — used when creating in this style)
- Build a 40–56px heroic-chibi sprite with head+hair occupying about 38–45% of body height.
- Start with an asymmetrical silhouette: swept hair, trailing cloth, shield/guard, and weapon must each break the body contour.
- Use a shared black-plum outline and cool violet/navy shadows; reserve warm highlights for skin/hair and cyan-white for steel.
- Shade with 2–4 connected clusters per material under a top-left light; avoid single-pixel texture noise.
- Keep facial information minimal and high contrast beneath the fringe.
- Make the weapon the brightest object and outline it cleanly so its direction reads at 1x.
- Offset near/far legs and arms in value as well as position to preserve the three-quarter view.
- Add a compact irregular cast shadow beneath the feet for presentation previews, but omit it from engine sprites if requested.

## Do NOT copy
- Do not reproduce the source character's exact hair, scarf, shield, costume, or pose pixel-for-pixel.
- Do not inherit screenshot background pixels or treat display-upscaled blocks as the native grid.
- Do not spend the full 27-color screenshot palette; target 14–18 purposeful colors for a new animated character.

