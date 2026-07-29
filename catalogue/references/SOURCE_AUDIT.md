# Source audit — the sample sheet vs the system documents

The client designated the ten `.docx` files in
`intake/materials/01-catalogue-materials/` as the source of truth for technical
facts. `SAMPLE__USE_THIS.pdf` was supplied as the **layout** to reproduce.

Checking the sample's figures against `S60  Catalogue material_.docx` showed
that most of them are not in the source. This is consistent with how the sample
was circulated — in the covering email it is described as a concept, with the
note that *"the product picture I used is just the depiction of how the
catalogue will/may look like."* The numbers were illustrative.

So the rule applied throughout: **layout from the sample, every figure from the
`.docx`.** This file records what was dropped and why, so the omissions read as
decisions rather than oversights.

## Certifications & Performance — 5 of 6 rows unsupported

| Sample claims | S60 source says | Action |
|---|---|---|
| Air Permeability — EN 12207, **Class 4** | Class 4 | ✅ kept |
| Watertightness — EN 12208, **Class E1200** | **Class 7A / 3A**. "E1200" is not a valid EN 12208 class | corrected |
| Wind Resistance — **EN 12211**, Class E1200 | **EN 12210, Class C3**. EN 12211 is the test method, EN 12210 the classification | corrected |
| Burglar Resistance — EN 1627, **RC2** | **Absent.** "EN 1627", "RC2" and "burglar" appear zero times | dropped |
| Thermal Insulation — EN 10077, **1.8–2.5 W/m²K** | **Absent.** No U-value anywhere for S60 | dropped |
| Sound Reduction — EN 717, **Rw 36 dB** | **Absent.** No acoustic figure for S60 | dropped |

A certification claim in a specification document carries legal weight. Three of
these do not exist in the source at any strength, so they are not printed — not
even as "on request", which would imply the figure exists and is being withheld.

In their place the sheet publishes the four **ASTM** results the document does
carry (E283 air, E331 static water, E330 serviceability and safety) plus the
test specimen. That is more verified data than the sample showed, not less.

## Technical Specifications

| Sample claims | S60 source says |
|---|---|
| Insulation Type — **Polyamide 24 mm** | The word "polyamide" appears **zero times**. The document says *Thermal construction: Aluminium composite profiles* |
| Glazing Range — **up to 53 mm** | "53" appears **zero times**. Tested to **28 mm**; max **44 mm** fixed and co-planar, **54 mm** overlap sash |
| Maximum Sash Weight — **130 kg** | No max sash weight exists for S60. "130" occurs only inside the profile code `C060-130` |
| Visible Aluminium Face 88–137.5 mm · Frame Height 46–66 mm · Sash 70 × 70–100 mm | No corresponding rows in the source |

The masthead chip strip was rebuilt from source values for the same reason:
system depth, system type, tested glazing and sealing system all appear verbatim
in the document.

## Two design departures from the sample

1. **The typology strip is larger.** Anthony's review: *"The typology section
   appears too small, and the figures do not clearly represent the exact
   typologies."* Cells went from roughly 7mm to 17mm, and the symbols are the
   supplied typology drawings rather than the sample's placeholder — which was
   one 107×107px image repeated across all eight slots.
2. **The product name is not the brand red.** `#C11720` on the ink masthead
   measures **2.77:1**, below even the 3:1 large-text threshold, so the sample's
   red "S60" is illegible by the standard. It is set in `red-on-dark`
   (`#DC1A25`, 3.43:1) — the minimum lift that clears 3:1 while still reading as
   the brand red. `verify_layout.py` enforces this.

## Open items in the source documents

Two systems carry unresolved author queries in their body text. These must be
settled with Sujith or Anthony before anything from those rows is published:

- **SL20**, §2 water result: *"I think this was 180 Pa only when tested?? We
  need to re-test this"*
- **S77**, §16: *"Should we mention the limitations for this system??"* and
  *"This is based on Masters hardware, which we are trying to changed…"*

## Range-wide gaps worth knowing before the extended catalogue

Found while reading all ten documents, not just S60:

- **No burglar resistance data anywhere** — not one system, not one RC class.
- **U-values in 2 of 10** — only SY35 and SY50. The thermally broken systems
  that most need one (S60, SL20, SL450, SL450s, SL580) have none.
- **Acoustic figures in 1 of 10** — only SY50 (38 dB), with the standard given
  as "EN / ASTM" and no number.
- **Standards are not comparable across the range.** Seven systems are ASTM/AAMA
  only, two EN/DIN, and S50 and SL350 have no testing at all. A single shared
  performance table across systems would not be like-for-like.
- **Max sash weight in 4 of 10.**
- **Finishes essentially undocumented** — five say only "min. 75 microns". No
  RAL range, no anodising grades, no QUALICOAT reference, despite SL580 being
  positioned for marine environments.
- **S50 and SL350 have no artwork at all** — a `.docx` each, and nothing in any
  view or drawing batch. Neither can produce a sheet until renders exist.
