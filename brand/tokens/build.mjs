#!/usr/bin/env node
/**
 * Sykon ABS GmbH — token build.
 *
 *   node brand/tokens/build.mjs
 *
 * Reads sykon.tokens.json (the only source of truth) and writes brand/dist/:
 *   sykon.css            CSS custom properties
 *   sykon.tailwind.js    Tailwind preset
 *   sykon_tokens.py      consumed by the catalogue engine
 *
 * Zero dependencies. Node 18+.
 *
 * The build fails loudly on two things, both of which are real failure modes
 * this brand has already suffered:
 *   1. a doc.* (non-brand) colour reachable from a brand surface
 *   2. a colour pairing whose contrast is below what its documented role needs
 */
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const HERE = dirname(fileURLToPath(import.meta.url))
const ROOT = join(HERE, '..')
const DIST = join(ROOT, 'dist')

const T = JSON.parse(readFileSync(join(HERE, 'sykon.tokens.json'), 'utf8'))

/* ---------------------------------------------------------------- colour */

const srgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16) / 255)
const lin = (c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
const lum = (h) => {
  const [r, g, b] = srgb(h).map(lin)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}
const contrast = (a, b) => {
  const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p)
  return (x + 0.05) / (y + 0.05)
}

/* ------------------------------------------------------------- validate */

const errors = []
const warnings = []

// 1. The doc.* namespace must not leak. Any doc value that also appears as a
//    brand colour means the diagram red has re-entered the system.
const brandHexes = new Map()
for (const [k, v] of Object.entries(T.color)) {
  if (k.startsWith('$')) continue
  brandHexes.set(v.value.toUpperCase(), k)
}
for (const [k, v] of Object.entries(T.doc)) {
  if (k.startsWith('$')) continue
  const hex = v.value.toUpperCase()
  if (brandHexes.has(hex)) {
    errors.push(
      `doc.${k} (${hex}) is also published as color.${brandHexes.get(hex)}. ` +
        `The non-brand namespace has leaked into the brand palette.`
    )
  }
}

// 2. Contrast claims in the token file must be true. A stale contrast number is
//    worse than none, because it gets quoted in reviews.
const PAIRS = [
  ['red', 'paper', 'on_paper'],
  ['red', 'ink', 'on_ink'],
  ['red-hover', 'paper', 'on_paper'],
  ['red-hover', 'ink', 'on_ink'],
]
for (const [fg, bg, key] of PAIRS) {
  const claimed = T.color[fg]?.contrast?.[key]
  if (claimed == null) continue
  const actual = contrast(T.color[fg].value, T.color[bg].value)
  if (Math.abs(actual - claimed) > 0.02) {
    errors.push(
      `color.${fg}.contrast.${key} claims ${claimed}:1 but measures ${actual.toFixed(2)}:1`
    )
  }
}

// 3. Red on ink is the pairing this brand keeps reaching for and cannot have.
//    Surface it every build so nobody rediscovers it in print.
const redOnInk = contrast(T.color.red.value, T.color.ink.value)
if (redOnInk < 3.0) {
  warnings.push(
    `color.red on color.ink is ${redOnInk.toFixed(2)}:1 — below 3:1, so it fails even ` +
      `the large-text threshold. Red is a GRAPHIC FILL ONLY on dark grounds; it is ` +
      `never text there. Use color.paper for dark-surface copy (${contrast(
        T.color.paper.value,
        T.color.ink.value
      ).toFixed(2)}:1).`
  )
}

// 4. The symbol aspect must match the path it ships with.
const seg = T.symbol.path.match(/-?\d+(?:\.\d+)?/g).map(Number)
const xs = seg.filter((_, i) => i % 2 === 0)
const ys = seg.filter((_, i) => i % 2 === 1)
const aspect = (Math.max(...xs) - Math.min(...xs)) / (Math.max(...ys) - Math.min(...ys))
if (Math.abs(aspect - T.symbol.aspect) > 0.001) {
  errors.push(
    `symbol.aspect declares ${T.symbol.aspect} but the shipped path measures ${aspect.toFixed(5)}`
  )
}

if (errors.length) {
  console.error('\n  TOKEN BUILD FAILED\n')
  for (const e of errors) console.error(`   x  ${e}`)
  console.error('')
  process.exit(1)
}

/* ----------------------------------------------------------------- emit */

const BANNER = `Sykon ABS GmbH design tokens — GENERATED, DO NOT EDIT.
Source: brand/tokens/sykon.tokens.json
Rebuild: node brand/tokens/build.mjs

Sykon Aluminium Building Systems is NOT Sykon Properties.
Do not import Sykon Properties assets, colours or type into this system.`

const colorVars = Object.entries(T.color)
  .filter(([k]) => !k.startsWith('$'))
  .map(([k, v]) => `  --sy-${k}: ${v.value};`)
  .join('\n')

const docVars = Object.entries(T.doc)
  .filter(([k]) => !k.startsWith('$'))
  .map(([k, v]) => `  --sy-doc-${k}: ${v.value};`)
  .join('\n')

const weightVars = Object.entries(T.type.weight)
  .map(([k, v]) => `  --sy-weight-${k}: ${v.value};`)
  .join('\n')

const leadVars = Object.entries(T.type.leading)
  .map(([k, v]) => `  --sy-leading-${k}: ${v};`)
  .join('\n')

const spaceVars = T.space.scale.map((n) => `  --sy-space-${n}: ${n}mm;`).join('\n')

const css = `/*
${BANNER}
*/

:root {
  /* --- brand colour ------------------------------------------------- */
${colorVars}

  /* --- non-brand: construction/anatomy artwork ONLY ------------------
     Never use these on a brand surface. See tokens.doc.$warning.       */
${docVars}

  /* --- type ---------------------------------------------------------- */
  --sy-font-text: "${T.type.text.family}", ${T.type.text.fallback.map((f) => (f.includes(' ') ? `"${f}"` : f)).join(', ')};
${weightVars}
${leadVars}
  --sy-tracking-none: ${T.type.tracking.none};
  --sy-tracking-caps-label: ${T.type.tracking['caps-label']};
  --sy-tracking-caps-display: ${T.type.tracking['caps-display']};

  /* --- space --------------------------------------------------------- */
  --sy-margin: ${T.space['margin-mm']}mm;
  --sy-bleed: ${T.space['bleed-mm']}mm;
  --sy-gutter: ${T.space['gutter-mm']}mm;
${spaceVars}

  /* --- radius -------------------------------------------------------- */
  --sy-radius-pill: ${T.radius.pill.value};
  --sy-radius-circle: ${T.radius.circle.value};
}

/* Ligatures stay on. The brand's own copy relies on them —
   "profile", "fluid", "flow", "certifications". */
.sy-text {
  font-family: var(--sy-font-text);
  font-feature-settings: "liga" 1, "kern" 1;
  font-weight: var(--sy-weight-regular);
  line-height: var(--sy-leading-body);
  color: var(--sy-ink);
}

/* Buttons — the book sanctions exactly two. No ghost/outline variant exists. */
.sy-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0 20px;
  border: 0;
  border-radius: 9px; /* 0.20 x 44px control height */
  font-family: var(--sy-font-text);
  font-weight: var(--sy-weight-medium);
  font-size: 15px;
  cursor: pointer;
}
.sy-btn--primary { background: var(--sy-red); color: var(--sy-paper-warm); }
.sy-btn--primary:hover { background: var(--sy-red-hover); }
.sy-btn--secondary { background: #fff; color: var(--sy-ink); }

/* RESERVED shape. Not a button — the eyebrow tag and nothing else. */
.sy-tag {
  display: inline-block;
  border-radius: var(--sy-radius-pill);
  background: var(--sy-red-tint-17);
  color: var(--sy-red);
  padding: 6px 16px;
  font-size: 13px;
  font-weight: var(--sy-weight-medium);
}

/* Dark sections. Red is a graphic fill here, never type — it measures
   ${redOnInk.toFixed(2)}:1 on ink, below even the large-text threshold. */
.sy-on-ink { background: var(--sy-ink); color: var(--sy-paper); }
.sy-on-red { background: var(--sy-red); color: var(--sy-paper-warm); }
`

const tailwind = `/*
${BANNER}
*/
export default {
  theme: {
    extend: {
      colors: {
        sykon: {
${Object.entries(T.color)
  .filter(([k]) => !k.startsWith('$'))
  .map(([k, v]) => `          "${k}": "${v.value}",`)
  .join('\n')}
        },
      },
      fontFamily: {
        sykon: [${[T.type.text.family, ...T.type.text.fallback].map((f) => `"${f}"`).join(', ')}],
      },
      fontWeight: {
${Object.entries(T.type.weight)
  .map(([k, v]) => `        "sykon-${k}": "${v.value}",`)
  .join('\n')}
      },
      lineHeight: {
${Object.entries(T.type.leading)
  .map(([k, v]) => `        "sykon-${k}": "${v}",`)
  .join('\n')}
      },
      borderRadius: {
        "sykon-pill": "${T.radius.pill.value}",
      },
    },
  },
}
`

const py = `# ${BANNER.split('\n').join('\n# ')}

RED           = "${T.color.red.value}"
RED_HOVER     = "${T.color['red-hover'].value}"
RED_TINT_29   = "${T.color['red-tint-29'].value}"
RED_TINT_17   = "${T.color['red-tint-17'].value}"
RED_TINT_12   = "${T.color['red-tint-12'].value}"
INK           = "${T.color.ink.value}"
PAPER         = "${T.color.paper.value}"
PAPER_WARM    = "${T.color['paper-warm'].value}"
SURFACE_COOL  = "${T.color['surface-cool'].value}"
PAPER_COOL    = "${T.color['paper-cool'].value}"

# NON-BRAND. Construction/anatomy artwork only. Never on a brand surface.
DOC_GRID_LINE = "${T.doc['grid-line'].value}"

FONT_TEXT     = "${T.type.text.family}"
FONT_FALLBACK = ${JSON.stringify(T.type.text.fallback)}

W_LIGHT, W_REGULAR, W_MEDIUM, W_BOLD = ${T.type.weight.light.value}, ${T.type.weight.regular.value}, ${T.type.weight.medium.value}, ${T.type.weight.bold.value}

LEAD_DISPLAY = ${T.type.leading.display}
LEAD_BODY    = ${T.type.leading.body}
LEAD_CAPTION = ${T.type.leading.caption}
LEAD_TIGHT   = ${T.type.leading.tight}

MARGIN_MM = ${T.space['margin-mm']}
BLEED_MM  = ${T.space['bleed-mm']}
GUTTER_MM = ${T.space['gutter-mm']}

PAGE_W_MM = ${T.page['a4-portrait'].width_mm}
PAGE_H_MM = ${T.page['a4-portrait'].height_mm}

SYMBOL_VIEWBOX = "${T.symbol.viewBox}"
SYMBOL_ASPECT  = ${T.symbol.aspect}
SYMBOL_PATH    = "${T.symbol.path}"
SYMBOL_T       = ${T.symbol.module.t}          # bar thickness / height — the spacing module
CLEAR_SPACE_T  = 1.5                            # multiples of SYMBOL_T, all four sides
MIN_H_PRINT_MM = ${T.symbol.min_height_print_mm}
MIN_H_SCREEN_PX = ${T.symbol.min_height_screen_px}

# Red on ink measures ${redOnInk.toFixed(2)}:1 — below 3:1. On dark grounds red is a
# GRAPHIC FILL ONLY, never text. Dark-surface copy uses PAPER.
RED_IS_TEXT_SAFE_ON_INK = False
`

mkdirSync(DIST, { recursive: true })
writeFileSync(join(DIST, 'sykon.css'), css)
writeFileSync(join(DIST, 'sykon.tailwind.js'), tailwind)
writeFileSync(join(DIST, 'sykon_tokens.py'), py)

console.log('  built brand/dist/')
console.log('    sykon.css')
console.log('    sykon.tailwind.js')
console.log('    sykon_tokens.py')
for (const w of warnings) console.log(`\n  note: ${w}`)
