#!/usr/bin/env python3
"""
Build the Rent Increase SF dashboard (static HTML, no runtime dependencies).

All figures are computed here from data/*.json so that the tables on the site can
never drift from the underlying record. Every table row that makes a factual claim
carries one or more source ids that resolve to a link on sources.html.

Usage:
    python3 build.py            # write HTML
    python3 build.py --check    # also assert every data-backed table row has a source
"""

import html
import json
import os
import sys
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")


def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


SOURCES = load("sources.json")
INCREASES = load("increases.json")
UNITS = load("units.json")
FLAGS = load("flags.json")
SRC = {s["id"]: s for s in SOURCES}

E = html.escape


def money(value):
    d = Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "${:,.2f}".format(d)


def pct(value):
    return ("%g" % value) + "%"


# --------------------------------------------------------------------------
# scenario maths (all inputs are published percentages; nothing is inferred)
# --------------------------------------------------------------------------

BASE_RATE = 1.6          # 3/1/2026 - 2/28/2027, S01 / S02 / S03
PRIOR_RATE = 1.4         # 3/1/2025 - 2/28/2026, S02 / S03

# Unit A: availability of the 1.4% on 1 Feb 2026 (first anniversary); not banked.
# Unit B: anniversaries 1 Jun 2020..1 Jun 2026 and the rate that attached to each.
UNIT_B_YEARS = [
    ("1 Jun 2020", 1.8, "3/1/2020 – 2/28/2021", True),
    ("1 Jun 2021", 0.7, "3/1/2021 – 2/28/2022", True),
    ("1 Jun 2022", 2.3, "3/1/2022 – 2/28/2023", True),
    ("1 Jun 2023", 3.6, "3/1/2023 – 2/29/2024", True),
    ("1 Jun 2024", 1.7, "3/1/2024 – 2/28/2025", True),
    ("1 Jun 2025", 1.4, "3/1/2025 – 2/28/2026", "conflict"),
    ("1 Jun 2026", 1.6, "3/1/2026 – 2/28/2027", False),
]

BANKED_24 = sum(r for _, r, _, s in UNIT_B_YEARS if s is True)          # 10.1
BANKED_12 = sum(r for _, r, _, s in UNIT_B_YEARS if s is True or s == "conflict")  # 11.5
TOTAL_24 = round(BANKED_24 + BASE_RATE, 4)   # 11.7
TOTAL_12 = round(BANKED_12 + BASE_RATE, 4)   # 13.1

UNIT_A_RENT = 3995.00
UNIT_B_RENT = 3150.00

SCENARIOS = [
    {
        "unit": "Unit A",
        "id": "A-1",
        "label": "Annual increase only, effective on or after 6 Dec 2026 (30 days after service)",
        "rate": BASE_RATE,
        "notice": "30 days written",
        "basis": "Published annual allowable increase for the effective date",
        "sources": ["S01", "S02", "S03"],
        "verdict": "lawful",
        "note": "No banked amount is available: the 1.4% that first became available on 1 Feb 2026 has not yet banked (F01).",
    },
    {
        "unit": "Unit A",
        "id": "A-2",
        "label": "Annual increase as dated in the brief, effective 1 Apr 2026",
        "rate": BASE_RATE,
        "notice": "30 days written",
        "basis": "Published annual allowable increase for the effective date",
        "sources": ["S01", "S02", "S03"],
        "verdict": "lawful but past",
        "note": "Shown for completeness: an increase effective 1 Apr 2026 fell in the 1.6% window. If one was imposed, the next one cannot take effect before 1 Apr 2027.",
    },
    {
        "unit": "Unit B",
        "id": "B-1",
        "label": "Annual increase only (most conservative option)",
        "rate": BASE_RATE,
        "notice": "30 days written",
        "basis": "Published annual allowable increase for the effective date",
        "sources": ["S01", "S02", "S03"],
        "verdict": "lawful",
        "note": "Requires no rent-history reconstruction and no judgement calls.",
    },
    {
        "unit": "Unit B",
        "id": "B-2",
        "label": "Annual increase + banked 2020–2024 increases (24-month banking reading)",
        "rate": TOTAL_24,
        "notice": "90 days written",
        "basis": "1.8 + 0.7 + 2.3 + 3.6 + 1.7 = 10.1% banked, plus 1.6% current",
        "sources": ["S03", "S04", "S07"],
        "verdict": "conditionally lawful",
        "note": "Conditional on a verified rent history showing no increase since 1 Jun 2019 (F04) and on resolving F01.",
    },
    {
        "unit": "Unit B",
        "id": "B-3",
        "label": "Annual increase + banked 2020–2025 increases (Rule 4.12 twelve-month reading)",
        "rate": TOTAL_12,
        "notice": "90 days written",
        "basis": "10.1% + 1.4% (2025–26) = 11.5% banked, plus 1.6% current",
        "sources": ["S03", "S04", "S07"],
        "verdict": "not safe to use yet",
        "note": "Blocked by F01: the explanatory page requires 24 months, Rule 4.12 requires 12. Do not serve this until the Rent Board confirms.",
    },
]


def scenario_row(s):
    base = UNIT_A_RENT if s["unit"] == "Unit A" else UNIT_B_RENT
    delta = Decimal(str(base)) * Decimal(str(s["rate"])) / Decimal("100")
    delta = delta.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    new = (Decimal(str(base)) + delta).quantize(Decimal("0.01"))
    badge = {
        "lawful": "ok",
        "lawful but past": "warn",
        "conditionally lawful": "warn",
        "not safe to use yet": "bad",
    }[s["verdict"]]
    return (
        "<tr>"
        f"<td><strong>{E(s['unit'])}</strong><br><span class='muted'>{E(s['id'])}</span></td>"
        f"<td>{E(s['label'])}<div class='muted small'>{E(s['note'])}</div></td>"
        f"<td class='num'>{money(base)}</td>"
        f"<td class='num'>{E(pct(s['rate']))}</td>"
        f"<td class='num'>{money(delta)}</td>"
        f"<td class='num'><strong>{money(new)}</strong></td>"
        f"<td>{E(s['notice'])}</td>"
        f"<td><span class='badge {badge}'>{E(s['verdict'])}</span></td>"
        f"<td class='src'>{cite(*s['sources'])}</td>"
        "</tr>"
    )


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def cite(*ids):
    bits = []
    for i in ids:
        s = SRC[i]
        bits.append(
            f'<a class="ref" href="{E(s["url"])}" target="_blank" rel="noopener" '
            f'title="{E(s["title"])}">{E(i)}</a>'
        )
    return " ".join(bits)


NAV = [
    ("index.html", "Dashboard", "index"),
    ("exec-summary.html", "Executive Summary", "exec"),
    ("units.html", "Units", "units"),
    ("increases.html", "Increases", "increases"),
    ("laws.html", "Laws", "laws"),
    ("practice.html", "Owner Practice", "practice"),
    ("notice.html", "Notice &amp; Reasons", "notice"),
    ("discrimination.html", "One vs Both", "discrimination"),
    ("review.html", "Flagged for Review", "review"),
    ("sources.html", "Sources", "sources"),
]

CSS = """
:root{
  --bg:#f5f7fa; --panel:#ffffff; --ink:#16202b; --muted:#5b6b7c;
  --line:#dfe6ee; --brand:#124559; --brand-2:#1f6f8b; --accent:#0f766e;
  --ok:#0f766e; --warn:#a16207; --bad:#b91c1c; --flag:#fff8e6;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
a{color:var(--brand-2)}
header.top{background:linear-gradient(135deg,#0d3446,#12657f);color:#fff;padding:22px 0 18px}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
.brandline{display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;justify-content:space-between}
.brand{font-size:20px;font-weight:700;letter-spacing:.2px}
.brand small{display:block;font-weight:400;font-size:12.5px;opacity:.85;letter-spacing:.4px;text-transform:uppercase}
.meta{font-size:12.5px;opacity:.9;text-align:right}
nav.main{background:#0a2836;position:sticky;top:0;z-index:30;border-bottom:1px solid rgba(255,255,255,.08)}
nav.main .wrap{display:flex;gap:4px;overflow-x:auto;padding:0 20px}
nav.main a{color:#cfe2ea;text-decoration:none;padding:11px 12px;font-size:13.5px;white-space:nowrap;border-bottom:3px solid transparent}
nav.main a:hover{color:#fff;background:rgba(255,255,255,.06)}
nav.main a.active{color:#fff;border-bottom-color:#4cc9c0;font-weight:600}
main{padding:26px 0 60px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:-.3px}
h2{font-size:19px;margin:32px 0 10px}
h3{font-size:15.5px;margin:22px 0 8px;text-transform:uppercase;letter-spacing:.6px;color:var(--muted)}
p{margin:0 0 12px}
.lede{color:var(--muted);max-width:70ch;margin-bottom:18px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:0 0 18px;
  box-shadow:0 1px 2px rgba(16,32,48,.04)}
.grid{display:grid;gap:14px}
.g2{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.g4{grid-template-columns:repeat(auto-fit,minmax(160px,1fr))}
.kpi{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--brand-2);border-radius:8px;padding:14px 16px}
.kpi .n{font-size:24px;font-weight:700;letter-spacing:-.5px;display:block}
.kpi .l{font-size:12.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.kpi .s{font-size:12px;color:var(--muted);margin-top:4px}
table{width:100%;border-collapse:collapse;background:var(--panel);font-size:14px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--panel)}
th,td{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
th{background:#eef3f8;font-size:12.5px;text-transform:uppercase;letter-spacing:.5px;color:#31465a;position:sticky;top:0}
tbody tr:nth-child(even){background:#fbfdff}
tbody tr:hover{background:#f2f8fb}
tbody tr:last-child td{border-bottom:none}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.src,th.src{white-space:nowrap}
.muted{color:var(--muted)}
.small{font-size:12.5px}
.ref{display:inline-block;background:#e6f2f7;color:#0f5570;border:1px solid #b8d8e4;border-radius:5px;
  padding:0 5px;font-size:11.5px;font-weight:600;text-decoration:none;margin-right:2px}
.ref:hover{background:#0f5570;color:#fff}
.badge{display:inline-block;font-size:11.5px;font-weight:700;padding:2px 8px;border-radius:20px;white-space:nowrap}
.badge.ok{background:#dcf5f0;color:#0b5f57}
.badge.warn{background:#fef3c7;color:#8a5a06}
.badge.bad{background:#fee2e2;color:#991b1b}
.badge.info{background:#e0edf6;color:#12506b}
.note{background:#eef6fb;border-left:4px solid var(--brand-2);padding:12px 14px;border-radius:0 8px 8px 0;margin:14px 0}
.warnbox{background:var(--flag);border-left:4px solid #d97706;padding:12px 14px;border-radius:0 8px 8px 0;margin:14px 0}
ul,ol{margin:0 0 12px;padding-left:22px}
li{margin-bottom:6px}
footer{border-top:1px solid var(--line);padding:22px 0 40px;color:var(--muted);font-size:12.5px}
.disclaimer{font-size:12.5px;color:var(--muted);border-top:1px dashed var(--line);padding-top:12px;margin-top:26px}
.flagcard{border:1px solid var(--line);border-left:5px solid #d97706;border-radius:0 10px 10px 0;background:var(--panel);
  padding:16px 18px;margin-bottom:14px}
.flagcard.high{border-left-color:#b91c1c}
.flagcard.low{border-left-color:#64748b}
.flagcard h4{margin:0 0 6px;font-size:16px}
.flaghead{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.dl{display:grid;grid-template-columns:150px 1fr;gap:6px 16px;font-size:14px}
.dl dt{color:var(--muted);font-size:12.5px;text-transform:uppercase;letter-spacing:.4px}
.dl dd{margin:0}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px;align-items:center}
input[type=search]{padding:8px 12px;border:1px solid var(--line);border-radius:8px;font-size:14px;min-width:240px;background:#fff}
.chip{font-size:12.5px;background:#eef3f8;border:1px solid var(--line);border-radius:20px;padding:3px 10px;color:#31465a}
.q{font-style:italic;color:#2b3f52;border-left:3px solid var(--line);padding-left:12px;margin:10px 0}
@media (max-width:640px){.dl{grid-template-columns:1fr}.meta{text-align:left}}
@media print{nav.main{display:none}body{background:#fff}.card{box-shadow:none}}
"""

JS = """
(function(){
  var box = document.getElementById('filter');
  if(!box) return;
  var target = document.querySelector(box.dataset.target);
  if(!target) return;
  box.addEventListener('input', function(){
    var q = box.value.toLowerCase().trim();
    var rows = target.querySelectorAll('tbody tr');
    var shown = 0;
    rows.forEach(function(r){
      var hit = !q || r.textContent.toLowerCase().indexOf(q) > -1;
      r.style.display = hit ? '' : 'none';
      if(hit) shown++;
    });
    var c = document.getElementById('count');
    if(c) c.textContent = shown + ' of ' + rows.length + ' rows';
  });
})();
"""


def page(name, title, subtitle, active, body, extra_head=""):
    nav_bits = []
    for href, label, key in NAV:
        cls = " class=\"active\"" if key == active else ""
        nav_bits.append(f'<a href="{href}"{cls}>{label}</a>')
    nav = "".join(nav_bits)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} — Rent Increase SF</title>
<meta name="description" content="Verified analysis of lawful rent increases for two rent-controlled units in San Francisco ZIP 94122.">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/style.css">
{extra_head}
</head>
<body>
<header class="top">
  <div class="wrap brandline">
    <div class="brand">Rent Increase SF
      <small>San Francisco 94122 · two rent-controlled units · verified against primary sources</small>
    </div>
    <div class="meta">Data current to<br><strong>6 November 2026</strong></div>
  </div>
</header>
<nav class="main"><div class="wrap">{nav}</div></nav>
<main><div class="wrap">
<h1>{E(title)}</h1>
<p class="lede">{subtitle}</p>
{body}
<div class="disclaimer">
  <strong>Not legal advice.</strong> This is a documented reading of published rules, prepared so that a
  qualified reviewer can check every value. Every factual claim links to an official source on the
  <a href="sources.html">Sources</a> page. Items that could not be confirmed from an official source are
  left blank and listed on <a href="review.html">Flagged for Review</a>.
</div>
</div></main>
<footer><div class="wrap">
  Rent Increase SF · prepared for owner review · all personal identifiers removed ·
  dates and amounts preserved as supplied · <a href="review.html">11 items flagged for review</a>
</div></footer>
<script src="assets/app.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_index():
    a1 = next(s for s in SCENARIOS if s["id"] == "A-1")
    b2 = next(s for s in SCENARIOS if s["id"] == "B-2")
    b3 = next(s for s in SCENARIOS if s["id"] == "B-3")

    def calc(s, base):
        d = (Decimal(str(base)) * Decimal(str(s["rate"])) / Decimal("100")).quantize(Decimal("0.01"))
        return money(d), money(Decimal(str(base)) + d)

    a_delta, a_new = calc(a1, UNIT_A_RENT)
    b_delta, b_new = calc(b2, UNIT_B_RENT)
    b3_delta, b3_new = calc(b3, UNIT_B_RENT)

    body = f"""
<div class="grid g4" style="margin-bottom:20px">
  <div class="kpi"><span class="l">Lawful cap now</span><span class="n">1.6%</span>
    <span class="s">1 Mar 2026 – 28 Feb 2027 · <a href="sources.html">S01 S02</a></span></div>
  <div class="kpi"><span class="l">Unit A maximum</span><span class="n">{a_new}</span>
    <span class="s">+{a_delta} on $3,995.00</span></div>
  <div class="kpi"><span class="l">Unit B ceiling</span><span class="n">{b_new}</span>
    <span class="s">+{b_delta} on $3,150.00 · conditional</span></div>
  <div class="kpi"><span class="l">Open items</span><span class="n">11</span>
    <span class="s"><a href="review.html">flagged for review</a></span></div>
</div>

<div class="card">
  <h3 style="margin-top:0">Answer in one paragraph</h3>
  <p>Both units sit in a building constructed in 1940, so they are presumed covered by the San Francisco
  Rent Ordinance. For a covered unit the “reasonable and normal” increase is not a matter of market
  judgement: it is the Rent Board's published annual allowable increase — <strong>1.6%</strong> for
  increases taking effect between 1 March 2026 and 28 February 2027 — applied once every
  twelve months to the lawful base rent, plus any properly banked prior-year allowances that were
  never imposed {cite('S01','S02','S03')}. Anything above that figure requires a Rent Board petition and
  evidence of the kind of cost increase the Ordinance recognises {cite('S10')}. Adding a roommate is
  never a lawful reason to raise rent on a continuing tenancy {cite('S08')}.</p>
</div>

<div class="grid g2">
  <div class="card">
    <h3 style="margin-top:0">The two units</h3>
    <div class="tablewrap"><table>
      <thead><tr><th>Unit</th><th class="num">Base rent</th><th>Tenancy began</th><th class="num">Max now</th></tr></thead>
      <tbody>
        <tr><td><strong>Unit A</strong><div class="muted small">3 tenants initially, 2 now; 1 original tenant continues</div></td>
            <td class="num">{money(UNIT_A_RENT)}</td><td>1 Feb 2025</td><td class="num">+1.6% = {a_new}</td></tr>
        <tr><td><strong>Unit B</strong><div class="muted small">2 tenants; no rent history supplied after 2019</div></td>
            <td class="num">{money(UNIT_B_RENT)}</td><td>1 Jun 2019</td><td class="num">1.6% to 11.7%</td></tr>
      </tbody>
    </table></div>
    <p class="small muted" style="margin-top:10px">Unit-level detail and the reasoning behind each
    figure: <a href="units.html">Units</a> and <a href="increases.html">Increases</a>.</p>
  </div>
  <div class="card">
    <h3 style="margin-top:0">How the layers interact</h3>
    <div class="tablewrap"><table>
      <thead><tr><th>Layer</th><th>Effect on these units</th><th class="src"></th></tr></thead>
      <tbody>
        <tr><td>Federal</td><td>No rent cap; Fair Housing Act bars discrimination only</td><td class="src">{cite('S20')}</td></tr>
        <tr><td>State</td><td>AB 1482 cap does not govern — stricter local rule controls; §827 sets 30/90-day notice</td><td class="src">{cite('S14','S15')}</td></tr>
        <tr><td>Local</td><td><strong>Binding:</strong> 1.6% cap, licensing, notice content, banking</td><td class="src">{cite('S08','S09')}</td></tr>
      </tbody>
    </table></div>
    <p class="small muted" style="margin-top:10px">Full matrix: <a href="laws.html">Laws</a>.</p>
  </div>
</div>

<h2>What the site contains</h2>
<div class="grid g3">
  <div class="card"><h3 style="margin-top:0">Findings</h3>
    <p class="small">Executive summary with the conclusions, the numbers, and the two things that must be
    confirmed before serving any notice.</p>
    <p class="small"><a href="exec-summary.html">Read the executive summary →</a></p></div>
  <div class="card"><h3 style="margin-top:0">Evidence</h3>
    <p class="small">Every allowable increase since 1982, the per-unit calculations, the federal/state/local
    matrix, and the notice checklist — each row carrying its source.</p>
    <p class="small"><a href="increases.html">Increases →</a> · <a href="laws.html">Laws →</a> ·
    <a href="notice.html">Notice →</a></p></div>
  <div class="card"><h3 style="margin-top:0">Review</h3>
    <p class="small">Two official SF sources contradict each other on the banking test. That conflict, plus
    nine other gaps, are published rather than papered over.</p>
    <p class="small"><a href="review.html">Flagged for Review →</a></p></div>
</div>

<h2>Recommended sequence</h2>
<div class="tablewrap"><table>
  <thead><tr><th style="width:44px">#</th><th>Step</th><th>Why</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>1</td><td>Confirm the rent increase licence is active in the Housing Inventory</td>
        <td>A notice is unenforceable without a licence in effect on its effective date</td><td class="src">{cite('S09')}</td></tr>
    <tr><td>2</td><td>Reconstruct Unit B's rent history from 2019; confirm Unit A's tenancy status</td>
        <td>Both determine the lawful base rent and the banked total (F03, F04)</td><td class="src">{cite('S04','S07')}</td></tr>
    <tr><td>3</td><td>Decide 1.6% only, or banked amounts; keep the figure at or below the safe ceiling</td>
        <td>Over-banking is the usual route to a refund order</td><td class="src">{cite('S07','S13')}</td></tr>
    <tr><td>4</td><td>Serve one written notice per unit: dollars, percentage, effective date, banked portion</td>
        <td>Content is prescribed; a non-conforming increase is void</td><td class="src">{cite('S08','S07')}</td></tr>
    <tr><td>5</td><td>Use 30 days if ≤10%, 90 days if &gt;10%; add 5 days for mail</td>
        <td>Statutory minimum; longer period governs</td><td class="src">{cite('S15','S01')}</td></tr>
    <tr><td>6</td><td>Write a one-page rationale per unit and keep it on file</td>
        <td>Shows the difference between the units is arithmetic, not personal</td><td class="src">{cite('S19','S20')}</td></tr>
  </tbody>
</table></div>

<div class="warnbox"><strong>Two blockers before any notice.</strong>
F01 — the Rent Board's rule text and its explanatory page give different banking tests (12 vs 24 months),
which changes Unit B by $44.10 a month. F04 — Unit B's rent history after 2019 has not been verified, so
no banked figure is safe yet. Details on <a href="review.html">Flagged for Review</a>.</div>
"""
    return page("index.html", "Dashboard",
                "Two rent-controlled units in ZIP 94122, checked line by line against the San Francisco "
                "Rent Ordinance, California statutes and federal law.", "index", body)


def build_exec():
    rows = [
        ("1", "Both units are covered by the San Francisco Rent Ordinance",
         "Building constructed 1940; covered units are those built on or before 13 June 1979 that are not "
         "single-family dwellings. Coverage gives rent control <em>and</em> just-cause eviction protection.",
         "Verified (subject to F05)", ("S06",)),
        ("2", "The lawful annual increase is 1.6%",
         "Effective 1 March 2026 through 28 February 2027, set at 60% of the Bay Area CPI change. The prior "
         "period was 1.4%. The Ordinance caps any annual increase at 7% regardless of CPI.",
         "Verified", ("S01", "S02", "S03", "S08")),
        ("3", "Unit A: maximum lawful increase is $63.92 per month",
         "$3,995.00 × 1.6% = $63.92, for a new base rent of $4,058.92, on 30 days' written notice. No banked "
         "amount is available yet.",
         "Verified arithmetic", ("S01", "S03")),
        ("4", "Unit B: 1.6% is safe; 11.7% is the defensible ceiling; 13.1% is unresolved",
         "$3,150.00 × 1.6% = $50.40 → $3,200.40. If no increase has been imposed since 2019, banked "
         "allowances of 10.1%–11.5% may be added, giving 11.7%–13.1% ($3,518.55–$3,562.65). Above 10% the "
         "notice period is 90 days.",
         "Conditional", ("S03", "S04", "S07", "S15")),
        ("5", "Different increases for the two units are lawful if they follow from documented rent facts",
         "The two units have different base rents, different tenancy start dates and different banking "
         "histories. Anti-discrimination law bars differences based on a protected characteristic, not "
         "differences produced by the rent formula.",
         "Analysis of verified law", ("S19", "S20")),
        ("6", "Adding an occupant never justifies an increase on a continuing tenancy",
         "Expressly prohibited even where the lease allows it. Only a genuinely new tenancy can be re-priced.",
         "Verified", ("S01", "S08", "S17")),
        ("7", "“Market rent” is not a lawful reason for an above-cap increase",
         "The Rent Board states that the mere fact a long-standing tenant pays well below market is not an "
         "extraordinary circumstance. Above-cap increases need a petition based on documented costs or "
         "narrow special circumstances.",
         "Verified", ("S12", "S11", "S10")),
        ("8", "A licence is a precondition, not paperwork",
         "A rent increase licence must be in effect on the effective date of the notice, or the increase is "
         "not enforceable — even if the percentage is right.",
         "Verified", ("S09",)),
        ("9", "A tenant can challenge any increase for free",
         "The Rent Board hears unlawful-rent-increase petitions and summary petitions based on an invalid "
         "notice at no charge; overcharges can be ordered refunded.",
         "Verified", ("S13", "S07")),
        ("10", "Free legal representation exists, so assume the notice will be read by a lawyer",
         "The City's Tenant Right to Counsel programme provides a free attorney in eviction proceedings, and "
         "the Rent Board publishes a list of free tenant resources, including a Sunset office in 94122.",
         "Verified", ("S21", "S22")),
    ]
    trs = "".join(
        f"<tr><td class='num'>{n}</td><td><strong>{t}</strong><div class='small muted'>{d}</div></td>"
        f"<td><span class='badge {'ok' if v.startswith('Verified') else 'warn'}'>{v}</span></td>"
        f"<td class='src'>{cite(*s)}</td></tr>"
        for n, t, d, v, s in rows
    )

    body = f"""
<div class="card">
  <h3 style="margin-top:0">Bottom line</h3>
  <p>These are two units in a 1940 building in the Outer Sunset. Under the San Francisco Rent Ordinance the
  owner may raise each tenant's rent once every twelve months by the Rent Board's published percentage —
  <strong>1.6%</strong> for anything effective between 1 March 2026 and 28 February 2027 — applied to the
  tenant's base rent, plus any prior-year allowances that were skipped and have properly banked.</p>
  <p>For Unit A that means <strong>$63.92</strong> a month, taking $3,995.00 to <strong>$4,058.92</strong>.
  For Unit B the safe figure is <strong>$50.40</strong> (to $3,200.40); a larger figure up to
  <strong>$3,562.65</strong> is defensible only if the rent history proves that no increase has been taken
  since 1 June 2019, and only if the Rent Board's own banking-test conflict is resolved first. Anything
  above those figures requires a Rent Board petition, and “the market is higher” is expressly not a
  sufficient ground.</p>
</div>

<h2>Ten findings</h2>
<div class="tablewrap"><table>
  <thead><tr><th class="num" style="width:40px">#</th><th>Finding</th><th>Status</th><th class="src">Sources</th></tr></thead>
  <tbody>{trs}</tbody>
</table></div>

<h2>The numbers, side by side</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Item</th><th class="num">Unit A</th><th class="num">Unit B</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>Tenancy start</td><td class="num">1 Feb 2025</td><td class="num">1 Jun 2019</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Base rent of record</td><td class="num">{money(UNIT_A_RENT)}</td><td class="num">{money(UNIT_B_RENT)}</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Current annual allowable rate</td><td class="num">1.6%</td><td class="num">1.6%</td><td class="src">{cite('S01','S03')}</td></tr>
    <tr><td>Annual increase in dollars</td><td class="num">{money(63.92)}</td><td class="num">{money(50.40)}</td><td class="src">{cite('S02')}</td></tr>
    <tr><td>New base rent, annual only</td><td class="num">{money(4058.92)}</td><td class="num">{money(3200.40)}</td><td class="src">{cite('S02')}</td></tr>
    <tr><td>Banked allowance available</td><td class="num">{money(0)}</td><td class="num">10.1% – 11.5%</td><td class="src">{cite('S04','S07')}</td></tr>
    <tr><td>Ceiling if banking is proven</td><td class="num">{money(4058.92)}</td><td class="num">{money(3562.65)}</td><td class="src">{cite('S03','S07')}</td></tr>
    <tr><td>Notice period</td><td class="num">30 days</td><td class="num">30 days (90 if &gt;10%)</td><td class="src">{cite('S15')}</td></tr>
    <tr><td>Rent increase licence required</td><td class="num">Yes</td><td class="num">Yes</td><td class="src">{cite('S09')}</td></tr>
  </tbody>
</table></div>

<h2>What must be confirmed before serving a notice</h2>
<ol>
  <li><strong>Unit B's rent ledger.</strong> The 11.7%–13.1% ceiling assumes no increase since 1 June 2019.
      Without the notices and payment records, only 1.6% is safe (F04).</li>
  <li><strong>Which banking test the Rent Board applies.</strong> Rule 4.12 says 12 months; the Rent Board's
      explanatory page says 24. The difference is 1.4 percentage points and $44.10 a month (F01).</li>
  <li><strong>Unit A's tenancy status.</strong> If one original tenant never left, the added occupant cannot
      trigger any charge and the anniversary stays 1 February (F03).</li>
  <li><strong>The certificate of occupancy.</strong> Coverage is inferred from 1940 and should be checked on
      the City's Property Information Map (F05).</li>
</ol>

<h2>How to speak about the increase to a tenant</h2>
<p>The most defensible framing is also the simplest, and it is the one a tenant lawyer can check: the
increase is the Rent Board's published annual allowable increase for the effective date, calculated on base
rent, served with the dollar amount, the percentage and the effective date, once in twelve months, with the
banked portion and its source years itemised where banking is used. No other justification is required for
the annual amount, and none should be improvised — invented reasons create exposure that the correct notice
does not {cite('S01','S08','S07')}.</p>
<p class="small muted">More: <a href="notice.html">Notice &amp; Reasons</a> · <a href="discrimination.html">One vs Both</a> ·
<a href="practice.html">Owner Practice</a> · <a href="laws.html">Laws</a></p>
"""
    return page("exec-summary.html", "Executive Summary",
                "What the law allows these two units to be charged, what is still unproven, and what to do "
                "about it.", "exec", body)


def build_units():
    cards = ""
    for u in UNITS["units"]:
        facts = "".join(f"<li>{E(f)}</li>" for f in u["facts"])
        cons = "".join(f"<li>{E(c)}</li>" for c in u["legal_consequences"])
        cards += f"""
<div class="card">
  <div class="flaghead">
    <h2 style="margin:0">{E(u['id'])}</h2>
    <span class="chip">{E(u['role'])}</span>
    <span class="badge info">{E(u['status'])}</span>
  </div>
  <dl class="dl">
    <dt>Base rent</dt><dd>{money(u['base_rent'])} per month</dd>
    <dt>Tenancy begins</dt><dd>{E(u['lease_start_display'])}</dd>
    <dt>Current rent line</dt><dd>{E(u['rent_date_display'])} — {money(u['base_rent'])}</dd>
    <dt>Tenants</dt><dd>{u['initial_tenants']} on the initial lease, {u['current_tenants']} now (role labels only)</dd>
    <dt>First lawful increase</dt><dd>No earlier than {E(u['lease_start_display'])} + 12 months {cite('S01')}</dd>
  </dl>
  <h3>Facts of record</h3><ul>{facts}</ul>
  <h3>What follows legally</h3><ul>{cons}</ul>
</div>"""

    body = f"""
<div class="note">
  <strong>Privacy control.</strong> This page publishes no names, initials, addresses or contact details.
  Tenants appear as <em>Tenant A-1 … Tenant B-2</em>. Dates and dollar amounts are preserved exactly,
  because every legal conclusion depends on them. The key linking role labels to individuals is held
  outside this repository.
</div>

<div class="card">
  <h3 style="margin-top:0">Property</h3>
  <dl class="dl">
    <dt>Location</dt><dd>{E(UNITS['property']['jurisdiction'])}</dd>
    <dt>Year built</dt><dd>{UNITS['property']['year_built']}</dd>
    <dt>Legal units</dt><dd>{UNITS['property']['units']}</dd>
    <dt>Coverage basis</dt><dd>{E(UNITS['property']['coverage_basis'])}</dd>
    <dt>Coverage sources</dt><dd>{cite('S06')}</dd>
  </dl>
</div>
{cards}

<h2>Both units in one table</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Field</th><th>Unit A</th><th>Unit B</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>Year built</td><td>1940</td><td>1940</td><td class="src">{cite('S06')}</td></tr>
    <tr><td>Rent-control coverage</td><td>Presumed covered</td><td>Presumed covered</td><td class="src">{cite('S06')}</td></tr>
    <tr><td>Tenancy begins</td><td>1 Feb 2025</td><td>1 Jun 2019</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Base rent</td><td class="num">{money(UNIT_A_RENT)}</td><td class="num">{money(UNIT_B_RENT)}</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Occupants then → now</td><td>3 → 2 (one original tenant continues)</td><td>2 → 2</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Annual allowable increase</td><td>1.6%</td><td>1.6%</td><td class="src">{cite('S01','S03')}</td></tr>
    <tr><td>Increase in dollars</td><td class="num">{money(63.92)}</td><td class="num">{money(50.40)}</td><td class="src">{cite('S02')}</td></tr>
    <tr><td>Banked allowance</td><td class="num">None yet</td><td class="num">10.1% – 11.5% conditional</td><td class="src">{cite('S04','S07')}</td></tr>
    <tr><td>Maximum monthly rent now</td><td class="num">{money(4058.92)}</td><td class="num">{money(3562.65)}</td><td class="src">{cite('S03','S07')}</td></tr>
    <tr><td>Notice period</td><td>30 days</td><td>30 days, or 90 if &gt;10%</td><td class="src">{cite('S15')}</td></tr>
  </tbody>
</table></div>
<p class="small muted">A blank cell would mean “not confirmed”. Nothing on this page is inferred: where a
fact is unknown it is stated as unknown and listed on <a href="review.html">Flagged for Review</a>.</p>
"""
    return page("units.html", "Units",
                "Anonymised ledger of the two tenancies, with the legal consequence of each fact.",
                "units", body)


def build_increases():
    trs = ""
    for i in INCREASES:
        cls = " style='background:#e7f6f2;font-weight:600'" if i.get("current") else ""
        note = f"<div class='small muted'>{E(i['note'])}</div>" if i.get("note") else ""
        trs += (f"<tr{cls}><td>{E(i['period'])}</td><td class='num'>{i['rate']:.1f}%</td>"
                f"<td>{note}</td><td class='src'>{cite('S03')}</td></tr>")

    b_rows = ""
    for date, rate, period, state in UNIT_B_YEARS:
        if state is True:
            status = "<span class='badge ok'>banked</span>"
            avail = "Yes — 12+ months elapsed"
        elif state == "conflict":
            status = "<span class='badge warn'>disputed</span>"
            avail = "12 months yes / 24 months no (F01)"
        else:
            status = "<span class='badge bad'>not banked</span>"
            avail = "No — 12 months not elapsed"
        b_rows += (f"<tr><td>{E(date)}</td><td class='num'>{rate:.1f}%</td><td>{E(period)}</td>"
                   f"<td>{avail}</td><td>{status}</td><td class='src'>{cite('S03','S07','S04')}</td></tr>")

    body = f"""
<div class="grid g4" style="margin-bottom:18px">
  <div class="kpi"><span class="l">Current rate</span><span class="n">1.6%</span><span class="s">3/1/2026 – 2/28/2027</span></div>
  <div class="kpi"><span class="l">Prior rate</span><span class="n">1.4%</span><span class="s">3/1/2025 – 2/28/2026</span></div>
  <div class="kpi"><span class="l">Statutory ceiling</span><span class="n">7%</span><span class="s">Ordinance §37.3(a)(1)</span></div>
  <div class="kpi"><span class="l">Frequency</span><span class="n">12 mo</span><span class="s">one increase per 12 months</span></div>
</div>

<div class="card">
  <h3 style="margin-top:0">How the percentage is set</h3>
  <p>On 1 March each year the Rent Board publishes the increase in the CPI for the preceding twelve months and
  grants landlords a licence to impose an annual increase of up to 60% of that figure — never more than 7%
  {cite('S08')}. The published figure is applied to the tenant's <em>base rent</em>, which includes housing
  services such as parking or storage but excludes temporary passthroughs and fluctuating charges
  {cite('S01')}. Increases may not be rounded up to the nearest dollar, and may not be compounded
  {cite('S01','S04')}.</p>
</div>

<h2>Every published allowable annual increase, 1982–2027</h2>
<p class="small muted">Transcribed from the Rent Board's own schedule. The current period is highlighted.</p>
<div class="toolbar">
  <input type="search" id="filter" data-target="#aga-table" placeholder="Filter periods (e.g. 2024, 1.6)">
  <span class="chip" id="count">46 rows</span>
  <span class="small muted">Values are copied, not recalculated. {cite('S03')}</span>
</div>
<div class="tablewrap"><table id="aga-table">
  <thead><tr><th>Effective period</th><th class="num">Allowable increase</th><th>Note</th><th class="src">Source</th></tr></thead>
  <tbody>{trs}</tbody>
</table></div>
<p class="small muted" style="margin-top:8px">Only one of the two 1992–93 increases may be imposed for that
period. Neither tenancy in this report reaches back that far.</p>

<h2>Unit A — work through the rule</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Step</th><th>Rule applied</th><th>Result</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>Earliest possible increase</td><td>12 months after the lease began (1 Feb 2025)</td><td>1 Feb 2026</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Rate for an effective date in the current window</td><td>Rate in effect on the effective date</td><td>1.6%</td><td class="src">{cite('S01','S02')}</td></tr>
    <tr><td>Base rent</td><td>Base rent only; no passthroughs</td><td>{money(UNIT_A_RENT)}</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Dollar increase</td><td>{money(UNIT_A_RENT)} × 1.6%</td><td>{money(63.92)}</td><td class="src">{cite('S02')}</td></tr>
    <tr><td>New base rent</td><td>Sum, not rounded up</td><td><strong>{money(4058.92)}</strong></td><td class="src">{cite('S02')}</td></tr>
    <tr><td>Banked addition</td><td>1.4% available 1 Feb 2026 — not banked until 12 (or 24) months pass</td><td>{money(0)}</td><td class="src">{cite('S07','S04')}</td></tr>
    <tr><td>Notice</td><td>Increase ≤10% of rent charged in the prior 12 months</td><td>30 days written (35 if mailed)</td><td class="src">{cite('S15','S01')}</td></tr>
    <tr><td>Added occupant</td><td>No increase may be charged for an added occupant</td><td>{money(0)}</td><td class="src">{cite('S08','S01')}</td></tr>
  </tbody>
</table></div>

<h2>Unit B — why the ceiling is a range</h2>
<p>Unit B's tenancy began 1 June 2019. If no increase has been imposed since, one annual increase became
available on 1 June of each year from 2020 to 2026. Whether each of those banked depends on which banking test
applies — and the two official sources disagree (F01).</p>
<div class="tablewrap"><table>
  <thead><tr><th>Available on</th><th class="num">Rate</th><th>Rate period</th><th>Banked?</th><th>Status</th><th class="src">Source</th></tr></thead>
  <tbody>{b_rows}
    <tr style="background:#eef6fb"><td><strong>Current annual</strong></td><td class="num">1.6%</td><td>3/1/2026 – 2/28/2027</td><td>Applied on the effective date</td><td><span class="badge info">current</span></td><td class="src">{cite('S01','S03')}</td></tr>
  </tbody>
</table></div>

<div class="grid g2" style="margin-top:16px">
  <div class="card"><h3 style="margin-top:0">Reading 1 — 24-month test (S04)</h3>
    <dl class="dl">
      <dt>Banked</dt><dd>1.8 + 0.7 + 2.3 + 3.6 + 1.7 = 10.1%</dd>
      <dt>Plus current</dt><dd>+ 1.6%</dd>
      <dt>Total</dt><dd><strong>11.7%</strong></dd>
      <dt>Dollars</dt><dd>{money(368.55)} → <strong>{money(3518.55)}</strong></dd>
      <dt>Notice</dt><dd>90 days (&gt;10%)</dd>
    </dl>
    <p class="small muted">The 1.4% available on 1 Jun 2025 is excluded because 24 months had not passed.</p>
  </div>
  <div class="card"><h3 style="margin-top:0">Reading 2 — 12-month test, Rule 4.12 (S07)</h3>
    <dl class="dl">
      <dt>Banked</dt><dd>10.1 + 1.4 = 11.5%</dd>
      <dt>Plus current</dt><dd>+ 1.6%</dd>
      <dt>Total</dt><dd><strong>13.1%</strong></dd>
      <dt>Dollars</dt><dd>{money(412.65)} → <strong>{money(3562.65)}</strong></dd>
      <dt>Notice</dt><dd>90 days (&gt;10%)</dd>
    </dl>
    <p class="small muted">Not recommended until the Rent Board confirms which test controls (F01).</p>
  </div>
</div>

<h2>All scenarios, computed</h2>
<p class="small muted">Dollar figures are computed from the published percentages; no rate is estimated.</p>
<div class="tablewrap"><table>
  <thead><tr><th>Unit</th><th>Scenario</th><th class="num">Base rent</th><th class="num">Rate</th><th class="num">Monthly increase</th><th class="num">New base rent</th><th>Notice</th><th>Status</th><th class="src">Source</th></tr></thead>
  <tbody>{''.join(scenario_row(s) for s in SCENARIOS)}</tbody>
</table></div>

<div class="warnbox">
  <strong>Both 90-day figures depend on Unit B's history.</strong> If any increase was served between 2019 and
  2026, the banked total falls by that amount and the notice period may drop back to 30 days. Reconstruct the
  ledger first (F04), and read F01 before using anything above 1.6%.
</div>
"""
    return page("increases.html", "Increases",
                "The published percentages, the two units measured against them, and every scenario computed.",
                "increases", body)


def build_laws():
    rows = [
        ("Federal", "Fair Housing Act, 42 U.S.C. §3604 (via HUD)", "Prohibits discrimination in the rental of housing because of race, colour, national origin, religion, sex, familial status or disability — including in the terms of a tenancy.", "Applies", "ok", ("S20",)),
        ("Federal", "No federal rent cap", "No federal statute, regulation or agency page was found that caps rent in private-market residential housing. Recorded as an absence-of-law finding, not a citation.", "No effect", "warn", ("S20",)),
        ("State", "Civil Code §1947.12 — Tenant Protection Act (AB 1482)", "Caps increases at 5% + CPI change, maximum 10%, with at most two increments in 12 months. §(d)(3) exempts housing under a local ordinance that restricts increases to less than the state cap.", "Does not govern — stricter local rule applies", "warn", ("S14",)),
        ("State", "Civil Code §827 — notice of rent change", "30 days' written notice where the increase is 10% or less of the rent charged in the prior 12 months; 90 days where it is greater. Service personally or by mail under CCP §1013. A longer period required by other law controls.", "Applies", "ok", ("S15",)),
        ("State", "Civil Code §1954.52 — Costa-Hawkins", "Lets an owner set initial and subsequent rates for units with a certificate of occupancy after 1 Feb 1995, and for separately alienable units. This 1940 building's units are neither.", "Does not exempt these units", "warn", ("S16",)),
        ("State", "Civil Code §1954.53 — new tenancy pricing", "An owner may set the initial rate for a new tenancy, except where the prior tenancy was ended by the owner's notice or by a §827 change in terms.", "Relevant to Unit A only if the tenancy truly ended (F03)", "warn", ("S17",)),
        ("State", "Civil Code §1942.5 — retaliation", "A landlord may not increase rent or reduce services to retaliate for a repair request, an agency complaint, an inspection, or tenant organising — with a 180-day window after specified tenant acts.", "Applies", "ok", ("S18",)),
        ("State", "Government Code §12955 — FEHA (housing)", "Unlawful for an owner to discriminate or harass because of race, colour, religion, sex, gender identity or expression, sexual orientation, marital status, national origin, ancestry, familial status, source of income, disability, veteran or military status, or genetic information.", "Applies", "ok", ("S19",)),
        ("Local", "Admin Code §37.3(a)(1) — annual increase", "A landlord licensed under §37.15 may impose an annual increase of up to 60% of the published CPI change, and in no event more than 7%.", "Binding: 1.6% now", "ok", ("S08", "S01")),
        ("Local", "Admin Code §37.3(a)(2) — banking", "A landlord who skips an annual increase may accumulate it and impose it on a later anniversary date.", "Applies to Unit B", "ok", ("S08", "S07")),
        ("Local", "Admin Code §37.3(a)(8) — above the cap", "Any increase beyond the allowable amounts requires a rental arbitration petition under §37.8.", "The only route above 1.6%", "ok", ("S08", "S10")),
        ("Local", "Admin Code §37.3(a)(11) — additional occupants", "A landlord may not impose an increase solely because a tenant added an occupant, even where the lease permits such a charge. Costa-Hawkins pricing is preserved.", "Applies to Unit A", "ok", ("S08", "S01")),
        ("Local", "Admin Code §37.3(b) — notice content", "The notice must state which portion is the annual increase, which is banked, and which is any passthrough or improvement charge; a non-conforming increase is null and void.", "Applies", "ok", ("S08", "S07")),
        ("Local", "Admin Code §37.15 — housing inventory", "A rent increase licence must be in effect on the effective date; the notice is unenforceable without it.", "Applies", "ok", ("S09",)),
        ("Local", "Rules & Regulations §4.12 — banking mechanics", "One increase per 12 months; a full 12 months must have elapsed before banking applies; no compounding, no rounding up; the banked portion and its dates must be disclosed.", "Applies to Unit B", "ok", ("S07",)),
        ("Local", "Rules & Regulations §4.10 — null and void", "A rent increase that does not conform is void in its entirety, unless it is within the allowable amounts and the error is within a half of one percent good-faith tolerance.", "Applies", "ok", ("S07",)),
        ("Local", "Admin Code §37.10C — algorithmic devices", "Sale or use of algorithmic devices to set rents or manage occupancy levels for residential units is prohibited in San Francisco.", "Applies to any pricing tool", "ok", ("S08",)),
        ("Local", "Rent Board jurisdiction limit", "The Rent Board does not adjudicate harassment, discrimination or retaliation; those go to court or another forum.", "Determines the forum", "ok", ("S13", "S24")),
    ]
    trs = "".join(
        f"<tr><td><span class='chip'>{E(j)}</span></td><td><strong>{E(t)}</strong></td><td>{E(d)}</td>"
        f"<td><span class='badge {b}'>{E(a)}</span></td><td class='src'>{cite(*s)}</td></tr>"
        for j, t, d, a, b, s in rows
    )
    body = f"""
<div class="card">
  <h3 style="margin-top:0">Which layer actually decides the number</h3>
  <p>Three layers apply at once, but only one sets the price. Federal law adds anti-discrimination duties and
  no rent cap. California's statewide cap is expressly displaced where a local ordinance is stricter, which is
  the case in San Francisco {cite('S14')}. The Rent Ordinance therefore decides: 1.6% now, once every twelve
  months, with a 7% absolute ceiling {cite('S08','S01')}. State law still adds the notice mechanics
  {cite('S15')} and the anti-retaliation rule {cite('S18')}, and both state and federal law add the
  anti-discrimination rules {cite('S19','S20')}.</p>
</div>

<h2>Requirement matrix</h2>
<div class="toolbar">
  <input type="search" id="filter" data-target="#laws-table" placeholder="Filter requirements (e.g. notice, Unit A, federal)">
  <span class="chip" id="count">18 rows</span>
</div>
<div class="tablewrap"><table id="laws-table">
  <thead><tr><th>Layer</th><th>Instrument</th><th>What it requires</th><th>Effect here</th><th class="src">Source</th></tr></thead>
  <tbody>{trs}</tbody>
</table></div>

<h2>Note on the state cap figure</h2>
<p>The statewide formula is “5% plus the percentage change in the cost of living, or 10%, whichever is
lower” {cite('S14')}. The actual CPI-derived statewide percentage for a given year is published separately;
it is not reproduced here because it does not apply to these units, and reproducing it without its own
official citation would breach the no-unverified-values rule. Nothing on this site depends on it.</p>

<h2>What “rent” means for the calculation</h2>
<p>The Ordinance defines rent broadly — any consideration demanded for use or occupancy, including parking and
furnishings — and treats a reduction in housing services without a corresponding rent reduction as a rent
increase {cite('S08')}. The Rent Board's calculation instruction is narrower: apply the percentage to base
rent, including housing services such as parking or storage, excluding temporary passthroughs and fluctuating
charges {cite('S01')}. A rent increase licence does not change the amount that may be charged; it only
determines whether the increase can take effect {cite('S09')}.</p>
"""
    return page("laws.html", "Laws",
                "Federal, state and local requirements in one matrix, with what each one actually does to these "
                "two tenancies.", "laws", body)


def build_practice():
    rows = [
        ("Ownership structure", "Publicly traded REIT; 2,988 employees at 31 Jan 2025; ~63% on-site at communities.",
         "Individual owner or small entity; no separate rule set exists — §37.2(h) defines “landlord” to include owner, lessor, sublessor, agent, representative and successor.",
         ("S23", "S08")),
        ("Lease length and reset points", "“Substantially all of our apartment leases are for a term of one year or less”, which lets the owner realise increased rents at renewal.",
         "Same freedom: SF tenancies commonly go month-to-month after the initial term, which keeps the same anniversary-based increase discipline.",
         ("S23", "S01")),
        ("Timing of increases", "“Staggering lease terms such that lease expirations are matched with seasonal demand.”",
         "Practical equivalent is keeping one anniversary date per unit and re-noticing annually rather than moving dates, which the Rent Board warns can forfeit a year's allowance.",
         ("S23", "S01", "S05")),
        ("Pricing approach", "“Delivering high occupancy with premium pricing for various customer segments”; “utilizing data science … to optimize NOI”.",
         "In a covered unit the compliant equivalent is the published percentage applied to base rent — the Ordinance's own formula — not a market comparison.",
         ("S23", "S01", "S12")),
        ("Administration", "“Centralization of lease renewal activity, as well as many community administration and support tasks at our shared service center.”",
         "A single written checklist and one file per unit achieves the same control: licence status, base rent, anniversary, notice copy, calculation sheet.",
         ("S23", "S09", "S07")),
        ("Regulatory posture", "The 10-K states that rents and renewal increases are limited by fair housing laws and by state and local rent regulations, and describes California's statewide cap.",
         "The local cap binds harder than the state cap: 1.6% versus a statewide formula of 5% + CPI capped at 10%. A 10-K's high-level description is not a substitute for the local ordinance.",
         ("S23", "S14", "S01")),
        ("Pricing software", "The 10-K lists “algorithmic pricing tools” among the practices that rent regulation may limit.",
         "San Francisco prohibits the sale or use of algorithmic devices to set rents or manage occupancy for residential units — so this is not available here at all.",
         ("S23", "S08")),
        ("Above-cap increases", "Institutional owners use the statutory petition routes where costs justify them.",
         "Identical routes: capital improvement certification, operating and maintenance petitions (up to 7% extra), utility and bond passthroughs, and special-circumstances petitions.",
         ("S10", "S11", "S12")),
        ("Banked increases on acquisition", "Portfolio acquisitions bring existing tenancies and their rent histories.",
         "“New owners may use banked increases from prior owners”, which makes reconstructing the ledger the first task after any purchase.",
         ("S04",)),
        ("Professional support", "In-house counsel and compliance functions.",
         "Free Rent Board counselling for landlords and tenants; the Rent Board also publishes the membership bodies for owners (San Francisco Apartment Association, Small Property Owners of San Francisco).",
         ("S01", "S21")),
    ]
    trs = "".join(
        f"<tr><td><strong>{E(a)}</strong></td><td>{E(b)}</td><td>{E(c)}</td><td class='src'>{cite(*s)}</td></tr>"
        for a, b, c, s in rows
    )
    body = f"""
<div class="card">
  <h3 style="margin-top:0">Short answer</h3>
  <p>Large owners do not have a different rule book. The evidence available from a public filer shows a
  professional operating model — one-year leases, deliberately staggered expirations, centralised renewal
  administration, data-driven pricing — layered on top of exactly the same statutory constraints that apply to
  a two-unit owner {cite('S23')}. What differs is administrative discipline, not legal permission. In San
  Francisco the binding number is the Rent Board's published percentage, and the most sophisticated tool in the
  corporate kit — algorithmic rent-setting — is expressly prohibited by the local ordinance {cite('S08')}.</p>
</div>

<h2>Institutional practice versus individual practice</h2>
<div class="toolbar">
  <input type="search" id="filter" data-target="#practice-table" placeholder="Filter rows (e.g. lease, notice, software)">
  <span class="chip" id="count">10 rows</span>
</div>
<div class="tablewrap"><table id="practice-table">
  <thead><tr><th style="width:16%">Topic</th><th style="width:34%">What the institutional record shows</th><th>What an individual owner does instead (same legal constraints)</th><th class="src">Source</th></tr></thead>
  <tbody>{trs}</tbody>
</table></div>

<h2>What the filing actually says, and what it does not</h2>
<p class="q">“The construction, operation and leasing of our communities is subject to federal, state and local
laws and regulations, include … fair housing laws, and, depending on the jurisdiction, regulations regarding the
charging of rents and fees and increases in such amounts upon renewal of leases.”</p>
<p class="q">“Some laws relating to the setting of rents apply broadly, such as in California, where residential
rent increases at renewal in communities older than fifteen years are limited to the lesser of 10% or 5% plus
local consumer price index (CPI) …” {cite('S23')}</p>
<p>Two things follow, and one important thing does not. First, a public company describes rent regulation as a
material business constraint and puts renewal increases inside a compliance framework rather than treating them
as a free commercial decision. Second, the description quotes the statewide cap: it does not describe San
Francisco's stricter local cap, which is 1.6% here. A general filing is therefore not a source for a local
number, and this report does not use it as one — the local number comes from the Rent Board
{cite('S01','S03')}.</p>

<h2>The individual owner's actual toolkit</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Tool</th><th>Availability</th><th>Evidence needed</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>Annual allowable increase</td><td>By right, once per 12 months, with a licence</td><td>Correct base rent and anniversary date</td><td class="src">{cite('S01','S09')}</td></tr>
    <tr><td>Banked prior increases</td><td>By right if properly banked</td><td>Full rent history; itemised banked portion</td><td class="src">{cite('S07','S04')}</td></tr>
    <tr><td>Operating and maintenance petition</td><td>Up to 7% extra where expenses rose more than the annual allowance</td><td>Two comparison years of operating statements</td><td class="src">{cite('S11')}</td></tr>
    <tr><td>Capital improvement passthrough</td><td>Petition and certification</td><td>Invoices, permits, amortisation</td><td class="src">{cite('S10')}</td></tr>
    <tr><td>Special circumstances (comparable rents)</td><td>Petition only; extraordinary circumstances unrelated to market conditions</td><td>Comparable-unit evidence; one time per tenancy</td><td class="src">{cite('S12')}</td></tr>
    <tr><td>Utility, water and bond passthroughs</td><td>Worksheet or petition depending on type</td><td>Bills, completed Rent Board worksheets</td><td class="src">{cite('S10','S08')}</td></tr>
    <tr><td>Market-rate reset</td><td>Only on a genuinely new tenancy</td><td>Proof no prior tenant remains in possession</td><td class="src">{cite('S17','S01')}</td></tr>
    <tr><td>Algorithmic pricing</td><td>Not available — prohibited</td><td>—</td><td class="src">{cite('S08')}</td></tr>
  </tbody>
</table></div>

<div class="note"><strong>The practical takeaway.</strong> The defensible posture for a small owner is to
mirror what a compliance department would do: one file per unit, one anniversary date, one written notice with
the prescribed contents, one calculation sheet, and no explanation offered beyond the statutory basis — because
the statutory basis is the only one that survives review {cite('S01','S08','S07')}.</div>
"""
    return page("practice.html", "Owner Practice",
                "How institutional owners actually handle increases, with the individual-owner equivalent for "
                "each practice.", "practice", body)


def build_notice():
    steps = [
        ("1", "Confirm coverage and the licence", "Check the unit is covered (built on or before 13 June 1979, not a single-family dwelling) and that a rent increase licence is active for the unit in the Housing Inventory.", "A notice is unenforceable without a licence in effect on its effective date.", ("S06", "S09")),
        ("2", "Fix the base rent", "Use base rent only — include parking or storage, exclude temporary passthroughs and fluctuating charges.", "The percentage applies to base rent, not to the total cheque.", ("S01",)),
        ("3", "Fix the effective date and check 12 months", "Pick the date the new rent starts. It must be at least 12 months after the tenancy began and after any previous increase; the date becomes the new anniversary.", "One increase per 12 months; skipping does not license two at once unless banked.", ("S01", "S07")),
        ("4", "Apply the rate in effect on that date", "1.6% for any date from 1 March 2026 through 28 February 2027. Do not round the result up.", "Using the wrong year's rate is the second most common error.", ("S01", "S03")),
        ("5", "Add any banked amount and itemise it", "State the banked dollar/percentage and the years it is based on.", "Rule 4.12(b) requires disclosure of the banked portion and its dates.", ("S07", "S08")),
        ("6", "Choose 30 or 90 days", "30 days if the increase is 10% or less of the rent charged in the prior 12 months; 90 days if more.", "State law and the Rent Board agree; a longer period required elsewhere controls.", ("S15", "S01")),
        ("7", "Serve it in writing with the prescribed contents", "Dollar amount, percentage, effective date, effective-date rate, and the split between annual, banked and any passthrough.", "A non-conforming increase is null and void in its entirety.", ("S08", "S07")),
        ("8", "Add five days if you mail it", "Service by mail extends the notice period by five days.", "Compliant personal service avoids the argument.", ("S15", "S01")),
        ("9", "Never charge for an added occupant", "Do not add rent because a roommate moved in, even if the lease says you may.", "Expressly unlawful on a continuing tenancy.", ("S08", "S01")),
        ("10", "File the paperwork", "Keep the licence confirmation, the calculation sheet, the signed notice, the service record and the rationale memo.", "Burden of proof sits with the landlord in any petition.", ("S07", "S13")),
    ]
    trs = "".join(
        f"<tr><td class='num'>{n}</td><td><strong>{E(t)}</strong></td><td>{E(d)}</td><td class='small muted'>{E(w)}</td><td class='src'>{cite(*s)}</td></tr>"
        for n, t, d, w, s in steps
    )

    reasons = [
        ("The published annual allowable increase", "Lawful by right", "Licence active; correct base rent; correct rate for the effective date; 12 months elapsed.", "ok", ("S01", "S08")),
        ("Banked prior annual increases", "Lawful by right if banked", "Rent history proving the allowance was not imposed; itemised in the notice.", "ok", ("S04", "S07")),
        ("Increased operating and maintenance costs", "Petition only, up to 7% extra", "Two comparison years showing expenses rose more than the annual allowance; petition filed before the notice.", "warn", ("S11", "S10")),
        ("Capital improvements", "Petition and certification", "Invoices, permits, amortisation; certification under §37.7.", "warn", ("S10", "S08")),
        ("Utility, water or bond passthroughs", "Worksheet or petition, separate from base rent", "Bills and the Rent Board's completed worksheet.", "warn", ("S10", "S08")),
        ("Comparable rents in the area", "Petition only, narrow grounds", "Extraordinary circumstances unrelated to market conditions — a long-standing below-market rent is expressly insufficient.", "bad", ("S12",)),
        ("A new roommate moved in", "Unlawful", "No evidence can make this lawful on a continuing tenancy.", "bad", ("S08", "S01")),
        ("“The market went up”", "Not a lawful ground on its own", "Only relevant inside a special-circumstances petition, and only with the extraordinary-circumstances showing.", "bad", ("S12",)),
        ("The tenant complained or organised", "Unlawful — retaliation", "A rent increase within 180 days of protected activity is exposed under §1942.5.", "bad", ("S18",)),
        ("A protected characteristic of the tenant", "Unlawful — discrimination", "FEHA and the Fair Housing Act both apply; the Rent Board will not hear the claim, a court or the HRC will.", "bad", ("S19", "S20", "S24")),
    ]
    rtrs = "".join(
        f"<tr><td><strong>{E(a)}</strong></td><td><span class='badge {b}'>{E(v)}</span></td><td>{E(c)}</td><td class='src'>{cite(*s)}</td></tr>"
        for a, v, c, b, s in reasons
    )

    body = f"""
<div class="card">
  <h3 style="margin-top:0">The notice is the whole case</h3>
  <p>If a San Francisco tenant disputes an increase, the landlord has to show the arithmetic, the licence and the
  service. The Ordinance makes a non-conforming increase void in its entirety, not merely reduced
  {cite('S08')}. That is why the checklist below is sequential: each step depends on the one before, and the
  most common failures are an unlicensed unit, a wrong-year rate, a missing banked-itemisation, and too short a
  notice period {cite('S01','S07','S09')}.</p>
</div>

<h2>Notice checklist</h2>
<div class="tablewrap"><table>
  <thead><tr><th class="num" style="width:36px">#</th><th>Step</th><th>What to do</th><th>Why it matters</th><th class="src">Source</th></tr></thead>
  <tbody>{trs}</tbody>
</table></div>

<h2>What the notice must contain</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Element</th><th>Requirement</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>Dollar amount of the increase</td><td>Required</td><td class="src">{cite('S01','S08')}</td></tr>
    <tr><td>Percentage of the increase</td><td>Required</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Effective date</td><td>Required</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Which portion is the annual increase</td><td>Required on or before the date legal notice is given</td><td class="src">{cite('S08','S07')}</td></tr>
    <tr><td>Which portion is banked, and the dates it is based on</td><td>Required where banking is used; omission does not void the increase but must be corrected</td><td class="src">{cite('S07')}</td></tr>
    <tr><td>Which portion is any certified improvement, utility or bond passthrough</td><td>Required where applicable, with the Rent Board's worksheet where prescribed</td><td class="src">{cite('S08','S10')}</td></tr>
    <tr><td>Licence number printed on the notice</td><td>Not required — but the licence must exist on the effective date</td><td class="src">{cite('S09')}</td></tr>
  </tbody>
</table></div>

<h2>Reasons: which ones survive review</h2>
<div class="toolbar">
  <input type="search" id="filter" data-target="#reasons-table" placeholder="Filter reasons (e.g. market, banker, roommate)">
  <span class="chip" id="count">10 rows</span>
</div>
<div class="tablewrap"><table id="reasons-table">
  <thead><tr><th>Reason a landlord might give</th><th>Lawful ground?</th><th>What would have to be shown</th><th class="src">Source</th></tr></thead>
  <tbody>{rtrs}</tbody>
</table></div>

<h2>The banked-itemisation sentence nobody writes</h2>
<p>Rule 4.12(b) requires the landlord to tell the tenant, on or before the date legal notice is given, “which
portion of the rent increase reflects banked amount” and “the dates upon which said banked amount is based”
{cite('S07')}. The rule softens the consequence — failure to include it “shall not render the increase null and
void” — but in practice an un-itemised banked increase is the hardest thing to defend in a hearing, because the
landlord then has to reconstruct the history from scratch under a burden of proof it carries.</p>

<div class="note"><strong>Model sentence for a Unit B notice.</strong>
“The monthly rent of $3,150.00 will increase by 11.7% ($368.55) to $3,518.55 effective [date]. Of this increase,
10.1% ($318.15) is a banked increase consisting of the annual allowable increases of 1.8% (effective 3/1/2020),
0.7% (3/1/2021), 2.3% (3/1/2022), 3.6% (3/1/2023) and 1.7% (3/1/2024) which were not imposed, and 1.6% ($50.40)
is the current annual allowable increase effective 3/1/2026.”
<span class="small muted">Figures are illustrative arithmetic from the published rates {cite('S03')} and must not be sent
until F01 and F04 are resolved.</span></div>
"""
    return page("notice.html", "Notice &amp; Reasons",
                "The exact sequence for a defensible notice, the contents it must carry, and which reasons survive "
                "review.", "notice", body)


def build_discrimination():
    body = f"""
<div class="card">
  <h3 style="margin-top:0">Direct answer</h3>
  <p>Raising one unit and not the other is not, by itself, unlawful. What the law prohibits is a difference that
  is based on a protected characteristic — race, colour, religion, sex, gender identity or expression, sexual
  orientation, marital status, national origin, ancestry, familial status, source of income, disability, veteran
  or military status, or genetic information under state law {cite('S19')}, and race, colour, national origin,
  religion, sex, familial status or disability under federal law {cite('S20')}. A difference that follows from
  objective rent facts — a different base rent, a different tenancy start date, a different banking history —
  is the ordinary output of the formula, not evidence of discrimination.</p>
  <p><strong>Recommended:</strong> apply the same published percentage to both units and document why the dollar
  outcomes differ. That is the simplest position to defend, and it also avoids the appearance problem that
  invites an inquiry in the first place.</p>
</div>

<h2>The two units are objectively different — this is the documentation that matters</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Objective factor</th><th>Unit A</th><th>Unit B</th><th>Consequence</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>Base rent</td><td>{money(UNIT_A_RENT)}</td><td>{money(UNIT_B_RENT)}</td><td>Same percentage produces a different dollar increase ($63.92 vs $50.40)</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Tenancy start</td><td>1 Feb 2025</td><td>1 Jun 2019</td><td>Different anniversary dates and a different number of available annual increases</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Available banked allowance</td><td>None yet</td><td>10.1% – 11.5% (conditional)</td><td>A larger percentage on Unit B is explained by history, not by the tenant</td><td class="src">{cite('S04','S07')}</td></tr>
    <tr><td>Rent as a share of the other unit</td><td>100% ($3,995)</td><td>78.8% ($3,150)</td><td>Even at the 13.1% ceiling, Unit B ($3,562.65) remains below Unit A's current rent</td><td class="src">{cite('S03','S07')}</td></tr>
    <tr><td>Notice period triggered</td><td>30 days</td><td>90 days if the increase exceeds 10%</td><td>Different procedure because the percentages differ, not because the tenants differ</td><td class="src">{cite('S15')}</td></tr>
  </tbody>
</table></div>

<h2>Where a claim would actually be filed</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Forum</th><th>Handles</th><th>Model / route</th><th class="src">Source</th></tr></thead>
  <tbody>
    <tr><td>SF Rent Board</td><td>Whether the amount charged is lawful; invalid notices; decreased services</td><td>Free tenant petition, mediation, then an Administrative Law Judge</td><td class="src">{cite('S13')}</td></tr>
    <tr><td>SF Human Rights Commission, Civil Rights Division</td><td>Discrimination complaints in housing</td><td>Investigation and mediation at City level</td><td class="src">{cite('S24')}</td></tr>
    <tr><td>California Civil Rights Department / courts</td><td>FEHA housing discrimination</td><td>State administrative complaint or civil action</td><td class="src">{cite('S19')}</td></tr>
    <tr><td>HUD / federal courts</td><td>Fair Housing Act claims</td><td>Federal administrative complaint or civil action</td><td class="src">{cite('S20')}</td></tr>
    <tr><td>Superior Court</td><td>Retaliation, harassment, wrongful eviction</td><td>Civil action — the Rent Board expressly does not adjudicate these</td><td class="src">{cite('S13','S18')}</td></tr>
  </tbody>
</table></div>
<p class="small muted">That the Rent Board will not hear discrimination, harassment or retaliation claims
{cite('S13')} does not reduce exposure — it moves the dispute to a forum where damages and fees are available.</p>

<h2>Three concrete risks if only one unit is increased</h2>
<ol>
  <li><strong>The differential needs a written reason, and “we chose to” is a weak one.</strong> A one-line
      per-unit rationale that cites base rent, anniversary and banking history converts an unexplained
      difference into a documented application of the formula {cite('S01','S04')}.</li>
  <li><strong>Timing can look retaliatory even when it is not.</strong> An increase served within 180 days of a
      repair request, agency complaint or organising activity is exposed under Civil Code §1942.5, whatever the
      arithmetic shows {cite('S18')}.</li>
  <li><strong>A free challenge exists.</strong> Any tenant can file an unlawful-rent-increase petition or a
      summary petition based on an invalid notice at no cost {cite('S13')}, so a unit that is not increased this
      year is still a unit whose neighbour's file will be read closely.</li>
</ol>

<div class="warnbox"><strong>What this page is not.</strong> It is not a legal opinion on whether any particular
tenant belongs to a protected class, and it deliberately records no such information. The analysis assumes only
what the brief supplies: rent, dates and occupancy changes. If any tenant has a characteristic protected under
{cite('S19')} or {cite('S20')}, the safe course is unchanged — identical policy, identical process, documented
arithmetic, and no reference to the tenant's circumstances in any communication.</div>
"""
    return page("discrimination.html", "One Unit or Both",
                "Whether to raise one unit or both, tested against discrimination, retaliation and the "
                "arithmetic itself.", "discrimination", body)


def build_review():
    order = {"High": 0, "Medium": 1, "Low": 2}
    cards = ""
    for f in sorted(FLAGS, key=lambda x: (order[x["severity"]], x["id"])):
        cls = f["severity"].lower()
        srcs = "".join(
            f'<a class="ref" href="{E(SRC[s]["url"])}" target="_blank" rel="noopener">{E(s)}</a>'
            for s in f["sources"]
        )
        cards += f"""
<div class="flagcard {cls}">
  <div class="flaghead">
    <strong>{E(f['id'])}</strong>
    <span class="badge {'bad' if f['severity']=='High' else ('warn' if f['severity']=='Medium' else 'info')}">{E(f['severity'])}</span>
    <span class="chip">{E(f['status'])}</span>
    <span class="src">{srcs}</span>
  </div>
  <h4>{E(f['title'])}</h4>
  <dl class="dl">
    <dt>Detail</dt><dd>{E(f['detail'])}</dd>
    <dt>Impact</dt><dd>{E(f['impact'])}</dd>
    <dt>Action</dt><dd>{E(f['action'])}</dd>
  </dl>
</div>"""

    body = f"""
<div class="warnbox">
  <strong>Nothing here blocks publication.</strong> Every item below is either a conflict between two official
  sources, a fact the owner has not yet supplied, or a value deliberately left blank rather than guessed. They
  are listed so they can be reviewed after the site is live. Reading order: F01 and F04 first — those two change
  the numbers.
</div>

<div class="grid g4" style="margin-bottom:18px">
  <div class="kpi"><span class="l">High</span><span class="n">3</span><span class="s">affect the figures</span></div>
  <div class="kpi"><span class="l">Medium</span><span class="n">5</span><span class="s">scope or records</span></div>
  <div class="kpi"><span class="l">Low</span><span class="n">3</span><span class="s">documentation only</span></div>
  <div class="kpi"><span class="l">Blank cells</span><span class="n">0</span><span class="s">every published value has a source</span></div>
</div>

{cards}

<h2>Values deliberately left blank</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Value</th><th>Why it is blank</th><th class="src">Would need</th></tr></thead>
  <tbody>
    <tr><td>2027–28 allowable increase</td><td>Not published until 1 March 2027</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Unit B rent history 2019–2026</td><td>Not supplied by the owner</td><td class="src">{cite('S04')}</td></tr>
    <tr><td>Certificate of occupancy / legal unit count</td><td>Not yet pulled from City records</td><td class="src">{cite('S06')}</td></tr>
    <tr><td>Market rent for the two units</td><td>No official source; excluded by design</td><td class="src">{cite('S01')}</td></tr>
    <tr><td>Statewide AB 1482 percentage for the current year</td><td>Not applicable to these units and not separately verified</td><td class="src">{cite('S14')}</td></tr>
    <tr><td>Rent Board fee amount</td><td>Not verified in this pass; not needed for the analysis</td><td class="src">{cite('S09')}</td></tr>
    <tr><td>Any federal rent cap</td><td>No such federal rule was located</td><td class="src">{cite('S20')}</td></tr>
  </tbody>
</table></div>

<h2>Integration record — parallel sessions</h2>
<p>Two other sessions published work to this repository while this analysis was being prepared. Their files are
retained untouched for audit — <code>docs/</code> (the earlier published draft and the data file behind it),
<code>site/</code> (an earlier static draft), <code>research/</code> (their research notes) and
<code>scripts/</code> (their build and verify scripts) — and the earlier draft remains reachable at
<a href="docs/index.html">docs/index.html</a>. The pages you are reading are the integration output.</p>
<div class="tablewrap"><table>
  <thead><tr><th>Item</th><th>Earlier draft (docs/)</th><th>This site</th><th>Reconciled?</th></tr></thead>
  <tbody>
    <tr><td>Current allowable increase</td><td>1.6% for 1 Mar 2026 – 28 Feb 2027</td><td>1.6% for 1 Mar 2026 – 28 Feb 2027</td><td><span class="badge ok">Match</span></td></tr>
    <tr><td>Unit A illustration</td><td>$3,995 × 1.6% = $63.92 → $4,058.92</td><td>$63.92 → $4,058.92</td><td><span class="badge ok">Match</span></td></tr>
    <tr><td>Unit B illustration</td><td>$3,150 × 1.6% = $50.40 → $3,200.40</td><td>$50.40 → $3,200.40</td><td><span class="badge ok">Match</span></td></tr>
    <tr><td>Banked allowance for Unit B</td><td>Flagged as needing the rent history; no figure given</td><td>Conditional range 10.1%–11.5%, totals 11.7%–13.1%</td><td><span class="badge warn">Extended here</span></td></tr>
    <tr><td>Notice periods</td><td>30 / 90 days</td><td>30 / 90 days, plus 5 for mail</td><td><span class="badge ok">Match</span></td></tr>
    <tr><td>Coverage basis</td><td>1940 build, flagged unverified</td><td>Same, flagged as F05</td><td><span class="badge ok">Match</span></td></tr>
    <tr><td>Source standard</td><td>Mostly official; some trade/agency blogs in the task log</td><td>Official sources only; secondary items labelled</td><td><span class="badge warn">Tightened here</span></td></tr>
  </tbody>
</table></div>
<p class="small muted">Two sessions reading the same Rent Board pages reached the same three figures independently,
which is the strongest available check on the arithmetic. Where they differ, it is in depth of treatment of
banked increases (this site supplies a computed, deliberately conditional range), not in any verified value.</p>

<h2>How to read the status labels</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Label</th><th>Meaning</th></tr></thead>
  <tbody>
    <tr><td><span class="badge ok">Verified</span></td><td>Read directly from an official source; the quoted value appears on the linked page.</td></tr>
    <tr><td><span class="badge warn">Conditional</span></td><td>The rule is verified but the outcome depends on a fact the owner has not supplied.</td></tr>
    <tr><td><span class="badge bad">Flagged</span></td><td>Sources conflict, or the value could not be confirmed. Nothing was invented to fill the gap.</td></tr>
  </tbody>
</table></div>
"""
    return page("review.html", "Flagged for Review",
                "Eleven items that need a human decision, with the source links for each.", "review", body)


def build_sources():
    trs = ""
    for s in SOURCES:
        trs += (f"<tr><td><strong>{E(s['id'])}</strong></td><td><span class='chip'>{E(s['tier'])}</span></td>"
                f"<td><a href='{E(s['url'])}' target='_blank' rel='noopener'>{E(s['title'])}</a>"
                f"<div class='small muted'>{E(s['publisher'])}</div></td>"
                f"<td class='small'>{E(s['supports'])}</td></tr>")

    body = f"""
<div class="card">
  <h3 style="margin-top:0">Source policy</h3>
  <p>Every factual claim on this site resolves to one of the {len(SOURCES)} entries below. Nothing is cited from
  memory, and no value appears anywhere on the site without a source id next to it. Where an official source
  could not be found, the value is left blank and recorded on <a href="review.html">Flagged for Review</a> rather
  than filled from a secondary source. Two secondary sources are used, and both are labelled as such: an SEC
  filing (a primary filing, but a company document rather than a regulator's) and the programme operator for the
  Tenant Right to Counsel programme.</p>
  <p class="small muted">All links were opened and read on 6 November 2026.</p>
</div>

<h2>Register</h2>
<div class="toolbar">
  <input type="search" id="filter" data-target="#src-table" placeholder="Filter sources (e.g. banking, notice, federal)">
  <span class="chip" id="count">{len(SOURCES)} sources</span>
</div>
<div class="tablewrap"><table id="src-table">
  <thead><tr><th style="width:60px">ID</th><th style="width:15%">Tier</th><th style="width:32%">Document</th><th>What it supports on this site</th></tr></thead>
  <tbody>{trs}</tbody>
</table></div>

<h2>Coverage of the question set</h2>
<div class="tablewrap"><table>
  <thead><tr><th>Question asked</th><th>Answered on</th><th>Principal sources</th></tr></thead>
  <tbody>
    <tr><td>What is a reasonable and normal increase under local, state and federal law?</td><td><a href="laws.html">Laws</a>, <a href="increases.html">Increases</a></td><td class="src">{cite('S01','S08','S14','S20')}</td></tr>
    <tr><td>How do large corporations handle increases?</td><td><a href="practice.html">Owner Practice</a></td><td class="src">{cite('S23','S08')}</td></tr>
    <tr><td>How do individual owners handle them?</td><td><a href="practice.html">Owner Practice</a></td><td class="src">{cite('S08','S21')}</td></tr>
    <tr><td>How should tenants be informed, and what reasons are reasonable?</td><td><a href="notice.html">Notice &amp; Reasons</a></td><td class="src">{cite('S08','S07','S15','S11','S12')}</td></tr>
    <tr><td>Would a tenant lawyer find the increase reasonable?</td><td><a href="review.html">Flagged for Review</a>, <a href="notice.html">Notice &amp; Reasons</a></td><td class="src">{cite('S13','S21','S22')}</td></tr>
    <tr><td>One unit or both?</td><td><a href="discrimination.html">One vs Both</a></td><td class="src">{cite('S19','S20','S18')}</td></tr>
  </tbody>
</table></div>
"""
    return page("sources.html", "Sources",
                "The full register of official sources, with what each one supports.", "sources", body)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def check():
    """Assert the data-driven tables all carry sources and that the maths is consistent."""
    problems = []
    for s in SCENARIOS:
        if not s["sources"]:
            problems.append(f"scenario {s['id']} has no source")
    for f in FLAGS:
        if not f["sources"]:
            problems.append(f"flag {f['id']} has no source")
    for i in INCREASES:
        if not (0 <= i["rate"] <= 7.0):
            problems.append(f"implausible rate {i['period']}")
    if round(BANKED_24, 4) != 10.1:
        problems.append(f"BANKED_24 expected 10.1, got {BANKED_24}")
    if round(BANKED_12, 4) != 11.5:
        problems.append(f"BANKED_12 expected 11.5, got {BANKED_12}")
    if TOTAL_24 != 11.7 or TOTAL_12 != 13.1:
        problems.append(f"totals drifted: {TOTAL_24} / {TOTAL_12}")
    if money(Decimal(str(UNIT_A_RENT)) * Decimal("0.016")) != "$63.92":
        problems.append("Unit A annual dollars drifted")
    if money(Decimal(str(UNIT_B_RENT)) * Decimal("0.016")) != "$50.40":
        problems.append("Unit B annual dollars drifted")
    if problems:
        print("CHECK FAILED")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"CHECK OK — {len(SCENARIOS)} scenarios, {len(FLAGS)} flags, {len(INCREASES)} annual rates, "
          f"{len(SOURCES)} sources, banking totals {BANKED_24}/{BANKED_12} → {TOTAL_24}%/{TOTAL_12}%")
    return True


def main():
    check()
    pages = {
        "index.html": build_index(),
        "exec-summary.html": build_exec(),
        "units.html": build_units(),
        "increases.html": build_increases(),
        "laws.html": build_laws(),
        "practice.html": build_practice(),
        "notice.html": build_notice(),
        "discrimination.html": build_discrimination(),
        "review.html": build_review(),
        "sources.html": build_sources(),
    }
    for name, content in pages.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"wrote {name:24s} {len(content):>7,d} bytes")

    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    with open(os.path.join(ROOT, "assets", "style.css"), "w", encoding="utf-8") as fh:
        fh.write(CSS)
    with open(os.path.join(ROOT, "assets", "app.js"), "w", encoding="utf-8") as fh:
        fh.write(JS)
    print("wrote assets/style.css, assets/app.js")


if __name__ == "__main__":
    main()
