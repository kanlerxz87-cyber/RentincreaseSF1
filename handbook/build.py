#!/usr/bin/env python3
"""Deterministic generator for the /handbook/ GitHub Pages edition.

Reads handbook/data/sources.json, handbook/data/site_data.json and
handbook/data/repo_audit.json and writes the ten handbook HTML pages.
Every claim-table row carries a direct link to its official source.
Unverified values are rendered as truly blank cells (<td></td>).
No personal identifier is read or emitted by this generator.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SOURCES = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text(encoding="utf-8"))}
SITE = json.loads((DATA / "site_data.json").read_text(encoding="utf-8"))
AUDIT = json.loads((DATA / "repo_audit.json").read_text(encoding="utf-8"))
DATE = SITE["meta"]["verification_date"]
RECHECK = SITE["meta"]["recheck"]["date"]

PAGES = [
    ("index.html", "Owner Dashboard", ""),
    ("decision-questions.html", "Decisions & Suggestions", str(len(SITE["decisions"]["questions"]))),
    ("licensing-guide.html", "Licence & Step-by-Step", ""),
    ("unit-calculations.html", "Unit Calculations", ""),
    ("notice-and-reasons.html", "Notice & Lawful Reasons", ""),
    ("landlord-practices.html", "Corporate vs Individual", ""),
    ("fair-housing.html", "Fair Housing: One vs Both", ""),
    ("lawyer-scrutiny.html", "Tenant-Lawyer Audit", str(len(SITE["review"]))),
    ("repo-audit.html", "Repository Audit", str(len(AUDIT["findings"]))),
    ("flagged-for-review.html", "Flagged for Review", str(len(SITE["flags"]))),
    ("sources.html", "Official Sources", str(len(SOURCES))),
]


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def src(ids: list[str]) -> str:
    parts = []
    for sid in ids:
        s = SOURCES[sid]
        parts.append(
            f'<a class="src-ref" href="sources.html#{e(sid)}">{e(sid)}</a> '
            f'<a href="{e(s["url"])}">{e(s["short"])} &#8599;</a>'
        )
    return "<br>".join(parts)


def badge(text: str, kind: str) -> str:
    return f'<span class="badge badge-{e(kind)}">{e(text)}</span>'


def sev_badge(sev: str) -> str:
    kind = {"High": "flag", "Medium": "warn", "Low": "ok"}.get(sev, "warn")
    return badge(sev, kind)


def money(value: str) -> str:
    return f"${float(value):,.2f}"


def cell(value: object) -> str:
    """Blank stays truly blank; anything else is escaped text."""
    if value is None or str(value) == "":
        return "<td></td>"
    return f"<td>{e(value)}</td>"


def num_cell(value: object) -> str:
    if value is None or str(value) == "":
        return "<td></td>"
    return f'<td class="num">{e(value)}</td>'


def table(table_id: str, headers: list[str], rows: list[str], filterable: bool = False) -> str:
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    filt = ""
    if filterable:
        filt = (
            f'<div class="filter-bar"><label>Filter rows '
            f'<input class="filter-input" type="search" data-table-filter="{e(table_id)}" '
            f'placeholder="Type to filter this table"></label>'
            f'<span class="filter-status" data-filter-status="{e(table_id)}"></span></div>'
        )
    body = "\n".join(rows)
    return (
        f"{filt}<div class=\"table-wrap\"><table class=\"data-table\" id=\"{e(table_id)}\">"
        f"<thead><tr>{head}</tr></thead><tbody>\n{body}\n</tbody></table></div>"
    )


def layout(current: str, eyebrow: str, title: str, lead: str, body: str) -> str:
    nav_items = []
    for fname, label, count in PAGES:
        active = ' class="active"' if fname == current else ""
        extra = ' class="nav-flagged"' if fname == "flagged-for-review.html" else ""
        # active class goes on the anchor; flagged styling on the li anchor wrapper class merge:
        cls = "active" if fname == current else ""
        if fname == "flagged-for-review.html":
            cls = (cls + " nav-flagged").strip()
        cls_attr = f' class="{e(cls)}"' if cls else ""
        count_html = f'<span class="nav-count">{e(count)}</span>' if count else ""
        nav_items.append(f'<li><a href="{e(fname)}"{cls_attr}>{e(label)} {count_html}</a></li>')
    nav = "\n".join(nav_items)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} | SF Rent Increase Handbook (94122)</title>
<meta name="description" content="Anonymized, official-source-verified San Francisco rent increase handbook for a reported 1940 two-unit building in Outer Sunset 94122. Verified {e(DATE)}.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<div class="topbar"><span><strong>SF Rent Increase Handbook</strong> &middot; Outer Sunset 94122 &middot; reported 1940 two-unit building</span><span class="topbar-meta"><span class="pill-top">Verified {e(DATE)}</span><span class="pill-top">{len(SOURCES)} official sources</span><a href="sources.html">Official sources</a> <a href="flagged-for-review.html">Flagged for Review</a></span></div>
<div class="layout">
<aside class="sidebar"><p class="brand-title">Compliance Handbook</p><p class="brand-sub">Anonymized placeholders only. Dates and dollar amounts exactly as supplied. Unverified values are left blank and flagged &mdash; never inferred.</p><nav aria-label="Handbook"><ul class="nav-list">
{nav}
</ul></nav><p class="sidebar-foot">Canonical root dashboard: <a href="../index.html">repository home</a>. This handbook is an independent, disjoint-scope edition; preserved earlier editions are archives.</p></aside>
<main class="main-content" id="main">
<header class="page-header"><span class="eyebrow">{e(eyebrow)}</span><h1>{e(title)}</h1><p class="lead">{e(lead)}</p></header>
{body}
<footer class="site-footer"><span>Verified live {e(DATE)} against official publishers; primary sources re-read {e(RECHECK)}. General information, not legal advice for a specific lease.</span><span><a href="EXECUTIVE_SUMMARY.md">Executive Summary (Markdown)</a> &middot; <a href="sources.html">Sources</a> &middot; <a href="flagged-for-review.html">Flagged for Review</a></span></footer>
</main>
</div>
<script src="assets/filter.js"></script>
</body>
</html>
"""


def section(title: str, desc: str, inner: str) -> str:
    d = f'<p class="section-desc">{e(desc)}</p>' if desc else ""
    return f'<section class="card-section"><div class="section-head"><h2>{e(title)}</h2></div>{d}{inner}</section>'


def calc_row(c: dict) -> str:
    comp = "<br>".join(
        f"{e(x['label'])}: {e(x['pct'])}% = {money(x['dollar'])}"
        for x in c["components"]
    )
    return (
        f"<tr><td><strong>{e(c['id'])}</strong><br>{e(c['label'])}</td>"
        f'<td class="num">{money(c["base"])}</td><td>{comp}</td>'
        f'<td class="num">{e(c["total_pct"])}%<br><strong>+{money(c["increase"])}/mo</strong></td>'
        f'<td class="num"><strong>{money(c["new_rent"])}</strong></td>'
        f"<td>{e(c['effective_label'])}<br>{e(c['notice_days'])} days personal / {c['notice_days'] + 5} days CA mail<br>"
        f"Serve by: {e(c['personal_label'])} / {e(c['mail_label'])}<br>{e(c['status'])}</td>"
        f"{cell(c['official_confirmation'])}"
        f'<td class="src-cell">{src(c["sources"])}</td></tr>'
    )


def flag_row(f: dict) -> str:
    return (
        f'<tr id="{e(f["id"])}"><td><strong>{e(f["id"])}</strong><br>{sev_badge(f["severity"])}</td>'
        f"<td>{e(f['item'])}<br><em>Missing:</em> {e(f['missing'])}<br><em>Effect:</em> {e(f['effect'])}</td>"
        f"{cell(f['official_confirmation'])}"
        f"<td>{e(f['action'])}</td>"
        f'<td class="src-cell">{src(f["sources"])}</td></tr>'
    )


# ---------------------------------------------------------------- index
def page_index() -> str:
    calc_rows = [calc_row(c) for c in SITE["calculations"]]
    reg_rows = [
        f'<tr><td><strong>Housing Inventory + Rent Increase License</strong> (SF Rent Board)</td><td>Yes &mdash; mandatory for an individual 2-unit owner; no individual-owner exemption (buildings of 1&ndash;9 units since March 1, 2023)</td><td>Free; annually by March 1; late filing accepted, no monetary penalty</td><td>Hard gate: no current licence on the <em>effective date</em> = entire annual/banked increase null and void</td><td class="src-cell">{src(["HS01", "HS02", "HS03"])}</td></tr>',
        f'<tr><td><strong>Annual Rent Board Fee</strong> (SF Rent Board)</td><td>Yes, per dwelling unit unless an approved exemption applies</td><td>$59.00 per dwelling unit for 2026&ndash;27, due March 1; 2027 exemption request deadline December 14, 2026</td><td>Separate from the licence; after full payment 50% ($29.50) is recoverable only as the fee pages direct &mdash; never added to base rent</td><td class="src-cell">{src(["HS06", "HS07", "HS08"])}</td></tr>',
        f'<tr><td><strong>Business Registration Certificate</strong> (Treasurer &amp; Tax Collector)</td><td>Conditionally no &ldquo;by reason of that fact alone&rdquo; for one residential structure with fewer than four units; other SF business, payroll or short-term rental can change this</td>{cell("")}<td>Not a Rent Ordinance validity gate; Inventory asks for the number &ldquo;if any&rdquo;</td><td class="src-cell">{src(["HS09", "HS10", "HS01"])}</td></tr>',
    ]
    body = f"""
<div class="callout callout-forefront"><h2>Forefront answer: yes &mdash; an individual owner needs the Rent Increase License, obtained before serving notice</h2>
<p>There is <strong>no individual-owner or small-building exemption</strong> from Housing Inventory reporting. Every owner of a 1&ndash;9 unit building (including this reported two-unit building) has had to report annually since March 1, 2023. Reporting is free at <a href="https://portal.sfrb.org/">portal.sfrb.org</a>; a Rent Increase License is then generated for each tenant-occupied unit. The legal test is licence-on-the-<em>effective-date</em>, but tenants can look the licence up immediately and petition before (Form 518) or after (Form 516C) the effective date &mdash; so the challenge-proof workflow is: <strong>report first, download both licences, then serve notice</strong>. Ordinary annual/banked notices themselves are served on tenants, not filed with the Rent Board for approval.</p>
<p><a href="licensing-guide.html">Open the beginner step-by-step licence guide</a> &middot; <a href="EXECUTIVE_SUMMARY.md">Read the Executive Summary</a></p></div>
<div class="kpi-grid">
<div class="kpi-card"><div class="kpi-label">Current annual allowance</div><div class="kpi-value">1.6%</div><div class="kpi-note">March 1, 2026 &ndash; February 28, 2027 (Form 571). Next rate: blank &mdash; unpublished.</div></div>
<div class="kpi-card"><div class="kpi-label">Official sources verified {e(DATE)}</div><div class="kpi-value">{len(SOURCES)}</div><div class="kpi-note">SF, California and federal official publishers only.</div></div>
<div class="kpi-card"><div class="kpi-label">Items flagged for review</div><div class="kpi-value">{len(SITE['flags'])}</div><div class="kpi-note">Unverified values stay blank; flags do not block reading the verified guidance.</div></div>
<div class="kpi-card"><div class="kpi-label">Tenant-lawyer audit gates</div><div class="kpi-value">{len(SITE['review'])}</div><div class="kpi-note">Every gate needs its own evidence; arithmetic alone is not acceptance.</div></div>
</div>
<div class="callout callout-alert"><h2>Legislative alert: pending File #261020 (not law)</h2>
<p>Live Legistar check on {e(DATE)}: <strong>Pending Committee Action</strong>, no final action or enactment date. As proposed (Leg Ver1 / Leg Dig Ver1) it would cap combined banked + capital-improvement increases at 10% of the lowest base rent in the prior 12 months through December 31, 2029, for banked notices on or after September 15, 2026, preserving excess for January 1, 2030 or later. Any banked notice served now is after that proposed cutoff. Unit 2 therefore also shows partial-banked options U2-C1 and U2-C2. Re-check before serving.</p></div>
{section("Conditional scenarios at a glance (not notice-ready)", "All dollar figures assume the supplied base rents and histories stated on the calculations page. Official confirmation is blank until leases, ledgers and Portal licences are proved.", table("index-calcs", ["Scenario", "Assumed base", "Additive components", "Total", "New base", "Effective / notice / status", "Official confirmation", "Official source"], calc_rows))}
{section("Three different City requirements — do not confuse them", "", table("index-regs", ["Requirement", "Applies here?", "Cost / deadline", "Effect", "Official source"], reg_rows))}
<div class="callout"><h2>Two direct answers (re-read {e(RECHECK)})</h2>
<p><strong>Is the Rent Board requirement state or local law?</strong> Local. The Housing Inventory report and the Rent Increase License come from San Francisco&rsquo;s Rent Ordinance, Admin. Code &sect; 37.15 (added by Ord. No. 265-20, effective January 18, 2021), and Rent Board Rules Part XIII &sect; 13.14. State law applies on top of that: the notice periods in Civ. Code &sect; 827, and the statewide rules in Civ. Code &sect;&sect; 1947.12 and 1954.53. See the <a href="EXECUTIVE_SUMMARY.md">Executive Summary</a>.</p>
<p><strong>The &ldquo;2023&rdquo; date:</strong> The ordinance took effect in 2021. Reporting began on March 1, 2023 for condominiums and buildings with fewer than 10 units, and the licence rule applies to increases effective on or after that date for those buildings. A 1&ndash;9 unit owner therefore must report and hold a licence; there is no individual-owner exemption.</p>
<p><strong>Time-critical:</strong> For a 28 February 2027 increase above 10% (Unit 2 scenarios), the last service dates are <strong>30 November 2026</strong> (personal delivery) and <strong>25 November 2026</strong> (mail). Read the <a href="decision-questions.html">Decisions &amp; Suggestions</a> page before choosing any option.</p></div>
<div class="callout callout-privacy"><h2>Privacy</h2><p>Tenant identities and any street address are withheld. Occupants appear only as placeholders (Unit 1: Placeholder Tenants 1A&ndash;1D; Unit 2: Placeholder Tenants 2A&ndash;2B). Dates and dollar amounts are exactly as supplied. Blank cells mean &ldquo;not confirmed from an official source or proved record&rdquo; &mdash; never a guess.</p></div>
"""
    return layout("index.html", "Owner dashboard", "What an individual owner must do before any rent increase", "Start with the licence answer, then work through calculations, notice, fair housing and the tenant-lawyer audit. Every table row links to its official source.", body)


# ---------------------------------------------------------------- licensing
def page_licensing() -> str:
    step_rows = [
        f'<tr><td class="num">{s["n"]}</td><td><strong>{e(s["action"])}</strong><br>{e(s["details"])}</td><td class="src-cell">{src(s["sources"])}</td></tr>'
        for s in SITE["steps"]
    ]
    duty_rows = [
        f'<tr><td>Who must report?</td><td>Owners of residential dwelling units subject to Chapter 37; reporting by one co-owner suffices. No corporation requirement and no individual-owner exemption.</td><td class="src-cell">{src(["HS01", "HS02"])}</td></tr>',
        f'<tr><td>When did 1&ndash;9 unit buildings start?</td><td>March 1, 2023; then annually by March 1. Update owner/manager contact changes within 30 days.</td><td class="src-cell">{src(["HS01", "HS06"])}</td></tr>',
        f'<tr><td>What is reported (non-owner-occupied unit)?</td><td>Mailing address; owner-occupied status; owner/manager habitability contact; business registration number if any; approx. sq ft (250-ft increments), bedrooms/baths; vacant/occupied + dates + prior-12-month history; base rent in $250 increments + landlord-paid utilities.</td><td class="src-cell">{src(["HS01", "HS02", "HS03"])}</td></tr>',
        f'<tr><td>Unsure of a field?</td><td>Report to the best of knowledge on information and belief; state unknown with the reason. Rule 13.13 deems that substantial compliance and bars penalties for good-faith approximation.</td><td class="src-cell">{src(["HS03", "HS02"])}</td></tr>',
        f'<tr><td>Licence consequence</td><td>Substantial compliance = licence for §37.3(a)(1)&ndash;(2) increases. Noncompliance suspends it; restoration is prospective only and the tenant owes nothing for suspension months. An increase effective while unlicensed is null and void (effective date controls), but banking rights survive for a future licensed notice.</td><td class="src-cell">{src(["HS01", "HS03"])}</td></tr>',
        f'<tr><td>Late? Cost?</td><td>Late Housing Inventory submission is still accepted and can still generate a licence; the Rent Board states no monetary penalty for late Inventory filing. (The separate Rent Board Fee does carry late penalties.)</td><td class="src-cell">{src(["HS02", "HS07"])}</td></tr>',
        f'<tr><td>Must the licence be attached to the notice? Must each increase be filed?</td><td>No and no, for annual/banked increases: the licence need not be included with the notice, and banked increases do not need Rent Board approval. Petition types (O&amp;M, capital, comparables, utility) are different and do require a petition/worksheet first.</td><td class="src-cell">{src(["HS02", "HS13", "HS20"])}</td></tr>',
        f'<tr><td>How a tenant challenges a missing licence</td><td>Portal lookup by address/APN, then Tenant Summary Petition (Form 518) before the effective date or Tenant Petition for Unlawful Rent Increase (Form 516C) after it, for an ALJ hearing/refund.</td><td class="src-cell">{src(["HS04", "HS05"])}</td></tr>',
    ]
    body = f"""
<div class="callout callout-forefront"><h2>The one-sentence answer</h2><p>An individual owner must complete the free annual Housing Inventory report and have a current Rent Increase License for the unit <strong>on the effective date</strong> &mdash; and should finish reporting and save both licence PDFs <strong>before</strong> serving notice, because that is what prevents a Form 518/516C challenge.</p></div>
{section("The licence duty, line by line", "", table("lic-duty", ["Question", "Verified rule", "Official source"], duty_rows))}
{section("Beginner step-by-step (no prior Rent Board experience assumed)", "Work the steps in order. Do not serve notice until Steps 1–7 are evidenced in the file.", table("lic-steps", ["Step", "Action and exact detail", "Official source"], step_rows))}
{section("What happens if you skip it", "These are the tenant-side routes your notice would face. Paper fallback (email/drop-off) exists, but the Portal is the documented route.", table("lic-risk", ["Situation", "Tenant route / consequence", "Official source"], [
        f'<tr><td>No licence yet, increase not yet effective</td><td>Tenant Summary Petition (Form 518); Rent Board staff write to the landlord that a licence is required before the increase takes effect.</td><td class="src-cell">{src(["HS04"])}</td></tr>',
        f'<tr><td>Increase took effect while unlicensed</td><td>Tenant Petition for Unlawful Rent Increase (Form 516C); ALJ hearing; possible rent refund. Increase is null and void for the unlicensed period.</td><td class="src-cell">{src(["HS04", "HS03", "HS01"])}</td></tr>',
        f'<tr><td>Owner cures late</td><td>Licence restored prospectively only; tenant does not owe the increase for suspension months. Underlying banked percentages are not forfeited.</td><td class="src-cell">{src(["HS01", "HS03"])}</td></tr>',
    ]))}
"""
    return layout("licensing-guide.html", "Licence & step-by-step", "Rent Board licence: the individual-owner walkthrough", "Free, online, and required. Follow the ten steps in order; keep dated Portal evidence for each unit.", body)


# ---------------------------------------------------------------- calculations
def page_calcs() -> str:
    unit_rows = []
    for u in SITE["units"]:
        occ = "<br>".join(e(x) for x in u["occupants_current"])
        unit_rows.append(
            f'<tr><td><strong>{e(u["label"])}</strong><br>Lease start: {e(u["lease_start_label"])}<br>{occ}</td>'
            f'<td class="num">{e(u["base_rent_label"])}/month<br>{e(u["base_status"])}</td>'
            f'{cell(u["official_confirmation"])}<td class="src-cell">{src(u["sources"])}</td></tr>'
        )
    rate_rows = []
    for r in SITE["rates"]:
        pct = f'<td class="num">{e(r["pct"])}%</td>' if r["pct"] else "<td></td>"
        rate_rows.append(f'<tr><td>{e(r["period"])}</td>{pct}<td class="src-cell">{src(r["sources"])}</td></tr>')
    calc_rows = [calc_row(c) for c in SITE["calculations"]]
    u2b = next(c for c in SITE["calculations"] if c["id"] == "U2-B")
    bank_rows = [
        f'<tr><td>{e(x["label"])}</td><td class="num">{e(x["pct"])}%</td><td class="num">{money(x["dollar"])}</td><td>{e(x["basis"])}</td><td class="src-cell">{src(["HS11", "HS13", "HS15"])}</td></tr>'
        for x in u2b["components"]
    ]
    notice_rows = [
        f'<tr><td>{e(c["id"])} ({e(c["total_pct"])}%)</td><td>{e(c["effective_label"])}</td><td class="num">{c["notice_days"]} days</td><td>{e(c["personal_label"])}</td><td>{e(c["mail_label"])} ({c["notice_days"] + 5} days by CA mail)</td><td class="src-cell">{src(["HS24", "HS25"])}</td></tr>'
        for c in SITE["calculations"]
    ]
    notice_rows.append(
        f'<tr><td>U2-C2 alternative (10.0%)</td><td>February 1, 2027 (scenario)</td><td class="num">30 days</td><td>2 January 2027</td><td>28 December 2026 (35 days by CA mail)</td><td class="src-cell">{src(["HS24", "HS25"])}</td></tr>'
    )
    body = f"""
<div class="callout"><h2>How to read these numbers</h2><p>Arithmetic is exact to the cent (additive percentages on base rent only; never compounded, never rounded up). <strong>Conditional</strong> means the supplied input/history still has to be proved from the lease and ledger. Nothing here is permission to serve notice. The 2027&ndash;28 rate cell is blank because it was unpublished on {e(DATE)}.</p></div>
{section("Supplied unit inputs (anonymized)", "Dates and dollars exactly as supplied; official confirmation stays blank until proved records are attached.", table("calc-units", ["Unit and occupants", "Supplied rent and status", "Official confirmation", "Official source"], unit_rows))}
{section("Form 571 allowable annual increases used", "The official rate schedule controls over narrative worked examples (see Flagged FL-19).", table("calc-rates", ["Effective period", "Allowable annual increase", "Official source"], rate_rows))}
{section("Conditional scenarios", "", table("calc-main", ["Scenario", "Assumed base", "Additive components", "Total", "New base", "Effective / notice / status", "Official confirmation", "Official source"], calc_rows))}
{section("Unit 2 assumed bank, year by year (U2-B only)", "Each line is an assumption until the ledger proves the increase was actually skipped and eligible. Banking guidance (24 full months without an increase) and Rule 4.12 (12 months from when the skipped allowance could first have been imposed; only with an annual increase) are different measuring points &mdash; the February 2027 scenarios satisfy both on the assumed histories.", table("calc-bank", ["Component", "Percent", "Dollars on $3,150.00", "Basis", "Official source"], bank_rows))}
{section("Notice calendar for the scenarios", "Personal delivery vs California mail (+5 days). Serve well before the last date and keep proof; other increases in the 12-month look-back can move a scenario into the 90-day band.", table("calc-notice", ["Scenario", "Effective (scenario)", "Statutory band", "Last personal-service date", "Last CA-mail date", "Official source"], notice_rows))}
{section("Unit 1 occupant change: what it does not allow", "", table("calc-occ", ["Question", "Verified answer on reported facts", "Official source"], [
        f'<tr><td>Can rent reset to market because occupants changed April 1, 2026?</td><td>No. A continuing original occupant (Placeholder Tenant 1A) remained, so there was no vacancy and no §6.14/Costa-Hawkins reset. Both routes key to the <em>last</em> original occupant leaving, under different tests (vacates vs no longer permanently resides).</td><td class="src-cell">{src(["HS21", "HS22", "HS29", "HS14"])}</td></tr>',
        f'<tr><td>Can rent rise because an occupant joined?</td><td>No. An increase solely because an additional occupant joined is prohibited even if the lease purports to allow it. Reported Unit 1 rent was unchanged ($3,995.00) across the change, consistent with that ban.</td><td class="src-cell">{src(["HS14", "HS22", "HS12"])}</td></tr>',
        f'<tr><td>What must still be preserved for the future?</td><td>Whether a §6.14 notice was timely served on Placeholder Tenant 1D (60-day benchmark) and whether Tenant 1D is a co-tenant or subtenant/assignee. Neither changes today&rsquo;s 1.6% math; both decide any future claim if Tenant 1A leaves. Optional determination petition: Form 537.</td><td class="src-cell">{src(["HS21", "HS22", "HS23"])}</td></tr>',
        f'<tr><td>Does the statewide AB 1482 cap (8.8%) replace the SF 1.6% cap here?</td><td>No. For units under the SF Rent Ordinance rent-increase limitations the statewide figure does not apply; the stricter local Form 571 rate governs this reported 1940 building.</td><td class="src-cell">{src(["HS27", "HS28"])}</td></tr>',
    ]))}
"""
    return layout("unit-calculations.html", "Unit calculations", "Unit 1 and Unit 2: exact conditional arithmetic", "94122 has no separate official rate. The San Francisco Form 571 rate, banking rules and §827 notice bands produce every figure below.", body)


# ---------------------------------------------------------------- notice
def page_notice() -> str:
    rows_service = [
        f'<tr><td>Total increase 10% or less (including all increases in the prior 12 months)</td><td class="num">30 days</td><td class="num">35 days</td><td>Personal delivery, or mail under CCP §1013</td><td class="src-cell">{src(["HS24", "HS25"])}</td></tr>',
        f'<tr><td>Total increase more than 10%</td><td class="num">90 days</td><td class="num">95 days</td><td>Personal delivery, or mail under CCP §1013</td><td class="src-cell">{src(["HS24", "HS25"])}</td></tr>',
        f'<tr><td>Mail to/from outside California (within the US) / outside the US</td><td colspan="2">Add 10 days / 20 days respectively instead of 5 (Secretary of State address-confidentiality program: 12 days; overnight delivery: +2 court days)</td><td>Use the extension that matches the actual mailing/address facts</td><td class="src-cell">{src(["HS25"])}</td></tr>',
        f'<tr><td>Email, text, portal message or taping to the door alone</td><td colspan="2">Not a §827(b)(1) method</td><td>Use personal delivery or USPS mail; mailing copy must bear date/place-of-mailing notation or be accompanied by the mailing certificate</td><td class="src-cell">{src(["HS24", "HS25"])}</td></tr>',
    ]
    rows_content = [
        f'<tr><td>Current base, dollar increase, percentage, new base, effective date</td><td>Best-practice completeness drawn from Rent Board guidance; use the rate in force on the effective date, on base rent only, without rounding up</td><td class="src-cell">{src(["HS12"])}</td></tr>',
        f'<tr><td>Annual vs banked split, with banked basis dates</td><td>Required written itemisation (§37.3(b), Rules 4.10/4.12). Omission consequences are text-specific (Rule 4.10(b) amount exception; Rule 4.12(b) says missing banked dates alone does not void) &mdash; include everything anyway</td><td class="src-cell">{src(["HS14", "HS15"])}</td></tr>',
        f'<tr><td>Any certified/passthrough components (if claimed)</td><td>State each portion separately; utility/water/bond passthroughs need their Board forms/worksheets and, where required, filing before notice</td><td class="src-cell">{src(["HS14", "HS15", "HS20"])}</td></tr>',
        f'<tr><td>Licence copy attached?</td><td>Not required. What matters is a current licence on the effective date, verifiable on the Portal</td><td class="src-cell">{src(["HS02", "HS04"])}</td></tr>',
    ]
    rows_reasons = [
        f'<tr><td>Annual allowable (currently 1.6%)</td><td>{badge("Lawful without petition", "ok")}</td><td>Statutory entitlement under §37.3(a)(1) if licence, lease, base, timing and service all check out; no cost excuse needed</td><td class="src-cell">{src(["HS14", "HS11", "HS12"])}</td></tr>',
        f'<tr><td>Properly banked prior allowances</td><td>{badge("Lawful without petition", "ok")}</td><td>Additive, eligible and proved from the ledger; re-check File #261020 before serving any banked notice dated on/after Sept 15, 2026</td><td class="src-cell">{src(["HS13", "HS15", "HS16", "HS17"])}</td></tr>',
        f'<tr><td>Operating &amp; maintenance, capital improvement, comparable-rent, utility routes</td><td>{badge("Petition/worksheet first", "warn")}</td><td>Six petition types must be filed before notice (tenants need not pay until approved). Post-April 3, 2018 purchases: increased debt service is not considered and ownership-change tax uplift is narrowly limited &mdash; &ldquo;taxes/mortgage went up&rdquo; is not a standalone annual-increase reason</td><td class="src-cell">{src(["HS20", "HS22"])}</td></tr>',
        f'<tr><td>&ldquo;Extra occupant / roommate joined&rdquo;</td><td>{badge("Unlawful as a surcharge", "flag")}</td><td>Prohibited solely for an added occupant even if the lease says otherwise (narrow petition route for certain authorized-occupancy costs aside)</td><td class="src-cell">{src(["HS14", "HS22"])}</td></tr>',
        f'<tr><td>&ldquo;Below market / catch up to market&rdquo; on an occupied controlled unit</td><td>{badge("Not an annual/banked reason", "flag")}</td><td>Market reset needs a vacancy/§6.14/Costa-Hawkins basis or a granted comparables petition &mdash; none is established for Unit 1 while Tenant 1A remains</td><td class="src-cell">{src(["HS14", "HS20", "HS21", "HS29"])}</td></tr>',
        f'<tr><td>Fixed-term mid-term increase without an escalation clause</td><td>{badge("Barred by the lease", "flag")}</td><td>California guidance: no increase during a fixed term unless the agreement expressly allows it</td><td class="src-cell">{src(["HS26"])}</td></tr>',
    ]
    body = f"""
{section("Statutory service bands (Civil Code §827 + CCP §1013)", "The 10% threshold counts the proposed increase together with other increases in the 12 months before the effective date. When in doubt, use the longer band and serve early.", table("notice-bands", ["Situation", "Personal delivery", "CA mail", "Valid methods / notes", "Official source"], rows_service))}
{section("What the written notice must show", "", table("notice-content", ["Item", "Rule", "Official source"], rows_content))}
{section("Lawful reasons vs reasons that invite challenge", "Annual/banked increases need no excuse letter. Attaching an unlawful rationale (occupancy, market catch-up, unpetitioned costs) creates the challenge it purports to explain.", table("notice-reasons", ["Stated basis", "Status", "Why", "Official source"], rows_reasons))}
<div class="callout"><h2>File the paperwork, keep the proof</h2><p>Keep the final signed notice, the calculation worksheet, the licence PDFs and the proof of service/certificate of mailing together per unit. If any certified, passthrough or petition component is ever added, file the petition/worksheet <em>before</em> serving that notice.</p></div>
"""
    return layout("notice-and-reasons.html", "Notice & lawful reasons", "How to notify tenants — and what counts as a lawful reason", "Written notice, statutory service, complete itemisation, and no invented justifications.", body)


# ---------------------------------------------------------------- practices
def page_practices() -> str:
    rhfs = [
        ("Share of rental properties", "14.6% of properties", "0.4% of properties"),
        ("Share of rental units", "15.5% of units", "39.2% of units"),
        ("Median debt-service coverage ratio", "74", "164"),
        ("2023 mean operating expenses per unit", "$5,820 (±$529)", "$10,979 (±$6,441)"),
        ("2023 mean capital improvement value per unit", "$2,665 (±$404)", "$2,019 (±$321)"),
        ("Mean low – high rents", "$1,326 – $1,668", "$1,324 – $2,239"),
        ("Mean original / outstanding debt per property", "$320k / $261k", "$22,161k / $17,085k"),
    ]
    rhfs_rows = [
        f'<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td class="src-cell">{src(["HS38"])}</td></tr>'
        for a, b, c in rhfs
    ]
    body = f"""
{section("The law does not split by owner size", "", table("prac-rules", ["Topic", "Individual 2-unit owner", "Large/corporate owner", "Official source"], [
        f'<tr><td>Housing Inventory + licence</td><td>Same duty; Individual Unit form (bulk Excel only recommended at 5+ units)</td><td>Same duty; bulk upload available at 5+ units</td><td class="src-cell">{src(["HS01", "HS02", "HS05"])}</td></tr>',
        f'<tr><td>Annual cap + banking</td><td>Same Form 571 percentages, same banking rules</td><td>Same</td><td class="src-cell">{src(["HS11", "HS13", "HS14"])}</td></tr>',
        f'<tr><td>Notice</td><td>Same §827/§1013 service and itemisation</td><td>Same</td><td class="src-cell">{src(["HS24", "HS25", "HS14"])}</td></tr>',
        f'<tr><td>Business Registration</td><td>Conditional &lt;4-unit carve-out (&ldquo;by that fact alone&rdquo;)</td><td>Per-building separate registration/treatment; carve-out assessed per structure and other activity</td><td class="src-cell">{src(["HS09", "HS10"])}</td></tr>',
        f'<tr><td>Pricing software</td><td>Manual Form 571 math has no §37.10C exposure; using a covered algorithmic device would</td><td>Covered algorithmic devices using nonpublic competitor data are banned for any SF landlord; DOJ RealPage matter is allegations + a proposed consent judgment, not proof about every firm</td><td class="src-cell">{src(["HS37", "HS41"])}</td></tr>',
    ]))}
{section("What federal data actually show: 2–4 units vs 50+ units (2024 RHFS, national)", "Structure and finance differ; lawful increase behaviour by owner type in San Francisco is not measured in an official dataset and stays blank (FL-15). National survey means are context, not a 94122 rent norm.", table("prac-rhfs", ["Measure", "2 to 4 units", "50 or more units", "Official source"], rhfs_rows))}
{section("Practical difference that matters for this building", "", table("prac-practical", ["Control", "Why it protects a small owner", "Official source"], [
        f'<tr><td>Per-unit licence + ledger file</td><td>Replaces portfolio systems with two auditable files: lease, ledger, licence PDF, worksheet, notice, proof</td><td class="src-cell">{src(["HS02", "HS04", "HS12"])}</td></tr>',
        f'<tr><td>No competitor-data pricing tool</td><td>Keeps the owner outside §37.10C and the fact pattern alleged in the federal RealPage complaint</td><td class="src-cell">{src(["HS37", "HS41"])}</td></tr>',
        f'<tr><td>Uniform written policy</td><td>One neutral rule for both units is the small-portfolio equivalent of a corporate policy manual (see Fair Housing page)</td><td class="src-cell">{src(["HS34", "HS35", "HS36"])}</td></tr>',
    ]))}
"""
    return layout("landlord-practices.html", "Corporate vs individual", "How large operators and individual owners compare", "Same ordinance, different scale. Use the federal survey for structure — never as a stereotype or a rent norm.", body)


# ---------------------------------------------------------------- fair housing
def page_fair() -> str:
    rows_law = [
        f'<tr><td>Federal Fair Housing Act, 42 U.S.C. §3604</td><td>Race, color, religion, sex, familial status, national origin, disability (handicap)</td><td>No percentage cap; discriminatory terms/conditions are unlawful. Owner-occupied 1–4 family exemption (§3603(b)(2)) is narrow, never covers §3604(c) statements, and does not displace California/SF law</td><td class="src-cell">{src(["HS36", "HS39"])}</td></tr>',
        f'<tr><td>California FEHA, Gov. Code §12955 (+ §12955(f) anti-retaliation)</td><td>Adds gender identity/expression, sexual orientation, marital status, ancestry, source of income (incl. vouchers), veteran/military, genetic information and more</td><td>Applies to this rental with no 2-unit &ldquo;Mrs. Murphy&rdquo; shelter; dominant-purpose retaliation for opposing unlawful practices is separately barred</td><td class="src-cell">{src(["HS34"])}</td></tr>',
        f'<tr><td>Unruh Civil Rights Act, Civ. Code §51</td><td>Adds citizenship, primary language, immigration status, medical condition, age and arbitrary personal characteristics in business establishments</td><td>Equal accommodations/privileges required; perceived/associated characteristics count</td><td class="src-cell">{src(["HS35", "HS34"])}</td></tr>',
        f'<tr><td>SF Tenant Harassment, Admin. Code §37.10B</td><td>Bad-faith service cuts, repair failures, push-out coercion, and violating any anti-discrimination law</td><td>Treble actual damages or $1,000 statutory (greater), plus mandatory prevailing-tenant fees; Rent Board rent-reduction route for (a)(1)–(3)</td><td class="src-cell">{src(["HS40"])}</td></tr>',
        f'<tr><td>Anti-retaliation, Civ. Code §1942.5</td><td>Protected complaints, inspections, proceedings, association/rights activity</td><td>180-day listed-event screen (tenant not in rent default) plus a general retaliatory-purpose ban; lawful cause/good faith preserved — screen facts, claim neither blanket ban nor blanket clearance</td><td class="src-cell">{src(["HS33"])}</td></tr>',
    ]
    rows_scen = [
        f'<tr><td>Both units eligible; same neutral policy, same method, each priced from its own proved base/bank</td><td>{badge("Lowest-risk pattern", "ok")}</td><td>Differences trace to records (base, anniversary, proved bank), not people. Identical percentages are not required; identical <em>method</em> is the protection</td><td class="src-cell">{src(["HS34", "HS35", "HS36", "HS12"])}</td></tr>',
        f'<tr><td>Only one unit raised because the other is in a closed fixed term, unlicensed, in a repair/citation hold, or inside a retaliation screen</td><td>{badge("Documented neutral reason", "ok")}</td><td>Deferring an ineligible unit is compliance, not favouritism. Never raise an ineligible unit &ldquo;for symmetry&rdquo;</td><td class="src-cell">{src(["HS26", "HS01", "HS30", "HS33"])}</td></tr>',
        f'<tr><td>Only one unit raised, chosen by who the tenants are, who complained, voucher status, family status, or a desire to push a unit vacant</td><td>{badge("Unlawful motive risk", "flag")}</td><td>Protected-trait, retaliatory or bad-faith selection violates FEHA/Unruh/FHA/§37.10B even if the percentage itself is within Form 571</td><td class="src-cell">{src(["HS34", "HS35", "HS36", "HS40"])}</td></tr>',
        f'<tr><td>Different banked totals per unit because ledgers genuinely differ</td><td>{badge("Neutral if proved", "warn")}</td><td>Allowed only to the extent each bank is proved year-by-year; an assumed bank (notably Unit 2) cannot justify a real-world difference until proved</td><td class="src-cell">{src(["HS13", "HS15", "HS11"])}</td></tr>',
    ]
    body = f"""
<div class="callout"><h2>Short answer</h2><p>Raising one unit and not the other is <strong>not automatically discrimination</strong>. Exposure turns on <em>why</em> that unit was chosen. Fix a neutral written policy from records (lease eligibility, proved base, anniversary, Form 571 rate, proved bank) <strong>before</strong> serving, apply the same method to both units, and defer any unit that fails a legal gate. For a two-unit owner there is no California/SF small-owner shelter to fall back on.</p></div>
{section("The four overlapping bans (+ retaliation)", "", table("fair-law", ["Law", "Protected grounds (summary)", "What it means for unit selection", "Official source"], rows_law))}
{section("One unit or both: worked patterns", "", table("fair-scen", ["Pattern", "Assessment", "Reasoning", "Official source"], rows_scen))}
{section("Documentation checklist (keep with both unit files)", "", table("fair-docs", ["Record", "What it must show", "Official source"], [
        f'<tr><td>Neutral policy memo (dated, pre-service)</td><td>Eligibility rule, rate source, banking method and deferral gates — written before outcomes per unit are known</td><td class="src-cell">{src(["HS12", "HS34"])}</td></tr>',
        f'<tr><td>Per-unit eligibility sheet</td><td>Lease term, anniversary, proved base/bank, licence status, repair/citation and retaliation screens per unit</td><td class="src-cell">{src(["HS01", "HS30", "HS33"])}</td></tr>',
        f'<tr><td>Communications log</td><td>No protected-trait, complaint-history or vacancy-motive input into selection; repair requests answered on their own track</td><td class="src-cell">{src(["HS40", "HS33", "HS34"])}</td></tr>',
    ]))}
"""
    return layout("fair-housing.html", "Fair housing", "Raising one unit or both: discrimination analysis", "Motive and method decide legality. Document neutral criteria before you serve — especially with no small-owner exemption under California/SF law.", body)


# ---------------------------------------------------------------- scrutiny
def page_scrutiny() -> str:
    review_rows = [
        f'<tr><td class="num">{r["n"]}</td><td><strong>{e(r["test"])}</strong><br>{e(r["evidence"])}</td><td>{e(r["result"])}</td><td class="src-cell">{src(r["sources"])}</td></tr>'
        for r in SITE["review"]
    ]
    petition_rows = [
        f'<tr><td>Tenant Summary Petition (Form 518)</td><td>Before the effective date (e.g., no licence yet)</td><td>Staff letter to landlord: licence required before the increase takes effect</td><td class="src-cell">{src(["HS04"])}</td></tr>',
        f'<tr><td>Tenant Petition for Unlawful Rent Increase (Form 516C)</td><td>After an allegedly unlawful increase took effect</td><td>ALJ hearing/decision; refund exposure for unlicensed or over-cap amounts</td><td class="src-cell">{src(["HS04", "HS01", "HS03"])}</td></tr>',
        f'<tr><td>Failure to Repair and Maintain (Form 516B, Topic 353)</td><td>Within 60 days after receiving the increase notice</td><td>Deferral until repairs are made (no deferral if completed before the effective date); pay disputed increase pending decision</td><td class="src-cell">{src(["HS31"])}</td></tr>',
        f'<tr><td>Financial hardship application (Topic 363)</td><td>Passthroughs / O&amp;M only</td><td>Not available for annual, banked or Costa-Hawkins increases — do not concede or promise it for CPI scenarios</td><td class="src-cell">{src(["HS32"])}</td></tr>',
        f'<tr><td>§6.14 / Costa-Hawkins determination (Form 537, Topic 329)</td><td>Either side, when a future reset is disputed</td><td>Optional Rent Board determination; no petition is required to assert a (well-founded) route, and tenants may petition alleging unlawfulness</td><td class="src-cell">{src(["HS23", "HS21"])}</td></tr>',
    ]
    body = f"""
<div class="callout"><h2>Assume a tenant advocate reads every line</h2><p>Tenants need no lawyer to petition, and the Rent Board referral listing includes counseling/legal-aid providers serving 94122 (including a Sunset-district office) — subject to each provider&rsquo;s eligibility, scope and capacity. &ldquo;Free representation for every notice review&rdquo; is <strong>not</strong> guaranteed (FL-20). The defence is not rhetoric; it is passing all sixteen gates on documents.</p></div>
{section(f"Sixteen-gate tenant-lawyer audit ({len(SITE['review'])} gates)", "“Verified” means the legal rule/scope was confirmed from the official source on 2026-11-11. Anything fact-dependent stays “Needs evidence” until the record is in the file.", table("scrutiny-main", ["#", "Gate and evidence required", "Result", "Official source"], review_rows, filterable=True))}
{section("Petition routes a tenant can actually file", "", table("scrutiny-petitions", ["Route", "When", "Consequence", "Official source"], petition_rows))}
{section("Normal business practice, stated defensibly", "", table("scrutiny-practice", ["Claim you may make (if evidenced)", "Claim never to make", "Official source"], [
        f'<tr><td>&ldquo;Annual/banked increase priced from Form 571 on proved base rent, under a current licence, with statutory notice&rdquo;</td><td>&ldquo;Market/94122 norm requires this catch-up&rdquo; (no official figure — FL-16)</td><td class="src-cell">{src(["HS11", "HS12"])}</td></tr>',
        f'<tr><td>&ldquo;Same written method applied to both units; differences follow proved records&rdquo;</td><td>&ldquo;Everyone does it / corporate landlords charge more, so this is normal&rdquo; (no official behaviour dataset — FL-15)</td><td class="src-cell">{src(["HS34", "HS38"])}</td></tr>',
        f'<tr><td>&ldquo;No covered pricing software was used&rdquo;</td><td>Any suggestion rents were set from nonpublic competitor data</td><td class="src-cell">{src(["HS37", "HS41"])}</td></tr>',
    ]))}
"""
    return layout("lawyer-scrutiny.html", "Tenant-lawyer audit", "Would this survive tenant-advocate scrutiny?", "Sixteen gates, five petition routes, and the exact wording that helps or hurts.", body)


# ---------------------------------------------------------------- repo audit
def page_audit() -> str:
    base_rows = [
        f'<tr><td>{e(b["suite"])}</td><td><code>{e(b["command"])}</code></td><td>{e(b["result"])}</td><td class="src-cell">{src(b["sources"])}</td></tr>'
        for b in AUDIT["baseline"]
    ]
    find_rows = [
        f'<tr id="{e(f["id"])}"><td><strong>{e(f["id"])}</strong><br>{sev_badge(f["severity"])}</td><td>{e(f["files"])}<br>{e(f["irregularity"])}</td>{cell(f["official_confirmation"])}<td>{e(f["status"])}</td><td class="src-cell">{src(f["sources"])}</td></tr>'
        for f in AUDIT["findings"]
    ]
    arith_rows = [
        f'<tr><td>Unit 1 annual: $3,995.00 × 1.6%</td><td class="num">$63.92 → $4,058.92</td><td>Exact Decimal recompute matches</td><td class="src-cell">{src(["HS11"])}</td></tr>',
        f'<tr><td>Unit 1 banked scenario: 1.4% + 1.6% = 3.0%</td><td class="num">$55.93 + $63.92 = $119.85 → $4,114.85</td><td>Exact; earliest Feb 1, 2027 on assumed history</td><td class="src-cell">{src(["HS11", "HS15", "HS13"])}</td></tr>',
        f'<tr><td>Unit 2 annual: $3,150.00 × 1.6%</td><td class="num">$50.40 → $3,200.40</td><td>Exact on the assumed (unproved) base</td><td class="src-cell">{src(["HS11"])}</td></tr>',
        f'<tr><td>Unit 2 banked maximum: 11.5% + 1.6% = 13.1%</td><td class="num">$362.25 + $50.40 = $412.65 → $3,562.65</td><td>Exact; high caution (ledger + File #261020)</td><td class="src-cell">{src(["HS11", "HS16"])}</td></tr>',
        f'<tr><td>Service calendar (Feb 1 / Feb 28, 2027)</td><td>Jan 2 / Dec 28; Jan 29 / Jan 24; Nov 30 / Nov 25, 2026</td><td>Day-exact §827/§1013 subtraction matches</td><td class="src-cell">{src(["HS24", "HS25"])}</td></tr>',
    ]
    body = f"""
<div class="callout"><h2>Scope of this audit</h2><p>Read-only line-by-line check of the canonical dashboard, root Markdown and preserved editions against the 42 live official sources. Shared-file fixes are logged in <code>COORDINATION.md</code> for their scope holders — this disjoint edition never edits another session&rsquo;s files. Full text: <code>audit/session-fb3db9a1/REPO_AUDIT.md</code>.</p></div>
{section("Suite baseline (re-run on the final combined tree before merge)", "", table("audit-baseline", ["Suite", "Command", "Result", "Official source"], base_rows))}
{section("Independent arithmetic and calendar verification", "", table("audit-arith", ["Check", "Recomputed value", "Verdict", "Official source"], arith_rows))}
{section("Irregularities found (RA-FB3-01 – RA-FB3-08)", "Official confirmation is blank where the fix belongs to another scope holder or a repository administrator.", table("audit-findings", ["ID", "Files and irregularity", "Official confirmation", "Status", "Official source"], find_rows, filterable=True))}
"""
    return layout("repo-audit.html", "Repository audit", "Line-by-line repository verification", "What was recomputed, what passed, and every irregularity — with nothing silently fixed in someone else’s scope.", body)


# ---------------------------------------------------------------- flagged
def page_flagged() -> str:
    rows = [flag_row(f) for f in SITE["flags"]]
    body = f"""
<div class="callout callout-alert"><h2>Flagged for Review — read this before serving anything</h2><p>{len(SITE['flags'])} items could not be confirmed from an official source or proved record on {e(DATE)}. Their official-confirmation cells are intentionally <strong>blank</strong>. Flags do not block reading the verified guidance; High-severity flags (notably FL-01–FL-05, FL-17, FL-22, FL-24, FL-25, FL-26, FL-28) block treating any scenario dollar figure as notice-ready.</p></div>
{section("All flagged and unverified items", "Filter by unit, topic or severity. Resolve each item from the named record, then attach dated evidence to the unit file.", table("flags-main", ["Flag", "Item, missing record and effect", "Official confirmation", "Action required", "Official source"], rows, filterable=True))}
"""
    return layout("flagged-for-review.html", "Flagged for Review", "Flagged for Review: blanks that must stay blank", "If it is listed here, do not fill it in by inference. Prove it, price without it, or defer.", body)


# ---------------------------------------------------------------- sources
def page_sources() -> str:
    rows = []
    for sid in sorted(SOURCES):
        s = SOURCES[sid]
        rows.append(
            f'<tr id="{e(sid)}"><td><strong>{e(sid)}</strong><br>{e(s["short"])}</td>'
            f'<td>{e(s["title"])}<br><em>{e(s["publisher"])}</em> &middot; {e(s["layer"])}<br>Retrieved: {e(s["retrieved"])}</td>'
            f'<td>&ldquo;{e(s["quote"])}&rdquo;<br><em>Used for:</em> {e(s["used_for"])}</td>'
            f'<td class="src-cell"><a href="{e(s["url"])}">Official source &#8599;</a><br><code>{e(s["url"])}</code></td></tr>'
        )
    body = f"""
<div class="callout"><h2>Official publishers only</h2><p>All {len(SOURCES)} sources were fetched and read live on {e(DATE)} from San Francisco (sf.gov, portal.sfrb.org, sftreasurer.org, sfgov.legistar.com), California (leginfo.legislature.ca.gov, courts.ca.gov) and federal (govinfo.gov, hud.gov, justice.gov, census.gov) publishers. No commercial listing, blog or aggregator is cited anywhere in this handbook.</p></div>
{section("Source registry HS01–HS42", "Every claim-table row in this handbook links here and directly to the official URL.", table("sources-main", ["ID", "Source", "Verified passage and use", "Official link"], rows, filterable=True))}
"""
    return layout("sources.html", "Official sources", "Official source registry (42 sources)", "One row per live-verified official source. If a claim is not traceable to this registry, it is flagged — not asserted.", body)


# ---------------------------------------------------------------- decisions
def page_decisions() -> str:
    dec = SITE["decisions"]
    q_rows = []
    for q in dec["questions"]:
        q_rows.append(
            f'<tr id="{e(q["id"])}"><td><strong>{e(q["id"])}</strong></td>'
            f'<td>{e(q["question"])}</td>'
            f'<td>{e(q["known"])}</td>'
            f'<td>{e(q["unknown"])}</td>'
            f'<td>{e(q["how"])}</td>'
            f'<td class="src-cell">{src(q["sources"])}</td>'
            f'<td>{e(q["status"])}</td></tr>'
        )
    s_rows = []
    for s_ in dec["suggestions"]:
        opts = "<br>".join(f"&#9744; {e(o)}" for o in s_["options"])
        s_rows.append(
            f'<tr id="{e(s_["id"])}"><td><strong>{e(s_["id"])}</strong><br>{e(s_["title"])}</td>'
            f'<td>{e(s_["proposal"])}</td>'
            f'<td>{opts}</td>'
            f'<td>{e(s_["why"])}<br><em>Effort:</em> {e(s_["effort"])}</td>'
            f'<td class="src-cell">{src(s_["sources"])}</td>'
            f'<td>Owner choice: ________<br>Date: ________</td></tr>'
        )
    body = f"""
<div class="callout callout-alert"><h2>Read first: nothing on this page changes a figure or a notice</h2>
<p>{e(dec["intro"])}</p>
<p><strong>Time-critical:</strong> the last service dates for a 28 February 2027 increase above 10% are <strong>25 November 2026</strong> (mail) and <strong>30 November 2026</strong> (personal delivery). Decide before then, or choose a later effective date.</p></div>
{section("Questions to answer before deciding", "What the official record already says, what is missing, and how to find out. Filter by question or status. Every row links to the official source it relies on.", table("decision-questions", ["ID", "Question", "What the official record says", "What we do not have", "How to find out", "Official source", "Status"], q_rows, filterable=True))}
{section("Suggestions: choose a path before anything is implemented", "Tick one option per suggestion. These are decision aids, not legal advice. Attorney review is recommended before any banked notice (S-08).", table("decision-suggestions", ["ID", "Suggestion", "Options (tick one)", "Why and effort", "Official source", "Owner decision"], s_rows, filterable=True))}
"""
    return layout("decision-questions.html", "Decisions & Suggestions", "Questions to answer, and paths to choose from, before any decision", "Work through the questions in order. Each one lists what the official record says, what is still missing, and where to find it. Suggestions are for the owner to choose from; none has been implemented.", body)


BUILDERS = {
    "index.html": page_index,
    "decision-questions.html": page_decisions,
    "licensing-guide.html": page_licensing,
    "unit-calculations.html": page_calcs,
    "notice-and-reasons.html": page_notice,
    "landlord-practices.html": page_practices,
    "fair-housing.html": page_fair,
    "lawyer-scrutiny.html": page_scrutiny,
    "repo-audit.html": page_audit,
    "flagged-for-review.html": page_flagged,
    "sources.html": page_sources,
}


def main() -> None:
    for fname, _label, _count in PAGES:
        out = BUILDERS[fname]()
        (ROOT / fname).write_text(out, encoding="utf-8")
        print(f"wrote handbook/{fname} ({len(out)} bytes)")


if __name__ == "__main__":
    main()
