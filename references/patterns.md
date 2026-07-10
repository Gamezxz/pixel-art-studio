# Patterns — how to build things

## Canvas sizes

| Size | Use |
|---|---|
| 8x8 | bullets, particles, tiny items, NES-era tiles |
| 16x16 | classic platformer characters, icons, tiles |
| 24x24 / 32x32 | modern standard for characters (Celeste, Shovel Knight), icons, tiles |
| 48x48 / 64x64 | large characters, bosses, detailed portraits |
| 96–128 | portraits, big props |
| 128x128 – 320x240 | full scenes, backgrounds (320x240 = retro screen) |

Pick the SMALLEST size that holds the design. Detail you can't see at 1x is wasted
and hurts readability. Leave a 1px transparent margin when using `outline(where="outside")`.

## Character proportions

- **Chibi** (16–32px): head = 40–50% of height. Platformers/action. Huge readable head,
  stubby limbs, feet 1–2px tall.
- **Heroic** (32–48px): head = 1/3 to 1/4 of height. Action-RPG standard.
- **Realistic** (48px+): head = 1/6 to 1/8. RPG portraits, strategy units.

32x32 chibi row budget (y coords): head 2–13 · torso 14–22 · legs 23–29 · ground/contact 29–31.
Eyes sit at ~60% of head height, 1–2px each, 2–4px apart.

## Build order (silhouette-first) — always this order

1. **Silhouette blob** — one dark color, shape only. Run `save_silhouette()`:
   if the pose/species doesn't read as a flat shape, fix NOW. Never start from the eye.
2. **Big color masses** — flat fills per material (skin / hair / cloth / metal). No shading.
3. **Light + shading** — pick light source (default top-left). 1 shadow band + 1 highlight
   band per material (cel). Use the shifted-shape recipe in techniques.md.
4. **Outline decision** — selout / black / none (see techniques.md). Apply uniformly.
5. **Details & AA last** — face, buckles, sparkle px. If a detail needs >3 colors, cut it.

## Readability rules

- **The 1x test**: if you can't tell what it is at 1x (preview scale 4 viewed quickly), it failed.
- **Clusters, not noise**: same-color pixels in groups of 3+; single stray px only for
  eye glints / sparkles.
- Value contrast carries readability; hue carries mood. Character midtones must separate
  from background midtones by value.
- Silhouette breaks (weapon over shoulder, ear tuft, tail) do more than internal detail.

## Symmetry

Draw half, `mirror_x()`, then **break** symmetry: shift the weapon arm, fringe, scarf.
Perfect mirror = mannequin. Asymmetric light (highlight only on lit side) also breaks it.

## Items / icons (16–32px)

4–6 colors. Read by silhouette alone: sword = long diagonal, potion = bottle + neck,
key = ring + teeth. 45° diagonals look cleanest (1:1 pixel steps). Add 1 highlight px
cluster at the light corner, done.

## Tiles & tilesets

- Sizes: 16x16 or 32x32.
- **Seamless check**: `t.shift(w//2, h//2, wrap=True)` then preview — seams appear at
  the cross in the middle. Fix, shift back.
- Keep tile corners/edges quieter than centers; heavy detail at edges creates visible grids.
- Make 3–4 variants of common tiles (grass, floor) and scatter to break repetition.
- Autotile (bitmask N=1, E=2, S=4, W=8 → 16 tiles; full blob = 47) — build the plain
  center tile first, then edges/corners as copies with modified borders.
- Backgrounds: lower saturation + contrast than foreground; distant layers shift darker & bluer.

## Scenes

Compose in 3 depth bands (sky / mid / playfield). Detail budget goes to the playfield.
Use `gradient_dither()` for skies with the palette's cool ramp.
