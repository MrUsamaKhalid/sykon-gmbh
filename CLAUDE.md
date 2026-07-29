# Working in this repo

## Read first

**`BRAIN.md`** is the project memory — current mode, locked decisions, open
items, file map, session log. Read it before doing anything. When a decision
gets made, record it there, not in chat.

## CURRENT MODE: INTAKE — collect, do not analyse

The user is uploading catalogue materials in batches, deliberately one at a
time. For every batch:

1. Save it under `intake/materials/<NN>-<short-name>/`
2. Log it in `intake/INTAKE_LOG.md`
3. Reply **"Got it."** plus one line on what landed
4. **Stop**

Do not analyse, summarise the contents, extract data, critique, or start
building. Analysis begins **only** when the user says **"Analyze now"**.

This is written down because the failure mode is being helpful too early —
processing an upload the user is not ready to discuss breaks their flow. When
in doubt during intake, say less.

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
