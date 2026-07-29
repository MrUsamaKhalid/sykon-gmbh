---
name: sykon-gmbh-catalogue
description: Build a branded Sykon ABS GmbH A4 portrait product catalogue as print and digital PDFs — the extended systems catalogue or the short 1-pager — from product content plus profile renders, section drawings and photography. Trigger whenever the user is producing a Sykon ABS document, however phrased, including "make the systems catalogue", "build a 1-pager", "spec sheet for SK-70", "aluminium catalogue", "company leave-behind", or when they supply system data (profile depths, U-values, EN classes) or a folder of profile renders. Do NOT use for Sykon Properties listings or brochures — that is a different brand entirely, see sykon-property-listing.
---

# Sykon ABS GmbH catalogue

Turns product content and artwork into the A4 portrait Sykon ABS catalogue, in
two files: a press-ready PDF and a lighter one for email.

## The one thing to get right

This is **Sykon Aluminium Building Systems** — German aluminium profile systems,
since 1967. It is **not Sykon Properties**, the Dubai real-estate brokerage.
Sykon Properties is monochrome editorial in Inter; Sykon ABS is red, industrial
and chevron-driven. Never carry an asset, colour, font or line of copy across.

## Workflow

### 1. Establish what is being built

- **Extended catalogue** — 6+ pages: cover, intro, pillars, families, one page
  per system, highlights, certifications, how-we-serve, back cover.
- **1-pager** — cover, one content side, back cover. A leave-behind.

Start from `catalogue/examples/extended.example.json` or
`catalogue/examples/onepager.example.json`.

### 2. Gather

Ask only for what is genuinely missing:

- system names and, per system: profile depths, glazing thickness, max vent
  weight, finishes
- tested performance with the standard cited — Uf, EN 12207 air, EN 12208
  water, EN 12210 wind, EN 1627 security, dB
- profile renders (cut-away section renders on transparent or white)
- section drawings
- application photography
- which certifications are genuinely held

If performance figures are not confirmed, leave the row out. Do not infer a
class from a similar system.

### 3. Write the config

Field-by-field notes are in `catalogue/references/CONFIG.md`. Copy rules are in
`catalogue/references/COPY.md` and they are not optional — the voice is
specification-led, and the length targets exist because pages are fixed-height
and overrun is silently clipped.

### 4. Build

```bash
python catalogue/scripts/build_catalogue.py <config.json> <image_dir> <out_dir>
```

Produces `<slug>-print.pdf` (216×303mm, 3mm bleed, crop marks) and
`<slug>-digital.pdf` (210×297mm, trimmed). Any image missing from disk renders
as a labelled proof plate and is listed in the build report — that is by design,
so a layout can be approved before artwork exists.

### 5. Verify, then look

```bash
python catalogue/scripts/verify_layout.py <config.json> <out_dir>
```

Checks page count, page dimensions, blank pages, off-palette colour, and text
contrast measured against the ground each span actually sits on. It exits
non-zero on failure.

Then **render a page and look at it**. A broken layout still produces a valid
PDF, and clipped copy is invisible to the verifier:

```bash
python -c "import fitz; fitz.open('<out>/<slug>-digital.pdf')[0].get_pixmap(dpi=110).save('/tmp/p1.png')"
```

### 6. Deliver

Both files, saying which is which. Name any proof plates still in the document —
never let one reach a client unflagged.

## Rules the engine already enforces, so do not fight them

- Primary red is `#C11720`. The `#E10916` in the brand master's construction
  spreads is a diagram colour and is quarantined.
- Light type on red or ink is `#F1E9E8`, never white.
- Red is never text on a dark ground (2.77:1). Graphic fill only.
- Display headlines end with a full stop. "Performance with Profile."
- One oversized chevron per surface, bleeding off an edge. The chevron is not
  the Y symbol and never substitutes for it.
- The wordmark is outlined SVG. It is never live text, so it cannot be re-set.

## Adding a page type

The block library is in `catalogue/scripts/build_catalogue.py`. Adding a block
is a renderer plus a `BLOCKS` entry — see the end of `CONFIG.md`. Prefer
composing existing blocks over inventing a layout; that is what keeps a
reference sheet cheap to match.
