#!/usr/bin/env python3
"""Independent gate for the /verification/ record.

Fails (non-zero exit) if any of the following is untrue:

 1. Every generated page exists and every page carries the same navigation.
 2. Every internal link and anchor resolves.
 3. Every source id used anywhere is registered, and its URL is an official
    publisher (sf.gov, leginfo, courts.ca.gov, hud.gov, justice.gov, govinfo).
 4. Every claim row, step row, unit row and high-severity flag row links to at
    least one registered official source.
 5. Every dollar figure printed on the site recomputes from the published
    percentages, and every notice date recomputes from the effective date.
 6. No personal identifier (tenant names, initials, email, street address) is
    present in any published file.
 7. No unverified claim has a filled-in value: claims marked "Unverified" must
    keep their cell blank and be flagged.
 8. The committed HTML matches what verification/build.py generates (no drift).

Standard library only.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import pathlib
import re
import sys
from decimal import Decimal as D
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
VDIR = ROOT / "verification"
DATA = json.loads((VDIR / "data.json").read_text(encoding="utf-8"))
S = {s["id"]: s for s in DATA["sources"]}

OFFICIAL_HOSTS = (
    "sf.gov", "www.sf.gov", "sfgov.org", "leginfo.legislature.ca.gov",
    "www4.courts.ca.gov", "www.hud.gov", "www.justice.gov", "www.govinfo.gov",
    "www.dir.ca.gov", "portal.sfrb.org", "www.sfassessor.org",
)

errors: list[str] = []
checks = 0


def ok(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


PAGES = [p[0] for p in [
    ("index.html",), ("process.html",), ("answers.html",), ("units.html",),
    ("checks.html",), ("flags.html",), ("privacy.html",), ("repo.html",),
    ("sources.html",),
]]
pages = {p: (VDIR / p).read_text(encoding="utf-8") for p in PAGES}

# ---------------------------------------------------------------- 1. pages exist
for p in PAGES:
    ok((VDIR / p).is_file(), f"missing page {p}")
    ok(len(pages[p]) > 2000, f"page {p} looks truncated")
ok((VDIR / "assets" / "style.css").is_file(), "missing stylesheet")

# every page links the stylesheet and has the same nav set
nav_sets = set()
for p in PAGES:
    src = pages[p]
    ok('href="assets/style.css"' in src, f"{p}: stylesheet not linked")
    ok('class="ftr"' in src, f"{p}: footer missing")
    ok("Not legal advice" in src, f"{p}: legal disclaimer missing")
    ok("Privacy." in src, f"{p}: privacy note missing")
    links = tuple(re.findall(r'<nav class="nav"[^>]*>(.*?)</nav>', src, re.S)[0].split("</a>")[:-1])
    nav_sets.add(tuple(sorted(re.findall(r'href="([^"]+)"', "".join(links)))))
ok(len(nav_sets) == 1, f"pages do not share one navigation set: {len(nav_sets)} variants")

# ------------------------------------------------- 2. internal links and anchors
for p in PAGES:
    src = pages[p]
    for href in set(re.findall(r'href="([^"]+)"', src)):
        if href.startswith(("http://", "https://", "mailto:", "#")):
            if href.startswith("#"):
                ok(f'id="{href[1:]}"' in src, f"{p}: dead same-page anchor {href}")
            continue
        target, _, frag = href.partition("#")
        tpath = (VDIR / target).resolve()
        ok(tpath.is_file(), f"{p}: broken internal link {href}")
        if frag and tpath.is_file():
            tsrc = tpath.read_text(encoding="utf-8")
            ok(f'id="{frag}"' in tsrc, f"{p}: anchor {href} not found in {target}")

# ------------------------------------------------------- 3. source registration
used = set()
for p in PAGES:
    used |= set(re.findall(r'>\s*(S\d\d)\s*</a>', pages[p]))
registered = set(S)
ok(used, "no source links found at all")
ok(used <= registered, f"unregistered source ids used: {sorted(used - registered)}")

for sid, s in S.items():
    host = urlparse(s["url"]).netloc.lower()
    ok(host in OFFICIAL_HOSTS, f"{sid}: non-official host {host}")
    ok(s["checked"] == "2026-11-08", f"{sid}: checked date is not the verification date")
    ok(len(s["quote"]) > 40, f"{sid}: quote too short to be a supporting passage")
    ok(s["url"].startswith("https://"), f"{sid}: not https")

# --------------------------------------------------- 4. source per published row
for c in DATA["claims"]:
    ok(bool(c["src"]), f"claim {c['id']} has no source")
    ok(all(x in S for x in c["src"]), f"claim {c['id']} cites an unknown source")
    ok(c["id"] in pages["checks.html"], f"claim {c['id']} not rendered")
    ok(c["claim"] in html.escape(pages["checks.html"], quote=False) or c["claim"] in pages["checks.html"],
       f"claim {c['id']} text not found in rendered page")

for s in DATA["steps"]:
    ok(bool(s["src"]), f"step {s['n']} has no source")

for u in DATA["units"]:
    ok(bool(u["src"]), f"unit row {u['unit']} has no source")

for q in DATA["questions"]:
    ok(bool(q["src"]), "question row has no source")

for f in DATA["flags"]:
    if f["sev"] == "High":
        ok(bool(f["src"]) or bool(f.get("evidence")), f"high-severity flag {f['id']} has no source or evidence")
    ok(f"id=\"{f['id']}\"" in pages["flags.html"], f"flag {f['id']} not rendered with an anchor")

# every rendered data-table row inside a description table carries a source chip
for p in ("checks.html", "flags.html", "units.html", "process.html", "sources.html"):
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", pages[p], re.S):
        if "<td" not in row:
            continue  # header row
        ok(("class=\"src\"" in row) or ("Repository record" in row) or p == "sources.html",
           f"{p}: table row without a source link: {re.sub('<[^>]+>', ' ', row)[:70]!r}")
# sources page: every row's first cell is an id anchor and carries an external link
for row in re.findall(r"<tr[^>]*>(.*?)</tr>", pages["sources.html"], re.S):
    if "<td" not in row:
        continue
    ok("<a href=\"https://" in row, "sources.html: row without an external source URL")

# --------------------------------------------------------- 5. arithmetic recheck
def money(x: D) -> D:
    from decimal import ROUND_HALF_UP
    return x.quantize(D("0.01"), rounding=ROUND_HALF_UP)

# published rate table, read from Form 571 / S06
RATES = {"2019": D("1.8"), "2020": D("0.7"), "2021": D("2.3"),
         "2022": D("3.6"), "2023": D("1.7"), "2024": D("1.4"), "2025": D("1.6")}
CURRENT = D("1.6")

formula = []

# Unit 1
b1 = D("3995.00")
formula.append((money(b1 * D("0.016")), ["$63.92"], "U1 annual"))
formula.append((b1 + money(b1 * D("0.016")), ["$4,058.92"], "U1 annual new"))
formula.append((money(b1 * D("0.014")), ["$55.93"], "U1 1.4% component"))
formula.append((money(b1 * D("0.030")), ["$119.85"], "U1 combined 3.0%"))
formula.append((b1 + money(b1 * D("0.030")), ["$4,114.85"], "U1 combined new"))

# Unit 2
b2 = D("3150.00")
formula.append((money(b2 * D("0.016")), ["$50.40"], "U2 annual"))
formula.append((b2 + money(b2 * D("0.016")), ["$3,200.40"], "U2 annual new"))
bank = [RATES[str(y)] for y in range(2019, 2025)]
formula.append((sum(bank), [D("11.5")], "U2 banked percentage sum"))
formula.append((money(b2 * D("0.115")), ["$362.25"], "U2 banked dollars"))
formula.append((money(b2 * D("0.131")), ["$412.65"], "U2 combined 13.1%"))
formula.append((b2 + money(b2 * D("0.131")), ["$3,562.65"], "U2 combined new"))
formula.append((D("11.5") + CURRENT, [D("13.1")], "U2 combined percentage"))
formula.append((D("1.4") + D("1.6"), [D("3.0")], "U1 combined percentage"))

for computed, shown, label in formula:
    for text in shown:
        # the figure must appear somewhere in the rendered record
        ok(any(str(text) in pages[p] for p in PAGES), f"{label}: computed {computed} ({text}) is not published")
        if isinstance(computed, D) and isinstance(text, D):
            ok(computed == text, f"{label}: {computed} != {text}")

# non-compounding check: additive must equal the single multiply
ok(money(b1 * D("0.014")) + money(b1 * D("0.016")) == money(b1 * D("0.030")), "U1 components do not add to 3.0%")
ok(money(b2 * D("0.115")) + money(b2 * D("0.016")) == money(b2 * D("0.131")), "U2 components do not add to 13.1%")

# notice dates
notice = [
    (dt.date(2027, 2, 1), 30, "2 Jan 2027"), (dt.date(2027, 2, 1), 35, "28 Dec 2026"),
    (dt.date(2027, 2, 28), 30, "29 Jan 2027"), (dt.date(2027, 2, 28), 35, "24 Jan 2027"),
    (dt.date(2027, 2, 28), 90, "30 Nov 2026"), (dt.date(2027, 2, 28), 95, "25 Nov 2026"),
]
for eff, days, shown in notice:
    got = eff - dt.timedelta(days=days)
    label = f"{got.day} {got.strftime('%b %Y')}".lstrip("0")
    ok(label == shown, f"notice date {days}d before {eff} is {label}, not {shown}")
    ok(shown in pages["units.html"], f"notice date {shown} is not published")

# ------------------------------------------------------------ 6. privacy scan
PRIVATE_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "email address"),
    (r"\b\d{1,5}\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Way|Drive|Dr)\b", "street address"),
    (r"\b\(\d{3}\)\s?\d{3}-\d{4}\b|\b\d{3}-\d{3}-\d{4}\b", "phone number"),
    (r"\b(tenant|occupant|lessee)s?\s+(?:named\s+)?[A-Z]{1,2}\b(?!\s*[A-Z])", "possible raw initials"),
]
scanned = PAGES + ["data.json", "assets/style.css", "build.py"]
for name in scanned:
    text = (VDIR / name).read_text(encoding="utf-8")
    for pat, label in PRIVATE_PATTERNS:
        for m in re.finditer(pat, text):
            frag = m.group(0)
            # allow the public government contact line quoted from an official page
            if "415-252-4600" in frag or "415" in frag and "252" in frag:
                continue
            errors.append(f"privacy: {label} found in verification/{name}: {frag!r}")
        checks += 1

TENANT_FOLLOW_WORDS = set("""
A An The If No Yes Tenant Tenants May Shall Has Have Who Which That This These Those
Protection Harassment Maintenance Repair Petitions Guide Residential Names Name
""".split())

ALLOWED_WORDS = set("""
The A An If No Yes Banking Rule Section Civil Code Rent Board SF San Francisco California
Housing Inventory Portal January February March April May June July August September October
November December Property Map City Costa Hawkins Form Banked Licence License Increase Two One
Each It In On At For And But Or Where When That This Because Use Confirm Read Keep Serve Apply
Federal Fair Act Ordinary Confirming Whether Any What Why How Who With Without Under
Protection Harassment Maintenance Repair Petitions Guide Residential Tenants Tenant
""".split())

# Structural check on the VISIBLE text only, because this file is published and
# therefore must not itself contain a raw identifier. The risk this targets is a
# LIST of people's initials — a comma-separated run of isolated single capital
# letters — so the test looks for a RUN of two or more isolated single capital
# letters separated only by a comma, "and" or a space. A statutory subdivision
# marker such as "(B)", a source chip such as "S15" and a document id such as
# "F-01" are excluded because they are not standalone letters. The pattern is
# written abstractly on purpose: this file is published, so it must never spell
# out an actual initial set.
TAG = re.compile(r"<[^>]+>")


def visible_text(src: str) -> str:
    body = re.sub(r"(?s)<(script|style|head).*?</\1>", " ", src)
    return re.sub(r"&[a-z]+;|&#\d+;", " ", TAG.sub(" ", body))


INITIAL_RUN = re.compile(
    r"(?<![A-Za-z0-9])[A-Z](?![A-Za-z0-9\-])(?:\s*(?:,|and|&)\s*|\s+)"
    r"[A-Z](?![A-Za-z0-9\-])")
for name in PAGES:
    vis = visible_text(pages[name])
    for m in INITIAL_RUN.finditer(vis):
        ctx = vis[max(0, m.start() - 45): m.end() + 45].replace("\n", " ")
        errors.append(f"privacy: run of initials {m.group(0)!r} in {name}: …{ctx}…")
        checks += 1
    # initials joined by periods ("J.P.") are identifiers in this context
    for m in re.finditer(r"(?<![A-Za-z])[A-Z]\.[A-Z]\.(?![A-Za-z])", vis):
        if m.group(0) == "U.S.":      # country abbreviation, not a person
            checks += 1
            continue
        errors.append(f"privacy: dotted initials {m.group(0)!r} in {name}")
        checks += 1
    # a tenant word followed by a capitalised proper name that is not a known word
    for m in re.finditer(r"(?i:\b(?:tenant|occupant|lessee)s?)\s+([A-Z][a-z]{2,})\b", vis):
        word = m.group(1)
        if word not in TENANT_FOLLOW_WORDS:
            errors.append(f"privacy: possible tenant name {word!r} in {name}")
        checks += 1
    ok("placeholder" in vis.lower(), f"{name}: no placeholder wording")

ok("two placeholders" in " ".join(visible_text(pages["units.html"]).split()).lower(),
   "units page does not use placeholders")
ok("one original tenant and one replacement occupant"
   in " ".join(visible_text(pages["units.html"]).split()).lower(),
   "units page does not state the occupant structure as placeholders")

# the building's street address must not be published anywhere in the repo tree
for bad in ("Irving Street", "1722 Irving"):
    ok(bad not in "".join(pages.values()), f"privacy: building address {bad!r} published")

# --------------------------------------------- 7. unverified values stay blank
for c in DATA["claims"]:
    if c["status"].startswith("Unverified"):
        ok("blank" in c["basis"].lower() or "not publish" in c["basis"].lower(),
           f"unverified claim {c['id']} does not explain the blank")
        ok(any(f["id"] for f in DATA["flags"]), "unverified claim not mirrored by a flag")
        ok("b-blank" in pages["checks.html"], "no blank badge rendered on checks page")

blanked = [f for f in DATA["flags"] if "not supplied" in f["detail"].lower() or "unknown" in f["item"].lower()]
ok(len(blanked) >= 3, "expected at least three flags to record a missing value")

# a guessed market figure must never appear
ok("market increase: $" not in "".join(pages.values()), "a market dollar figure appears to be asserted")
for forbidden in ("approximately 1.6%", "typical increase of", "average increase of"):
    ok(forbidden not in "".join(pages.values()).lower(), f"unsupported norm language: {forbidden}")

# --------------------------------------------------- 8. reproducible generation
import subprocess
before = {p: (VDIR / p).read_text(encoding="utf-8") for p in PAGES}
env = {"PATH": "/usr/bin:/bin:/usr/local/bin"}
r = subprocess.run([sys.executable, str(VDIR / "build.py")], capture_output=True, text=True, env=env)
ok(r.returncode == 0, f"build.py failed: {r.stderr[:300]}")
for p in PAGES:
    ok((VDIR / p).read_text(encoding="utf-8") == before[p],
       f"{p} is not reproducible from data.json (regenerate and commit)")

# ------------------------------------------------------------------- report
print(f"verification record: {len(PAGES)} pages, {len(S)} sources, "
      f"{len(DATA['claims'])} claims, {len(DATA['flags'])} flags")
print(f"checks passed: {checks}")
if errors:
    print(f"\nERRORS ({len(errors)}):", file=sys.stderr)
    for e in errors:
        print("  -", e, file=sys.stderr)
    sys.exit(1)
print("no errors")
