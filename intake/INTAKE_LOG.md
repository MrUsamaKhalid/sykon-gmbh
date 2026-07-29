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
| 02 | — | *(expected)* PDF — different views | — | |

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
