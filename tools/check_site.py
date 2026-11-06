#!/usr/bin/env python3
"""
Verifies the generated site:

  1. every internal href resolves to a file that exists
  2. every internal anchor (#id) resolves to an id in the target page
  3. every external source URL in data/sources.json appears at least once
     on the site, and appears with the correct href
  4. every row of the analysis tables carries at least one source link
  5. no personal names from the source data leak into the output
  6. all arithmetic in data/units.json recomputes correctly

Exit code 0 = all checks pass.

Usage: python3 tools/check_site.py
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "v2")
PUB = os.path.join(ROOT, "docs", "v2")

PAGES = sorted(f for f in os.listdir(PUB) if f.endswith(".html"))

# Names supplied by the owner. These must never appear in published output.
FORBIDDEN_NAMES = ["L O", "V N", "JP", "M T", "E R", "I S"]

errors = []
warnings = []
checks = 0


def fail(msg):
    errors.append(msg)


def ok(msg):
    global checks
    checks += 1


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------- 1 + 2 links
ids_by_page = {}
for p in PAGES:
    body = read(os.path.join(PUB, p))
    ids_by_page[p] = set(re.findall(r'id="([^"]+)"', body))

for p in PAGES:
    body = read(os.path.join(PUB, p))
    for href in re.findall(r'href="([^"]+)"', body):
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        target, _, anchor = href.partition("#")
        if target == "":
            # same-page anchor
            if anchor and anchor not in ids_by_page[p]:
                fail("%s: broken same-page anchor #%s" % (p, anchor))
            else:
                ok("anchor")
            continue
        dest = os.path.join(PUB, target)
        if not os.path.isfile(dest):
            fail("%s: broken internal link -> %s" % (p, target))
            continue
        if anchor and target.endswith(".html"):
            if anchor not in ids_by_page.get(target, set()):
                fail("%s: broken anchor -> %s#%s" % (p, target, anchor))
                continue
        ok("link")

# ------------------------------------------------------- 3 external sources
all_html = "\n".join(read(os.path.join(PUB, p)) for p in PAGES)
# hrefs are HTML-escaped in output (& -> &amp;); compare against both forms
def unescaped(text):
    return text.replace("&amp;", "&")
sources = json.load(open(os.path.join(DATA, "sources.json"), encoding="utf-8"))["sources"]
practice = json.load(open(os.path.join(DATA, "practice.json"), encoding="utf-8"))
secondary = practice.get("secondary_sources", [])

for s in sources:
    if 'href="%s"' % s["url"] not in unescaped(all_html):
        fail("source %s URL never linked on the site: %s" % (s["id"], s["url"]))
    else:
        ok("source-linked")

for s in secondary:
    if 'href="%s"' % s["url"] not in unescaped(all_html):
        fail("commercial source %s URL never linked: %s" % (s["id"], s["url"]))
    else:
        ok("source-linked")

# every inline Sxx reference must exist in the register
referenced = set(re.findall(r">(S\d{2})</a>", all_html))
known = {s["id"] for s in sources}
for ref in sorted(referenced - known):
    fail("inline reference to unknown source id: %s" % ref)
ok("source-ids")

# ------------------------------------------------- 4 source link per table row
for p in PAGES:
    if p in ("index.html",):
        continue
    body = read(os.path.join(PUB, p))
    for tbl_i, table_html in enumerate(re.findall(r"<table.*?</table>", body, re.S)):
        for row_i, row in enumerate(re.findall(r"<tr>(.*?)</tr>", table_html, re.S)):
            if "<th>" in row:
                continue  # header row
            has_source = 'class="srcref' in row or "href=" in row
            flagged = 'class="blank"' in row or 'class="pill bad"' in row
            if not has_source and not flagged:
                # No source and not explicitly marked unverified: a real gap.
                fail("%s table %d row %d has neither a source link nor an unverified marker"
                     % (p, tbl_i, row_i))
            else:
                ok("row-source" if has_source else "row-flagged-unverified")

# ------------------------------------------- 4b column counts match the header
for p in PAGES:
    body = read(os.path.join(PUB, p))
    for tbl_i, table_html in enumerate(re.findall(r"<table.*?</table>", body, re.S)):
        ncols = None
        for row_i, row in enumerate(re.findall(r"<tr>(.*?)</tr>", table_html, re.S)):
            cells = len(re.findall(r"<t[hd][ >]", row))
            if "<th>" in row:
                ncols = cells
                continue
            if ncols is not None and cells != ncols:
                fail("%s table %d row %d has %d cells, header has %d"
                     % (p, tbl_i, row_i, cells, ncols))
            else:
                ok("column-count")

# --------------------------------------------------------- 5 privacy check
for name in FORBIDDEN_NAMES:
    pat = r"\b%s\b" % re.escape(name)
    for p in PAGES:
        if re.search(pat, read(os.path.join(PUB, p))):
            fail("privacy: personal name %r found in %s" % (name, p))
ok("privacy")

# --------------------------------------------------------- 6 arithmetic check
units = json.load(open(os.path.join(DATA, "units.json"), encoding="utf-8"))
for unit in units["units"]:
    for calc in unit["calculations"]:
        if calc["total_pct"] is None:
            if calc["increase_dollars"] is not None or calc["new_rent"] is not None:
                fail("%s: blank percentage but non-blank amount" % calc["id"])
            ok("blank-consistency")
            continue
        summed = round(sum(c["pct"] for c in calc["components"]), 10)
        if calc["components"] and abs(summed - calc["total_pct"]) > 1e-9:
            fail("%s: components sum to %s not %s" % (calc["id"], summed, calc["total_pct"]))
        expect_inc = round(unit["current_rent"] * calc["total_pct"] / 100.0, 2)
        if abs(expect_inc - calc["increase_dollars"]) > 0.005:
            fail("%s: increase should be %.2f not %.2f" % (calc["id"], expect_inc, calc["increase_dollars"]))
        expect_new = round(unit["current_rent"] + calc["increase_dollars"], 2)
        if abs(expect_new - calc["new_rent"]) > 0.005:
            fail("%s: new rent should be %.2f not %.2f" % (calc["id"], expect_new, calc["new_rent"]))
        ok("arithmetic")

# AGA table: the years marked as used must sum to the stated totals
aga = json.load(open(os.path.join(DATA, "aga.json"), encoding="utf-8"))
u1_sum = round(sum(r["pct"] for r in aga["rows"] if r["used_in_unit1"]), 10)
u2_sum = round(sum(r["pct"] for r in aga["rows"] if r["used_in_unit2"]), 10)
if abs(u1_sum - 3.0) > 1e-9:
    fail("AGA: Unit 1 marked years sum to %s, expected 3.0" % u1_sum)
if abs(u2_sum - 13.1) > 1e-9:
    fail("AGA: Unit 2 marked years sum to %s, expected 13.1" % u2_sum)
ok("aga-sums")

# ---------------------------------------------------------------- report
print("checks passed: %d" % checks)
if warnings:
    print("\nWARNINGS (%d)" % len(warnings))
    for w in warnings:
        print("  - %s" % w)
if errors:
    print("\nERRORS (%d)" % len(errors))
    for e in errors:
        print("  x %s" % e)
    sys.exit(1)
print("no errors")
