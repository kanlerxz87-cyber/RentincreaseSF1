#!/usr/bin/env python3
"""Independent assurance checks for the corrected canonical dashboard.

Checks reproducible inputs, arithmetic, notice dates, source/flag coverage,
internal links, required caution labels, source manifests, and repository-wide
current-text privacy. Official legal values are never inferred by this checker.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
HUB = json.loads((ROOT / "hub/data.json").read_text(encoding="utf-8"))
AUDIT = json.loads((ROOT / "audit/final-integration/findings.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / "audit/final-integration/source-manifest.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(ROOT / "tools"))
from check_links import FORBIDDEN_HASHES  # noqa: E402

PAGES = ["index.html"] + [f"hub/{n}" for n in (
    "licensing.html", "limits.html", "notice.html", "practice.html",
    "fair-housing.html", "review.html", "flags.html", "sources.html",
)] + ["assurance/index.html"]
C = Decimal("0.01")
errors: list[str] = []
checks = 0


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        errors.append(message)


def money(value: Decimal) -> str:
    return "${:,.2f}".format(value)


def longdate(value: date) -> str:
    return f"{value.day} {value.strftime('%B')} {value.year}"


def ids(document: str) -> set[str]:
    return set(re.findall(r'id="([^"]+)"', document))


# Required files and internal links.
docs: dict[str, str] = {}
for rel in PAGES:
    path = ROOT / rel
    check(path.is_file(), f"missing canonical page {rel}")
    docs[rel] = path.read_text(encoding="utf-8") if path.is_file() else ""
id_map = {rel: ids(doc) for rel, doc in docs.items()}

# Reconciled Markdown entry points must not contain broken local links.
for rel in ("README.md", "EXECUTIVE_SUMMARY.md", "EXECUTIVE-SUMMARY.md", "SOURCES.md", "VERIFICATION.md"):
    text = (ROOT / rel).read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("https://", "http://", "mailto:", "tel:", "#")):
            continue
        path = target.split("#", 1)[0]
        if path:
            check((ROOT / path).exists(), f"{rel}: broken local Markdown link {target}")

for rel, doc in docs.items():
    for href in re.findall(r'href="([^"]+)"', doc):
        href = html.unescape(href)
        if href.startswith(("https://", "http://", "mailto:", "tel:")):
            continue
        if href.startswith("#"):
            target, anchor = rel, href[1:]
        else:
            path, _, anchor = href.partition("#")
            target = os.path.normpath(str(Path(rel).parent / path)) if path else rel
        full = ROOT / target
        check(full.exists(), f"{rel}: broken internal link {href}")
        if full.exists() and anchor:
            if target not in id_map and target.endswith(".html"):
                id_map[target] = ids(full.read_text(encoding="utf-8"))
            check(anchor in id_map.get(target, set()), f"{rel}: missing anchor {href}")

# Every assurance claim-table row has official-source support.
assurance = docs["assurance/index.html"]
assurance_rows = 0
for table in re.findall(r'<table class="data-table">(.*?)</table>', assurance, re.S):
    body = table.split("<tbody>", 1)[-1]
    for tr in re.findall(r"<tr>(.*?)</tr>", body, re.S):
        assurance_rows += 1
        check("hub/sources.html#S" in tr, f"assurance row lacks official source: {tr[:100]}")
check(assurance_rows == len(AUDIT["corrections"]) + 4 + 4 + len(AUDIT["residual_flag_ids"]),
      f"unexpected assurance table row count {assurance_rows}")

# Official source registry and live-retrieval manifest are complete and bounded.
source_ids = [s["id"] for s in HUB["sources"]]
check(len(source_ids) == len(set(source_ids)) >= 26, "expected at least 26 unique official sources")
check(len(MANIFEST) == len(source_ids), "source manifest length mismatch")
manifest_by_id = {m["id"]: m for m in MANIFEST}
allowed_hosts = {
    "www.sf.gov", "sf.gov", "leginfo.legislature.ca.gov", "www4.courts.ca.gov",
    "www.hud.gov", "hud.gov", "www.justice.gov", "justice.gov",
    # City of San Francisco official publishers, added 2026-11-08 with live retrieval:
    # sftreasurer.org  -> SF Office of the Treasurer & Tax Collector (Business Registration
    #                     Certificate and lessor-of-residential-real-estate guidance)
    # sfgov.legistar.com -> the Board of Supervisors' legislation portal, reached from sf.gov/bos
    "sftreasurer.org", "sfgov.legistar.com",
}
for s in HUB["sources"]:
    sid = s["id"]
    host = urlsplit(s["url"]).netloc
    check(host in allowed_hosts, f"{sid}: non-official or unapproved source host {host}")
    check(sid in manifest_by_id, f"{sid}: absent from retrieval manifest")
    if sid in manifest_by_id:
        m = manifest_by_id[sid]
        check(m["url"] == s["url"], f"{sid}: manifest URL mismatch")
        check(m["retrieved"] in ("2026-11-07", "2026-11-08", "2026-11-10"),
              f"{sid}: retrieval date {m['retrieved']} is not a recorded live-verification date")
        # The manifest must carry the date this source was actually fetched, not a blanket date.
        check(m["retrieved"] == s.get("retrieved"),
              f"{sid}: manifest date {m['retrieved']} != registry date {s.get('retrieved')}")
        check(m["result"] == "Retrieved and read from official publisher", f"{sid}: retrieval result missing")
    for field in ("title", "publisher", "level", "quote", "used_for"):
        check(bool(str(s.get(field, "")).strip()), f"{sid}: empty {field}")

# Every source is actually used by the canonical pages.
canonical_text = "\n".join(docs[rel] for rel in PAGES if rel != "assurance/index.html")
for sid in source_ids:
    check(f"sources.html#{sid}" in canonical_text or f'id="{sid}"' in canonical_text,
          f"{sid}: registered but not used")

# Arithmetic and dates are independently recomputed.
for unit in ("U1", "U2"):
    u = HUB["units"][unit]
    calc = HUB["calculations"][unit]
    base = Decimal(u["base_rent"])
    annual_pct = Decimal(calc["annual_pct"])
    banked_pct = Decimal(calc["banked_total_pct"])
    total_pct = Decimal(calc["total_pct"])
    check(annual_pct + banked_pct == total_pct, f"{unit}: percentage sum mismatch")
    annual = (base * annual_pct / 100).quantize(C, rounding=ROUND_HALF_UP)
    banked = (base * banked_pct / 100).quantize(C, rounding=ROUND_HALF_UP)
    total = (base * total_pct / 100).quantize(C, rounding=ROUND_HALF_UP)
    check(annual + banked == total, f"{unit}: dollar components do not add")
    check(base + annual == Decimal(u["base_rent"]) + annual, f"{unit}: invalid base arithmetic")
    for amount in (annual, total, base + annual, base + total):
        check(money(amount) in assurance, f"{unit}: computed amount {money(amount)} absent from assurance")
    eff = date.fromisoformat(calc["annual_effective"])
    for days in {30, int(calc["notice_days"])}:
        personal = eff - timedelta(days=days)
        mail = eff - timedelta(days=days + 5)
        check(longdate(personal) in assurance, f"{unit}: personal-service date missing for {days} days")
        check(longdate(mail) in assurance, f"{unit}: mail date missing for {days} days")

# Known source values and scenario inputs remain distinct.
check(HUB["units"]["U2"]["base_rent"] == "3150.00", "Unit 2 scenario input changed unexpectedly")
check("lease-start" in HUB["units"]["U2"]["base_status"], "Unit 2 lease-start caveat missing")
check("not expressly as the current base rent" in HUB["units"]["U2"]["base_status"],
      "Unit 2 current-base caveat missing")
check("fixed-term/month-to-month" in HUB["units"]["U1"]["occupancy_note"],
      "Unit 1 fixed-term caveat missing")
check(all(b["conditional"] for b in HUB["calculations"]["U2"]["banked"]),
      "every Unit 2 banked component must remain conditional")
check(HUB["rates"][0]["pct"] == "1.6" and HUB["rates"][0]["end"] == "2027-02-28",
      "current official rate period mismatch")
check(len(HUB["flags"]) >= 22, "expected at least 22 canonical flags")
check(len(HUB["review_rows"]) == 14, "expected 14 review checks")
for fid in ("H-01", "H-03", "H-17", "H-18", "H-19", "H-20"):
    check(fid in {f["id"] for f in HUB["flags"]}, f"missing required flag {fid}")
    check(f"flags.html#{fid}" in canonical_text, f"{fid}: not linked from canonical content")

# The exact overstatements corrected by this audit must not return.
for rel in PAGES[:-1]:
    doc = docs[rel]
    for forbidden in (
        "Unit 1 — certain increase", "Unit 2 — lawful maximum", "No, for 180 days",
        "free representation is available", "Get free representation in 94122",
        "Seven checks pass", "Seven can be answered", "Sixteen items",
        "Two official pages state different banking look-back tests",
        "A conforming amount in a nonconforming notice is void",
        "Unit 2 — $3,150.00 a month, unchanged since 1 June 2019",
    ):
        check(forbidden not in doc, f"{rel}: stale overstatement returned: {forbidden}")

# Root and flags contain explicit blank official-confirmation cells, not inferred values.
check(docs["index.html"].count("<td></td>") >= 7, "root official-confirmation blanks missing")
check(docs["hub/flags.html"].count("<td></td>") >= 8, "flag-page official-confirmation blanks missing")
check("scenario date 1 February 2027" in docs["index.html"], "Unit 1 scenario date missing from root")
check("current Rent Increase License" in docs["index.html"], "individual-owner license answer missing")
check("effective date" in docs["index.html"], "effective-date license gate missing")
check("before</em> serving notice" in docs["index.html"], "recommended pre-notice workflow missing")

# Privacy scan over current text files (not Git history), using shared digests so
# no raw personal token is embedded in this checker or printed in output.
text_ext = {".html", ".md", ".json", ".csv", ".py", ".yml", ".yaml", ".txt", ".js", ".css"}
token_re = re.compile(r"\b(?:[A-Z]{2}|[A-Z] [A-Z])\b")
scanned = 0
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
        continue
    if path.suffix.lower() not in text_ext:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    scanned += 1
    for token in token_re.findall(html.unescape(re.sub(r"<[^>]+>", " ", text))):
        if hashlib.sha256(token.encode()).hexdigest() in FORBIDDEN_HASHES:
            errors.append(f"{path.relative_to(ROOT)}: forbidden personal token in current text")
check(scanned >= 120, f"privacy scan covered too few files: {scanned}")

print(f"canonical pages: {len(PAGES)}")
print(f"assurance claim rows with official sources: {assurance_rows}")
print(f"official sources / manifest rows: {len(source_ids)} / {len(MANIFEST)}")
print(f"current text files privacy-scanned: {scanned}")
print(f"checks passed: {checks - len(errors)}")
if errors:
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    print(f"\n{len(errors)} error(s)", file=sys.stderr)
    raise SystemExit(1)
print("no errors")
