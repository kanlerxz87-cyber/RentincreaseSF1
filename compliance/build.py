#!/usr/bin/env python3
"""Deterministic static site generator for the /compliance/ GitHub Pages suite."""
from __future__ import annotations

import html
import json
import pathlib
from dataclasses import dataclass
from typing import Sequence

COMPLIANCE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = COMPLIANCE_DIR / "data"


@dataclass(frozen=True)
class Cell:
    text: str
    is_html: bool = False
    classes: str = ""
    row_id: str = ""


def h(val: str) -> str:
    return html.escape(val, quote=True)


def raw(markup: str, classes: str = "") -> Cell:
    return Cell(text=markup, is_html=True, classes=classes)


def num(val: str) -> Cell:
    return Cell(text=h(val), is_html=True, classes="num")


def blank_cell() -> Cell:
    return Cell(text="", is_html=True, classes="blank-unverified")


def badge(label: str, kind: str = "verified") -> str:
    return f'<span class="badge badge-{h(kind)}">{h(label)}</span>'


NAV_ITEMS: list[tuple[str, str, str]] = [
    ("index.html", "Overview & License Summary", ""),
    ("licensing.html", "Rent Board License Guide", ""),
    ("units-and-rates.html", "Units 1 & 2 · 94122 Caps", ""),
    ("notice-and-reasons.html", "Notice & Lawful Reasons", ""),
    ("practices.html", "Corporate vs. Individual", ""),
    ("fair-housing.html", "1 Unit vs. Both Units", ""),
    ("lawyer-scrutiny.html", "Tenant-Lawyer Audit", ""),
    ("repo-audit.html", "Repo Audit", ""),
    ("flagged.html", "Flagged for Review", "nav-flagged"),
    ("sources.html", "Official Sources (37)", ""),
]


def load_inputs() -> tuple[dict, dict[str, dict], list[dict]]:
    site_data = json.loads((DATA_DIR / "site_data.json").read_text(encoding="utf-8"))
    sources_list = json.loads((DATA_DIR / "sources.json").read_text(encoding="utf-8"))
    sources_by_id = {item["id"]: item for item in sources_list}
    repo_audit = json.loads((DATA_DIR / "repo_audit.json").read_text(encoding="utf-8"))
    return site_data, sources_by_id, repo_audit


def render_source_links(source_ids: Sequence[str], sources_by_id: dict[str, dict]) -> str:
    if not source_ids:
        raise ValueError("Every table row must cite at least one official source_id")
    parts: list[str] = []
    for sid in source_ids:
        if sid not in sources_by_id:
            raise KeyError(f"Unknown source_id: {sid}")
        src = sources_by_id[sid]
        parts.append(
            f'<div><a class="src-ext" href="{h(src["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{h(src["short"])} &#8599;</a> '
            f'<a class="src-ref" href="sources.html#{h(sid)}">[{h(sid)}]</a></div>'
        )
    return "".join(parts)


def render_table(
    table_id: str,
    headers: Sequence[str],
    rows: Sequence[tuple[Sequence[Cell | str], Sequence[str], str]],
    sources_by_id: dict[str, dict],
    filter_placeholder: str | None = None,
) -> str:
    all_headers = list(headers) + ["Official Source"]
    th_html = "".join(f'<th scope="col">{h(col)}</th>' for col in all_headers)
    body_rows: list[str] = []
    for cells, sids, tr_id in rows:
        if len(cells) != len(headers):
            raise ValueError(
                f"Table {table_id}: expected {len(headers)} cells, got {len(cells)}"
            )
        td_parts: list[str] = []
        for cell in cells:
            if isinstance(cell, Cell):
                cls = f' class="{h(cell.classes)}"' if cell.classes else ""
                inner = cell.text if cell.is_html else h(cell.text)
                td_parts.append(f"<td{cls}>{inner}</td>")
            else:
                td_parts.append(f"<td>{h(cell)}</td>")
        src_html = render_source_links(sids, sources_by_id)
        td_parts.append(f'<td class="src-cell">{src_html}</td>')
        id_attr = f' id="{h(tr_id)}"' if tr_id else ""
        body_rows.append(f"<tr{id_attr}>{''.join(td_parts)}</tr>")

    filter_html = ""
    if filter_placeholder:
        filter_html = (
            f'<div class="filter-bar">'
            f'<input type="search" class="filter-input" data-table-filter="{h(table_id)}" '
            f'placeholder="{h(filter_placeholder)}" aria-label="{h(filter_placeholder)}">'
            f'<span class="filter-count" data-filter-count="{h(table_id)}">'
            f"Showing {len(rows)} of {len(rows)} rows</span>"
            f"</div>"
        )

    return (
        f"{filter_html}"
        f'<div class="table-wrap">'
        f'<table class="data-table" id="{h(table_id)}">'
        f"<thead><tr>{th_html}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        f"</table>"
        f"</div>"
    )


def page_shell(current_file: str, page_title: str, hero_title: str, hero_desc: str, body_html: str, meta: dict) -> str:
    nav_links: list[str] = []
    for fname, label, extra_cls in NAV_ITEMS:
        curr = ' aria-current="page"' if fname == current_file else ""
        cls = f' class="{h(extra_cls)}"' if extra_cls else ""
        nav_links.append(f'<a href="{h(fname)}"{cls}{curr}>{h(label)}</a>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{h(page_title)} — {h(meta["edition"])}</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <div class="top-banner">
    <div class="top-banner-inner">
      <span><strong>Verified Live:</strong> {h(meta["verified_date"])} (37/37 primary <code>.gov</code> &amp; City-portal sources) · <strong>Privacy:</strong> 100% Anonymized Placeholders Only</span>
      <span><a href="../index.html">&larr; Canonical Repository Root</a> &middot; <a href="EXECUTIVE_SUMMARY.md">Executive Summary (.md)</a> &middot; <a href="flagged.html">Flagged for Review (26)</a></span>
    </div>
  </div>
  <header class="site-header">
    <div class="header-inner">
      <div class="eyebrow">{h(meta["neighborhood"])}</div>
      <div class="site-title">San Francisco Rent Increase Compliance &amp; Verification Dashboard</div>
      <p class="site-subtitle">Line-by-line statutory analysis for an individual (non-corporate) two-unit property owner — zero inferred facts, every row linked to an official government source.</p>
      <nav class="nav-bar" aria-label="Dashboard sections">
        {"".join(nav_links)}
      </nav>
    </div>
  </header>
  <main class="container" id="main-content">
    <section class="page-hero">
      <h1>{h(hero_title)}</h1>
      <p>{h(hero_desc)}</p>
    </section>
    {body_html}
  </main>
  <footer class="site-footer">
    <div class="footer-inner">
      <div><strong>Privacy &amp; Anonymization Guarantee:</strong> {h(meta["privacy_statement"])}</div>
      <div><strong>Scope &amp; Legal Notice:</strong> {h(meta["legal_disclaimer"])}</div>
      <div><a href="index.html">Overview</a> &middot; <a href="licensing.html">License Guide</a> &middot; <a href="units-and-rates.html">Units 1 &amp; 2 Math</a> &middot; <a href="notice-and-reasons.html">Notice Rules</a> &middot; <a href="practices.html">Corporate vs. Individual</a> &middot; <a href="fair-housing.html">1 Unit vs. Both</a> &middot; <a href="lawyer-scrutiny.html">Tenant-Lawyer Audit</a> &middot; <a href="repo-audit.html">Repo Audit</a> &middot; <a href="flagged.html">Flagged for Review</a> &middot; <a href="sources.html">Official Sources</a></div>
    </div>
  </footer>
  <script src="assets/app.js" defer></script>
</body>
</html>
"""


def build_index(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    scen_rows = []
    for s in site_data["scenarios"]:
        exp_badge = (
            badge("Pending-Bill Watch", "danger")
            if s["id"] == "U2-B"
            else badge("Conditional Scenario", "conditional")
        )
        scen_rows.append(
            (
                [
                    raw(f"<strong>{h(s['id'])}</strong><br>{h(s['unit'])}"),
                    f"{s['household']} — {s['label']}",
                    num(f"${s['base_rent']}"),
                    num(f"{s['annual_pct']}% + {s['banked_pct']}% = {s['total_pct']}%"),
                    num(f"+${s['increase_amt']}"),
                    num(f"${s['new_rent']}"),
                    f"Eff. {s['effective_date']} · Personal <= {s['personal_by']} ({s['personal_notice_days']}d) · CA Mail <= {s['ca_mail_by']} ({s['ca_mail_days']}d)",
                    raw(f"{exp_badge}<br><small>{h(s['gate_summary'])}</small>"),
                ],
                [s["source_id"], "CS19", "CS20"],
                f"scen-{s['id']}",
            )
        )

    case_rows = []
    for c in site_data["case_inputs"]:
        case_rows.append(
            (
                [
                    c["id"],
                    c["category"],
                    c["item"],
                    c["brief_input"],
                    blank_cell() if c["official_confirmed"] == "" else c["official_confirmed"],
                    raw(badge(c["status"], "flagged")),
                ],
                [c["source_id"]],
                c["id"],
            )
        )

    body = f"""
    <section class="callout callout-forefront">
      <h2>Forefront Answer — Must an Individual Owner (Not a Corporation) Get a Rent Board License Before Notifying Tenants?</h2>
      <p><strong>YES for the SF Rent Board Rent Increase License — NO incorporation required.</strong> Under <a href="{h(sources['CS01']['url'])}" target="_blank" rel="noopener noreferrer">SF Administrative Code &sect;37.15</a> and <a href="{h(sources['CS02']['url'])}" target="_blank" rel="noopener noreferrer">SF Rent Board Housing Inventory guidance</a>, <strong>every</strong> residential owner in San Francisco (including a natural-person owner of a 2-unit 1940 building; 1&ndash;9 unit buildings became subject March 1, 2023) must report unit occupancy and rent range annually on the free <a href="{h(sources['CS03']['url'])}" target="_blank" rel="noopener noreferrer">SF Rent Board Portal (<code>portal.sfrb.org</code>)</a>. Reporting a unit as tenant-occupied <strong>automatically generates the Rent Increase License</strong> at zero cost.</p>
      <p><strong>Exact Timing &amp; Challenge-Proof Sequence:</strong> The statutory hard bar is having an active license on the <strong>effective date</strong> of the rent increase (during noncompliance, your license is suspended and suspended months are permanently uncollectible under &sect;37.15(e)). However, because Housing Inventory records are public and tenants can check your status on <code>portal.sfrb.org</code> the day they receive your notice, <strong>complete Housing Inventory reporting and save dated PDF/screenshot proof of both active licenses BEFORE serving any notice</strong>. You do <em>not</em> send annual/banked notices to the Rent Board for approval, and you do <em>not</em> confuse this license with the separate <a href="{h(sources['CS04']['url'])}" target="_blank" rel="noopener noreferrer">SF Treasurer Business Registration Certificate</a> (from which a single &lt;4-unit residential building is conditionally exempt). <a href="licensing.html"><strong>Read the full beginner step-by-step guide &rarr;</strong></a></p>
    </section>

    <section class="callout callout-alert">
      <h3>Posted November 9, 2026 — Official SF Rent Board Alert on Proposed File No. 261020 (Pending Committee Action — NOT Law)</h3>
      <p>Live verification on <strong>2026-11-10</strong> confirms that on <strong>November 9, 2026</strong>, the SF Rent Board added a formal warning box to <a href="{h(sources['CS09']['url'])}" target="_blank" rel="noopener noreferrer">Learn About Rent Increases</a> and <a href="{h(sources['CS10']['url'])}" target="_blank" rel="noopener noreferrer">Banked Rent Increases</a>: Board of Supervisors <a href="{h(sources['CS12']['url'])}" target="_blank" rel="noopener noreferrer">File No. 261020</a> (still <em>Pending Committee Action</em> in the Land Use and Transportation Committee as of <code>2026-11-10</code> — <strong>not enacted law</strong>) would cap combined <strong>Banked + Capital Improvement</strong> increases at <strong>10% per year</strong> of the lowest prior-12-month base rent through December 31, 2029 (<a href="{h(sources['CS13']['url'])}" target="_blank" rel="noopener noreferrer">Legislative Digest Ver. 1</a>). <strong>Crucially, if enacted as currently drafted, it would apply retroactively to banked rent increases noticed on or after September 15, 2026</strong> (preserving excess banked % for January 1, 2030+). Unit 2's full 6-year conditional banked catch-up (<code>11.5%</code> banked + <code>1.6%</code> annual = <code>13.1%</code>) sits <code>1.5%</code> above that proposed 10% banked ceiling, so we model both annual-only (<code>U2-A</code>) and a 10.0%-banked risk-mitigated option (<code>U2-C</code>) alongside enacted-law <code>U2-B</code>.</p>
    </section>

    <div class="kpi-grid">
      <div class="kpi-card">
        <span class="kpi-label">2026&ndash;27 SF Annual Allowance</span>
        <span class="kpi-value">1.6%</span>
        <span class="kpi-note">Effective Mar 1, 2026 &ndash; Feb 28, 2027 (<a href="sources.html#CS08">Form 571</a>). State AB 1482 (8.8%) is inapplicable.</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Individual-Owner License Gate</span>
        <span class="kpi-value">Mandatory · $0</span>
        <span class="kpi-note">Report both units on <code>portal.sfrb.org</code> before notice/effective date (<a href="licensing.html">&sect;37.15 Guide</a>).</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Conditional Routine Annual Scenarios</span>
        <span class="kpi-value">+$63.92 / +$50.40</span>
        <span class="kpi-note">Scenario math only on $3,995 (U1) &amp; $3,150 (U2); subject to lease &amp; ledger verification.</span>
      </div>
      <div class="kpi-card">
        <span class="kpi-label">Unverified Private Inputs</span>
        <span class="kpi-value">16 Blank Cells</span>
        <span class="kpi-note">Zero inferred facts: unconfirmed official cells are left blank on <a href="flagged.html">Flagged for Review</a>.</span>
      </div>
    </div>

    <section class="section-card">
      <div class="section-header">
        <h2>Explore Categorized Compliance Subpages</h2>
      </div>
      <div class="card-links">
        <a class="card-link" href="licensing.html"><strong>1. Rent Board License &amp; Step-by-Step Guide</strong><span>Beginner walkthrough of &sect;37.15 Housing Inventory filing, Rent Board Fee ($59/$29.50), and Tax Collector &lt;4-unit carve-out.</span></a>
        <a class="card-link" href="units-and-rates.html"><strong>2. Units 1 &amp; 2 Math, 94122 Caps &amp; Form 571</strong><span>Local/State/Federal rules, Unit 1 &sect;6.14/Costa-Hawkins partial-occupancy rules, Unit 2 banking, and all 46 Form 571 periods.</span></a>
        <a class="card-link" href="notice-and-reasons.html"><strong>3. Tenant Notice Protocol &amp; Lawful Reasons</strong><span>Civil Code &sect;827 + CCP &sect;1013(a) service calendar, &sect;&sect;4.10/4.12 itemization, and lawful vs. prohibited stated reasons.</span></a>
        <a class="card-link" href="practices.html"><strong>4. Corporate vs. Individual Landlords</strong><span>2024 HUD/Census RHFS empirical benchmarks, SF &sect;37.10C algorithmic ban, and U.S. DOJ RealPage consent-decree bounds.</span></a>
        <a class="card-link" href="fair-housing.html"><strong>5. Raise One Unit vs. Both Units</strong><span>FHA, FEHA &sect;12955, Unruh &sect;51, SF &sect;37.10B, and &sect;1942.5 retaliation analysis for neutral unit selection.</span></a>
        <a class="card-link" href="lawyer-scrutiny.html"><strong>6. Tenant-Lawyer 15-Point Audit &amp; 94122 Clinics</strong><span>How SF tenant advocates audit notices line by line, plus official Sunset 94122 referral directory.</span></a>
        <a class="card-link" href="repo-audit.html"><strong>7. Line-by-Line Repository Audit</strong><span>Audit of <code>main</code> against live 2026-11-10 government sources with clickable verification links.</span></a>
        <a class="card-link" href="flagged.html"><strong>8. Flagged for Review (26 Open Items)</strong><span>16 blank-cell unverified private inputs + 10 official-source &amp; repository cautions.</span></a>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>Conditional Unit 1 &amp; Unit 2 Rent Increase Scenarios (Scenario Arithmetic Only — Not Certified Lawful Maxima)</h2>
      </div>
      <p class="section-lead">Every dollar figure below is exact non-compounded, non-rounded multiplication on the owner-brief inputs (<code>$3,995.00</code> and <code>$3,150.00</code>). Do not serve notice until every unresolved private gate in the right-hand column is verified from the signed leases, rent ledgers, and Rent Board Portal.</p>
      {render_table(
          "overview-scenarios",
          [
              "Scenario",
              "Anonymized Household & Option",
              "Scenario Base",
              "Annual + Banked",
              "Monthly Increase",
              "Illustrative New Rent",
              "Illustrative Service Deadlines",
              "Status & Unresolved Gates",
          ],
          scen_rows,
          sources,
      )}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>Anonymized Owner-Brief Inputs &amp; Blank Official Confirmation Register</h2>
      </div>
      <p class="section-lead">Per strict zero-hallucination rules, any value that cannot be confirmed from a public official government record is left <strong>physically blank</strong> in the <em>Official Confirmed Value</em> column and flagged for owner verification.</p>
      {render_table(
          "overview-case-inputs",
          [
              "Flag ID",
              "Category",
              "Fact / Parameter",
              "Owner-Brief Scenario Input (Anonymized)",
              "Official Confirmed Value",
              "Verification Status",
          ],
          case_rows,
          sources,
          "Filter 16 case inputs by unit, license, lease, repair, or rate...",
      )}
    </section>
    """
    return page_shell(
        "index.html",
        "Executive Summary & Overview",
        "Executive Summary — Outer Sunset 94122 Two-Unit Rent Increase Compliance",
        "Forefront Rent Board License guidance for an individual property owner, conditional Unit 1 & Unit 2 calculations under San Francisco, California, and Federal law, and transparent blank-cell tracking of every unverified private input.",
        body,
        meta,
    )


def build_licensing(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    qa_rows = [
        (
            [
                "Q1",
                "I own this 2-unit building as an individual (not a corporation or LLC). Must I still get a Rent Board license?",
                "Yes. SF Admin. Code §37.15 applies to all 'owners of residential dwelling units subject to this Chapter 37.' Buildings with 1–9 units became subject on March 1, 2023. There is zero corporate-form threshold or small-owner exemption.",
                raw(badge("Verified Rule", "verified")),
            ],
            ["CS01", "CS02"],
            "lic-q1",
        ),
        (
            [
                "Q2",
                "Is the Rent Increase License a discretionary application or hearing that can be denied?",
                "No. Reporting into the Housing Inventory on portal.sfrb.org is free, 24/7, and self-service. Once you report a unit as tenant-occupied in substantial compliance with §37.15(b)(2), the Portal automatically generates your Rent Increase License.",
                raw(badge("Verified Rule", "verified")),
            ],
            ["CS02", "CS03"],
            "lic-q2",
        ),
        (
            [
                "Q3",
                "Must the license be active BEFORE I serve the rent-increase notice, or BEFORE the effective date?",
                "Statutory hard gate: before the effective date ('your rent increase notice will not be enforceable without having a rent increase license on the effective date of the notice'). Best-practice sequence: obtain and screenshot the active license BEFORE serving notice, because tenants can verify your Portal status immediately upon receiving notice.",
                raw(badge("Verified Distinction", "verified")),
            ],
            ["CS01", "CS02"],
            "lic-q3",
        ),
        (
            [
                "Q4",
                "What happens if I serve a notice while unlicensed and file the Housing Inventory months later?",
                "Under §37.15(e), your authority to impose §37.3(a)(1)–(2) annual or banked increases is 'temporarily suspended' during noncompliance. Filing terminates the suspension prospectively only — tenants are NEVER obligated to pay the increase for any month during suspension.",
                raw(badge("Verified Penalty", "danger")),
            ],
            ["CS01"],
            "lic-q4",
        ),
        (
            [
                "Q5",
                "Do I attach a copy of the Rent Increase License to the tenant's notice, or mail the notice to the Rent Board?",
                "No to both. SF.gov states: 'The rent increase license does not need to be included with your rent increase notice,' and annual/banked increases 'do not have to be approved by the Rent Board.' Keep dated copies of both the license and notice in your permanent unit file.",
                raw(badge("Verified Rule", "verified")),
            ],
            ["CS02", "CS10"],
            "lic-q5",
        ),
        (
            [
                "Q6",
                "What if I missed the March 1 annual Housing Inventory deadline?",
                "You can submit late online 24/7, and the Rent Board 'does not assess monetary penalties for filing after the deadline.' However, the Rent Board may mail tenants a Notice of Owner Noncompliance, and no annual/banked increase can take effect until you file.",
                raw(badge("Verified Rule", "verified")),
            ],
            ["CS02"],
            "lic-q6",
        ),
        (
            [
                "Q7",
                "Can my tenants or their lawyer see whether I completed the Housing Inventory?",
                "Yes. SF.gov explicitly advises tenants they can search portal.sfrb.org to check whether their landlord's Rent Increase License is up to date, and notes that Housing Inventory submissions are public records.",
                raw(badge("Verified Rule", "verified")),
            ],
            ["CS02", "CS03"],
            "lic-q7",
        ),
        (
            [
                "Q8",
                "Do I also need a San Francisco Business Registration Certificate from the Treasurer & Tax Collector?",
                "Separate question: the Business Registration Certificate is a City tax registration unrelated to Rent Ordinance rent-increase validity. On the reported facts (one residential building with 2 units, i.e., <4 units), Treasurer guidance states rental income from 'one residential structure consisting of fewer than four units' does NOT, 'by reason of that fact alone,' require registration — unless you have other SF business activity, payroll expense, or short-term rentals.",
                raw(badge("Conditional Carve-Out (CF-04)", "conditional")),
            ],
            ["CS04", "CS05"],
            "lic-q8",
        ),
    ]

    steps_rows = [
        (
            [
                "Step 1",
                "Gather per-unit facts before opening the Portal",
                "For Unit 1 and Unit 2: owner/habitability contact name, business address, phone, email; Business Registration Number ('if any' — leave blank if exempt under <4-unit rule); approx. sq. ft. in 250 sq. ft. increments; bedroom/bathroom counts; current occupancy start date; current base rent in $250 increments; utilities included in base rent.",
            ],
            ["CS01", "CS02"],
            "step-1",
        ),
        (
            [
                "Step 2",
                "Sign in or register at portal.sfrb.org",
                "Create/open your owner account on the official SF Rent Board Portal (call SF 311 at 415-701-2311 if you need help linking your parcel/APN PIN).",
            ],
            ["CS02", "CS03"],
            "step-2",
        ),
        (
            [
                "Step 3",
                "Use the 'Individual Unit' form (skip the 5+ unit Excel template)",
                "SF.gov explicitly recommends the 'Individual Unit' online submission form rather than the bulk Excel template for properties with fewer than 5 residential units.",
            ],
            ["CS02"],
            "step-3",
        ),
        (
            [
                "Step 4",
                "Submit Unit 1 & Unit 2 reports under penalty of perjury",
                "Best-knowledge approximations are expressly permitted without penalty for square footage (250 sq. ft. bands) and occupancy start dates if exact historical records are unavailable.",
            ],
            ["CS01", "CS02"],
            "step-4",
        ),
        (
            [
                "Step 5",
                "Download & archive each unit's Rent Increase License PDF",
                "Confirm a distinct current license exists for Unit 1 and Unit 2 BEFORE serving any rent-increase notice, and calendar a re-check on the effective date plus annual renewal before March 1.",
            ],
            ["CS01", "CS02"],
            "step-5",
        ),
        (
            [
                "Step 6",
                "Update owner/manager contact details within 30 days of any change",
                "SF Admin. Code §37.15(c) requires updating unit contact information within 30 days of any change in owner or designated habitability manager name/contact details.",
            ],
            ["CS01"],
            "step-6",
        ),
    ]

    comp_rows = [
        (
            [
                "SF Rent Increase License (Housing Inventory)",
                "SF Rent Board (portal.sfrb.org)",
                "Mandatory for all SF residential units (1–9 units since Mar 1, 2023)",
                num("$0.00 (Free)"),
                "March 1 annually (late filing free, but required before increase effective date)",
                "DIRECT HARD GATE: Unlicensed annual/banked increases are suspended and uncollectible (§37.15(e)).",
            ],
            ["CS01", "CS02"],
            "reg-license",
        ),
        (
            [
                "Annual SF Rent Board Fee",
                "SF Rent Board (portal.sfrb.org)",
                "Mandatory per dwelling unit unless valid exemption approved (2027 exemption window closes Dec 14, 2026)",
                num("$59.00 / unit (2026–27)"),
                "March 1 annually (5%/mo late penalty starting Mar 2, max 15%)",
                "Separate from license & base rent: after full payment, 50% ($29.50) may be billed separately to tenants in occupancy on Nov 1 (penalties non-recoverable).",
            ],
            ["CS06"],
            "reg-fee",
        ),
        (
            [
                "SF Business Registration Certificate",
                "SF Office of the Treasurer & Tax Collector (sftreasurer.org)",
                "Conditionally NOT required if sole SF business is long-term rental of 1 residential structure with <4 units (triggered by other business, payroll, or short-term rental)",
                num("$0 if exempt"),
                "Within 30 days of commencing taxable business; renew by last day of Feb",
                "Tax registration only — does NOT issue or suspend the Rent Board Rent Increase License (confirm owner facts under CF-04).",
            ],
            ["CS04", "CS05"],
            "reg-brc",
        ),
    ]

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>1. Individual Property Owner Q&amp;A — Every Licensing Question Answered</h2>
      </div>
      <p class="section-lead">Clear, citation-backed answers explaining why individual ownership does not exempt you from the Rent Board Housing Inventory, and how to ensure your license cannot be challenged.</p>
      {render_table("licensing-qa", ["#", "Owner Question", "Verified Official Answer", "Rule Status"], qa_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Beginner Step-by-Step Filing Walkthrough (<code>portal.sfrb.org</code>)</h2>
      </div>
      <p class="section-lead">Follow these six steps in order before drafting or serving any rent-increase notice on Unit 1 or Unit 2.</p>
      {render_table("licensing-steps", ["Step", "Action", "Exact Portal Requirement & Statutory Detail"], steps_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>3. Three Distinct San Francisco Requirements — Do Not Mix Them Up</h2>
      </div>
      <p class="section-lead">Small individual owners frequently confuse the free Rent Increase License, the $59.00 per-unit Rent Board Fee, and the Treasurer's Business Registration Certificate. Never fold the $29.50 fee recovery into monthly base rent.</p>
      {render_table(
          "licensing-comparison",
          ["Requirement", "Issuing Agency", "Applies to Reported 2-Unit Individual Owner?", "2026–27 Cost", "Annual Deadline", "Effect on Rent Increase Validity"],
          comp_rows,
          sources,
      )}
    </section>
    """
    return page_shell(
        "licensing.html",
        "Rent Board License Guide",
        "Individual Owner Rent Board License & Step-by-Step Portal Guide",
        "Complete beginner walkthrough of SF Administrative Code §37.15 Housing Inventory reporting, Rent Increase License generation, the $59/$29.50 Rent Board Fee, and the <4-unit Business Registration Certificate carve-out.",
        body,
        meta,
    )


def build_units_and_rates(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    layer_rows = [
        (
            [
                "Local — SF Rent Ordinance (Admin. Code §37.3 & Form 571)",
                "CONTROLS BOTH UNITS (if 1940 C of O & non-exempt)",
                num("1.6% annual"),
                "Effective 3/1/2026–2/28/2027 (60% of Bay Area CPI-U; 7.0% statutory ceiling). Lawfully banked prior allowances may be added without compounding or rounding up.",
            ],
            ["CS07", "CS08", "CS09"],
            "layer-local",
        ),
        (
            [
                "Local — Proposed BOS File No. 261020 (Pending — NOT Law)",
                "WATCH FOR UNIT 2 BANKING >10%",
                num("10.0% banked cap (proposed)"),
                "Pending Committee Action on 2026-11-10. Per Nov 9, 2026 Rent Board notice & Leg Dig Ver1, if enacted as drafted it would cap Banked + Capital Improvement increases at 10%/yr of lowest prior-12-month base rent for notices >= Sept 15, 2026 through Dec 31, 2029 (preserving excess for Jan 1, 2030+).",
            ],
            ["CS10", "CS12", "CS13"],
            "layer-261020",
        ),
        (
            [
                "Local — ZIP 94122 'Normal Market Increase' Benchmark",
                "NO OFFICIAL .GOV BENCHMARK EXISTS",
                blank_cell(),
                "Flagged (CF-14): No government agency publishes a lawful or normal rent-increase norm by SF neighborhood/ZIP; commercial listing blogs are excluded.",
            ],
            ["CS08"],
            "layer-zip",
        ),
        (
            [
                "State — California Tenant Protection Act (AB 1482 / Civ. Code §1947.12)",
                "INAPPLICABLE TO SF RENT-CONTROLLED UNITS",
                num("8.8% (not applicable)"),
                "SF AB 1482 cap is 8.8% (5% + 3.8% CPI) for 8/1/2026–7/31/2027, but Civ. Code §1947.12(d)(3) & SF Rent Board guidance expressly exempt units subject to stricter SF Rent Ordinance caps.",
            ],
            ["CS22", "CS23"],
            "layer-ab1482",
        ),
        (
            [
                "State — Costa-Hawkins Act (Civ. Code §§1954.52–1954.53)",
                "BARS UNIT 1 VACANCY RESET",
                num("0% market reset"),
                "A 2-unit building on one parcel is not exempt as a single-family home; §1954.53(d)(3) bars market resets on partial occupancy changes while original Placeholder Tenant 1A remains.",
            ],
            ["CS16", "CS24"],
            "layer-costa",
        ),
        (
            [
                "Federal — Fair Housing Act (42 U.S.C. §3604)",
                "APPLIES TO ALL TERMS & CONDITIONS",
                raw("Non-discriminatory"),
                "No federal percentage cap for private unsubsidized housing (subsidy status unverified under CF-12), but prohibits discriminatory rent-increase selection or terms.",
            ],
            ["CS30", "CS36"],
            "layer-federal",
        ),
    ]

    scen_rows = []
    for s in site_data["scenarios"]:
        scen_rows.append(
            (
                [
                    s["id"],
                    f"{s['unit']} — {s['label']}",
                    num(f"${s['base_rent']}"),
                    num(f"{s['annual_pct']}%"),
                    num(f"{s['banked_pct']}%"),
                    num(f"{s['total_pct']}%"),
                    num(f"+${s['increase_amt']}"),
                    num(f"${s['new_rent']}"),
                    num(f"{s['retained_banked_pct']}%"),
                    s["pending_261020_exposure"],
                ],
                [s["source_id"], "CS08"],
                f"math-{s['id']}",
            )
        )

    u2_bank_rows = []
    for b in site_data["u2_banked_components"]:
        u2_bank_rows.append(
            (
                [
                    b["anniversary"],
                    b["rate_period"],
                    num(f"{b['pct']}%"),
                    num(f"+${b['dollar_on_3150']}"),
                    b["status"],
                ],
                [b["source_id"], "CS10"],
                f"u2-bank-{b['anniversary']}",
            )
        )
    u2_bank_rows.append(
        (
            [
                "Subtotal (6 Skipped Years) + Current 2026–27 Annual",
                "Banked 11.5% ($362.25) + Current 1.6% ($50.40)",
                num("13.1%"),
                num("+$412.65"),
                "Conditional enacted-law total -> $3,562.65 (Note: 2026-06-01 is NOT bankable before 2027-06-01 under Rule 4.12(a)).",
            ],
            ["CS08", "CS10", "CS11"],
            "u2-bank-total",
        )
    )

    occ_rows = [
        (
            [
                "Can Unit 1 rent be reset to market because 2 of 3 initial Feb. 1, 2025 tenants left by April 1, 2026?",
                "NO. Placeholder Tenant 1A (an original Feb. 1, 2025 occupant) remains in lawful possession. Both Rule §6.14 and Costa-Hawkins §1954.53(d)(3) bar market resets while any original occupant remains.",
                raw(badge("Prohibited Now", "danger")),
            ],
            ["CS16", "CS24"],
            "occ-1",
        ),
        (
            [
                "Can the owner add a roommate surcharge because Placeholder Tenant 1D moved in on April 1, 2026?",
                "NO. SF Admin. Code §37.3(a)(11)(A) and Rule §6.13 prohibit rent increases solely for adding an occupant, even if a written lease expressly allows an additional-occupant charge.",
                raw(badge("Prohibited", "danger")),
            ],
            ["CS07", "CS17"],
            "occ-2",
        ),
        (
            [
                "What if the April 1, 2026 document was a new 12-month fixed-term lease through March 31, 2027?",
                "CONTRACT GATE (CF-05): Under California law, rent cannot be raised mid-term during a fixed-term lease unless the lease expressly authorizes it. Inspect the signed April 1, 2026 agreement before serving any Feb. 1, 2027 notice.",
                raw(badge("Must Verify Lease (CF-05)", "flagged")),
            ],
            ["CS21"],
            "occ-3",
        ),
        (
            [
                "What matters later if Placeholder Tenant 1A eventually moves out, leaving only Placeholder Tenant 1D?",
                "Two distinct rules (CF-07 & CF-08): (1) Rule §6.14 allows an unlimited increase after the last original occupant vacates ONLY if a written 6.14 notice was served within a reasonable time (~60 days of actual knowledge, ~May 31, 2026; missing 60 days creates a rebuttable presumption of untimeliness). (2) Even without a 6.14 notice (§6.14(d)(2)), Costa-Hawkins §1954.53(d) applies when the last original occupant no longer permanently resides there — ONLY if Tenant 1D is a subtenant/assignee, NOT if Tenant 1D became a co-tenant via direct lease/addendum or direct rent acceptance.",
                raw(badge("Future Preservation Check", "conditional")),
            ],
            ["CS16", "CS17", "CS18"],
            "occ-4",
        ),
    ]

    rate_rows = []
    for r in site_data["rates"]:
        rate_rows.append(
            (
                [
                    f"{r['start']} to {r['end']}",
                    num(f"{r['pct']}%"),
                    r["note"],
                ],
                [r["source_id"]],
                f"rate-{r['start']}",
            )
        )

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>1. Local, State &amp; Federal Rent-Increase Rules for Outer Sunset 94122</h2>
      </div>
      <p class="section-lead">How San Francisco, California, and Federal statutes interact for two reported rent-controlled units in a 1940 building.</p>
      {render_table("jurisdiction-layers", ["Legal Layer & Authority", "Applicability to Units 1 & 2", "Verified Rate / Limit", "How It Operates"], layer_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Exact Conditional Math — Unit 1 ($3,995.00) &amp; Unit 2 ($3,150.00)</h2>
      </div>
      <p class="section-lead">All percentages are strictly additive (never compounded) and truncated/exact to the cent (never rounded up to the nearest dollar, per SF.gov &amp; Rule 4.12).</p>
      {render_table(
          "unit-scenarios-detail",
          [
              "ID",
              "Unit & Scenario",
              "Scenario Base",
              "Annual %",
              "Banked %",
              "Total %",
              "Monthly +$",
              "New Base Rent",
              "Remaining Banked %",
              "Pending File #261020 Exposure",
          ],
          scen_rows,
          sources,
      )}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>3. Unit 2 Year-by-Year Conditional Banking Ledger (Assuming Zero Increases Since June 1, 2019)</h2>
      </div>
      <p class="section-lead">Why 6 skipped anniversaries equal <code>11.5%</code> (<code>$362.25</code>) rather than 7: the initial <code>2.6%</code> period (<code>3/1/19&ndash;2/29/20</code>) was in effect at lease start, and the <code>6/1/2026</code> allowance cannot be banked until 12 full months after <code>6/1/2026</code> under Rule 4.12(a).</p>
      {render_table(
          "u2-banking-table",
          ["Skipped Anniversary Date", "Form 571 Rate Period", "Published Rate", "Conditional Dollar Amount on $3,150.00", "Verification Condition"],
          u2_bank_rows,
          sources,
      )}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>4. Unit 1 April 1, 2026 Occupant Change — Rule &sect;6.14 &amp; Costa-Hawkins Analysis</h2>
      </div>
      <p class="section-lead">Evaluating the transition from three initial occupants (<code>Placeholder Tenants 1A, 1B, 1C</code> on Feb. 1, 2025) to two occupants (<code>Placeholder Tenant 1A</code> + <code>Placeholder Tenant 1D</code> on Apr. 1, 2026 at <code>$3,995.00</code>).</p>
      {render_table("u1-occupant-rules", ["Occupant-Change Question", "Statutory & Regulatory Analysis", "Compliance Posture"], occ_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>5. Complete Official Form 571 Rate Schedule (April 1, 1982 &ndash; February 28, 2027)</h2>
      </div>
      <p class="section-lead">All 46 historical periods verified directly from official Form 571 PDF on <code>2026-11-10</code>. Where SF.gov webpage prose examples contain year-label typos (Flag <code>RA-BA23-07</code>), Form 571 controls.</p>
      {render_table(
          "form-571-schedule",
          ["Effective Period", "Allowable Increase", "Compliance Note"],
          rate_rows,
          sources,
          "Filter 46 Form 571 periods by year (e.g., 2026, 2023, 2019, 1992)...",
      )}
    </section>
    """
    return page_shell(
        "units-and-rates.html",
        "Units 1 & 2 Math & 94122 Caps",
        "Outer Sunset 94122 Legal Caps, Unit 1 & Unit 2 Conditional Calculations & Form 571",
        "Side-by-side Local, State, and Federal rent limitations, exact non-compounded Unit 1 & Unit 2 scenario tables, Unit 1 occupant-change rules, and the complete 46-period Form 571 schedule.",
        body,
        meta,
    )


def build_notice_and_reasons(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    svc_rows = [
        (
            [
                "Increase <= 10% in 12 months — Personal Delivery (Civ. Code §827(b)(1)(A), (b)(2))",
                num("30 calendar days"),
                "Deliver written copy personally to each adult tenant on the lease; retain signed acknowledgment or contemporaneously dated declaration of personal service.",
                "U1-A / U1-B (eff. 2027-02-01): serve <= 2027-01-02 · U2-A (eff. 2027-02-28): serve <= 2027-01-29",
            ],
            ["CS19"],
            "svc-30-pers",
        ),
        (
            [
                "Increase <= 10% in 12 months — USPS First-Class Mail within CA (Civ. Code §827 + CCP §1013(a))",
                num("35 calendar days (30 + 5)"),
                "Deposit sealed, postage-paid USPS envelope addressed to tenant's residence; include notation of date/place of mailing or unsigned certificate of mailing per CCP §1013(b) (+10d if out-of-state US; +20d international).",
                "U1-A / U1-B (eff. 2027-02-01): mail <= 2026-12-28 · U2-A (eff. 2027-02-28): mail <= 2027-01-24",
            ],
            ["CS19", "CS20"],
            "svc-35-mail",
        ),
        (
            [
                "Increase > 10% in 12 months — Personal Delivery (Civ. Code §827(b)(3)(A))",
                num("90 calendar days"),
                "Triggered whenever proposed increase (alone or combined with prior 12-month increases) exceeds 10% — applies to BOTH U2-B (13.1%) and U2-C (11.6%).",
                "U2-B / U2-C (eff. 2027-02-28): serve personally <= 2026-11-30",
            ],
            ["CS19"],
            "svc-90-pers",
        ),
        (
            [
                "Increase > 10% in 12 months — USPS First-Class Mail within CA (Civ. Code §827 + CCP §1013(a))",
                num("95 calendar days (90 + 5)"),
                "Same strict USPS first-class mail rules (+5 calendar days within CA). Serve several days early so postmark/deposit date cannot be disputed.",
                "U2-B / U2-C (eff. 2027-02-28): mail within CA <= 2026-11-25",
            ],
            ["CS19", "CS20"],
            "svc-95-mail",
        ),
        (
            [
                "Email, Text Message, Portal Message, or Taping to Door Alone",
                raw(badge("INVALID ALONE", "danger")),
                "Civil Code §827(b)(1) authorizes ONLY personal delivery or CCP §1013 mail for residential rent increases. Email courtesy copies may be sent AFTER valid personal or USPS mail service, never instead of it.",
                "Defective service renders the notice unenforceable until re-served with full statutory lead time.",
            ],
            ["CS19", "CS20"],
            "svc-invalid",
        ),
    ]

    content_rows = [
        (
            [
                "Dollar amount of increase, percentage increase, current base rent & new base rent",
                "Mandatory (SF.gov Topic 050 & Civ. Code §827)",
                "Calculate strictly on base rent excluding temporary passthroughs; never round up to the nearest dollar.",
            ],
            ["CS09", "CS19"],
            "cnt-1",
        ),
        (
            [
                "Exact effective date — using the Form 571 rate in effect ON the effective date",
                "Mandatory (SF.gov Topic 050 & Topic 503)",
                "SF.gov rule: 'use the percentage that will be in effect on the date of the increase, not the percentage in effect on the date they serve the notice.'",
            ],
            ["CS09", "CS10"],
            "cnt-2",
        ),
        (
            [
                "Itemized breakdown: annual CPI portion vs. banked portion & banked basis dates",
                "Mandatory to state (§37.3(b)(1), Rule §4.10(a)(1), Rule §4.12(b))",
                "Nuance: §37.3(b)(5) states nonconforming increases are null and void, while Rule §4.10(b) and Rule §4.12(b) specify that omitting banked dates does not void an increase that does not exceed allowable annual + banked limits. Always include the full year-by-year table anyway so no dispute arises.",
            ],
            ["CS07", "CS11"],
            "cnt-3",
        ),
        (
            [
                "Separate accounting for any Rent Board Fee recovery ($29.50) or bond/utility worksheet passthrough",
                "Mandatory separation (SF.gov Rent Board Fee & §37.3(b)(3))",
                "Never merge the $29.50 fee share or temporary passthroughs into base rent; bill separately with supporting documentation/worksheets.",
            ],
            ["CS06", "CS07"],
            "cnt-4",
        ),
    ]

    reason_rows = [
        (
            [
                "Routine Annual CPI Allowance under SF Admin. Code §37.3(a)(1) (1.6% for 3/1/26–2/28/27)",
                raw(badge("Lawful & Standard", "verified")),
                "Expressly authorized by ordinance to partially offset Bay Area CPI inflation (60% of CPI-U) without a Rent Board petition once licensed under §37.15.",
            ],
            ["CS01", "CS07", "CS08"],
            "rsn-1",
        ),
        (
            [
                "Accumulated Skipped Annual Allowances ('Banked Increases') under §37.3(a)(2) & Rule §4.12",
                raw(badge("Lawful if Ledger-Proven", "conditional")),
                "Expressly authorized without Rent Board pre-approval when at least 12 months have elapsed since the skipped allowance could have been imposed (24 months without increase from lease start) — subject to re-checking pending File #261020 if banking >10%.",
            ],
            ["CS07", "CS10", "CS11"],
            "rsn-2",
        ),
        (
            [
                "Pre-Approved Landlord Petition (Capital Improvement, O&M up to 7%, Comparable Rents) or Bond/Utility Worksheet",
                raw(badge("Requires Pre-Filing / Worksheet", "conditional")),
                "Permitted ONLY if the landlord files the required Rent Board petition or worksheet BEFORE serving notice (Topic 301); tenants may seek Financial Hardship deferral on these passthroughs (Topic 363).",
            ],
            ["CS15", "CS27"],
            "rsn-3",
        ),
        (
            [
                "'Catching Unit 1 or Unit 2 up to Outer Sunset 94122 market rent'",
                raw(badge("Unlawful Justification", "danger")),
                "Market-rate catch-up is prohibited for occupied rent-controlled tenancies unless all original occupants have left under §6.14 or Costa-Hawkins.",
            ],
            ["CS07", "CS16"],
            "rsn-4",
        ),
        (
            [
                "'Adding rent because Placeholder Tenant 1D moved into Unit 1'",
                raw(badge("Unlawful Justification", "danger")),
                "Directly violates SF Admin. Code §37.3(a)(11)(A) and Rule §6.13, even if a lease clause purported to allow it.",
            ],
            ["CS07", "CS17"],
            "rsn-5",
        ),
        (
            [
                "'Offsetting recent tenant repair complaints or code inspections'",
                raw(badge("Unlawful Retaliation / Harassment", "danger")),
                "Triggers Cal. Civ. Code §1942.5 retaliation defenses, SF Form 516B 60-day deferral petitions, and potential SF §37.10B bad-faith harassment treble damages.",
            ],
            ["CS26", "CS28", "CS33"],
            "rsn-6",
        ),
    ]

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>1. Statutory Delivery Methods &amp; Illustrative Service Deadlines</h2>
      </div>
      <p class="section-lead">Under California Civil Code &sect;827 and CCP &sect;1013(a), how you deliver the notice changes the minimum calendar lead time by 5 to 20 days.</p>
      {render_table("notice-service-table", ["Service Method & Threshold", "Minimum Lead Time", "Statutory Procedure & Proof to Retain", "Illustrative Latest Service Date"], svc_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. What Every San Francisco Rent-Increase Notice Should Contain</h2>
      </div>
      <p class="section-lead">Include every item below in plain, neutral business prose so neither arithmetic nor notice format can be disputed.</p>
      {render_table("notice-contents-table", ["Notice Element", "Legal Requirement Level", "Exact Compliance Rule"], content_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>3. Lawful 'Normal Business Practice' Reasons vs. Prohibited Reasons</h2>
      </div>
      <p class="section-lead">In San Francisco rent-controlled units, lawful rent increases do not require a narrative essay — citing the published Rent Ordinance section and Form 571 schedule is cleaner and safer than informal explanations.</p>
      {render_table("notice-reasons-table", ["Stated Basis / Reason for Increase", "Legal Standing", "Why It Passes or Fails Review"], reason_rows, sources)}
    </section>
    """
    return page_shell(
        "notice-and-reasons.html",
        "Notice Protocol & Lawful Reasons",
        "Proper Tenant Notification, Service Deadlines & Lawful Reasons for a Rent Increase",
        "Exact California Civil Code §827 and CCP §1013(a) delivery procedures, SF Rent Ordinance §§37.3(b) & 4.10/4.12 itemization rules, and lawful vs. unlawful stated reasons.",
        body,
        meta,
    )


def build_practices(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    rhfs_rows = [
        (
            ["1 unit", num("82.9%"), num("31.6%"), num("80"), num("$8,670 (±$1,109)"), num("$1,651 – $1,651")],
            ["CS32"],
            "rhfs-1",
        ),
        (
            ["2 to 4 units (reported building tier)", num("14.6%"), num("15.5%"), num("74"), num("$5,820 (±$529)"), num("$1,326 – $1,668")],
            ["CS32"],
            "rhfs-2-4",
        ),
        (
            ["5 to 24 units", num("1.7%"), num("8.2%"), num("125"), num("$7,185 (±$1,075)"), num("$1,201 – $1,807")],
            ["CS32"],
            "rhfs-5-24",
        ),
        (
            ["25 to 49 units", num("0.4%"), num("5.4%"), num("148"), num("$6,325 (±$533)"), num("$1,078 – $1,736")],
            ["CS32"],
            "rhfs-25-49",
        ),
        (
            ["50 or more units (institutional tier)", num("0.4%"), num("39.2%"), num("164"), num("$10,979 (±$6,441)"), num("$1,324 – $2,239")],
            ["CS32"],
            "rhfs-50p",
        ),
    ]

    comp_rows = [
        (
            [
                "Annual SF Rent Cap & Banking Rules (§37.3, Form 571, Rule §4.12)",
                "Identical statutory cap (1.6% for 2026–27) and non-compounded banking rules; typically automated on annual lease anniversaries via property-management accounting calendars.",
                "Identical statutory cap (1.6% for 2026–27) and banking rules; small owners more often defer annual increases and accumulate multi-year banked balances (though no official SF dataset measures exact rates — Flag CF-16).",
            ],
            ["CS07", "CS08", "CS10"],
            "prac-cap",
        ),
        (
            [
                "Housing Inventory & Rent Increase License (§37.15)",
                "Mandatory since July 1, 2022 for 10+ unit buildings; bulk Excel upload available for 5+ units.",
                "Mandatory since March 1, 2023 for 1–9 unit buildings; Rent Board recommends 'Individual Unit' online Portal submission.",
            ],
            ["CS01", "CS02"],
            "prac-inv",
        ),
        (
            [
                "SF Business Registration Certificate & Gross Receipts Tax",
                "Mandatory for 4+ unit buildings, commercial units, or corporations exercising franchise powers in SF.",
                "Conditionally exempt if sole SF business activity is long-term rental of one residential structure with <4 units (confirm CF-04).",
            ],
            ["CS04", "CS05"],
            "prac-tax",
        ),
        (
            [
                "Algorithmic Rent-Setting Software (SF Admin. Code §37.10C & DOJ RealPage Action)",
                "BANNED IN SF: §37.10C (eff. Oct 2024; nonprofit standing Oct 2025) bans using revenue-management software that processes nonpublic competitor data ($1,000/unit/month penalty + attorney's fees). U.S. DOJ filed a proposed consent judgment with RealPage on Nov. 24, 2025 (allegations & proposed settlement, not a finding against all corporate owners).",
                "BANNED IN SF: Same §37.10C ban applies. Standard spreadsheets, accounting ledgers, and official Rent Board Form 571 tables are 100% lawful because they use zero nonpublic competitor data.",
            ],
            ["CS31", "CS34"],
            "prac-algo",
        ),
        (
            [
                "Capital Improvement & Bond Passthrough Petitions (Topic 301)",
                "Institutional portfolios routinely file Capital Improvement (10% cap in 6+ unit buildings) and GO/Water Bond passthrough worksheets alongside annual CPI notices.",
                "In buildings with <6 units, general Capital Improvement passthroughs are capped at 5%/yr (seismic/energy rules differ; see Leg Dig Ver1 & Topic 301). Small owners often rely solely on petition-free annual/banked CPI notices.",
            ],
            ["CS13", "CS15"],
            "prac-pet",
        ),
        (
            [
                "SF Owner-Type Empirical Increase Rate Dataset",
                blank_cell(),
                "Flagged (CF-16): No official SF Rent Board report tabulates typical annual increase percentages by corporate vs. individual ownership. Best practice is adopting institutional-grade recordkeeping (uniform calendar, ledger audit, proof of mail) without banned pricing tools.",
            ],
            ["CS02"],
            "prac-blank",
        ),
    ]

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>1. National Empirical Structure — 2024 HUD &amp; U.S. Census Rental Housing Finance Survey</h2>
      </div>
      <p class="section-lead">Official federal statistical benchmark (<code>CBDRB-FY25-0428</code>) comparing small 2&ndash;4 unit properties against 50+ unit institutional properties across the United States (national figures; not San Francisco-specific caps).</p>
      {render_table(
          "rhfs-benchmark",
          ["Property Size Tier", "Share of All Rental Properties", "Share of All Rental Units", "Median Debt Service Coverage Ratio", "2023 Mean Operating Expense / Unit", "Mean Low–High Monthly Rent"],
          rhfs_rows,
          sources,
      )}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. How Large Corporate Operators vs. Individual Owners Operate Under San Francisco Law</h2>
      </div>
      <p class="section-lead">In San Francisco, tenant protections and rent caps apply per covered unit regardless of owner size — what differs is administrative workflow, tax thresholds, and prohibited pricing software.</p>
      {render_table(
          "corporate-vs-individual",
          ["Compliance Dimension", "Large Corporate / Institutional Multifamily Operators", "Individual Owner of a 2-Unit 1940 Building"],
          comp_rows,
          sources,
      )}
    </section>
    """
    return page_shell(
        "practices.html",
        "Corporate vs. Individual Landlords",
        "How Large Real Estate Corporations vs. Individual Property Owners Handle SF Rent Increases",
        "Empirical 2024 HUD/Census Rental Housing Finance Survey data, San Francisco's §37.10C ban on algorithmic pricing software, U.S. DOJ RealPage enforcement bounds, and compliance best practices for a two-unit owner.",
        body,
        meta,
    )


def build_fair_housing(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    strat_rows = [
        (
            [
                "Option 1 — Uniform Neutral Formula Applied to BOTH Units (When Both Are Legally Eligible)",
                raw(badge("Strongest Anti-Discrimination Posture", "verified")),
                "Apply the same written, objective rule to both units (e.g., impose the published 1.6% annual CPI allowance on each unit's first lawful eligibility date once licensed and repair-cleared). Eliminates disparate-treatment comparisons between Unit 1 and Unit 2 households.",
            ],
            ["CS29", "CS30", "CS37"],
            "fh-opt-1",
        ),
        (
            [
                "Option 2 — Raise ONE Unit Only Because the Other Unit Is Contractually or Legally Ineligible",
                raw(badge("Lawful if Documented by Neutral Record", "conditional")),
                "Raising Unit 2 while deferring Unit 1 (or vice versa) is NOT unlawful discrimination when driven by an objective, documented unit fact — such as Unit 1 being inside an active fixed-term lease through March 31, 2027 (CF-05), not yet reaching its 12-month anniversary, or having an active repair item. Contemporaneously write down that neutral contract/ledger reason in your file before serving notice.",
            ],
            ["CS21", "CS29", "CS30"],
            "fh-opt-2",
        ),
        (
            [
                "Option 3 — Different Percentages on Both Units Driven Strictly by Objective Banking Math",
                raw(badge("Lawful Under Neutral Formula (Check File #261020)", "conditional")),
                "Applying a uniform policy such as 'current 1.6% annual + 100% (or up to 10.0%) of ledger-verified banked allowances' naturally yields different percentages for a 2019 lease vs. a 2025 lease because of lease start dates, not tenant traits.",
            ],
            ["CS10", "CS13", "CS29"],
            "fh-opt-3",
        ),
        (
            [
                "Option 4 — Raising an Ineligible Unit 'Just to Treat Both Units the Same' OR Selecting One Unit Based on Protected Traits / Complaints",
                raw(badge("High Legal Liability — Avoid", "danger")),
                "Forcing an increase onto a fixed-term or repair-impaired unit for 'symmetry' violates contract/habitability law; conversely, singling out one household because of race, national origin, familial status/children, disability, age, sexual orientation, source of income (vouchers), primary language, immigration status, or repair/union activity violates FHA, FEHA, Unruh, §1942.5, and SF §37.10B.",
            ],
            ["CS28", "CS29", "CS30", "CS33", "CS37"],
            "fh-opt-4",
        ),
    ]

    law_rows = [
        (
            [
                "Federal Fair Housing Act — 42 U.S.C. §3604(b) & (f)",
                "Race, color, religion, national origin, sex, familial status, handicap/disability (including reasonable accommodations/modifications).",
                "HUD / DOJ administrative investigation or federal civil lawsuit; actual & punitive damages, injunctive relief, and attorney's fees.",
            ],
            ["CS30", "CS36"],
            "law-fha",
        ),
        (
            [
                "California FEHA — Gov. Code §12955(a), (f)",
                "Race, color, religion, sex, gender, gender identity/expression, sexual orientation, marital status, national origin, ancestry, familial status, source of income (vouchers), disability, veteran/military status, genetic information, plus fair-housing retaliation.",
                "California Civil Rights Department (CRD) investigation or Superior Court civil suit; actual/punitive damages and prevailing-plaintiff attorney's fees (no 'Mrs. Murphy' carve-out for non-owner-occupied two-unit buildings).",
            ],
            ["CS29"],
            "law-feha",
        ),
        (
            [
                "California Unruh Civil Rights Act — Civ. Code §51",
                "Sex, race, color, religion, ancestry, national origin, disability, medical condition, genetic info, marital status, sexual orientation, citizenship, primary language, immigration status (plus perceived/associational traits).",
                "Statutory minimum damages (up to 3x actual damages, minimum $4,000 per Civ. Code §52) plus mandatory prevailing-plaintiff attorney's fees.",
            ],
            ["CS37"],
            "law-unruh",
        ),
        (
            [
                "SF Tenant Harassment Ordinance — Admin. Code §37.10B(a)(5), (a)(9), (c)(5)",
                "Bad-faith coercion to vacate and any discrimination based on actual/perceived race, gender, sexual orientation, ethnicity, nationality, place of birth, immigration/citizenship status, religion, age, parenthood, marriage, pregnancy, disability, AIDS, or minor child occupancy.",
                "Mandatory treble (3x) actual damages or $1,000 statutory damages (whichever is greater), injunctive relief, and mandatory prevailing-tenant attorney's fees.",
            ],
            ["CS33"],
            "law-3710b",
        ),
        (
            [
                "California Anti-Retaliation Statute — Civ. Code §1942.5",
                "Good-faith oral/written tenantability complaints, suspected bed-bug notices, DBI/DPH complaints/citations (180-day window under §1942.5(a) if not in rent default), and organizing/peaceably exercising legal rights at any time (§1942.5(d)).",
                "Invalidates retaliatory increase; statutory & actual damages plus attorney's fees. Preserves good-faith lawful cause (§1942.5(f)–(g)), which the landlord must prove if controverted.",
            ],
            ["CS28"],
            "law-19425",
        ),
    ]

    body = f"""
    <section class="callout callout-forefront">
      <h2>Bottom-Line Answer — Should You Raise Rent on One Unit or Both Units?</h2>
      <p><strong>Raising one unit and not the other is NOT automatically illegal discrimination</strong> — Fair Housing laws prohibit <em>why</em> you differentiate (protected characteristics or protected complaints), not objective differences in lease expiration dates, anniversary dates, or ledger histories. However, <strong>if both Unit 1 and Unit 2 are legally eligible at the same review cycle, applying the same neutral formula to both units (most conservatively, the routine <code>1.6%</code> annual CPI allowance) is the cleanest way to prevent disparate-treatment inquiries before they start.</strong> If one unit is ineligible (for example, if Unit 1's April 1, 2026 document is a 12-month fixed-term lease), raise only the eligible unit and record the objective contract reason in a dated file memo before serving notice.</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>1. Strategic Comparison — Raising One Unit vs. Raising Both Units</h2>
      </div>
      {render_table("one-vs-both-matrix", ["Strategy", "Fair-Housing & Retaliation Posture", "Operational Rule & Documentation Required"], strat_rows, sources)}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Federal, State &amp; San Francisco Anti-Discrimination &amp; Anti-Retaliation Authorities</h2>
      </div>
      <p class="section-lead">Every protected class and statutory enforcement mechanism applicable to a two-unit residential rental property in San Francisco.</p>
      {render_table("fair-housing-statutes", ["Statute / Ordinance", "Protected Classes & Triggering Conduct", "Enforcement Forum & Statutory Remedies"], law_rows, sources)}
    </section>
    """
    return page_shell(
        "fair-housing.html",
        "One Unit vs. Both Units — Fair Housing",
        "Raising Rent on One Unit vs. Both Units — Discrimination & Retaliation Compliance",
        "Objective, neutral decision rules under 42 U.S.C. §3604, California FEHA (§12955), Unruh (§51), Civil Code §1942.5, and SF Administrative Code §37.10B.",
        body,
        meta,
    )


def build_lawyer_scrutiny(site_data: dict, sources: dict[str, dict]) -> str:
    meta = site_data["meta"]
    audit_rows = [
        (["01", "Rent Control Coverage & Parcel Exemption", "Verify pre-June 14, 1979 C of O and confirm no condo/single-family/subsidy exemption.", "Misclassifying a covered unit and serving an uncapped increase renders the notice null and void (§37.3(b)(5)).", "Assessor/DBI C of O record in unit file (CF-01)."], ["CS07", "CS14"], "chk-01"),
        (["02", "Active §37.15 Rent Increase License on Effective Date", "Search portal.sfrb.org for current Housing Inventory compliance on the target unit.", "Increase is suspended during noncompliance; tenant owes $0 increase for suspended months (§37.15(e)).", "Dated PDF/screenshot of active license before notice AND on effective date (CF-02, CF-03)."], ["CS01", "CS02"], "chk-02"),
        (["03", "Fixed-Term Lease Authority", "Read current lease and all addenda (especially Unit 1's April 1, 2026 document).", "Mid-term rent increase during a fixed-term lease without an express escalation clause is unenforceable.", "Signed lease/addendum confirming month-to-month status or escalation clause (CF-05)."], ["CS21"], "chk-03"),
        (["04", "12-Month Minimum Spacing & Anniversary Date", "Confirm >=12 full months since lease start or last rent-increase effective date.", "Premature effective date (<12 months) invalidates the increase under §37.3(a)(1) & Rule §4.12(a).", "Complete rent ledger from move-in through present (CF-06, CF-09)."], ["CS09", "CS11"], "chk-04"),
        (["05", "Effective-Date Form 571 Rate Selection", "Match the percentage to the Form 571 period in force ON the effective date (1.6% through 2/28/2027).", "Using notice-date rate instead of effective-date rate, or guessing an unpublished post-3/1/2027 rate, fails audit.", "Form 571 PDF (2026–27) attached to owner file (CF-15)."], ["CS08", "CS09"], "chk-05"),
        (["06", "Base-Rent-Only Basis (Passthrough Exclusion)", "Verify percentage is multiplied solely by base rent, excluding bond/utility passthroughs or $29.50 fee recovery.", "Applying CPI % to temporary passthroughs overstates the lawful dollar cap.", "Ledger reconciliation separating base rent from passthroughs (CF-06, CF-09)."], ["CS06", "CS09"], "chk-06"),
        (["07", "Zero Compounding & Zero Rounding Up", "Recompute additive percentages and verify cents are exact/truncated (never rounded up).", "Compounding banked years or rounding $63.92 up to $64.00 violates SF.gov & Rule §4.12(a).", "Exact cent-level worksheet ($63.92 / $119.85 / $50.40 / $365.40 / $412.65)."], ["CS09", "CS11"], "chk-07"),
        (["08", "Banking Eligibility & Pending File #261020 Check", "Verify >=24 months with no increase (12 months post-eligibility per Rule §4.12(a)) AND check BOS File #261020 status.", "Premature banking fails Rule §4.12(a); banking >10% noticed >= Sept 15, 2026 faces retroactive cap risk if File #261020 passes as drafted.", "Ledger proof + same-day Legistar status check before serving any >10% banked notice."], ["CS10", "CS11", "CS12", "CS13"], "chk-08"),
        (["09", "Written Itemization (Annual vs. Banked + Basis Dates)", "Check notice states old base, +$, +%, new base, effective date, and annual vs. banked components/dates.", "Omissions invite Rent Board Unlawful Rent Increase petitions even where Rule §4.12(b) avoids automatic voidness.", "Written notice containing explicit component table."], ["CS07", "CS11"], "chk-09"),
        (["10", "Statutory Service Method & Calendar Lead Time", "Confirm personal delivery or USPS first-class mail (never email/text/posting alone) and 30/35 vs. 90/95 days.", "Short notice or email-only delivery defeats enforceability under Civ. Code §827 & CCP §1013(a).", "Signed proof of personal service or CCP §1013(b) certificate of mailing + USPS receipt (CF-13)."], ["CS19", "CS20"], "chk-10"),
        (["11", "35-Day Unabated Code Citation Gate (Civ. Code §1942.4)", "Check DBI/DPH records for any open Notice of Violation >35 days unabated without good cause.", "Issuing a rent-increase notice while §1942.4 applies triggers $100–$5,000 statutory damages + tenant attorney's fees.", "DBI permit/complaint lookup showing zero open citations (CF-10)."], ["CS25"], "chk-11"),
        (["12", "60-Day Failure-to-Repair Deferral Gate (Form 516B)", "Check all written/oral tenant maintenance requests and complete repairs BEFORE serving notice.", "Tenant can file Form 516B within 60 days of notice receipt to defer the increase until repairs are completed.", "Dated repair invoices/completion photos prior to effective date (CF-10)."], ["CS26"], "chk-12"),
        (["13", "180-Day Anti-Retaliation Screen (Civ. Code §1942.5)", "Screen prior 180 days for habitability complaints, inspections, or tenant-association activity.", "Retaliatory motive bars the increase under §1942.5(a)/(d); landlord bears burden of proving good-faith lawful cause if controverted (§1942.5(g)).", "Dated compliance memo showing routine CPI calendar schedule (CF-11)."], ["CS28"], "chk-13"),
        (["14", "Fair Housing, Harassment & Algorithmic Software Ban", "Confirm neutral selection across Units 1 & 2 and zero use of §37.10C competitor-data pricing software.", "Violations carry treble damages + mandatory attorney's fees (§37.10B) or $1,000/unit/mo penalties (§37.10C).", "Written neutral policy + Form 571 manual calculation."], ["CS29", "CS30", "CS31", "CS33"], "chk-14"),
        (["15", "Occupant-Change & Financial Hardship Distinction", "Confirm no unlawful roommate fee/reset on Unit 1, and distinguish passthrough hardship petitions from CPI increases.", "Roommate surcharges are void (§37.3(a)(11)); note that Topic 363 financial hardship deferral applies to passthroughs/O&M, NOT annual or banked CPI increases.", "Unit 1 occupancy file + separate passthrough accounting (CF-07, CF-08)."], ["CS07", "CS16", "CS27"], "chk-15"),
    ]

    ref_rows = [
        (["SF Rent Board Counseling Line & Administrative Petitions", "25 Van Ness Ave, Suite 700 · Tel: 415-252-4600 (Mon–Fri 9–12 & 1–4)", "Free phone counseling for both tenants and landlords; tenants do NOT need a lawyer to file an Unlawful Rent Increase or Failure-to-Repair petition."], ["CS14", "CS35"], "ref-sfrb"),
        (["Open Door Legal — Sunset Office (ZIP 94122)", "1722 Irving Street, San Francisco, CA 94122 · Tel: 415-735-4124", "Listed on official Rent Board Referral Listing directly in Outer Sunset 94122; provides legal assistance to qualifying residents in service areas (subject to eligibility & capacity)."], ["CS35"], "ref-odl"),
        (["Housing Rights Committee of SF (incl. Richmond District Office)", "Main: 11 Grove St (415-703-8644) · Westside/Richmond: 415-947-9085", "Listed on official Rent Board Referral Listing for free tenant counseling (proof of income requested; HUD/subsidized counseling also listed)."], ["CS35"], "ref-hrc"),
        (["San Francisco Tenants Union (SFTU)", "558 Capp Street, San Francisco, CA 94110 · Tel: 415-282-6622", "Citywide tenant counseling clinic listed on official Rent Board Referral Listing; frequently reviews banking math, §37.15 license status, and repair deferral rights."], ["CS35"], "ref-sftu"),
        (["Eviction Defense Collaborative (EDC) & Bay Area Legal Aid", "EDC: 976 Mission St (415-659-9184) · BayLegal: 1800 Market St (415-982-1300)", "Official referral providers focused on eviction notices/summonses (EDC) and Section 8 / subsidized housing & low-income legal aid (BayLegal). Listing does not guarantee universal free notice review."], ["CS35"], "ref-edc"),
        (["Small Property Owners of SF & SF Apartment Association", "SPOSFI: 415-647-2419 · SFAA: 265 Ivy St (415-255-2288) · BASF Referral: 415-989-1616", "Official Landlord & Bar Association resources listed on the same Rent Board Referral Listing for owner forms, counseling, and attorney review."], ["CS35"], "ref-landlord"),
    ]

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>1. 15-Point SF Tenant-Advocate &amp; Tenant-Lawyer Notice Audit</h2>
      </div>
      <p class="section-lead">When a San Francisco tenant brings a rent-increase notice to a Rent Board counselor, tenant clinic, or legal-aid attorney, these are the exact 15 statutory checkpoints they test. Passing all 15 makes an increase routine, lawful, non-discriminatory business practice.</p>
      {render_table(
          "lawyer-audit-15",
          ["#", "Scrutiny Checkpoint", "What a Tenant Counselor / Lawyer Checks", "Consequence If Defective", "Owner Pre-Notice File Proof"],
          audit_rows,
          sources,
          "Filter 15 audit checkpoints (e.g., license, mail, repair, banked, 1942.4)...",
      )}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Official SF Rent Board Referral Directory (Including Outer Sunset 94122)</h2>
      </div>
      <p class="section-lead">Verified from the SF Rent Board Referral Listing on <code>2026-11-10</code>. Important accuracy note: tenants can file Rent Board petitions for free without an attorney, while nonprofit legal representation depends on service area, income, issue type, and clinic capacity.</p>
      {render_table(
          "referral-directory",
          ["Organization / Agency", "Official Listed Address & Phone", "Documented Scope & Eligibility Caveat"],
          ref_rows,
          sources,
      )}
    </section>
    """
    return page_shell(
        "lawyer-scrutiny.html",
        "Tenant-Lawyer 15-Point Audit",
        "Scrutinizing Your Rent Increase Against SF Tenant Advocates & Legal Aid Clinics",
        "Line-by-line 15-point legal audit checklist plus the official San Francisco Rent Board referral directory serving Outer Sunset 94122.",
        body,
        meta,
    )


def build_repo_audit(site_data: dict, sources: dict[str, dict], repo_audit: list[dict]) -> str:
    meta = site_data["meta"]
    rows = []
    for item in repo_audit:
        sev = item["severity"]
        kind = (
            "danger"
            if "High" in sev
            else ("flagged" if "Medium" in sev else ("verified" if "Clean" in sev else "conditional"))
        )
        rows.append(
            (
                [
                    item["id"],
                    item["target"],
                    raw(f"{badge(item['status'], kind)}<br><small>{h(sev)}</small>"),
                    item["finding"],
                ],
                [item["source_id"]],
                item["id"],
            )
        )

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>Line-by-Line Repository Verification Matrix (<code>main</code> @ <code>7dad58d</code>, Verified 2026-11-10)</h2>
      </div>
      <p class="section-lead">Every existing canonical file, root Markdown document, verification script, and preserved historical directory in <code>kanlerxz87-cyber/RentincreaseSF1</code> was audited against primary <code>.gov</code> sources fetched live on <code>2026-11-10</code>. Each row links directly to the controlling official source for manual review.</p>
      {render_table(
          "repo-audit-table",
          ["Audit ID", "Repository File(s) / Scope", "Disposition & Severity", "Exact Line-by-Line Finding"],
          rows,
          sources,
          "Filter 10 repository audit findings...",
      )}
    </section>
    """
    return page_shell(
        "repo-audit.html",
        "Line-by-Line Repository Audit",
        "Line-by-Line Repository Audit & Manual Review Links",
        "Independent verification of repository files, arithmetic, source registries, superseded editions, and privacy history against official government publications.",
        body,
        meta,
    )


def build_flagged(site_data: dict, sources: dict[str, dict], repo_audit: list[dict]) -> str:
    meta = site_data["meta"]
    case_rows = []
    for c in site_data["case_inputs"]:
        case_rows.append(
            (
                [
                    c["id"],
                    c["category"],
                    c["item"],
                    c["brief_input"],
                    blank_cell() if c["official_confirmed"] == "" else c["official_confirmed"],
                    raw(badge(c["status"], "flagged")),
                    c["impact"],
                ],
                [c["source_id"]],
                f"flag-{c['id']}",
            )
        )

    audit_rows = []
    for item in repo_audit:
        audit_rows.append(
            (
                [
                    item["id"],
                    item["target"],
                    raw(badge(item["severity"], "conditional" if "Clean" not in item["severity"] else "verified")),
                    item["finding"],
                ],
                [item["source_id"]],
                f"flag-{item['id']}",
            )
        )

    body = f"""
    <section class="callout callout-warn">
      <h2>Zero-Hallucination &amp; Blank-Cell Policy (26 Total Review Items)</h2>
      <p>Every item below represents either (A) a private property, lease, ledger, license, repair, or benchmark value that <strong>cannot be confirmed from public official government sources</strong> — in which case its <em>Official Confirmed Value</em> cell is intentionally left <strong>blank</strong> rather than inferred — or (B) an official-source ambiguity, pending legislative watch (<a href="{h(sources['CS12']['url'])}" target="_blank" rel="noopener noreferrer">BOS File No. 261020</a>), webpage year-label typo, or historical repository note requiring human awareness before serving any notice.</p>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>Part A — Unverified Private Case Facts &amp; Unconfirmed Official Benchmarks (16 Blank-Cell Items)</h2>
      </div>
      <p class="section-lead">Striped amber cells in the <em>Official Confirmed Value</em> column are physically empty (<code>&lt;td&gt;&lt;/td&gt;</code>) until verified by the owner from primary records.</p>
      {render_table(
          "flagged-case-inputs",
          [
              "Flag ID",
              "Category",
              "Unverified Fact or Benchmark",
              "Supplied Scenario Input (Anonymized)",
              "Official Confirmed Value",
              "Status",
              "Why It Matters Before Serving Notice",
          ],
          case_rows,
          sources,
          "Filter 16 unverified private inputs & blank benchmarks...",
      )}
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>Part B — Pending Legislation Watches, Official Webpage Typos &amp; Repository Audit Flags (10 Items)</h2>
      </div>
      {render_table(
          "flagged-repo-items",
          ["Flag ID", "Target Source or Repo File", "Severity / Classification", "Detailed Finding & Action Required"],
          audit_rows,
          sources,
          "Filter 10 legislative, agency-example, and repo flags...",
      )}
    </section>
    """
    return page_shell(
        "flagged.html",
        "Flagged for Review",
        "Flagged for Review — Unverified Inputs (Blank Cells), Pending Legislation & Source Irregularities",
        "Complete register of all 16 unconfirmed case/benchmark values (left blank, never inferred) and 10 legislative, agency-example, and repository audit flags.",
        body,
        meta,
    )


def build_sources(site_data: dict, sources: dict[str, dict], sources_list: list[dict]) -> str:
    meta = site_data["meta"]
    rows = []
    for s in sources_list:
        detail_html = (
            f"<strong>{h(s['title'])}</strong><br>"
            f"<small>{h(s['used_for'])}</small>"
            f'<div class="quote-box">&ldquo;{h(s["quote"])}&rdquo;</div>'
        )
        rows.append(
            (
                [
                    raw(f"<strong>{h(s['id'])}</strong>"),
                    s["jurisdiction"],
                    s["publisher"],
                    raw(detail_html),
                    s["retrieved"],
                ],
                [s["id"]],
                s["id"],
            )
        )

    body = f"""
    <section class="section-card">
      <div class="section-header">
        <h2>Primary Official Government Source Registry (37/37 Live-Verified on 2026-11-10)</h2>
      </div>
      <p class="section-lead">Zero commercial listing sites, blogs, or secondary summaries are used for legal rules or rates. Every row below was fetched and read directly from its official <code>.gov</code> or City portal publisher on <code>2026-11-10</code>.</p>
      {render_table(
          "official-sources-registry",
          ["ID", "Jurisdiction", "Official Publisher", "Title, Scope & Verbatim Supporting Excerpt", "Live Verified"],
          rows,
          sources,
          "Filter 37 official sources by code section, topic, or publisher (e.g., 37.15, 261020, 827, FEHA, RHFS)...",
      )}
    </section>
    """
    return page_shell(
        "sources.html",
        "Official Sources Registry (37)",
        "Official Government Sources Registry — Live Verified 2026-11-10",
        "Complete 37-source Local, State, and Federal authority index with verbatim statutory/agency excerpts and direct links for manual verification.",
        body,
        meta,
    )


def main() -> None:
    site_data, sources_by_id, repo_audit = load_inputs()
    sources_list = json.loads((DATA_DIR / "sources.json").read_text(encoding="utf-8"))

    outputs = {
        "index.html": build_index(site_data, sources_by_id),
        "licensing.html": build_licensing(site_data, sources_by_id),
        "units-and-rates.html": build_units_and_rates(site_data, sources_by_id),
        "notice-and-reasons.html": build_notice_and_reasons(site_data, sources_by_id),
        "practices.html": build_practices(site_data, sources_by_id),
        "fair-housing.html": build_fair_housing(site_data, sources_by_id),
        "lawyer-scrutiny.html": build_lawyer_scrutiny(site_data, sources_by_id),
        "repo-audit.html": build_repo_audit(site_data, sources_by_id, repo_audit),
        "flagged.html": build_flagged(site_data, sources_by_id, repo_audit),
        "sources.html": build_sources(site_data, sources_by_id, sources_list),
    }

    for filename, html_text in outputs.items():
        (COMPLIANCE_DIR / filename).write_text(html_text, encoding="utf-8")

    print(f"compliance/build.py: generated {len(outputs)} deterministic HTML pages.")


if __name__ == "__main__":
    main()
