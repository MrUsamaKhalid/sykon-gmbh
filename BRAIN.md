# BRAIN — Sykon ABS GmbH

Project memory. If context is lost, **read this file first**, then `CLAUDE.md`.
Keep it current: when a decision is made, record it here, not in chat.

---

## ACTIVE MODE: BUILD — S60 spec sheet

Intake closed at batch 08. Analysis authorised. Now building.

**Current objective:** reproduce `SAMPLE__USE_THIS.pdf` as a data-driven block
in the catalogue engine, populated with real S60 content, so the other nine
systems regenerate from the same template. S60 gets approved first, then scale.

If more material arrives, fall back to the intake habit — save it under
`intake/materials/`, log it in `intake/INTAKE_LOG.md`, and carry on.

## THE ONLY SOURCE OF FACT IS THE .DOCX

Not an ordering — a single source. **Every word, letter, symbol and figure on a
catalogue page comes from that system's `.docx`.** The sample supplies DESIGN
only. The portfolio, old brochure, drawings and emails are input, never fact.
The old catalogue is a post-approval reference.

Two approved exceptions, in `catalogue/references/furniture.json`: the logo, and
the contact line. The certification badge and PIV / ift / A|U|F marks were
**removed** — no `.docx` evidences them and a certification mark carries legal
weight.

Enforced, not trusted:

| Tool | Does |
|---|---|
| `tools/check_provenance.py` | Fails the build on any printed string not traceable to the document |
| `tools/build_review_questions.py` | One question per claim, with its source section, for the reviewer |

This exists because the first S60 sheet shipped contaminated — "Superior" in the
product name, four invented segment descriptions, a certification badge, three
certification marks. All from the sample. The rule alone did not catch it.

## People

| Who | Role | Note |
|---|---|---|
| **Anthony Makhlouf** | Director of Pre-Sales, Sykon GmbH · `a.makhlouf@sykon.ae` | **Heads this project.** The approver. His design feedback is binding |
| **Usama Khalid** | `usama@sykonproperties.ae` | The user. Producing the catalogues |
| **Sujith** | `sujith@sykon.ae` | Producing the section details and dimensions for the extended catalogue |
| Muhammad Ali Zafar | Marketing Manager, Sykon Properties | Coordinating freelancers |
| Zain Riaz, Mohammed Imran | cc | |

## Anthony's direction (from the email thread — treat as requirements)

Agreed plan, 8 Apr:
- Individual catalogues **per system first**, then a comprehensive catalogue
  covering the full portfolio. This matches the build order already chosen.
- Technical info is the base; **placeholder images are acceptable for now**.
- A freelancer will produce **40–50 rendered images** of doors and windows from
  various angles, detailed and overall. BIM models go out after first approval.
- The design must align with the **new corporate identity** — that is the brand
  master already encoded in `brand/tokens/`.

Feedback on the first draft, 10 Apr — **the two things he asked to be fixed**:

1. **"The typology section appears too small, and the figures do not clearly
   represent the exact typologies. Some clients prefer to see accurate and
   recognizable typology symbols."**
   → This is why the 53 typology SVGs exist. In the rebuild the typology strip
   must be **larger than the sample's**, and every symbol must be the correct,
   recognisable one for its label. A wrong symbol is worse than no symbol.
2. **"For the extended catalogue, we need to allocate space for the dimensions
   and detailed sections."**
   → The extended catalogue needs a dimensions/section region reserved. Sujith
   supplies the content.

1 May:
- Drawings and sections are **vector PDFs**, each section clearly titled and
  ready to lift directly. Good — sections can be extracted as vector, not traced.
- The product images supplied so far are **AI-generated placeholders**.
- **The project is behind schedule.** Prefer shipping something reviewable over
  polishing something unreviewable.

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

**Goal:** product catalogues — a per-system spec sheet (the "1-pager") and an
extended catalogue covering the full portfolio, as print and digital PDFs. The
design system exists to serve catalogue production.

Ten systems: S50 non-thermal, S60, S77 folding, SL20 panoramic, SL350
non-thermal, SL450 lift-and-slide, SL450S, SL580, SY35, SY50.

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
| Page ground | `#FFFFFF` (`color.page`) | Client direction. `paper` keeps its other role — light type on dark is still `#F1E9E8` |
| Red on dark | `color.red-on-dark` `#DC1A25` | Brand red is 2.77:1 on ink, below even 3:1. This is the minimum lift clearing it. LARGE display only |
| Sample figures | **Layout only** | Its numbers are illustrative and mostly absent from the `.docx`. See `catalogue/references/SOURCE_AUDIT.md` |
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

- [ ] **S60 sheet sign-off** — then scale the template to the other nine
- [ ] **S50 and SL350 have zero artwork** — cannot produce a sheet until renders exist
- [ ] **Unresolved author queries** in SL20 (§2 water result) and S77 (§16 limitations)
      — must be settled before those systems publish. See `catalogue/references/SOURCE_AUDIT.md`
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
| Catalogue engine + verifier | Done — all examples build and pass all checks |
| **S60 product spec sheet** | **Done** — reproduces the sample layout, all figures from the `.docx` |
| Typology symbols | 53 named + normalised to `brand/assets/typologies/` |
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
