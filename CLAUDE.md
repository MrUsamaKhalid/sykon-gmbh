# Working in this repo

## Read first

**`BRAIN.md`** is the project memory — current mode, locked decisions, open
items, file map, session log. Read it before doing anything. When a decision
gets made, record it there, not in chat.

## CURRENT MODE: REVIEW — ten spec sheets, awaiting placements

Intake is closed. All ten sheets build, pass the provenance gate and pass the
layout verifier. What is outstanding is the client's input: where each drawing
goes on the page.

One command rebuilds everything:

```bash
python tools/scaffold_sheet.py --all     # .docx -> catalogue/examples/*.json
python tools/build_all_sheets.py         # gate -> build -> verify -> questions
```

Never hand-edit a sheet config to add text. If a string is not in the `.docx`,
it does not go on the page — and `scaffold_sheet.py` regenerates the file, so a
hand edit is lost anyway. To change *what the document says*, fix the document.
To change *which of it appears*, move rows between `pages[0]` and `_deferred`.

If new material arrives mid-build: save it under `intake/materials/`, log it in
`intake/INTAKE_LOG.md`, and continue.

## The only source of fact is the .docx

**Every word, letter, symbol and figure printed on a catalogue page must come
from that system's `.docx` in `intake/materials/01-catalogue-materials/`.**
Not the sample, not the portfolio, not the old brochure, not the drawings, not
the emails. Those are input. They are not facts.

Two exceptions, both listed in `catalogue/references/furniture.json`, both
approved explicitly by the client:

- **Brand furniture** — the logo, and `www.sykon.ae | info@sykon.ae`.
- **Design headings** — section titles taken from the sample, which supplies
  DESIGN only. They label the page; they assert nothing about a product.

Nothing else. The certification badge and the PIV / ift / A|U|F marks were
removed for exactly this reason: no `.docx` evidences them, and a certification
mark is the one claim on the page carrying legal weight.

```bash
python tools/check_provenance.py catalogue/examples/<system>-sheet.json
```

It resolves the document through `systems/<SYSTEM>/source/`, not by matching
filenames. Filename matching had SL450 gated against the SL450s document —
"SL450" is a prefix of "SL450S" — which is exactly the class of mistake that
makes a printed figure belong to a different product.

Run it before any build. It walks every printed string, matches it against the
document by token sequence, and exits non-zero on anything untraceable. This is
a gate, not advice — the first S60 sheet shipped with "Superior" in the product
name and four invented segment descriptions, all from the sample. Good
intentions did not catch that.

```bash
python tools/build_review_questions.py catalogue/examples/<system>-sheet.json
```

Writes `catalogue/review/<system>-questions.md` — one question per claim, each
quoting the exact string, its slot on the sheet, and the section it traces to,
so the reviewer confirms rather than hunts. Anything untraceable heads the file
under **UNVERIFIED — DO NOT PUBLISH**.

The old catalogue is a **post-approval** reference. It is not a source.

## Two binding requirements from Anthony (project lead)

Both came from his review of the first draft and are not optional:

1. **Typology symbols must be large and accurate.** His words: the section
   "appears too small, and the figures do not clearly represent the exact
   typologies." Make the strip bigger than the sample's, and make sure each
   symbol is genuinely the typology its label claims. A mislabelled symbol in a
   technical catalogue is worse than an omitted one.
2. **The extended catalogue must reserve space for dimensions and detailed
   sections.** Sujith supplies that content as titled vector PDFs.

The project is behind schedule. Prefer shipping something reviewable over
polishing something unreviewable.

## The one thing to get right

This is **Sykon ABS GmbH** — Sykon Aluminium Building Systems, German aluminium
profile systems, since 1967. It is **not Sykon Properties**, the Dubai
real-estate brokerage.

If you have the `sykon-property-listing` or `sykon-featured-listing` skills
loaded: those are Sykon Properties. Their *engineering* pattern is the right one
to follow here — Python builds an HTML string, Chromium renders it via
Playwright, fonts and images base64-inlined, fixed page height with
`overflow:hidden`, `@page` size in mm set in both the CSS and the `page.pdf()`
call. Their *design* is the wrong one to follow: monochrome, Inter, no accent
colour, hairlines only. Sykon ABS is red, industrial, chevron-driven.

Never copy an asset, colour, font or line of copy from one brand to the other.

## Source of truth

`brand/tokens/sykon.tokens.json`. Everything in `brand/dist/` is generated —
edit the JSON and rerun `node brand/tokens/build.mjs`. Never hand-edit `dist/`.

The build lints. It fails on a contrast claim that no longer measures true, a
symbol path that disagrees with its declared aspect, or the non-brand `doc.*`
red reappearing in the palette. If it fails, the token file is wrong, not the
linter.

## Regenerating assets

Logo and pattern SVGs are generated, not hand-drawn:

```bash
python tools/build_logos.py <brand-master.pdf>
python tools/build_patterns.py
```

`build_logos.py` needs the brand master PDF because it reads the Swiss 721
subset out of it. That font is commercial and must never be committed —
`.gitignore` covers the scratch directory it lands in.

## Rules that came from measurement, not taste

Do not "improve" these without measuring first. Each one is in the token file
with its evidence.

- **Primary red is `#C11720`.** `#E10916` is a diagram colour that leaked into
  the master's construction spreads. It lives in the `doc.*` namespace and must
  never appear on a brand surface.
- **Red is never text on a dark ground** (2.77:1). Graphic fill only. Dark-surface
  copy is `paper`.
- **Light type on red or ink is `#F1E9E8`**, never `#FFFFFF`.
- **The symbol's aspect is locked at 2.2568:1.** Any component API takes an
  aspect-locked box, never independent width and height.
- **The symbol is not monoline** — diagonals are 6.3% thicker than the bars.
- **Clear space is 1.5t**, where `t` is the bar thickness (0.17903 of height).
- **Display headlines close with a terminal period.** "Performance with Profile."
  It is a brand signature, not a typo — do not strip it.
- **Exactly one oversized chevron per surface**, bleeding off at least one edge.
  Never repeated, never centred inside the frame.
- **The chevron is not the symbol.** It never stands in for the mark in a lockup
  or an avatar slot.
- **Ligatures stay on.** The brand's copy is full of "profile", "fluid", "flow",
  "certifications".

## Things the master gets wrong

If you are reading the brand master PDF directly, be aware:

- Page 3 says the typeface is "Neue Montreal". It is not, and never was — no
  Neue Montreal is embedded in the file. It is Hanken Grotesk.
- Pages 4, 5 and 9 use `#E10916` for the logo. Off-spec.
- The symbol on page 5 is 1.66% vertically squashed. Never trace it — use
  `symbol.path` from the token file.
- Page 8's colourway sheet covers the legacy stacked "SYKON GmbH" mark, not the
  horizontal lockup used on nearly everything.

## Style

Match the surrounding code. The Python here is stdlib-only except for the
generators (fontTools, PyMuPDF) and the renderer (Playwright). The token build
is zero-dependency Node. Keep it that way unless there is a real reason not to.
