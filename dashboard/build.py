#!/usr/bin/env python3
"""Build the independent verification dashboard from the verified data registry.

No network access and no third-party packages are needed. Every published table
row is rendered with a link to an official source from dashboard/data/site_data.json.
"""
from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "site_data.json").read_text(encoding="utf-8"))
SOURCES = {s["id"]: s for s in DATA["sources"]}
FACTS = DATA["facts"]
CASE = DATA["case_facts"]
FLAGS = {f["id"]: f for f in DATA["flags"]}
SCENARIOS = DATA["scenarios"]

NAV = [
    ("index.html", "Overview"),
    ("pages/summary.html", "Executive Summary"),
    ("pages/laws.html", "Laws & Rates"),
    ("pages/units.html", "Case Facts"),
    ("pages/analysis.html", "Analysis & Scenarios"),
    ("pages/notice.html", "Notice & Reasons"),
    ("pages/owners.html", "Owner Practices"),
    ("pages/discrimination.html", "One Unit or Both"),
    ("pages/review.html", "Tenant Lawyer Review"),
    ("pages/sources.html", "Official Sources"),
    ("pages/flagged.html", "Flagged for Review"),
    ("pages/repo.html", "Repo Review"),
]


def e(value) -> str:
    return html.escape(str(value), quote=True)


def src_links(ids, label: str | None = None) -> str:
    out = []
    for sid in ids:
        s = SOURCES[sid]
        text = label or sid
        out.append(
            f'<a class="src" href="{e(s["url"])}" target="_blank" '
            f'rel="noopener noreferrer" title="{e(s["agency"])} — {e(s["title"])}">{e(text)}</a>'
        )
    return " ".join(out)


def fact_row(f) -> list[str]:
    return [
        f'<span class="mono">{e(f["id"])}</span>',
        f'<span class="pill pill-{e(f["level"].split()[0].lower())}">{e(f["level"])}</span>',
        e(f["topic"]),
        e(f["value"]),
        e(f["effective"]),
        src_links([f["source_id"]]),
    ]


def table(headers: list[str], rows: list[list[str]], caption: str, row_ids=None, filterable=True) -> str:
    cls = ' class="data-table" data-filter="1"' if filterable else ' class="data-table"'
    head = "".join(f"<th scope=\"col\">{e(h)}</th>" for h in headers)
    body = []
    for i, row in enumerate(rows):
        rid = f' id="{e(row_ids[i])}"' if row_ids and i < len(row_ids) else ""
        cells = "".join(f"<td>{c}</td>" for c in row)
        body.append(f"<tr{rid}>{cells}</tr>")
    return (
        f'<div class="table-wrap"><table{cls}><caption>{e(caption)}</caption>'
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def callout(title: str, body: str, kind: str = "info") -> str:
    return f'<div class="callout {kind}"><h3>{e(title)}</h3>{body}</div>'


def nav_html(prefix: str) -> str:
    items = []
    for path, label in NAV:
        href = path if prefix == "" else ("../index.html" if path == "index.html" else path.split("/")[-1])
        items.append(f'<a href="{e(href)}">{e(label)}</a>')
    return '<nav aria-label="Dashboard navigation">' + "".join(items) + "</nav>"


def page(title: str, intro: str, body: str, prefix: str = "", active: str = "") -> str:
    css = f"{prefix}assets/style.css"
    js = f"{prefix}assets/app.js"
    home = "index.html" if prefix == "" else "../index.html"
    nav_items = []
    for path, label in NAV:
        href = path if prefix == "" else ("../index.html" if path == "index.html" else path.split("/")[-1])
        sel = ' class="active"' if label == active else ""
        nav_items.append(f'<a{sel} href="{e(href)}">{e(label)}</a>')
    nav = '<nav aria-label="Dashboard navigation">' + "".join(nav_items) + "</nav>"
    footer_sources = f"{prefix}pages/sources.html"
    footer_flagged = f"{prefix}pages/flagged.html"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Anonymized, official-source-only San Francisco rent-increase review dashboard.">
<title>{e(title)} — SF Rent Review</title>
<link rel="stylesheet" href="{e(css)}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <a class="brand" href="{e(home)}"><span class="brand-mark">SF</span><span>Rent Increase Review<small>independent verification dashboard</small></span></a>
  <div class="topbar-tools">
    <label class="search"><span class="sr-only">Filter table rows</span><input id="tableFilter" type="search" placeholder="Filter table rows…" autocomplete="off"></label>
    <a class="top-link" href="{e(footer_flagged)}">Flagged for Review</a>
  </div>
</header>
<div class="layout">
  <aside class="sidebar">{nav}</aside>
  <main class="content" id="main">
    <div class="page-head"><p class="eyebrow">San Francisco · ZIP 94122 area · anonymized</p><h1>{e(title)}</h1><p class="lede">{intro}</p></div>
{body}
    <footer class="footer"><p>Compiled 2026-11-06 from official government sources. Informational summary only — not legal advice. Real tenant identifiers are never published.</p><p><a href="{e(footer_sources)}">Official source register</a> · <a href="{e(footer_flagged)}">Flagged for Review</a> · <a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1" target="_blank" rel="noopener noreferrer">Repository</a></p></footer>
  </main>
</div>
<script src="{e(js)}"></script>
</body>
</html>
"""


def write(path: str, text: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def build_index() -> None:
    key_rows = [
        ["Current SF allowable annual increase", "1.6% of base rent", "March 1, 2026 – February 28, 2027", src_links(["S02"])],
        ["Prior allowable annual increase", "1.4% of base rent", "March 1, 2025 – February 28, 2026", src_links(["S02"])],
        ["Statutory formula", "60% of CPI; maximum 7%", "SF Admin. Code §37.3(a)(1)", src_links(["S09"])],
        ["AB 1482 statewide cap for SF area", "8.8% (5% + 3.8% CPI)", "August 1, 2026 – July 31, 2027; does not apply to units under the SF Rent Ordinance cap", src_links(["S27", "S28"])],
        ["Notice period", "30 days; 90 days if over 10%; +5 days if mailed", "Current", src_links(["S01", "S29"])],
        ["Rent increase license", "Required before an annual or banked increase takes effect", "Current", src_links(["S13"])],
        ["Federal numeric rent cap for private unsubsidized housing", "", "No official federal source found — blank / flagged", src_links(["S39", "S37"])],
    ]
    cards = [
        ("pages/summary.html", "Executive Summary", "Anonymized overview, dates and amounts retained, all case values flagged unverified."),
        ("pages/laws.html", "Laws & Rates", "Local, state and federal rules in source-linked tables, including the blank federal-cap row."),
        ("pages/units.html", "Case Facts", "Placeholder unit labels only. User-supplied dates and amounts; verified values left blank."),
        ("pages/analysis.html", "Analysis & Scenarios", "Answers to every question, compliance checklist, and clearly labelled illustrative arithmetic."),
        ("pages/notice.html", "Notice & Reasons", "Step-by-step notice procedure, required contents, and official grounds for extra increases."),
        ("pages/owners.html", "Owner Practices", "What official sources document about large corporate landlords and individual owners."),
        ("pages/discrimination.html", "One Unit or Both", "Fair-housing framework and the per-unit analysis of raising one or both units."),
        ("pages/review.html", "Tenant Lawyer Review", "A checklist designed to survive review by SF tenant advocates and free legal resources."),
        ("pages/sources.html", "Official Sources", f"{len(SOURCES)} registered official sources with verbatim quotes and links for manual review."),
        ("pages/flagged.html", "Flagged for Review", f"{len(FLAGS)} irregularities and unverified items, each with official source links."),
        ("pages/repo.html", "Repo Review", "Repository inspection, merge/coordination notes, and irregularities for review."),
    ]
    card_html = "".join(
        f'<a class="card" href="{e(h)}"><span class="card-kicker">Open page</span><h3>{e(t)}</h3><p>{e(d)}</p><span class="card-arrow">→</span></a>'
        for h, t, d in cards
    )
    repo_callout = callout(
        "Repository state at a glance",
        "<p>" + str(len(SOURCES)) + " official sources · " + str(len(FACTS)) + " verified facts · "
        + str(len(CASE)) + " case facts (all unverified values blank) · " + str(len(FLAGS))
        + " flagged items · " + str(len(SCENARIOS)) + ' illustrative scenarios. See <a href="pages/repo.html">Repo Review</a>'
        + " for the line-by-line inspection and coordination notes.</p>",
    )
    body = f"""
<section class="grid-2">
  <div class="panel accent"><h2>What this dashboard answers</h2>
    <p>Whether a rent increase for two rent-controlled units in a San Francisco 94122-area building would be normal and lawful under local, state, and federal law; how notice must be given; how corporate and individual owners are treated; and whether one or both units should be increased.</p>
    <p class="small">Every published value was read from an official government page. Anything not confirmed from an official source is left blank and listed on the <a href="pages/flagged.html">Flagged for Review</a> page.</p>
  </div>
  <div class="panel"><h2>Privacy rule</h2>
    <p>No real names, initials, street addresses, or contact details are published. Only placeholders (<strong>Unit A</strong>, <strong>Unit B</strong>, Tenant A1…, Tenant B1…) are used. The user-supplied dates and amounts are kept verbatim but are <strong>flagged as unverified</strong> and are never presented as official records.</p>
    <p class="small">The Rent Board also notes that Housing Inventory submissions are public; tenant identities are deliberately kept out of this public site. {src_links(['S13'])}</p>
  </div>
</section>
<h2>Key verified figures</h2>
{table(['Item', 'Verified value', 'Effective / authority', 'Official source'], key_rows, 'Key verified figures — one official source link per row')}
<h2>Answers at a glance</h2>
<ul class="answer-list">
  <li><strong>Normal local increase:</strong> the published annual allowable increase of 1.6%, once every 12 months, on base rent only, for a licensed landlord. {src_links(['S01', 'S13'])}</li>
  <li><strong>State law:</strong> AB 1482's 8.8% cap does not replace the more protective SF cap for units covered by the Rent Ordinance. {src_links(['S27', 'S28'])}</li>
  <li><strong>Federal law:</strong> no numeric rent-increase cap for private unsubsidized housing was confirmed; federal fair-housing law still applies. That value is left blank and flagged. {src_links(['S39', 'S37', 'S38'])}</li>
  <li><strong>Corporate vs individual owners:</strong> official sources document enforcement against shared pricing algorithms and rules that apply to all owners; no official comparative practice dataset was found. {src_links(['S35', 'S36', 'S10', 'S13'])}</li>
  <li><strong>One unit or both:</strong> no official rule requires both units to be raised, and no official source supports a discrimination "safe harbor"; a uniform, documented, objective policy is the recommended analysis. {src_links(['S37', 'S33', 'S12'])}</li>
</ul>
<h2>Explore by category</h2>
<div class="cards">{card_html}</div>
{repo_callout}
"""
    write("index.html", page("Overview", "A clean, source-linked dashboard for a privacy-first review of rent increases on two rent-controlled San Francisco units.", body, "", "Overview"))


def build_summary() -> None:
    case_rows = [
        [e(c["unit"]), e(c["field"]), e(c["user_supplied"]), "", src_links([c["source_id"]]), f'<a href="flagged.html#{e(c["flag_id"])}">{e(c["flag_id"])}</a>']
        for c in CASE
    ]
    body = f"""
<section class="panel"><h2>Executive summary (anonymized, published version)</h2>
<p>This project collects, organizes, and analyzes a full list of requirements for two rent-controlled residential units in a San Francisco 94122-area building that the user says was built in 1940. The user-supplied dates and monthly amounts are retained below; all personal identifiers have been replaced with placeholders. The <em>internal</em> version of this summary is delivered in the conversation, not published here.</p>
<p><strong>Bottom line.</strong> For a covered, licensed unit, the ordinary and lawful annual increase effective March 1, 2026 through February 28, 2027 is <strong>1.6% of base rent</strong>, once every 12 months, with 30 days' written notice (90 days if the increase exceeds 10%, plus 5 days if mailed). {src_links(['S02', 'S01', 'S29'])} The state AB 1482 cap of 8.8% for the San Francisco area does not apply to units already subject to the more restrictive SF Rent Ordinance cap. {src_links(['S27', 'S28'])} No federal numeric rent cap for private unsubsidized housing was confirmed, so that value is left blank and flagged. {src_links(['S39', 'S37'])}</p>
<p><strong>Scrutiny standard.</strong> Any increase can be challenged by a tenant at no charge and with no time limit before a Rent Board Administrative Law Judge; free Rent Board counseling and an official referral listing of tenant legal resources exist. {src_links(['S18', 'S23', 'S22'])} Therefore the defensible approach is a documented, uniformly applied rule tied to each unit's own lawful base rent, anniversary date, and banking history — not to tenant characteristics. {src_links(['S01', 'S05', 'S33'])}</p>
</section>
<h2>Anonymized case facts (dates and amounts retained)</h2>
<p class="note">The <strong>Verified value</strong> column is intentionally blank on every row: these facts come only from the user, not from an official source. The final column links to the official rule that governs the field. Full details on <a href="flagged.html">Flagged for Review</a>.</p>
{table(['Unit', 'Field', 'User-supplied value (unverified)', 'Verified value', 'Governing official rule', 'Flag'], case_rows, 'Anonymized case facts — verified values blank')}
<h2>Important findings</h2>
<ul class="answer-list">
  <li><strong>Coverage is conditional.</strong> Official guidance says many units built on or before June 13, 1979 have rent control, but the specific certificate of occupancy and exemptions must be checked. {src_links(['S07'])}</li>
  <li><strong>Unit A has an occupancy-change issue.</strong> A new or additional roommate cannot itself justify extra rent; an unlimited market-rate increase is available only in narrow 6.14 / Costa-Hawkins situations, and §1954.53(d)(3) does not apply where an original occupant remains. The City strongly recommends legal advice. {src_links(['S21', 'S19', 'S20', 'S32'])}</li>
  <li><strong>Unit B may have banked increases.</strong> Skipped annual increases can be banked under detailed conditions, but eligibility depends on the full rent history and a 24-month rule; no case-specific banked amount is asserted as verified. {src_links(['S05', 'S06', 'S18'])}</li>
  <li><strong>Prerequisites matter.</strong> A current rent increase license must be on file before an annual or banked increase takes effect. {src_links(['S13'])}</li>
  <li><strong>No algorithmic rent setting.</strong> SF prohibits any landlord from using algorithmic devices fed by non-public competitor data to set rents; California and federal enforcers have acted against shared pricing algorithms. {src_links(['S10', 'S34', 'S35', 'S36'])}</li>
</ul>
{callout('Not legal advice', '<p>This dashboard is an informational summary of official sources. A San Francisco tenant lawyer should review the actual leases, rent history, notices, and license before any increase is served. See the <a href="review.html">Tenant Lawyer Review</a> checklist.</p>', 'warn')}
"""
    write("pages/summary.html", page("Executive Summary", "Anonymized overview of the project, important details, and findings — with dates and amounts retained but unverified.", body, "../", "Executive Summary"))


def build_laws() -> None:
    grouped = defaultdict(list)
    for f in FACTS:
        grouped[f["level"].split()[0]].append(f)
    sections = []
    for level, heading in [("Local", "Local law — San Francisco"), ("State", "State law — California"), ("Federal", "Federal law — United States"), ("Repository", "Repository facts")]:
        rows = [fact_row(f) for f in grouped.get(level, [])]
        if level == "Federal":
            rows.append([
                '<span class="mono">GAP</span>', '<span class="pill pill-federal">Federal</span>',
                'Numeric rent-increase cap for private unsubsidized housing',
                '', 'No official federal source found — blank / flagged F10',
                src_links(["S39", "S37", "S38"]),
            ])
        if rows:
            sections.append(f"<h2>{e(heading)}</h2>" + table(
                ["ID", "Level", "Topic", "Verified value", "Effective / authority", "Official source"],
                rows, f"{heading} — verified values with official source links"))
    body = f"""
<section class="panel"><h2>How the three levels interact</h2>
<p>The San Francisco Rent Ordinance sets a single <strong>citywide</strong> allowable annual increase; no official ZIP-code-specific rate for 94122 was found. {src_links(['S02', 'S07'])} California's AB 1482 cap is higher, but the official state chart and the City both say that where a local cap is lower, the local rule applies. {src_links(['S28', 'S27'])} At the federal level, HUD defines rent controls as state and local actions and the Fair Housing Act governs discrimination; no numeric federal cap was confirmed, so that cell is blank. {src_links(['S39', 'S37', 'S38'])}</p>
<p class="small">Secondary (non-official) calculators were found quoting both 1.6% and 1.7% for 2026–27. Official SF.gov, the Rent Board news announcement, and Form 571 all state <strong>1.6%</strong>; 1.7% belongs to 2024–25. See <a href="flagged.html#F14">F14</a>. {src_links(['S02', 'S03', 'S04'])}</p>
</section>
{''.join(sections)}
{callout('Coverage check before applying any rate', '<p>Official guidance: many units built on or before June 13, 1979 have rent control and eviction protection; check the address on the City Property Information Map and confirm exemptions with a Rent Board counselor. ' + src_links(['S07', 'S23']) + '</p>')}
"""
    write("pages/laws.html", page("Laws & Rates", "Local, state, and federal requirements in source-linked tables. Blank cells mean no official value was confirmed.", body, "../", "Laws & Rates"))


def build_units() -> None:
    case_rows = [
        [e(c["unit"]), e(c["field"]), e(c["user_supplied"]), "", src_links([c["source_id"]]), f'<a href="flagged.html#{e(c["flag_id"])}">{e(c["flag_id"])}</a>']
        for c in CASE
    ]
    coverage_rows = [
        ["Rent-control date threshold", "Many residential units built on or before June 13, 1979 have both rent control and eviction protection.", src_links(["S07"])],
        ["Check the building", "Official guidance directs users to the City's Property Information Map and to a Rent Board counselor if classification is unclear.", src_links(["S07", "S23"])],
        ["Partial exemptions", "Units built after June 13, 1979 and most single-family homes / condos (tenant moved in on or after Jan 1, 1996) may have only eviction protection.", src_links(["S07"])],
        ["Licensing prerequisite", "A current rent increase license must be on file before any annual or banked increase can go into effect.", src_links(["S13"])],
        ["State cap does not displace local cap", "Units already subject to the Rent Ordinance's rent-increase limits are not subject to the AB 1482 cap.", src_links(["S27", "S28"])],
    ]
    body = f"""
<section class="panel"><h2>Privacy and placeholder scheme</h2>
<p>The two units are labelled <strong>Unit A</strong> and <strong>Unit B</strong>. Tenants are labelled Tenant A1…, Tenant B1… . No real names, initials, or street address appear anywhere in this repository. Dates and dollar amounts are kept exactly as supplied, but they are user-provided and therefore <strong>unverified</strong>: the verified-value column is blank on every row and each item appears on <a href="flagged.html">Flagged for Review</a>.</p>
</section>
<h2>Case facts</h2>
{table(['Unit', 'Field', 'User-supplied value (unverified)', 'Verified value', 'Governing official rule', 'Flag'], case_rows, 'Anonymized case facts — all verified values blank')}
<h2>Coverage conditions (verified)</h2>
{table(['Condition', 'Verified rule', 'Official source'], coverage_rows, 'Coverage conditions from official sources')}
<h2>What must be resolved before any increase</h2>
<ul class="answer-list">
  <li>Unit A: whether the occupancy change is a continuing tenancy with an original occupant (so the ordinary AGA applies) or a new tenancy (initial rent rules). The City describes 6.14 / Costa-Hawkins as complicated and strongly encourages legal advice. {src_links(['S19', 'S20', 'S32'])}</li>
  <li>Unit A: the lawful base rent, last increase date, and anniversary date; changing an anniversary date can permanently lose a skipped increase. {src_links(['S01', 'S05', 'S06'])}</li>
  <li>Unit B: the full rent history, because banked increases cannot be computed from a start date alone. {src_links(['S05', 'S18'])}</li>
  <li>Both: license status, prior notices, petitions, passthroughs, and any subsidy or exemption. {src_links(['S13', 'S14', 'S27'])}</li>
</ul>
{callout('Illustrative arithmetic is not a verified case value', '<p>Dollar figures derived from the user-supplied rents appear only in clearly labelled callouts on <a href="analysis.html">Analysis & Scenarios</a>, never in a verified-value column. ' + src_links(['S02', 'S04']) + '</p>', 'warn')}
"""
    write("pages/units.html", page("Case Facts", "Anonymized unit and tenancy facts, dates and amounts retained, with every verified value left blank.", body, "../", "Case Facts"))


def build_analysis() -> None:
    benchmark_rows = [
        ["Local (SF Rent Ordinance)", "1.6% of base rent, once every 12 months", "March 1, 2026 – February 28, 2027", src_links(["S02", "S01"])],
        ["Local statutory ceiling", "60% of published CPI increase; never greater than 7%", "SF Admin. Code §37.3(a)(1)", src_links(["S09"])],
        ["State (AB 1482, if it applied)", "8.8% for the SF area (5% + 3.8% CPI)", "August 1, 2026 – July 31, 2027", src_links(["S27", "S28"])],
        ["State rule of priority", "Where the local cap is lower, the local rule applies; SF-covered units are outside the state cap.", "Current", src_links(["S28", "S27"])],
        ["Federal numeric cap for private unsubsidized housing", "", "No official federal source confirmed — blank / F10", src_links(["S39", "S37", "S38"])],
    ]
    def scenario_html(sc) -> str:
        return (
            f'<div class="callout scenario"><h3>{e(sc["unit"])} — {e(sc["id"])} '
            f'<span class="pill pill-warn">illustrative / unverified</span></h3>'
            f'<p class="small">{e(sc["assumption"])}</p>'
            f'<p class="figure">{e(sc["base"])} × {e(sc["rate_percent"])}% = '
            f'<strong>${e(sc["increase_amount"])}</strong> increase → '
            f'<strong>${e(sc["new_rent"])}</strong> new monthly rent</p>'
            f'<p class="small">{e(sc["note"])}</p>'
            f'<p class="small">Official rate / method: {src_links(sc["source_ids"])} · '
            f'<a href="flagged.html#{e(sc["flag_id"])}">{e(sc["flag_id"])}</a></p></div>'
        )
    scen = "".join(scenario_html(s) for s in SCENARIOS)
    body = f"""
<section class="panel"><h2>1. What is a reasonable and normal increase under local, state, and federal law?</h2>
<p>Official sources do not define "reasonable" or "normal" as a separate legal standard; they publish a maximum annual allowable increase. For a covered, licensed unit, the ordinary business practice documented by the Rent Board is one increase of up to <strong>1.6%</strong> on the tenant's anniversary, calculated on base rent only, with no rounding up. {src_links(['S01', 'S02', 'S13'])} An owner may impose less, and nothing in the Rent Board rules requires any landlord to raise any tenant's rent. {src_links(['S05', 'S12'])}</p>
<p>The state cap is higher, but official guidance says the more protective local rule applies. {src_links(['S27', 'S28'])} For federal law, no numeric rent-increase cap for private unsubsidized housing was confirmed from an official source; HUD describes rent controls as state and local actions and enforces the Fair Housing Act. That value is therefore blank and flagged rather than inferred. {src_links(['S39', 'S37', 'S38'])}</p>
</section>
{table(['Level', 'Verified benchmark', 'Effective / authority', 'Official source'], benchmark_rows, 'Verified benchmarks — blank where not officially confirmed')}
{callout('ZIP 94122 / Outer Sunset', '<p>The Rent Board publishes one citywide rate; no official source was found setting a ZIP-specific rate. The citywide rate is used and the absence of a ZIP-specific official value is flagged as <a href="flagged.html#F17">F17</a>. ' + src_links(['S02', 'S07']) + '</p>')}
<h2>2. Illustrative calculations (unverified — not legal advice)</h2>
<p class="note">These are arithmetic illustrations from user-supplied rents and official percentages. They are not verified case values, are not a Rent Board determination, and must not be served as a notice without legal review.</p>
{scen}
{callout('Unit A — alternative new-tenancy assumption', '<p>If the April 1, 2026 occupancy were legally a brand-new tenancy with an initial rent of $3,995 (user-supplied), official guidance says the Rent Ordinance does not regulate the initial rent for a new tenancy and the first annual increase would be 12 months after that tenancy began. No case-specific figure is asserted as verified. ' + src_links(['S19', 'S01']) + ' See <a href="flagged.html#F02">F02</a>.</p>', 'warn')}
<h2>3. Findings that a tenant lawyer would scrutinize</h2>
<ul class="answer-list">
  <li><strong>Unit A occupancy:</strong> a new roommate cannot itself trigger extra rent; a co-tenant is not subject to a Costa-Hawkins increase; §1954.53(d)(3) excludes partial occupancy changes where an original occupant remains. {src_links(['S21', 'S20', 'S32'])}</li>
  <li><strong>Unit A timing:</strong> a skipped increase is only banked after the applicable 24-month condition, and changing the anniversary date can lose an increase. {src_links(['S05', 'S06'])}</li>
  <li><strong>Unit B banking:</strong> increases cannot be compounded; the sum must be tied to the correct anniversary dates and full rent history. {src_links(['S06', 'S05', 'S18'])}</li>
  <li><strong>Notice threshold:</strong> any combined increase above 10% needs 90 days' written notice. {src_links(['S01', 'S29'])}</li>
  <li><strong>Above-AGA increases:</strong> six petition categories require Rent Board forms, supporting documentation, and prior filing; hardship relief is not available for annual or banked increases. {src_links(['S14', 'S17'])}</li>
</ul>
{callout('Recommended decision path (analysis, not legal advice)', '<p>Confirm coverage and license; obtain the full rent history for both units; calculate each unit separately from its own lawful base rent and anniversary; choose a documented uniform policy; serve the correct written notice; then have an SF tenant lawyer review the complete file. ' + src_links(['S07', 'S13', 'S18', 'S01', 'S22']) + '</p>', 'ok')}
"""
    write("pages/analysis.html", page("Analysis & Scenarios", "Answers to the project's questions, verified benchmarks, and clearly labelled illustrative arithmetic.", body, "../", "Analysis & Scenarios"))


def build_notice() -> None:
    procedure = [
        ["1", "Confirm the unit is covered by SF rent control and check exemptions.", src_links(["S07", "S27"])],
        ["2", "Obtain / verify a current rent increase license through the Housing Inventory before the increase takes effect.", src_links(["S13", "S01"])],
        ["3", "Determine the lawful base rent, the 12-month anniversary date, and any banked amount from the full rent history.", src_links(["S01", "S05", "S18"])],
        ["4", "Use the percentage in effect on the effective date (1.6% for March 1, 2026 – February 28, 2027).", src_links(["S01", "S02"])],
        ["5", "Calculate on base rent only; do not compound; do not round up to the nearest dollar.", src_links(["S01", "S06"])],
        ["6", "Serve written notice at least 30 days before the effective date (90 days if the increase alone or combined is over 10%; add 5 days if mailed).", src_links(["S01", "S29"])],
        ["7", "Include the dollar amount, percentage, effective date, and which portion is annual, banked, or a certified passthrough.", src_links(["S01", "S09", "S05"])],
        ["8", "For petition-based increases, file the Rent Board petition before serving the notice; tenants need not pay until approved.", src_links(["S14", "S15", "S16"])],
        ["9", "Keep a copy of the notice, proof of service, license, and calculation for tenant-lawyer review.", src_links(["S13", "S18"])],
    ]
    contents = [
        ["Dollar amount of the increase", "SF.gov guidance", src_links(["S01"])],
        ["Percentage amount of the increase", "SF.gov guidance", src_links(["S01"])],
        ["Date the increase goes into effect", "SF.gov guidance", src_links(["S01"])],
        ["Which part is annual and/or banked", "§37.3(b)(1); Rules §4.10(a)(1); banked-increase page", src_links(["S09", "S12", "S05"])],
        ["Which part reflects O&M, comparable rents, or certified capital improvements", "§37.3(b)(2)", src_links(["S09"])],
        ["Which part reflects utility / bond / RAP passthroughs, with Board forms", "§37.3(b)(3)–(4)", src_links(["S09"])],
        ["Nonconforming increase is null and void", "§37.3(b)(5); Rules §4.10(b)", src_links(["S09", "S12"])],
    ]
    reasons = [
        ["Annual allowable increase", "No petition; available to a licensed landlord once every 12 months on base rent.", src_links(["S01", "S13", "S09"])],
        ["Banked annual increase", "No petition, but strict 24-month and anniversary conditions; notice must state the banked portion.", src_links(["S05", "S06"])],
        ["Operating & maintenance expenses", "Petition required; additional increase up to 7%; two comparison years; petition before notice.", src_links(["S15", "S14"])],
        ["Capital improvements", "Petition required after work is complete and within five years; supporting documentation.", src_links(["S16", "S14"])],
        ["Special circumstances / comparable units", "Petition required; one of the six listed categories.", src_links(["S14"])],
        ["Utility, water revenue bond, general obligation bond passthroughs", "Board worksheet / petition rules; some need no petition but must use the official worksheet.", src_links(["S14", "S09"])],
        ["Any other increase above those permitted", "§37.3(a)(8) requires a petition for a rental arbitration hearing under §37.8.", src_links(["S09"])],
    ]
    body = f"""
<section class="panel"><h2>What "reasonable reasons" means in official sources</h2>
<p>For the ordinary annual allowable increase, official SF.gov pages describe a percentage-based entitlement for a licensed landlord and do not list a separate justification requirement; the six categories that require a petition and supporting documentation are listed separately. Because no official page explicitly says "no reason is required", that negative inference is flagged rather than asserted as verified (<a href="flagged.html#F09">F09</a>). {src_links(['S01', 'S13', 'S14'])}</p>
<p>General "market conditions" or "inflation" are not listed as standalone grounds for an above-AGA increase to an existing tenancy; the official grounds are the petition categories below. {src_links(['S14', 'S15', 'S09'])}</p>
</section>
<h2>Correct notification procedure</h2>
{table(['Step', 'Required action', 'Official source'], procedure, 'Step-by-step notice procedure')}
<h2>Required notice contents</h2>
{table(['Content item', 'Authority', 'Official source'], contents, 'Notice contents required by official sources')}
<h2>Lawful grounds / reasons for an increase</h2>
{table(['Ground', 'Official requirement', 'Official source'], reasons, 'Official grounds for rent increases')}
{callout('Common notice mistake', '<p>Form 1007 ("Notice to Tenant Required by §37.9(c)") is officially required on <strong>notices to terminate tenancy</strong>, not on rent-increase notices. Rent-increase notice content comes from §37.3(b), Rules §4.10, Civil Code §827, and SF.gov guidance. ' + src_links(['S24', 'S09', 'S12', 'S29']) + ' See <a href="flagged.html#F12">F12</a>.</p>', 'warn')}
{callout('Service detail', '<p>Civil Code §827 requires written notice delivered personally or served by mail under Code of Civil Procedure §1013; SF.gov adds 5 days when the notice is mailed. ' + src_links(['S29', 'S01']) + '</p>')}
"""
    write("pages/notice.html", page("Notice & Reasons", "The correct way to inform tenants, required notice contents, and official grounds for a rent increase.", body, "../", "Notice & Reasons"))


def build_owners() -> None:
    corp = [
        ["Centralized revenue-management software", "DOJ alleged competing landlords shared nonpublic rental data to train algorithmic pricing software that recommends rents (allegations, not findings).", src_links(["S35"])],
        ["Large-landlord enforcement", "DOJ's amended complaint named six large landlords alleged to have set rents using competitors' sensitive information through common pricing algorithms; together over 1.3 million units.", src_links(["S36"])],
        ["SF prohibition", "§37.10C makes it unlawful for any SF landlord to use an algorithmic device using non-public competitor data to set rents or occupancy levels.", src_links(["S10"])],
        ["Expanded enforcement", "From October 6, 2025, tenants' rights organizations may also sue to enforce the SF prohibition.", src_links(["S26"])],
        ["California antitrust law", "AB 325 (Chapter 338, 2025) makes use/distribution of a common pricing algorithm as part of a restraint of trade unlawful.", src_links(["S34"])],
        ["AB 1482 corporate difference", "The single-family/condo exemption is unavailable to REITs, corporations, and LLCs with a corporate member.", src_links(["S30", "S27", "S28"])],
    ]
    indiv = [
        ["Same local rules apply", "The Housing Inventory and rent-increase license requirements apply to all residential owners, including condominiums and buildings with 1–9 units.", src_links(["S13"])],
        ["Banking is available to any owner", "A landlord who does not impose an allowed increase may bank it; banked increases do not expire during a tenancy but do not carry over to a new tenant.", src_links(["S05"])],
        ["Petition routes are owner-size aware", "Capital improvement petition forms differ for 1–5 unit and 6+ unit buildings.", src_links(["S16"])],
        ["Small-owner organizations", "The City's official referral listing names Small Property Owners of San Francisco and the San Francisco Apartment Association.", src_links(["S22"])],
        ["Free City counseling", "Rent Board counseling on Rent Ordinance topics is free; counselors cannot give legal advice.", src_links(["S23"])],
        ["No comparative official dataset", "No official source was found quantifying how individual SF owners typically set increases; the value is blank / flagged F11.", src_links(["S13", "S22", "S35"])],
    ]
    body = f"""
<section class="panel"><h2>What can and cannot be said from official sources</h2>
<p>Official government material documents <strong>enforcement actions and rules</strong>, not a statistical description of "how corporations normally raise rent" versus "how individual owners normally raise rent". The verified findings are below; any claim about typical private behaviour by owner type is left unverified and flagged. {src_links(['S35', 'S36', 'S10', 'S13'])}</p>
</section>
<h2>Large corporate / institutional owners — verified findings</h2>
{table(['Topic', 'Verified finding', 'Official source'], corp, 'Large-landlord findings from official sources')}
<h2>Individual / small owners — verified findings</h2>
{table(['Topic', 'Verified finding', 'Official source'], indiv, 'Small-owner findings from official sources')}
{callout('Practical conclusion (analysis, not legal advice)', '<p>The SF Rent Ordinance, the licensing requirement, the notice rules, and the algorithmic-device ban apply to "landlords" generally, not only to corporations. A small owner should therefore use the same official rate calculation, the same written notice, and the same documented non-discriminatory policy as a large owner. ' + src_links(['S09', 'S13', 'S10', 'S01']) + '</p>', 'ok')}
{callout('Unverified gap', '<p>No official source was found that compares rent-increase practices by owner type or that blesses "industry practice" as a legal justification. See <a href="flagged.html#F11">F11</a> and <a href="flagged.html#F19">F19</a>. ' + src_links(['S14', 'S15']) + '</p>', 'warn')}
"""
    write("pages/owners.html", page("Owner Practices", "What official sources actually document about large real estate corporations and individual property owners.", body, "../", "Owner Practices"))


def build_discrimination() -> None:
    framework = [
        ["Federal Fair Housing Act", "Prohibits housing discrimination based on race, color, national origin, religion, sex, familial status, or disability in nearly all housing.", src_links(["S37"])],
        ["Federal discriminatory-effect rule", "24 CFR §100.500 allows liability based on discriminatory effect even without discriminatory intent, subject to a legally sufficient justification.", src_links(["S38"])],
        ["California FEHA", "Gov. Code §12955 prohibits discrimination/harassment based on a broader list including source of income, ancestry, and veteran or military status.", src_links(["S33"])],
        ["SF tenant harassment", "§37.10B prohibits bad-faith coercion to vacate (including a rent increase substantially above market in specified circumstances) and violations of anti-discrimination laws.", src_links(["S11"])],
        ["No duty to raise rent", "Rent Board Rules §4.11(e): nothing in the rules requires any landlord to raise any tenant's rent.", src_links(["S12"])],
        ["Per-unit calculation", "The allowable increase is calculated on each tenant's base rent and each tenancy's 12-month anniversary date.", src_links(["S01", "S09"])],
    ]
    matrix = [
        ["Increase only Unit A", "", "Lawful only if Unit A's own base rent, anniversary, license, and notice support it; the reason must be objective and documented, not tenant-based.", src_links(["S01", "S13", "S33"])],
        ["Increase only Unit B", "", "Same per-unit test; a long tenancy with banked increases must be supported by the full rent history.", src_links(["S05", "S18", "S33"])],
        ["Increase both units", "", "Not required by any official source found; it is not a safe harbor from fair-housing review. Apply the same written formula to both files.", src_links(["S12", "S37", "S38"])],
        ["Increase neither unit", "", "Permitted: no official rule requires a landlord to impose an allowable increase.", src_links(["S12", "S05"])],
    ]
    body = f"""
<section class="panel"><h2>The question</h2>
<p>Would it be acceptable to raise the rent on one tenant's unit, or does it make more sense to raise both to avoid discrimination lawsuits or inquiries? <strong>No official source was found that requires both units to be raised or that treats a both-unit increase as a legal safe harbor</strong> — that gap is flagged as <a href="flagged.html#F08">F08</a>. {src_links(['S37', 'S33', 'S38', 'S11'])}</p>
<p>What official sources do establish is that rent increases are calculated <strong>per unit and per tenancy</strong> (base rent, anniversary, banking, license), and that discrimination in the terms and conditions of rental is prohibited. {src_links(['S01', 'S09', 'S13', 'S37'])}</p>
</section>
<h2>Legal framework</h2>
{table(['Rule', 'Verified content', 'Official source'], framework, 'Anti-discrimination and per-unit rules')}
<h2>Decision matrix (analysis, not legal advice)</h2>
<p class="note">The <strong>Verified legal requirement</strong> column is intentionally blank where no official source states a requirement; the analysis column is a recommendation for a lawyer to review.</p>
{table(['Option', 'Verified legal requirement', 'Analysis / risk control', 'Official source'], matrix, 'One unit or both units — no verified requirement found')}
{callout('Recommended, reviewable approach', '<p>Write down one uniform, objective policy before acting: apply the published AGA to the lawful base rent on each unit&#39;s own anniversary, use the same notice form and service method, document the license and calculation for both units, and record a legitimate nondiscriminatory business reason (e.g., keeping pace with the officially published allowable increase). Then have an SF tenant lawyer review both files together. Uniformity is a risk-control measure, not a verified legal immunity. ' + src_links(['S01', 'S13', 'S09', 'S33', 'S22']) + '</p>', 'ok')}
{callout('Why raising only one unit can still be defensible', '<p>The two units have different user-supplied start dates and rents (Unit A: February 1, 2025 / $3,995; Unit B: June 1, 2019 / $3,150). Different anniversary dates and different banking histories are objective, non-personal reasons for different timing. Those inputs are unverified, so an SF tenant lawyer should confirm the rent history before relying on them. ' + src_links(['S01', 'S05', 'S18']) + ' See <a href="flagged.html#F05">F05</a>.</p>')}
{callout('Disparate-impact caution', '<p>Even a neutral policy can create liability under 24 CFR §100.500 if it has a discriminatory effect without a legally sufficient justification; state protected classes are broader than the federal list. ' + src_links(['S38', 'S33']) + '</p>', 'warn')}
"""
    write("pages/discrimination.html", page("One Unit or Both", "Whether to increase one or both units, reviewed against federal, state, and local anti-discrimination law.", body, "../", "One Unit or Both"))


def build_review() -> None:
    checklist = [
        ["Coverage", "Confirm the certificate-of-occupancy date and every exemption using official City tools.", src_links(["S07", "S23"])],
        ["License", "Verify a current rent increase license on file for the effective date.", src_links(["S13"])],
        ["Lawful base rent", "Reconstruct the full rent history; exclude passthroughs; no rounding up.", src_links(["S18", "S01"])],
        ["Anniversary / 12 months", "Confirm at least 12 months since the last increase and the correct anniversary date.", src_links(["S01", "S05"])],
        ["Rate", "Use the percentage in effect on the effective date (1.6% for 3/1/26–2/28/27).", src_links(["S01", "S02", "S03"])],
        ["Banking", "Any banked amount must satisfy the 24-month rule, be non-compounded, and belong to the same tenancy.", src_links(["S05", "S06"])],
        ["Additional occupants", "Confirm no part of the increase is based on a new roommate; confirm 6.14 / Costa-Hawkins status if relevant.", src_links(["S21", "S19", "S20", "S32"])],
        ["Notice period / service", "30 days (90 if >10%; +5 if mailed), delivered personally or by mail under CCP §1013.", src_links(["S01", "S29"])],
        ["Notice contents", "Dollar amount, percentage, effective date, and the breakdown required by §37.3(b) / Rule 4.10.", src_links(["S01", "S09", "S12"])],
        ["Petitions", "Any above-AGA increase needs the correct petition, filed before the notice, with supporting documents.", src_links(["S14", "S15", "S16"])],
        ["Algorithmic devices", "Confirm no prohibited revenue-management software was used to set the rent.", src_links(["S10", "S26", "S34"])],
        ["Fair housing / uniformity", "Document the same objective policy for both units and check protected-class and disparate-impact exposure.", src_links(["S37", "S33", "S38", "S11"])],
        ["Tenant remedies", "Be ready for a 516C unlawful-increase petition, a 518 summary petition, and hardship applications on eligible passthroughs.", src_links(["S18", "S41", "S17"])],
        ["Legal review", "Ask an SF tenant lawyer / free legal clinic to review the complete file before service.", src_links(["S22", "S23"])],
    ]
    resources = [
        ["Free Rent Board counseling", "Free counseling on Rent Ordinance topics; cannot give legal advice; multilingual.", src_links(["S23"])],
        ["Official referral listing", "City list of tenant counseling organizations, free limited-advice legal clinics, and legal-aid providers; no lawyer needed to file a Rent Board petition.", src_links(["S22"])],
        ["Tenant Right to Counsel (Prop F)", "Officially described as a right to legal representation for tenants facing eviction.", src_links(["S25"])],
        ["Tenant petitions", "No charge and no time limit for an unlawful-rent-increase / rent-history petition before an Administrative Law Judge.", src_links(["S18", "S41"])],
    ]
    body = f"""
<section class="panel"><h2>Design standard</h2>
<p>The project asks that any increase be able to pass review by San Francisco tenant-friendly advocates and lawyers, be considered reasonable and normal business practice, and show no discrimination or broken laws. The checklist below turns each official requirement into a review item. It is a compliance aid, not a guarantee of outcome and not legal advice. {src_links(['S18', 'S22', 'S33'])}</p>
</section>
<h2>Compliance review checklist</h2>
{table(['Review item', 'What the reviewer should verify', 'Official source'], checklist, 'Tenant-lawyer review checklist — one official source link per row')}
<h2>Free / low-cost review resources</h2>
{table(['Resource', 'What the official source says', 'Official source'], resources, 'Official tenant legal-help resources')}
{callout('Scope of free counsel', '<p>Proposition F / Tenant Right to Counsel is officially described for eviction proceedings; no official source was found guaranteeing free counsel for a rent-increase dispute. Free general counseling and clinic referrals are separately listed by the Rent Board. See <a href="flagged.html#F13">F13</a>. ' + src_links(['S25', 'S22', 'S23']) + '</p>', 'warn')}
{callout('What a tenant can challenge', '<p>A tenant can file an unlawful-rent-increase petition alleging that the increase exceeds the allowable annual/banked amount, is less than 12 months after the prior increase, or the landlord is not licensed. ' + src_links(['S18', 'S41']) + '</p>')}
"""
    write("pages/review.html", page("Tenant Lawyer Review", "A checklist built from official sources for scrutiny by SF tenant advocates and lawyers.", body, "../", "Tenant Lawyer Review"))


def build_sources() -> None:
    rows = []
    for s in DATA["sources"]:
        rows.append([
            f'<span class="mono">{e(s["id"])}</span>',
            e(s["agency"]),
            f'<span class="pill pill-{e(s["level"].split()[0].lower())}">{e(s["level"])}</span>',
            f'<a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])}</a>',
            e(s["quote"]),
            e(s["notes"]),
        ])
    body = f"""
<section class="panel"><h2>How this register was verified</h2>
<p>Each source below was fetched and read directly on 2026-11-06 with the page-fetch tool; the quote column records a short excerpt actually present on that official page. Only government sources (plus the repository of record for repository facts) are used. Secondary commercial calculators and blogs are excluded; where they disagreed with the official rate, the disagreement is logged on <a href="flagged.html#F14">F14</a>.</p>
<p>For manual review, open the linked title, search for the quoted phrase, and compare it with the corresponding row on the <a href="laws.html">Laws & Rates</a> page.</p>
</section>
{table(['ID', 'Agency', 'Level', 'Title / official link', 'Verbatim quote checked', 'Notes'], rows, 'Official source register — every row links to an official site')}
{callout('Official publisher note', '<p>The Rent Board states that its online copy of the Rent Ordinance is provided for public convenience and that American Legal is the official publisher of the San Francisco Administrative Codes. ' + src_links(['S08']) + '</p>')}
"""
    write("pages/sources.html", page("Official Sources", "All official sources used, with verbatim quotes and links for manual review.", body, "../", "Official Sources"))


def build_flagged() -> None:
    rows = []
    for f in DATA["flags"]:
        rows.append([
            f'<span class="mono">{e(f["id"])}</span>',
            e(f["title"]),
            e(f["detail"]),
            f'<span class="pill pill-warn">{e(f["status"])}</span>',
            src_links(f["source_ids"]),
            e(f["action"]),
        ])
    case_rows = [
        [e(c["unit"]), e(c["field"]), e(c["user_supplied"]), "", src_links([c["source_id"]]), f'<span class="mono">{e(c["flag_id"])}</span>']
        for c in CASE
    ]
    body = f"""
<section class="panel danger"><h2>Flagged for Review</h2>
<p>Everything on this page is published for the user to review after the site goes live. Per the project rule, values that could not be confirmed from an official source are left <strong>blank</strong> in verified columns; they are never inferred or filled in. These items are <strong>needs review</strong> and do not block the site build, the pull request, or the merge.</p>
</section>
<h2>Irregularities, gaps, and conflicts</h2>
{table(['ID', 'Item', 'Detail', 'Status', 'Official source links', 'Action for reviewer'], rows, 'Flagged for Review — official source links on every row', row_ids=[f["id"] for f in DATA["flags"]])}
<h2>Unverified case values (blank verified column)</h2>
<p class="note">Dates and amounts are retained exactly as supplied; no official source confirms them, so the verified-value column is empty on every row.</p>
{table(['Unit', 'Field', 'User-supplied value', 'Verified value', 'Governing official rule', 'Flag'], case_rows, 'Unverified case values — verified values blank')}
{callout('Illustrative dollar figures', '<p>Arithmetic illustrations derived from the user-supplied rents and official percentages are on <a href="analysis.html">Analysis & Scenarios</a> and are flagged as <a href="#F20">F20</a>. ' + src_links(['S02', 'S04', 'S29']) + '</p>', 'warn')}
"""
    write("pages/flagged.html", page("Flagged for Review", "Irregularities, unverified values, and gaps — each with official source links. Needs review does not block the merge.", body, "../", "Flagged for Review"))


def build_repo() -> None:
    rows = [
        ["Initial repository state", "Only README.md ('# RentincreaseSF1') at commit b2a2caf; no COORDINATION.md, site, data, or verification tooling existed to review line by line.", '<a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1" target="_blank" rel="noopener noreferrer">S42</a>'],
        ["COORDINATION.md created", "This session created the shared task board, claimed a scope, committed and pushed the claim immediately, then rebased onto main and preserved the earlier boards.", '<a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1/blob/main/COORDINATION.md" target="_blank" rel="noopener noreferrer">S42</a>'],
        ["Parallel session scopes", "Three other sessions merged PRs to main while this research was underway; their scopes (docs/**, site/**, research/**, data/*.csv, tools/**, workflows, root index.html) are preserved and not edited here.", '<a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1/branches" target="_blank" rel="noopener noreferrer">S42</a>'],
        ["Merge conflict resolution", "An add/add conflict in COORDINATION.md was resolved by keeping main's board verbatim and appending this session's section; no other session's work was discarded.", '<a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1/blob/main/COORDINATION.md" target="_blank" rel="noopener noreferrer">S42</a>'],
        ["GitHub Pages configuration", "Repository settings show legacy publishing from main at root '/', with root index.html redirecting to docs/index.html; this dashboard is live at /dashboard/.", '<a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1/settings/pages" target="_blank" rel="noopener noreferrer">S42</a>'],
        ["Privacy scan", "No real tenant names, initials, or street address are published anywhere in this dashboard; placeholder labels are used throughout.", '<a href="https://www.sf.gov/rent-board-housing-inventory" target="_blank" rel="noopener noreferrer">S13</a>'],
        ["Verification gate", "dashboard/verify.py re-checks data, source links, blank verified values, arithmetic, internal links, navigation, and privacy; build.py regenerates all pages from the single data registry.", '<a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1" target="_blank" rel="noopener noreferrer">S42</a>'],
    ]
    body = f"""
<section class="panel"><h2>Repository review, line by line</h2>
<p>The initial checkout contained a single README.md. There were no data tables, no legal values, and no site to verify; the work therefore started from official sources rather than from repository content. The shared board did not exist and was created, claimed, and pushed before implementation.</p>
<p>While research was in progress, other sessions merged work to <code>main</code>. This session ran <code>git pull --rebase origin main</code>, resolved the COORDINATION.md conflict without discarding their content, and moved its own scope into the disjoint <code>dashboard/**</code> directory. No file owned by another session is edited by this session; a request for a navigation link is logged in COORDINATION.md instead.</p>
<p>The site is generated from <code>dashboard/data/site_data.json</code> by <code>dashboard/build.py</code> and checked by <code>dashboard/verify.py</code>. Both are Python standard library only; no build service or external dependency is required.</p>
</section>
<h2>Review log</h2>
{table(['Topic', 'Finding', 'Source / link'], rows, 'Repository review findings — each row has a source link')}
<h2>Commands for manual review</h2>
<pre><code>cd dashboard
python3 build.py
python3 verify.py
cd .. &amp;&amp; git status --short</code></pre>
{callout('Flagged items', '<p>Repository-related flags: <a href="flagged.html#F15">F15</a> (initial repo state), <a href="flagged.html#F16">F16</a> (overlapping claims), <a href="flagged.html#F18">F18</a> (anonymization), and <a href="flagged.html#F21">F21</a> (raw tenant initials found in published files of other sessions). All ' + str(len(FLAGS)) + ' flags are on <a href="flagged.html">Flagged for Review</a>.</p>', 'warn')}
"""
    write("pages/repo.html", page("Repo Review", "Repository inspection, coordination notes, conflicts, and verification commands, with links for manual review.", body, "../", "Repo Review"))


def build_markdown() -> None:
    lines = [
        "# Official source register — line-by-line verification",
        "",
        f"Compiled {DATA['meta']['compiled_on']} by `{DATA['meta']['compiled_by']}`. Each entry below was fetched and read directly; the quote is a short verbatim excerpt from the linked official page. {DATA['meta']['legal_status']}",
        "",
        "| ID | Agency | Level | Title / official link | Verbatim quote checked | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for s in DATA["sources"]:
        q = s["quote"].replace("|", "\\|")
        n = s["notes"].replace("|", "\\|")
        t = s["title"].replace("|", "\\|")
        lines.append(f"| {s['id']} | {s['agency']} | {s['level']} | [{t}]({s['url']}) | {q} | {n} |")
    lines += ["", "## Verification rule", "", DATA["meta"]["verification"], "", "## Privacy rule", "", DATA["meta"]["privacy"]]
    write("SOURCES.md", "\n".join(lines) + "\n")

    research = [
        "# Research findings — line by line",
        "",
        f"Compiled {DATA['meta']['compiled_on']}. Every finding below maps to a source in [SOURCES.md](SOURCES.md) and is published with a source link on the site. {DATA['meta']['legal_status']}",
        "",
    ]
    grouped = defaultdict(list)
    for f in FACTS:
        grouped[f["category"]].append(f)
    for cat in sorted(grouped):
        research += [f"## {cat}", "", "| ID | Level | Topic | Verified value | Effective | Official source |", "|---|---|---|---|---|---|"]
        for f in grouped[cat]:
            s = SOURCES[f["source_id"]]
            val = f["value"].replace("|", "\\|")
            research.append(f"| {f['id']} | {f['level']} | {f['topic']} | {val} | {f['effective']} | [{s['id']} — {s['title']}]({s['url']}) |")
        research.append("")
    research += [
        "## Questions answered",
        "",
        "1. **Reasonable / normal increase under local, state, and federal law.** The published local AGA is 1.6% for March 1, 2026 – February 28, 2027 (S02, S03, S04); the state AB 1482 cap for the SF area is 8.8% for August 1, 2026 – July 31, 2027 but does not displace the more protective local cap (S27, S28); no federal numeric cap for private unsubsidized housing was confirmed and the value is left blank (S39, S37, S38).",
        "2. **Corporate vs individual owners.** Official sources document DOJ allegations about shared pricing algorithms (S35, S36), SF's algorithmic-device ban (S10, S26), California AB 325 (S34), and rules that apply to all owners regardless of size (S13, S09). No official comparative practice dataset was found; that gap is flagged (F11).",
        "3. **Correct notice and reasonable reasons.** 30-day written notice, 90 days above 10%, +5 days if mailed, with the content required by SF.gov, §37.3(b), Rule 4.10, and Civil Code §827 (S01, S09, S12, S29, S05). Petition-based grounds are the six official categories (S14, S15, S16); general market conditions are not an official standalone ground (F19).",
        "4. **Tenant-lawyer review.** A tenant can challenge an increase at no charge with no time limit (S18, S41); free counseling, an official referral listing, and Right to Counsel for eviction proceedings are documented (S23, S22, S25). The compliance checklist on the site maps each review item to an official source.",
        "5. **One unit or both.** No official source requires both units to be increased or provides a discrimination safe harbor (F08). The rules are per unit (S01, S09, S13), no rule requires raising rent (S12), and fair-housing / disparate-impact rules apply (S37, S33, S38, S11). A uniform documented objective policy is a recommendation for counsel, not a verified legal rule.",
        "",
        "## Flagged items",
        "",
    ]
    for f in DATA["flags"]:
        urls = ", ".join(f"[{sid}]({SOURCES[sid]['url']})" for sid in f["source_ids"])
        research.append(f"- **{f['id']} — {f['title']}** ({f['status']}). {f['detail']} Sources: {urls}. Action: {f['action']}")
    write("RESEARCH.md", "\n".join(research) + "\n")

    summary = f"""# Executive summary — anonymized published version

Compiled {DATA['meta']['compiled_on']}. {DATA['meta']['privacy']} {DATA['meta']['legal_status']}

## Purpose

Collect, organize, and analyze a full list of requirements for two rent-controlled residential units in a San Francisco 94122-area building that the user says was built in 1940. Real tenant identifiers are not included in this public repository; placeholder labels are used.

## Case facts (user-supplied, unverified)

| Unit | Field | User-supplied value | Verified value |
|---|---|---|---|
"""
    for c in CASE:
        summary += f"| {c['unit']} | {c['field']} | {c['user_supplied']} | |\n"
    summary += f"""
## Bottom line

- The ordinary lawful annual increase for a covered, licensed unit is **1.6% of base rent**, effective March 1, 2026 – February 28, 2027, once every 12 months, with 30 days' written notice (90 days above 10%; +5 days if mailed). Sources: [S01]({SOURCES['S01']['url']}), [S02]({SOURCES['S02']['url']}), [S29]({SOURCES['S29']['url']}), [S13]({SOURCES['S13']['url']}).
- California's AB 1482 cap for the San Francisco area is 8.8% for August 1, 2026 – July 31, 2027, but official state and city guidance says the more protective local rule applies to units covered by the SF Rent Ordinance. Sources: [S27]({SOURCES['S27']['url']}), [S28]({SOURCES['S28']['url']}).
- No federal numeric rent-increase cap for private unsubsidized housing was confirmed from an official source; the value is blank and flagged. Sources: [S39]({SOURCES['S39']['url']}), [S37]({SOURCES['S37']['url']}), [S38]({SOURCES['S38']['url']}).
- Any increase can be challenged by a tenant before a Rent Board Administrative Law Judge at no charge with no time limit. Sources: [S18]({SOURCES['S18']['url']}), [S41]({SOURCES['S41']['url']}).
- No official source was found requiring both units to be raised or providing a discrimination safe harbor; a uniform, documented, objective policy is recommended for tenant-lawyer review. Sources: [S12]({SOURCES['S12']['url']}), [S37]({SOURCES['S37']['url']}), [S33]({SOURCES['S33']['url']}).

## Irregularities

{len(FLAGS)} items are published on the site's Flagged for Review page with official source links. They include unverified building coverage, Unit A's occupancy change and anniversary ambiguity, Unit B's missing rent history, missing license/notice information, conflicting secondary-source percentages, and the absence of a confirmed federal cap. Flagged items do not block the build or merge.

## Deliverables

- `dashboard/index.html` — landing dashboard
- `dashboard/pages/**` — subpages by category, all with source-linked tables
- `dashboard/data/site_data.json` — single verified data registry
- `dashboard/SOURCES.md`, `dashboard/RESEARCH.md` — line-by-line manual-review documents
- `dashboard/build.py`, `dashboard/verify.py` — generator and verification gate
"""
    write("EXECUTIVE_SUMMARY.md", summary)

    readme = """# Independent verification dashboard

This directory is the file scope of session `arena/dd1caa16-rentincreasesf1`. It is
deliberately disjoint from `docs/**`, `site/**`, `research/**`, `data/*.csv`,
`tools/**`, `scripts/**`, `.github/workflows/**`, root `index.html`, and
`README.md`, which are owned by other sessions.

```
python3 build.py     # regenerate index.html and pages/** from data/site_data.json
python3 verify.py    # line-by-line data, source-link, link, nav, arithmetic, privacy checks
```

GitHub Pages serves this dashboard at `https://kanlerxz87-cyber.github.io/RentincreaseSF1/dashboard/`.
No build service, network access, or third-party Python package is required.
"""
    write("README.md", readme)


def main() -> None:
    build_index()
    build_summary()
    build_laws()
    build_units()
    build_analysis()
    build_notice()
    build_owners()
    build_discrimination()
    build_review()
    build_sources()
    build_flagged()
    build_repo()
    build_markdown()
    print(f"Built dashboard: {len(SOURCES)} sources, {len(FACTS)} facts, {len(CASE)} case facts, {len(FLAGS)} flags, {len(SCENARIOS)} scenarios")


if __name__ == "__main__":
    main()
