#!/usr/bin/env python3
"""Generate the consolidated dashboard in site2/ from data/final/.

Deterministic: same input -> byte-identical output. No network access, no
templating library, no external assets. Every table row that states a fact
carries a source link to an official page; rows whose value cannot be
confirmed from an official source are rendered blank and marked UNVERIFIED.

Run:  python3 build2/build.py
"""

from __future__ import annotations

import html
import json
import re
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "final"
OUT = ROOT / "site2"

# ---------------------------------------------------------------- data loading

SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
SRCRAW = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
SOURCES = {s["id"]: s for s in SRCRAW["sources"]}
RETRIEVED = SRCRAW["retrieved"]

NAV = [
    ("index.html", "Overview"),
    ("process.html", "Rent Board process"),
    ("units.html", "The two units"),
    ("limits.html", "Rate limits 2019-2027"),
    ("requirements.html", "Requirements"),
    ("questions.html", "Your five questions"),
    ("notice.html", "Notices & deadlines"),
    ("review.html", "Tenant-lawyer review"),
    ("practice.html", "How owners do it"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for review"),
]


def e(text: object) -> str:
    return html.escape(str(text), quote=True)


# ---------------------------------------------------------------- source links

def src_links(ids, *, allow_none: bool = False) -> str:
    """Render a row's source cell. Each id becomes a link to the official page."""
    out = []
    for sid in ids:
        if sid == "owner-record":
            out.append('<span class="src-private" title="Private owner record — internal only, not published">'
                       'owner record <em>(internal)</em></span>')
            continue
        if sid.startswith("--"):
            continue
        s = SOURCES.get(sid)
        if s is None:
            raise SystemExit(f"unknown source id {sid!r}")
        out.append(f'<a class="src" href="{e(s["url"])}">{e(sid)}</a>')
    if not out:
        if not allow_none:
            raise SystemExit("row has no source")
        return '<span class="unverified">UNVERIFIED — no official source</span>'
    return " ".join(out)


def blank_cell() -> str:
    return '<span class="blank" aria-label="left blank: not confirmed by an official source">&mdash; blank &mdash;</span>'


def status_pill(status: str) -> str:
    key = status.lower()
    label = {
        "verified": "Verified",
        "verified-by-rule": "Verified by rule",
        "private-input": "Owner record (internal)",
        "conflicting": "Conflicting sources",
        "unverified": "Unverified",
        "calculated": "Calculated",
    }.get(key, status)
    return f'<span class="pill pill-{e(key)}">{e(label)}</span>'


# ---------------------------------------------------------------- page shell

def page(slug: str, title: str, body: str, lede: str = "") -> str:
    nav_items = []
    for h, t in NAV:
        active = ' class="active" aria-current="page"' if h == slug else ""
        nav_items.append(f'      <a href="{h}"{active}>{e(t)}</a>')
    nav = "\n".join(nav_items)
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} &middot; Rent Increase Review 94122</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <div class="wrap">
    <a class="brand" href="index.html">Rent Increase Review<span class="brand-sub">Outer Sunset &middot; SF 94122</span></a>
    <nav class="nav" aria-label="Sections">
{nav}
    </nav>
  </div>
</header>
<main id="main" class="wrap">
  <h1>{e(title)}</h1>
  {lede_html}
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <p><strong>Not legal advice.</strong> {e(SITE["meta"]["disclaimer"])}</p>
    <p>Every value on this site is taken from an official source fetched on {e(RETRIEVED)} and linked in
    place. Where no official source confirms a value, the cell is left blank and listed on the
    <a href="flagged.html">Flagged for review</a> page. No tenant name, initial, address, telephone
    number or email appears anywhere on this site.</p>
    <p class="tiny">Generated from <code>data/final/</code> by <code>build2/build.py</code>. Do not edit the HTML by hand.</p>
  </div>
</footer>
</body>
</html>
"""


def table(headers, rows, cls: str = "grid") -> str:
    head = "".join(f"<th scope=\"col\">{h}</th>" for h in headers)
    body = "\n".join(rows)
    return (f'<div class="tablewrap">\n<table class="{cls}">\n<thead><tr>{head}</tr></thead>\n'
            f"<tbody>\n{body}\n</tbody>\n</table>\n</div>")


# ---------------------------------------------------------------- calculations

def _layer_counts() -> str:
    from collections import Counter
    c = Counter(r["layer"].split(" ")[0].rstrip(",") for r in SITE["requirements"])
    parts = [f"{n} {name.lower()}" for name, n in c.most_common()]
    return ", ".join(parts[:-1]) + " and " + parts[-1]


def _status_count(status: str) -> int:
    return sum(1 for r in SITE["requirements"] if r["status"] == status)


def _high_count() -> int:
    return sum(1 for f in SITE["flags"] if f["severity"] == "HIGH")


def money(d: Decimal) -> str:
    return f"${d:,.2f}"


def compute(base: Decimal, pct) -> tuple[str, str]:
    p = Decimal(str(pct)) / Decimal(100)
    inc = (base * p).quantize(Decimal("0.01"))
    return money(inc), money(base + inc)


# ---------------------------------------------------------------- pages

def build_index() -> str:
    h = SITE["headline"]
    rows = []
    for r in h["answer_rows"]:
        rows.append(
            "<tr>"
            f'<td>{status_pill(r["status"])}</td>'
            f'<td><strong>{e(r["point"])}</strong><br><span class="muted">{e(r["detail"])}</span></td>'
            f'<td class="srccell">{src_links(r["sources"])}</td>'
            "</tr>"
        )

    # headline numbers table
    num_rows = []
    for c in SITE["calculations"]:
        base = Decimal(str(c["base"]))
        inc, new = compute(base, c["pct"])
        num_rows.append(
            "<tr>"
            f'<td>{e(c["unit"])}</td>'
            f'<td>{e(c["scenario"])}</td>'
            f'<td class="num">{money(base)}</td>'
            f'<td class="num">{e(c["pct"])}%</td>'
            f'<td class="num"><strong>{inc}</strong></td>'
            f'<td class="num"><strong>{new}</strong></td>'
            f'<td>{status_pill(c["status"])}</td>'
            f'<td class="srccell">{src_links(c["sources"])}</td>'
            "</tr>"
        )

    q5 = next(q for q in SITE["questions"] if q["id"] == "Q5")

    body = f"""
<section class="callout answer">
  <h2>The question you led with</h2>
  <p class="big">{e(h["question"])}</p>
  <p class="short">{e(h["short_answer"])}</p>
  <p>You do not file anything with the Rent Board to raise rent on an annual or banked schedule, and
  you do not need the Board's approval. What you do need is the <strong>rent-increase licence</strong>,
  and it is not an application: it is generated automatically once you report the unit in the annual
  <a href="https://www.sf.gov/rent-board-housing-inventory">Housing Inventory</a>. Owning as an
  individual rather than a corporation changes nothing — the obligation attaches to the unit, not to
  the size of the owner. If the licence is not in place on the <em>effective date</em> of the increase,
  the entire increase is void.</p>
  <p class="jump">Read the <a href="process.html">step-by-step process</a> &middot;
  the <a href="units.html">numbers for both units</a> &middot;
  the <a href="flagged.html">{len(SITE["flags"])} items flagged for your review</a></p>
</section>

<h2>Seven points that answer it</h2>
{table(["Status", "Point", "Official source"], rows)}

<h2>The numbers, with every source</h2>
<p>Percentages come from the Rent Board's rate sheet, form 571. Each dollar figure is recomputed from
the published percentage and the base rent you supplied, on base rent only, added and never
compounded, and not rounded up.</p>
{table(["Unit", "Scenario", "Base rent", "Increase", "Dollars / month", "New rent", "Status", "Source"],
       num_rows)}

<div class="callout warn">
  <h3>One conflict you must resolve before serving notice</h3>
  <p>The Rent Board's binding <strong>Rule 4.12</strong> requires a skipped annual increase to be banked
  after <strong>12 months</strong>. Its public summary page says <strong>24 months</strong>. The Board's
  own worked examples apply 12. That single difference decides whether Unit 2 is 13.1%
  ($412.65) or 11.7% ($368.55), and whether Unit 1 is 3.0% ($119.85) or 1.6% ($63.92). Both ranges are
  published here rather than picking one silently. See
  <a href="flagged.html">F01</a>.</p>
</div>

<h2>Your five questions, in one line each</h2>
<ul class="qlist">
  <li><a href="questions.html#Q1">What is reasonable and normal under local, state and federal law?</a>
      &mdash; 1.6% plus properly banked years; the state cap is displaced; federal law sets no ceiling.</li>
  <li><a href="questions.html#Q2">How do corporations and individuals handle increases?</a>
      &mdash; identically in law; no official source measures actual behaviour, so those rows are blank.</li>
  <li><a href="questions.html#Q3">How should tenants be told, and what reasons are lawful?</a>
      &mdash; written notice with four specific elements on the right timeline; documentary reasons only.</li>
  <li><a href="questions.html#Q4">Would a tenant lawyer approve it?</a>
      &mdash; it can pass 14 tests; nine conditions must hold at once; four cannot be assessed from the record.</li>
  <li><a href="questions.html#Q5">One unit or both?</a>
      &mdash; {e(q5["answer"].split(".")[0])}. See the <a href="questions.html#Q5">full answer</a>.</li>
</ul>

<h2>What is on this site</h2>
<div class="cards">
  <a class="card" href="process.html"><h3>Rent Board process</h3><p>Eight steps from checking coverage to
  keeping the file, with what to file, when, and the two deadlines that matter.</p></a>
  <a class="card" href="units.html"><h3>The two units</h3><p>Anonymised records, the year-by-year bank
  that produces 11.5%, and every figure recomputed.</p></a>
  <a class="card" href="limits.html"><h3>Rate limits</h3><p>The published annual percentages, 2019 to
  2027, marked by which year each tenancy uses.</p></a>
  <a class="card" href="requirements.html"><h3>Requirements</h3><p>23 togglable requirements across
  local, state and federal law, each with a source.</p></a>
  <a class="card" href="questions.html"><h3>Your five questions</h3><p>The full answers, including what
  is deliberately left blank.</p></a>
  <a class="card" href="notice.html"><h3>Notices &amp; deadlines</h3><p>The eight things a valid notice
  needs, and the exact last service dates.</p></a>
  <a class="card" href="review.html"><h3>Tenant-lawyer review</h3><p>The 14 tests a tenant-side reviewer
  would run, with the pass condition for each.</p></a>
  <a class="card" href="practice.html"><h3>How owners do it</h3><p>Corporate versus individual owners,
  and why the honest answer to "what do they typically do" is blank.</p></a>
  <a class="card" href="sources.html"><h3>Sources</h3><p>All {len(SOURCES)} sources, with the quote each
  one supports.</p></a>
  <a class="card card-flag" href="flagged.html"><h3>Flagged for review</h3><p>{len(SITE["flags"])} irregularities,
  including {_high_count()} that can void or materially change an otherwise correct increase.</p></a>
</div>

<section class="callout privacy">
  <h2>Privacy</h2>
  <p>{e(SITE["privacy"]["statement"])}</p>
  <p>One thing is <em>not</em> fixed: the original initials are still present in four files outside this
  session's scope (<code>site/</code> and <code>research/</code>), and <code>site/</code> is served by
  GitHub Pages. They were removed from the published <code>docs/v1</code> copy. See
  <a href="flagged.html">F10</a>.</p>
</section>
"""
    return page("index.html", SITE["meta"]["title"], body,
                "What a lawful, and defensible, rent increase looks like for two rent-controlled flats "
                "in a 1940 building in the Outer Sunset. Every figure below is traced to an official "
                f"source fetched on {RETRIEVED}.")


def build_process() -> str:
    rows = []
    for s in SITE["steps"]:
        rows.append(
            "<tr>"
            f'<td class="stepnum">{s["n"]}</td>'
            f'<td><strong>{e(s["action"])}</strong><br><span class="muted">{e(s["detail"])}</span>'
            f'<br><span class="timing">Timing: {e(s["timing"])}</span></td>'
            f'<td class="srccell">{src_links(s["sources"])}</td>'
            "</tr>"
        )

    body = f"""
<div class="callout answer">
  <h2>In one paragraph</h2>
  <p>Confirm the units are covered. Report both units into the Rent Board Housing Inventory, which
  generates the rent-increase licence automatically — this is the step you read about, and it is
  compulsory even for a single individual owner. Fix each tenancy's anniversary date. Add the current
  annual percentage to any properly banked years, on base rent only, without compounding or rounding
  up. Pick the notice period from the size of the total. Serve a written notice that states four
  specific things. Keep the evidence. You never file the notice with the Rent Board and you never ask
  it to approve an annual or banked increase.</p>
</div>

<h2>Step by step</h2>
{table(["#", "What to do", "Official source"], rows)}

<div class="callout warn">
  <h3>Where this most often goes wrong</h3>
  <ol>
    <li><strong>The licence.</strong> Not a filing for approval — but if it is missing on the effective
    date, Rule 13.14 voids the whole increase. It is also the one item on this page that cannot be
    checked from your lease paperwork.</li>
    <li><strong>The 10% threshold.</strong> Banked years push Unit 2 over 10%, which turns a 30-day
    notice into a 90-day notice. A 30-day notice on a 13.1% increase is defective.</li>
    <li><strong>Using the wrong percentage.</strong> Use the rate in effect on the <em>effective date</em>,
    not the date you hand over the notice.</li>
    <li><strong>Giving a reason that is not lawful.</strong> Market rent, the length of the tenancy and
    the April 2026 occupant change in Unit 1 are all expressly unavailable as grounds.</li>
  </ol>
</div>

<h2>What you do not have to do</h2>
{table(
  ["Not required", "Why", "Official source"],
  [
    "<tr><td>Apply to the Rent Board for permission to raise rent by the annual amount</td>"
    "<td>Annual and banked increases need no petition and no approval; only six listed increase types do</td>"
    f'<td class="srccell">{src_links(["S12", "S13"])}</td></tr>',
    "<tr><td>Send the notice to the Rent Board</td>"
    "<td>The notice duty runs to the tenant; the licence itself need not even be attached</td>"
    f'<td class="srccell">{src_links(["S01", "S09"])}</td></tr>',
    "<tr><td>Hire a lawyer or a property manager because you are an individual owner</td>"
    "<td>Nothing in §37.15 or Rule 13.14 distinguishes an individual from a corporation</td>"
    f'<td class="srccell">{src_links(["S08", "S07"])}</td></tr>',
    "<tr><td>Use the state's AB 1482 percentage</td>"
    "<td>The state cap is displaced where a stricter local cap applies, which it does here</td>"
    f'<td class="srccell">{src_links(["S24"])}</td></tr>',
  ])}
"""
    return page("process.html", "Do you have to involve the Rent Board?", body,
                "The short answer is yes to the licence and no to an application. Here is the whole "
                "sequence, in the order it has to happen.")


def build_units() -> str:
    parts = []
    for u in SITE["units"]:
        rows = []
        for r in u["rows"]:
            val = e(r["value"]) if r["value"] else blank_cell()
            rows.append(
                "<tr>"
                f'<td>{e(r["item"])}</td>'
                f'<td>{val}</td>'
                f'<td>{status_pill(r["status"])}</td>'
                f'<td class="srccell">{src_links(r["sources"], allow_none=r["status"] == "unverified")}</td>'
                "</tr>"
            )
        parts.append(f"""
<h2 id="{e(u["id"])}">{e(u["label"])}</h2>
<p class="muted">Tenants are referred to only as {e(u["placeholders"])}. Lease date and rent are
unchanged because the lawful ceiling depends on them.</p>
{table(["Item", "Value", "Status", "Source"], rows)}
""")

    calc_rows = []
    for c in SITE["calculations"]:
        base = Decimal(str(c["base"]))
        inc, new = compute(base, c["pct"])
        calc_rows.append(
            "<tr>"
            f'<td>{e(c["id"])}</td>'
            f'<td>{e(c["unit"])}</td>'
            f'<td>{e(c["scenario"])}<br><span class="muted">{e(c["note"])}</span></td>'
            f'<td class="num">{money(base)}</td>'
            f'<td class="num">{e(c["pct"])}%</td>'
            f'<td class="num"><strong>{inc}</strong></td>'
            f'<td class="num"><strong>{new}</strong></td>'
            f'<td>{status_pill(c["status"])}</td>'
            f'<td class="srccell">{src_links(c["sources"])}</td>'
            "</tr>"
        )

    # the bank detail for unit 2
    bank = [
        ("1 June 2020", "1.8%", "3/1/2020 – 2/28/2021"),
        ("1 June 2021", "0.7%", "3/1/2021 – 2/28/2022"),
        ("1 June 2022", "2.3%", "3/1/2022 – 2/28/2023"),
        ("1 June 2023", "3.6%", "3/1/2023 – 2/29/2024"),
        ("1 June 2024", "1.7%", "3/1/2024 – 2/28/2025"),
        ("1 June 2025", "1.4%", "3/1/2025 – 2/28/2026"),
    ]
    bank_rows = [
        f"<tr><td>{a}</td><td class=\"num\">{b}</td><td>{c}</td>"
        f'<td class="srccell">{src_links(["S03"])}</td></tr>'
        for a, b, c in bank
    ]
    bank_rows.append(
        '<tr class="total"><td>Sum of the six skipped years</td><td class="num"><strong>11.5%</strong></td>'
        f'<td>Added, not compounded</td><td class="srccell">{src_links(["S05", "S12"])}</td></tr>')
    bank_rows.append(
        '<tr class="total"><td>Plus the current annual increase</td><td class="num"><strong>1.6%</strong></td>'
        f'<td>3/1/2026 – 2/28/2027</td><td class="srccell">{src_links(["S03"])}</td></tr>')
    bank_rows.append(
        '<tr class="total grand"><td>Total</td><td class="num"><strong>13.1%</strong></td>'
        f'<td>1.6 + 1.8 + 0.7 + 2.3 + 3.6 + 1.7 + 1.4</td><td class="srccell">{src_links(["S05", "S03"])}</td></tr>')

    body = f"""
<div class="callout">
  <h2>How the two ceilings arise</h2>
  <p>The units are next door to each other, but the ceilings differ by a factor of four. That is not a
  property of the flats: it is a property of the tenancies. Unit 1's tenancy began in 2025 and has had
  at most one anniversary. Unit 2's tenancy began in 2019 and appears never to have been increased, so
  six annual allowances have accumulated. Banked percentages are added to the current year and applied
  once to the current base rent. They are never compounded, and the result is never rounded up.</p>
</div>
{"".join(parts)}

<h2>Every figure, recomputed</h2>
<p>Each row below is recomputed from the base rent and the published percentage. The arithmetic is
repeated by <code>tools/check2.py</code> on every build, which fails if any figure here stops matching.</p>
{table(["ID", "Unit", "Scenario", "Base rent", "Increase", "Dollars / month", "New rent", "Status", "Source"],
       calc_rows)}

<h2 id="bank">Where Unit 2's 11.5% comes from</h2>
<p>Six annual allowances fell due on 1 June in each of 2020 to 2025. On the owner's account, Unit 2 has
been at $3,150 throughout. Each unused allowance is banked at the percentage that was available in that
year — not at today's rate. That assumption is the single biggest open question on this site: there is
no rent ledger in the record, so it is flagged as <a href="flagged.html">F03</a>.</p>
{table(["Anniversary it fell due", "Percentage", "Rate period", "Source"], bank_rows)}

<div class="callout warn">
  <h3>The 12-month versus 24-month question</h3>
  <p>The 1.4% that fell due on 1 June 2025 is the contested one. Rule 4.12 requires only 12 months to
  have elapsed since it became available, and on 1 June 2026 a full year had passed — so under the Rule
  it is banked. The sf.gov summary page says a skipped increase is banked only after 24 full months,
  which would exclude it and bring the total to 11.7% ($368.55). Both are shown. The Rule is the binding
  text; the summary is the page the Rent Board publishes for owners. Confirming the answer with a
  counselor before service costs a phone call.</p>
</div>
"""
    return page("units.html", "The two units", body,
                "Anonymised tenancy records, the year-by-year accumulation, and every dollar figure "
                "recomputed from the published percentages.")


def build_limits() -> str:
    rows = []
    for r in SITE["rates"]:
        pct = f'{e(r["pct"])}%' if r["pct"] else blank_cell()
        used = e(r["used_by"]) if r["pct"] else ("Not published as of 2026-11-07 — left blank" if not r["pct"] else "")
        rows.append(
            "<tr>"
            f'<td>{e(r["period"])}</td>'
            f'<td class="num">{pct}</td>'
            f'<td>{used}</td>'
            f'<td class="srccell">{src_links(r["sources"])}</td>'
            "</tr>"
        )

    body = f"""
<div class="callout answer">
  <p class="big">1.6%</p>
  <p>is the annual allowable increase for rent-controlled units for increases effective
  <strong>1 March 2026 through 28 February 2027</strong>. It is set at 60% of the increase in the Bay
  Area Consumer Price Index and can never exceed 7% in a year.</p>
</div>

<h2>The rate table</h2>
<p>Only the years that matter to these two tenancies are shown, plus the one year that does not and the
next year that is not yet known. The full series runs back to 1 April 1982 on the Board's own sheet.</p>
{table(["Effective period", "Allowable", "How it is used here", "Official source"], rows)}

<h2>The rules that turn a percentage into a lawful increase</h2>
{table(
  ["Rule", "What it means", "Official source"],
  [
    "<tr><td>Once every 12 months</td><td>The first increase can be imposed 12 months after the lease "
    "began. After that, no more than one increase in any 12 months. An increase imposed late makes its "
    f'effective date the new anniversary.</td><td class="srccell">{src_links(["S01", "S11"])}</td></tr>',
    "<tr><td>Base rent only</td><td>Exclude temporary passthroughs and fluctuating charges. Parking and "
    "storage rent generally do count as base rent.</td>"
    f'<td class="srccell">{src_links(["S01", "S12"])}</td></tr>',
    "<tr><td>Add, never compound</td><td>Sum the percentages first, then apply the sum once to the "
    "current base rent. Applying each year to a progressively larger rent overstates the ceiling.</td>"
    f'<td class="srccell">{src_links(["S05", "S12"])}</td></tr>',
    "<tr><td>Never round up</td><td>Carry the cent-level result. Rounding $63.92 up to $64 is not "
    "permitted.</td>"
    f'<td class="srccell">{src_links(["S01", "S12"])}</td></tr>',
    "<tr><td>Percentage on the effective date</td><td>Use the rate in force when the increase takes "
    "effect, not the rate when the notice is served.</td>"
    f'<td class="srccell">{src_links(["S01", "S04"])}</td></tr>',
    "<tr><td>10% switches the notice period</td><td>10% or less: 30 days. More than 10%: 90 days. Add 5 "
    "days if served by mail.</td>"
    f'<td class="srccell">{src_links(["S01", "S23", "S28"])}</td></tr>',
  ])}

<div class="callout warn">
  <h3>Why the state's AB 1482 number is not the answer</h3>
  <p>The state cap (5% plus CPI, hard maximum 10%) is the figure most commonly quoted for California, but
  it does not apply to these units. Civil Code §1947.12(d)(3) excludes housing already subject to local
  rent control that restricts increases to less than the state cap. San Francisco's 1.6% is lower, so the
  local cap controls.</p>
  <p class="muted">Source: {src_links(["S24"])}</p>
</div>
"""
    return page("limits.html", "Rate limits, 2019 to 2027", body,
                "The published annual percentages, which year each tenancy uses, and the four rules that "
                "convert a percentage into a lawful increase.")


def build_requirements() -> str:
    rows = []
    for r in SITE["requirements"]:
        rows.append(
            "<tr>"
            f'<td>{e(r["id"])}</td>'
            f'<td><span class="layer">{e(r["layer"])}</span></td>'
            f'<td><strong>{e(r["requirement"])}</strong></td>'
            f'<td>{e(r["detail"])}</td>'
            f'<td>{e(r["applies"])}</td>'
            f'<td>{status_pill(r["status"])}</td>'
            f'<td class="srccell">{src_links(r["sources"])}</td>'
            "</tr>"
        )
    body = f"""
<p>Every requirement that bears on raising rent on these two units, across local, state and federal law.
Each row carries a link to the official page it comes from. The "Applies" column states what the source
actually requires of this building, not a general summary.</p>
<p class="muted">Filter: <input type="search" id="filter" placeholder="Filter requirements…"
aria-label="Filter requirements"> <span id="count" class="count"></span></p>
{table(["ID", "Layer", "Requirement", "Detail", "Applies here?", "Status", "Official source"], rows,
       cls="grid filterable")}
<div class="callout">
  <h3>Count</h3>
  <p>{len(SITE["requirements"])} requirements: {_layer_counts()}. Of these,
  {_status_count("verified")} are verified against a primary source and {_status_count("conflicting")} is marked
  conflicting because two official pages disagree (banking, <a href="flagged.html">F01</a>).</p>
</div>
"""
    return page("requirements.html", "Requirements across all three layers of law", body,
                "23 requirements, each traced to the official text, with what each one actually requires "
                "of this building.")


def build_questions() -> str:
    parts = []
    for q in SITE["questions"]:
        blank = ""
        if q["blank"]:
            blank = (f'<div class="callout blankbox"><h3>Deliberately left blank</h3>'
                     f'<p>{e(q["blank"])}</p></div>')
        numbers = ""
        if q["numbers"]:
            numbers = f'<p class="numbers">{e(q["numbers"])}</p>'
        parts.append(f"""
<h2 id="{e(q["id"])}">{e(q["id"])}. {e(q["question"])}</h2>
<p>{e(q["answer"])}</p>
{numbers}
{blank}
<p class="srcline">Sources: {src_links(q["sources"])}</p>
""")
    body = '<p class="lede">Every question you asked, answered only as far as the sources go. Where the sources stop, the answer stops.</p>' + "".join(parts)
    return page("questions.html", "Your five questions", body)


def build_notice() -> str:
    el_rows = [
        f'<tr><td>{e(x["element"])}</td><td>{status_pill(x["status"])}</td>'
        f'<td class="srccell">{src_links(x["sources"])}</td></tr>'
        for x in SITE["notice"]["elements"]
    ]
    dl_rows = []
    for d in SITE["notice"]["deadlines"]:
        dl_rows.append(
            "<tr>"
            f'<td>{e(d["label"])}</td>'
            f'<td>{e(d["notice"])}</td>'
            f'<td class="num">{e(d["serve_by_personal"])}</td>'
            f'<td class="num">{e(d["serve_by_mail"])}</td>'
            f'<td class="srccell">{src_links(d["sources"])}</td>'
            "</tr>"
        )
    body = f"""
<div class="callout urgent">
  <h2>Act first on Unit 2</h2>
  <p>{e(SITE["notice"]["urgent_note"])}</p>
</div>

<h2>Eight things a valid notice must contain or do</h2>
{table(["Requirement", "Status", "Official source"], el_rows)}

<h2>Last safe service dates</h2>
<p>Computed from the effective date, working backwards. Personal delivery and mail are shown separately
because CCP §1013 adds five calendar days when a notice is mailed within California.</p>
{table(["Increase", "Notice period", "Serve in person by", "Mail by", "Official source"], dl_rows)}

<div class="callout warn">
  <h3>Two wording traps</h3>
  <p><strong>Rule 4.10 versus Rule 4.12.</strong> Rule 4.10(b) says a non-conforming notice makes the
  whole increase void, but it carves out an increase that equals no more than the allowable annual and
  banked amounts. Rule 4.12(b) says omitting the banked breakdown "shall not render the increase null
  and void". A notice that states the correct total but omits the banked breakdown is therefore very
  likely enforceable — but it hands a tenant-side reviewer the first thing to argue about, for no gain.
  State the breakdown.</p>
  <p><strong>The percentage must match the effective date.</strong> A notice served in November 2026 for
  a February 2027 effective date uses the rate in force in February 2027 (1.6%), not whatever the Board
  announces next. If the increase is pushed past 28 February 2027 the whole calculation has to be redone.</p>
</div>

<h2>Reasonable versus unreasonable reasons</h2>
{table(
  ["Reason you might be tempted to give", "Verdict", "Official source"],
  [
    f'<tr><td>"The Rent Board allows 1.6% this year"</td><td><span class="pill pill-verified">Lawful</span> '
    f'— this is the whole lawful reason for an annual increase</td><td class="srccell">{src_links(["S01"])}</td></tr>',
    f'<tr><td>"We skipped prior years, so here is the accumulated amount"</td>'
    f'<td><span class="pill pill-verified">Lawful</span> — provided each year is added, not compounded, and '
    f'the notice says which part is banked</td><td class="srccell">{src_links(["S05", "S04"])}</td></tr>',
    f'<tr><td>"Operating costs went up, so we are filing for more than 1.6%"</td>'
    f'<td><span class="pill pill-calculated">Possible, by petition only</span> — operating-and-maintenance '
    f'petition, filed before the notice, capped at 7% in 12 months</td>'
    f'<td class="srccell">{src_links(["S13"])}</td></tr>',
    f'<tr><td>"The unit is below market"</td><td><span class="pill pill-conflicting">Not lawful</span> '
    f'— expressly not an extraordinary circumstance</td><td class="srccell">{src_links(["S14"])}</td></tr>',
    f'<tr><td>"They have been there since 2019"</td><td><span class="pill pill-conflicting">Not lawful</span> '
    f'— length of tenancy is not a ground</td><td class="srccell">{src_links(["S14"])}</td></tr>',
    f'<tr><td>"A fourth person moved into Unit 1"</td><td><span class="pill pill-conflicting">Unlawful</span> '
    f'— extra rent for a new occupant is expressly prohibited, even if the lease says otherwise</td>'
    f'<td class="srccell">{src_links(["S01"])}</td></tr>',
    f'<tr><td>"They complained about repairs, so we are raising the rent"</td>'
    f'<td><span class="pill pill-conflicting">Unlawful</span> — retaliation within 180 days</td>'
    f'<td class="srccell">{src_links(["S25"])}</td></tr>',
    f'<tr><td>"We would like them to move on"</td><td><span class="pill pill-conflicting">Unlawful</span> '
    f'— bad-faith pressure to vacate is harassment, and a rent substantially above market rates is '
    f'named as evidence of it</td><td class="srccell">{src_links(["S17"])}</td></tr>',
  ])}
"""
    return page("notice.html", "Notices and deadlines", body,
                "What a valid notice contains, the exact last service dates for each option, and which "
                "reasons are lawful.")


def build_review() -> str:
    rows = []
    for t in SITE["review_tests"]:
        rows.append(
            "<tr>"
            f'<td>{e(t["id"])}</td>'
            f'<td><strong>{e(t["test"])}</strong></td>'
            f'<td>{e(t["pass_condition"])}</td>'
            f'<td>{e(t["result"])}</td>'
            f'<td class="srccell">{src_links(t["sources"])}</td>'
            "</tr>"
        )
    body = f"""
<div class="callout answer">
  <h2>The honest version of "would a tenant lawyer approve it"</h2>
  <p>A tenant-side reviewer does not ask whether the increase was reasonable in a business sense. They
  ask a short list of mechanical questions, in roughly this order, because any single wrong answer is
  enough. Nine of the fourteen below can be answered "yes" from the facts you supplied. One is answered
  "yes, but only on one reading of a rule the Rent Board states two different ways". Four cannot be
  answered from the record at all, and each of those is a place where a challenge could succeed on
  paperwork rather than on principle.</p>
</div>

<h2>The fourteen tests</h2>
{table(["ID", "Test", "Pass condition", "Result on the facts supplied", "Official source"], rows)}

<h2>How a challenge would actually arrive</h2>
<p>Not through a lawsuit, and not usually through a lawyer. A tenant can file an unlawful-rent-increase
petition at the Rent Board, free, with no time limit, and have it heard by an Administrative Law Judge in
a process the Board runs on the express basis that no one needs an attorney. That is the forum where
every item above gets tested.</p>
<p class="srcline">Sources: {src_links(["S15", "S16"])}</p>

<div class="callout">
  <h3>On the free-legal-advice point</h3>
  <p>San Francisco's free legal representation for tenants — the Tenant Right to Counsel programme — is
  triggered by a notice to terminate tenancy or an eviction suit. The Board's own notice form states it
  must be attached to every notice to terminate tenancy. A rent-increase dispute is a different track: a
  free Rent Board petition. This matters practically, because it means the realistic risk is a
  staff-reviewed petition about arithmetic and paperwork, not an adversarial lawsuit.</p>
  <p class="srcline">Sources: {src_links(["S31", "S15"])}</p>
</div>

<div class="callout warn">
  <h3>The four unanswerable items, and how to close them</h3>
  <ol>
    <li>Licence status — check <code>portal.sfrb.org</code> for each unit (F04).</li>
    <li>Whether Unit 2 has been flat since 2019 — produce the rent ledger (F03).</li>
    <li>Whether Unit 1 was increased on 1 February 2026 — check the notice file (F07).</li>
    <li>Whether either rent is entirely base rent — check the leases (F05).</li>
  </ol>
  <p>Each is answerable from the owner's own records, without any research. Closing all four converts
  the review from "passes on the arithmetic" to "passes on everything".</p>
</div>
"""
    return page("review.html", "The tenant-lawyer review test", body,
                "The fourteen questions a tenant-side reviewer would run, the pass condition for each, "
                "and the four that cannot be answered from the record.")


def build_practice() -> str:
    rows = []
    for p in SITE["practice"]:
        ans = e(p["answer"]) if p["answer"] else blank_cell()
        rows.append(
            "<tr>"
            f'<td><strong>{e(p["question"])}</strong></td>'
            f'<td>{ans}</td>'
            f'<td>{status_pill(p["status"])}</td>'
            f'<td class="srccell">{src_links(p["sources"], allow_none=p["status"] == "unverified")}</td>'
            "</tr>"
        )
    body = f"""
<div class="callout answer">
  <h2>The part of your question the sources cannot answer</h2>
  <p>You asked how large real-estate corporations handle increases and how individual owners do. There is
  no official source that measures either. No government body publishes the average increase imposed by
  corporate versus individual owners in 94122, and the Rent Board does not survey owner behaviour. Those
  rows are left blank below rather than filled with an estimate. What the sources do establish is the
  part that matters for compliance: in law there is no difference between the two.</p>
</div>

<table class="grid">
<thead><tr><th scope="col">Question</th><th scope="col">What the official sources support</th>
<th scope="col">Status</th><th scope="col">Official source</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table>

<h2>Why the "big corporations get away with more" intuition is wrong here</h2>
<p>Three specific claims are worth testing against the text, because each is commonly believed and each
fails:</p>
{table(
  ["Common belief", "What the sources actually say", "Official source"],
  [
    "<tr><td>Institutional owners can use the state's AB 1482 cap instead of the city's</td>"
    "<td>The state cap is expressly excluded where a stricter local cap applies. It applies by the "
    "unit's regulatory status, not the owner's size.</td>"
    f'<td class="srccell">{src_links(["S24"])}</td></tr>',
    "<tr><td>Large owners use pricing software to stay just under the limit</td>"
    "<td>Using revenue-management software that recommends rents from non-public competitor data is "
    "unlawful in San Francisco, with a separate violation for every month and every unit. Tenants, the "
    "City Attorney and tenants' organisations can all sue.</td>"
    f'<td class="srccell">{src_links(["S18", "S32"])}</td></tr>',
    "<tr><td>Small owner-occupiers are exempt from fair-housing rules</td>"
    "<td>The federal exemption requires the owner to actually occupy one of the units in a building of "
    "no more than four families. It does not apply here, and it would not narrow the city's rent-control "
    "obligations in any event.</td>"
    f'<td class="srccell">{src_links(["S30", "S10"])}</td></tr>',
  ])}

<h2>What an individual owner should actually do</h2>
<ol>
  <li><strong>File the inventory and get the licence.</strong> This is the only step that is genuinely
  administrative, and it is the one most often skipped. It is free.</li>
  <li><strong>Write the rule down once and apply it to both tenancies.</strong> A one-page rent-setting
  policy — "the annual allowable increase is imposed on each tenancy's anniversary date, on base rent,
  together with any banked prior-year allowances" — is the single most useful document you can produce if
  either tenant ever asks why. It also answers the discrimination question you raised: the reason the
  two units are treated differently is visible on the page and has nothing to do with who lives there.</li>
  <li><strong>Keep the file.</strong> Licence status for the effective date, last rent and last increase
  date, the notice and proof of service, the form 571 sheet for each percentage used. Everything a
  reviewer would ask for fits in one folder.</li>
  <li><strong>Do not reach for a reason.</strong> The lawful reason is the published percentage. Adding a
  market-rent or life-circumstances explanation does not help and can create a retaliation or harassment
  issue where none existed.</li>
</ol>
"""
    return page("practice.html", "How owners handle increases", body,
                "Corporate versus individual owners in law, what the sources cannot tell you about actual "
                "practice, and the four things an individual owner should do.")


def build_sources() -> str:
    rows = []
    for sid, s in SOURCES.items():
        rows.append(
            "<tr>"
            f'<td><a class="src" href="{e(s["url"])}">{e(sid)}</a></td>'
            f'<td><a href="{e(s["url"])}">{e(s["name"])}</a></td>'
            f'<td>{e(s["used_for"])}</td>'
            f'<td class="quote">&ldquo;{e(s["quote"])}&rdquo;</td>'
            "</tr>"
        )
    body = f"""
<p>Every source below was fetched and read directly on <strong>{e(RETRIEVED)}</strong>. The final column
quotes the text that the source was used to support, so each claim on this site can be checked against
the page without leaving this table. All are government or official pages; the one repository-internal
entry (S33) is used only for audit findings about this repository, never for a legal or numeric value.</p>
{table(["ID", "Source", "Used to confirm", "Verbatim text relied on"], rows)}
<div class="callout">
  <h3>Sources that were tried and rejected</h3>
  <p>Commercial landlord and property-management blogs were found during research and deliberately
  excluded from every value, even where they agreed. Two sf.gov URL patterns used by earlier sessions
  return "we can't find that page" (<code>/topics/rent-increase-license</code> and
  <code>/information/annual-rent-increases</code>); the live pages were located and are cited instead.
  See <a href="flagged.html">F15</a> and the repo audit.</p>
</div>
"""
    return page("sources.html", "Sources", body,
                f"All {len(SOURCES)} sources with the exact text each one supports. Fetch date: {RETRIEVED}.")


def build_flagged() -> str:
    flags = SITE["flags"]
    audit = SITE["repo_audit"]
    corr = SITE["corrections"]

    flag_rows = []
    for f in flags:
        flag_rows.append(
            "<tr>"
            f'<td><strong>{e(f["id"])}</strong></td>'
            f'<td><span class="sev sev-{e(f["severity"].lower())}">{e(f["severity"])}</span></td>'
            f'<td><strong>{e(f["topic"])}</strong><br><span class="muted">{e(f["detail"])}</span>'
            f'<br><span class="timing">To close it: {e(f["action_required"])}</span></td>'
            f'<td class="srccell">{src_links(f["sources"])}</td>'
            "</tr>"
        )
    audit_rows = [
        f'<tr><td>{e(a["id"])}</td><td><span class="sev sev-{e(a["severity"].lower())}">{e(a["severity"])}</span></td>'
        f'<td><strong>{e(a["finding"])}</strong><br><span class="muted">{e(a["detail"])}</span></td>'
        f'<td class="srccell">{src_links(a.get("sources", ["S33"]))}</td></tr>'
        for a in audit
    ]
    corr_rows = [
        f'<tr><td>{e(c["id"])}</td><td><strong>{e(c["item"])}</strong></td><td>{e(c["prior"])}</td>'
        f'<td>{e(c["corrected"])}</td><td class="srccell">{src_links(c["sources"])}</td></tr>'
        for c in corr
    ]

    high = sum(1 for f in flags if f["severity"] == "HIGH")
    med = sum(1 for f in flags if f["severity"] == "MEDIUM")
    low = sum(1 for f in flags if f["severity"] == "LOW")

    body = f"""
<div class="callout warn">
  <h2>Read this page before you serve a notice</h2>
  <p><strong>{len(flags)} items</strong> are flagged: {high} high, {med} medium and {low} low severity.
  Four of the high items can void an otherwise arithmetically correct increase, and none of them is
  something the arithmetic can fix. Nothing here blocks publication; everything here is something you
  should resolve or accept knowingly before the notice goes out.</p>
</div>

<h2>Irregularities and unverified items</h2>
<p>Each row states what is uncertain, why it matters to the numbers, and what would close it. Values that
no official source could confirm were left blank in the tables rather than estimated.</p>
{table(["ID", "Severity", "Item", "Official source"], flag_rows)}

<h2>The four that change the numbers</h2>
<table class="grid">
<thead><tr><th scope="col">Flag</th><th scope="col">If it resolves one way</th><th scope="col">If it resolves the other way</th><th scope="col">Official source</th></tr></thead>
<tbody>
<tr><td><a href="flagged.html">F01</a></td><td>Unit 2: <strong>13.1% = $412.65</strong>; Unit 1: <strong>3.0% = $119.85</strong> (Rule 4.12, 12 months)</td><td>Unit 2: <strong>11.7% = $368.55</strong>; Unit 1: <strong>1.6% = $63.92</strong> (sf.gov page, 24 months)</td><td class="srccell">{src_links(["S05", "S04"])}</td></tr>
<tr><td><a href="flagged.html">F02</a></td><td>Anniversary stays 1 February; an increase effective 1 Feb 2027 is available</td><td>If a new tenancy is treated as starting 1 April 2026, nothing can be served now; the first increase would fall after the current rate period</td><td class="srccell">{src_links(["S01", "S26"])}</td></tr>
<tr><td><a href="flagged.html">F03</a></td><td>Unit 2 has been flat since 2019: 11.5% of banked years stands</td><td>Any year already applied must come out of the bank, lowering the ceiling</td><td class="srccell">{src_links(["S05", "S03"])}</td></tr>
<tr><td><a href="flagged.html">F04</a></td><td>Licence current on the effective date: increase stands</td><td>Licence missing: the entire increase is null and void, whatever the percentage</td><td class="srccell">{src_links(["S07", "S09"])}</td></tr>
</tbody></table>

<h2>Repository audit</h2>
<p>Findings about this repository itself, from a line-by-line check of every edition published by earlier
sessions. Nothing was deleted; the findings are recorded so they can be reviewed.</p>
{table(["ID", "Severity", "Finding", "Source"], audit_rows)}

<h2>Corrections to earlier published figures</h2>
<p>Places where an earlier session's published conclusion was right but its stated reasoning was not, or
where its figure was superseded. Recorded rather than silently overwritten.</p>
{table(["ID", "Item", "As previously published", "Corrected or clarified here", "Official source"], corr_rows)}

<h2>How to read a blank</h2>
<p>A blank cell on this site means exactly one thing: no official source confirmed a value, so no value
was entered. It never means zero, and it never means "we assumed". Every blank has a corresponding flag
above.</p>
"""
    return page("flagged.html", "Flagged for review", body,
                "Everything uncertain, everything unverified, and every correction to earlier work, with "
                "the source for each.")


# ---------------------------------------------------------------- assembly

PAGES = {
    "index.html": build_index,
    "process.html": build_process,
    "units.html": build_units,
    "limits.html": build_limits,
    "requirements.html": build_requirements,
    "questions.html": build_questions,
    "notice.html": build_notice,
    "review.html": build_review,
    "practice.html": build_practice,
    "sources.html": build_sources,
    "flagged.html": build_flagged,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    written = []
    for slug, fn in PAGES.items():
        (OUT / slug).write_text(fn(), encoding="utf-8")
        written.append(slug)
    # stylesheet and tiny progressive-enhancement filter
    (OUT / "assets" / "styles.css").write_text(CSS, encoding="utf-8")
    (OUT / "assets" / "app.js").write_text(JS, encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote {len(written)} pages + assets to site2/: " + ", ".join(written))


CSS = """
:root{
  --ink:#14181f; --muted:#5b6675; --line:#dfe4ea; --bg:#ffffff; --soft:#f6f8fa;
  --accent:#1f5f8b; --accent-soft:#eaf2f8; --ok:#1c6b45; --ok-soft:#e7f4ec;
  --warn:#8a5a00; --warn-soft:#fdf3e0; --bad:#9a2b2b; --bad-soft:#fbeceb;
  --flag:#6d3fa8; --flag-soft:#f2ecfb;
  --radius:10px; --shadow:0 1px 2px rgba(20,24,31,.06),0 2px 8px rgba(20,24,31,.04);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
a{color:var(--accent);text-underline-offset:2px}
a:hover{text-decoration-thickness:2px}
.skip{position:absolute;left:-999px}
.skip:focus{left:12px;top:12px;background:#fff;padding:8px 12px;z-index:9;border-radius:6px}
.topbar{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.topbar .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:6px 22px;padding-top:12px;padding-bottom:8px}
.brand{font-weight:700;letter-spacing:-.01em;text-decoration:none;color:var(--ink);font-size:16px;line-height:1.2}
.brand-sub{display:block;font-weight:500;font-size:11.5px;color:var(--muted);letter-spacing:.04em;text-transform:uppercase}
.nav{display:flex;flex-wrap:wrap;gap:2px 4px}
.nav a{font-size:13.5px;color:var(--muted);text-decoration:none;padding:5px 9px;border-radius:999px}
.nav a:hover{background:var(--soft);color:var(--ink)}
.nav a.active{background:var(--accent-soft);color:var(--accent);font-weight:600}
main{padding:34px 20px 70px}
h1{font-size:clamp(24px,3.4vw,33px);line-height:1.2;letter-spacing:-.02em;margin:.2em 0 .3em}
h2{font-size:clamp(19px,2.1vw,23px);line-height:1.3;margin:2.1em 0 .5em;letter-spacing:-.01em;padding-bottom:.28em;border-bottom:1px solid var(--line)}
h3{font-size:16.5px;margin:1.5em 0 .35em}
.lede{font-size:17.5px;color:var(--muted);max-width:78ch;margin:0 0 1.6em}
.muted{color:var(--muted);font-size:14.5px}
.tiny{font-size:12.5px;color:var(--muted)}
.numbers{font-weight:600;background:var(--soft);border-left:3px solid var(--accent);padding:10px 14px;border-radius:0 6px 6px 0}
.srcline{font-size:13px;color:var(--muted);margin-top:.4em}
.timing{display:inline-block;margin-top:6px;font-size:13px;color:var(--accent);background:var(--accent-soft);padding:2px 8px;border-radius:999px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);margin:1em 0 1.8em;background:#fff}
table{border-collapse:collapse;width:100%;font-size:14.5px;min-width:600px}
thead th{background:var(--soft);text-align:left;font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);padding:11px 13px;border-bottom:1px solid var(--line);white-space:nowrap}
tbody td{padding:12px 13px;border-bottom:1px solid #eef1f4;vertical-align:top}
tbody tr:last-child td{border-bottom:none}
tbody tr:hover{background:#fbfcfd}
tr.total td{background:var(--soft);font-weight:600}
tr.grand td{background:var(--accent-soft);font-weight:700}
td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
td.stepnum{font-size:20px;font-weight:700;color:var(--accent);text-align:center;width:2.5em}
td.srccell{font-size:12px;white-space:nowrap;width:1%}
td.quote{font-size:13px;color:#36404d;min-width:280px}
td.quote:before{content:""}
a.src{display:inline-block;font-variant-numeric:tabular-nums;background:var(--soft);border:1px solid var(--line);
  border-radius:5px;padding:1px 6px;font-size:11.5px;text-decoration:none;color:var(--accent);margin:1px 2px}
a.src:hover{background:var(--accent-soft);border-color:var(--accent)}
.src-private{display:inline-block;font-size:11.5px;color:var(--muted);background:#f4f2ee;border:1px solid #e6e1d8;border-radius:5px;padding:1px 6px}
.pill{display:inline-block;font-size:11.5px;font-weight:600;padding:2px 8px;border-radius:999px;white-space:nowrap;line-height:1.5}
.pill-verified,.pill-verified-by-rule{background:var(--ok-soft);color:var(--ok)}
.pill-private-input{background:#f4f2ee;color:#6b5f4a}
.pill-conflicting{background:var(--bad-soft);color:var(--bad)}
.pill-unverified{background:var(--warn-soft);color:var(--warn)}
.pill-calculated{background:var(--flag-soft);color:var(--flag)}
.blank{color:#a8b0ba;font-style:italic;font-size:13px}
.unverified{color:var(--warn);font-weight:600;font-size:12.5px}
.layer{font-size:12.5px;color:var(--muted)}
.sev{font-weight:700;font-size:11.5px;padding:2px 8px;border-radius:999px}
.sev-high{background:var(--bad-soft);color:var(--bad)}
.sev-medium{background:var(--warn-soft);color:var(--warn)}
.sev-low{background:var(--soft);color:var(--muted)}
.callout{border:1px solid var(--line);border-left:4px solid var(--accent);background:#fff;border-radius:0 var(--radius) var(--radius) 0;padding:16px 20px;margin:1.4em 0 1.8em;box-shadow:var(--shadow)}
.callout>*:first-child{margin-top:0}
.callout>*:last-child{margin-bottom:0}
.callout h2,.callout h3{margin-top:0;border-bottom:none;padding-bottom:0}
.callout.answer{background:linear-gradient(180deg,#f7fbfe,#fff);border-left-color:var(--accent)}
.callout.warn{background:var(--warn-soft);border-left-color:var(--warn);border-color:#f0dcc0}
.callout.urgent{background:var(--bad-soft);border-left-color:var(--bad);border-color:#f0cccc}
.callout.blankbox{background:var(--warn-soft);border-left-color:var(--warn);border-color:#f0dcc0;padding:12px 18px}
.callout.privacy{background:var(--soft)}
.callout p.big{font-size:19px;font-weight:600;margin:.2em 0}
.callout p.short{font-size:21px;font-weight:700;letter-spacing:-.01em;color:var(--accent);margin:.1em 0 .7em}
.callout p.jump{margin-top:1em;font-size:14.5px}
ul.qlist{list-style:none;padding:0;margin:1em 0}
ul.qlist li{padding:12px 0;border-bottom:1px solid #eef1f4}
ul.qlist li:last-child{border-bottom:none}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin:1.2em 0 2em}
.card{display:block;border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;text-decoration:none;color:inherit;background:#fff;box-shadow:var(--shadow);transition:border-color .15s,transform .15s}
.card:hover{border-color:var(--accent);transform:translateY(-1px)}
.card h3{margin:0 0 .3em;font-size:15.5px;color:var(--accent)}
.card p{margin:0;font-size:13.5px;color:var(--muted);line-height:1.55}
.card-flag{border-color:#dccdf0;background:var(--flag-soft)}
.card-flag h3{color:var(--flag)}
input[type=search]{border:1px solid var(--line);border-radius:6px;padding:6px 10px;font-size:14px;min-width:240px}
.count{font-size:13px;color:var(--muted);margin-left:8px}
.foot{border-top:1px solid var(--line);background:var(--soft);padding:26px 0 40px;margin-top:20px}
.foot p{font-size:13px;color:var(--muted);max-width:84ch}
@media (max-width:640px){
  .nav a{font-size:13px;padding:4px 7px}
  main{padding:22px 16px 50px}
  table{font-size:13.5px;min-width:520px}
  .wrap{padding:0 16px}
}
@media print{
  .topbar,.foot{display:none}
  .tablewrap{box-shadow:none}
  a.src{color:#000}
  body{font-size:11pt}
}
"""

JS = """
// Progressive enhancement only. Every page is fully readable without it.
(function(){
  var input=document.getElementById('filter');
  if(!input) return;
  var rows=[].slice.call(document.querySelectorAll('table.filterable tbody tr'));
  var count=document.getElementById('count');
  function upd(){
    var q=input.value.trim().toLowerCase(),n=0;
    rows.forEach(function(r){
      var hit=!q||r.textContent.toLowerCase().indexOf(q)>-1;
      r.style.display=hit?'':'none';
      if(hit)n++;
    });
    if(count) count.textContent=q?n+' of '+rows.length+' shown':'';
  }
  input.addEventListener('input',upd);
  upd();
})();
"""

if __name__ == "__main__":
    main()
