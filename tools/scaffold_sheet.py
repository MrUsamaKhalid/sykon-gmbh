#!/usr/bin/env python3
"""
Sykon ABS GmbH — sheet config scaffolder.

    python tools/scaffold_sheet.py S60          # one system
    python tools/scaffold_sheet.py --all        # all ten

Reads a system's .docx catalogue material and writes
catalogue/examples/<system>-sheet.json, quoting the document and nothing else.

WHY A GENERATOR AND NOT TEN HAND-WRITTEN FILES
----------------------------------------------
The S60 sheet was assembled by hand and shipped with "Superior" in the product
name, four invented segment descriptions and a certification badge no document
supports. Hand-copying ten more is ten more chances to do that again. Here the
only text that reaches a config is text lifted verbatim out of the document, so
the failure mode changes from "wrote something plausible" to "picked the wrong
section", which the provenance gate and the reviewer question sheet both catch.

Every config it writes still has to pass tools/check_provenance.py. This
generator is not a substitute for that gate; it is the thing that makes passing
it the default.

WHAT MAPS TO WHAT
-----------------
The ten documents share a structure, so one mapping serves all of them:

    Heading 1                       system name and subtitle
    1. System Overview              lead sentence, lead-in, bullets
    N. System Basic Technical Data  Technical Specifications table
    N. Performance Summary          Tested Performance table, upper rows
    N. Measured Performance Data    Tested Performance table, lower rows
    N. System Options               System Options chips
      (S50 calls this "System Configurations")
    N. Area of Usage / Project Type Area of Usage cards

NOTHING IS SILENTLY DROPPED
---------------------------
The sheet is one page and the bands are fixed, so a document with eleven spec
rows cannot print all eleven. Everything that does not fit goes to the config's
"_deferred" block — underscore keys are invisible to the gate and to the page —
and the run prints what was set aside. A cut you can see is an editorial
decision; a cut you cannot is a lie about coverage.

Two things are refused outright rather than deferred:

  * Cells carrying an unresolved author query. SL20's water result reads
    "~399 Pa (no water ingress) I think this was 180 Pa only when tested?? We
    need to re-test this". That is a note to a colleague, not a test result, and
    it must never reach a page.
  * Cells whose value is a "not available" marker (S50 and SL350 have no tested
    performance at all). A spec sheet that prints a row of crosses reads worse
    than one that omits the table, and which of the two to publish is the
    client's call, not this script's.
"""
import os
import re
import sys
import json
import glob
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SYSTEMS_DIR = os.path.join(ROOT, "systems")
OUT_DIR = os.path.join(ROOT, "catalogue", "examples")

#: What the page can hold. Measured off the sample's bands, not guessed —
#: see blk_sheet in catalogue/scripts/build_catalogue.py.
MAX_TYPOLOGIES = 8
MAX_SEGMENTS = 4
MAX_BULLETS = 5

#: The spec band runs 136mm to the hairline at 207mm; the section heading eats
#: the first 10.4mm. What is left is what both tables have to fit inside.
#:
#: Set generously on purpose. This estimate only stops a document with thirty
#: rows from producing an absurd first draft — tools/build_all_sheets.py then
#: renders the page, measures the real overflow and trims to it, which is the
#: only way to be exact about a line count that depends on Chromium's wrapping.
TABLE_BUDGET_MM = 74.0
COL_MM = 84.97          # (181.94 - 12 gap) / 2
ICON_MM = 5.6
PAD_MM = 8.0
CHAR_MM = 1.42          # Hanken Grotesk at 8.2px, averaged over mixed case
LINE_MM = 2.9
ROW_PAD_MM = 3.0


def table_height(rows):
    """Roughly how tall a spec table renders, in mm.

    A row is one line until its label runs out of room, and how much room the
    label has depends on the value beside it — the value cell is nowrap, so
    "+1400 Pa / +1920 Pa (within L/175)" squeezes "Wind resistance –
    serviceability — ASTM E330" into three lines. Counting rows alone said S60's
    nine fitted; they overflowed the band by 5mm and collided with the section
    below. verify_layout now fails on that collision, so this only has to be
    close, not exact.
    """
    total = 0.0
    for r in rows:
        avail = COL_MM - ICON_MM - PAD_MM - len(r["value"]) * CHAR_MM
        lines = 1 if avail <= 0 else max(1, math.ceil(len(r["label"]) * CHAR_MM / avail))
        total += ROW_PAD_MM + lines * LINE_MM
    return total


def fit_table(rows):
    """(kept, deferred) — as many rows as the band holds, in document order."""
    for n in range(len(rows), 0, -1):
        if table_height(rows[:n]) <= TABLE_BUDGET_MM:
            return rows[:n], rows[n:]
    return rows[:1], rows[1:]

#: An unresolved note to a colleague, left inside a results cell. Deliberately
#: not "re-test" on its own — SL580 ran a legitimate second water test and its
#: row is labelled "Static water penetration (re-test)". What marks a query is
#: someone addressing a reader: a doubled question mark, or the first person.
QUERY = re.compile(r"\?\?|\bi think\b|\bwe (need|have) to\b|\bnot sure\b", re.I)
#: "Not available", "Not specified", and the crosses and warnings beside them.
ABSENT = re.compile(r"^[\s❌⚠️✅✔️→]*"
                    r"(not (available|specified|applicable|tested)|n/?a|none)"
                    r"[\s.]*$", re.I)
MARKER = re.compile(r"[❌⚠️✅✔️→]")
#: The authors mark a negative with a cross and a caveat with a warning sign.
#: Their own visual coding is more reliable than guessing at the words beside
#: it: S50 writes "❌ Non-thermal system", which no phrase-match would catch.
NEGATIVE = re.compile(r"[❌⚠️]")

SEC_OVERVIEW = re.compile(r"^\d+\.\s*system overview", re.I)
SEC_SPECS = re.compile(r"system basic technical data", re.I)
SEC_PERF_SUM = re.compile(r"performance (summary|& certification)", re.I)
SEC_PERF_CERT = re.compile(r"certified performance", re.I)
SEC_PERF_MEAS = re.compile(r"measured performance data", re.I)
SEC_OPTIONS = re.compile(r"system (options|configurations)", re.I)
SEC_USAGE = re.compile(r"area of usage", re.I)

#: Which spec rows earn a masthead chip. Four groups, one chip each; inside a
#: group the alternatives are tried in order of how much they tell a reader, NOT
#: in the order the document happens to list them. "Tested glass thickness: 24 /
#: 28 mm" is worth a chip; "Glazing type: Double glazing" says almost nothing,
#: and it sits higher in S60's table.
CHIP_PREFS = [
    ("system depth", "system designation", "sightline width",
     "frame depth", "frame width"),
    ("frame material", "aluminium alloy", "profile system"),
    ("tested glass thickness", "maximum glazing thickness",
     "typical glazing thickness", "glazing type"),
    ("sealing system", "thermal break", "thermal construction",
     "thermal behavior"),
]


def sections(path):
    """[(heading, [('p', text) | ('t', [cells])])] — the document in order."""
    import docx

    d = docx.Document(path)
    out, cur = [], ("(front matter)", [])
    pi = ti = 0
    paras, tbls = d.paragraphs, d.tables
    for child in d.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p" and pi < len(paras):
            p = paras[pi]
            pi += 1
            if p.style.name.startswith("Heading") and p.text.strip():
                out.append(cur)
                cur = (p.text.strip(), [])
            elif p.text.strip():
                cur[1].append(("p", p.text.strip()))
        elif tag == "tbl" and ti < len(tbls):
            t = tbls[ti]
            ti += 1
            for r in t.rows:
                cur[1].append(("t", [c.text.strip() for c in r.cells]))
    out.append(cur)
    return out


def find(secs, pattern):
    for heading, items in secs:
        if pattern.search(heading):
            return heading, items
    return None, []


def paras(items):
    return [v for kind, v in items if kind == "p"]


def rows(items):
    """Table rows with the header line dropped."""
    r = [v for kind, v in items if kind == "t"]
    if r and r[0] and r[0][0].lower() in ("item", "parameter", "performance item",
                                          "pressure (pa)", "test pressure"):
        r = r[1:]
    return r


def flat(cell):
    """One line. A cell's own wrapping is layout, not meaning."""
    return " ".join(str(cell).split())


def without_parenthetical(lines):
    """Drop an aside that Word broke across several paragraphs.

    S50's options list ends with a cross-reference typed over three lines:
    "(Refer to general arrangement drawings ...", "S50 Casement Non-Thermal",
    ")". Testing each line for a leading "(" catches the first and the last and
    leaves the middle one standing as if it were a sixth system option, so the
    depth has to be carried between lines.
    """
    out, depth = [], 0
    for line in lines:
        if depth == 0 and not line.startswith("("):
            out.append(line)
        depth = max(0, depth + line.count("(") - line.count(")"))
    return out


def title_case_heading(secs):
    """'SYKON S60 - Casement / Door System' -> ('S60', 'Casement / Door System')."""
    for heading, _ in secs:
        if heading.upper().startswith("SYKON"):
            left, _, right = heading.partition("–")   # en dash
            if not right:
                left, _, right = heading.partition(" - ")
            designation = left.strip()[len("SYKON"):].strip()
            return designation, right.strip()
    return "", ""


def build(designation):
    src = glob.glob(os.path.join(SYSTEMS_DIR, designation, "source", "*.docx"))
    if not src:
        raise SystemExit("  no source .docx under systems/%s/source/" % designation)
    secs = sections(src[0])
    printed, deferred, refused = {}, {}, []

    name_as_written, subtitle = title_case_heading(secs)
    if not name_as_written:
        raise SystemExit("  %s: no 'SYKON ...' heading in %s"
                         % (designation, os.path.basename(src[0])))

    # ---- overview -----------------------------------------------------------
    _, ov = find(secs, SEC_OVERVIEW)
    ov_paras = paras(ov)
    lead = ov_paras[0] if ov_paras else ""
    lead_in, bullets, rest = "", [], []
    for p in ov_paras[1:]:
        if p.rstrip().endswith(":"):
            if lead_in:                 # a second list — "It is designed for:"
                rest.append(p)
                continue
            lead_in = p
        elif lead_in and not rest:
            bullets.append(p)
        else:
            rest.append(p)
    if len(bullets) > MAX_BULLETS:
        deferred["overview_list"] = bullets[MAX_BULLETS:]
        bullets = bullets[:MAX_BULLETS]
    if rest:
        deferred.setdefault("overview_rest", []).extend(rest)

    # ---- technical specifications -------------------------------------------
    _, sp = find(secs, SEC_SPECS)
    specs = []
    for r in rows(sp):
        if len(r) < 2:
            continue
        label, value = flat(r[0]), flat(r[1])
        if not label or not value:
            continue
        if QUERY.search(value):
            refused.append(("spec", label, value, "unresolved author query"))
            continue
        if ABSENT.match(value) or NEGATIVE.search(value):
            deferred.setdefault("specs_absent", []).append({"label": label, "value": value})
            continue
        specs.append({"label": label, "value": MARKER.sub("", value).strip()})
    specs, over = fit_table(specs)
    if over:
        deferred["specs"] = over

    # ---- tested performance --------------------------------------------------
    # Order is priority, because the cap bites here. The tested classes come
    # first, then the certified EN classes, then the measured detail — S60's
    # "Water tightness — EN 12208: Class 7A / Class 3A" earns its place over
    # "Glass type: Double glazing".
    perf = []
    for pattern in (SEC_PERF_SUM, SEC_PERF_CERT, SEC_PERF_MEAS):
        _, block = find(secs, pattern)
        for r in rows(block):
            if len(r) < 2:
                continue
            cells = [flat(c) for c in r]
            # 4-column summary tables read Item | Standard | Result | Status.
            # The standard belongs with the item; "Pass" is not a figure.
            if len(cells) >= 3 and re.match(r"^(ASTM|EN|DIN|AAMA)\b", cells[1], re.I):
                label, value = "%s — %s" % (cells[0], cells[1]), cells[2]
            else:
                label, value = cells[0], cells[1]
            if not label or not value:
                continue
            if QUERY.search(value) or QUERY.search(label):
                refused.append(("performance", label, value, "unresolved author query"))
                continue
            if ABSENT.match(value) or NEGATIVE.search(value):
                deferred.setdefault("performance_absent", []).append(
                    {"label": label, "value": value})
                continue
            perf.append({"label": label, "value": MARKER.sub("", value).strip()})
    perf, over = fit_table(perf)
    if over:
        deferred["performance"] = over

    # ---- system options ------------------------------------------------------
    _, op = find(secs, SEC_OPTIONS)
    options = [p for p in without_parenthetical(paras(op))
               if not p.rstrip().endswith(":")]
    if len(options) > MAX_TYPOLOGIES:
        deferred["typologies"] = options[MAX_TYPOLOGIES:]
        options = options[:MAX_TYPOLOGIES]

    # ---- area of usage -------------------------------------------------------
    _, us = find(secs, SEC_USAGE)
    usage = [p for p in paras(us) if not p.rstrip().endswith(":")]
    if len(usage) > MAX_SEGMENTS:
        deferred["segments"] = usage[MAX_SEGMENTS:]
        usage = usage[:MAX_SEGMENTS]

    # ---- masthead chips ------------------------------------------------------
    chips, taken = [], set()
    for group in CHIP_PREFS:
        pick = None
        for wanted in group:
            for i, s in enumerate(specs):
                if i not in taken and wanted in s["label"].lower():
                    pick = i
                    break
            if pick is not None:
                break
        if pick is not None:
            chips.append({"value": specs[pick]["value"], "note": specs[pick]["label"]})
            taken.add(pick)
    for i, s in enumerate(specs):
        if len(chips) >= 4:
            break
        if i not in taken:
            chips.append({"value": s["value"], "note": s["label"]})
            taken.add(i)

    # ---- hero ----------------------------------------------------------------
    edir = os.path.join(SYSTEMS_DIR, designation, "extracted")
    art = sorted(os.path.basename(x) for x in glob.glob(os.path.join(edir, "*.png")))
    # The sectioned corner render is the sample's hero. Sheet 3D views are whole
    # elevations — correct drawings, but they read as an outline at this size.
    hero = next((a for a in art if "-3dview-" in a), "")

    page = {
        "block": "sheet",
        "system_name": "SYKON| %s" % name_as_written,
        "system_subtitle": subtitle,
        "hero": hero,
        "chips": chips,
        "overview_title": "Product Overview",
        "overview": lead,
        "overview_list_title": lead_in,
        "overview_list": bullets,
        "specs_title": "Technical Specifications",
        "specs": specs,
        "performance_title": "Tested Performance",
        "performance": perf,
        "typologies_title": "System Options",
        "typologies": [{"name": o} for o in options],
        "segments_title": "Area of Usage",
        "segments": [{"title": u} for u in usage],
        "contact": "www.sykon.ae  |  info@sykon.ae",
    }
    if not hero:
        del page["hero"]
    if not lead_in:
        del page["overview_list_title"]

    cfg = {
        "slug": "Sykon-%s-Spec-Sheet" % name_as_written,
        "system": designation,
        "title": "SYKON %s — %s" % (name_as_written, subtitle),
        "_rule": "Generated by tools/scaffold_sheet.py from %s, the only source "
                 "of fact. Section headings come from SAMPLE__USE_THIS.pdf, which "
                 "supplies DESIGN only. The contact line is approved brand "
                 "furniture. Enforced by tools/check_provenance.py."
                 % os.path.basename(src[0]),
        "_image_dir": os.path.join("systems", designation, "extracted"),
        "pages": [page],
    }
    if deferred:
        cfg["_deferred"] = deferred
    if refused:
        cfg["_refused"] = [
            {"slot": s, "label": l, "value": v, "reason": why}
            for s, l, v, why in refused
        ]

    dest = os.path.join(OUT_DIR, "%s-sheet.json" % designation.lower())
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(dest, "w") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return dest, page, deferred, refused


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit("usage: scaffold_sheet.py <SYSTEM> | --all")
    if args[0] == "--all":
        targets = sorted(d for d in os.listdir(SYSTEMS_DIR)
                         if not d.startswith("_")
                         and os.path.isdir(os.path.join(SYSTEMS_DIR, d)))
    else:
        targets = [a.upper() for a in args]

    print()
    for designation in targets:
        dest, page, deferred, refused = build(designation)
        print("  %-7s %-34s %d specs · %d perf · %d options · %d usage · hero %s"
              % (designation, os.path.relpath(dest, ROOT),
                 len(page["specs"]), len(page["performance"]),
                 len(page["typologies"]), len(page["segments"]),
                 "yes" if page.get("hero") else "NONE"))
        for key, items in deferred.items():
            print("            deferred %-18s %d item(s)" % (key, len(items)))
        for slot, label, value, why in refused:
            print("            REFUSED  %-18s %s — %s" % (slot, label[:30], why))
    print()


if __name__ == "__main__":
    main()
