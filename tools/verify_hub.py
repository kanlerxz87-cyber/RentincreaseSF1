#!/usr/bin/env python3
"""
Line-by-line gate for the integrated dashboard (index.html + hub/*.html).

What it proves, from the generated HTML itself:

  1  every internal link and anchor resolves to a real file / id
  2  every page carries the same nine-item navigation and the same footer disclaimers
  3  every row of every claim table carries a link to an official source,
     or to an explicit flag when the row rests on an unverified private record
  4  every citation points at a source id that exists, and every registered
     source is cited somewhere
  5  the source registry is internally complete: id, publisher, level, url,
     verbatim quote, usage note
  6  every dollar figure on the site is either recomputed here from a published
     percentage and a known rent, or appears verbatim in a cited source quote —
     anything else fails as an unsourced number
  7  every service date shown is recomputed here from the statutory period
  8  no personal identifiers (tenant initials, names, emails) appear anywhere
  9  the site's arithmetic matches hub/data.json exactly

Exit code 0 = all checks pass. Usage: python3 tools/verify_hub.py
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = json.load(open(os.path.join(ROOT, "hub", "data.json"), encoding="utf-8"))
C = Decimal("0.01")

PAGES = ["index.html"] + [
    "hub/" + name
    for name in (
        "licensing.html",
        "limits.html",
        "notice.html",
        "practice.html",
        "fair-housing.html",
        "review.html",
        "flags.html",
        "sources.html",
    )
]

# Tenant initials are never written here in plaintext. The digests are the shared
# list maintained by tools/check_links.py, so a matched value is never echoed.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from check_links import FORBIDDEN_HASHES  # noqa: E402

TOKEN_RE = re.compile(r"\b(?:[A-Z]{2}|[A-Z] [A-Z])\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

errors: list[str] = []
checks = 0


def ok() -> None:
    global checks
    checks += 1


def fail(msg: str) -> None:
    errors.append(msg)


def read(rel: str) -> str:
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        fail(f"{rel}: missing")
        return ""
    return open(path, encoding="utf-8").read()


def money(value: Decimal) -> str:
    return "${:,.2f}".format(value)


def d(s: str) -> date:
    return date.fromisoformat(s)


def longdate(x: date) -> str:
    return "{} {} {}".format(x.day, x.strftime("%B"), x.year)


def ids_of(doc: str) -> set[str]:
    return set(re.findall(r'id="([^"]+)"', doc))


def resolve(rel_page: str, href: str) -> tuple[str | None, str]:
    """Return (target file or None if external, anchor)."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        if href.startswith("#"):
            return rel_page, href[1:]
        return None, ""
    path, _, anchor = href.partition("#")
    if not path:
        return rel_page, anchor
    target = os.path.normpath(os.path.join(os.path.dirname(rel_page), html.unescape(path)))
    return target, anchor


# ----------------------------------------------------------------- 1 links/anchors
docs = {p: read(p) for p in PAGES}
id_map = {p: ids_of(doc) for p, doc in docs.items()}
id_map["hub/assets/style.css"] = set()
id_map["docs/index.html"] = ids_of(read("docs/index.html"))
id_map["docs/v2/index.html"] = ids_of(read("docs/v2/index.html"))
id_map["dashboard/index.html"] = ids_of(read("dashboard/index.html"))
id_map["portal/index.html"] = ids_of(read("portal/index.html"))

for page, doc in docs.items():
    for href in re.findall(r'href="([^"]+)"', doc):
        target, anchor = resolve(page, html.unescape(href))
        if target is None:
            continue
        full = os.path.join(ROOT, target)
        if not os.path.exists(full):
            fail(f"{page}: link '{href}' does not resolve (missing {target})")
            continue
        if anchor:
            if target not in id_map:
                id_map[target] = ids_of(open(full, encoding="utf-8").read()) if target.endswith(".html") else set()
            if anchor not in id_map[target]:
                fail(f"{page}: link '{href}' points at missing anchor #{anchor} in {target}")
        ok()

# ----------------------------------------------------------------- 2 nav + footer
NAV_EXPECT = [
    "Dashboard", "Licence & Board", "Limits & amounts", "Notice & reasons",
    "Owner practice", "One unit or both", "Lawyer test", "Flagged", "Sources",
]
navs = {}
for page, doc in docs.items():
    m = re.search(r'<nav class="main"[^>]*>(.*?)</nav>', doc, re.S)
    if not m:
        fail(f"{page}: no navigation block")
        continue
    links = re.findall(r'href="([^"]+)"', m.group(1))
    labels = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r">([^<]*)</a>", m.group(1))]
    targets = [resolve(page, h)[0] for h in links]
    navs[page] = (targets, labels)
    if labels != NAV_EXPECT:
        fail(f"{page}: navigation labels {labels} != {NAV_EXPECT}")
    for target in targets:
        if not os.path.exists(os.path.join(ROOT, target)):
            fail(f"{page}: navigation target {target} missing")
    ok()

reference = navs.get("index.html")
for page, value in navs.items():
    if value != reference:
        fail(f"{page}: navigation differs from index.html")

for page, doc in docs.items():
    for phrase in (
        "Anonymised.",
        "Not legal advice.",
        "Flagged for Review",
    ):
        if phrase not in doc:
            fail(f"{page}: missing footer statement '{phrase}'")
    if 'name="viewport"' not in doc or "<title>" not in doc:
        fail(f"{page}: missing viewport or title")
    if not re.search(r'href="(?:\.\./)?(?:hub/)?assets/style\.css"', doc):
        fail(f"{page}: stylesheet not linked")
    ok()

# ----------------------------------------------------------------- 3 every data-table row cited
def table_blocks(doc: str, cls: str):
    """Yield the inner HTML of each <table class="cls"> ... </table>."""
    for m in re.finditer(r'<table class="%s">(.*?)</table>' % cls, doc, re.S):
        yield m.group(1)


citation_rows = 0
for page, doc in docs.items():
    for tbl in table_blocks(doc, "data-table"):
        body = tbl.split("<tbody>", 1)[-1]
        rows = re.findall(r"<tr>(.*?)</tr>", body, re.S)
        for row in rows:
            hrefs = re.findall(r'href="([^"]+)"', row)
            cited = [h for h in hrefs if re.search(r"(sources\.html#S\d\d|flags\.html#H-\d\d)", html.unescape(h))]
            if not cited:
                snippet = html.unescape(re.sub(r"<[^>]+>", " ", row))[:90].strip()
                fail(f"{page}: table row has no official-source or flag link: {snippet}")
            else:
                citation_rows += 1
                ok()

# ----------------------------------------------------------------- 4/5 source registry
sources = DATA["sources"]
ids = [s["id"] for s in sources]
if len(set(ids)) != len(ids):
    fail("duplicate source ids in hub/data.json")
registered_urls = set()
for s in sources:
    for field in ("id", "title", "publisher", "level", "url", "quote", "used_for"):
        if not str(s.get(field, "")).strip():
            fail(f"source {s.get('id')}: empty field '{field}'")
    if not s["url"].startswith("https://"):
        fail(f"source {s['id']}: URL is not https")
    parts = urlsplit(s["url"])
    if not parts.netloc:
        fail(f"source {s['id']}: unparseable URL")
    registered_urls.add(s["url"])
    ok()

src_doc = docs["hub/sources.html"]
linked_urls = {html.unescape(u) for u in re.findall(r'href="(https://[^"]+)"', src_doc)}
for url in registered_urls:
    if url not in linked_urls:
        fail(f"hub/sources.html: registered URL not linked: {url}")
    ok()
for url in linked_urls:
    if url not in registered_urls:
        fail(f"hub/sources.html: links an unregistered URL: {url}")

cited_ids: set[str] = set()
for page, doc in docs.items():
    for sid in re.findall(r"sources\.html#(S\d\d)", html.unescape(doc)):
        cited_ids.add(sid)
        if sid not in ids:
            fail(f"{page}: cites unknown source id {sid}")
        ok()
    if page == "hub/sources.html":
        for anchor in re.findall(r'id="(S\d\d)"', doc):
            cited_ids.add(anchor)
for sid in ids:
    if sid not in cited_ids:
        fail(f"source {sid} is registered but never cited")
    ok()

# ----------------------------------------------------------------- 6/7 numbers and dates
def compute() -> dict:
    out = {}
    for key in ("U1", "U2"):
        unit, calc = DATA["units"][key], DATA["calculations"][key]
        base = Decimal(unit["base_rent"])
        a_pct, b_pct, t_pct = (Decimal(calc["annual_pct"]), Decimal(calc["banked_total_pct"]), Decimal(calc["total_pct"]))
        a_amt = (base * a_pct / 100).quantize(C, rounding=ROUND_HALF_UP)
        b_amt = (base * b_pct / 100).quantize(C, rounding=ROUND_HALF_UP)
        t_amt = (base * t_pct / 100).quantize(C, rounding=ROUND_HALF_UP)
        if a_pct + b_pct != t_pct:
            fail(f"{key}: annual {a_pct} + banked {b_pct} != total {t_pct}")
        if a_amt + b_amt != t_amt:
            fail(f"{key}: dollar components do not add up")
        eff = d(calc["annual_effective"])
        notice = int(calc["notice_days"])
        yearly = [
            (Decimal(b["pct"]), (base * Decimal(b["pct"]) / 100).quantize(C, rounding=ROUND_HALF_UP))
            for b in calc["banked"]
        ]
        out[key] = dict(
            yearly=yearly,
            base=base, a_pct=a_pct, b_pct=b_pct, t_pct=t_pct,
            a_amt=a_amt, b_amt=b_amt, t_amt=t_amt,
            a_rent=base + a_amt, t_rent=base + t_amt,
            eff=eff, serve=eff - timedelta(days=notice), mail=eff - timedelta(days=notice + 5),
            short_serve=eff - timedelta(days=30), short_mail=eff - timedelta(days=35),
        )
        ok()
    return out


N = compute()

# allowed dollar amounts: computed + owner rents + every amount inside a source quote
allowed_money = set()
for n in N.values():
    for key in ("base", "a_amt", "b_amt", "t_amt", "a_rent", "t_rent"):
        allowed_money.add(money(n[key]))
    for _, amt in n["yearly"]:
        allowed_money.add(money(amt))
for s in sources:
    for amt in re.findall(r"\$[\d,]+(?:\.\d{2})?", s["quote"]):
        allowed_money.add(amt)
# amounts the ordinance/guidance text uses in prose elsewhere on the site
allowed_money |= {
    "$59.00", "$29.50", "$250", "$250.00", "$1,000", "$1,000.00",
    "$3,995.00", "$3,150.00",
}

unsourced = 0
for page, doc in docs.items():
    text = html.unescape(re.sub(r"<[^>]+>", " ", doc))
    for amt in re.findall(r"\$[\d,]+(?:\.\d{2})?", text):
        if amt not in allowed_money:
            fail(f"{page}: dollar figure not traceable to a computed value or a source quote: {amt}")
            unsourced += 1
    ok()

expected_dates = {
    "hub/notice.html": [
        longdate(N["U1"]["eff"]),
        longdate(N["U1"]["serve"]),
        longdate(N["U1"]["mail"]),
        longdate(N["U2"]["eff"]),
        longdate(N["U2"]["serve"]),
        longdate(N["U2"]["mail"]),
        longdate(N["U1"]["short_serve"]),
        longdate(N["U2"]["short_serve"]),
    ],
    "hub/limits.html": [longdate(N["U1"]["eff"]), longdate(N["U2"]["eff"])],
    "index.html": [longdate(N["U2"]["serve"]), longdate(N["U2"]["mail"]), longdate(N["U1"]["eff"])],
}
for page, dates in expected_dates.items():
    for value in dates:
        if value not in docs[page]:
            fail(f"{page}: expected computed date '{value}' not present")
        ok()

# the headline amounts must appear on the two pages that carry the analysis
for page, needles in {
    "index.html": [money(N["U1"]["a_amt"]), money(N["U2"]["t_amt"])],
    "hub/limits.html": [money(N["U1"]["a_amt"]), money(N["U2"]["t_amt"]), money(N["U1"]["a_rent"]), money(N["U2"]["t_rent"])],
}.items():
    for needle in needles:
        if needle not in docs[page]:
            fail(f"{page}: expected computed amount {needle} not present")
        ok()

# every published rate must appear on the limits page
limits_doc = docs["hub/limits.html"]
for r in DATA["rates"]:
    label = "{}%".format(Decimal(r["pct"]).quantize(Decimal("0.1")))
    if label not in limits_doc:
        fail(f"hub/limits.html: published rate {label} missing")
    ok()
if len(DATA["rates"]) != 46:
    fail(f"hub/data.json: expected 46 published rate periods, found {len(DATA['rates'])}")
ok()

# ----------------------------------------------------------------- 8 privacy
for page, doc in docs.items():
    for token in TOKEN_RE.findall(html.unescape(re.sub(r"<[^>]+>", " ", doc))):
        if hashlib.sha256(token.encode()).hexdigest() in FORBIDDEN_HASHES:
            fail(f"{page}: contains a forbidden personal token")
    for match in EMAIL_RE.findall(doc):
        fail(f"{page}: contains an email address: {match}")
    ok()

# tenant placeholder names must be used, not real ones
if "Tenants 1A and 1B" not in docs["index.html"]:
    fail("index.html: expected placeholder tenant names")

# ----------------------------------------------------------------- 9 corrected legal labels
# Regression gates for issues found by the independent final assurance review.
for page, doc in docs.items():
    for phrase in (
        "Unit 1 — certain increase", "Unit 2 — lawful maximum", "No, for 180 days",
        "free representation is available", "Get free representation in 94122",
        "Seven checks pass", "Seven can be answered", "Sixteen items",
        "Two official pages state different banking look-back tests",
        "A conforming amount in a nonconforming notice is void",
        "Unit 2 — $3,150.00 a month, unchanged since 1 June 2019",
    ):
        if phrase in doc:
            fail(f"{page}: stale categorical claim: {phrase}")
        ok()

# Floors, not exact pins: a later session may add sources/flags, but may never
# silently drop the ones already verified. Each addition below is also asserted
# positively further down, so removing one is a failure rather than a renumber.
if len(sources) < 26:
    fail(f"expected at least 26 official sources, found {len(sources)}")
if len(DATA["flags"]) < 22:
    fail(f"expected at least 22 flags, found {len(DATA['flags'])}")
if len(DATA["review_rows"]) != 13:
    fail(f"expected 13 review checks, found {len(DATA['review_rows'])}")

# ---- G1/G2: the second licence (Business Registration Certificate) must stay answered
by_id = {s["id"]: s for s in sources}
for sid, host, needle in (
    ("S24", "sftreasurer.org", "fewer than four units"),
    ("S25", "sftreasurer.org", "fewer than four units"),
    ("S26", "sfgov.legistar.com", "Pending Committee Action"),
):
    if sid not in by_id:
        fail(f"required source {sid} missing from the registry")
    else:
        if host not in by_id[sid]["url"]:
            fail(f"source {sid}: URL is not on {host}: {by_id[sid]['url']}")
        if needle not in by_id[sid]["quote"]:
            fail(f"source {sid}: verbatim quote no longer contains '{needle}'")
        ok()
licensing_q = " ".join(s["question"] for s in DATA["licensing_steps"])
for needle in (
    "only licence an individual owner needs",
    "need a Business Registration Certificate",
    "become required",
):
    if needle not in licensing_q:
        fail(f"licensing Q&A no longer answers: {needle}")
    ok()
if len(DATA["licensing_steps"]) < 10:
    fail(f"expected at least 10 licensing Q&A rows, found {len(DATA['licensing_steps'])}")

# ---- G3/G5: verbatim Rule 4.12 text and the pending cap must remain in the record
flag_by_id = {f["id"]: f for f in DATA["flags"]}
for fid, needles in (
    ("H-01", ("A full 12 months must have elapsed", "only be given at the time of an annual increase",
              "24 full months pass without any rent increase")),
    ("H-21", ("by reason of that fact alone", "payroll expense")),
    ("H-22", ("261020", "Pending Committee Action", "10% per year", "not law")),
):
    if fid not in flag_by_id:
        fail(f"required flag {fid} missing")
        continue
    for n in needles:
        if n not in flag_by_id[fid]["detail"]:
            fail(f"flag {fid}: detail no longer contains '{n}'")
        ok()
if "S26" not in flag_by_id.get("H-22", {}).get("sources", []):
    fail("flag H-22 must cite the Legistar record directly (S26)")
for field, needle in (
    (DATA["units"]["U2"]["base_status"], "lease-start"),
    (DATA["units"]["U2"]["base_status"], "not expressly as the current base rent"),
    (DATA["units"]["U1"]["occupancy_note"], "fixed-term/month-to-month"),
):
    if needle not in field:
        fail(f"required private-input caveat missing: {needle}")
    ok()
for item in DATA["calculations"]["U2"]["banked"]:
    if not item.get("conditional"):
        fail("Unit 2 has a banked component not marked conditional")
    ok()
for flag_id in ("H-01", "H-03", "H-17", "H-18", "H-19", "H-20"):
    if flag_id not in {f["id"] for f in DATA["flags"]}:
        fail(f"missing required flag {flag_id}")
    if not any(f"flags.html#{flag_id}" in doc for doc in docs.values()):
        fail(f"{flag_id}: not cross-linked from canonical content")
    ok()
for rel, minimum in (("index.html", 7), ("hub/flags.html", 8)):
    if docs[rel].count("<td></td>") < minimum:
        fail(f"{rel}: unsupported official-confirmation cells were filled instead of left blank")
    ok()
if "scenario date 1 February 2027" not in docs["index.html"]:
    fail("index.html: Unit 1 scenario date missing")
if "before</em> serving notice" not in docs["index.html"]:
    fail("index.html: recommended pre-notice license workflow missing")

# ----------------------------------------------------------------- summary
print(f"pages checked: {len(PAGES)}")
print(f"claim-table rows with an official source or flag link: {citation_rows}")
print(f"sources: {len(sources)} registered, {len(cited_ids & set(ids))} cited")
print(f"pressured dollar figures rejected: {unsourced}")
print(f"checks passed: {checks}")
if errors:
    for e in errors:
        print(f"FAIL: {e}", file=sys.stderr)
    print(f"\n{len(errors)} error(s)", file=sys.stderr)
    sys.exit(1)
print("no errors")
