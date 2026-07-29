# Intake log

Every batch the user sends, logged as it arrives. **Collect only** — see the
INTAKE MODE section at the top of `BRAIN.md`.

Analysis starts when the user says **"Analyze now"**. Not before.

Files live in `intake/materials/<batch>/`.

---

## Protocol

For each batch:

1. Save the files under `intake/materials/<NN>-<short-name>/`
2. Add a row to the table below and a block under **Batch detail**
3. Reply **"Got it."** plus one line on what landed
4. **Stop.** No analysis, no summary of contents, no suggestions

---

## Batches received

| # | Received | Name | Files | Notes |
|---|---|---|---|---|
| 01 | 2026-07-29 | Catalogue materials — system .docx | 10 | Per-system source content, 15MB |
| — | 2026-07-29 | SY Families (`.rfa` / `.rvt`) | ~19 | **PARKED** — not uploaded. See below |
| 02 | 2026-07-29 | PDF views — per-system drawings | 22 | Numbered 000–020, 14MB |
| 03 | 2026-07-29 | Drawings — Batch A | 11 | Sample boards, 19MB. Batch B to follow |
| 04 | 2026-07-29 | Drawings — Batch B | 10 | Sample boards, 20MB. No overlap with A; A+B = 21 |
| 05 | 2026-07-29 | Performance icons | 9 | PNG, 4.1MB |
| 06 | 2026-07-29 | Typologies | 53 | SVG in A/B/C sets, 3.1MB (+1 redundant zip) |
| 07 | 2026-07-29 | References — sample, background, portfolio, old brochure | 5 | 26MB |
| 08 | 2026-07-29 | Email conversation | 6 | Project thread, 1.2MB. **Intake closed here** |

---

## Batch detail

<!-- One block per batch. Record what it is and where it went. Nothing more
     until analysis is authorised. -->

### Batch 01 — Catalogue materials (system .docx)

`intake/materials/01-catalogue-materials/` — 10 files, 15MB, from
`Sykon_ABS_Catalogues.zip`. One Word document per system:

| File | System |
|---|---|
| `S 50 Non thermal   Catalogue material_.docx` | S 50 non-thermal |
| `S60  Catalogue material_.docx` | S 60 |
| `S77 folding   Catalogue material_.docx` | S 77 folding |
| `SL 20 panoramic Catalogue material_.docx` | SL 20 panoramic |
| `SL 350 non thermal Catalogue material_.docx` | SL 350 non-thermal |
| `SL 450 Lift and slide Catalogue material_.docx` | SL 450 lift-and-slide |
| `SL 450 S Catalogue material_.docx` | SL 450 S |
| `SL 580 Catalogue material_.docx` | SL 580 |
| `SY 35 Catalogue material_.docx` | SY 35 |
| `SY 50 Catalogue material_.docx` | SY 50 |

Not opened. Contents unexamined pending "Analyze now".

### Batch 02 — PDF views

`intake/materials/02-pdf-views/PDF Views/` — 22 files, 14MB, from
`PDF_Views.zip`. Numbered `000`–`020`, sequence matching batch 01's systems.

| # | File | System |
|---|---|---|
| 000 | Starting View | — |
| 001 | S60 Side Hung Window | S 60 |
| 002 | S60 Single Hinged Door Open Out | S 60 |
| 002 | S60 Single Hinged Door Open Out **_compressed** | S 60 — duplicate, compressed |
| 003 | S60 Single Hinged Door Open In | S 60 |
| 004 | S77 3+0 Folding Door | S 77 |
| 005 | SL20 | SL 20 |
| 006 | SL450 | SL 450 |
| 007 | SL450s 2 Panel Sliding with Flyscreen | SL 450 S |
| 008 | SL450s 3 Track Sliding Door | SL 450 S |
| 009 | SL450s Monorail with Flyscreen Sliding Door | SL 450 S |
| 010 | SL580 2 Panel Narrow Sliding Door | SL 580 |
| 011 | SL580 2 Panel Sliding with Flyscreen | SL 580 |
| 012 | SL580 Monorail Sliding Door | SL 580 |
| 013 | SY35 Top Hung Window Wall Fix | SY 35 |
| 014 | SY35 with Top Hung Window | SY 35 |
| 015 | SY50 Conventional Curtain Wall | SY 50 |
| 016 | SY50 Structural Curtain Wall | SY 50 |
| 017–020 | Detailed 3D Views (×4) | — |

Two files share the number `002` — one is a `_compressed` variant of the same
view. Flag at analysis; do not resolve now.

Not opened. Contents unexamined pending "Analyze now".

### Batch 03 — Drawings, Batch A

`intake/materials/03-drawings-batch-a/` — 11 PDFs, 19MB, from
`Drawings_Batch_A.zip`. Sample boards and detail drawings.

| File | System |
|---|---|
| `LS450S Sample Board rev01.pdf` | LS 450 S — note the "LS" prefix; elsewhere it is "SL 450 S" |
| `S60 Casement Door A1 Sample Board.pdf` | S 60 |
| `S60 Casement Window A1 Sample Board.pdf` | S 60 |
| `S60 Hinged Door Swing Out 8+16+8.pdf` | S 60 |
| `S60 Open-In Overlap Sample Board rev01.pdf` | S 60 |
| `S60 TT Sample Board rev01.pdf` | S 60 — TT presumably tilt-and-turn |
| `SL20 Panoramic Slim Sliders Exposed Sides (20260311).pdf` | SL 20 |
| `SL20 Panoramic Slim Sliders Exposed Sides 02 (20260312).pdf` | SL 20 |
| `SL20 Panoramic Slim Sliders Exposed Sides 03 (20260316).pdf` | SL 20 |
| `SL20 Panoramic Slim Sliders Generic Board.pdf` | SL 20 |
| `SL20 Sample Board.pdf` | SL 20 |

Noted for analysis, not resolved now:
- `LS450S` vs `SL 450 S` — prefix inconsistency across batches
- Three dated SL20 "Exposed Sides" files (0311 / 0312 / 0316) look like
  revisions of one drawing; latest is presumably authoritative
- `rev01` suffixes appear on some boards and not others

Not opened. Contents unexamined pending "Analyze now".

### Batch 04 — Drawings, Batch B

`intake/materials/04-drawings-batch-b/` — 10 PDFs, 20MB, from
`Drawings_Batch_B.zip`. Continues the sample-board set from Batch A.

| File | System |
|---|---|
| `SL450 Lift & Slide Board A1.pdf` | SL 450 |
| `SL450 Monorail Slide Only Board A1.pdf` | SL 450 |
| `SL450S A1 Sample Board.pdf` | SL 450 S |
| `SL450S Monorail Board A1.pdf` | SL 450 S |
| `SL580 Heavy Duty Sliders Generic.pdf` | SL 580 |
| `SL580 Monorail L&S Details.pdf` | SL 580 |
| `SL580 Monorail Sliders Generic.pdf` | SL 580 |
| `SY35 Slim SCW Generic Board.pdf` | SY 35 — SCW presumably structural curtain wall |
| `SY50 Sample Board.pdf` | SY 50 |
| `SY50 with Vent Toggle Glazed 8+16+8.pdf` | SY 50 |

**Verified: zero filename overlap with Batch A.** A + B together are the
complete 21-file drawing set, matching the user's screenshot.

Note for analysis: `SL450S A1 Sample Board` here vs `LS450S Sample Board rev01`
in Batch A — same system, different prefix and revision marker. Resolve later.

Not opened. Contents unexamined pending "Analyze now".

### Batch 05 — Performance icons

`intake/materials/05-performance-icons/` — 9 PNGs, 4.1MB, from
`Performance_Icons.zip`. Descriptively named, covering the test/performance
categories a spec table cites:

| File | Likely category |
|---|---|
| `Acoustic performance illustration with house and speaker.png` | Sound reduction |
| `Airflow dynamics around a house.png` | Air permeability |
| `Static water penetration icon.png` | Watertightness, static |
| `Dynamic water penetration test icon.png` | Watertightness, dynamic |
| `Wind resistance safety icon design.png` | Wind load, safety |
| `Wind resistance serviceability concept illustration.png` | Wind load, serviceability |
| `Thermal cycling around the house.png` | Thermal performance |
| `Horizontal displacement in building structure.png` | Structural movement |
| `Vertical displacement in building structure.png` | Structural movement |

Note for analysis: these are **raster**. The catalogue is vector-first and these
would sit next to spec tables at small size, so check resolution and whether
transparent-background or SVG versions exist. Filenames read as AI-generation
prompts rather than an asset naming scheme — worth renaming to category codes.

Not opened. Contents unexamined pending "Analyze now".

### Batch 06 — Typologies

`intake/materials/06-typologies/Typologies/SVG/` — 53 SVGs, 3.1MB, from
`Typologies.zip`, split across three folders:

| Set | Files | Range |
|---|---|---|
| `A/` | 20 | Asset 80–100 |
| `B/` | 20 | Asset 100–119 |
| `C/` | 13 | Asset 120–132 |

`C/C.zip` also present — **verified byte-identical to the 13 files already in
`C/`**, so it is a redundant archive. Left in place, not counted in the 53.

Notes for analysis, not resolved now:
- Filenames are Illustrator export defaults (`Asset NN`), carrying no meaning.
  These will need mapping to actual typology names before they are usable.
- Numbering overlaps between sets: `Asset 100` appears in both `A/` and `B/`;
  `A/` also has `Asset 100 (2)`.
- Several `(2)` duplicates: `Asset 86`, `Asset 95`, `Asset 100` in `A/`,
  `Asset 122` in `C/`. Establish which is authoritative.
- Vector, which is right for the catalogue — unlike the performance icons.

Not opened. Contents unexamined pending "Analyze now".

### Batch 07 — References  *(final batch — intake closed)*

`intake/materials/07-references/` — 5 PDFs, 26MB.

| File | Pages | Size | Role |
|---|---|---|---|
| `SAMPLE__USE_THIS.pdf` | 1 | 210×297mm | **The target layout.** A per-system product spec sheet for "Superior S60" |
| `Syko_GmbH__Concept__Catalogue_Simplified.pdf` | 1 | 210×297mm | **Byte-identical to the sample** — same file, two names |
| `SAMPLE_BACKGROUND__USE_THIS_AS_BACKGROUND.pdf` | 1 | 210×297mm | The same page with content stripped — the reusable shell |
| `Sykon_Portfolio.pdf` | 80 | 210×297mm | Company copy, completed projects, certification claims |
| `OLD__Sykon_brochure_compressed.pdf` | 14 | 216×303mm | A4 + 3mm bleed. The document this work supersedes |

The sample's own icons are **placeholders** — three 107×107px images repeated
across all 8 typology slots and the spec rows. The real icons are batches 05
and 06.

### Batch 08 — Email conversation  *(final)*

`intake/materials/08-email-convo/` — 6 PDFs, 1.2MB. The project thread,
Mar–May 2026, between Anthony Makhlouf (Sykon GmbH, project lead), Usama Khalid,
Muhammad Ali Zafar and Sujith.

Carries the binding project direction now recorded in `BRAIN.md`: the per-system
then portfolio-wide sequence, Anthony's two design corrections (typologies too
small and not recognisable; reserve space for dimensions and sections), the
freelancer render pipeline, and the schedule pressure.

### PARKED — SY Families (`.rfa` / `.rvt`)

~19 Revit files, ~347MB total. Not uploaded, deliberately. Revisit later.

Two blockers, both real:

- **Unreadable here.** `.rfa` / `.rvt` are proprietary OLE compound formats.
  No Revit on Linux and no parser that yields usable geometry — an embedded
  preview thumbnail and a version string is the ceiling.
- **`SYKON.rvt` is 247MB**, over GitHub's 100MB per-file hard limit. It cannot
  be pushed at all. The `.rfa` files would push but shouldn't — ~100MB of
  binaries in normal git history burdens every future clone. Needs Git LFS.

Two possible purposes, and they lead to different work:

1. *Source for catalogue artwork* → wrong artifact. What the `system` block
   needs is Revit **exports**: section drawings as PDF/DWG (vector, stays crisp
   at print size) and product views as 300dpi PNG, ideally transparent. Roughly
   20–40MB instead of 347MB.
2. *A downloadable BIM library* → a legitimate deliverable in its own right;
   architects search for these. But it is a hosting job, not a repo job —
   cloud storage or CDN with a download page on sykon.ae, and the catalogue
   links out to it.

Unresolved. Ask before acting on either.

---

## Analysis

**Authorised 2026-07-29.** Intake closed at batch 07.

### Direction confirmed by the user

| Question | Answer |
|---|---|
| Scope | **S60 first**, approve the template, then scale to the other nine |
| Fidelity | **Match the sample as closely as it can be measured** |
| Typology naming | Name them from the drawings themselves |
| Portfolio + old brochure | All four roles: mine for copy, treat as superseded, source a projects page, and cross-check for factual conflicts |

### Correction to the record

The user expected the typology SVGs to carry names internally. They do not —
there is no `<title>`, `<desc>` or `<text>` in any of the 53, only Illustrator
UUID ids. Naming therefore has to come from reading the drawings, which is
workable because architectural opening symbols encode the typology visually
(hinge side, fold lines, direction arrows).

### Findings

*Analysis in progress.*
