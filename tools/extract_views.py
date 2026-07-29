#!/usr/bin/env python3
"""
Sykon ABS GmbH — drawing-sheet view extractor.

    python tools/extract_views.py

Pulls each titled view off the drawing sheets in
intake/materials/02-pdf-views/ and writes it as a standalone asset under
catalogue/assets/<system>/.

WHY THIS EXISTS
---------------
Every sheet Sujith produced is a Revit export laid out as an A3 drawing: two
elevations, a 3D view, four to six section details, and a title block. The
catalogue needs those pieces individually — the 3D view as the sheet hero, the
details for the extended catalogue's dimensions section.

They are VECTOR. Rendering a clipped region straight off the sheet gives artwork
sharper than the sample's own hero, which was a 661x1453 raster of the same view.
No Revit round-trip is needed; the export already happened.

HOW THE VIEWS ARE FOUND
-----------------------
By their printed titles, not by fixed coordinates. Revit prints a view title
("3D View", "Detail 1", "Elevation Front") directly beneath each viewport, with
a rule under it. So: find the title text, then take the region ABOVE it, bounded
left and right by its own rule, and above by whatever the next thing up is.

Fixed clip rectangles were the obvious alternative and would not survive: the
sheets carry between four and six details, laid out differently depending on how
many, so a box tuned to one sheet lands on the wrong drawing in another.
"""
import os
import re
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "intake", "materials", "02-pdf-views", "PDF Views")
OUT = os.path.join(ROOT, "catalogue", "assets")

DPI = 600
#: Ignore the title block down the right-hand edge — it holds the Sykon logo,
#: revision table and approval grid, none of which is catalogue artwork.
FRAME_RIGHT = 0.815
#: A view never sits taller than this share of the sheet, so the search upward
#: from a title stops here rather than running into the sheet border.
MAX_VIEW_H = 0.46

TITLE_RE = re.compile(r"^(3D View|Detail \d+|Elevation (?:Front|Back)|Section [A-Z\d]+)$")

#: Sheet number -> system. Taken from the filenames, which are consistent.
SYSTEM_RE = re.compile(r"^\d+-((?:S|SL|SY)\s?\d+s?)", re.I)


def system_of(filename):
    m = SYSTEM_RE.match(os.path.basename(filename))
    if not m:
        return None
    return m.group(1).replace(" ", "").lower()


def slug(title):
    return (title.lower()
            .replace("3d view", "3d")
            .replace("elevation ", "elevation-")
            .replace("detail ", "detail-")
            .replace("section ", "section-")
            .replace(" ", "-"))


def find_titles(page):
    """Every view title on the sheet, with its rectangle."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        for line in blk.get("lines", []):
            text = "".join(s["text"] for s in line["spans"]).strip()
            if TITLE_RE.match(text):
                out.append((text, line["bbox"]))
    return out


def view_region(page, title_bbox, all_titles):
    """The drawing that belongs to a title: the space above it.

    Bounded below by the title, above by MAX_VIEW_H or the foot of any view
    sitting higher in the same column, and horizontally by the midpoints between
    this title and its neighbours on the same row.
    """
    r = page.rect
    x0, y0, x1, y1 = title_bbox
    cx = (x0 + x1) / 2

    same_row = [b for t, b in all_titles
                if abs(((b[1] + b[3]) / 2) - ((y0 + y1) / 2)) < r.height * 0.04]
    same_row.sort(key=lambda b: (b[0] + b[2]) / 2)

    left, right = 0.0, r.width * FRAME_RIGHT
    for b in same_row:
        bcx = (b[0] + b[2]) / 2
        if bcx < cx - 1:
            left = max(left, (bcx + cx) / 2)
        elif bcx > cx + 1:
            right = min(right, (bcx + cx) / 2)

    top = max(0.0, y0 - r.height * MAX_VIEW_H)
    for _, b in all_titles:
        bcx = (b[0] + b[2]) / 2
        if left < bcx < right and b[3] < y0 - r.height * 0.02:
            top = max(top, b[3] + r.height * 0.01)

    # the title itself, and the rule beneath it, are not part of the drawing
    bottom = y0 - r.height * 0.004
    # A title sitting directly under another view collapses the region, and a
    # zero-height clip makes the renderer fail rather than return nothing.
    if bottom - top < r.height * 0.03 or right - left < r.width * 0.02:
        return None
    return (left, top, right, bottom)


def trim_and_knockout(path):
    """Crop to ink and make the paper transparent, so views can overlap freely."""
    from PIL import Image

    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    minx, miny, maxx, maxy = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b, _ = px[x, y]
            if r < 244 or g < 244 or b < 244:
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if maxx <= minx or maxy <= miny:
        return None
    pad = max(2, int(w * 0.004))
    im = im.crop((max(minx - pad, 0), max(miny - pad, 0),
                  min(maxx + pad, w), min(maxy + pad, h)))
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if r > 246 and g > 246 and b > 246:
                px[x, y] = (r, g, b, 0)
    im.save(path)
    return im.size


def main():
    import fitz

    sheets = sorted(f for f in glob.glob(os.path.join(SRC, "*.pdf"))
                    if "Detailed 3D" not in os.path.basename(f)
                    and "Starting View" not in os.path.basename(f)
                    and "_compressed" not in os.path.basename(f))
    if not sheets:
        sys.exit("  no drawing sheets found under %s" % SRC)

    manifest, counts = {}, {}
    for f in sheets:
        sysname = system_of(f)
        if not sysname:
            print("  skipped (no system in filename): %s" % os.path.basename(f))
            continue
        doc = fitz.open(f)
        page = doc[0]
        titles = find_titles(page)
        if not titles:
            print("  %-50s no titled views found" % os.path.basename(f)[:50])
            continue

        outdir = os.path.join(OUT, sysname)
        os.makedirs(outdir, exist_ok=True)

        for title, bbox in titles:
            region = view_region(page, bbox, titles)
            if region is None:
                continue
            x0, y0, x1, y1 = region
            name = "%s-%s" % (sysname, slug(title))
            # a system can appear on several sheets; keep them all, numbered
            n = counts.get(name, 0)
            counts[name] = n + 1
            fname = "%s.png" % (name if n == 0 else "%s-%d" % (name, n + 1))
            path = os.path.join(outdir, fname)

            page.get_pixmap(dpi=DPI, clip=fitz.Rect(x0, y0, x1, y1),
                            alpha=False).save(path)
            size = trim_and_knockout(path)
            if size is None:
                os.remove(path)
                continue
            manifest[os.path.join(sysname, fname)] = {
                "sheet": os.path.basename(f),
                "title": title,
                "px": "%dx%d" % size,
            }

        print("  %-50s %2d views -> catalogue/assets/%s/"
              % (os.path.basename(f)[:50], len(titles), sysname))

    with open(os.path.join(OUT, "_views-manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)

    heroes = sorted(k for k in manifest if k.endswith("-3d.png"))
    print("\n  %d views extracted across %d systems"
          % (len(manifest), len({k.split(os.sep)[0] for k in manifest})))
    print("  %d hero 3D views:" % len(heroes))
    for h in heroes:
        print("    %-34s %s" % (h, manifest[h]["px"]))


if __name__ == "__main__":
    main()
