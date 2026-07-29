# Catalogue config reference

One JSON file describes a catalogue. The engine composes pages from a fixed
block library — a catalogue is a *sequence of blocks*, not a bespoke layout.
That is what makes matching a reference sheet a composition change rather than
a rewrite.

```bash
python catalogue/scripts/build_catalogue.py <config.json> <image_dir> <out_dir>
python catalogue/scripts/verify_layout.py  <config.json> <out_dir>
```

Image values are filenames resolved against `<image_dir>`. Anything missing
renders as a labelled proof plate and is listed in the build report.

## Top level

| Key | Required | Notes |
|---|---|---|
| `slug` | no | Output filename stem. Defaults to the config's filename |
| `title` | yes | PDF title |
| `running` | no | Running footer text. Defaults to "Sykon Aluminium Building Systems" |
| `pages` | yes | Ordered array of blocks |

## Blocks

Every block takes `block`, naming its type. Blocks other than `cover` and `back`
carry a folio and running footer automatically.

### `cover`
| Key | Notes |
|---|---|
| `headline` | Sentence case, ends with a full stop. Set in Hanken Light at 30px |
| `deck` | One or two lines under the headline |
| `strip` | Full-bleed image across the foot — the aluminium extrusion shot |
| `products` | Up to 3 `{name, image}`. Render on tinted discs, overlapping |

### `intro`
`eyebrow`, `heading`, `lead`, `columns` (array of 2 strings), `image` (bottom band).
Use `\n\n` inside a column for a paragraph break.

### `pillars`
`eyebrow`, `heading`, `items` — array of `{title, body}`. Two columns. Six items
is the natural fit for one page.

### `families`
`eyebrow`, `heading`, `items` — array of `{name, image, note}`. Three columns,
each on a tinted disc. Six items fills the page.

### `system`
One system per page.

| Key | Notes |
|---|---|
| `name` | e.g. "SK-70 thermally broken casement." |
| `intro` | One or two sentences |
| `drawing` | Section drawing, sits left |
| `photo` | Application photo, fills the foot |
| `specs_title` / `specs` | Array of `{label, value}` — profile data |
| `performance_title` / `performance` | Array of `{label, value}` — tested classes |

### `highlights`
`eyebrow`, `heading`, `items` (array of strings). Full-bleed red band, two
columns. This is the block the 1-pager leans on.

### `certifications`
`eyebrow`, `heading`, `body`, `marks` — array of `{name, image}`. Four across,
normalised to a common height. Certification marks keep their own colours.

### `serve`
`eyebrow`, `heading`, `groups` — array of `{title, items}`. Two columns.

### `back`
`contact` — `{company, address, phone, email, web}`. Full red, oversized ink
chevron. No folio.

## Adding a block

Write the renderer, register it in `BLOCKS`, and add it to `FOLIO_BLOCKS` if it
should carry running furniture. Take `(b, images, ctx)`; use `head()` for the
eyebrow/heading/rule so the eyebrow does not stretch, `pfoot(ctx)` for the
footer, and `img()` for anything that might be missing.
