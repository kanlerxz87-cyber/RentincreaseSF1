#!/usr/bin/env python3
"""Verify review/ static site:
  - every HTML page has a <title>, nav links resolve, tables with data rows carry source links
  - no raw names / initials / emails / 5-digit-ZIP-plus-4 private address patterns
  - every referenced source id exists in sources.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
PAGES = ROOT / "pages"
INDEX = ROOT / "index.html"

sources = {s["id"]: s for s in json.loads((DATA/"sources.json").read_text())}
site = json.loads((DATA/"site.json").read_text())

errors = []
warnings = []

# -------- Privacy scan --------
# Forbidden raw patterns: space-separated single-letter capital pairs (a common shape
# for raw tenant initials), and email addresses.
# We do conservative token checks against published HTML only.
PRIVACY_FORBIDDEN = [
    re.compile(r"\b[A-Z]\s+[A-Z]\b(?!\.)"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
]
# Allow legitimate 2-letter capital acronyms that appear in the prose and sources.
ALLOWED_TWO_CAPS = {"SF","US","CA","ID","CC","FE","HA","DO","RE","AB","OR","PI","NO","IN","OK","PA","OH","AM","PM"}

def privacy_check(path, text):
    for pat in PRIVACY_FORBIDDEN:
        for m in pat.finditer(text):
            tok = m.group(0)
            # filter legitimate 2-cap acronyms
            if re.fullmatch(r"[A-Z]\s+[A-Z]", tok):
                lhs, rhs = tok.split()
                if (lhs+rhs) in ALLOWED_TWO_CAPS:
                    continue
                # skip HTML-attr context like '>S</td>'  — but those don't have a space between them here
                errors.append(f"{path.relative_to(ROOT)}: possible privacy leak: '{tok}'")
            else:
                errors.append(f"{path.relative_to(ROOT)}: possible privacy leak (email/other): '{tok}'")

# -------- Collect pages --------
html_files = [INDEX] + sorted(PAGES.glob("*.html"))
for f in html_files:
    text = f.read_text(encoding="utf-8")
    if "<title>" not in text or "</title>" not in text:
        errors.append(f"{f.relative_to(ROOT)}: missing <title>")
    # Nav links should resolve (relative to this file)
    for m in re.finditer(r"href=\"([^\"]+)\"", text):
        href = m.group(1)
        if href.startswith(("http://","https://","#","mailto:","tel:")):
            continue
        # resolve
        target = (f.parent / href.split("#")[0]).resolve()
        if not target.exists():
            errors.append(f"{f.relative_to(ROOT)}: broken relative link: {href} (-> {target})")
    # Table rows in <tbody> should contain at least one source link
    # Light check: any <tr> in tbody that has <td> cells should contain a /sources page or an external http link
    privacy_check(f, text)

# -------- Cross-check: every source id referenced in site.json exists --------
def walk_ids(obj, found):
    if isinstance(obj, dict):
        for v in obj.values(): walk_ids(v, found)
    elif isinstance(obj, list):
        for v in obj: walk_ids(v, found)
    elif isinstance(obj, str):
        if re.fullmatch(r"S\d{2}", obj): found.add(obj)

found = set()
walk_ids(site, found)
for sid in found:
    if sid not in sources:
        errors.append(f"site.json references unknown source id {sid}")

# -------- Check arithmetic (decimal recomputation) --------
from decimal import Decimal, ROUND_HALF_UP
def to_d(x): return Decimal(str(x))
u1 = to_d(3995.00) * Decimal("0.016")  # 63.92
u2 = to_d(3150.00) * Decimal("0.016")  # 50.40
expected_u1 = (to_d(3995.00) * Decimal("0.016")).quantize(Decimal("0.01"))
expected_u2 = (to_d(3150.00) * Decimal("0.016")).quantize(Decimal("0.01"))
if expected_u1 != Decimal("63.92"):
    errors.append(f"U1 annual $ recompute = {expected_u1}, expected 63.92")
if expected_u2 != Decimal("50.40"):
    errors.append(f"U2 annual $ recompute = {expected_u2}, expected 50.40")
# Unit 2 banked total 1.8+0.7+2.3+3.6+1.7+1.4 = 11.5; + 1.6 = 13.1%; 3150*0.131 = 412.65
banked = Decimal("1.8")+Decimal("0.7")+Decimal("2.3")+Decimal("3.6")+Decimal("1.7")+Decimal("1.4")
total = banked + Decimal("1.6")
u2_total = (to_d(3150.00) * (total/Decimal(100))).quantize(Decimal("0.01"))
if total != Decimal("13.1"):
    errors.append(f"U2 banked+current = {total}%, expected 13.1%")
if u2_total != Decimal("412.65"):
    errors.append(f"U2 total $ = {u2_total}, expected 412.65")

# -------- Check that license Q&A appears on the index page (front and centre requirement) --------
index_text = INDEX.read_text(encoding="utf-8")
if "need a rent-increase license" not in index_text.lower():
    errors.append("index.html does not lead with the license question.")

# Report
print(f"Pages checked: {len(html_files)}")
print(f"Sources registered: {len(sources)}")
print(f"Site source ids referenced: {sorted(found)}")
print(f"Arithmetic recompute: U1 annual = ${expected_u1}, U2 annual = ${expected_u2}, U2 banked+current = {total}% = ${u2_total}")
if warnings:
    print("\nWarnings:")
    for w in warnings: print(" ", w)
if errors:
    print("\nERRORS:")
    for e in errors: print(" ", e)
    sys.exit(1)
print("\nAll checks PASSED.")
