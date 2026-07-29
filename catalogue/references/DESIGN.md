# Sykon ABS catalogue design

Read this before touching the CSS in `scripts/build_catalogue.py`. Every value
below was measured from the brand master or solved against a contrast target.
If a page looks wrong, the fix is almost never a new colour — it is spacing.

## Palette

Pulled from `brand/dist/sykon_tokens.py`. Never hardcode a hex in the engine.

| Token | Hex | Used for |
|---|---|---|
| `RED` | `#C11720` | headings on light, rules, labels, red bands, list markers |
| `INK` | `#1C1C1A` | body copy, dark bands, the back-cover chevron |
| `PAPER` | `#FEF4F4` | page background |
| `PAPER_WARM` | `#F1E9E8` | all light type on red or ink |
| `PAPER_COOL` | `#E0E0E1` | proof plates, technical grounds |
| `RED_TINT_12` | `#F7D9DB` | product spot discs, and the eyebrow tag |
| `RED_TINT_17` | `#F4CED0` | chevron echo only — **not** behind red text |

Three rules that are not preferences:

1. **Light type on red or ink is `PAPER_WARM`, never `#FFFFFF`.** This is how
   the master sets it on every poster, banner and lockup.
2. **Red is never text on ink.** `#C11720` on `#1C1C1A` is 2.77:1 — it fails
   even the 3:1 large-text threshold. On dark grounds red is a graphic fill and
   nothing else. This is why `.band-red ul.sy li:before` and `.band-*-.lbl`
   flip to warm.
3. **`RED_TINT_17` cannot carry red text.** 4.28:1, just under AA. The eyebrow
   uses `RED_TINT_12` (4.66:1) for exactly this reason.

`verify_layout.py` enforces all three by sampling the rendered ground behind
every text span, so a regression fails the build rather than reaching a printer.

## Typeface

Hanken Grotesk throughout, bundled as a variable woff2 and base64-embedded so
the render never depends on an installed font. Ligatures are on — the brand's
own copy is full of "profile", "fluid", "flow", "certifications".

Swiss 721 Black Extended appears **only** inside the logo SVGs, as outlines.
It is never available to the engine as a live face. That means section heads
read narrower here than in the master, which set them in Swiss 721. That is the
accepted cost of not licensing it.

| Role | Size | Weight | Notes |
|---|---|---|---|
| Cover display | 30px | 300 | line-height 1.24, tracking −0.012em |
| Page heading | 23px | 500 | tracking −0.008em |
| Sub-head | 15.5px | 500 | |
| Body | 9.4px | 400 | line-height 1.585 |
| Highlights body | 12px | 400 | line-height 1.72, on the red band |
| Small / caption | 8px | 300 | opacity .72 |
| Eyebrow tag | 8.5px | 500 | uppercase, tracking 0.10em |
| Label | 7.6px | 500 | uppercase, tracking 0.16em |
| Footer | 7.2px | 400 | tracking 0.04em, opacity .68 |

**Display headlines close with a terminal period.** "Performance with Profile."
It is a brand signature taken from the master, not a typo. Do not strip it.

## Grid

- A4 portrait, 210 × 297mm trim
- Print builds add 3mm bleed on all four sides (216 × 303mm) plus corner crop marks
- Margin 16mm, gutter 6mm
- `.pad` is absolutely positioned at the margin and is a flex column, so a
  `.grow` spacer pushes the running footer to the foot of the page

## Page furniture

Content pages carry a hairline, the running brand line, and a two-digit folio.
The cover and back cover do not — a folio on a cover reads as a mistake. This is
what stops a short page looking unfinished, and it is why blocks do not need to
be padded with filler.

## The chevron

One per surface, bleeding off at least one edge, never repeated and never
centred inside the frame. On content pages it sits at 7% opacity behind the
lower field. On the back cover it is `INK` at full strength, oversized, running
off the right edge. It is **not** the Y symbol and must never stand in for it.

## Proof plates

Any image named in the config but absent from disk renders as a labelled grey
plate instead of failing. That is deliberate — it lets a layout be signed off
before the photography and section drawings exist. The build report lists every
plate so none reaches a client by accident.

## Why the CSS is written the way it is

- Fixed `height` on `.page` plus `overflow:hidden` is what keeps one page to one
  page. A `flex:1` child in place of a fixed height reliably spills a phantom page.
- `.pad` is absolutely positioned, which bounds the flex column inside it — that
  is what makes `.grow` safe here.
- Images and fonts are base64-inlined because Chromium's `file://` renderer
  resolves relative paths unpredictably.
- The page size is set in mm in `@page` **and** passed again to `page.pdf()`.
  Setting it in one place only produces an A4 that is a millimetre out.
- `.eyebrow` needs `align-self:flex-start`, or as a flex item it stretches the
  full column width and the pill becomes a bar.
