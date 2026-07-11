# Study: Tall tactical job sprites with elongated heroic anatomy

- **source**: user-provided class/job sprite lineup · studied: 2026-07-11
- **true size**: 540x617 screenshot; estimated ~2x resampled display, 270x308 working grid · **colors**: resampling inflated to 19k+; rebuild with a hard budget · **palette saved as**: not saved
- **subject**: fifteen humanoid fantasy jobs/classes with armor, robes, hats, and distinct silhouettes

## Measurements (from report.json)
- ramps: each job centers on one dominant hue family (red, green, cyan, violet, ivory) plus shared skin, leather, metal, and near-black outline ramps
- outline: dark brown/charcoal external contour with selective colored interior edges; automatic edge statistic is unreliable against baked gray background
- dithering: effectively none as an authored sprite technique; observed intermediate colors mostly come from screenshot resampling
- value range: near-black to near-white; brightest values reserved for polished armor, cloth trim, hair, and focal emblems

## Observations (from LOOKING at the supplied lineup)
- Characters are taller than conventional 32px chibi: roughly 4–5 heads high, with a compact head, readable torso, and visibly extended thigh/shin regions.
- Estimated native field sprites occupy about 28–38px width and 52–64px height before oversized hats or weapons.
- The shoulder line is broad enough to carry armor class identity, while the waist narrows and the legs separate clearly below the pelvis.
- Hands and boots remain slightly oversized relative to realistic anatomy, preserving action readability even though the overall figure is elongated.
- Each job reads through one dominant silhouette device: horned helmet, asymmetric pauldron, winged helm, pointed hat, long coat, hood, or robe hem.
- Armor is assembled as overlapping plates with alternating dark gaps and bright rim clusters; cloth classes use long vertical coat/robe panels to emphasize height.
- Most figures use a 3/4 front view: near shoulder/hand/knee/boot are larger and brighter; far limbs are offset, darker, and partially occluded but never missing.
- Heads are small enough to look heroic but retain enlarged hair/hat clusters and minimal 2-eye facial marks.
- Color variants share construction grammar: one saturated job color, a darker hue-shifted shadow, a bright trim, neutral metal/leather, and a shared outline.
- Long vertical highlight paths on coat edges, greaves, and robe panels reinforce the taller proportion.

## Rules to apply (imperative — used when creating in this style)
- Use the `tall tactical` proportion preset: 48–64px body height, approximately 4–5 heads tall.
- Budget vertical anatomy before drawing: head/headgear 18–24%, torso 25–30%, pelvis 8–12%, legs+boots 35–42%, with remaining pixels for margins.
- Keep shoulders 1.6–2.0 head-widths, narrow the waist, and separate both legs for at least the lower third of the body.
- Preserve slightly oversized hands and boots; elongated does not mean realistic or thin at every joint.
- Design one unmistakable job silhouette feature and 2–3 secondary material cues; do not rely on tiny internal decorations.
- Build armor from large plate clusters first, then add 1px rim highlights and dark overlap gaps; build robes from long tapered panels with vertical highlight paths.
- Maintain the 3/4 anatomy rule: both eyes and all paired limbs remain accounted for, with far-side forms smaller/darker rather than absent.
- Use a 14–20 color budget per character and share outline, skin, leather, and metal ramps across a cast.
- For animation, use a stable ground pivot and allow tall canvases or oversized action canvases; never compress a long body or weapon back into a 32px chibi cell.
- Validate at native 1x that the head, torso, pelvis, knees, and boots remain separately readable.

## Do NOT copy
- Do not reproduce any exact armor set, helmet, robe pattern, character, or class insignia from the reference.
- Do not treat resampled antialias colors or the gray screenshot background as palette colors.
- Do not apply this tall preset to every request automatically; retain compact chibi and heroic-chibi presets as intentional alternatives.
- Do not increase height by stretching pixels or scaling an existing chibi vertically; redraw the anatomy with new joint positions and cluster shapes.

