# Sykon ABS GmbH — design system

Design tokens, logo and pattern assets, and the catalogue engine for
**Sykon Aluminium Building Systems** (Sykon ABS GmbH) — German-engineered
aluminium profile systems, since 1967.

> **This is not Sykon Properties.** Sykon Properties is the Dubai real-estate
> brokerage, with a monochrome editorial identity set in Inter and no accent
> colour. Sykon ABS is red, industrial and typographically loud. The two brands
> share an owner and nothing else. Never import assets, colours, type or voice
> from one into the other.

## Layout

```
brand/tokens/sykon.tokens.json   the single source of truth — edit this
brand/tokens/build.mjs           generates brand/dist/, and lints the palette
brand/dist/                      generated: CSS vars, Tailwind preset, Python
brand/assets/logo/               8 logo SVGs, rebuilt from the master's vectors
brand/assets/pattern/            chevron, echo stack, band, masthead wave
brand/assets/fonts/              Hanken Grotesk variable woff2 + OFL licence
brand/docs/index.html            living guidelines, renders the tokens directly
catalogue/                       the A4 catalogue engine (JSON -> PDF)
tools/                           asset generators, run against the brand master
```

## Build

```bash
node brand/tokens/build.mjs                      # tokens -> brand/dist/
python tools/build_logos.py <brand-master.pdf>   # regenerate logo SVGs
python tools/build_patterns.py                   # regenerate pattern SVGs
```

The token build fails on a stale contrast claim, a symbol path that disagrees
with its declared aspect ratio, or a non-brand colour leaking into the palette.
Those are not hypothetical — see below.

## What this system fixes

The brand master is a 34-page Illustrator document. Building against it surfaced
several things it gets wrong or leaves unsaid, all resolved here and documented
in `brand/docs/`:

| Issue | Resolution |
|---|---|
| Two different reds in circulation | `#C11720` is the brand red. `#E10916` appears only on the logo-construction spreads (pp. 4, 5, 9) and on no produced application; it is quarantined in a non-brand `doc.*` namespace and the build lints for its escape |
| Page 3 names the typeface as "Neue Montreal" | Wrong. No Neue Montreal is embedded anywhere. The pairing is Swiss 721 BT Black Extended (wordmark only) + Hanken Grotesk |
| Nine near-whites, one declared | Collapsed to `paper`, `paper-warm`, `surface-cool` |
| No clear-space rule, no minimum size | Authored here, derived from the mark's own bar thickness and its most fragile feature |
| Colourways specified for the legacy GmbH mark only | Colourway set authored for the horizontal ABS lockup, the one actually in use |
| The p5 symbol is 1.66% short | A hand-squash defect. Deprecated — never trace it |

## Typography and licensing

Two typefaces, two entirely different legal situations:

- **Hanken Grotesk** — SIL OFL 1.1, free to redistribute. Vendored here as a
  variable woff2 (weight 100–900) with `OFL.txt` alongside, as the licence
  requires.
- **Swiss 721 BT Black Extended** — commercial Bitstream. **Not vendored.** The
  wordmark ships exclusively as outlined SVG, generated from the master by
  `tools/build_logos.py`. The generated files contain artwork, not a font, and
  the extracted subset is written to a gitignored scratch directory. This also
  means the wordmark cannot be mis-set at runtime: there is no live text in any
  logo asset, so no font substitution and no colour drift.

Because Hanken Grotesk has no extended cut, section heads set live will read
narrower than the master's Swiss 721 heads. That is the accepted cost of not
licensing the face. See `brand/docs/` for the two ways out if it matters.

## Colour rules that are not negotiable

- Light type on red or ink is `#F1E9E8`, never pure white.
- **Red is never text on a dark ground.** `#C11720` on `#1C1C1A` measures
  2.77:1 — below even the 3:1 large-text threshold. On dark, red is a graphic
  fill only; copy uses `paper` (15.82:1).
- The brand has **no CMYK, Pantone or ICC specification** — the master contains
  none. Reference values in the docs are marked unverified and must be
  commissioned before any press run, signage or vehicle wrap.
