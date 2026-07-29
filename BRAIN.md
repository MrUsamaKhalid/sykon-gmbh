# BRAIN — Sykon ABS GmbH

Project memory. If context is lost, **read this file first**, then `CLAUDE.md`.
Keep it current: when a decision is made, record it here, not in chat.

---

## ACTIVE MODE: INTAKE — collect only, do not analyse

The user is uploading catalogue materials in batches, one at a time.

**The rule:** for every batch, save it, log it in `intake/INTAKE_LOG.md`, reply
**"Got it."** plus a one-line note of what landed, and **stop**. Do not analyse,
summarise, critique, extract, or start building from it.

**Analysis begins only when the user says "Analyze now"** (or an unmistakable
equivalent). Until that phrase arrives, collecting is the whole job.

Why this is written down: it is easy to "helpfully" start processing an upload.
That breaks the user's flow and wastes the batch. Don't.

When "Analyze now" arrives → switch to ANALYSIS MODE: read every logged item,
cross-reference against the brand system already built, and report findings.

---

## What this is

**Sykon Aluminium Building Systems** (legal entity: Sykon ABS GmbH) — German
aluminium profile systems, "German Engineering System Since 1967", selling into
the UAE architectural specification market via sykon.ae.

Contact of record: `+971 50 804 0985` · `info@sykon.ae` · `www.sykon.ae`

> **NOT Sykon Properties.** That is the Dubai real-estate brokerage — monochrome
> editorial, Inter, no accent colour. Same owner, different brand. Never mix
> assets, palettes, type or voice. The `sykon-property-listing` /
> `sykon-featured-listing` skills belong to Properties: copy their *engineering*
> pattern, never their *design*.

**Goal:** product catalogues — an extended systems catalogue (6+ pages) and a
short 1-pager, as print and digital PDFs. The design system exists to serve
catalogue production.

---

## Where things are

| Path | What |
|---|---|
| `BRAIN.md` | This file. Project state, decisions, open items |
| `CLAUDE.md` | How to work in the repo. Rules, gotchas, style |
| `intake/INTAKE_LOG.md` | Running log of every batch the user has sent |
| `intake/materials/` | The uploaded files themselves |
| `brand/tokens/sykon.tokens.json` | **Single source of truth.** Edit this, never `dist/` |
| `brand/tokens/build.mjs` | Generates `dist/`, and lints the palette |
| `brand/dist/` | Generated: CSS vars, Tailwind preset, Python module |
| `brand/assets/logo/` | 8 logo SVGs, generated from the brand master |
| `brand/assets/pattern/` | Chevron, echo, band, masthead wave |
| `brand/assets/fonts/` | Hanken Grotesk variable woff2 + OFL licence |
| `catalogue/scripts/build_catalogue.py` | The engine. JSON → HTML → Chromium → 2 PDFs |
| `catalogue/scripts/verify_layout.py` | Gates the build. Exits non-zero on failure |
| `catalogue/references/` | DESIGN.md, CONFIG.md, COPY.md |
| `catalogue/examples/` | `extended.example.json`, `onepager.example.json` |
| `tools/build_logos.py` | Regenerates logo SVGs from the brand master PDF |
| `tools/build_patterns.py` | Regenerates pattern SVGs |
| `.claude/skills/sykon-gmbh-catalogue/` | Repo-local skill |

Source of truth for the brand: `MASTERFILE_Sykon_ABS_GmbH__Brand_Identity.pdf`,
34 pages, Adobe Illustrator 30.1.

---

## Decisions locked (do not relitigate)

| Decision | Value | Why |
|---|---|---|
| Primary red | `#C11720` | All 17 application pages measure nearest to it, two exactly. `#E10916` appears only on construction spreads pp.4/5/9 and on no produced application |
| `#E10916` status | Non-brand | Quarantined in the `doc.*` namespace. `build.mjs` lints for its escape |
| Wordmark type | Swiss 721 BT Black Extended, **outlined SVG only** | Commercial Bitstream face. Never vendored, never live text |
| Text type | Hanken Grotesk (OFL) | Vendored as variable woff2 with licence |
| Page format | A4 portrait, 210×297mm | Matches the master's catalogue mockup |
| Language | English only | Structured so Arabic is additive later |
| Outputs | Print (216×303mm, 3mm bleed, crop marks) + digital (trimmed) | |
| Print colour specs | Reference values, marked unverified | The master contains **no** CMYK, Pantone or ICC data at all |
| Symbol geometry | **Frozen exactly as drawn** | Diagonals span 32.5–33.4°; regularising means redrawing the logo — the owner's call, not ours |

### Colour rules that are measured, not taste

- Light type on red or ink is `#F1E9E8`, **never** pure white.
- **Red is never text on a dark ground.** `#C11720` on `#1C1C1A` is 2.77:1 —
  fails even the 3:1 large-text threshold. Graphic fill only.
- `red-tint-17` (`#F4CED0`) cannot carry red text — 4.28:1, under AA.
  Use `red-tint-12` (`#F7D9DB`) — 4.66:1.
- On light, `#C11720` is 5.71:1 and passes AA for body text.

### Defects in the brand master (already handled)

1. Page 3 credits "Neue Montreal" — wrong, none is embedded. It is Hanken Grotesk.
2. Pages 4, 5, 9 use the off-spec `#E10916`.
3. The symbol on page 5 is **1.66% vertically squashed** — a hand-squash defect.
   Never trace it; use `symbol.path` from the tokens.
4. Nine near-whites in use where one is declared → collapsed to three tokens.
5. No clear-space or minimum-size rule existed → authored (clear space `1.5t`;
   min 12mm/34px symbol, 16mm/46px lockup).
6. Page 8's colourway sheet covers the *legacy stacked GmbH* mark, not the
   horizontal lockup used on nearly everything.

---

## Open items

Waiting on the user:

- [ ] **1-pager reference sheets** — its layout is provisional until matched
- [ ] **Full catalogue file** — real content and system data
- [ ] **Artwork** — profile renders, section drawings, application photography,
      certification marks (PIV, ift Rosenheim, A|U|F)
- [ ] **PARKED: Revit `.rfa`/`.rvt`** (~19 files, ~347MB). Unreadable here, and
      `SYKON.rvt` at 247MB exceeds GitHub's 100MB file limit. Needs either Revit
      *exports* for the catalogue, or LFS/CDN hosting if the BIM library is itself
      a deliverable. See `intake/INTAKE_LOG.md`. Do not act without asking
- [ ] **Confirmed certifications** — never claim one that is not held
- [ ] Decision: licence Swiss 721 for section heads? Hanken has no extended cut,
      so live heads read narrower than the master
- [ ] Decision: regularise the symbol's diagonals to a clean 33.69°? Means
      redrawing the logo. Default is to leave frozen
- [ ] Commission authoritative CMYK/Pantone before any press run
- [ ] Request the original vector logo package from the designer as long-term master

---

## Status

| Area | State |
|---|---|
| Design tokens + build/lint | Done |
| Logo SVGs (8) | Done — 98.1% shape overlap vs original artwork |
| Pattern SVGs | Done |
| Fonts | Done |
| Catalogue engine + verifier | Done — both examples build and pass all checks |
| Repo skill + references | Done |
| Living docs site (`brand/docs/index.html`) | **Not built yet** |
| Real content wired in | Blocked on uploads |

Branch: `claude/sykon-gmbh-design-system-4jnnt4`
No PR — the repo was empty, so this branch is the only branch and the default.
There is no base to open a PR against unless a `main` baseline is created.

---

## Session log

Newest last. One line per meaningful event.

- Analysed the 34-page brand master forensically (embedded fonts, vector paths,
  per-span colour) rather than visually.
- Corrected an early error of mine: I claimed the mockups used `#E10916`. They
  do not. `#C11720` is the brand red.
- Built tokens, logo/pattern assets, fonts, catalogue engine, verifier, skill.
- Verifier caught two real defects: red-on-red list marker, and an eyebrow tag
  under AA. Both fixed.
- Entered INTAKE MODE at the user's request — collecting catalogue materials in
  batches, analysis deferred until "Analyze now".
