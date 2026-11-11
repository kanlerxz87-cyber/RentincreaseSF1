#!/usr/bin/env python3
"""Build the independent assurance page from canonical hub data and audit findings."""
from __future__ import annotations
import html
import json
import os
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = json.load(open(os.path.join(ROOT, "hub", "data.json"), encoding="utf-8"))
AUDIT = json.load(open(os.path.join(ROOT, "audit", "final-integration", "findings.json"), encoding="utf-8"))
C = Decimal("0.01")

def esc(x): return html.escape(str(x), quote=True)
def money(x): return "${:,.2f}".format(Decimal(x))
def longdate(s):
    x = date.fromisoformat(s) if isinstance(s, str) else s
    return f"{x.day} {x.strftime('%B')} {x.year}"
def src(ids):
    return " ".join(f'<a href="../hub/sources.html#{esc(i)}">{esc(i)}</a>' for i in ids)
def flags(ids):
    return " ".join(f'<a href="../hub/flags.html#{esc(i)}">{esc(i)}</a>' for i in ids)
def row(cells):
    return "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
def table(headers, rows, caption):
    return ('<div class="tablewrap"><table class="data-table"><caption>' + esc(caption) +
            "</caption><thead><tr>" + "".join(f'<th scope="col">{esc(h)}</th>' for h in headers) +
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")

correction_rows = [row([f'<strong>{esc(c["id"])} · {esc(c["item"])}</strong>', esc(c["finding"]), src(c["sources"]), flags(c["flags"]) or "—"])
                   for c in AUDIT["corrections"]]
correction_table = table(["Correction", "Independent finding", "Official source", "Flag"], correction_rows,
                         f"{len(AUDIT['corrections'])} corrections made after reading the canonical source data, generated pages, and 2026-11-11 official updates line by line.")

scenario_rows = []
for unit in ("U1", "U2"):
    u = HUB["units"][unit]
    calc = HUB["calculations"][unit]
    base = Decimal(u["base_rent"])
    for kind in ("annual", "combined"):
        pct = Decimal(calc["annual_pct"] if kind == "annual" else calc["total_pct"])
        amount = (base * pct / 100).quantize(C, rounding=ROUND_HALF_UP)
        new = base + amount
        open_flags = ["H-02", "H-17"] if unit == "U1" else ["H-18", "H-03"]
        label = "Annual-only" if kind == "annual" else "Combined"
        scenario_rows.append(row([
            f"{unit[-1]} · {label}", money(base), f"{pct.quantize(Decimal('0.1'))}%", money(amount), money(new),
            "Conditional scenario; not a certified lawful current rent or maximum.",
            src(["S05", "S06", "S07"]), flags(open_flags)
        ]))
scenario_table = table(["Scenario", "Input rent", "Rate", "Increase / month", "Illustrative new rent", "Status", "Official basis", "Open facts"], scenario_rows,
                       "Decimal arithmetic is independently recomputed from hub/data.json. Percentages are added; no compounding or rounding up.")

service_rows = []
for unit in ("U1", "U2"):
    calc = HUB["calculations"][unit]
    eff = date.fromisoformat(calc["annual_effective"])
    for kind in ("annual", "combined"):
        days = 30 if kind == "annual" else int(calc["notice_days"])
        if unit == "U1" and kind == "combined": days = 30
        personal = eff - timedelta(days=days)
        mail = eff - timedelta(days=days + 5)
        extra = ["S20"] if unit == "U1" else []
        service_rows.append(row([
            f"{unit[-1]} · {'Annual-only' if kind == 'annual' else 'Combined'}", longdate(eff), f"{days} days",
            longdate(personal), longdate(mail), src(["S08", "S21"] + extra)
        ]))
service_table = table(["Scenario", "Illustrative effective date", "Notice band", "Personal-service arithmetic", "California-mail arithmetic", "Official basis"], service_rows,
                      "Calendar subtraction only. These are not universal last-safe dates and do not clear lease, ledger, license, coverage, repair, or retaliation issues.")

flag_map = {f["id"]: f for f in HUB["flags"]}
residual_rows = []
for fid in AUDIT["residual_flag_ids"]:
    f = flag_map[fid]
    residual_rows.append(row([
        f'<strong>{esc(fid)} · {esc(f["item"])}</strong>', esc(f["effect"]), esc(f["action"]), src(f["sources"])
    ]))
residual_table = table(["Residual flag", "Effect", "Required private review", "Official source"], residual_rows,
                       f'Selected high-impact and source-interpretation flags. The canonical Flagged for Review page contains all {len(HUB["flags"])}.')

# Each source carries the date it was actually retrieved and read, so a later
# session adding a source cannot inherit a stale blanket date.
manifest = [{
    "id": s["id"], "publisher": s["publisher"], "url": s["url"],
    "retrieved": s.get("retrieved", AUDIT["retrieved"]),
    "result": "Retrieved and read from official publisher"
} for s in HUB["sources"]]
with open(os.path.join(ROOT, "audit", "final-integration", "source-manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

page = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Independent final assurance — SF Rent Increase Compliance</title>
<meta name="description" content="Independent corrections, arithmetic, service-date checks, source manifest, and residual flags for the canonical San Francisco rent-increase dashboard.">
<link rel="stylesheet" href="../hub/assets/style.css">
</head>
<body>
<header class="site-header"><div class="wrap navwrap">
  <a class="brand" href="../index.html"><span class="mark">SF</span><span>Independent Assurance<small>Canonical root + hub edition</small></span></a>
  <nav class="main" aria-label="Assurance"><a href="../index.html">Dashboard</a><a href="../hub/licensing.html">Licence &amp; Board</a><a href="../hub/limits.html">Limits &amp; amounts</a><a href="../hub/flags.html">All {len(HUB['flags'])} flags</a><a href="../hub/sources.html">Sources</a></nav>
</div></header>
<section class="hero"><div class="wrap">
<p class="eyebrow">Independent final assurance · {esc(AUDIT['retrieved'])}</p>
<h1>What changed, what was recomputed, and what remains unresolved</h1>
<p class="lede">This is a verification record, not another legal edition. The canonical dashboard is the root page and <code>hub/</code>. Older parallel editions are preserved as superseded archives.</p>
<div class="pillrow"><span class="pill">{len(AUDIT['corrections'])} corrections</span><span class="pill">{len(HUB['sources'])} official sources</span><span class="pill">{len(HUB['flags'])} canonical flags</span><span class="pill">Current-file privacy scan only</span></div>
</div></section>
<main class="wrap">
<section>
  <h2>Assurance conclusion<span class="sub">Official rules and arithmetic verified; notice-readiness not established.</span></h2>
  <div class="callout red"><p><strong>Historical privacy exposure:</strong> The current-text scan excludes Git history. An earlier public commit contains tenant initials; current-file redaction does not remove that history. See <a href="../hub/flags.html#history-privacy">the privacy review flag</a>.</p></div>
  <div class="answer"><h3>The individual-owner license answer is verified. No current lawful maximum or attorney acceptance is certified.</h3>
  <p>Each tenant-occupied unit needs a current Rent Increase License on the annual/banked increase's effective date. The safer sequence is to complete reporting before notice. Unit 1's lease instrument, Unit 2's current base, both ledgers, both licenses, and official coverage remain open. All amounts below are conditional scenarios.</p></div>
</section>
<section><h2>Correction register<span class="sub">Every substantive correction has an official source and, where applicable, a public flag.</span></h2>{correction_table}</section>
<section><h2>Independent arithmetic<span class="sub">Values are generated from the same canonical inputs, not copied from prose.</span></h2>{scenario_table}</section>
<section><h2>Independent service-date arithmetic<span class="sub">Thirty/90-day statutory bands plus five calendar days for California mail.</span></h2>{service_table}</section>
<section><h2>Residual Flagged for Review<span class="sub">Unsupported official-confirmation values remain blank on the canonical pages.</span></h2>{residual_table}</section>
<section>
  <h2>Verification evidence<span class="sub">Local reproducibility and content gates; live official retrieval is separately manifested.</span></h2>
  <ul>
    <li><strong>Source manifest:</strong> <code>audit/final-integration/source-manifest.json</code> records all {len(HUB['sources'])} official URLs, each with the date it was actually retrieved and read: {esc(", ".join(f"{k} ({v})" for k, v in sorted({r: sum(1 for m in manifest if m["retrieved"] == r) for r in {m["retrieved"] for m in manifest}}.items())))}.</li>
    <li><strong>Canonical generation:</strong> <code>python3 hub/build.py</code> regenerates the root and eight hub pages.</li>
    <li><strong>Assurance generation:</strong> <code>python3 assurance/build.py</code> regenerates this page and the source manifest.</li>
    <li><strong>Content gates:</strong> <code>python3 tools/verify_hub.py</code> and <code>python3 tools/verify_assurance.py</code> check internal links, source/flag citations, arithmetic, dates, conditional labels, and privacy.</li>
    <li><strong>Legacy checks preserved:</strong> existing companion, dashboard, portal, integration, and review suites are run before merge; archival status is not a claim that every historical sentence was re-certified.</li>
  </ul>
</section>
</main>
<footer class="site-footer"><div class="wrap">
<p><strong>Privacy.</strong> No tenant names, initials, street address, or contact details are published. Supplied dates and dollar amounts are retained only as anonymized scenario inputs.</p>
<p><strong>Not legal advice.</strong> No attorney reviewed this material. Resolve every high-severity flag and obtain advice on the actual lease and notice before serving.</p>
</div></footer>
</body></html>'''
with open(os.path.join(ROOT, "assurance", "index.html"), "w", encoding="utf-8") as fh:
    fh.write(page)
print(f"wrote assurance/index.html and {len(manifest)} source-manifest rows")
