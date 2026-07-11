# LPC universal sheet — humanoid movement contract

Use this whenever the character is **humanoid: 2 arms + 2 legs** and needs a movement
set. The LPC (Liberated Pixel Cup) universal layout is the movement engine: frame
counts, row order and timing are a solved problem — target the grid with
`scripts/lpc.py` instead of inventing per-action sheets.

Only the **layout convention** is adopted. Art drawn here is original. Never bundle
actual LPC assets without per-artist CC-BY-SA/GPL credits.

## The grid

- Cell 64×64 · 13 columns × 21 rows (832×1344 full sheet)
- Direction order within every action: **up, left, down, right** (top→bottom)
- Feet baseline: bottom of the character at **y=58** inside the cell (`lpc.FEET`);
  `LPCSheet.place()` aligns this automatically
- Smaller art (32–48px chibi) is legal — it is centered in the cell, feet on baseline

| Action | Frames | Rows | ms/frame | Notes |
|---|---|---|---|---|
| spellcast | 7 | 4 | 100 | arms raise gradually, flash on 5–6 |
| thrust | 8 | 4 | 90 | polearm jab: pull back 0–2, jab 3–5, recover 6–7 |
| walk | 9 | 4 | 90 | **frame 0 = standing idle**, 1–8 = the cycle |
| slash | 6 | 4 | 80 | windup 0–1, swing 2–3, follow-through 4–5 |
| shoot | 13 | 4 | 70 | bow: nock 0–3, draw 4–8, loose 9–10, settle 11–12 |
| hurt | 6 | 1 (down) | 110 | collapse: recoil 0–1, fall 2–4, lying 5 |

## Humanoid proportions inside the cell

Full LPC-style adult (~56px tall): head ~13px, torso ~18px, legs ~22px, feet on
baseline. Chibi (32–40px): head half the height — same rows, same counts; only the
puppet is smaller. Keep one silhouette scale across the whole cast.

Draw each direction as its own parametric function (`draw(action, dir, frame)`),
not by mirroring: LPC left/right rows are true mirrors ONLY for symmetric
characters — a sword hand breaks that. Weapon in the same hand in every direction.

## Key-pose rules per action

- **walk (8-frame cycle)**: contacts on 1 and 5, passing on 3 and 7; arms swing
  opposite the legs; ±2px stride at chibi scale, ±4px at full scale; head bob 1px
  on passing frames. Frame 0 is the relaxed stand used by engines as idle.
- **slash**: the swing frames (2–3) displace the weapon ~90°; add a 1-frame smear
  or arc on 3 only. Body leans into 3–4.
- **thrust**: weapon stays horizontal; the body does the work (lean back → lunge).
- **spellcast**: hands rise symmetrically; palette-flash the hands/staff on 5–6.
- **shoot**: hold 4–8 readable (this is what the eye sees); loose is 2 frames max.
- **hurt**: last frame must read lying flat — engines hold it as the death pose.

## Avoid weapon clipping: draw on a margin canvas, not the bare cell

A long weapon (spear, staff, bow) swung through its arc reaches well outside the
character's own silhouette — sometimes at negative coordinates relative to where
the body was authored. If you draw straight onto a Sprite sized to the body, those
reaching frames get silently clipped at the canvas edge (a spear tip or staff orb
vanishes mid-swing). **The character's own size must stay exactly the same** —
only the scratch canvas gets bigger, so nothing you already tuned has to be
redrawn.

Fix: draw through a coordinate-translating wrapper onto a generous scratch
canvas (e.g. 96×96), keeping every pose's numbers in the original small
coordinate space (e.g. 0..40) you authored them in:

```python
OFFX, OFFY, SCRATCH = 28, 26, 96

class Canvas:
    """Translates every call by (OFFX, OFFY) so reaching poses never clip."""
    def __init__(self, w, h): self.s = Sprite(w, h)
    def px(self, x, y, c, only=None): self.s.px(x+OFFX, y+OFFY, c, only=only)
    def line(self, x0,y0,x1,y1,c,only=None):
        self.s.line(x0+OFFX,y0+OFFY,x1+OFFX,y1+OFFY,c,only=only)
    def rect(self, x0,y0,x1,y1,c,fill=True,only=None):
        self.s.rect(x0+OFFX,y0+OFFY,x1+OFFX,y1+OFFY,c,fill=fill,only=only)
    def ellipse(self, x0,y0,x1,y1,c,fill=True,only=None):
        self.s.ellipse(x0+OFFX,y0+OFFY,x1+OFFX,y1+OFFY,c,fill=fill,only=only)
    def polygon(self, pts, c, fill=True, only=None):
        self.s.polygon([(x+OFFX,y+OFFY) for x,y in pts], c, fill=fill, only=only)
    def outline(self, c, where="outside", diagonals=False):
        self.s.outline(c, where=where, diagonals=diagonals)
    def composite(self, frame=None): return self.s.composite(frame)
```

Use `Canvas(SCRATCH, SCRATCH)` in place of `Sprite(W, H)` when rendering each
frame; `LPCSheet.place()` crops the tight bbox and centers it in the real 64px
cell, so the extra scratch margin costs nothing in the final sheet. If a pose's
total reach still exceeds 64px, `place()` raises `ValueError` — a legitimate
signal to shorten that pose, not a bug to silence.

## Workflow

1. Draw the character parametrically in pixelstudio as usual (32×32 or 64×64).
2. `from lpc import LPCSheet` → `sheet.place(action, dir, frame, img)` for each
   cell you support. Unfilled cells stay transparent — partial sheets are valid;
   engines only read the rows they need. Start with walk, add actions later.
3. `sheet.save("name_lpc.png")` writes the sheet + engine JSON;
   `sheet.gif(...)` previews any row — LOOK at it before shipping.
4. Row/cell math when needed: `lpc.row_of(action, dir)`, `sheet.cell(...)`,
   `sheet.slots()` iterates every cell in sheet order.
