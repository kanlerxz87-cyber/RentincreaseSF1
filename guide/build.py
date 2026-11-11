#!/usr/bin/env python3
"""Deterministic static site generator for /guide/ and audit/session-5d4a1320/SOURCES.md.

Reads verified data from audit/session-5d4a1320/{sources.json,site_data.json}
and produces 10 byte-reproducible HTML pages under guide/ plus SOURCES.md.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "audit" / "session-5d4a1320"
GUIDE_DIR = ROOT / "guide"

SOURCES_LIST = json.loads((AUDIT_DIR / "sources.json").read_text(encoding="utf-8"))
SOURCES = {s["id"]: s for s in SOURCES_LIST}
DATA = json.loads((AUDIT_DIR / "site_data.json").read_text(encoding="utf-8"))

NAV_ITEMS = [
    ("index.html", "Executive Summary"),
    ("licensing.html", "Rent Board License"),
    ("units-and-rates.html", "Units 1 & 2 Rates"),
    ("legal-framework.html", "94122 Legal Matrix"),
    ("market-practices.html", "Corporate vs. Individual"),
    ("tenant-notice.html", "Notice & Reasons"),
    ("lawyer-scrutiny.html", "Lawyer Audit & Fair Housing"),
    ("repo-audit.html", "Repo Audit"),
    ("sources.html", "Official Sources (33)"),
    ("flagged-for-review.html", "Flagged for Review"),
]


def esc(val: object) -> str:
    return html.escape(str(val), quote=True)


def money(val: str) -> str:
    return f"${float(val):,.2f}"


def src_cell(sid: str, current_page: str) -> str:
    s = SOURCES[sid]
    quote_href = f"#{sid}" if current_page == "sources.html" else f"sources.html#{sid}"
    return (
        f'<a class="src-link" href="{esc(s["url"])}" target="_blank" rel="noopener">'
        f'{esc(s["publisher"].split("(")[0].strip())} ({esc(sid)})</a>'
        f'<span class="src-sub"><a href="{quote_href}">Verbatim excerpt &rarr;</a></span>'
    )


def severity_badge(sev: str) -> str:
    low = sev.lower()
    if "high" in low or "unlawful" in low:
        cls = "badge-high"
    elif "med" in low or "watch" in low or "flag" in low or "cond" in low:
        cls = "badge-medium"
    elif "low" in low or "pass" in low or "verified" in low or "lawful" in low:
        cls = "badge-low"
    else:
        cls = "badge-info"
    return f'<span class="badge {cls}">{esc(sev)}</span>'


def render_shell(filename: str, page_title: str, hero_title: str, hero_desc: str, body_html: str) -> str:
    nav_links = "\n".join(
        f'      <a href="{href}" class="{"active" if href == filename else ""}">{esc(label)}</a>'
        for href, label in NAV_ITEMS
    )
    meta = DATA["meta"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)} — SF 94122 Rent Increase Compliance Guide</title>
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <div>
        <div class="brand-title">San Francisco Rent Increase Compliance Dashboard — Outer Sunset 94122</div>
        <div class="brand-subtitle">1940 Two-Unit Rent-Controlled Building &middot; Privacy-First Anonymized Edition &middot; Live-Verified {esc(meta["verified_date"])}</div>
      </div>
      <div class="topbar-badges">
        <span class="pill pill-green">Current Annual Cap: 1.6% (3/1/26&ndash;2/28/27)</span>
        <span class="pill pill-amber">Nov. 9, 2026 File #261020 Alert Included</span>
        <span class="pill">33 Official .gov Sources</span>
      </div>
    </div>
  </header>
  <div class="nav-wrap">
    <nav class="main-nav" aria-label="Primary category navigation">
{nav_links}
    </nav>
  </div>
  <main class="container">
    <section class="hero">
      <h1>{esc(hero_title)}</h1>
      <p>{esc(hero_desc)}</p>
    </section>
    <div class="filter-bar">
      <input id="table-filter" class="filter-input" type="search" placeholder="Filter any table row on this page (e.g., license, 1.6%, Unit 2, 90-day, 261020)..." aria-label="Filter table rows">
      <span id="filter-count" class="section-desc" style="margin:0;"></span>
    </div>
{body_html}
  </main>
  <footer class="footer">
    <div><strong>Privacy &amp; Evidentiary Notice:</strong> {esc(meta["privacy_policy"])}</div>
    <div style="margin-top:6px;">{esc(meta["disclaimer"])} &middot; <a href="flagged-for-review.html">View Flagged for Review (15 Blank Unverified Inputs)</a> &middot; <a href="sources.html">View All 33 Official Sources</a> &middot; <a href="../index.html">Repository Root Hub</a></div>
  </footer>
  <script src="assets/app.js"></script>
</body>
</html>
"""


def build_index() -> str:
    qa_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(r["question"])}</strong></td>
            <td>{severity_badge(r["short_answer"])}</td>
            <td>{esc(r["detail"])}</td>
            <td>{src_cell(r["source_id"], "index.html")}</td>
          </tr>"""
        for r in DATA["forefront_license_qa"]
    )
    step_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(s["step"])}</strong><br><span class="badge badge-info">{esc(s["phase"])}</span></td>
            <td><strong>{esc(s["action"])}</strong></td>
            <td>{esc(s["beginner_instructions"])}</td>
            <td>{esc(s["cost_or_deadline"])}</td>
            <td>{src_cell(s["source_id"], "index.html")}</td>
          </tr>"""
        for s in DATA["step_by_step_process"]
    )
    scen_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(sc["scenario_id"])}</strong><br>{esc(sc["unit"])}</td>
            <td><strong>{esc(sc["label"])}</strong><br><span class="src-sub">{esc(sc["conditions"])}</span></td>
            <td class="num">{money(sc["base_rent"])}</td>
            <td class="num">{esc(sc["total_pct"])}%<br><span class="src-sub">({esc(sc["annual_pct"])}% ann + {esc(sc["banked_pct"])}% bnk)</span></td>
            <td class="num"><strong>+{money(sc["total_increase_dollars"])}</strong></td>
            <td class="num"><strong>{money(sc["new_base_rent"])}</strong></td>
            <td>Eff. <strong>{esc(sc["illustrative_effective_date"])}</strong><br><span class="src-sub">Personal &le; {esc(sc["personal_service_deadline"])} ({sc["personal_service_days"]}d)<br>CA Mail &le; {esc(sc["ca_mail_deadline"])} ({sc["ca_mail_days"]}d)</span></td>
            <td>{src_cell(sc["source_id"], "index.html")}</td>
          </tr>"""
        for sc in DATA["scenarios"]
    )
    high_flags = [f for f in DATA["flagged_items"] if f["official_confirmed_value"] == ""][:7]
    flag_rows = "\n".join(
        f"""          <tr>
            <td><a href="flagged-for-review.html#{esc(f["flag_id"])}"><strong>{esc(f["flag_id"])}</strong></a></td>
            <td>{severity_badge(f["severity"])}</td>
            <td><strong>{esc(f["item"])}</strong></td>
            <td>{esc(f["owner_brief_input"])}</td>
            <td class="blank-official"></td>
            <td>{esc(f["status"])} &mdash; {esc(f["explanation"])}</td>
            <td>{src_cell(f["source_id"], "index.html")}</td>
          </tr>"""
        for f in high_flags
    )

    body = f"""    <div class="alert-banner alert-forefront">
      <h2>Forefront Answer: Do Individual Property Owners Need a Rent Board License Before Raising Rent?</h2>
      <p><strong>YES.</strong> Under <a href="https://www.sf.gov/information/sec-3715-reporting-obligations-licensing" target="_blank" rel="noopener">San Francisco Administrative Code &sect; 37.15</a> and <a href="https://www.sf.gov/rent-board-housing-inventory" target="_blank" rel="noopener">SF Rent Board Housing Inventory rules</a>, <strong>every owner of a rent-controlled unit &mdash; including an individual ("mom-and-pop") owner not in a corporation or LLC &mdash; must report each unit annually on the free <a href="https://portal.sfrb.org/" target="_blank" rel="noopener">Rent Board Portal</a> to obtain a Rent Increase License.</strong> While the strict statutory gate requires holding the license on the increase's <em>effective date</em>, <strong>completing your Housing Inventory report and saving your active license PDF BEFORE serving the tenant notice</strong> is the essential best practice to prevent immediate tenant or attorney challenges. Standard annual/banked notices are served directly on the tenant (not filed with the Rent Board). Separately, leasing fewer than 4 residential units in a single building is conditionally exempt from the SF Treasurer's <a href="https://sftreasurer.org/information-lessors-residential-real-estate" target="_blank" rel="noopener">Business Registration Certificate</a>.</p>
    </div>

    <div class="alert-banner alert-warn">
      <h3>November 9, 2026 SF Rent Board Warning &mdash; Pending Board of Supervisors File #261020 (10% Banked Cap)</h3>
      <p>Live-verified on <strong>2026-11-10</strong>: On November 9, 2026, the SF Rent Board posted an official alert on <a href="https://www.sf.gov/learn-about-rent-increases-san-francisco" target="_blank" rel="noopener">sf.gov</a> that <a href="https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&amp;GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770" target="_blank" rel="noopener">BOS File No. 261020</a> (currently <em>Pending Committee Action &mdash; NOT enacted law</em>) proposes a 3-year <strong>10%/year cap</strong> on combined banked + capital-improvement increases, <strong>retroactive to banked increases noticed on or after September 15, 2026</strong> if enacted as drafted. Standard 1.6% annual increases are unaffected, but Unit 2's full 11.5% banked catch-up sits above 10%.</p>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Rent Increase License (&sect; 37.15)</div>
        <div class="kpi-value">YES &mdash; $0 Free</div>
        <div class="kpi-note">Mandatory for individual 2-unit owners via portal.sfrb.org before effective date (confirm before serving)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">2026&ndash;2027 SF Annual Allowance</div>
        <div class="kpi-value">1.6%</div>
        <div class="kpi-note">Effective March 1, 2026 &ndash; February 28, 2027 (Form 571; 60% of Bay Area CPI-U)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Unit 1 Scenarios ($3,995 Base)</div>
        <div class="kpi-value">+$63.92 / +$119.85</div>
        <div class="kpi-note">1.6% annual (&rarr; $4,058.92) or conditional 3.0% on 2027-02-01 (&rarr; $4,114.85); verify April 2026 lease term</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Unit 2 Scenarios ($3,150 Input)</div>
        <div class="kpi-value">+$50.40 to +$412.65</div>
        <div class="kpi-note">1.6% annual (&rarr; $3,200.40), 11.6% hedge (&rarr; $3,515.40), or 13.1% full banked (&rarr; $3,562.65; watch File #261020)</div>
      </div>
    </div>

    <section class="section-card" id="forefront-qa">
      <div class="section-header">
        <h2>1. Forefront Executive Q&amp;A: Rent Board License, Business Registration &amp; Pending Law</h2>
        <a href="licensing.html">Detailed Licensing Subpage &rarr;</a>
      </div>
      <p class="section-desc">Direct, verified answers for an individual property owner with no prior Rent Board experience. Every row links directly to an official government source.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Owner Inquiry</th>
              <th>Verified Ruling</th>
              <th>Plain-English Explanation</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{qa_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card" id="step-by-step">
      <div class="section-header">
        <h2>2. Step-by-Step Rent Board &amp; Notice Process (Beginner Walkthrough)</h2>
        <a href="tenant-notice.html">Notice &amp; Service Protocol &rarr;</a>
      </div>
      <p class="section-desc">Follow Steps 1 through 8 in exact order so your rent increase can pass review by a San Francisco tenant counselor or attorney.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Step</th>
              <th>Action</th>
              <th>How to Complete It (Plain-English Instructions)</th>
              <th>Fee / Statutory Timing</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{step_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card" id="scenario-summary">
      <div class="section-header">
        <h2>3. Conditional Unit 1 &amp; Unit 2 Rent-Increase Scenarios (Outer Sunset 94122, Built 1940)</h2>
        <a href="units-and-rates.html">Full Unit &amp; Banking Breakdown &rarr;</a>
      </div>
      <p class="section-desc">Exact unrounded arithmetic using anonymized placeholders (Tenant A&ndash;F) and preserving reported dates and dollar amounts. Conditional on private lease, ledger, and active license verification.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Scenario &amp; Conditions</th>
              <th class="num">Scenario Base</th>
              <th class="num">Rate</th>
              <th class="num">Monthly Increase</th>
              <th class="num">Illustrative Rent</th>
              <th>Illustrative Service Deadlines</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{scen_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card" id="open-gates">
      <div class="section-header">
        <h2>4. High-Priority Unverified Private Inputs (Official Confirmed Values Left Strictly Blank)</h2>
        <a href="flagged-for-review.html">View All 18 Flagged Items &rarr;</a>
      </div>
      <p class="section-desc">Per strict verification rules, any fact that cannot be confirmed from a public official source is left blank in the Official Confirmed Value column and flagged for owner review.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Flag</th>
              <th>Severity</th>
              <th>Required Gate</th>
              <th>Owner-Brief Input</th>
              <th>Official Confirmed Value</th>
              <th>Why It Matters Before Serving Notice</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{flag_rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "index.html",
        "Executive Summary & Rent Board License Guide",
        "Executive Summary: Raising Rent Lawfully in San Francisco (Outer Sunset 94122)",
        "Forefront Rent Board license walkthrough for an individual 2-unit owner, anonymized Unit 1 & Unit 2 scenario math, Nov. 9, 2026 File #261020 alert, and SF tenant-lawyer compliance gates.",
        body,
    )


def build_licensing() -> str:
    reg_comparison = [
        (
            "SF Rent Board Rent Increase License (via Housing Inventory)",
            "SF Rent Board (Admin. Code § 37.15)",
            "YES — Mandatory for ALL owners (zero individual-owner exemption)",
            "$0 (Free online 24/7 at portal.sfrb.org)",
            "Annual update due March 1; must hold active license on effective date (best practice: confirm & save PDF before serving notice).",
            "GS-01",
        ),
        (
            "SF Rent Board Annual Fee",
            "SF Rent Board (Admin. Code Ch. 37A)",
            "YES — Mandatory per dwelling unit unless exempt",
            "$59.00 per dwelling unit ($118.00 for 2 units in 2026–2027)",
            "Due March 1 annually (5%/mo penalty after March 1 up to 15%). Requesting a fee exemption does NOT satisfy Housing Inventory. 50% ($29.50) optionally recoverable from Nov. 1 tenants via deposit-interest offset or separate bill.",
            "GS-06",
        ),
        (
            "SF Business Registration Certificate",
            "SF Office of the Treasurer & Tax Collector",
            "CONDITIONAL NO — Exempt if sole SF business is leasing 1 residential building with <4 units",
            "$0 if exempt (leave 'Business registration number, if any' blank in Rent Board Portal)",
            "Exemption applies ONLY if owner has zero short-term rentals (e.g., Airbnb), zero SF payroll expense, zero commercial units, and no other SF business activity.",
            "GS-04",
        ),
        (
            "Per-Increase Notice Filing / Pre-Approval with Rent Board",
            "SF Rent Board (Admin. Code § 37.3(a)(1)–(2); Rule 4.10)",
            "NO — Standard annual & banked notices are NOT filed with the Rent Board",
            "$0 / Not required",
            "Serve the written rent increase notice directly on the tenant; do not attach the license or mail a copy to the Rent Board unless filing a special petition (e.g., Capital Improvement).",
            "GS-02",
        ),
    ]
    comp_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(a)}</strong></td>
            <td>{esc(b)}</td>
            <td>{severity_badge(c)}</td>
            <td>{esc(d)}</td>
            <td>{esc(e)}</td>
            <td>{src_cell(sid, "licensing.html")}</td>
          </tr>"""
        for a, b, c, d, e, sid in reg_comparison
    )
    step_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(s["step"])}</strong></td>
            <td><strong>{esc(s["action"])}</strong></td>
            <td>{esc(s["beginner_instructions"])}</td>
            <td>{esc(s["cost_or_deadline"])}</td>
            <td>{src_cell(s["source_id"], "licensing.html")}</td>
          </tr>"""
        for s in DATA["step_by_step_process"]
    )
    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>1. Three Distinct San Francisco Registrations &amp; Fees (Do Not Confuse Them)</h2>
      </div>
      <p class="section-desc">Individual landlords frequently confuse the Rent Board's free Rent Increase License, the $59/unit Rent Board Fee, and the Treasurer's Business Registration Certificate.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Registration / Fee</th>
              <th>Issuing SF Agency</th>
              <th>Applies to Individual 2-Unit Owner?</th>
              <th>Cost</th>
              <th>Key Rule &amp; Enforcement Impact</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{comp_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Complete 8-Step Walkthrough for First-Time Individual Owners</h2>
      </div>
      <p class="section-desc">Designed for an individual owner with zero prior experience navigating the SF Rent Board Portal (<a href="https://portal.sfrb.org/" target="_blank" rel="noopener">portal.sfrb.org</a>).</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Step</th>
              <th>Task</th>
              <th>Detailed Beginner Instructions</th>
              <th>Cost / Deadline</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{step_rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "licensing.html",
        "Rent Board License & Housing Inventory Walkthrough",
        "Rent Board License (§ 37.15), Fee & Business Registration Guide",
        "Why individual owners must obtain a free SF Rent Increase License, why you should confirm it before serving notice, and how the <4-unit Business Registration rule works.",
        body,
    )


def build_units() -> str:
    unit_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(u["unit_id"])}</strong><br><span class="src-sub">{esc(u["neighborhood"])} (Built {u["year_built"]})</span></td>
            <td>Initial: <strong>{esc(u["initial_lease_start"])}</strong><br>Continuing: <strong>{esc(u["continuing_tenancy_date"])}</strong></td>
            <td>Initial: {esc(u["initial_tenants_placeholder"])}<br>Current: <strong>{esc(u["current_tenants_placeholder"])}</strong></td>
            <td class="num"><strong>{money(u["reported_rent"])}</strong></td>
            <td>{esc(u["occupancy_analysis"])}</td>
            <td>{esc(u["key_open_facts"])}</td>
            <td>{src_cell(u["source_id"], "units-and-rates.html")}</td>
          </tr>"""
        for u in DATA["units"]
    )
    scen_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(sc["scenario_id"])}</strong></td>
            <td><strong>{esc(sc["label"])}</strong></td>
            <td class="num">{money(sc["base_rent"])}</td>
            <td class="num">{esc(sc["annual_pct"])}% ({money(sc["annual_dollars"])})</td>
            <td class="num">{esc(sc["banked_pct"])}% ({money(sc["banked_dollars"])})</td>
            <td class="num"><strong>{esc(sc["total_pct"])}% (+{money(sc["total_increase_dollars"])})</strong></td>
            <td class="num"><strong>{money(sc["new_base_rent"])}</strong></td>
            <td>Eff. <strong>{esc(sc["illustrative_effective_date"])}</strong><br><span class="src-sub">Personal &le; {esc(sc["personal_service_deadline"])} ({sc["personal_service_days"]}d)<br>CA Mail &le; {esc(sc["ca_mail_deadline"])} ({sc["ca_mail_days"]}d)</span></td>
            <td>{esc(sc["file_261020_exposure"])}</td>
            <td>{src_cell(sc["source_id"], "units-and-rates.html")}</td>
          </tr>"""
        for sc in DATA["scenarios"]
    )
    bank_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(b["anniversary_date"])}</strong></td>
            <td>{esc(b["form_571_window"])}</td>
            <td class="num"><strong>{esc(b["pct"])}%</strong></td>
            <td class="num">{money(b["dollar_on_3150"])}</td>
            <td>{esc(b["status"])}</td>
            <td>{src_cell(b["source_id"], "units-and-rates.html")}</td>
          </tr>"""
        for b in DATA["unit2_banked_breakdown"]
    )
    rate_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(r["period"])}</strong></td>
            <td class="{"blank-official" if r["rate"] == "" else "num"}">{esc(r["rate"])}</td>
            <td>{esc(r["notes"])}</td>
            <td>{src_cell(r["source_id"], "units-and-rates.html")}</td>
          </tr>"""
        for r in DATA["form_571_recent_rates"]
    )
    occ_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(o["rule_topic"])}</strong></td>
            <td>{esc(o["governing_law"])}</td>
            <td>{esc(o["effect_on_unit_1"])}</td>
            <td>{src_cell(o["source_id"], "units-and-rates.html")}</td>
          </tr>"""
        for o in DATA["occupant_change_rules"]
    )

    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>1. Anonymized Unit Profiles (Outer Sunset 94122, Built 1940)</h2>
      </div>
      <p class="section-desc">All personal tenant identifiers are replaced with neutral placeholders (Tenant A&ndash;F); all reported dates and dollar amounts are preserved verbatim.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Unit</th>
              <th>Reported Dates</th>
              <th>Anonymized Occupants</th>
              <th class="num">Reported Monthly Rent</th>
              <th>Occupancy &amp; Rent-Control Status</th>
              <th>Private Records to Confirm</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{unit_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Reproducible Rent-Increase Scenarios (Additive, Never Compounded, Never Rounded Up)</h2>
      </div>
      <p class="section-desc">Includes conservative annual-only baselines (1A, 2A), conditional banked options (1B, 2B), and the Scenario 2C 10%-banked hedge addressing the November 9, 2026 Rent Board warning on pending File #261020.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Scenario</th>
              <th class="num">Base Input</th>
              <th class="num">Annual Portion</th>
              <th class="num">Banked Portion</th>
              <th class="num">Total Increase</th>
              <th class="num">New Base Rent</th>
              <th>Service Deadlines</th>
              <th>Pending File #261020 Exposure</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{scen_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>3. Unit 2 Year-by-Year Conditional Banking Schedule (June 1, 2019 Lease Start @ $3,150.00)</h2>
      </div>
      <p class="section-desc">Shows how the 6 skipped June 1 anniversaries (2020&ndash;2025) sum to 11.5% ($362.25) plus the current 1.6% ($50.40) = 13.1% ($412.65) if zero prior increases occurred.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Anniversary / Period</th>
              <th>Form 571 Window</th>
              <th class="num">Official Rate</th>
              <th class="num">Dollar Component on $3,150</th>
              <th>Banking Status &amp; Rule</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{bank_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>4. Official SF Rent Board Form 571 Rate Schedule (2019&ndash;2028)</h2>
      </div>
      <p class="section-desc">The 2027&ndash;2028 rate is not yet published as of 2026-11-10 and is left strictly blank per verification protocol.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Effective Period</th>
              <th>Published Rate</th>
              <th>Application Notes</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{rate_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>5. Unit 1 Occupant-Change Analysis (SF Rule 6.14 &amp; Costa-Hawkins Civ. Code &sect; 1954.53)</h2>
      </div>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Legal Rule</th>
              <th>Statutory / Regulatory Authority</th>
              <th>Application to Unit 1 (April 1, 2026 Change)</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{occ_rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "units-and-rates.html",
        "Unit 1 & Unit 2 Analysis, Form 571 Rates & Banking",
        "Unit 1 & Unit 2 Reasonable & Lawful Rent Increase Analysis",
        "Exact cent calculations, Form 571 rate windows, Rule 4.12 additive banking, § 6.14 / Costa-Hawkins roommate rules, and pending BOS File #261020 impact.",
        body,
    )


def build_legal() -> str:
    rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(r["level"])}</strong></td>
            <td><strong>{esc(r["authority"])}</strong></td>
            <td>{esc(r["rule_summary"])}</td>
            <td>{esc(r["applies_to_units"])}</td>
            <td>{src_cell(r["source_id"], "legal-framework.html")}</td>
          </tr>"""
        for r in DATA["legal_framework"]
    )
    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>Local, State &amp; Federal Law Matrix Governing Rent Increases in SF ZIP 94122</h2>
      </div>
      <p class="section-desc">How San Francisco's Rent Ordinance interacts with California statutes (AB 1482, Costa-Hawkins, Civil Code &sect;&sect; 827, 1942.4, 1942.5, FEHA, Unruh) and Federal law (Fair Housing Act).</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Jurisdiction</th>
              <th>Statute / Regulation</th>
              <th>Verified Legal Rule</th>
              <th>Application to Outer Sunset 94122 Units</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "legal-framework.html",
        "Local, State & Federal Legal Matrix (94122)",
        "Local, State & Federal Laws Governing 94122 Rent Increases",
        "Why SF Admin. Code Ch. 37 (1.6%) preempts California AB 1482 (8.8%), while California notice/habitability/retaliation statutes and Federal Fair Housing laws apply in full.",
        body,
    )


def build_market() -> str:
    rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(r["dimension"])}</strong></td>
            <td>{esc(r["corporate_practice"])}</td>
            <td>{esc(r["individual_practice"])}</td>
            <td><strong>{esc(r["compliance_takeaway"])}</strong></td>
            <td>{src_cell(r["source_id"], "market-practices.html")}</td>
          </tr>"""
        for r in DATA["corporate_vs_individual"]
    )
    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>How Big Real Estate Corporations vs. Individual SF Property Owners Handle Rent Increases</h2>
      </div>
      <p class="section-desc">Evidence-bounded comparison grounded in the 2024 HUD/Census Rental Housing Finance Survey (RHFS), SF Admin. Code &sect; 37.10C (algorithmic pricing ban), U.S. DOJ RealPage antitrust enforcement, and SF Rent Board rules.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Operational Dimension</th>
              <th>Large Real Estate Corporations / REITs</th>
              <th>Individual ("Mom-and-Pop") SF Owners</th>
              <th>Practical Takeaway for Your 2-Unit Building</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "market-practices.html",
        "Corporate REITs vs. Individual SF Landlords",
        "Corporate Real Estate Operators vs. Individual SF Property Owners",
        "How institutional compliance workflows compare to individual ownership in San Francisco, including SF's § 37.10C algorithmic pricing ban.",
        body,
    )


def build_notice() -> str:
    proto_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(r["element"])}</strong></td>
            <td>{esc(r["requirement"])}</td>
            <td>{esc(r["statutory_basis"])}</td>
            <td>{esc(r["common_trap_to_avoid"])}</td>
            <td>{src_cell(r["source_id"], "tenant-notice.html")}</td>
          </tr>"""
        for r in DATA["notice_protocol"]
    )
    reasons = [
        (
            "Annual Allowable CPI Adjustment (Form 571 — 1.6%)",
            "LAWFUL & NORMAL BUSINESS PRACTICE",
            "Expressly authorized once every 12 months under SF Admin. Code § 37.3(a)(1) when holding an active § 37.15 license; offsets standard operating, property tax, insurance, and maintenance inflation.",
            "GS-11",
        ),
        (
            "Accumulated Banked Annual Increases (Itemized Under Rule 4.12)",
            "LAWFUL (Subject to Ledger Proof & Watching Pending File #261020)",
            "Authorized under SF Admin. Code § 37.3(a)(2) and Rule 4.12(a)–(b) when skipped for >=12/24 months, added without compounding, and served with 30/35-day (<=10%) or 90/95-day (>10%) notice.",
            "GS-12",
        ),
        (
            "Separate 50% Rent Board Fee Recovery ($29.50 for 2026–2027)",
            "LAWFUL ONLY AS SEPARATE BILL / DEPOSIT OFFSET (NEVER IN BASE RENT)",
            "Allowed after full payment of the $59.00/unit fee for tenants residing in the unit on/before November 1; nonpayment is NOT just cause for eviction.",
            "GS-07",
        ),
        (
            "Adding or Replacing a Roommate (e.g., Tenant D Joining Unit 1)",
            "UNLAWFUL & VOID",
            "SF Admin. Code § 37.3(a)(11) and Rule 6.13 prohibit any rent increase solely for an additional occupant, even if the written lease purports to allow it.",
            "GS-16",
        ),
        (
            "'Catching Up to Neighborhood 94122 Market Rent' on Occupied Unit",
            "UNLAWFUL WITHOUT VACANCY / CERTIFIED PETITION",
            "Occupied rent-controlled units cannot be raised to market rate while any original tenant remains; market resets apply only upon full lawful vacancy under Costa-Hawkins.",
            "GS-18",
        ),
        (
            "Retaliation for Repair Requests or Coercing Tenant to Vacate",
            "UNLAWFUL — TREBLE DAMAGES & ATTORNEY'S FEES",
            "Prohibited by Cal. Civ. Code § 1942.5 (180-day retaliation bar) and SF Admin. Code § 37.10B (bad-faith tenant harassment).",
            "GS-30",
        ),
    ]
    reason_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(a)}</strong></td>
            <td>{severity_badge(b)}</td>
            <td>{esc(c)}</td>
            <td>{src_cell(sid, "tenant-notice.html")}</td>
          </tr>"""
        for a, b, c, sid in reasons
    )

    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>1. Correct Statutory Protocol for Informing Tenants of a Rent Increase</h2>
      </div>
      <p class="section-desc">Every mandatory content and service requirement under California Civil Code &sect; 827, CCP &sect; 1013, SF Admin. Code &sect; 37.3, and Rent Board Rules &sect;&sect; 4.10 &amp; 4.12.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Notice Element</th>
              <th>Exact Legal Requirement</th>
              <th>Statutory Authority</th>
              <th>Common Landlord Trap to Avoid</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{proto_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Lawful &amp; Reasonable Reasons vs. Unlawful Reasons for a Rent Increase</h2>
      </div>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Stated or Underlying Reason</th>
              <th>Legal Classification</th>
              <th>How an SF Tenant Lawyer or Administrative Law Judge Evaluates It</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{reason_rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "tenant-notice.html",
        "Tenant Notice Protocol & Lawful Reasons",
        "How to Properly Inform Tenants & What Reasons Pass Scrutiny",
        "Written notice contents, 30/35-day vs. 90/95-day delivery rules, itemizing banked increases, and lawful vs. prohibited justifications.",
        body,
    )


def build_lawyer() -> str:
    chk_rows = "\n".join(
        f"""          <tr>
            <td><strong>#{esc(c["check_no"])}</strong><br><span class="badge badge-info">{esc(c["category"])}</span></td>
            <td><strong>{esc(c["lawyer_question"])}</strong></td>
            <td>{severity_badge(c["status_here"])}</td>
            <td>{esc(c["how_to_pass"])}</td>
            <td>{src_cell(c["source_id"], "lawyer-scrutiny.html")}</td>
          </tr>"""
        for c in DATA["lawyer_scrutiny_checklist"]
    )
    fair_rows = "\n".join(
        f"""          <tr>
            <td><strong>{esc(o["option"])}</strong></td>
            <td>{severity_badge(o["legality"])}</td>
            <td>{esc(o["lawyer_view"])}</td>
            <td>{esc(o["caveat"])}</td>
            <td>{src_cell(o["source_id"], "lawyer-scrutiny.html")}</td>
          </tr>"""
        for o in DATA["one_vs_both_units"]
    )
    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>1. Raising One Unit vs. Raising Both Units (Fair Housing &amp; Discrimination Analysis)</h2>
      </div>
      <p class="section-desc">How FEHA (Cal. Gov. Code &sect; 12955), the Unruh Civil Rights Act (Civ. Code &sect; 51), the Federal Fair Housing Act (42 U.S.C. &sect; 3604), and SF Admin. Code &sect; 37.10B apply to a 2-unit building.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Strategy Option</th>
              <th>Legal Risk Rating</th>
              <th>SF Tenant-Lawyer &amp; Fair Housing Analysis</th>
              <th>Critical Operational Rule</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{fair_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. 15-Point San Francisco Tenant-Lawyer Red-Team Scrutiny Audit</h2>
      </div>
      <p class="section-desc">Tenants in 94122 can petition the SF Rent Board without a lawyer and can seek counseling from organizations on the <a href="https://www.sf.gov/reports--january-2025--rent-board-referral-listing" target="_blank" rel="noopener">Official Rent Board Referral Listing</a> (including Open Door Legal's Sunset office at 1722 Irving St, SF 94122, subject to intake/eligibility limits). Every row below must be satisfied before serving notice.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Check</th>
              <th>What a Tenant Advocate / Attorney Audits</th>
              <th>Current Case Status</th>
              <th>Required Action to Pass Review</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{chk_rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "lawyer-scrutiny.html",
        "SF Tenant-Lawyer 15-Point Audit & Fair Housing",
        "Passing SF Tenant-Lawyer Scrutiny & Raising One Unit vs. Both Units",
        "Line-by-line 15-point red-team defense audit and Fair Housing analysis comparing selective vs. uniform building-wide rent increases.",
        body,
    )


def build_repo_audit() -> str:
    rows = "\n".join(
        f"""          <tr id="{esc(r["audit_id"])}">
            <td><strong>{esc(r["audit_id"])}</strong></td>
            <td><code>{esc(r["file_or_scope"])}</code></td>
            <td>{severity_badge(r["finding_status"])}</td>
            <td>{esc(r["details"])}</td>
            <td>{src_cell(r["source_id"], "repo-audit.html")}</td>
          </tr>"""
        for r in DATA["repo_audit_findings"]
    )
    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>Line-by-Line Repository Verification Audit (Verified 2026-11-10)</h2>
      </div>
      <p class="section-desc">Independent verification of existing repository files, arithmetic, source URLs, archived editions, and privacy compliance against live official government sources.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Audit ID</th>
              <th>Repository File / Scope</th>
              <th>Verification Status</th>
              <th>Line-by-Line Finding &amp; Resolution</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "repo-audit.html",
        "Line-by-Line Repository Audit",
        "Repository-Wide Line-by-Line Verification Audit",
        "Every repository directory, canonical dataset, and root Markdown file checked against live official sources on 2026-11-10.",
        body,
    )


def build_sources() -> str:
    rows = "\n".join(
        f"""          <tr id="{esc(s["id"])}">
            <td><strong>{esc(s["id"])}</strong></td>
            <td><strong>{esc(s["title"])}</strong><br><span class="src-sub">{esc(s["publisher"])} &middot; {esc(s["jurisdiction"])} &middot; Live-fetched {esc(s["retrieved"])}</span></td>
            <td><div class="quote-box">&ldquo;{esc(s["verbatim_quote"])}&rdquo;</div></td>
            <td>{esc(s["used_for"])}</td>
            <td><a class="src-link" href="{esc(s["url"])}" target="_blank" rel="noopener">Open Official Site &rarr;</a></td>
          </tr>"""
        for s in SOURCES_LIST
    )
    body = f"""    <section class="section-card">
      <div class="section-header">
        <h2>33 Live-Verified Official Government Sources (Retrieved 2026-11-10)</h2>
      </div>
      <p class="section-desc">Every source below is an official municipal (sf.gov, portal.sfrb.org, sftreasurer.org, sfgov.legistar.com), California state (leginfo.legislature.ca.gov, courts.ca.gov), or U.S. federal (govinfo.gov, hud.gov, justice.gov, census.gov) publication fetched and read directly in this session. Zero commercial blogs or listing sites are used.</p>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Official Document &amp; Publisher</th>
              <th>Verbatim Supporting Passage</th>
              <th>Used to Verify</th>
              <th>Official Link</th>
            </tr>
          </thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "sources.html",
        "Verified Official Sources Register (33)",
        "Official Verified Trusted Sources Register",
        "Complete primary-source registry with verbatim quotes, retrieval dates (2026-11-10), and direct official links for manual review.",
        body,
    )


def build_flagged() -> str:
    unverified = [f for f in DATA["flagged_items"] if f["official_confirmed_value"] == ""]
    reconciled = [f for f in DATA["flagged_items"] if f["official_confirmed_value"] != ""]

    unv_rows = "\n".join(
        f"""          <tr id="{esc(f["flag_id"])}">
            <td><strong>{esc(f["flag_id"])}</strong></td>
            <td>{severity_badge(f["severity"])}</td>
            <td><strong>{esc(f["item"])}</strong></td>
            <td>{esc(f["owner_brief_input"])}</td>
            <td class="blank-official"></td>
            <td>{severity_badge(f["status"])}<br><span class="src-sub">{esc(f["explanation"])}</span></td>
            <td>{src_cell(f["source_id"], "flagged-for-review.html")}</td>
          </tr>"""
        for f in unverified
    )
    rec_rows = "\n".join(
        f"""          <tr id="{esc(f["flag_id"])}">
            <td><strong>{esc(f["flag_id"])}</strong></td>
            <td>{severity_badge(f["severity"])}</td>
            <td><strong>{esc(f["item"])}</strong></td>
            <td>{esc(f["official_confirmed_value"])}</td>
            <td>{esc(f["explanation"])}</td>
            <td>{src_cell(f["source_id"], "flagged-for-review.html")}</td>
          </tr>"""
        for f in reconciled
    )

    body = f"""    <div class="alert-banner alert-warn">
      <h2>Strict Zero-Hallucination &amp; Blank-Cell Protocol</h2>
      <p>Every item that depends on private owner records (leases, rent ledgers, parcel Certificate of Occupancy, active portal license) or an unpublished government statistic has its <strong>Official Confirmed Value cell left strictly BLANK</strong> and is flagged below with an official source explaining why it matters. Flagged items are published for manual review and do not block site deployment.</p>
    </div>

    <section class="section-card">
      <div class="section-header">
        <h2>1. Unverified Private Facts &amp; Unpublished Official Values ({len(unverified)} Items &mdash; Official Value Left Blank)</h2>
      </div>
      <div class="table-wrap">
        <table class="guide-table" id="unverified-table">
          <thead>
            <tr>
              <th>Flag ID</th>
              <th>Severity</th>
              <th>Item Requiring Verification</th>
              <th>Owner-Brief Input</th>
              <th>Official Confirmed Value</th>
              <th>Flagged Status &amp; Action Required</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{unv_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section-card">
      <div class="section-header">
        <h2>2. Flagged Statutory Nuances, Agency Webpage Typos &amp; Repository Governance Notes ({len(reconciled)} Items)</h2>
        <a href="repo-audit.html">See Full 9-Row Repo Audit &rarr;</a>
      </div>
      <div class="table-wrap">
        <table class="guide-table">
          <thead>
            <tr>
              <th>Flag ID</th>
              <th>Severity</th>
              <th>Irregularity / Governance Item</th>
              <th>Verified Finding</th>
              <th>Detailed Explanation</th>
              <th>Official Source</th>
            </tr>
          </thead>
          <tbody>
{rec_rows}
          </tbody>
        </table>
      </div>
    </section>"""
    return render_shell(
        "flagged-for-review.html",
        "Flagged for Review (Unverified Items & Irregularities)",
        "Flagged for Review — Unverified Inputs & Source/Repo Irregularities",
        "Every unconfirmed value is left strictly blank (never inferred), paired with the controlling official government source for manual owner review.",
        body,
    )


def build_sources_md() -> str:
    lines = [
        "# Verified Official Sources Register (`arena/5d4a1320-rentincreasesf1`)",
        "",
        "- **Live Retrieval & Verification Date:** `2026-11-10`",
        "- **Total Official Sources Fetched & Read:** `33` (`GS-01` through `GS-33`)",
        "- **Commercial / Unofficial Sources Used:** `0`",
        "",
        "| ID | Official Title | Publisher | Jurisdiction | Live Retrieved | Official URL |",
        "|---|---|---|---|---|---|",
    ]
    for s in SOURCES_LIST:
        lines.append(
            f'| `{s["id"]}` | {s["title"]} | {s["publisher"]} | {s["jurisdiction"]} | `{s["retrieved"]}` | <{s["url"]}> |'
        )
    lines.append("")
    return "\n".join(lines)


def _legacy_notice(edition):
    """Superseded-edition notice and direct official links (tools/legacy_notice.py).

    Run as the last build step so that a rebuild reproduces the committed pages.
    """
    import importlib.util
    from pathlib import Path as _Path
    here = _Path(__file__).resolve()
    tool = next(p / "tools" / "legacy_notice.py" for p in here.parents if (p / "tools" / "legacy_notice.py").is_file())
    spec = importlib.util.spec_from_file_location("legacy_notice", str(tool))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.apply_edition(edition)


def main() -> None:
    GUIDE_DIR.mkdir(parents=True, exist_ok=True)
    pages = {
        "index.html": build_index(),
        "licensing.html": build_licensing(),
        "units-and-rates.html": build_units(),
        "legal-framework.html": build_legal(),
        "market-practices.html": build_market(),
        "tenant-notice.html": build_notice(),
        "lawyer-scrutiny.html": build_lawyer(),
        "repo-audit.html": build_repo_audit(),
        "sources.html": build_sources(),
        "flagged-for-review.html": build_flagged(),
    }
    for name, content in pages.items():
        (GUIDE_DIR / name).write_text(content, encoding="utf-8")
    (AUDIT_DIR / "SOURCES.md").write_text(build_sources_md(), encoding="utf-8")
    _legacy_notice("guide")
    print(f"Built {len(pages)} deterministic HTML pages in guide/ and SOURCES.md ({len(SOURCES_LIST)} official sources).")


if __name__ == "__main__":
    main()
