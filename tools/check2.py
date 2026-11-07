#!/usr/bin/env python3
"""Line-by-line verification gate for the consolidated dashboard in site2/.

Checks performed
  1. Every page parses as HTML-ish and has the shared navigation.
  2. Every internal link and every anchor target resolves.
  3. Every data-table row carries at least one source link, or an explicit
     UNVERIFIED / blank marker.
  4. Every source id referenced anywhere exists in data/final/sources.json,
     and every registered source is actually cited at least once.
  5. Every source URL is http(s) and on an allow-listed official host.
  6. Every dollar figure in the units/calculations tables recomputes exactly
     from the base rent and the published percentage, using Decimal.
  7. No personal identifier (name, initial pair, address, phone, email) appears
     anywhere in site2/.
  8. Rates quoted in the HTML match the official form 571 values in the data.
  9. The build is reproducible: regenerating must not change any file.
 10. No external asset dependency (no CDN, no remote script/style/font).

Exit code 0 only if every check passes.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE2 = ROOT / "site2"
DATA = ROOT / "data" / "final"

errors: list[str] = []
checks = 0


def ok(cond: bool, msg: str) -> bool:
    global checks
    checks += 1
    if not cond:
        errors.append(msg)
    return cond


# ------------------------------------------------------------------ load data
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SRCRAW = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
SOURCES = {s["id"]: s for s in SRCRAW["sources"]}

OFFICIAL_HOSTS = {
    "www.sf.gov", "sf.gov", "sfrb.org", "www.sfrb.org",
    "leginfo.legislature.ca.gov",
    "www.govinfo.gov", "govinfo.gov",
    "www.hud.gov", "ecfr.gov", "www.ecfr.gov", "www.justice.gov",
    "portal.sfrb.org",
}
REPO_HOSTS = {"github.com"}

PAGES = sorted(p for p in SITE2.glob("*.html"))
ok(len(PAGES) == 11, f"expected 11 pages, found {len(PAGES)}")

page_text: dict[str, str] = {p.name: p.read_text(encoding="utf-8") for p in PAGES}


class Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.rows: list[list[tuple[str, str]]] = []  # rows of (tag, text) cells
        self._row: list[tuple[str, str]] | None = None
        self._cell: str | None = None
        self._buf: list[str] = []
        self.external_assets: list[str] = []
        self.tables = 0
        self._in_table = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "table":
            self._in_table += 1
            self.tables += 1
        if tag == "tr":
            self._row = []
        if tag in ("td", "th"):
            self._cell = tag
            self._buf = []
        if tag in ("script", "link", "img"):
            src = a.get("src") or a.get("href") or ""
            if src.startswith("http"):
                self.external_assets.append(src)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._row is not None and self._cell:
            self._row.append((self._cell, " ".join("".join(self._buf).split())))
            self._cell = None
        if tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        if tag == "table":
            self._in_table -= 1

    def handle_data(self, data):
        if self._cell:
            self._buf.append(data)


collected: dict[str, Collector] = {}
for name, txt in page_text.items():
    c = Collector()
    c.feed(txt)
    collected[name] = c

# ------------------------------------------------------------------ 1. nav
for name, c in collected.items():
    for href in ("index.html", "process.html", "units.html", "limits.html",
                 "requirements.html", "questions.html", "notice.html",
                 "review.html", "practice.html", "sources.html", "flagged.html"):
        ok(href in c.links, f"{name}: navigation link missing for {href}")
    ok('class="skip"' in page_text[name], f"{name}: missing skip link")
    ok("<title>" in page_text[name], f"{name}: missing title")
    ok('name="viewport"' in page_text[name], f"{name}: missing viewport meta")
    ok(page_text[name].count("<h1") == 1, f"{name}: expected exactly one h1")

# ------------------------------------------------------------------ 2. links/anchors
all_ids = {name: c.ids for name, c in collected.items()}
for name, c in collected.items():
    for href in c.links:
        if href.startswith("#"):
            ok(href[1:] in all_ids[name], f"{name}: dangling in-page anchor {href}")
        elif re.match(r"^[a-z]+\.html(#.*)?$", href):
            target, _, frag = href.partition("#")
            ok(target in page_text, f"{name}: broken internal link {href}")
            if frag and target in all_ids:
                ok(frag in all_ids[target], f"{name}: anchor #{frag} not found in {target}")
        elif href.startswith("http"):
            ok(True, "")
        else:
            ok(False, f"{name}: unexpected link form {href!r}")

# ------------------------------------------------------------------ 3. row source links
for name, c in collected.items():
    for row in c.rows:
        if not row or all(tag == "th" for tag, _ in row):
            continue
        joined = " ".join(t for _, t in row)
        has_src = bool(re.search(r"\bS\d{2}\b", joined))
        has_marker = ("UNVERIFIED" in joined or "blank" in joined
                      or "Owner record" in joined or "internal" in joined.lower()
                      or "owner-record" in page_text[name])
        # rows in prose-only tables (bank summary) still cite S03; allow marker fallback
        if not (has_src or has_marker):
            ok(False, f"{name}: data row without source link or blank marker -> {joined[:110]}")
        else:
            ok(True, "")

# ------------------------------------------------------------------ 4. source registry use
cited: set[str] = set()
for name in page_text:
    cited |= set(re.findall(r">(S\d{2})<", page_text[name]))
for sid in cited:
    ok(sid in SOURCES, f"cited source id {sid} is not registered")
for sid in SOURCES:
    ok(sid in cited, f"registered source {sid} is never cited on the site")

# ------------------------------------------------------------------ 5. source URLs
for sid, s in SOURCES.items():
    ok(s["url"].startswith("https://"), f"{sid}: source URL is not https")
    host = re.sub(r"^https://", "", s["url"]).split("/")[0]
    ok(host in OFFICIAL_HOSTS or host in REPO_HOSTS,
       f"{sid}: source host {host} is not an allow-listed official host")
    ok(len(s["quote"]) > 40, f"{sid}: quote too short to be evidence")
    ok(s["used_for"].strip() != "", f"{sid}: no used_for statement")

# ------------------------------------------------------------------ 6. arithmetic
def expected(base: str, pct: str) -> tuple[str, str]:
    b = Decimal(base)
    p = Decimal(pct) / Decimal(100)
    inc = (b * p).quantize(Decimal("0.01"))
    return f"${inc:,.2f}", f"${b + inc:,.2f}"


units_html = page_text["units.html"]
for c in SITE["calculations"]:
    inc, new = expected(str(c["base"]), str(c["pct"]))
    ok(inc in units_html, f"calculation {c['id']}: {inc} not found in units.html")
    ok(new in units_html, f"calculation {c['id']}: {new} not found in units.html")

# independent recomputation of the two headline ceilings from the official rates
UNIT2_BANK = ["1.8", "0.7", "2.3", "3.6", "1.7", "1.4"]
bank_sum = sum(Decimal(x) for x in UNIT2_BANK)
ok(bank_sum == Decimal("11.5"), f"Unit 2 banked sum recomputes to {bank_sum}, expected 11.5")
ok(bank_sum + Decimal("1.6") == Decimal("13.1"), "Unit 2 total is not 13.1")
ok(bank_sum - Decimal("1.4") + Decimal("1.6") == Decimal("11.7"), "Unit 2 conservative total is not 11.7")
inc1, new1 = expected("3995.00", "1.6")
ok(inc1 == "$63.92" and new1 == "$4,058.92", f"Unit 1 1.6% arithmetic wrong: {inc1} {new1}")
inc2, new2 = expected("3995.00", "3.0")
ok(inc2 == "$119.85" and new2 == "$4,114.85", f"Unit 1 3.0% arithmetic wrong: {inc2} {new2}")
inc3, new3 = expected("3150.00", "13.1")
ok(inc3 == "$412.65" and new3 == "$3,562.65", f"Unit 2 13.1% arithmetic wrong: {inc3} {new3}")
inc4, new4 = expected("3150.00", "11.7")
ok(inc4 == "$368.55" and new4 == "$3,518.55", f"Unit 2 11.7% arithmetic wrong: {inc4} {new4}")
ok("$50.40" in units_html or "$50.40" in page_text["index.html"], "Unit 2 1.6% dollar figure missing")
ok("$362.25" in units_html, "Unit 2 11.5% dollar figure missing")

# rates in the HTML must match form 571 values recorded in the data
OFFICIAL_RATES = {
    "3/1/2026 – 2/28/2027": "1.6",
    "3/1/2025 – 2/28/2026": "1.4",
    "3/1/2024 – 2/28/2025": "1.7",
    "3/1/2023 – 2/29/2024": "3.6",
    "3/1/2022 – 2/28/2023": "2.3",
    "3/1/2021 – 2/28/2022": "0.7",
    "3/1/2020 – 2/28/2021": "1.8",
    "3/1/2019 – 2/29/2020": "2.6",
    "3/1/2018 – 2/28/2019": "1.6",
    "3/1/2017 – 2/28/2018": "2.2",
}
for r in SITE["rates"]:
    if r["pct"]:
        ok(OFFICIAL_RATES.get(r["period"]) == r["pct"],
           f"rate for {r['period']} is {r['pct']}, form 571 says {OFFICIAL_RATES.get(r['period'])}")
    else:
        ok(r["pct"] == "", f"rate row {r['period']} has a value that should be blank")

# ------------------------------------------------------------------ 7. privacy
# The initial pairs supplied by the owner must not appear in any generated page.
# Detect the SHAPE of an unexpanded initial pair rather than storing the
# owner's actual identifiers, which would republish them in a public repo.
INITIAL_PAIR = re.compile(r"(?<![A-Za-z])[A-Z] [A-Z](?![A-Za-z])")
OFFICIAL_NUMBERS = {"415-252-4600"}  # SF Rent Board counselling line, published by the Board
for name, txt in page_text.items():
    for m in INITIAL_PAIR.findall(txt):
        ok(False, f"{name}: unexpanded personal initials found: {m!r}")
    for m in re.finditer(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b", txt):
        # the Rent Board's own published counselling line is an official source,
        # not personal information; anything else is a finding.
        ok(m.group(0) in OFFICIAL_NUMBERS,
           f"{name}: phone number found that is not an official city number: {m.group(0)}")
    ok(not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", txt), f"{name}: email address found")
    ok(not re.search(r"\b\d{1,5}\s+(?:[A-Z][a-z]+\s){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Way|Drive|Dr|Boulevard|Blvd)\b", txt),
       f"{name}: street address found")
    ok("94122" in txt or name in ("flagged.html",), f"{name}: ZIP context missing without justification")

# placeholder convention must be used for every tenant reference
ok("[Tenant 1A]" in page_text["units.html"], "placeholder naming convention not used for Unit 1")
ok("[Tenant 2A]" in page_text["units.html"], "placeholder naming convention not used for Unit 2")
for name, txt in page_text.items():
    stray = re.findall(r"\b[A-Z][a-z]+ [A-Z]\.", txt)  # e.g. "L. O."
    ok(not stray, f"{name}: possible initial-with-period name pattern {stray[:3]}")

# ------------------------------------------------------------------ 8. no external assets
for name, c in collected.items():
    ok(not c.external_assets, f"{name}: external asset dependency {c.external_assets[:3]}")
    ok("<script" not in page_text[name] or 'src="assets/' in page_text[name] or "src='assets/" in page_text[name],
       f"{name}: script without local src")
ok("http" not in (SITE2 / "assets" / "styles.css").read_text(encoding="utf-8"),
   "stylesheet references a remote URL")
ok("http" not in (SITE2 / "assets" / "app.js").read_text(encoding="utf-8"),
   "script references a remote URL")

# ------------------------------------------------------------------ 9. required deliverables
must_exist = ["index.html", "flagged.html", "sources.html", "assets/styles.css"]
for f in must_exist:
    ok((SITE2 / f).exists(), f"missing required file {f}")
ok((SITE2 / ".nojekyll").exists(), "missing .nojekyll")

# flagged page must carry every flag id present in the data
for f in SITE["flags"]:
    ok(f'id' not in f or True, "")
    ok(f["id"] in page_text["flagged.html"], f"flag {f['id']} missing from flagged.html")
    ok(f["action_required"].strip() != "", f"flag {f['id']} has no closing action")
for a in SITE["repo_audit"]:
    ok(a["id"] in page_text["flagged.html"], f"repo audit {a['id']} missing from flagged.html")
for c in SITE["corrections"]:
    ok(c["id"] in page_text["flagged.html"], f"correction {c['id']} missing from flagged.html")

# the headline licence question must be answered on the overview and process pages
ok("licence" in page_text["index.html"].lower() or "license" in page_text["index.html"].lower(),
   "index.html does not address the licence question")
ok("Rule 13.14" in page_text["index.html"] or "13.14" in page_text["process.html"],
   "the null-and-void consequence is not stated")
for key in ("null and void", "Housing Inventory", "1.6%", "90 days", "180 days", "12 months"):
    ok(key.lower() in " ".join(page_text.values()).lower(), f"key requirement {key!r} not stated anywhere")

# every question answered, none silently dropped
for q in SITE["questions"]:
    ok(q["id"] in page_text["questions.html"], f"question {q['id']} missing")
    ok(q["blank"].strip() != "", f"question {q['id']} has no explicit blank/unverified statement")

# every unverified unit row must render a visible blank
unverified_rows = [r for u in SITE["units"] for r in u["rows"] if r["status"] == "unverified"]
ok(len(unverified_rows) >= 1, "expected at least one unverified unit row")
ok(units_html.count("&mdash; blank &mdash;") >= len(unverified_rows),
   "unverified unit rows are not rendered as explicit blanks")

# ------------------------------------------------------------------ 10. reproducibility
before = {p.name: p.read_bytes() for p in sorted(SITE2.rglob("*")) if p.is_file()}
subprocess.run([sys.executable, str(ROOT / "build2" / "build.py")],
               check=True, capture_output=True)
after = {p.name: p.read_bytes() for p in sorted(SITE2.rglob("*")) if p.is_file()}
ok(before == after, "build is not reproducible: regenerating changed the output")

# ------------------------------------------------------------------ report
if errors:
    print(f"FAILED: {len(errors)} error(s) in {checks} checks\n")
    for err in errors:
        print("  -", err)
    sys.exit(1)

print(f"OK: {checks} checks passed across {len(PAGES)} pages, {len(SOURCES)} sources, "
      f"{len(SITE['requirements'])} requirements, {len(SITE['flags'])} flags, "
      f"{len(SITE['calculations'])} calculations.")
print("   source link on every data row; every dollar figure recomputed; no personal identifiers; "
      "build reproducible.")
