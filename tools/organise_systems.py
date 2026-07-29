#!/usr/bin/env python3
"""
Sykon ABS GmbH — per-system organiser.

    python tools/organise_systems.py

Builds systems/<SYSTEM>/ — one self-contained folder per system, holding every
source file and every extracted asset that belongs to it — then writes a
coverage report saying what each one is still missing.

    systems/S60/
        source/       the .docx catalogue material — the only source of fact
        views/        Sujith's A3 drawing sheets for this system
        drawings/     large-format sample boards
        extracted/    3D view, elevations and section details, cut from the
                      sheets as individual PNGs
        content/      the sheet config, once written
        README.md     what is here, what is missing

WHY THE MATCHING IS EXPLICIT
----------------------------
Filenames across the batches disagree with each other, and a loose match gets it
wrong in three specific ways:

  * "SL450" is a prefix of "SL450S", so a substring test files SL450S's sheets
    under SL450 as well.
  * "LS450S Sample Board rev01.pdf" is a typo for SL450S — the drawing inside is
    titled "SL 450S".
  * The .docx files space their designations ("SL 450 S") while the drawings do
    not ("SL450S").

So each system declares its own patterns, longest first, and a file is claimed by
the first system that matches it. Nothing is inferred.

The four "Detailed 3D Views" sheets each carry four systems in quadrants, so they
are split by reading the caption printed under each quadrant rather than by
assuming a fixed order.
"""
import os
import re
import sys
import json
import glob
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
M = os.path.join(ROOT, "intake", "materials")
OUT = os.path.join(ROOT, "systems")

DOCX = os.path.join(M, "01-catalogue-materials")
VIEWS = os.path.join(M, "02-pdf-views", "PDF Views")
BOARDS = [os.path.join(M, "03-drawings-batch-a"), os.path.join(M, "04-drawings-batch-b")]

DPI = 600
FRAME_RIGHT = 0.815
#: The sheet border rule sits just inside the page edge. A quadrant clipped to
#: the raw page corner picks it up, and trim_knockout then treats that rule as
#: the drawing's own extent, so the render arrives boxed in on two sides.
FRAME_INSET = 0.025
MAX_VIEW_H = 0.46
TITLE_RE = re.compile(r"^(3D View|Detail \d+|Elevation (?:Front|Back)|Section [A-Z\d]+)$")
#: Revit prints the scale directly beneath each view title ("1 : 20").
SCALE_RE = re.compile(r"^\d+\s*:\s*\d+$")

#: Ordered longest-first. A file is claimed by the first system that matches.
SYSTEMS = [
    ("SL450S", ["sl450s", "sl 450 s", "ls450s"], "Thermal break sliding"),
    ("SL350",  ["sl350", "sl 350"],              "Sliding, non-thermal"),
    ("SL450",  ["sl450", "sl 450"],              "Standard sliding / lift & slide"),
    ("SL580",  ["sl580", "sl 580"],              "Thermal sliding"),
    ("SL20",   ["sl20", "sl 20"],                "Minimal panoramic sliding"),
    ("SY35",   ["sy35", "sy 35"],                "Slim curtain wall"),
    ("SY50",   ["sy50", "sy 50"],                "Curtain wall"),
    ("S77",    ["s77", "s 77"],                  "Bi-folding"),
    ("S60",    ["s60", "s 60"],                  "Casement / door"),
    ("S50",    ["s50", "s 50"],                  "Casement, non-thermal"),
]


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def claim(filename):
    """Which system owns this file? None if it belongs to none or to all."""
    n = norm(filename)
    for designation, pats, _ in SYSTEMS:
        for p in pats:
            if norm(p) in n:
                return designation
    return None


# ----------------------------------------------------------------- extraction

def to_display(page, bbox):
    """Text coordinates -> the space get_pixmap(clip=...) expects.

    These sheets are A3 portrait media rotated 90 degrees for landscape display.
    page.rect reports the rotated box (1191x842) while get_text returns bboxes in
    the unrotated one (842x1191), so a title can come back at y=956 on a page
    that is only 842 tall. Clipping with those numbers renders nothing, which is
    why every 'Detail 1' failed. rotation_matrix maps one space onto the other.
    """
    import fitz

    return tuple(fitz.Rect(bbox) * page.rotation_matrix)


def find_titles(page):
    """Each view's title, paired with the bottom of its whole caption block.

    The caption is two lines — the title and the scale beneath it. The drawing
    above a title has to start below the PREVIOUS row's scale line, not below its
    title, or every detail in the lower row swallows "1 : 20" and a slice of the
    title above it.
    """
    lines = []
    for blk in page.get_text("dict")["blocks"]:
        for line in blk.get("lines", []):
            t = "".join(s["text"] for s in line["spans"]).strip()
            if t:
                lines.append((t, to_display(page, line["bbox"])))

    out = []
    for t, bbox in lines:
        if not TITLE_RE.match(t):
            continue
        caption_bottom = bbox[3]
        cx = (bbox[0] + bbox[2]) / 2
        for t2, b2 in lines:
            if not SCALE_RE.match(t2):
                continue
            # the scale sits just under its own title, roughly beneath it
            if b2[1] >= bbox[3] - 1 and b2[1] - bbox[3] < page.rect.height * 0.05 \
               and b2[0] - 4 <= cx <= b2[2] + page.rect.width * 0.10:
                caption_bottom = max(caption_bottom, b2[3])
        out.append((t, bbox, caption_bottom))
    return out


def view_region(page, bbox, all_titles):
    r = page.rect
    x0, y0, x1, y1 = bbox
    cx = (x0 + x1) / 2
    row = [b for _, b, _ in all_titles
           if abs(((b[1] + b[3]) / 2) - ((y0 + y1) / 2)) < r.height * 0.04]
    left, right = 0.0, r.width * FRAME_RIGHT
    for b in row:
        bcx = (b[0] + b[2]) / 2
        if bcx < cx - 1:
            left = max(left, (bcx + cx) / 2)
        elif bcx > cx + 1:
            right = min(right, (bcx + cx) / 2)
    top = max(0.0, y0 - r.height * MAX_VIEW_H)
    for _, b, cap_bottom in all_titles:
        # Overlap by span, not by centre. A caption whose midpoint sits outside
        # this region can still reach into it — "Elevation Back" is centred left
        # of the detail beneath its right end, and testing the centre let its
        # last letters bleed into that detail.
        if b[2] > left and b[0] < right and cap_bottom < y0 - r.height * 0.02:
            top = max(top, cap_bottom + r.height * 0.012)
    bottom = y0 - r.height * 0.004
    # A title sitting hard under another view collapses the region; a zero-height
    # clip makes the renderer throw rather than return nothing.
    if bottom - top < r.height * 0.03 or right - left < r.width * 0.02:
        return None
    return (left, top, right, bottom)


def trim_knockout(path, thresh=244):
    """Crop to the drawing's ink and make the paper transparent.

    Done with PIL's own band operations rather than a Python pixel loop. These
    are 600dpi crops off A3 sheets — tens of millions of pixels each, across
    ninety-odd views — and a per-pixel loop turns a few seconds into minutes.
    """
    from PIL import Image, ImageChops

    im = Image.open(path).convert("RGB")
    grey = im.convert("L")
    # ink = anything darker than the paper; getbbox() works on non-zero pixels,
    # so threshold to a mask where ink is white and paper is black
    mask = grey.point(lambda v: 255 if v < thresh else 0, mode="L")
    box = mask.getbbox()
    if box is None:
        return None
    pad = max(2, int(im.width * 0.004))
    box = (max(box[0] - pad, 0), max(box[1] - pad, 0),
           min(box[2] + pad, im.width), min(box[3] + pad, im.height))
    im = im.crop(box)
    grey = grey.crop(box)
    # soft alpha: fully opaque ink, fully transparent paper, ramped between so
    # antialiased edges do not fringe against a coloured ground
    alpha = grey.point(lambda v: 255 if v < thresh - 8 else
                       (0 if v > 250 else int((250 - v) * 255 / (250 - thresh + 8))),
                       mode="L")
    im = im.convert("RGBA")
    im.putalpha(alpha)
    im.save(path)
    return im.size


def drop_neighbour_sliver(path, thresh=244):
    """Cut a stray edge fragment off a quadrant render.

    The four models on a 'Detailed 3D Views' sheet are not confined to their own
    quadrant — S60 Side Hung Window's neighbour puts the corner of its plinth
    across the midline, so a half-page clip carries a slice of it.

    Deliberately narrow: only a leading or trailing run narrower than a sixth of
    the image, separated from the body by a blank column band, is dropped. A
    fragment that big or that close is more likely part of the drawing, and this
    is the kind of rule that gets it wrong when it is allowed to be clever.
    """
    from PIL import Image

    im = Image.open(path)
    w, h = im.size
    ink = im.convert("L").point(lambda v: 255 if v < thresh else 0, mode="L")
    if im.mode == "RGBA":  # paper is already transparent — judge on alpha
        ink = im.getchannel("A").point(lambda v: 255 if v > 24 else 0, mode="L")
    cols = [ink.crop((x, 0, x + 1, h)).getbbox() is not None for x in range(w)]

    runs, start = [], None
    for x, on in enumerate(cols + [False]):
        if on and start is None:
            start = x
        elif not on and start is not None:
            runs.append((start, x))
            start = None
    if len(runs) < 2:
        return
    gap = max(4, int(w * 0.03))
    keep = [r for r in runs if r[1] - r[0] >= w / 6]
    if not keep:
        return
    lo, hi = keep[0][0], keep[-1][1]
    for a, b in runs:
        if b <= lo and lo - b >= gap:
            continue          # leading sliver, detached — drop
        if a >= hi and a - hi >= gap:
            continue          # trailing sliver, detached — drop
        lo, hi = min(lo, a), max(hi, b)
    if hi - lo >= w - 2:
        return
    pad = max(2, int(w * 0.004))
    im.crop((max(lo - pad, 0), 0, min(hi + pad, w), h)).save(path)


def slug(t):
    return (t.lower().replace("3d view", "3d").replace("elevation ", "elevation-")
            .replace("detail ", "detail-").replace("section ", "section-")
            .replace(" ", "-"))


def extract_sheet(fitz, pdf, outdir, stem, log):
    doc = fitz.open(pdf)
    page = doc[0]
    titles = find_titles(page)
    if not titles:
        return 0
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for title, bbox, _cap in titles:
        region = view_region(page, bbox, titles)
        if region is None:
            log.append("%s: '%s' region collapsed, skipped" % (stem, title))
            continue
        name = "%s-%s.png" % (stem, slug(title))
        path = os.path.join(outdir, name)
        clip = fitz.Rect(*region) & page.rect
        if clip.is_empty or clip.width < 4 or clip.height < 4:
            log.append("%s: '%s' clip fell outside the page" % (stem, title))
            continue
        try:
            page.get_pixmap(dpi=DPI, clip=clip, alpha=False).save(path)
        except Exception as e:
            log.append("%s: '%s' render failed (%s)" % (stem, title, e))
            continue
        if trim_knockout(path) is None:
            os.remove(path)
            continue
        n += 1
    return n


def split_quadrants(fitz, pdf, log):
    """The 'Detailed 3D Views' sheets hold four systems each.

    Assigned by reading the caption printed under each quadrant, not by assuming
    an order — the four sheets do not use the same one.

    Captions are not all descriptive. Most read "SL580 Monorail Sliding Door",
    but two on sheet 018 are just "SL20" and "SL450". Any minimum-length guard
    drops exactly those two, so the filter is the system match itself.
    """
    doc = fitz.open(pdf)
    page = doc[0]
    r = page.rect
    found = []
    for blk in page.get_text("dict")["blocks"]:
        for line in blk.get("lines", []):
            t = "".join(s["text"] for s in line["spans"]).strip()
            if not t or TITLE_RE.match(t):
                continue
            bbox = to_display(page, line["bbox"])
            # the title block down the right edge repeats designations in its
            # revision and drawing-number cells; those are not quadrant captions
            if (bbox[0] + bbox[2]) / 2 > r.width * FRAME_RIGHT:
                continue
            owner = claim(t)
            if owner:
                found.append((owner, t, bbox))
    out = []
    for owner, caption, bbox in found:
        cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
        qx = 0 if cx < r.width / 2 else 1
        qy = 0 if cy < r.height / 2 else 1
        clip = fitz.Rect(
            max(r.width * 0.5 * qx, r.width * FRAME_INSET),
            max(r.height * 0.5 * qy, r.height * FRAME_INSET),
            # the right-hand quadrants otherwise run straight into the title
            # block, which is where the logo and the revision table live
            min(r.width * 0.5 * (qx + 1), r.width * FRAME_RIGHT),
            bbox[1] - r.height * 0.004)
        out.append((owner, caption, clip))
    return out


# --------------------------------------------------------------------- build

def main():
    import fitz

    if os.path.isdir(OUT):
        shutil.rmtree(OUT)

    index = {d: {"designation": d, "desc": desc, "source": [], "views": [],
                 "drawings": [], "extracted": 0, "content": None, "quadrants": []}
             for d, _, desc in SYSTEMS}
    log, unclaimed = [], []

    # ---- source documents ------------------------------------------------
    for f in sorted(glob.glob(os.path.join(DOCX, "*.docx"))):
        owner = claim(os.path.basename(f))
        if not owner:
            unclaimed.append(("docx", os.path.basename(f)))
            continue
        d = os.path.join(OUT, owner, "source")
        os.makedirs(d, exist_ok=True)
        shutil.copy2(f, d)
        index[owner]["source"].append(os.path.basename(f))

    # ---- drawing sheets --------------------------------------------------
    for f in sorted(glob.glob(os.path.join(VIEWS, "*.pdf"))):
        b = os.path.basename(f)
        if "Detailed 3D" in b or "Starting View" in b:
            continue
        if "_compressed" in b:
            log.append("skipped %s — recompression of the sheet beside it" % b)
            continue
        owner = claim(b)
        if not owner:
            unclaimed.append(("view", b))
            continue
        d = os.path.join(OUT, owner, "views")
        os.makedirs(d, exist_ok=True)
        shutil.copy2(f, d)
        index[owner]["views"].append(b)

    # ---- sample boards ---------------------------------------------------
    for folder in BOARDS:
        for f in sorted(glob.glob(os.path.join(folder, "*.pdf"))):
            b = os.path.basename(f)
            owner = claim(b)
            if not owner:
                unclaimed.append(("board", b))
                continue
            d = os.path.join(OUT, owner, "drawings")
            os.makedirs(d, exist_ok=True)
            shutil.copy2(f, d)
            index[owner]["drawings"].append(b)
            if b.lower().startswith("ls450s"):
                log.append("%s filed under SL450S — 'LS' is a typo, the drawing "
                           "inside is titled 'SL 450S'" % b)

    # ---- cut the titled views out of each sheet --------------------------
    for d in index:
        vdir = os.path.join(OUT, d, "views")
        if not os.path.isdir(vdir):
            continue
        edir = os.path.join(OUT, d, "extracted")
        for f in sorted(glob.glob(os.path.join(vdir, "*.pdf"))):
            stem = re.sub(r"[^A-Za-z0-9]+", "-", os.path.splitext(os.path.basename(f))[0]).strip("-")
            index[d]["extracted"] += extract_sheet(fitz, f, edir, stem, log)

    # ---- the shared 3D quadrant sheets -----------------------------------
    for f in sorted(glob.glob(os.path.join(VIEWS, "*Detailed 3D*.pdf"))):
        for owner, caption, clip in split_quadrants(fitz, f, log):
            edir = os.path.join(OUT, owner, "extracted")
            os.makedirs(edir, exist_ok=True)
            name = "%s-3dview-%s.png" % (
                owner.lower(), re.sub(r"[^A-Za-z0-9]+", "-", caption).strip("-").lower()[:44])
            path = os.path.join(edir, name)
            try:
                fitz.open(f)[0].get_pixmap(dpi=400, clip=clip, alpha=False).save(path)
            except Exception as e:
                log.append("%s quadrant '%s' failed (%s)" % (owner, caption, e))
                continue
            if trim_knockout(path) is None:
                os.remove(path)
                continue
            drop_neighbour_sliver(path)
            index[owner]["quadrants"].append(caption)
            index[owner]["extracted"] += 1

    # ---- range-wide artwork ------------------------------------------------
    # "Starting View" is the whole model set in one exploded row. It belongs to
    # no single system, so it goes to _shared/ rather than being reported as an
    # unclaimed file.
    shared = os.path.join(OUT, "_shared")
    for f in sorted(glob.glob(os.path.join(VIEWS, "*Starting View*.pdf"))):
        os.makedirs(shared, exist_ok=True)
        shutil.copy2(f, shared)
        page = fitz.open(f)[0]
        clip = fitz.Rect(page.rect.width * FRAME_INSET,
                         page.rect.height * FRAME_INSET,
                         page.rect.width * FRAME_RIGHT,
                         page.rect.height * (1 - FRAME_INSET))
        dest = os.path.join(shared, "range-starting-view.png")
        page.get_pixmap(dpi=400, clip=clip, alpha=False).save(dest)
        if trim_knockout(dest) is None:
            os.remove(dest)
        log.append("%s is the whole range in one view, not one system — filed "
                   "under systems/_shared/" % os.path.basename(f))

    # ---- sheet configs ---------------------------------------------------
    for f in glob.glob(os.path.join(ROOT, "catalogue", "examples", "*-sheet.json")):
        cfg = json.load(open(f))
        owner = (cfg.get("system") or "").upper()
        if owner in index:
            d = os.path.join(OUT, owner, "content")
            os.makedirs(d, exist_ok=True)
            shutil.copy2(f, d)
            index[owner]["content"] = os.path.basename(f)

    # ---- per-system README ------------------------------------------------
    for d, info in index.items():
        base = os.path.join(OUT, d)
        os.makedirs(base, exist_ok=True)
        miss = []
        if not info["source"]:
            miss.append("**the .docx catalogue material** — nothing can be written without it")
        if not info["views"]:
            miss.append("**drawing sheets** — no elevations, no 3D view, no section details")
        if not info["drawings"]:
            miss.append("**sample boards** — no large-format section board")
        if not info["extracted"]:
            miss.append("**extracted artwork** — nothing to place on a sheet")
        if not info["content"]:
            miss.append("**sheet config** — the page has not been written yet")

        L = ["# %s — %s" % (d, info["desc"]), ""]
        L += ["Everything for this system lives in this folder.", ""]
        for key, title in (("source", "Source document (the only source of fact)"),
                           ("views", "Drawing sheets"),
                           ("drawings", "Sample boards")):
            L += ["## %s" % title, ""]
            L += (["- `%s`" % x for x in info[key]] if info[key]
                  else ["*(none)*"])
            L += [""]
        L += ["## Extracted artwork", "",
              "%d file(s) in `extracted/`" % info["extracted"] if info["extracted"]
              else "*(none)*", ""]
        L += ["## Sheet", "",
              "`content/%s`" % info["content"] if info["content"]
              else "*(not written)*", ""]
        L += ["## Missing", ""]
        L += (["- %s" % x for x in miss] if miss else ["*(nothing — this system is complete)*"])
        L += [""]
        open(os.path.join(base, "README.md"), "w").write("\n".join(L))
        info["missing"] = miss

    # ---- coverage report ---------------------------------------------------
    L = ["# Coverage — what each system has, and what it is missing", "",
         "Generated by `tools/organise_systems.py`. Every system's files are in "
         "`systems/<SYSTEM>/`.", "",
         "| System | Description | .docx | Sheets | Boards | Extracted | Config |",
         "|---|---|---|---|---|---|---|"]
    for d, _, desc in SYSTEMS:
        i = index[d]
        L.append("| **%s** | %s | %s | %d | %d | %d | %s |" % (
            d, desc,
            "yes" if i["source"] else "**NO**",
            len(i["views"]), len(i["drawings"]), i["extracted"],
            "yes" if i["content"] else "no"))
    L += ["", "## What each system is missing", ""]
    for d, _, _ in SYSTEMS:
        i = index[d]
        L.append("### %s" % d)
        L.append("")
        L += (["- %s" % x for x in i["missing"]] if i["missing"]
              else ["*(nothing)*"])
        L.append("")
    if unclaimed:
        L += ["## Files claimed by no system", ""]
        for kind, name in unclaimed:
            L.append("- `%s` (%s)" % (name, kind))
        L.append("")
    if log:
        L += ["## Notes from the build", ""]
        for x in log:
            L.append("- %s" % x)
        L.append("")
    open(os.path.join(OUT, "_COVERAGE.md"), "w").write("\n".join(L))
    json.dump(index, open(os.path.join(OUT, "_index.json"), "w"), indent=2)

    # ---- console ------------------------------------------------------------
    print("\n  systems/ built\n")
    print("  %-8s %-32s %-6s %-7s %-7s %-10s %s"
          % ("SYSTEM", "DESCRIPTION", ".docx", "sheets", "boards", "extracted", "config"))
    for d, _, desc in SYSTEMS:
        i = index[d]
        print("  %-8s %-32s %-6s %-7d %-7d %-10d %s"
              % (d, desc[:32], "yes" if i["source"] else "NO",
                 len(i["views"]), len(i["drawings"]), i["extracted"],
                 "yes" if i["content"] else "-"))
    print("\n  systems/_COVERAGE.md written")
    if unclaimed:
        print("  %d file(s) claimed by no system" % len(unclaimed))


if __name__ == "__main__":
    main()
