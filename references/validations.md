# Validations — the per-iteration critique checklist

Copy this into the critique EVERY loop pass. Answer each line honestly, in writing.
Evidence: preview.png (scale 8–10), silhouette.png, stats() output, zoom() where unsure.

## Silhouette & readability
- [ ] silhouette.png reads as the subject at a glance (species/object/pose identifiable)
- [ ] at preview scale 4 (arm's-length 1x simulation) the subject is still identifiable
- [ ] value contrast separates subject from intended background
- [ ] internal shapes are clusters (3+ px), not noise
- [ ] paired anatomy is accounted for: both eyes/arms/hands/legs/feet are readable, or any hidden part is deliberately occluded by the pose
- [ ] in 3/4 view, far-side features read as smaller/darker forms—not as accidentally missing parts

## Light & color
- [ ] ONE light source; top/lit surfaces lightest, consistent across all parts
- [ ] no pillow shading (darkest shade does NOT hug the outline all around)
- [ ] no banding (shade bands not parallel 1px stripes along the outline)
- [ ] ramps are hue-shifted (shadows cooler, highlights warmer) — not straight darkened
- [ ] colors_used ≤ budget; near_duplicate_colors empty; every color visibly earns its slot

## Craft
- [ ] stats() isolated_px: every entry justified (glint/sparkle) or removed
- [ ] semi_alpha_px == 0 unless intentional alpha-AA
- [ ] outline style uniform (one rule: selout/black/none; weight 1px; light-side handled)
- [ ] curves step smoothly (1,2,3 progressions, no 1,3,1 jumps, no doubled corners)
- [ ] no mixed pixel density (nothing rotated/scaled/pasted at another scale)

## Animation (if animated)
- [ ] contact frames exist; body bob ≤2px; head/secondary parts lag 1 frame
- [ ] timings match the tables in animation.md (or deviation is deliberate & stated)
- [ ] GIF watched ≥3 loops: seam frame N→1 continues motion, nothing pops/skates
- [ ] no dither shimmer on moving parts

## Export (final pass only)
- [ ] 1x master PNG saved; display copies integer-scaled only
- [ ] GIF: bg composite for social OR hard-edged transparency; durations ≥40ms
- [ ] spritesheet JSON frameTags match designed tags; padding set for engine use
- [ ] outputs opened for the user; 1x master path reported

Verdict line: **SHIP / FIX (list)** — if FIX, the list becomes the next edit plan.
