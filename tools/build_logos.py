#!/usr/bin/env python3
"""
Sykon ABS GmbH — logo asset generator.

    python tools/build_logos.py <path-to-brand-master.pdf>

Rebuilds every logo SVG in brand/assets/logo/ from the brand master PDF.

WHY THIS EXISTS AS A SCRIPT RATHER THAN HAND-DRAWN FILES
--------------------------------------------------------
The wordmark is set in Swiss 721 BT Black Extended, a licensed Bitstream face.
We are not permitted to redistribute the font, and we do not: this script reads
the font subset out of the brand master (which the brand owner licenses), pulls
only the outlines of the 16 characters the wordmark uses, and writes them as
vector paths. The generated SVGs contain artwork, not a font. The extracted
font file is written to a gitignored scratch directory and never committed.

That also means the wordmark can never be mis-set at runtime — there is no live
text in any logo asset, so no font substitution and no colour drift.

MEASUREMENTS
------------
Every number below was measured from the master, not chosen:

  symbol            254.821 x 112.913 pt, aspect 2.25679 (p4)
  wordmark size     39.2946 pt
  wordmark leading  47.1535 pt = 1.2000 em
  tagline size      22.7903 pt = 0.58 x wordmark
  symbol -> type    27.918 pt = 0.1096 x symbol width
  vertical centring the symbol centres on the FULL text block including the
                    tagline (symbol centre 540.000, full block centre 539.41,
                    wordmark-only centre 519.195 — a 20.8pt miss)
"""
import os
import re
import sys
import json
from io import BytesIO

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "brand", "assets", "logo")
SCRATCH = os.path.join(ROOT, ".scratch")
TOKENS = json.load(open(os.path.join(ROOT, "brand", "tokens", "sykon.tokens.json")))

RED = TOKENS["color"]["red"]["value"]
INK = TOKENS["color"]["ink"]["value"]
PAPER_WARM = TOKENS["color"]["paper-warm"]["value"]
SYMBOL_PATH = TOKENS["symbol"]["path"]
SYMBOL_ASPECT = TOKENS["symbol"]["aspect"]

# --- measured from the master, page 4 horizontal lockup -------------------
WM_SIZE = 39.2946
WM_LEADING = 47.1535
TAG_SIZE = 22.7903
SYM_W = 254.821
SYM_H = 112.913
GAP = 27.918
LINE1_A, LINE1_B = "SYKON ", "ALUMINIUM"
LINE2 = "BUILDING SYSTEMS"
TAGLINE = "German Engineering System Since 1967"


def die(msg):
    sys.stderr.write("  error: %s\n" % msg)
    sys.exit(1)


# ---------------------------------------------------------------- extract

def extract_fonts(pdf_path):
    """Pull the embedded font subsets out of the master into .scratch/."""
    import fitz

    os.makedirs(SCRATCH, exist_ok=True)
    doc = fitz.open(pdf_path)
    found = {}
    seen = set()
    for i in range(doc.page_count):
        for f in doc[i].get_fonts(full=True):
            xref, name = f[0], f[3]
            if name in seen:
                continue
            seen.add(name)
            try:
                _, ext, _, content = doc.extract_font(xref)[:4]
            except Exception:
                continue
            if not content:
                continue
            path = os.path.join(SCRATCH, "%s.%s" % (name, ext))
            with open(path, "wb") as fh:
                fh.write(content)
            found[name] = path
    return doc, found


def glyph_positions(doc):
    """Exact per-glyph x offsets of the wordmark, as drawn on page 4.

    Read rather than modelled. The artwork applies Tc -40/1000 with per-glyph
    exceptions; reproducing the positions verbatim sidesteps having to guess
    which exceptions are deliberate.
    """
    page = doc[3]  # page 4
    lines = []
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if "Swiss" not in s["font"]:
                    continue
                lines.append(
                    {
                        "color": "#%06X" % s["color"],
                        "origin_y": round(s["origin"][1], 4),
                        "chars": [(c["c"], c["origin"][0]) for c in s["chars"]],
                    }
                )
    if not lines:
        die("no Swiss 721 wordmark spans found on page 4 of the master")
    return lines


def tagline_positions(doc):
    page = doc[3]
    for b in page.get_text("rawdict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if "Hanken" not in s["font"]:
                    continue
                text = "".join(c["c"] for c in s["chars"])
                if TAGLINE not in text:
                    continue
                return {
                    "font": s["font"],
                    "size": s["size"],
                    "origin_y": s["origin"][1],
                    "chars": [(c["c"], c["origin"][0]) for c in s["chars"]],
                }
    die("tagline span not found on page 4 of the master")


# ------------------------------------------------------------------ glyphs

def cff_glyph_paths(cff_path):
    """{glyphname: SVG path data} in 1000-unit em space, Y-up."""
    from fontTools.cffLib import CFFFontSet
    from fontTools.pens.svgPathPen import SVGPathPen

    cff = CFFFontSet()
    cff.decompile(BytesIO(open(cff_path, "rb").read()), None)
    td = cff[cff.fontNames[0]]
    out = {}
    for name in td.CharStrings.keys():
        pen = SVGPathPen(None)
        td.CharStrings[name].draw(pen)
        d = pen.getCommands()
        if d:
            out[name] = d
    return out


def ttf_glyph_paths(ttf_path):
    """{char: (svg_path, upem)} for a TrueType subset."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen

    font = TTFont(ttf_path)
    upem = font["head"].unitsPerEm
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    out = {}
    for code, gname in cmap.items():
        pen = SVGPathPen(gs)
        gs[gname].draw(pen)
        d = pen.getCommands()
        out[chr(code)] = (d, upem)
    return out


CHAR_TO_GLYPH = {
    " ": "space",
    "A": "A", "B": "B", "D": "D", "E": "E", "G": "G", "I": "I", "K": "K",
    "L": "L", "M": "M", "N": "N", "O": "O", "S": "S", "T": "T", "U": "U",
    "Y": "Y",
}


def place(d, x, baseline_y, size, upem=1000.0):
    """Transform a glyph path from font units (Y-up) into page space (Y-down)."""
    s = size / upem
    return (
        '<g transform="translate(%.4f %.4f) scale(%.6f %.6f)">'
        '<path d="%s"/></g>' % (x, baseline_y, s, -s, d)
    )


# ------------------------------------------------------------------- build

def build(pdf_path):
    doc, fonts = extract_fonts(pdf_path)

    swiss = next((p for n, p in fonts.items() if "Swiss721" in n), None)
    if not swiss:
        die("Swiss 721 subset not embedded in %s" % pdf_path)
    hanken_reg = next(
        (p for n, p in fonts.items() if "HankenGrotesk-Regular" in n and p.endswith(".ttf")),
        None,
    )

    swiss_glyphs = cff_glyph_paths(swiss)
    hanken_glyphs = ttf_glyph_paths(hanken_reg) if hanken_reg else {}

    wm = glyph_positions(doc)
    tag = tagline_positions(doc)

    # Origin: the lockup bounding box, translated to 0,0.
    sym_x0, sym_y0 = 919.221, 483.543
    all_x = [x for ln in wm for _, x in ln["chars"]] + [x for _, x in tag["chars"]]
    x0 = sym_x0
    # top of the lockup box = wordmark cap top on page 4
    y0 = 476.698
    tag_bottom = 602.115
    total_w = 1728.547 - x0
    total_h = tag_bottom - y0

    def sym_group(fill, x, y, h):
        w = h * SYMBOL_ASPECT
        s = h / 100.0
        return (
            '  <g transform="translate(%.4f %.4f) scale(%.6f)" fill="%s">\n'
            '    <path d="%s"/>\n  </g>\n' % (x, y, s, fill, SYMBOL_PATH)
        )

    def wordmark_groups(color_map):
        out = []
        for ln in wm:
            fill = color_map(ln["color"])
            parts = []
            for ch, x in ln["chars"]:
                g = CHAR_TO_GLYPH.get(ch)
                if not g or g not in swiss_glyphs:
                    continue
                parts.append(place(swiss_glyphs[g], x - x0, ln["origin_y"] - y0, WM_SIZE))
            if parts:
                out.append('  <g fill="%s">\n    %s\n  </g>\n' % (fill, "\n    ".join(parts)))
        return "".join(out)

    def tagline_group(fill):
        parts = []
        for ch, x in tag["chars"]:
            if ch not in hanken_glyphs:
                continue
            d, upem = hanken_glyphs[ch]
            if not d:
                continue
            parts.append(place(d, x - x0, tag["origin_y"] - y0, tag["size"], upem))
        if not parts:
            return ""
        return '  <g fill="%s">\n    %s\n  </g>\n' % (fill, "\n    ".join(parts))

    def svg(body, w, h, title):
        return (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %.3f %.3f" '
            'role="img" aria-label="%s">\n'
            "  <title>%s</title>\n%s</svg>\n" % (w, h, title, title, body)
        )

    os.makedirs(OUT, exist_ok=True)
    written = []

    # --- horizontal lockup, four sanctioned colourways -------------------
    LOCKUPS = [
        ("horizontal-full-on-light", lambda c: RED if c == "#E10916" else INK, INK, RED),
        ("horizontal-full-on-dark", lambda c: RED if c == "#E10916" else PAPER_WARM, PAPER_WARM, RED),
        ("horizontal-reversed", lambda c: PAPER_WARM, PAPER_WARM, PAPER_WARM),
        ("horizontal-ink", lambda c: INK, INK, INK),
        ("horizontal-red", lambda c: RED, RED, RED),
    ]
    sym_y = sym_y0 - y0
    for name, cmap, tag_fill, sym_fill in LOCKUPS:
        body = sym_group(sym_fill, 0, sym_y, SYM_H)
        body += wordmark_groups(cmap)
        body += tagline_group(tag_fill)
        path = os.path.join(OUT, name + ".svg")
        with open(path, "w") as fh:
            fh.write(svg(body, total_w, total_h, "Sykon Aluminium Building Systems"))
        written.append(path)

    # --- symbol alone, three colourways ----------------------------------
    for name, fill in [("symbol-red", RED), ("symbol-ink", INK), ("symbol-light", PAPER_WARM)]:
        body = '  <path fill="%s" d="%s"/>\n' % (fill, SYMBOL_PATH)
        path = os.path.join(OUT, name + ".svg")
        with open(path, "w") as fh:
            fh.write(svg(body, 225.679, 100, "Sykon symbol"))
        written.append(path)

    return written, {
        "lockup_w": total_w,
        "lockup_h": total_h,
        "symbol_w": SYM_W,
        "symbol_h": SYM_H,
        "gap": GAP,
        "gap_over_symbol_w": GAP / SYM_W,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        die("usage: python tools/build_logos.py <brand-master.pdf>")
    files, m = build(sys.argv[1])
    for f in files:
        print("  wrote %s" % os.path.relpath(f, ROOT))
    print(
        "\n  lockup %.3f x %.3f pt   symbol %.3f x %.3f   gap %.3f (%.4f x symbol width)"
        % (m["lockup_w"], m["lockup_h"], m["symbol_w"], m["symbol_h"], m["gap"], m["gap_over_symbol_w"])
    )
