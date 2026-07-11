# Study: Tactical chibi with layered cloth and painterly clusters

- **source**: user-provided Final Fantasy Tactics style reference screenshot · studied: 2026-07-11
- **true size**: 900x397 screenshot; analyzer estimate 150x66 at ~6x display scale · **colors**: resampling inflated to 2,659+; reduce deliberately · **palette saved as**: not saved
- **subject**: hooded silver-haired tactical character shown as portrait and three-quarter field sprites

## Measurements (from report.json)
- ramps: dominant purple-black cloth, warm beige/gold trim, neutral silver hair, pale warm skin, brown boots, small blue-violet accent
- outline: near-black brown/purple silhouette outline; white screenshot background makes automatic edge statistic unreliable
- dithering: essentially none as an authored technique; screenshot resampling creates false intermediate colors
- value range: full 0–1 due black outline and white background; field sprite keeps midtones compressed and reserves white for hair glints

## Observations (from LOOKING at zoom.png — pixel-level, specific)
- Field sprite uses a 3/4 tactical view: face points diagonally, near shoulder/hand/boot are larger and brighter than far-side parts.
- Proportions are super-deformed but not infant-like: head+hood is ~45% of standing height, torso short, legs stubby, hands and boots oversized.
- Hood is the primary silhouette mass, with a deep rear wedge; silver fringe creates three stepped spikes that cross the face contour.
- Costume readability comes from nested bands: dark cloak mass → warm gold edge trim → pale inner shirt/armor → brown boot masses.
- Gold trim is usually 1–2 native pixels wide and follows structural seams; it separates overlapping dark garments without excessive internal outlines.
- Hair uses strong neutral value steps and small warm reflected shadows, avoiding pure grayscale flatness.
- Face is extremely economical: a pale vertical plane, one red/dark eye mark, and a short nose/mouth cluster.
- Near fist and near boot are deliberately enlarged; perspective is conveyed through scale, overlap, value, and position together.
- The sprite is vertically compact but silhouette breaks at fringe, elbow/fist, cloak tail, weapon, and boots keep it readable.
- A later construction test exposed an important failure mode: reducing far-side anatomy too aggressively makes an eye or arm appear missing rather than foreshortened.

## Rules to apply (imperative — used when creating in this style)
- Design field characters at 32–48px native height in a consistent 3/4 tactical view.
- Set headgear+head to 40–48% of standing height; use short torso/legs and oversized near hand/boot.
- Build five large masses first: headgear, hair/face, torso garment, near arm/hand, and separated boots.
- Use near-black purple/brown outlines, then insert 1px warm trim along selected garment seams to clarify layers.
- Shade each material with 3–4 intentional cluster colors; shift cloth shadows toward violet, skin toward muted rose, and metal/hair highlights toward warm ivory.
- Keep the far-side limbs darker, smaller, and partially occluded; keep near-side parts brighter and 1–2px larger.
- Keep paired anatomy explicitly readable in 3/4 view. Unless the pose intentionally hides it, show both eyes, both arms/hands, and both legs/feet as distinct clusters.
- Draw the far eye as a compact 2–3px cluster after repainting hair/fringe; a lone dark pixel at a hair boundary reads as shadow, not an eye.
- Draw the far arm as its own sleeve+hand mass behind the torso. Make it smaller/darker than the near arm, but preserve a visible silhouette break or interior boundary.
- Break the silhouette with 3–5 purposeful features only; do not fill the interior with decorative noise.
- For animation, keep the body anchor stable while exaggerating hand, boot, hood-tail, and weapon overlap changes.

## Do NOT copy
- Do not reproduce the reference character's exact hood, silver fringe, red eyes, gold piping pattern, or weapon.
- Do not preserve thousands of resize/interpolation colors; rebuild with a hard 14–18 color budget.
- Do not outline every garment seam; alternate dark overlap edges with warm trim so the sprite remains readable rather than wired.
- Do not use hair, hood, or torso overlap to accidentally erase paired facial features or limbs.

