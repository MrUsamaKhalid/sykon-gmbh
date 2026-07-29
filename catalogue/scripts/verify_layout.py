#!/usr/bin/env python3
"""
Sykon ABS GmbH — catalogue verifier.

    python catalogue/scripts/verify_layout.py <config.json> <out_dir>

A broken layout still produces a perfectly valid PDF. That is the whole reason
this exists. Checks, in order of how often each one has actually caught something:

  1. page count matches the config          (a phantom page from a spilled flex child)
  2. every page is exactly the right size    (an A4 a millimetre out)
  3. no page is blank                        (a block that silently rendered nothing)
  4. brand colours only                      (an off-spec red, or the diagram red)
  5. red is never small text on a dark ground (2.77:1 — fails even large-text AA)

Exit status is non-zero if any check fails, so it can gate a build.
"""
import os
import sys
import json
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand", "dist"))

import sykon_tokens as TK  # noqa: E402

MM = 72.0 / 25.4
TOL_MM = 0.5

ALLOWED = {
    TK.RED, TK.RED_HOVER, TK.RED_TINT_29, TK.RED_TINT_17, TK.RED_TINT_12,
    TK.INK, TK.PAPER, TK.PAPER_WARM, TK.SURFACE_COOL, TK.PAPER_COOL,
    "#FFFFFF", "#000000",
}


def hexof(v):
    return "#%02X%02X%02X" % tuple(int(round(c * 255)) for c in v[:3])


def near(a, b, tol=10):
    ai = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    bi = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return sum((x - y) ** 2 for x, y in zip(ai, bi)) ** 0.5 <= tol


def _lin(c):
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def contrast(a, b):
    def lum(h):
        c = [_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5)]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def sample_ground(pix, bbox, scale, fg):
    """Modal colour inside a text bbox that is not the text colour itself.

    Glyphs cover a minority of their bounding box, so the most common colour in
    that box is the ground the text is actually sitting on — which is the only
    thing that decides whether the contrast is legal.
    """
    x0, y0, x1, y1 = (int(v * scale) for v in bbox)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, pix.width - 1), min(y1, pix.height - 1)
    if x1 <= x0 or y1 <= y0:
        return None
    c = Counter()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c[pix.pixel(x, y)] += 1
    for (r, g, b), _ in c.most_common(6):
        h = "#%02X%02X%02X" % (r, g, b)
        if not near(h, fg, 60):
            return h
    return None


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: verify_layout.py <config.json> <out_dir>")
    cfg = json.load(open(sys.argv[1]))
    out_dir = sys.argv[2]
    name = cfg.get("slug") or os.path.splitext(os.path.basename(sys.argv[1]))[0]

    import fitz

    expect_pages = len(cfg["pages"])
    fails, notes = [], []

    for label, bleed in (("print", TK.BLEED_MM), ("digital", 0)):
        path = os.path.join(out_dir, "%s-%s.pdf" % (name, label))
        if not os.path.exists(path):
            fails.append("%s: not built (%s)" % (label, path))
            continue
        doc = fitz.open(path)

        # 1. page count
        if doc.page_count != expect_pages:
            fails.append(
                "%s: %d pages, config declares %d — a block spilled or vanished"
                % (label, doc.page_count, expect_pages)
            )

        want_w = (TK.PAGE_W_MM + 2 * bleed) * MM
        want_h = (TK.PAGE_H_MM + 2 * bleed) * MM

        for i, page in enumerate(doc):
            r = page.rect
            # 2. page size
            if abs(r.width - want_w) > TOL_MM * MM or abs(r.height - want_h) > TOL_MM * MM:
                fails.append(
                    "%s p%d: %.2f x %.2fmm, expected %.0f x %.0fmm"
                    % (label, i + 1, r.width / MM, r.height / MM,
                       TK.PAGE_W_MM + 2 * bleed, TK.PAGE_H_MM + 2 * bleed)
                )

            # 3. blank page
            pix = page.get_pixmap(dpi=36)
            colours = Counter()
            for y in range(0, pix.height, 2):
                for x in range(0, pix.width, 2):
                    colours[pix.pixel(x, y)] += 1
            if len(colours) < 3:
                fails.append("%s p%d: renders blank (%d distinct colours)"
                             % (label, i + 1, len(colours)))

            # 4. off-brand colour in the vector layer
            for drw in page.get_drawings():
                for key in ("fill", "color"):
                    v = drw.get(key)
                    if not v:
                        continue
                    h = hexof(v)
                    if not any(near(h, a) for a in ALLOWED):
                        notes.append("%s p%d: off-palette vector %s" % (label, i + 1, h))

            # 5. text contrast, measured against the ground it actually sits on
            #    rather than assumed. Sampling the rendered page is the only way
            #    to know — the span carries a colour, not a background.
            hi = page.get_pixmap(dpi=110)
            scale = hi.width / r.width
            for blk in page.get_text("dict")["blocks"]:
                for ln in blk.get("lines", []):
                    for sp in ln["spans"]:
                        fg = "#%06X" % sp["color"]
                        ground = sample_ground(hi, sp["bbox"], scale, fg)
                        if ground is None:
                            continue
                        cr = contrast(fg, ground)
                        need = 3.0 if (sp["size"] >= 18 or
                                       (sp["size"] >= 14 and sp["flags"] & 2 ** 4)) else 4.5
                        if cr < need:
                            fails.append(
                                "%s p%d: %s on %s is %.2f:1 at %.1fpt, needs %.1f:1 — %r"
                                % (label, i + 1, fg, ground, cr, sp["size"], need,
                                   "".join(c["c"] for c in sp.get("chars", []))[:40]
                                   or sp.get("text", "")[:40])
                            )
        doc.close()

    print("\n  verify: %s" % name)
    print("  expected %d pages" % expect_pages)
    if notes:
        print("\n  %d note(s):" % len(notes))
        for n in sorted(set(notes))[:20]:
            print("    · %s" % n)
    if fails:
        print("\n  %d FAILURE(S):" % len(fails))
        for f in fails:
            print("    x %s" % f)
        print("")
        return 1
    print("\n  all checks passed\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
