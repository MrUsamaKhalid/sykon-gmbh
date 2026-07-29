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

Populated only after **"Analyze now"**.

*(not started)*
