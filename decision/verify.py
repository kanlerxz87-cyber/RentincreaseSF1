#!/usr/bin/env python3
"""Independent verifier for the /decision/ edition.

Re-derives every figure from decision/data/*.json without importing build.py's
computation, then checks links, anchors, per-row citation, blank-cell discipline,
privacy and external-URL registration.

Exits non-zero on any failure.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

SRC = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
RATES = json.loads((DATA / "rates.json").read_text(encoding="utf-8"))
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))

SOURCES = {s["id"]: s for s in SRC["sources"]}
PERIODS = RATES["periods"]
PAGES = SITE["pages"]
FLAGS = SITE["flags"]

TODAY = date(2026, 11, 13)
CENT = Decimal("0.01")

checks = 0
errors: list[str] = []


def ok() -> None:
    global checks
    checks += 1


def fail(msg: str) -> None:
    global checks
    checks += 1
    errors.append(msg)


def d(s: str) -> date:
    y, m, dd = (int(x) for x in str(s).split("-"))
    return date(y, m, dd)


def longdate(v: date) -> str:
    return "{d.day} {m} {d.year}".format(
        d=v,
        m=["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"][v.month - 1],
    )


def money(v: Decimal) -> str:
    return "${:,.2f}".format(v.quantize(CENT, rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ 1. files
html_files = sorted(HERE.glob("*.html"))
if not html_files:
    fail("no HTML files generated")
else:
    ok()

docs = {p.name: p.read_text(encoding="utf-8") for p in html_files}
ids_of = {n: set(re.findall(r'\bid="([^"]+)"', t)) for n, t in docs.items()}

expected = {p["file"] for p in PAGES}
if expected - set(docs):
    fail("missing generated pages: {}".format(sorted(expected - set(docs))))
else:
    ok()

# ------------------------------------------------------- 2. links and anchors
for name, text in docs.items():
    for attr, value in re.findall(r'\b(href|src)="([^"]+)"', text):
        if value.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
            continue
        target, _, frag = value.partition("#")
        resolved = target if target else name
        if resolved not in docs and not (HERE / resolved).exists():
            fail("{}: broken link '{}'".format(name, value))
            continue
        if frag:
            pool = ids_of.get(resolved) or set(
                re.findall(r'\bid="([^"]+)"', (HERE / resolved).read_text(encoding="utf-8")))
            if frag not in pool:
                fail("{}: dangling anchor '{}'".format(name, value))
            else:
                ok()
        else:
            ok()

# -------------------------------------------------------------- 3. navigation
nav_sets = set()
for name, text in docs.items():
    m = re.search(r'<nav class="main"[^>]*>(.*?)</nav>', text, re.S)
    if not m:
        fail("{}: no main navigation".format(name))
        continue
    nav_sets.add(tuple(re.findall(r'href="([^"#]+)"', m.group(1))))
if len(nav_sets) != 1:
    fail("navigation differs between pages: {} variants".format(len(nav_sets)))
else:
    ok()

# ------------------------------------------- 4. every data-table row is cited
SRC_TABLE_PAGES = {"sources.html"}
total_rows = 0
for name, text in docs.items():
    for tbl in re.findall(r'<table class="data-table">(.*?)</table>', text, re.S):
        body = re.search(r"<tbody>(.*?)</tbody>", tbl, re.S)
        if not body:
            continue
        for row in re.findall(r"<tr>(.*?)</tr>", body.group(1), re.S):
            total_rows += 1
            if name in SRC_TABLE_PAGES:
                ok()
                continue
            if 'class="srcref"' in row:
                ok()
            else:
                fail("{}: data-table row without an official source link: {}".format(
                    name, re.sub(r"<[^>]+>", " ", row)[:110].strip()))

# ------------------------------------------------ 5. external URLs registered
registered = {s["url"] for s in SOURCES.values()}
for name, text in docs.items():
    for url in re.findall(r'href="(https?://[^"]+)"', text):
        # the renderer HTML-escapes '&' in query strings; compare unescaped
        raw = url.replace("&amp;", "&")
        if raw in registered:
            ok()
        else:
            fail("{}: unregistered external URL {}".format(name, url))

# ------------------------------------- 6. independent arithmetic re-derivation
def rate_at(when: date):
    for p in PERIODS:
        if d(p["start"]) <= when <= d(p["end"]):
            return Decimal(p["pct"])
    return None


BASE = {"A": Decimal("3995.00"), "B": Decimal("3150.00")}
BANKED_B = ["2020-06-01", "2021-06-01", "2022-06-01", "2023-06-01",
            "2024-06-01", "2025-06-01", "2026-06-01"]

EXPECTED = {
    "A-1": dict(unit="A", eff="2027-02-01", banked=[], annual="rate"),
    "A-2": dict(unit="A", eff="2027-02-01", banked=["2026-02-01"], annual="rate"),
    "A-3": dict(unit="A", eff="2027-04-01", banked=["2026-02-01"], annual="unknown"),
    "B-1": dict(unit="B", eff="2027-06-01", banked=BANKED_B, annual="none"),
    "B-2": dict(unit="B", eff="2027-06-01", banked=BANKED_B, annual="unknown"),
}

for sid, spec in EXPECTED.items():
    eff = d(spec["eff"])
    base = BASE[spec["unit"]]
    banked = sum((rate_at(d(y)) for y in spec["banked"]), Decimal("0")).quantize(Decimal("0.1"))

    if spec["annual"] == "rate":
        ann = rate_at(eff)
        known = ann is not None
    elif spec["annual"] == "none":
        ann, known = Decimal("0"), True
    else:
        ann, known = None, False

    if known:
        total = (banked + ann).quantize(Decimal("0.1"))
        amount = (base * total / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
        rent = (base + amount).quantize(CENT, rounding=ROUND_HALF_UP)
    else:
        total = None
        if sid == "A-3":
            amount = (base * banked / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
            rent = (base + amount).quantize(CENT, rounding=ROUND_HALF_UP)
        else:
            amount = rent = None

    thresh = total if total is not None else banked
    days = 90 if thresh > Decimal("10") else 30
    want = dict(
        banked="{}%".format(banked.normalize()),
        annual="{}%".format(ann.normalize()) if known else "unverified",
        total="{}%".format(total.normalize()) if total is not None else "unverified",
        amount=money(amount) if amount is not None else "unverified",
        rent=money(rent) if rent is not None else "unverified",
        days="{} days".format(days),
        serve=longdate(eff - timedelta(days=days)),
        mail=longdate(eff - timedelta(days=days + 5)),
    )

    for page in ("index.html", "rates.html"):
        text = docs[page]
        m = re.search(
            r"<strong>{}</strong>.*?</tr>".format(re.escape(sid)), text, re.S)
        if not m:
            fail("{}: scenario {} not found".format(page, sid))
            continue
        row = re.sub(r"<[^>]+>", "|", m.group(0))
        row = re.sub(r"\|+", "|", row)
        for key, value in want.items():
            if value in row:
                ok()
            else:
                fail("{}: scenario {} — expected {} '{!r}' in row".format(page, sid, key, value))

# ------------------------------------------- 7. rate table matches Form 571
rates_doc = docs["rates.html"]
if len(re.findall(r'<td><strong>[\d.]+%</strong></td>', rates_doc)) == len(PERIODS):
    ok()
else:
    fail("rates.html: expected {} rate rows, found {}".format(
        len(PERIODS), len(re.findall(r'<td><strong>[\d.]+%</strong></td>', rates_doc))))

cur = [p for p in PERIODS if p["start"] == "2026-03-01"][0]
if cur["pct"] == "1.6":
    ok()
else:
    fail("current published rate is not 1.6% in rates.json")

# ------------------------------------------------------- 8. flags and anchors
flag_doc = docs["flagged.html"]
for f in FLAGS:
    if 'id="{}"'.format(f["id"]) in flag_doc:
        ok()
    else:
        fail("flagged.html: missing flag {}".format(f["id"]))
    if not f["src"]:
        fail("flag {} has no source".format(f["id"]))
    else:
        ok()

src_doc = docs["sources.html"]
for s in SOURCES.values():
    if 'id="{}"'.format(s["id"]) in src_doc:
        ok()
    else:
        fail("sources.html: missing source {}".format(s["id"]))
    if "verified_passage" not in s or len(s["verified_passage"]) < 40:
        fail("source {} has no verified passage".format(s["id"]))
    else:
        ok()

# ------------------------------------------------------------- 9. privacy scan
# Publicly published agency contact lines, printed on the agencies' own pages.
# These are not personal information and are allow-listed explicitly rather than
# by loosening the pattern.
AGENCY_LINES = {"415-252-4600", "415-252-4602", "415-701-2311", "415-252-4601"}

FORBIDDEN = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "email address"),
    (re.compile(r"\b(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b"), "telephone number"),
    (re.compile(r"\b\d{1,5}\s+(?:Sunset|Irving|Judah|Noriega|Taraval|Quintara|Kirkham|Lawton|"
                r"Moricaga|Pacheco|Ortega|Wawona|Vicente|Ulloa|Santiago|Avenue|Street)\b", re.I),
     "street address"),
]
# Tenant initials are never written into this file. They are detected by SHA-256
# digest, using the same six digests the repository's own check_links.py uses, so
# the verifier can catch them without ever containing them.
FORBIDDEN_HASHES = {
    "01efd0141d7d80509ee44bbbb2dee48875711d55358bd9a91bf22d5208ffa93d",
    "0b28c4215599de9c8f7019402d7eaeccc8cbdc5103aeca7427774222c2bf2f16",
    "158dc33a8be8ae49804b3fa72e2e116edb683730b51752bdb552435f31f0ba5a",
    "27c9478468718ed43669f8b2bbac3694d1f03287a6347d4c9adadc9d12f9ecf5",
    "399ad8e221e6815cd19b54cd7f313335f9bab0ecc681615af552c64ea3901b0f",
    "569ec6135d377e8ac326be2be2fd4cd8f3538fc3c23f33a89e81a4ed83671b7e",
}
INITIAL_TOKEN = re.compile(r"\b(?:[A-Z]{2}|[A-Z] [A-Z])\b")

def privacy_scan(name: str, text: str) -> None:
    for pattern, label in FORBIDDEN:
        for m in pattern.finditer(text):
            token = m.group(0).strip()
            if label == "telephone number" and token in AGENCY_LINES:
                ok()
                continue
            fail("{}: {!r} looks like a {}".format(name, token[:40], label))
    for token in INITIAL_TOKEN.findall(text):
        if hashlib.sha256(token.encode()).hexdigest() in FORBIDDEN_HASHES:
            fail("{}: contains forbidden personal token".format(name))
        else:
            ok()


for name, text in docs.items():
    privacy_scan(name, text)

# also scan the data files that drive the site
for f in sorted(DATA.glob("*.json")):
    privacy_scan(f.name, f.read_text(encoding="utf-8"))
ok()

# ------------------------------------------- 10. blank-cell discipline is real
blank_count = sum(len(re.findall(r'class="blank"', t)) for t in docs.values())
if blank_count >= 8:
    ok()
else:
    fail("expected blank/unverified cells to be rendered, found only {}".format(blank_count))

# ------------------------------------------------------------------- summary
print("checks run : {}".format(checks))
print("table rows : {}".format(total_rows))
print("blank cells: {}".format(blank_count))
if errors:
    print("\nFAILED ({}):".format(len(errors)))
    for e in errors:
        print("  - {}".format(e))
    sys.exit(1)
print("\nOK — 0 failures")
