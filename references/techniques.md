# Techniques — color, shading, dithering, AA, outlines, texture

## Color ramps (the foundation)

A ramp = 3–5 shades of one material, dark→light. NEVER straight-darken:
- shadows shift hue toward **cool** (blue/purple), highlights toward **warm** (yellow).
- hue shift 10–25° per ramp; saturation peaks at midtone, drops in highlights.
- value steps 15–25% apart — steps too close = mud, invisible at 1x.

`ramp("#b13e53", 5)` implements exactly this. `ramp(..., hue_shift=25)` for vivid/fantasy,
`hue_shift=8` for muted/realistic. Materials can share their darkest shade (also the selout
color) to save palette slots.

## Shading

- Pick ONE light source; default top-left 45°. Top faces = lightest, bottom/right = shadow.
- **Cel shading** (default): base + 1 shadow band + 1 highlight band. Hard edges.
- **Soft shading**: same bands, then dither ONLY the band border, a 2–3px wide zone, bayer4.
- Cast shadow: 1–2px flattened ellipse at the contact point, or checker-dithered
  (`dither(box, "keep", None, mix=0.5)` erases half the shadow px → classic 50% shadow).

### The shifted-shape recipe (cel shading with `only=`)

Draw the form in its DARKEST shade first, then restack lighter shades shifted toward
the light, clipped to the silhouette with `only="opaque"`:

```python
s.ellipse(6, 12, 25, 27, RAMP[0])                        # darkest = full silhouette
s.ellipse(5, 11, 24, 26, RAMP[1], only="opaque")         # shifted -1,-1: mid
s.ellipse(4, 10, 22, 24, RAMP[2], only="opaque")         # shifted more: light
s.circle(11, 15, 2, RAMP[3], fill=True, only="opaque")   # specular hotspot
```

Each layer only lands inside the silhouette → crescents of shadow emerge at the
bottom-right automatically. Works for any convex form.

### Anti-patterns

- **Pillow shading** = darkening all edges uniformly → balloon. Shadow follows LIGHT, not outline.
- **Banding** = ramp bands running parallel to the outline, 1px each → staircase. Vary band width.
- Pure black shadows / pure white highlights (unless the style is 1-bit or the palette says so).

## Dithering

Purpose: fake a missing mid-color, or texture. Tools: `dither()` (2-color, bayer2/4/8,
checker, `mix` = blend ratio), `gradient_dither()` (multi-stop banded gradient).

- USE for: sky/large gradients (≥8px span), glass, water sheen, soft shadow falloff, texture.
- DON'T use on: sprites <24px, faces, anything that animates fast (dither shimmers when moving).
- checker (50%) reads as texture; bayer8 at low mix reads as gradient. `only=` clips
  dither inside a color region: `s.dither(box, "keep", SHADE, mix=0.3, only=BASE)`.

## Anti-aliasing (manual only)

- Purpose: soften stair-steps on long curves/diagonals. Place ONE px of the in-between
  color at each corner of a stair-step. Never stack 2+ AA px (blur).
- Only where two COLOR REGIONS meet. Against transparency: either none (crisp, safest)
  or alpha-steps of the edge color (`(r,g,b,128)`) — never pre-mixed against an assumed bg
  (halo on any other bg).
- Skip AA entirely at ≤16px. At 32px, AA only the 2–3 worst curves.
- Jaggies fix: pixel steps along a curve must progress monotonically (runs of 1,1,2,3 —
  not 1,3,1). Redraw the curve before reaching for AA.

## Outlines

Choose ONE style per project and apply uniformly (weight always 1px):

| Style | How | Look |
|---|---|---|
| selout (default) | `outline(darkest_ramp_shade, where="inside")`, lighten top-side px 1 step by hand | pro, integrated |
| black cartoon | `outline("#000", where="outside")` | bold, action |
| none | — | soft, painterly; needs strong value contrast |
| colored | outside outline in a dark ambient color (`#1a1c2c`) | cozy/indie |

Light-side rule for selout: after outlining, repaint the outline px on the lit edge
(top/left) with the material's mid shade — the form pops.

## Texture recipes

- **Metal**: high contrast ramp, hard 1px specular line along the lit edge, darkest shade
  adjacent to the specular. No dither.
- **Wood**: mid ramp base, `line()` grain strokes in dark shade every 3–5px (wobble 1px),
  hue-shift grain toward orange.
- **Stone**: flat base, `noise(density=0.08, seed=k)` in shade color, a few 2–3px crack contours.
- **Fabric**: soft ramp, dither the shadow band border, fold lines follow gravity.
- **Grass tile**: 2 greens + noise sparkle of the lighter one, clusters of 2–3px blades on top edge.

## Sub-pixel detail (implied detail)

At small sizes, suggest instead of draw: a 2×1 dark px pair = belt; 1 light px under the
eye = cheek; 2px vertical dark = mouth. If a feature needs >3 colors at 16px, cut the feature.
