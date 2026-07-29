#!/usr/bin/env python3
"""
Sykon ABS GmbH — typology symbol normaliser.

    python tools/normalise_typologies.py

Reads the supplied typology SVGs and writes cropped copies to
brand/assets/typologies/.

WHY
---
Each supplied SVG carries its own caption baked into the artwork as outlined
paths ("Single tilt & turn casement", "Hinged opening inward door", ...). In a
catalogue the label belongs to the layout, not the icon: the sheet already sets
its own labels in Hanken Grotesk, so the embedded caption duplicates it, sets it
in the wrong face, and — because the caption occupies roughly a third of the
artboard — shrinks the symbol itself.

Anthony's review asked for exactly the opposite: typology figures that are
larger and more clearly recognisable. Cropping the caption away gives the symbol
the whole cell, which is the single cheapest way to satisfy that.

METHOD
------
Render the SVG, find the horizontal band of whitespace separating the drawing
from the caption, and emit a copy whose viewBox stops at that band. Geometry is
untouched — this only changes the window onto it, so nothing is distorted and
the drawing itself remains exactly as supplied.

Where no clean separation is found the file is copied through uncropped rather
than guessed at, and reported.
"""
import os
import re
import hashlib
import sys
import glob
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "intake", "materials", "06-typologies", "Typologies", "SVG")
OUT = os.path.join(ROOT, "brand", "assets", "typologies")

#: A gap must be at least this tall, as a share of the artboard, to count as the
#: break between the symbol and what follows it.
MIN_GAP = 0.025
#: The symbol always occupies at least this much of the artboard, so a gap found
#: above it is interior whitespace rather than the break.
MIN_DRAWING = 0.30


def ink_rows(pix, threshold=246):
    """True for each pixel row that contains any ink."""
    rows = []
    for y in range(pix.height):
        found = False
        for x in range(pix.width):
            r, g, b = pix.pixel(x, y)[:3]
            if r < threshold or g < threshold or b < threshold:
                found = True
                break
        rows.append(found)
    return rows


def drawing_bottom(rows):
    """Bottom of the symbol, as a fraction of height.

    Every supplied file is laid out the same way down the artboard: the opening
    symbol, a band of whitespace, the caption, and on most of them a full-width
    rule at the foot. So the symbol is simply the FIRST contiguous block of ink,
    and the first real gap after it is where to cut.

    Two earlier rules failed on this set and are worth not re-trying. Looking for
    the largest whitespace gap picks the wrong one on files where the caption sits
    tight under the symbol. Looking for the widest ink span picks the foot rule,
    which is wider than the symbol on every sheet that has one.
    """
    h = len(rows)
    y = 0
    while y < h and not rows[y]:
        y += 1
    if y >= h:
        return None
    start = y
    while y < h:
        if rows[y]:
            y += 1
            continue
        run = y
        while run < h and not rows[run]:
            run += 1
        if (run - y) >= h * MIN_GAP and (y - start) >= h * MIN_DRAWING:
            return y / h
        y = run
    return None


def ink_box(pix, y_limit, threshold=246):
    """Ink bounds above `y_limit`, as fractions of the artboard."""
    minx, miny, maxx, maxy = pix.width, y_limit, 0, 0
    for y in range(y_limit):
        for x in range(pix.width):
            r, g, b = pix.pixel(x, y)[:3]
            if r < threshold or g < threshold or b < threshold:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if maxx <= minx or maxy <= miny:
        return None
    return (minx / pix.width, miny / pix.height,
            maxx / pix.width, maxy / pix.height)


def crop(svg_text, box, clip_id):
    """Retarget the viewBox to `box` (l, t, r, b as fractions of the artboard).

    Cropping tight on all four sides — not just below the caption — is what makes
    the icons normalise. Left as-drawn, each symbol carries a different amount of
    slack around it, so identically-sized cells render visibly different symbol
    sizes. Geometry is untouched; only the window onto it changes.
    """
    m = re.search(r'viewBox="([\d.\-\s]+)"', svg_text)
    if not m:
        return None
    x0, y0, w, h = (float(v) for v in m.group(1).split())
    l, t, r, b = box
    pad = 0.02
    nx = x0 + w * max(l - pad, 0)
    ny = y0 + h * max(t - pad, 0)
    nw = w * min(r - l + pad * 2, 1)
    nh = h * min(b - t + pad * 2, 1)
    out = svg_text.replace(m.group(0), 'viewBox="%g %g %g %g"' % (nx, ny, nw, nh), 1)
    # Restate width/height to match the new viewBox, and clip explicitly.
    #
    # Both matter once the file is inlined into HTML rather than opened on its
    # own. An inline <svg> defaults to overflow:visible, so anything outside the
    # viewBox still paints; and with the intrinsic size stripped, Chromium falls
    # back to laying out the whole original artboard. Together those two put the
    # cropped-away caption back on the page even though the viewBox excludes it.
    out = re.sub(r'(<svg[^>]*?)\sheight="[\d.]+"', r"\1", out, count=1)
    out = re.sub(r'(<svg[^>]*?)\swidth="[\d.]+"', r"\1", out, count=1)
    attrs = 'width="%g" height="%g" overflow="hidden" ' % (nw, nh)
    if "preserveAspectRatio" not in out:
        attrs += 'preserveAspectRatio="xMidYMid meet" '
    out = out.replace("<svg ", "<svg " + attrs, 1)

    # Clip explicitly with a clipPath rather than trusting the viewBox alone.
    #
    # Renderers disagree here. PyMuPDF honours the viewBox and drops what falls
    # outside it; Chromium, with the file inlined into HTML, paints the caption
    # anyway. A clipPath is unambiguous to both. The id carries a hash of the
    # filename because eight of these end up inlined into a single page, and a
    # shared id would make every symbol clip to the first one's box.
    cid = "sy-crop-%s" % clip_id
    end = out.index(">", out.index("<svg ")) + 1
    head, body = out[:end], out[end:]
    body = body[: body.rindex("</svg>")]
    return (
        '%s<clipPath id="%s"><rect x="%g" y="%g" width="%g" height="%g"/></clipPath>'
        '<g clip-path="url(#%s)">%s</g></svg>'
        % (head, cid, nx, ny, nw, nh, cid, body)
    )


def main():
    import fitz

    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "*", "*.svg")))
    if not files:
        sys.exit("  no typology SVGs found under %s" % SRC)

    cropped, passed, report = 0, 0, {}
    for f in files:
        raw = open(f, encoding="utf-8", errors="ignore").read()
        rel = os.path.relpath(f, SRC).replace(os.sep, "-")
        try:
            pix = fitz.open("svg", raw.encode())[0].get_pixmap(dpi=140, alpha=False)
        except Exception as e:
            report[rel] = "render failed: %s" % e
            continue

        bottom = drawing_bottom(ink_rows(pix))
        y_limit = int(pix.height * bottom) if bottom is not None else pix.height
        box = ink_box(pix, y_limit)
        if box is None:
            out = raw
            report[rel] = "no ink found — copied uncropped"
            passed += 1
        else:
            out = crop(raw, box, hashlib.md5(rel.encode()).hexdigest()[:8]) or raw
            report[rel] = ("drawing ends %.0f%%, " % (bottom * 100) if bottom else "full height, ") + \
                          "ink box %.2f,%.2f-%.2f,%.2f" % box
            cropped += 1

        with open(os.path.join(OUT, rel), "w", encoding="utf-8") as fh:
            fh.write(out)

    with open(os.path.join(OUT, "_crop-report.json"), "w") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)

    print("  %d SVGs -> brand/assets/typologies/" % len(files))
    print("    %d cropped, %d passed through uncropped" % (cropped, passed))
    if passed:
        print("\n  passed through (check these by eye):")
        for k, v in sorted(report.items()):
            if "uncropped" in v or "failed" in v:
                print("    %-28s %s" % (k, v))


if __name__ == "__main__":
    main()
