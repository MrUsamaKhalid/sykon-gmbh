#!/usr/bin/env python3
"""
Sykon ABS GmbH — build every system's spec sheet, gated.

    python tools/build_all_sheets.py            # all ten
    python tools/build_all_sheets.py S60 SL580  # named systems

For each system, in this order and stopping that system at the first failure:

    1. tools/check_provenance.py     every printed string traces to the .docx
    2. catalogue/scripts/build_catalogue.py   print + digital PDF
    3. catalogue/scripts/verify_layout.py     page size, palette, contrast
    4. tools/build_review_questions.py        the reviewer's question sheet

The gate runs FIRST, on purpose. A sheet that cannot be traced should never
reach a PDF — an artefact on disk gets attached to an email, and by then nobody
remembers it failed a check.

Each config carries "_image_dir", written by tools/scaffold_sheet.py, pointing
at that system's own systems/<SYSTEM>/extracted/. Underscore keys are invisible
to the provenance gate and to the page, so this is configuration, not content.

A system with no artwork still builds. S50 and SL350 have no drawings anywhere
in the intake, so their sheets come out with an empty masthead — correct, and
more useful than no sheet at all, because the text is what needs reviewing.
"""
import os
import sys
import json
import glob
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = os.path.join(ROOT, "catalogue", "examples")
OUT = os.path.join(ROOT, "catalogue", "out")

PROVENANCE = [sys.executable, os.path.join(HERE, "check_provenance.py"), "{cfg}"]
BUILD = [sys.executable, os.path.join(ROOT, "catalogue", "scripts", "build_catalogue.py"),
         "{cfg}", "{images}", OUT]
VERIFY = [sys.executable, os.path.join(ROOT, "catalogue", "scripts", "verify_layout.py"),
          "{cfg}", OUT]
QUESTIONS = [sys.executable, os.path.join(HERE, "build_review_questions.py"), "{cfg}"]

#: How many rows the fit loop may trim before giving up. Eight is far more than
#: any document needs; it exists so a layout bug cannot empty a table one row at
#: a time and call the result a success.
MAX_TRIM = 8


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def trim_one_row(cfg_path):
    """Move the last row of the taller spec table into _deferred.

    Called only when the rendered page shows a table crossing into the 207mm
    dead zone. Estimating the row count from string lengths gets close and no
    closer — where a label wraps depends on Chromium's measurement of Hanken
    Grotesk, so the honest way to find the limit is to render, look, and trim.

    Returns the row it moved, or None when there is nothing left to give.
    """
    cfg = json.load(open(cfg_path))
    page = cfg["pages"][0]
    specs, perf = page.get("specs", []), page.get("performance", [])
    key = "performance" if len(perf) >= len(specs) else "specs"
    rows = page.get(key, [])
    if len(rows) <= 1:
        key = "specs" if key == "performance" else "performance"
        rows = page.get(key, [])
        if len(rows) <= 1:
            return None
    row = rows.pop()
    cfg.setdefault("_deferred", {}).setdefault(key, []).insert(0, row)
    with open(cfg_path, "w") as fh:
        json.dump(cfg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return key, row


def build_and_fit(cfg_path, images, log):
    """Build, and keep trimming until the page stops overflowing its band."""
    for _ in range(MAX_TRIM + 1):
        code, out = run([c.format(cfg=cfg_path, images=images) for c in BUILD])
        if code != 0:
            return "build", out
        code, out = run([c.format(cfg=cfg_path, images=images) for c in VERIFY])
        if code == 0:
            return None, out
        if "overflows its band" not in out:
            return "verify", out
        moved = trim_one_row(cfg_path)
        if not moved:
            return "verify", out
        log.append("%s: %s row %r did not fit and was deferred"
                   % (os.path.basename(cfg_path), moved[0], moved[1]["label"]))
    return "verify", out


def main():
    wanted = {a.upper() for a in sys.argv[1:]}
    configs = sorted(glob.glob(os.path.join(EXAMPLES, "*-sheet.json")))
    rows, failures, log = [], [], []

    print()
    for cfg_path in configs:
        designation = (json.load(open(cfg_path)).get("system") or "").upper()
        if wanted and designation not in wanted:
            continue
        cfg = json.load(open(cfg_path))
        images = os.path.join(ROOT, cfg.get("_image_dir", "catalogue/assets"))
        status = {}

        code, out = run([c.format(cfg=cfg_path) for c in PROVENANCE])
        status["provenance"] = "ok" if code == 0 else "FAIL"
        if code == 0:
            step, out = build_and_fit(cfg_path, images, log)
            status["build"] = "FAIL" if step == "build" else "ok"
            status["verify"] = "FAIL" if step == "verify" else ("ok" if not step else "-")
            if step:
                failures.append((designation, step, out))
            else:
                code, out = run([c.format(cfg=cfg_path) for c in QUESTIONS])
                status["questions"] = "ok" if code == 0 else "FAIL"
                if code != 0:
                    failures.append((designation, "questions", out))
        else:
            failures.append((designation, "provenance", out))

        # re-read: the fit loop rewrites the config as it trims
        cfg = json.load(open(cfg_path))
        rows.append((designation, status, cfg["pages"][0], cfg))

    if log:
        print("  Trimmed to fit the page:")
        for line in log:
            print("    %s" % line)
        print()

    print("  %-8s %-11s %-7s %-7s %-10s %s"
          % ("SYSTEM", "PROVENANCE", "BUILD", "VERIFY", "QUESTIONS", "ARTWORK"))
    for designation, status, page, cfg in rows:
        print("  %-8s %-11s %-7s %-7s %-10s %s"
              % (designation,
                 status.get("provenance", "-"), status.get("build", "-"),
                 status.get("verify", "-"), status.get("questions", "-"),
                 "hero" if page.get("hero") else "NONE"))

    deferred = [(d, cfg["_deferred"]) for d, _, _, cfg in rows if cfg.get("_deferred")]
    if deferred:
        print("\n  Held back — in the document, not on the page:")
        for designation, blocks in deferred:
            for key, items in blocks.items():
                print("    %-8s %-20s %d" % (designation, key, len(items)))

    refused = [(d, cfg["_refused"]) for d, _, _, cfg in rows if cfg.get("_refused")]
    if refused:
        print("\n  REFUSED — must not print until the document is corrected:")
        for designation, items in refused:
            for it in items:
                print("    %-8s %-28s %s" % (designation, it["label"][:28], it["reason"]))

    if failures:
        print("\n  FAILURES\n")
        for designation, step, out in failures:
            print("  == %s / %s" % (designation, step))
            print("\n".join("     " + l for l in out.splitlines()[-18:]))
            print()
        return 1
    print("\n  %d sheet(s) built and gated\n" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
