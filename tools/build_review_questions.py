#!/usr/bin/env python3
"""
Sykon ABS GmbH — reviewer question sheet.

    python tools/build_review_questions.py catalogue/examples/s60-sheet.json

Writes catalogue/review/<system>-questions.md: forty numbered questions a
reviewer can answer without hunting through the source.

WHY FORTY QUESTIONS AND NOT A DIFF
----------------------------------
A diff tells you what changed. It does not tell you whether a printed claim is
allowed to be on the page at all. The rule on this project is that the .docx
catalogue material is the only source of fact, so the thing a reviewer needs to
confirm, claim by claim, is "the document actually says this".

Each question therefore carries three things: the exact string as printed, where
it sits on the sheet, and the section it was traced to. The reviewer confirms or
rejects; they do not go looking.

Anything that could NOT be traced is listed first, under UNVERIFIED, and is the
same set that fails tools/check_provenance.py. If that section is non-empty the
sheet is not publishable, and the question sheet says so at the top.

Where a system yields fewer than forty distinct claims, the remainder are
coverage questions — sections that exist in the document but are not represented
on the sheet — because "what did we leave out" is the other half of the review.
"""
import os
import re
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from check_provenance import (  # noqa: E402
    tokens, contains, find_docx, walk, FURNITURE,
)

OUT = os.path.join(ROOT, "catalogue", "review")
TARGET = 40

SLOT_NAMES = {
    "system_name": "masthead, product name",
    "system_subtitle": "masthead, subtitle",
    "value": "specification table, value",
    "note": "masthead chip, caption",
    "label": "specification table, row label",
    "overview": "Product Overview",
    "overview_list": "Product Overview, bullet",
    "overview_list_title": "Product Overview, lead-in",
    "name": "System Options chip",
    "title": "Area of Usage card",
    "contact": "footer",
}


def sections(path):
    """[(heading, [lines])] — the document split by its Heading 2s."""
    import docx

    d = docx.Document(path)
    out, cur = [], ("(front matter)", [])
    body = d.element.body
    para_i = tbl_i = 0
    paras, tbls = d.paragraphs, d.tables
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p" and para_i < len(paras):
            p = paras[para_i]; para_i += 1
            if p.style.name.startswith("Heading") and p.text.strip():
                out.append(cur)
                # the heading is itself quotable — the product name is Heading 1
                cur = (p.text.strip(), [p.text.strip()])
            elif p.text.strip():
                cur[1].append(p.text.strip())
        elif tag == "tbl" and tbl_i < len(tbls):
            t = tbls[tbl_i]; tbl_i += 1
            for r in t.rows:
                cur[1].append(" | ".join(c.text.strip() for c in r.cells))
    out.append(cur)
    return [s for s in out if s[1]]


def locate(secs, claim):
    """Which section and line a claim came from."""
    need = tokens(claim)
    for heading, lines in secs:
        for line in lines:
            if contains(tokens(line), need):
                return heading, line
    return None, None


def slot_of(jpath, key):
    """Where on the sheet a claim appears, in words a reviewer can act on."""
    if "." not in jpath and key == "title":
        return "PDF document title"
    if jpath.endswith("segments") or ".segments[" in jpath:
        return "Area of Usage card"
    if ".typologies[" in jpath:
        return "System Options chip"
    if ".chips[" in jpath:
        return "masthead chip"
    if ".performance[" in jpath:
        return "Tested Performance table"
    if ".specs[" in jpath:
        return "Technical Specifications table"
    return SLOT_NAMES.get(key, key)


def shown(value):
    """As the reader sees it: '|' is our line-break marker, not printed text."""
    return " ".join(str(value).replace("|", " ").split())


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: build_review_questions.py <sheet-config.json>")
    cfg_path = sys.argv[1]
    cfg = json.load(open(cfg_path))
    fur = json.load(open(FURNITURE))

    allowed = {}
    for kind in ("furniture", "design_headings", "derived"):
        for s in fur.get(kind, []):
            allowed[" ".join(tokens(s))] = kind

    system = cfg.get("system") or cfg.get("slug", "")
    m = re.search(r"(S|SL|SY)\s?-?(\d+s?)", system, re.I)
    designation = (m.group(1) + m.group(2)).upper() if m else system
    src = find_docx(designation)
    if not src:
        raise SystemExit("  no .docx found for %s" % designation)
    secs = sections(src)

    traced, furniture, unverified = [], [], []
    seen = set()
    for jpath, key, value in walk(cfg):
        for part in ([l.strip() for l in str(value).split("\n") if l.strip()]
                     if "\n" in str(value) else [value]):
            j = " ".join(tokens(part))
            if not j or j in seen:
                continue
            seen.add(j)
            if j in allowed:
                furniture.append((part, slot_of(jpath, key), allowed[j]))
                continue
            heading, line = locate(secs, part)
            if heading:
                traced.append((part, slot_of(jpath, key), heading, line))
            else:
                unverified.append((part, slot_of(jpath, key)))

    # coverage: sections in the document that the sheet does not draw on
    used = {h for _, _, h, _ in traced}
    coverage = [h for h, _ in secs if h not in used and h != "(front matter)"]

    os.makedirs(OUT, exist_ok=True)
    dest = os.path.join(OUT, "%s-questions.md" % designation.lower())
    L = []
    A = L.append

    A("# %s — reviewer questions" % designation)
    A("")
    A("Source of fact: `%s`" % os.path.basename(src))
    A("Sheet: `%s`" % os.path.basename(cfg_path))
    A("")
    A("Every question below asks one thing: **does the document actually say "
      "this?** Tick or correct. The section it was traced to is given, so you do "
      "not have to go looking.")
    A("")

    if unverified:
        A("## UNVERIFIED — DO NOT PUBLISH")
        A("")
        A("These are printed on the sheet but could not be traced to the "
          "document, and are not approved furniture. Each one is either wrong or "
          "needs adding to `catalogue/references/furniture.json` with your "
          "approval.")
        A("")
        for v, slot in unverified:
            A("- **%s** — *%s*" % (shown(v), slot))
        A("")
    else:
        A("## UNVERIFIED — DO NOT PUBLISH")
        A("")
        A("*(empty — every printed string traced to the document or to approved "
          "furniture)*")
        A("")

    A("## Questions")
    A("")
    n = 0
    for value, slot, heading, line in traced:
        n += 1
        A("**Q%d.** The sheet prints **%s** *(%s)*." % (n, shown(value), slot))
        A("Is that in the document?")
        A("")
        A("> Traced to **%s** — `%s`" % (heading, line[:150]))
        A("")
        A("☐ correct  ☐ wrong — should be: ______________________")
        A("")

    for value, slot, kind in furniture:
        n += 1
        A("**Q%d.** The sheet prints **%s** *(%s)*." % (n, shown(value), slot))
        A("This is **not** from the document — it is approved %s."
          % kind.replace("_", " "))
        A("")
        A("☐ keep  ☐ remove")
        A("")

    for heading in coverage:
        if n >= TARGET:
            break
        n += 1
        A("**Q%d.** The document has a section **%s** that does not appear on "
          "the sheet." % (n, heading))
        A("Should it?")
        A("")
        A("☐ leave out  ☐ add it")
        A("")

    A("---")
    A("")
    A("%d questions — at least %d by design. %d traced claims, %d approved "
      "furniture items, " % (n, TARGET, len(traced), len(furniture)) +
      "%d untraceable, %d document sections not used on the sheet."
      % (len(unverified), len(coverage)))
    A("")
    A("_%s_" % ("Every claim on the sheet has a question. Coverage questions "
                "pad the count to %d." % TARGET))


    with open(dest, "w") as fh:
        fh.write("\n".join(L))

    print("\n  %s" % os.path.relpath(dest, ROOT))
    print("  %d questions — %d traced, %d furniture, %d UNVERIFIED, %d unused sections"
          % (n, len(traced), len(furniture), len(unverified), len(coverage)))
    if unverified:
        print("\n  UNVERIFIED present — the sheet is not publishable:")
        for v, slot in unverified:
            print("    x %-40s %s" % (v[:40], slot))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
