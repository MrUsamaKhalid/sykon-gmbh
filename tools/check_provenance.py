#!/usr/bin/env python3
"""
Sykon ABS GmbH — provenance gate.

    python tools/check_provenance.py catalogue/examples/s60-sheet.json

Asserts that every user-visible string in a sheet config is traceable to that
system's .docx catalogue material. Exits non-zero if anything is not.

THE RULE
--------
The .docx catalogue materials are the only source of fact. The sample supplies
design. The portfolio, the old brochure, the drawings and the email thread are
input, not truth. Nothing reaches a printed page unless the document says it.

This exists because the rule was not enough on its own. The first S60 sheet
carried "Superior" in the product name, four segment descriptions, a
certification badge and three certification marks — none of which appear in
S60's document. They came from the sample, which is a layout reference. Good
intentions did not catch that; a check does.

WHAT COUNTS AS A MATCH
----------------------
Token-sequence containment, not string equality. The document writes table rows
as "Water tightness | EN 12208 | Class 7A / 3A" while the sheet sets
"Watertightness — EN 12208" and "Class 7A / 3A" in separate cells, so a literal
comparison would fail on formatting that carries no meaning.

So: lowercase, drop separators (— – | / , : and friends), collapse whitespace,
and require the claim's tokens to appear as a contiguous run in the document's
token stream. Words and numbers still have to match exactly — "2880" will never
satisfy "2280", and "polyamide" will never appear at all, which is the point.

THE TWO EXCEPTIONS
------------------
catalogue/references/furniture.json lists them, both approved explicitly:
brand furniture (the contact line) and design headings taken from the sample.
Both are small, both are visible, and neither asserts anything about a product.
"""
import os
import re
import sys
import json
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCX_DIR = os.path.join(ROOT, "intake", "materials", "01-catalogue-materials")
SYSTEMS_DIR = os.path.join(ROOT, "systems")
FURNITURE = os.path.join(ROOT, "catalogue", "references", "furniture.json")

#: Config keys whose values are printed on the page. Anything not listed here is
#: structure (file paths, block names, slugs) and is not a claim about a product.
VISIBLE_KEYS = {
    "system_name", "value", "note", "overview", "label",
    "name", "title", "contact", "heading", "lead", "body", "item",
}
#: Keys that name a section rather than assert a fact.
HEADING_KEYS = {
    "overview_title", "specs_title", "performance_title",
    "typologies_title", "segments_title", "eyebrow",
}
#: Keys that never reach the page.
SKIP_KEYS = {"block", "slug", "svg", "icon", "hero", "image", "drawing",
             "photo", "strip", "cert_marks"}

SEP = re.compile(r"[—–\-|/,:;()\[\]&+\.·]+")
WS = re.compile(r"\s+")


def tokens(s):
    s = str(s).replace("×", " x ").replace("²", "2").replace("³", "3")
    s = SEP.sub(" ", s.lower())
    return [t for t in WS.split(s) if t]


def contains(hay, needle):
    """Is `needle` a contiguous run inside `hay`? Both are token lists."""
    if not needle:
        return True
    n = len(needle)
    for i in range(len(hay) - n + 1):
        if hay[i:i + n] == needle:
            return True
    return False


def docx_tokens(path):
    import docx

    d = docx.Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            parts.extend(c.text for c in r.cells)
    return tokens(" \n ".join(parts))


def find_docx(system):
    """Match a system designation to its catalogue material file.

    systems/<SYSTEM>/source/ holds exactly one document per system, filed by
    tools/organise_systems.py against an explicit pattern table. Ask it first.

    The fallback that scans filenames is kept for a config written before a
    system was organised, but it cannot be trusted on its own: "SL450" is a
    prefix of "SL450S", so the shortest-stem rule resolved SL450 to the SL450s
    document and would have gated one system against another's figures.
    """
    want = re.sub(r"[^a-z0-9]", "", system.lower())
    filed = glob.glob(os.path.join(SYSTEMS_DIR, system.upper(), "source", "*.docx"))
    if filed:
        return filed[0]
    best = None
    for f in glob.glob(os.path.join(DOCX_DIR, "*.docx")):
        stem = re.sub(r"[^a-z0-9]", "", os.path.basename(f).lower())
        stem = stem.replace("cataloguematerial", "").replace("docx", "")
        # the character after the designation must not extend it: sl450s is a
        # different system from sl450, not a longer spelling of it
        if stem.startswith(want) and not stem[len(want):len(want) + 1].isalnum():
            if best is None or len(stem) < len(best[1]):
                best = (f, stem)
    return best[0] if best else None


def walk(node, path=""):
    """Yield (json_path, key, string) for every printed value."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k.startswith("_") or k in SKIP_KEYS:
                continue
            p = "%s.%s" % (path, k) if path else k
            if isinstance(v, str):
                if k in VISIBLE_KEYS or k in HEADING_KEYS:
                    yield p, k, v
            else:
                yield from walk(v, p)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (path, i))


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: check_provenance.py <sheet-config.json>")
    cfg_path = sys.argv[1]
    cfg = json.load(open(cfg_path))
    fur = json.load(open(FURNITURE))

    allowed = set()
    for key in ("furniture", "design_headings", "derived"):
        for s in fur.get(key, []):
            allowed.add(" ".join(tokens(s)))

    system = cfg.get("system") or cfg.get("slug", "")
    m = re.search(r"(S|SL|SY)\s?-?(\d+s?)", system, re.I)
    if not m:
        raise SystemExit("  could not work out the system from %r" % system)
    designation = (m.group(1) + m.group(2)).upper()

    src = find_docx(designation)
    if not src:
        raise SystemExit("  no .docx found for %s in %s" % (designation, DOCX_DIR))
    hay = docx_tokens(src)

    ok, untraced, furniture_used = [], [], []
    for jpath, key, value in walk(cfg):
        toks = tokens(value)
        if not toks:
            continue
        joined = " ".join(toks)
        if joined in allowed:
            furniture_used.append((jpath, value))
            continue
        # multi-line values (a bullet list, a paragraph) are checked line by line
        lines = [l.strip() for l in str(value).split("\n") if l.strip()]
        parts = lines if len(lines) > 1 else [value]
        bad = [p for p in parts
               if not contains(hay, tokens(p))
               and " ".join(tokens(p)) not in allowed]
        if bad:
            untraced.append((jpath, key, bad))
        else:
            ok.append((jpath, value))

    print("\n  provenance: %s" % os.path.basename(cfg_path))
    print("  source:     %s" % os.path.basename(src))
    print("  %d traced to the document, %d approved furniture, %d UNTRACED"
          % (len(ok), len(furniture_used), len(untraced)))

    if furniture_used:
        print("\n  approved furniture (not from the .docx, signed off):")
        for jpath, v in furniture_used:
            print("    · %-28s %s" % (jpath, str(v)[:56]))

    if untraced:
        print("\n  UNTRACED — not in %s, and not approved furniture:"
              % os.path.basename(src))
        for jpath, key, bad in untraced:
            for b in bad:
                print("    x %-28s %r" % (jpath, b[:72]))
        print("\n  Nothing here may be printed. Either quote the document, or add it\n"
              "  to catalogue/references/furniture.json with the client's approval.\n")
        return 1

    print("\n  every printed string is traceable\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
