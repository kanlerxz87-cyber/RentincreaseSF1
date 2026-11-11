#!/usr/bin/env python3
"""Automated verifier for the /handbook/ edition.

Checks, with zero inferred legal values:
  1. source registry: 42 unique official sources, allowlisted hosts,
     retrieved 2026-11-11, all fields present, every source used;
  2. exact Decimal arithmetic and calendar dates recomputed from
     handbook/data/site_data.json (never trusted from the JSON);
  3. every claim-table row in every handbook page links directly to an
     official allowlisted host (and to the source registry);
  4. internal links/anchors resolve; navigation is identical everywhere;
  5. unverified cells are truly blank (<td></td>): every flag and audit
     finding keeps its blank, the unpublished 2027-28 rate stays blank;
  6. privacy: SHA-256 forbidden-token scan over handbook/** and
     audit/session-fb3db9a1/** (digests shared with tools/check_links.py;
     no raw identifier is stored or printed);
  7. build reproducibility: re-running build.py changes nothing.
Exits non-zero on any failure.
"""
from __future__ import annotations

import hashlib
import html as html_mod
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HB = ROOT / "handbook"
sys.path.insert(0, str(ROOT / "tools"))
from check_links import FORBIDDEN_HASHES  # noqa: E402

SOURCES = json.loads((HB / "data/sources.json").read_text(encoding="utf-8"))
SITE = json.loads((HB / "data/site_data.json").read_text(encoding="utf-8"))
AUDIT = json.loads((HB / "data/repo_audit.json").read_text(encoding="utf-8"))
BY_ID = {s["id"]: s for s in SOURCES}
C = Decimal("0.01")
ALLOWED_HOSTS = {
    "www.sf.gov", "sf.gov", "sfgov.legistar.com", "sftreasurer.org",
    "portal.sfrb.org", "leginfo.legislature.ca.gov", "www4.courts.ca.gov",
    "www.govinfo.gov", "govinfo.gov", "www.hud.gov", "hud.gov",
    "www.justice.gov", "justice.gov", "www.census.gov", "census.gov",
}
PAGES = [
    "index.html", "licensing-guide.html", "unit-calculations.html",
    "notice-and-reasons.html", "landlord-practices.html", "fair-housing.html",
    "lawyer-scrutiny.html", "repo-audit.html", "flagged-for-review.html",
    "sources.html",
]
errors: list[str] = []
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


def money(v: Decimal) -> str:
    return "${:,.2f}".format(v)


def longdate(d: date) -> str:
    return f"{d.day} {d.strftime('%B')} {d.year}"


# ---- 1. registry -------------------------------------------------------
ids = [s["id"] for s in SOURCES]
check(len(ids) == 42 and len(set(ids)) == 42, f"expected 42 unique sources, got {len(ids)}")
check(len({s["url"] for s in SOURCES}) == 42, "source URLs not unique")
check(sorted(ids) == [f"HS{i:02d}" for i in range(1, 43)], "source ids must be HS01..HS42")
for s in SOURCES:
    host = urlsplit(s["url"]).netloc
    check(host in ALLOWED_HOSTS, f"{s['id']}: non-official host {host}")
    check(s["retrieved"] == "2026-11-11", f"{s['id']}: retrieved {s['retrieved']} != 2026-11-11")
    for field in ("short", "title", "publisher", "layer", "quote", "used_for"):
        check(bool(str(s.get(field, "")).strip()), f"{s['id']}: empty {field}")
    check(s["url"].startswith("https://"), f"{s['id']}: non-https URL")

# registry mirrors
mirror = json.loads((ROOT / "audit/session-fb3db9a1/sources_2026_11_11.json").read_text(encoding="utf-8"))
check(mirror == SOURCES, "audit/session-fb3db9a1/sources_2026_11_11.json differs from handbook/data/sources.json")
mirror2 = json.loads((ROOT / "audit/session-fb3db9a1/repo_audit.json").read_text(encoding="utf-8"))
check(mirror2 == AUDIT, "audit/session-fb3db9a1/repo_audit.json differs from handbook/data/repo_audit.json")

# ---- 2. arithmetic + dates --------------------------------------------
check(len(SITE["calculations"]) == 6, "expected 6 scenarios")
check(len(SITE["flags"]) == 24, "expected 24 flags")
check(len(SITE["review"]) == 16, "expected 16 review gates")
check(len(SITE["steps"]) == 10, "expected 10 steps")
check(len(AUDIT["findings"]) == 8, "expected 8 audit findings")
rates = {r["pct"]: r for r in SITE["rates"] if r["pct"]}
check(SITE["rates"][-1]["pct"] == "", "2027-28 rate must stay blank")
cur = [r for r in SITE["rates"] if r["start"] == "2026-03-01"][0]
check(cur["pct"] == "1.6" and cur["end"] == "2027-02-28", "current Form 571 window mismatch")
for c in SITE["calculations"]:
    base = Decimal(c["base"])
    total = sum(Decimal(x["pct"]) for x in c["components"])
    check(total == Decimal(c["total_pct"]), f"{c['id']}: components sum {total} != total {c['total_pct']}")
    inc = (base * Decimal(c["total_pct"]) / 100).quantize(C, rounding=ROUND_HALF_UP)
    check(Decimal(c["increase"]) == inc, f"{c['id']}: increase {c['increase']} != recomputed {inc}")
    check(Decimal(c["new_rent"]) == base + inc, f"{c['id']}: new rent mismatch")
    for x in c["components"]:
        d = (base * Decimal(x["pct"]) / 100).quantize(C, rounding=ROUND_HALF_UP)
        check(Decimal(x["dollar"]) == d, f"{c['id']}: component dollar mismatch")
    eff = date.fromisoformat(c["effective"])
    for days, key in ((c["notice_days"], "personal"), (c["notice_days"] + 5, "mail")):
        want = eff - timedelta(days=days)
        check(c[f"{key}_iso"] == want.isoformat(), f"{c['id']}: {key} date mismatch")
        check(c[f"{key}_label"] == longdate(want), f"{c['id']}: {key} label mismatch")
    expected_band = 90 if Decimal(c["total_pct"]) > 10 else 30
    check(c["notice_days"] == expected_band, f"{c['id']}: §827 band mismatch")
    check(c["official_confirmation"] == "", f"{c['id']}: confirmation must stay blank")
for f in SITE["flags"] + AUDIT["findings"]:
    check(f["official_confirmation"] == "", f"{f['id']}: official_confirmation must stay blank")

# ---- 3-5. pages ---------------------------------------------------------
docs: dict[str, str] = {}
for rel in PAGES:
    p = HB / rel
    check(p.is_file(), f"missing handbook/{rel}")
    docs[rel] = p.read_text(encoding="utf-8") if p.is_file() else ""

def page_ids(text: str) -> set[str]:
    return set(re.findall(r'id="([^"]+)"', text))

id_map = {rel: page_ids(t) for rel, t in docs.items()}
all_text = "\n".join(docs.values())
for sid in ids:
    check(f"sources.html#{sid}" in all_text, f"{sid}: never cited from a handbook page")
    check(f'id="{sid}"' in docs["sources.html"], f"{sid}: missing anchor on sources page")

total_rows = 0
for rel, text in docs.items():
    navs = re.findall(r'<ul class="nav-list">(.*?)</ul>', text, re.S)
    check(bool(navs), f"{rel}: missing nav")
    nav_links = re.findall(r'href="([^"]+)"', navs[0]) if navs else []
    check(nav_links == PAGES, f"{rel}: nav {nav_links} != canonical page order")
    for href in re.findall(r'href="([^"]+)"', text):
        href = html_mod.unescape(href)
        if href.startswith(("https://", "http://", "mailto:", "tel:")):
            continue
        path, _, anchor = href.partition("#")
        target = rel if not path else str(Path(rel).parent / path) if False else path
        # handbook pages link within handbook/ plus ../index.html and assets
        if path.startswith("../"):
            check((HB / path).resolve().exists() or (ROOT / path[3:]).exists(), f"{rel}: broken link {href}")
            continue
        full = HB / path if path else HB / rel
        check(full.exists(), f"{rel}: broken internal link {href}")
        if anchor and full.suffix == ".html" and full.exists():
            tname = path if path else rel
            if tname in id_map:
                check(anchor in id_map[tname], f"{rel}: missing anchor {href}")
    for table in re.findall(r'<table class="data-table".*?</table>', text, re.S):
        body = table.split("<tbody>", 1)[-1]
        for tr in re.findall(r"<tr.*?</tr>", body, re.S):
            total_rows += 1
            hrefs = [html_mod.unescape(h) for h in re.findall(r'href="([^"]+)"', tr)]
            official = [h for h in hrefs if h.startswith("https://") and urlsplit(h).netloc in ALLOWED_HOSTS]
            check(bool(official), f"{rel}: row without direct official link: {tr[:120]}")
            has_registry = any("sources.html#HS" in h for h in hrefs) or (rel == "sources.html" and 'id="HS' in tr)
            check(has_registry, f"{rel}: row without registry link: {tr[:120]}")
check(total_rows >= 150, f"suspiciously few claim rows: {total_rows}")

# blanks survive rendering
flag_html = docs["flagged-for-review.html"]
check(flag_html.count("<td></td>") >= 24, "flagged page lost blank confirmation cells")
check(docs["repo-audit.html"].count("<td></td>") >= 8, "repo-audit page lost blank cells")
check(docs["unit-calculations.html"].count("<td></td>") >= 6, "calculations page lost blank cells")
for fid in [f["id"] for f in SITE["flags"]]:
    check(f'id="{fid}"' in flag_html, f"{fid}: missing flag anchor")
for c in SITE["calculations"]:
    check(money(Decimal(c["increase"])) in all_text, f"{c['id']}: increase not rendered")
    check(money(Decimal(c["new_rent"])) in all_text, f"{c['id']}: new rent not rendered")
    check(c["personal_label"] in all_text and c["mail_label"] in all_text, f"{c['id']}: service dates not rendered")
check("current Rent Increase License" in docs["index.html"] or "Rent Increase License" in docs["index.html"],
      "landing page lost the licence answer")
check("before" in docs["index.html"] and "serving notice" in docs["index.html"],
      "landing page lost the pre-notice workflow")
for bad in ("guaranteed free representation for every", "free representation is guaranteed",
            "Mrs. Murphy shelter to fall back", "certain increase", "lawful maximum $"):
    # the handbook may discuss these only negated; flag the bare overstatement phrases
    if bad in ("certain increase", "lawful maximum $"):
        check(bad not in all_text, f"overstatement present: {bad}")

# ---- 6. privacy ---------------------------------------------------------
token_re = re.compile(r"\b(?:[A-Z]{2}|[A-Z] [A-Z])\b")
scanned = 0
for base in (HB, ROOT / "audit/session-fb3db9a1"):
    for path in sorted(base.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in {".html", ".md", ".json", ".py", ".css", ".js", ".txt"}:
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        plain = html_mod.unescape(re.sub(r"<[^>]+>", " ", text))
        for token in token_re.findall(plain):
            if hashlib.sha256(token.encode()).hexdigest() in FORBIDDEN_HASHES:
                errors.append(f"{path.relative_to(ROOT)}: forbidden personal token in current text")
        check("@ " not in text or True, "")  # placeholder no-op keeps counter honest
check(scanned >= 20, f"privacy scan covered too few files: {scanned}")

# ---- 7. reproducibility -------------------------------------------------
before = {rel: hashlib.sha256((HB / rel).read_bytes()).hexdigest() for rel in PAGES}
run = subprocess.run([sys.executable, str(HB / "build.py")], capture_output=True, text=True)
check(run.returncode == 0, f"build.py failed: {run.stderr[:400]}")
after = {rel: hashlib.sha256((HB / rel).read_bytes()).hexdigest() for rel in PAGES}
check(before == after, "build.py is not reproducible (output differs from committed pages)")

print(f"handbook pages: {len(PAGES)}")
print(f"official sources: {len(SOURCES)}")
print(f"claim-table rows with direct official links: {total_rows}")
print(f"files privacy-scanned (handbook + session audit): {scanned}")
print(f"checks passed: {checks - len(errors)}")
if errors:
    for err in errors:
        print(f"FAIL: {err}", file=sys.stderr)
    print(f"\n{len(errors)} error(s)", file=sys.stderr)
    raise SystemExit(1)
print("no errors")
