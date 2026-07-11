# Animation — frame counts, timing, cycles, puppeting

Fewer, better frames. 4 great frames > 12 mushy ones. Key poses first, in-betweens only
if the motion still pops.

## Frame counts & timing

| Action | Frames | ms/frame | Notes |
|---|---|---|---|
| idle | 2–4 | 200–400 | breathing; ping-pong |
| walk | 4 (6 fancy) | 100–150 | contact-passing-contact-passing |
| run | 6–8 | 60–100 | exaggerated lean + stride |
| attack | 3–6 | windup 100–150 · strike 40–60 · impact hold 80–120 · recover 100–150 | speed asymmetry IS the punch |
| jump | 4–6 | crouch 100 · launch 50 · rise 80 · peak 150–200 (hang) · fall 80 · land 100 | |
| hurt | 2 | 60–80 | recoil + flash |
| death | 4–6 | 100–150 | impact, collapse, settle |

Even timing = predictable; variable timing = character. Put the long hold at the pose
you want the eye to remember (jump peak, sword extended).

## 4-frame walk construction

- F1 contact: right leg forward, left back, arms opposite legs, body at LOWEST (y+0)
- F2 passing: legs together under body, body HIGHEST (y-1)
- F3 contact: mirror of F1
- F4 passing: mirror of F2 (other arm)
- Stride ±2px at 32px scale. Head follows body 1 frame late (move head on F3 when body
  moved on F2) = follow-through, instantly alive.

## Idle (breathing)

2 frames: torso+head rows shifted down 1px on F2, ping-pong at 300–400ms.
4 frames: add eye-blink on one frame only (`tag` a longer cycle: frames 1,1,1,2 by
duplicating, or just give the blink frame a short duration).

## Part-per-layer puppeting (the studio's superpower)

Structure the character as layers = body parts, then animate by `shift()`ing layers
per frame instead of redrawing:

```python
s.layer("legs");  draw_legs()
s.layer("torso"); draw_torso()
s.layer("head");  draw_head()
s.layer("cape");  draw_cape()
for f in range(2, 5):
    s.add_frame(copy=True)               # copies all layers
    s.use(frame=f, layer="torso"); s.shift(0, BOB[f-1])
    s.use(frame=f, layer="head");  s.shift(0, BOB_DELAYED[f-1])
```

Better still: make draw functions parametric (`draw_legs(pose=2)`) and redraw per frame —
build scripts are code; loops write animation for you.

- Static background/prop layer: draw once, `copy_cel(layer="bg", to_frames="rest", link=True)`
  (link = same image shared; edit once, updates everywhere).
- Secondary motion: cape/hair/tail copies the body's offset from ONE FRAME AGO (lag 1).

## Squash & stretch, anticipation, impact

- Integer amounts only: squash = +1..2px wider & -1..2px shorter (redraw parametric, don't scale!).
- Anticipation before action: 1–2 frames opposite direction (crouch before jump, pull-back before punch).
- Impact: hold the contact frame + shift the WHOLE sprite 1px (screen-shake substitute),
  or flash the palette light for 1 frame (`replace`).

## Oversized attack frames and long weapons

Do not force every action into the idle/walk cell. Size the canvas from the complete
motion silhouette: character + weapon + trails/effects + a safety margin.

- Keep locomotion cells compact when the body stays inside the normal footprint.
- Before drawing an attack, block every key pose and measure the union bounding box of
  all opaque pixels across the whole action. Include the weapon tip at maximum reach,
  anticipation behind the body, follow-through, and any slash trail.
- If that union exceeds the normal cell, create an oversized attack cell. Prefer one
  fixed cell size for every frame within that attack tag; never resize individual frames,
  because changing frame dimensions/origins makes the character jitter in-engine.
- Add at least 2 px transparent safety margin at native resolution around the union box
  (more for a fast weapon trail). Clipping even one spear/sword-tip pixel is a failed export.
- Preserve a stable character anchor across actions: ground-contact pivot at the feet for
  side/front views, or the established body-origin for top-down views. Expand transparent
  space around that anchor instead of recentering each pose visually.
- Store per-action metadata: `frame_w`, `frame_h`, and `pivot_x/pivot_y` (or trim offsets).
  An atlas may mix compact locomotion regions and oversized attack regions; a rigid grid
  may instead use the largest attack cell, accepting transparent space.
- Judge reach from the weapon-tip arc, not only from body movement. Long weapons need
  readable anticipation → fastest crossing → extended contact → follow-through poses.

Pre-export validation: overlay all attack frames using the same pivot, confirm the feet/body
anchor does not drift, then inspect every outer edge for opaque pixels touching the boundary.
If any do, enlarge the action canvas and re-export.

## Loop hygiene

- Watch the GIF for ≥3 loops: the seam frame N→1 must continue the motion, not reset it.
- Contact frames must exist or feet skate ("moonwalk" = animation/movement speed mismatch —
  at game speed, stride px per cycle should match movement px).
- Dithered areas that move = shimmer. Solid-shade moving parts.
- Ping-pong for pendulum motions (breathing, tail sway); forward for cycles (walk, run, spin).

## Preview & judge

`preview()` shows all frames side by side with durations — check pose arcs (trace the
head's y across frames: should curve smoothly). `save_gif(scale=6)` and LOOK at it —
timing can only be judged in motion.
