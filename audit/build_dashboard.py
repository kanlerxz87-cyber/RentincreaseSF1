#!/usr/bin/env python3
"""Deterministic static site builder for /dashboard/ (Outer Sunset 94122 Rent Increase Audit)."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "dashboard" / "data"
OUT_DIR = ROOT / "dashboard"
ASSETS_DIR = OUT_DIR / "assets"

PAGES = [
    ("index.html", "Executive Summary", "Landing page, key findings, anonymized unit overview, and master summary table."),
    ("units-analysis.html", "Units & Calculations", "Anonymized Unit 1 & Unit 2 tenancy profiles, official Form 571 rates (2019–2027), and exact cent scenarios."),
    ("legal-framework.html", "Local, State & Federal Law", "Line-by-line legal rules for Outer Sunset (ZIP 94122) across SF Admin. Code Ch. 37, California Codes, and Federal FHA."),
    ("market-practices.html", "Corporate vs. Individual", "How institutional REITs vs. individual SF property owners handle rent increases, §37.10C algorithmic ban, and 2024 Census RHFS data."),
    ("notice-protocol.html", "Notice & Lawful Reasons", "Step-by-step statutory service protocol (Civ. Code §827, CCP §1013, Rules 4.10/4.12) and lawful vs. unlawful grounds."),
    ("lawyer-scrutiny.html", "Tenant-Lawyer Audit", "12-point red-team legal scrutiny modeled on SF free tenant counsel and 94122 neighborhood clinics."),
    ("discrimination-analysis.html", "1 Unit vs. Both Units", "Fair housing, anti-retaliation, and §37.10B analysis of raising one unit versus a uniform policy across both units."),
    ("repo-verification.html", "Repo Line-by-Line Audit", "Line-by-line verification audit of existing repository files and external references."),
    ("flagged-for-review.html", "Flagged for Review", "All unverified private inputs (official value left blank), unpublished future rates, and source/repo irregularities."),
    ("sources.html", "Official Sources (39)", "Complete verified catalog of 39 official .gov statutory, regulatory, and empirical sources."),
]

STYLES_CSS = """\
:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-alt: #f1f5f9;
  --border: #cbd5e1;
  --border-subtle: #e2e8f0;
  --text: #0f172a;
  --text-muted: #475569;
  --navy: #0f294a;
  --navy-light: #1e40af;
  --link: #1d4ed8;
  --link-hover: #1e3a8a;
  --ok-bg: #ecfdf5;
  --ok-fg: #065f46;
  --ok-bd: #a7f3d0;
  --emp-bg: #eff6ff;
  --emp-fg: #1e40af;
  --emp-bd: #bfdbfe;
  --cond-bg: #fefce8;
  --cond-fg: #854d0e;
  --cond-bd: #fde047;
  --flag-bg: #fff1f2;
  --flag-fg: #9f1239;
  --flag-bd: #fecdd3;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color: var(--text);
  background: var(--bg);
  line-height: 1.55;
  font-size: 15px;
}
a { color: var(--link); text-decoration: underline; text-underline-offset: 2px; }
a:hover { color: var(--link-hover); }
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  background: var(--navy);
  color: #fff;
  padding: 0.5rem 1rem;
  z-index: 100;
}
.skip-link:focus { left: 0.5rem; top: 0.5rem; }
header.site-header {
  background: var(--navy);
  color: #ffffff;
  border-bottom: 3px solid #eab308;
}
.header-inner {
  max-width: 1320px;
  margin: 0 auto;
  padding: 1.2rem 1.25rem 0.9rem;
}
.eyebrow {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #cbd5e1;
  margin-bottom: 0.35rem;
}
.privacy-pill {
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(110, 231, 183, 0.5);
  color: #d1fae5;
  padding: 0.12rem 0.55rem;
  border-radius: 999px;
  font-weight: 600;
}
.site-title {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.site-title a { color: #ffffff; text-decoration: none; }
.site-subtitle {
  margin: 0.3rem 0 0.9rem;
  color: #e2e8f0;
  font-size: 0.92rem;
  max-width: 960px;
}
nav.top-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding-top: 0.4rem;
}
nav.top-nav a {
  color: #e2e8f0;
  text-decoration: none;
  font-size: 0.82rem;
  font-weight: 500;
  padding: 0.4rem 0.68rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.12);
}
nav.top-nav a:hover { background: rgba(255, 255, 255, 0.16); color: #ffffff; }
nav.top-nav a[aria-current="page"] {
  background: #ffffff;
  color: var(--navy);
  font-weight: 700;
  border-color: #ffffff;
}
nav.top-nav a.nav-flag {
  border-color: rgba(253, 164, 175, 0.65);
  color: #ffe4e6;
}
nav.top-nav a.nav-flag[aria-current="page"] {
  background: #ffe4e6;
  color: #881337;
  border-color: #ffe4e6;
}
main.container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
}
.page-hero {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 1.25rem 1.4rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.page-hero h1 {
  margin: 0 0 0.4rem;
  font-size: 1.4rem;
  color: var(--navy);
}
.page-hero p {
  margin: 0;
  color: var(--text-muted);
  max-width: 980px;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 0.9rem;
  margin-bottom: 1.25rem;
}
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-left: 4px solid var(--navy-light);
  border-radius: 8px;
  padding: 1rem 1.1rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.kpi-label {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}
.kpi-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--navy);
  margin: 0.2rem 0;
}
.kpi-sub { font-size: 0.83rem; color: var(--text-muted); }
.callout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
  margin-bottom: 1.35rem;
}
.callout {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 1.1rem 1.25rem;
}
.callout h2, .section-card h2 {
  margin: 0 0 0.55rem;
  font-size: 1.1rem;
  color: var(--navy);
}
.callout ul { margin: 0.4rem 0 0; padding-left: 1.2rem; }
.callout li { margin-bottom: 0.4rem; }
.dir-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.85rem;
  margin-bottom: 1.4rem;
}
.dir-card {
  display: block;
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
  padding: 0.95rem 1.05rem;
  text-decoration: none;
  color: var(--text);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.dir-card:hover {
  border-color: var(--navy-light);
  box-shadow: 0 3px 8px rgba(15, 23, 42, 0.07);
}
.dir-card strong {
  display: block;
  color: var(--navy-light);
  margin-bottom: 0.25rem;
  font-size: 0.96rem;
}
.dir-card span {
  display: block;
  color: var(--text-muted);
  font-size: 0.83rem;
}
.section-card {
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  padding: 1.2rem 1.25rem;
  margin-bottom: 1.4rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}
.section-desc {
  margin: 0 0 0.9rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
  margin-bottom: 0.85rem;
  background: var(--surface-alt);
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
}
.filter-bar input[type="search"] {
  flex: 1 1 240px;
  padding: 0.42rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.88rem;
}
.filter-bar select {
  padding: 0.42rem 0.65rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.88rem;
  background: #fff;
}
.filter-note {
  font-size: 0.78rem;
  color: var(--text-muted);
}
.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--border-subtle);
  border-radius: 8px;
}
table.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
  background: #ffffff;
}
table.data-table thead th {
  background: var(--surface-alt);
  color: var(--navy);
  text-align: left;
  font-weight: 700;
  padding: 0.68rem 0.75rem;
  border-bottom: 2px solid var(--border);
  white-space: nowrap;
}
table.data-table tbody td {
  padding: 0.72rem 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
  vertical-align: top;
}
table.data-table tbody tr:last-child td { border-bottom: none; }
table.data-table tbody tr:hover { background: #f8fafc; }
td.col-id {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
  color: var(--navy);
}
td.col-cat { font-weight: 600; min-width: 190px; }
td.col-val {
  font-weight: 600;
  min-width: 165px;
  color: var(--navy);
}
td.col-val:empty {
  background: repeating-linear-gradient(
    -45deg,
    #fff1f2,
    #fff1f2 6px,
    #ffe4e6 6px,
    #ffe4e6 12px
  );
}
td.col-analysis { min-width: 300px; }
td.col-status { white-space: nowrap; }
td.col-sources { min-width: 200px; }
.badge {
  display: inline-block;
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid transparent;
}
.badge-ok { background: var(--ok-bg); color: var(--ok-fg); border-color: var(--ok-bd); }
.badge-emp { background: var(--emp-bg); color: var(--emp-fg); border-color: var(--emp-bd); }
.badge-cond { background: var(--cond-bg); color: var(--cond-fg); border-color: var(--cond-bd); }
.badge-flag { background: var(--flag-bg); color: var(--flag-fg); border-color: var(--flag-bd); }
.src-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.28rem;
}
.src-list a {
  font-size: 0.8rem;
  line-height: 1.3;
  display: inline-block;
}
footer.site-footer {
  max-width: 1320px;
  margin: 0 auto;
  padding: 1.25rem 1.25rem 2.5rem;
  border-top: 1px solid var(--border);
  color: var(--text-muted);
  font-size: 0.82rem;
}
@media (max-width: 768px) {
  .site-title { font-size: 1.2rem; }
  nav.top-nav a { font-size: 0.78rem; padding: 0.35rem 0.55rem; }
}
"""

FILTER_JS = """\
(function () {
  var wrappers = document.querySelectorAll('[data-filter-scope]');
  wrappers.forEach(function (scope) {
    var input = scope.querySelector('input[type="search"]');
    var select = scope.querySelector('select');
    var rows = scope.querySelectorAll('tbody tr');
    var countEl = scope.querySelector('[data-row-count]');
    function apply() {
      var q = input ? input.value.trim().toLowerCase() : '';
      var st = select ? select.value : 'all';
      var shown = 0;
      rows.forEach(function (tr) {
        var textMatch = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        var rowSt = tr.getAttribute('data-status-group') || '';
        var stMatch = st === 'all' || rowSt === st;
        var vis = textMatch && stMatch;
        tr.style.display = vis ? '' : 'none';
        if (vis) shown += 1;
      });
      if (countEl) {
        countEl.textContent = shown + ' of ' + rows.length + ' rows shown';
      }
    }
    if (input) input.addEventListener('input', apply);
    if (select) select.addEventListener('change', apply);
    apply();
  });
})();
"""


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def status_meta(status: str) -> tuple[str, str]:
    if status == "Verified Official Rule":
        return ("badge-ok", "verified")
    if status == "Verified Empirical Data":
        return ("badge-emp", "verified")
    if status.startswith("Conditional"):
        return ("badge-cond", "conditional")
    return ("badge-flag", "flagged")


def render_source_links(source_keys: list[str], sources: dict) -> str:
    items = []
    for key in source_keys:
        src = sources[key]
        url = esc(src["url"])
        label = esc(f'{src["id"]}: {src["short"]}')
        items.append(f'<li><a href="{url}" target="_blank" rel="noopener noreferrer">{label}</a></li>')
    return '<ul class="src-list">' + "".join(items) + "</ul>"


def render_table_section(
    section_id: str,
    heading: str,
    description: str,
    rows: list[dict],
    sources: dict,
    include_filter: bool = True,
) -> str:
    body_rows = []
    for row in rows:
        badge_cls, group = status_meta(row["status"])
        rid = esc(row["id"])
        cat = esc(row["category"])
        # CRITICAL RULE: leave Official Confirmed Value cell strictly empty ("") when unconfirmed!
        val = esc(row["official_value"]) if row["official_value"] != "" else ""
        analysis = esc(row["analysis"])
        status_txt = esc(row["status"])
        src_html = render_source_links(row["sources"], sources)
        body_rows.append(
            f'<tr id="{rid}" data-status-group="{group}">'
            f'<td class="col-id"><a href="#{rid}">{rid}</a></td>'
            f'<td class="col-cat">{cat}</td>'
            f'<td class="col-val">{val}</td>'
            f'<td class="col-analysis">{analysis}</td>'
            f'<td class="col-status"><span class="badge {badge_cls}">{status_txt}</span></td>'
            f'<td class="col-sources">{src_html}</td>'
            f"</tr>"
        )

    filter_html = ""
    if include_filter:
        filter_html = (
            '<div class="filter-bar">'
            f'<input type="search" aria-label="Search {esc(heading)}" placeholder="Filter rows by keyword, statute, or scenario...">'
            f'<select aria-label="Filter {esc(heading)} by verification status">'
            '<option value="all">All Verification Statuses</option>'
            '<option value="verified">Verified Official Rules &amp; Data</option>'
            '<option value="conditional">Conditional Calculations</option>'
            '<option value="flagged">Flagged / Unverified Items</option>'
            "</select>"
            f'<span class="filter-note" data-row-count>{len(rows)} of {len(rows)} rows shown</span>'
            '<span class="filter-note">Shaded empty cells = unconfirmed from official sources (left blank &amp; flagged).</span>'
            "</div>"
        )

    return (
        f'<section class="section-card" id="{esc(section_id)}" data-filter-scope>'
        f"<h2>{esc(heading)}</h2>"
        f'<p class="section-desc">{esc(description)}</p>'
        f"{filter_html}"
        '<div class="table-wrap">'
        '<table class="data-table">'
        "<thead><tr>"
        '<th scope="col">Row ID</th>'
        '<th scope="col">Category / Item</th>'
        '<th scope="col">Official Confirmed Value</th>'
        '<th scope="col">Line-by-Line Analysis &amp; Context</th>'
        '<th scope="col">Verification Status</th>'
        '<th scope="col">Official Source Link(s)</th>'
        "</tr></thead>"
        "<tbody>"
        + "".join(body_rows)
        + "</tbody></table></div></section>"
    )


def render_sources_table(sources: dict) -> str:
    body_rows = []
    for key, src in sources.items():
        sid = esc(src["id"])
        url = esc(src["url"])
        title = esc(src["title"])
        pub = esc(f'{src["publisher"]} ({src["jurisdiction"]})')
        vdate = esc(f'Verified live {src["verified_date"]}')
        scope = esc(src["scope"])
        body_rows.append(
            f'<tr id="{sid}" data-status-group="verified">'
            f'<td class="col-id"><a href="#{sid}">{sid}</a></td>'
            f'<td class="col-cat">{title}<br><small>{pub}</small></td>'
            f'<td class="col-val">{vdate}</td>'
            f'<td class="col-analysis">{scope}</td>'
            f'<td class="col-status"><span class="badge badge-ok">Verified Official .gov</span></td>'
            f'<td class="col-sources"><ul class="src-list"><li><a href="{url}" target="_blank" rel="noopener noreferrer">{esc(src["short"])}</a></li></ul></td>'
            f"</tr>"
        )
    return (
        '<section class="section-card" id="official-sources-registry" data-filter-scope>'
        "<h2>Master Registry of Official Government Sources (SRC-01 through SRC-39)</h2>"
        '<p class="section-desc">Every single link below resolves to an official city (.sf.gov), state (.ca.gov), or federal (.gov) primary authority retrieved and verified on November 6, 2026. Zero third-party blogs or commercial listing sites are used.</p>'
        '<div class="filter-bar">'
        '<input type="search" aria-label="Search official sources" placeholder="Search by statute, agency, section number, or topic...">'
        f'<span class="filter-note" data-row-count>{len(body_rows)} of {len(body_rows)} rows shown</span>'
        "</div>"
        '<div class="table-wrap"><table class="data-table">'
        "<thead><tr>"
        '<th scope="col">Source ID</th>'
        '<th scope="col">Official Document &amp; Publisher</th>'
        '<th scope="col">Official Confirmed Value</th>'
        '<th scope="col">Verified Legal / Empirical Scope</th>'
        '<th scope="col">Verification Status</th>'
        '<th scope="col">Official Source Link</th>'
        "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table></div></section>"
    )


def render_layout(current_file: str, page_title: str, hero_desc: str, inner_html: str) -> str:
    nav_links = []
    for fname, short_label, _ in PAGES:
        attrs = []
        if fname == current_file:
            attrs.append('aria-current="page"')
        if fname == "flagged-for-review.html":
            attrs.append('class="nav-flag"')
        attr_str = (" " + " ".join(attrs)) if attrs else ""
        nav_links.append(f'<a href="{fname}"{attr_str}>{esc(short_label)}</a>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page_title)} — SF Outer Sunset (94122) Rent Increase Audit</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <a class="skip-link" href="#main-content">Skip to main content</a>
  <header class="site-header">
    <div class="header-inner">
      <div class="eyebrow">
        <span>Outer Sunset · San Francisco ZIP 94122 · 1940 Two-Unit Property</span>
        <span class="privacy-pill">Privacy Protected: Placeholder Names Only</span>
        <span>Verified: 2026-11-06</span>
      </div>
      <div class="site-title"><a href="index.html">San Francisco Rent Increase Compliance &amp; Legal Scrutiny Dashboard</a></div>
      <p class="site-subtitle">Line-by-line official-source verification across SF Admin. Code Ch. 37, SF Rent Board Rules, California Civil &amp; Government Codes, and Federal Fair Housing Law.</p>
      <nav class="top-nav" aria-label="Dashboard Categories">
        {"".join(nav_links)}
      </nav>
    </div>
  </header>
  <main id="main-content" class="container">
    <section class="page-hero">
      <h1>{esc(page_title)}</h1>
      <p>{esc(hero_desc)}</p>
    </section>
    {inner_html}
  </main>
  <footer class="site-footer">
    <p><strong>Privacy &amp; Verification Notice:</strong> All personal tenant identifiers remain strictly internal; synthetic placeholder names (<em>Alex Morgan, Jordan Taylor, Sam Rivera, Casey Kim, Riley Chen, Quinn Patel</em>) are used throughout while keeping all dates and dollar amounts exact. Every table row links directly to an official <code>.gov</code> source; any value not confirmed by an official government source is left blank in the <em>Official Confirmed Value</em> column and logged on <a href="flagged-for-review.html">Flagged for Review</a>. Informational research audit only—not formal legal representation; free counseling is available from the SF Rent Board (415-252-4600) and <a href="https://www.sf.gov/reports--january-2025--rent-board-referral-listing" target="_blank" rel="noopener noreferrer">official SF referral clinics</a>. <a href="../index.html">Repository Root Overview</a>.</p>
  </footer>
  <script src="assets/filter.js"></script>
</body>
</html>
"""


def load_json(name: str):
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def build_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (ASSETS_DIR / "styles.css").write_text(STYLES_CSS, encoding="utf-8")
    (ASSETS_DIR / "filter.js").write_text(FILTER_JS, encoding="utf-8")

    sources = load_json("sources.json")
    exec_sum = load_json("executive_summary.json")
    units_data = load_json("units_analysis.json")
    rates = load_json("rate_schedule.json")
    legal = load_json("legal_framework.json")
    practices = load_json("practices.json")
    notice = load_json("notice_protocol.json")
    scrutiny = load_json("lawyer_scrutiny.json")
    disc = load_json("discrimination.json")
    repo_audit = load_json("repo_audit.json")
    flagged = load_json("flagged_items.json")

    # 1. index.html
    kpi_cards = []
    for k in exec_sum["kpis"]:
        src = sources[k["source"]]
        kpi_cards.append(
            '<div class="kpi-card">'
            f'<div class="kpi-label">{esc(k["label"])}</div>'
            f'<div class="kpi-value">{esc(k["value"])}</div>'
            f'<div class="kpi-sub">{esc(k["sub"])} · <a href="{esc(src["url"])}" target="_blank" rel="noopener noreferrer">{esc(src["id"])}</a></div>'
            "</div>"
        )
    dir_cards = []
    for fname, label, desc in PAGES[1:]:
        dir_cards.append(
            f'<a class="dir-card" href="{fname}"><strong>{esc(label)}</strong><span>{esc(desc)}</span></a>'
        )

    exec_callouts = """
    <div class="callout-grid">
      <div class="callout">
        <h2>Executive Summary: Core Legal &amp; Financial Findings</h2>
        <ul>
          <li><strong>SF Rent Control Governs (1.6% Annual Cap):</strong> A 1940 two-unit Outer Sunset (94122) building is governed by SF Admin. Code Ch. 37—not California AB 1482's 8.8% cap. Published annual rate for <strong>3/1/2026–2/28/2027 is 1.6%</strong> of base rent (never rounded up, never compounded).</li>
          <li><strong>Mandatory Licensing Gate (§37.15):</strong> Confirm an active SF Rent Increase License via annual March 1 Housing Inventory reporting on <code>portal.sfrb.org</code> before serving any notice; noncompliance suspends the increase.</li>
          <li><strong>Unit 1 (<em>Alex Morgan &amp; Casey Kim</em> — $3,995.00/mo):</strong> Zero vacancy reset or roommate fee is lawful while original co-tenant <em>Alex Morgan</em> resides in Unit 1. Verify first that the 4/1/2026 continuing tenancy is month-to-month (not a 12-month fixed term). Recommended uniform 1.6% = <strong>+$63.92/mo → $4,058.92/mo</strong> (waiting until <strong>2/1/2027</strong> preserves or allows banking the 1.4% = +$55.93 skipped 2026 rate for 3.0% = $4,114.85/mo).</li>
          <li><strong>Unit 2 (<em>Riley Chen &amp; Quinn Patel</em> — $3,150.00/mo since 6/1/2019):</strong> Recommended uniform 1.6% current annual increase = <strong>+$50.40/mo → $3,200.40/mo</strong> on 30/35-day written notice, keeping up to 11.5% ($362.25/mo) lawfully banked without expiring and avoiding a high-scrutiny 13.1% ($412.65/mo) 90/95-day shock notice.</li>
        </ul>
      </div>
      <div class="callout">
        <h2>Executive Summary: Fair Housing &amp; Tenant-Lawyer Verdict</h2>
        <ul>
          <li><strong>Both Units Under One Neutral Policy (Recommended):</strong> Adopting a written building-wide policy applying the identical <strong>1.6% current SF annual CPI percentage</strong> to both Unit 1 and Unit 2 on each unit's earliest lawful month-to-month eligibility date eliminates 1-vs-1 comparator claims under 42 U.S.C. §3604, California FEHA (Gov. Code §12955), Unruh (Civ. Code §51), and SF §37.10B(a)(9).</li>
          <li><strong>Corporate vs. Individual Practice:</strong> SF Admin. Code §37.10C bans corporate algorithmic pricing software ($1,000/unit/mo penalty); small 2-unit owners rely on Form 571 CPI schedules and banking rules.</li>
          <li><strong>Pre-Service Audit:</strong> Clear all pending repairs/habitability issues (Civ. Code §1942.4 / 180-day §1942.5 bar), itemize notices in writing, and add <strong>+5 calendar days</strong> when serving by California mail (CCP §1013(a)).</li>
        </ul>
      </div>
    </div>
    """

    index_inner = (
        '<div class="kpi-grid">' + "".join(kpi_cards) + "</div>"
        + exec_callouts
        + '<section class="section-card"><h2>Category Subpages</h2><p class="section-desc">Explore each verified research area, calculation schedule, legal audit checklist, and flagged item register below.</p><div class="dir-grid">'
        + "".join(dir_cards)
        + "</div></section>"
        + render_table_section(
            "executive-summary-table",
            "Executive Summary Verification Matrix (Line-by-Line)",
            "Every headline conclusion cross-referenced to verified official .gov sources. Private/conditional values leave the Official Confirmed Value cell blank and flag underlying private assumptions for owner verification.",
            exec_sum["rows"],
            sources,
        )
    )
    (OUT_DIR / "index.html").write_text(
        render_layout("index.html", PAGES[0][1], PAGES[0][2], index_inner), encoding="utf-8"
    )

    # 2. units-analysis.html
    units_inner = (
        render_table_section(
            "unit-profiles",
            "Anonymized Property & Unit Tenancy Baseline (Privacy-Protected Placeholders)",
            "Synthetic placeholder names replace all personal tenant information while keeping dates and dollar amounts unchanged. Official Confirmed Value cells are left blank because private leases are not public government records.",
            units_data["profiles"],
            sources,
            include_filter=False,
        )
        + render_table_section(
            "official-rate-schedule",
            "Official SF Rent Board Annual Allowable Rent Increase Schedule (2019–2027 — Form 571)",
            "Verified line by line from official SF Rent Board Form 571 (571_Allowable_Annual_Increases_26-27_1.pdf). The March 1, 2027–February 29, 2028 rate is not yet published as of November 6, 2026 and is left blank and flagged.",
            rates,
            sources,
            include_filter=False,
        )
        + render_table_section(
            "unit-scenarios",
            "Unit 1 & Unit 2 Conditional Rent Increase & Banking Scenarios (Exact Unrounded Cents)",
            "All dollar figures are computed on base rent only without compounding and without rounding up (SF Rent Board Rule 4.12(a)).",
            units_data["scenarios"],
            sources,
        )
    )
    (OUT_DIR / "units-analysis.html").write_text(
        render_layout("units-analysis.html", PAGES[1][1], PAGES[1][2], units_inner), encoding="utf-8"
    )

    # 3. legal-framework.html
    legal_inner = render_table_section(
        "legal-matrix",
        "San Francisco (94122), California State & Federal Rent Increase Requirements",
        "Every row links directly to enacted SF Administrative Code sections, SF Rent Board Rules & Regulations, California Legislative Information statutes, or U.S. Code / agency guidance.",
        legal,
        sources,
    )
    (OUT_DIR / "legal-framework.html").write_text(
        render_layout("legal-framework.html", PAGES[2][1], PAGES[2][2], legal_inner), encoding="utf-8"
    )

    # 4. market-practices.html
    practices_inner = render_table_section(
        "corporate-vs-individual",
        "Institutional Real Estate Corporations vs. Individual Property Owners in San Francisco",
        "Empirical and statutory comparison grounded in the 2024 HUD/Census Rental Housing Finance Survey, SF Admin. Code §37.10C (algorithmic pricing prohibition), U.S. DOJ antitrust filings, and SF Rent Board Housing Inventory / petition rules.",
        practices,
        sources,
    )
    (OUT_DIR / "market-practices.html").write_text(
        render_layout("market-practices.html", PAGES[3][1], PAGES[3][2], practices_inner), encoding="utf-8"
    )

    # 5. notice-protocol.html
    notice_inner = (
        render_table_section(
            "service-steps",
            "Mandatory 5-Step Statutory Tenant Notification Protocol",
            "Exact procedural sequence required under Cal. Civ. Code §827, Cal. Code Civ. Proc. §1013(a), SF Admin. Code §37.15, and SF Rent Board Rules §§4.10 & 4.12.",
            notice["steps"],
            sources,
            include_filter=False,
        )
        + render_table_section(
            "lawful-vs-unlawful-reasons",
            "Lawful Business Grounds vs. Unlawful / Prohibited Reasons for a Rent Increase",
            "Distinguishes self-executing annual/banked CPI adjustments and petition-approved passthroughs from unlawful market resets, roommate surcharges, and retaliatory/discriminatory motives.",
            notice["reasons"],
            sources,
        )
    )
    (OUT_DIR / "notice-protocol.html").write_text(
        render_layout("notice-protocol.html", PAGES[4][1], PAGES[4][2], notice_inner), encoding="utf-8"
    )

    # 6. lawyer-scrutiny.html
    scrutiny_inner = render_table_section(
        "lawyer-audit-checklist",
        "12-Point SF Tenant-Advocate & Free Legal Counsel Red-Team Audit",
        "Evaluates the proposed rent increases through the exact intake checklist used by San Francisco tenant attorneys and Outer Sunset (94122) legal clinics so the owner operates cleanly within normal, defensible business practice.",
        scrutiny,
        sources,
    )
    (OUT_DIR / "lawyer-scrutiny.html").write_text(
        render_layout("lawyer-scrutiny.html", PAGES[5][1], PAGES[5][2], scrutiny_inner), encoding="utf-8"
    )

    # 7. discrimination-analysis.html
    disc_inner = render_table_section(
        "one-vs-both-units",
        "Raising One Unit vs. Raising Both Units — Fair Housing, Retaliation & Harassment Analysis",
        "Compares single-unit vs. building-wide rent adjustment options under 42 U.S.C. §3604, California FEHA (Gov. Code §12955), Unruh Civil Rights Act (Civ. Code §51), Civ. Code §1942.5, and SF Admin. Code §37.10B.",
        disc,
        sources,
    )
    (OUT_DIR / "discrimination-analysis.html").write_text(
        render_layout("discrimination-analysis.html", PAGES[6][1], PAGES[6][2], disc_inner), encoding="utf-8"
    )

    # 8. repo-verification.html
    repo_inner = render_table_section(
        "repo-audit-table",
        "Line-by-Line Verification Audit of Existing Repository Files",
        "Documents line-by-line review of pre-existing repository files and external citations without overwriting other active sessions' claimed scopes.",
        repo_audit,
        sources,
    )
    (OUT_DIR / "repo-verification.html").write_text(
        render_layout("repo-verification.html", PAGES[7][1], PAGES[7][2], repo_inner), encoding="utf-8"
    )

    # 9. flagged-for-review.html
    flagged_inner = render_table_section(
        "flagged-items-register",
        "Flagged for Review — Unverified Inputs, Blank Official Values & Source/Repo Irregularities",
        "Items below require internal owner verification against private lease/ledger records or reflect unpublished future rates and external source irregularities. Per project protocol, flagged items are published transparently with official links and do not block deployment.",
        flagged,
        sources,
    )
    (OUT_DIR / "flagged-for-review.html").write_text(
        render_layout("flagged-for-review.html", PAGES[8][1], PAGES[8][2], flagged_inner), encoding="utf-8"
    )

    # 10. sources.html
    sources_inner = render_sources_table(sources)
    (OUT_DIR / "sources.html").write_text(
        render_layout("sources.html", PAGES[9][1], PAGES[9][2], sources_inner), encoding="utf-8"
    )


if __name__ == "__main__":
    build_all()
    print(f"Built {len(PAGES)} dashboard pages in {OUT_DIR}")
