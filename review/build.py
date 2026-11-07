#!/usr/bin/env python3
"""Static-site generator for review/ dashboard. Reads review/data/*.json and emits HTML pages."""
import json, os, pathlib, html, datetime

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "data"
PAGES = ROOT / "pages"

def load(p):
    with open(DATA / p, "r", encoding="utf-8") as f:
        return json.load(f)

SITE = load("site.json")
SOURCES = {s["id"]: s for s in load("sources.json")}

def source_links(ids):
    if not ids:
        return ""
    parts = []
    for sid in ids:
        s = SOURCES.get(sid)
        if not s:
            parts.append(f"<span class='tag bad'>missing:{sid}</span>")
            continue
        parts.append(f"<a href='{s['url']}' target='_blank' rel='noopener noreferrer'>[{sid}] {html.escape(s['title'])}</a>")
    return "<div class='src'>Sources: " + "; ".join(parts) + "</div>"

NAV = [
    ("index.html", "Executive Summary"),
    ("pages/license.html", "Rent Board License"),
    ("pages/process.html", "Step-by-Step Process"),
    ("pages/units.html", "Unit Calculations"),
    ("pages/rates.html", "Allowable Rates"),
    ("pages/notice.html", "Notice Protocol"),
    ("pages/practices.html", "Market Practices"),
    ("pages/discrimination.html", "Discrimination &amp; Scrutiny"),
    ("pages/lawyer.html", "Tenant-Lawyer Checklist"),
    ("pages/sources.html", "Sources"),
    ("pages/flagged.html", "Flagged for Review"),
]

def nav_html(current):
    out = ["<nav><ul>"]
    for href, label in NAV:
        cls = "active" if href.endswith(current) else ""
        # compute relative href
        if current in ("", "index.html"):
            rel = href
        else:
            rel = "../" + href if href.startswith("pages/") else "../" + href
            if current.startswith("pages/") and href.startswith("pages/"):
                rel = href.split("/")[-1]
        out.append(f"<li><a class='{cls}' href='{rel}'>{label}</a></li>")
    out.append("</ul></nav>")
    return "".join(out)

def shell(title, body, current):
    is_sub = current != "index.html" and current != ""
    prefix = "../" if is_sub else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — SF Rent Increase Review</title>
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<header>
  <div class="topbar">
    <div class="brand">SF Rent Increase Review <span class="sub">Outer Sunset 94122 · Rent-controlled 1940 building</span></div>
    {nav_html(current)}
  </div>
</header>
<main>
{body}
<div class="disclaimer">
  <strong>Privacy notice:</strong> All tenant names, initials, and the street address are replaced with placeholders. Dates, rents, and official percentages are stated as supplied or published. This dashboard is a source-traced research summary and is <em>not legal advice</em>. Every table row carries links to the official source(s) it relies on. Items that cannot be verified from an official source are left blank and listed on the Flagged for Review page.
</div>
</main>
<footer>
  Generated {datetime.date.today().isoformat()} · Sources: SF Rent Board / SF.gov, California Legislative Information, U.S. GPO.
</footer>
</body>
</html>
"""

def write_page(filename, title, body, current):
    full = shell(title, body, current)
    target = ROOT / filename if (not filename.startswith("pages/")) else ROOT / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(full, encoding="utf-8")
    print("wrote", target.relative_to(ROOT))

# ---------- index.html (executive summary landing) ----------
def build_index():
    case = SITE["case"]
    u1, u2 = SITE["units"]
    lic = SITE["license_qa"][0]
    body = f"""
<h1>Executive Summary</h1>
<p class="lede">{case['location']} · Building constructed {case['building_year']} (rent-controlled) · Two units · Individual property owner. This summary leads with the most important question — the Rent Board license requirement — and then walks through the allowed increases, the notice process, what is reasonable, and what a tenant lawyer would scrutinise.</p>

<div class="callout">
  <strong>Front-and-centre answer:</strong> Yes — you <em>do</em> need a rent-increase license from the SF Rent Board, and yes — you <em>must</em> report into the Rent Board Housing Inventory, <strong>even as an individual (non-corporate) owner of a small 2-unit building</strong>. There is no small-owner exemption. The license is issued automatically when you report that a unit is tenant-occupied in the Rent Board Portal, and it <strong>must be in effect on the effective date</strong> of the increase. An increase imposed without an active license is <strong>null and void</strong> even if the percentage math is perfect. (Effective for 1–9 unit buildings since March 1, 2023.)
  {source_links(["S02", "S03", "S01"])}
</div>

<h2>Case snapshot (anonymised)</h2>
<div class="table-wrap"><table>
  <thead><tr><th></th><th>Unit 1</th><th>Unit 2</th></tr></thead>
  <tbody>
    <tr><td>Location</td><td colspan="2">{html.escape(case['location'])} (ZIP 94122) — building built {case['building_year']}, rent-controlled</td></tr>
    <tr><td>Last lease start</td><td>1 Feb 2025</td><td>1 Jun 2019</td></tr>
    <tr><td>Initial rent</td><td>$3,995.00 / month</td><td>$3,150.00 / month</td></tr>
    <tr><td>Current rent (as supplied)</td><td>$3,995.00 / month (continuing tenancy; partial occupant change 4/1/2026 — no rent change)</td><td>$3,150.00 / month</td></tr>
    <tr><td>Rent-controlled</td><td>Yes (pre-1979 C of O)</td><td>Yes (pre-1979 C of O)</td></tr>
  </tbody>
</table></div>

<h2>Key numbers</h2>
<div class="grid">
  <div class="card"><h3>Current allowable increase (3/1/2026 – 2/28/2027)</h3><div class="kpi">1.6%<span class="unit">SF Rent Board</span></div>{source_links(["S04","S01","S05"])}</div>
  <div class="card"><h3>Unit 1 — annual-only increase</h3><div class="kpi">+$63.92<span class="unit">→ $4,058.92</span></div><p class="src">30 days' notice (35 if mailed). 1.4% banked availability is <strong>flagged</strong> pending banking look-back confirmation.</p>{source_links(["S01","S04","S14"])}</div>
  <div class="card"><h3>Unit 2 — annual-only increase</h3><div class="kpi">+$50.40<span class="unit">→ $3,200.40</span></div><p class="src">30 days' notice (35 if mailed).</p>{source_links(["S01","S04"])}</div>
  <div class="card"><h3>Unit 2 — maximum with banked (if no prior increases served)</h3><div class="kpi">+$412.65<span class="unit">→ $3,562.65 (13.1%)</span></div><p class="src"><span class="tag warn">90 days</span> 95 days if mailed. Banking assumes zero increases since 2019 — unverified and flagged.</p>{source_links(["S01","S14"])}</div>
</div>

<h2>Headline conclusions</h2>
<ol>
  <li><strong>License first, notice second.</strong> Report both units in the <a href="https://portal.sfrb.org/" target="_blank" rel="noopener">Rent Board Portal</a> and confirm the license is active before serving any notice. An unlicensed increase is void regardless of arithmetic.</li>
  <li><strong>The only "reasonable and normal" increase without a Rent Board petition is the published annual rate.</strong> For increases effective through 2/28/2027, that rate is 1.6%.</li>
  <li><strong>"Catch up to market" is not a lawful reason</strong> for a sitting tenant in a rent-controlled unit, and charging extra rent because of the new occupant in Unit 1 is explicitly prohibited.</li>
  <li><strong>You are not required to raise both units</strong>, but you must apply a uniform, written, neutral policy to both (e.g., the published annual rate on each anniversary, with year-by-year banking). Differences must come from base rent, anniversary date, and banked history — never from a protected characteristic or protected activity.</li>
  <li><strong>The conservative, tenant-lawyer-defensible path</strong> is: license confirmed → serve 30-day notice for the 1.6% annual increase on each unit's next anniversary → itemise any banked amounts in a separate worksheet → hold off on the full 13.1% on Unit 2 until you decide whether a large jump is worth the heightened scrutiny (it requires 90-day notice and invites a petition).</li>
</ol>

<h2>What this site contains</h2>
<div class="grid">
  <a class="card" href="pages/license.html" style="text-decoration:none;color:inherit"><h3>Rent Board License Q&amp;A →</h3><p>Step-by-step answer to whether individual owners need a license, what happens without one, and how to get it.</p></a>
  <a class="card" href="pages/process.html" style="text-decoration:none;color:inherit"><h3>Step-by-Step Process →</h3><p>Eight steps from Housing Inventory filing through post-effective-date recordkeeping.</p></a>
  <a class="card" href="pages/units.html" style="text-decoration:none;color:inherit"><h3>Unit Calculations →</h3><p>Per-unit table of allowable increases, banking, notice period, and latest service dates.</p></a>
  <a class="card" href="pages/notice.html" style="text-decoration:none;color:inherit"><h3>Notice Protocol &amp; Reasons →</h3><p>What a valid notice must contain and which reasons are (and are not) lawful.</p></a>
  <a class="card" href="pages/discrimination.html" style="text-decoration:none;color:inherit"><h3>Discrimination &amp; Scrutiny →</h3><p>Raising one unit vs. both; protected classes; best-practice uniform policy.</p></a>
  <a class="card" href="pages/lawyer.html" style="text-decoration:none;color:inherit"><h3>Tenant-Lawyer Checklist →</h3><p>12-point red-team audit modelled on what a free SF tenant attorney would test.</p></a>
  <a class="card" href="pages/flagged.html" style="text-decoration:none;color:inherit"><h3>Flagged for Review →</h3><p>Items that cannot be verified from official sources or that require owner confirmation.</p></a>
  <a class="card" href="pages/sources.html" style="text-decoration:none;color:inherit"><h3>Official Sources →</h3><p>Source register with direct links to SF.gov, California Legislative Information, and U.S. GPO.</p></a>
</div>
"""
    write_page("index.html", "Executive Summary", body, "index.html")

def build_license():
    body = [f"<h1>Rent Board License &amp; Housing Inventory — Your top question, answered</h1>",
            f"<p class='lede'>You asked: <em>“I am just an individual property owner and not part of a corporation, so do I still need to apply for the license and inform the rent board before notifying tenants of a rent increase?”</em></p>"]
    body.append("<div class='callout ok'><strong>Short answer: Yes.</strong> There is no individual-owner or small-building exemption. Reporting is required of ALL owners of residential property in San Francisco, and the license must be in effect on the effective date of any annual or banked increase.</div>")
    body.append("<h2>Q&amp;A (sourced from SF.gov)</h2><div class='table-wrap'><table><thead><tr><th style='width:40%'>Question</th><th>Answer</th><th>Sources</th></tr></thead><tbody>")
    for qa in SITE["license_qa"]:
        body.append(f"<tr><td><strong>{html.escape(qa['question'])}</strong></td><td><strong>{html.escape(qa['short_answer'])}</strong><br><br>{html.escape(qa['detail'])}</td><td>{source_links(qa['sources'])}</td></tr>")
    body.append("</tbody></table></div>")
    body.append("<h2>Why the rule applies to you</h2><p>Ordinance 265-20 (effective 1/18/2021) added Administrative Code §37.15. The SF Rent Board states:</p><ul><li>For condominium units and units in buildings with fewer than 10 residential units (which covers your 2-unit building), the requirement took effect <strong>March 1, 2023</strong>.</li><li>Reporting is done at <a href='https://portal.sfrb.org/' target='_blank' rel='noopener'>portal.sfrb.org</a>.</li><li>When you report a non-owner-occupied (tenant-occupied) unit, a rent-increase license is <strong>automatically generated</strong>; there is no separate 'application'.</li><li>The license must be in effect <strong>on the effective date of the increase</strong>, not just when you file.</li><li>There is no monetary penalty for late filing, but an increase imposed while unlicensed is null and void — the tenant does not have to pay it.</li></ul>")
    body.append(source_links(["S02","S03","S01","S12"]))
    write_page("pages/license.html", "Rent Board License", "".join(body), "pages/license.html")

def build_process():
    body = [f"<h1>Step-by-step process</h1>",
            "<p class='lede'>Follow this order. The sequence — file → license → calculate → notice → serve → record — is the part that most often trips up small owners.</p>",
            "<ol class='steps'>"]
    for s in SITE["steps"]:
        body.append(f"<li><div class='step-title'>Step {s['step']}: {html.escape(s['title'])}</div><div>{html.escape(s['how'])}</div>{source_links(s['sources'])}</li>")
    body.append("</ol>")
    body.append("<div class='callout warn'><strong>Common small-owner mistakes to avoid</strong><ul><li>Skipping the Housing Inventory because 'I only have two units.' The law applies to you.</li><li>Using next year's percentage because you served notice this year. Use the rate in effect on the <em>effective date</em>.</li><li>Rounding the dollar amount up. Don't.</li><li>Serving a large banked increase with 30 days' notice. Anything over 10% (including cumulative increases in the prior 12 months) needs 90 days.</li><li>Forgetting to add 5 days when the notice is mailed within California.</li><li>Charging extra for the new roommate in Unit 1. SF explicitly forbids that.</li></ul></div>")
    write_page("pages/process.html", "Step-by-Step Process", "".join(body), "pages/process.html")

def build_units():
    body = [f"<h1>Unit-by-unit calculations</h1>"]
    body.append("<p class='lede'>All figures recomputed from the SF Rent Board published rate of 1.6% (effective 3/1/2026–2/28/2027) and Form 571 history. No rounding up. Banked amounts are added, not compounded.</p>")
    body.append("<div class='table-wrap'><table><thead><tr><th></th><th>Unit 1</th><th>Unit 2</th></tr></thead><tbody>")
    rows = [
        ("Last lease start", "1 Feb 2025", "1 Jun 2019"),
        ("Current base rent", "$3,995.00", "$3,150.00"),
        ("Anniversary date", "1 February", "1 June"),
        ("Current allowable rate", "1.6% (through 2/28/2027)", "1.6% (through 2/28/2027)"),
        ("Annual-only increase (dollars)", "+$63.92 → $4,058.92", "+$50.40 → $3,200.40"),
        ("Banked amount available", "1.4% (2025–26) eligibility is flagged — see Flagged page", "11.5% (2020–2025) IF no increases were ever served — unverified"),
        ("Maximum before petition (with banked)", "1.6% conservative (until F2 resolved)", "13.1% = +$412.65 → $3,562.65"),
        ("Notice required", "30 days (35 if mailed)", "30 days for ≤10% / 90 days for full 13.1% (95 if mailed)"),
        ("Latest service date (illustrative)", "See Flagged page for recomputation before serving", "See Flagged page for recomputation before serving"),
    ]
    for r in rows:
        body.append(f"<tr><td><strong>{html.escape(r[0])}</strong></td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td></tr>")
    body.append("</tbody></table></div>")
    body.append(source_links(["S01","S04","S05","S06","S14","S07","S08"]))
    body.append("<h2>Calculation detail per unit</h2><div class='table-wrap'><table><thead><tr><th>Unit</th><th>Item</th><th>Value</th><th>Note</th><th>Source</th></tr></thead><tbody>")
    for a in SITE["allowable_increases"]:
        for k, label in [
            ("anniversary","Anniversary date"),
            ("current_rate_period","Rate period in effect"),
            ("annual_only_increase_pct","Annual-only %"),
            ("annual_only_dollars","Annual-only $"),
            ("new_rent_annual_only","New rent (annual only)"),
            ("banked_available","Banked amount"),
            ("lawful_max_before_petition","Lawful max (no petition)"),
            ("notice_required","Notice required"),
            ("latest_service_date_for_2_1_2027_effective" if a["unit"]=="U1" else "latest_service_date_for_2_28_2027_effective","Latest service date (illustrative)"),
        ]:
            body.append(f"<tr><td>{a['unit']}</td><td>{html.escape(label)}</td><td>{html.escape(str(a[k]))}</td><td></td><td>{source_links(a['sources'])}</td></tr>")
    body.append("</tbody></table></div>")
    write_page("pages/units.html", "Unit Calculations", "".join(body), "pages/units.html")

def build_rates():
    body = [f"<h1>Allowable annual rates history</h1>",
            "<p class='lede'>San Francisco's allowable annual increase is set annually at 60% of the Bay Area CPI-U increase, capped at 7%. The rate is applied on the tenant's anniversary date, using the percentage in effect on the effective date.</p>",
            "<div class='table-wrap'><table><thead><tr><th>Effective period</th><th class='num'>Allowable rate</th><th>Application to this case</th><th>Source</th></tr></thead><tbody>"]
    for r in SITE["rate_history"]:
        body.append(f"<tr><td>{html.escape(r['period'])}</td><td class='num'>{html.escape(r['rate']) if r['rate'] else '<em>not yet published</em>'}</td><td>{html.escape(r['note'])}</td><td>{source_links(r['sources'])}</td></tr>")
    body.append("</tbody></table></div>")
    write_page("pages/rates.html", "Allowable Rates", "".join(body), "pages/rates.html")

def build_notice():
    body = [f"<h1>Notice protocol &amp; lawful reasons</h1>"]
    body.append("<h2>What a valid written notice must contain</h2>")
    body.append("<div class='table-wrap'><table><thead><tr><th>Element</th><th>Requirement</th><th>Source</th></tr></thead><tbody>")
    elms = [
        ("Form", "In writing; verbal or informal email notice is insufficient.", ["S07"]),
        ("Dollar amount", "State the exact dollar increase (no rounding up).", ["S01"]),
        ("Percentage", "State the percentage increase.", ["S01"]),
        ("Effective date", "State the date the increase takes effect.", ["S01"]),
        ("Banking itemisation", "Best practice — itemise each banked year and its percentage; required for tenant-lawyer defensibility.", ["S14"]),
        ("Service method", "Personal delivery OR mail under CCP §1013 (add 5 days for California mail).", ["S07","S08"]),
        ("Timing — ≤10%", "At least 30 days before the effective date.", ["S01","S07"]),
        ("Timing — >10%", "At least 90 days before the effective date (incl. cumulative increases in the prior 12 months).", ["S01","S07"]),
        ("Rate to use", "The rate in effect on the effective date, not the notice date.", ["S01"]),
        ("License", "License must be active on the effective date. You do not need to attach the license to the tenant notice.", ["S02"]),
    ]
    for e in elms:
        body.append(f"<tr><td><strong>{html.escape(e[0])}</strong></td><td>{html.escape(e[1])}</td><td>{source_links(e[2])}</td></tr>")
    body.append("</tbody></table></div>")
    body.append("<h2>What counts as a reasonable / lawful reason vs. an unlawful reason</h2>")
    body.append("<div class='table-wrap'><table><thead><tr><th>Reason given for increase</th><th>Lawful?</th><th>Note</th><th>Source</th></tr></thead><tbody>")
    for r in SITE["reasonable_reasons"]:
        tag = "<span class='tag ok'>LAWFUL</span>" if r["is_lawful"] else "<span class='tag bad'>UNLAWFUL</span>"
        body.append(f"<tr><td>{html.escape(r['reason'])}</td><td>{tag}</td><td>{html.escape(r['note'])}</td><td>{source_links(r['sources'])}</td></tr>")
    body.append("</tbody></table></div>")
    write_page("pages/notice.html", "Notice Protocol", "".join(body), "pages/notice.html")

def build_practices():
    p = SITE["practices"]
    body = [f"<h1>How corporate vs. individual owners handle increases</h1>"]
    body.append("<div class='callout warn'><strong>Note:</strong> Descriptions of corporate practices here rest on public regulatory materials (SF Admin. Code §37.10C algorithmic-pricing ban, DOJ <em>RealPage</em> litigation reporting, Census/HUD Rental Housing Finance Survey categories) — no proprietary or anecdotal corporate data is used.</div>")
    body.append(f"<h2>Large corporate owners / REITs</h2><p>{html.escape(p['corporate_landlords'])}</p>{source_links(p['sources'])}")
    body.append(f"<h2>Individual San Francisco owners</h2><p>{html.escape(p['individual_sf_owners'])}</p>{source_links(p['sources'])}")
    body.append("<h2>What this means for you</h2><ul><li>The 'reasonable and normal' practice for an individual 2-unit Outer Sunset owner is the annual 1.6% on anniversary, with a clear written worksheet.</li><li>Do not deploy any algorithmic / revenue-management pricing tool that benchmarks against non-public competitor data — SF Admin. Code §37.10C prohibits that practice.</li><li>If you decide to use banked increases, phase them or at minimum itemise them year-by-year.</li><li>The Rent Board's free counseling line (415-252-4600 / 311) is available to both you and the tenant — expect the tenant to call.</li></ul>")
    write_page("pages/practices.html", "Market Practices", "".join(body), "pages/practices.html")

def build_discrimination():
    d = SITE["discrimination"]
    body = [f"<h1>Raising one unit vs. both — discrimination analysis</h1>",
            f"<p>{html.escape(d['summary'])}</p>{source_links(d['sources'])}",
            f"<h2>Practical recommendation</h2><p>{html.escape(d['practical_recommendation'])}</p>{source_links(d['sources'])}",
            "<h2>Key rules</h2><ul><li>Federal Fair Housing Act (42 U.S.C. §3604) and California FEHA (Gov. Code §12955) prohibit discrimination in the <em>terms, conditions, or privileges</em> of rental — which includes rent increases.</li><li>SF adds additional protected classes (source of income, immigration status, gender identity/expression, etc.).</li><li>Retaliation within 180 days of protected tenant activity (repair requests, Rent Board petitions, inspections, organizing) creates a presumption against the landlord.</li><li>Treating units differently is allowed when the difference is explained by neutral, documented factors (anniversary date, lease start date, banked history, approved passthroughs).</li></ul>"]
    write_page("pages/discrimination.html", "Discrimination & Scrutiny", "".join(body), "pages/discrimination.html")

def build_lawyer():
    body = [f"<h1>Tenant-lawyer scrutiny checklist</h1>",
            "<p class='lede'>San Francisco tenants can obtain free legal representation. Any rent increase you serve should pass this audit on the paperwork and on the facts. Each check links to the controlling source.</p>",
            "<div class='table-wrap'><table><thead><tr><th>#</th><th>Check</th><th>Status</th><th>Source</th></tr></thead><tbody>"]
    for i, c in enumerate(SITE["lawyer_scrutiny_checklist"], 1):
        body.append(f"<tr><td>{i}</td><td>{html.escape(c['check'])}</td><td>{html.escape(c['status'])}</td><td>{source_links(c['sources'])}</td></tr>")
    body.append("</tbody></table></div>")
    body.append("<div class='callout'><strong>Bottom line:</strong> If the license is active, the rate is 1.6% (or a fully itemised additive banked amount), the notice is 30/90 days with +5 for mail, no extra charge is made for the new occupant, and no protected activity is in the 180-day window, the increase is the same kind of increase the Rent Board expects to see across the city, and a tenant lawyer will generally not find a viable challenge.</div>")
    write_page("pages/lawyer.html", "Tenant-Lawyer Checklist", "".join(body), "pages/lawyer.html")

def build_sources():
    body = [f"<h1>Official sources</h1>",
            "<p class='lede'>Every factual claim on this dashboard traces to one or more of these sources. All are official .gov sites or the California Legislative Information / U.S. GPO.</p>",
            "<div class='table-wrap'><table><thead><tr><th>ID</th><th>Source</th><th>Agency</th><th>Used for</th></tr></thead><tbody>"]
    for s in load("sources.json"):
        body.append(f"<tr><td><strong>{s['id']}</strong></td><td><a href='{s['url']}' target='_blank' rel='noopener noreferrer'>{html.escape(s['title'])}</a></td><td>{html.escape(s['agency'])}</td><td>{html.escape(s['used_for'])}</td></tr>")
    body.append("</tbody></table></div>")
    write_page("pages/sources.html", "Official Sources", "".join(body), "pages/sources.html")

def build_flagged():
    body = [f"<h1>Flagged for review</h1>",
            "<p class='lede'>Items on this page either cannot be confirmed from an official source, depend on facts only the owner can verify, or reflect a known ambiguity in the published rules. They do not block you from proceeding — they should be resolved before you serve notice.</p>",
            "<div class='table-wrap'><table><thead><tr><th>ID</th><th>Flag</th><th>Source</th></tr></thead><tbody>"]
    for f in SITE["flags"]:
        body.append(f"<tr><td><strong>{f['id']}</strong></td><td>{html.escape(f['flag'])}</td><td>{source_links(f['sources']) if f['sources'] else '<em>No official source (owner-specific fact).</em>'}</td></tr>")
    body.append("</tbody></table></div>")
    write_page("pages/flagged.html", "Flagged for Review", "".join(body), "pages/flagged.html")

if __name__ == "__main__":
    build_index()
    build_license()
    build_process()
    build_units()
    build_rates()
    build_notice()
    build_practices()
    build_discrimination()
    build_lawyer()
    build_sources()
    build_flagged()
    print("done")
