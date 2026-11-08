#!/usr/bin/env python3
"""Generate the independent verification record at /verification/.

Reads verification/data.json and writes static HTML. Standard library only.
Every table row that makes a legal or arithmetic statement carries a link to a
registered official source; anything unverified is left blank and flagged.
"""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
S = {s["id"]: s for s in DATA["sources"]}

PAGES = [
    ("index.html", "Overview", "The answer first: the licence, the rate, and what is still unknown."),
    ("process.html", "Step by step", "Eight steps, in the order an owner actually needs them."),
    ("answers.html", "Your questions", "Each question answered from official text, with the gap stated where there is one."),
    ("units.html", "The two units", "Conditional arithmetic on the supplied figures, and what would change it."),
    ("checks.html", "Line-by-line checks", "34 published claims re-read against the official sources."),
    ("flags.html", "Flagged for review", "Unverified cells, official-page defects, and repository irregularities."),
    ("privacy.html", "Privacy", "What is withheld, what is retained, and how it was checked."),
    ("repo.html", "Repository audit", "What was verified in the repository, and what was found wrong."),
    ("sources.html", "Sources", "23 official sources, re-fetched on 8 November 2026."),
]


def esc(t) -> str:
    return html.escape(str(t), quote=False)


def attr(t) -> str:
    return html.escape(str(t), quote=True)


def src_links(ids) -> str:
    out = []
    for i in ids or []:
        s = S[i]
        out.append(f'<a class="src" href="{attr(s["url"])}" title="{attr(s["publisher"] + " — " + s["name"])}" '
                   f'target="_blank" rel="noopener">{esc(i)}</a>')
    return " ".join(out)


def ev_links(items) -> str:
    return " ".join(f'<a class="src" href="{attr(e["href"])}" target="_blank" rel="noopener">{esc(e["label"])}</a>'
                    for e in items or [])


def badge(status: str) -> str:
    s = status.lower()
    if s.startswith("verified arithmetic"):
        cls, txt = "b-calc", "Arithmetic"
    elif s.startswith("verified"):
        cls, txt = "b-ok", "Verified"
    elif s.startswith("unverified"):
        cls, txt = "b-blank", "Left blank"
    elif s.startswith("clean"):
        cls, txt = "b-ok", status
    elif s.startswith("retained"):
        cls, txt = "b-by", status
    elif s.startswith("irregular"):
        cls, txt = "b-warn", "Irregularity"
    elif s.startswith("flag"):
        cls, txt = "b-warn", "Flagged"
    else:
        cls, txt = "b-open", status
    extra = ""
    if status.strip().lower() != txt.strip().lower():
        extra = f'<span class="badge-text">{esc(status)}</span>'
    return f'<span class="badge {cls}">{esc(txt)}</span>{extra}'


def sev_badge(sev: str) -> str:
    cls = {"High": "b-hi", "Medium": "b-me", "Low": "b-lo"}.get(sev, "b-lo")
    return f'<span class="badge {cls}">{esc(sev)}</span>'


def table(headers, rows, caption="", cls="") -> str:
    th = "".join(f'<th scope="col">{h}</th>' for h in headers)
    tr = "".join(rows)
    cap = f"<caption>{caption}</caption>" if caption else ""
    return (f'<div class="tablewrap"><table class="t {cls}">{cap}'
            f'<thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>')


def nav(current: str) -> str:
    items = []
    for href, label, _ in PAGES:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    return "".join(items)


def page(fname: str, title: str, subtitle: str, body: str, eyebrow: str = "") -> str:
    label = next(p[1] for p in PAGES if p[0] == fname)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(label)} — Independent verification, SF 94122</title>
<meta name="description" content="{attr(subtitle)}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="hdr">
  <div class="wrap hdrin">
    <a class="brand" href="index.html"><span class="mk">✓</span><span>Independent verification<small>Outer Sunset · 94122 · checked 8 Nov 2026</small></span></a>
    <nav class="nav" aria-label="Main">{nav(fname)}</nav>
  </div>
</header>
<section class="band">
  <div class="wrap">
    {f'<p class="eyebrow">{esc(eyebrow)}</p>' if eyebrow else ''}
    <h1>{title}</h1>
    <p class="lede">{subtitle}</p>
  </div>
</section>
<main class="wrap">
{body}
</main>
<footer class="ftr">
  <div class="wrap">
    <p><strong>Privacy.</strong> No tenant names, initials, street address or private contact details are published here. The supplied dates and dollar amounts are retained unchanged, as instructed.</p>
    <p><strong>Scope.</strong> Every legal statement and every percentage on this site is quoted from an official source and linked in the row that uses it. Figures that could not be confirmed from an official source are left blank and listed on <a href="flags.html">Flagged for review</a>. Tenant-side figures use placeholders.</p>
    <p><strong>Not legal advice.</strong> This is an informational re-check of official material. A Rent Board counsellor can be reached on 415-252-4600 on weekday mornings and afternoons. <a href="../index.html">Canonical dashboard →</a></p>
  </div>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages
def build_index() -> str:
    n_flags = len(DATA["flags"])
    n_hi = sum(1 for f in DATA["flags"] if f["sev"] == "High")
    stats = [
        ("23", "official sources re-fetched"),
        ("34", "published claims re-read"),
        ("8", "dollar figures recomputed"),
        ("6", "notice dates recomputed"),
        (str(n_flags), "items flagged for review"),
    ]
    stat_html = "".join(
        f'<div class="stat{" hi" if k == str(n_flags) else ""}"><b>{k}</b><span>{esc(v)}</span></div>'
        for k, v in stats)

    qa = "".join(
        f'<a class="card" href="answers.html#q{i+1}"><b>{esc(q["q"])}</b>'
        f'<span>{esc(q["a"].split(". ")[0])}.</span></a>'
        for i, q in enumerate(DATA["questions"][:3]))

    hi = [f for f in DATA["flags"] if f["sev"] == "High"]
    hi_rows = [
        f'<tr><td><a href="flags.html#{esc(f["id"])}">{esc(f["id"])}</a></td><td>{esc(f["item"])}</td>'
        f'<td>{esc(f["effect"])}</td><td>{src_links(f["src"])}{ev_links(f.get("evidence"))}</td></tr>'
        for f in hi
    ]

    body = f"""
<section>
  <h2>The answer, in the order it matters</h2>
  <div class="answer">
    <h3>Yes — one individual owner still needs a Rent Increase Licence for each tenant-occupied unit. But there is no application about the increase itself.</h3>
    <p>The licence is not a form you send the Board about a specific increase. It is created automatically when you report the unit in the annual <strong>Housing Inventory</strong>, it is free, and it must be current when the increase takes effect. Ordinary annual and banked increases are not submitted to the Board for approval.</p>
    <p><strong>The one deadline that matters:</strong> a current licence on the increase's <strong>effective date</strong>. Without it the increase cannot take effect and the tenant does not owe it for the months the licence was suspended. Confirm the licence before you serve notice, so a fixable omission never becomes an unenforceable increase.</p>
  </div>
  <div class="grid3">{qa}<a class="card" href="answers.html"><b>All eight questions →</b><span>Coverage, the rate, notice, corporations versus individuals, one unit or both, and the tenant-lawyer test.</span></a></div>
</section>

<section>
  <h2>What this page is<span class="sub">An independent second pass over material that was already published, not a new edition of it.</span></h2>
  <p>The repository already contains a canonical dashboard. This record exists to check it: each of its 23 official sources was re-fetched on <strong>8 November 2026</strong>, each published quotation was compared with the live page, and every dollar figure and notice date was recomputed from scratch. Where the check found a discrepancy — in the source, in the arithmetic, or in the repository itself — it is written down rather than smoothed over.</p>
  <div class="stats">{stat_html}</div>
  <div class="note">
    <p><strong>What changed as a result:</strong> nothing in the published figures. All eight dollar amounts re-computed to the cent and all six notice dates to the day. The findings that survived are wording qualifications, missing private facts, two defects on the Board's own pages, and two repository housekeeping items.</p>
  </div>
</section>

<section>
  <h2>The three things that can still stop this<span class="sub">High-severity open items. Each has the official source that makes it matter.</span></h2>
  {table(["Flag", "Open item", "Why it changes the answer", "Source"], hi_rows,
         caption=f"{n_hi} high-severity items out of {n_flags} flagged. None of them is a reason to guess a value; each is a record to go and read.")}
</section>

<section>
  <h2>The only verified benchmark for “reasonable”<span class="sub">And why the market comparison stays blank.</span></h2>
  <div class="split">
    <div class="kpiv">
      <div class="k">1.6%</div>
      <div class="lbl">published annual allowance</div>
      <p>For increases taking effect 1 March 2026 – 28 February 2027. {src_links(["S06","S05"])}</p>
    </div>
    <div class="kpiv blank">
      <div class="k">—</div>
      <div class="lbl">ZIP 94122 “normal” market increase</div>
      <p>No official source publishes one. The cell is left blank rather than filled from commercial listings. <a href="flags.html#F-05">F-05</a></p>
    </div>
  </div>
  <p>Properly banked percentages can be added to the current allowance where the records support them, and a landlord may always take less. What the official sources do not provide is any data-driven “usual” increase for this ZIP, so the honest comparison is against the published allowance itself.</p>
</section>

<section>
  <h2>What each page covers</h2>
  <div class="grid3">
    <a class="card" href="process.html"><b>Step by step</b><span>Eight steps from coverage to proof of service, in the order they must happen.</span></a>
    <a class="card" href="answers.html"><b>Your questions</b><span>All eight, answered from the ordinance and the statutes.</span></a>
    <a class="card" href="units.html"><b>The two units</b><span>Conditional arithmetic for both units, with the unresolved inputs marked.</span></a>
    <a class="card" href="checks.html"><b>Line-by-line checks</b><span>34 claims, each with its verdict, its basis and its source.</span></a>
    <a class="card" href="flags.html"><b>Flagged for review</b><span>15 items: missing private facts, official-page defects, repository issues.</span></a>
    <a class="card" href="privacy.html"><b>Privacy</b><span>What is withheld and how the sweep was run.</span></a>
    <a class="card" href="repo.html"><b>Repository audit</b><span>What passed, and the two housekeeping items found.</span></a>
    <a class="card" href="sources.html"><b>Sources</b><span>All 23, with the passage each one supports.</span></a>
    <a class="card" href="../index.html"><b>Canonical dashboard →</b><span>The main edition this record verifies.</span></a>
  </div>
</section>
"""
    return page("index.html", "A line-by-line re-check of the San&#8209;Francisco rent&#8209;increase record",
                "Every claim re-read against its official source, every figure recomputed. The licence question comes first because it is the one that decides whether an increase can be enforced at all.",
                body, eyebrow="Independent verification · 8 November 2026")


def build_process() -> str:
    rows = []
    for s in DATA["steps"]:
        if s["status"].startswith("Verified"):
            st_cell = badge(s["status"])
        else:
            st_cell = f'<span class="tag">{esc(s["status"])}</span>'
        rows.append(
            f'<tr id="s{s["n"]}"><td class="n">{s["n"]}</td>'
            f'<td><b>{esc(s["title"])}</b><div class="sub2">{esc(s["what"])}</div></td>'
            f'<td>{esc(s["why"])}</td>'
            f'<td class="nowrap">{st_cell}</td>'
            f'<td>{src_links(s["src"])}</td></tr>')

    body = f"""
<section>
  <h2>The licence, precisely<span class="sub">Because this is the part the owner's premise gets almost right.</span></h2>
  <div class="answer">
    <h3>You do not apply for permission for each increase. You keep a licence current by reporting once a year.</h3>
    <p>Two separate duties are often confused. The <strong>reporting duty</strong> is annual and Board-facing: it is the Housing Inventory. The <strong>licence</strong> is the automatic result of that reporting for a tenant-occupied unit. The <strong>notice</strong> is tenant-facing and is not filed with the Board.</p>
    <p>What that means in practice: the compliance work happens <em>before</em> the notice and does not mention the notice. If the report is already current for both units, an ordinary 1.6% increase needs no additional Board step at all.</p>
  </div>
</section>

<section>
  <h2>Eight steps, in order<span class="sub">Steps 1 and 2 decide whether the arithmetic is even usable. Steps 5 and 6 are where most defects occur.</span></h2>
  {table(["#", "Step", "Why it matters", "Status", "Official source"], rows,
         caption="“Owner must confirm” and “Owner must supply records” mean the answer depends on private documents that are not in this record.")}
</section>

<section>
  <h2>Two things that are easy to get wrong</h2>
  <div class="split">
    <div class="note">
      <p><strong>1. The rate is chosen by the effective date, not the notice date.</strong> A notice served in December 2026 for a February 2027 increase uses the 1.6% that is in force in February 2027. If the increase were delayed into March 2027, the percentage would be whatever the Board publishes for the new year — which is not yet published. {src_links(["S05","S06"])}</p>
    </div>
    <div class="note">
      <p><strong>2. The behaviour of the occupant change matters more than the percentage.</strong> A partial change — one original tenant stays — does not reset the rent. A full turnover can. Between those two answers is a different legal route, and it turns on who actually remained. {src_links(["S11"])}</p>
    </div>
  </div>
</section>

<section>
  <h2>What the licence is not</h2>
  {table(["It is not…", "What the official text says", "Source"], [
    ('<tr><td>A fee</td><td>“Reporting is free and can be done online 24/7”.</td><td>' + src_links(["S03"]) + '</td></tr>'),
    ('<tr><td>Approval of the percentage</td><td>Banked increases “do not have to be approved by the Rent Board”; the annual allowance is published for everyone.</td><td>' + src_links(["S04","S05"]) + '</td></tr>'),
    ('<tr><td>A copy of the notice sent to the Board</td><td>No such filing appears in §37.3 (what the tenant must be told) or §37.15 (what the Board must be told).</td><td>' + src_links(["S02","S01"]) + '</td></tr>'),
    ('<tr><td>The same thing as the Rent Board Fee</td><td>The fee is $59.00 per dwelling unit for 2026–27, due 1 March unless exempt; requesting a fee exemption does not satisfy the Housing Inventory.</td><td>' + src_links(["S17","S03"]) + '</td></tr>'),
    ('<tr><td>Something you attach to the notice</td><td>“The rent increase license does not need to be included with your rent increase notice.”</td><td>' + src_links(["S03"]) + '</td></tr>'),
  ], caption="Five confusions that produce avoidable work — or an avoidable defect.")}
</section>
"""
    return page("process.html", "The Rent Board process, step by step",
                "Eight steps from confirming coverage to keeping proof of service. The licence is created by the annual report, so the work happens before the notice and the notice is never filed with the Board.",
                body, eyebrow="Question 1 of 8 · the licence and the Board")


def build_answers() -> str:
    blocks = []
    for i, q in enumerate(DATA["questions"]):
        blocks.append(
            f'<section id="q{i+1}" class="qa"><h2>{esc(q["q"])}<span class="sub">Answer, then the official basis.</span></h2>'
            f'<div class="answer"><p>{esc(q["a"])}</p></div>'
            f'<p class="srcrow">{src_links(q["src"])}</p></section>')
    body = "".join(blocks) + """
<section>
  <h2>Reading the sources yourself<span class="sub">Three of them carry most of the answer.</span></h2>
  <div class="grid3">
    <a class="card" href="https://www.sf.gov/rent-board-housing-inventory" target="_blank" rel="noopener"><b>Housing Inventory</b><span>The licence, the 1 March deadline, late filing and the effective-date rule.</span></a>
    <a class="card" href="https://www.sf.gov/information--sec-3715-reporting-obligations-licensing" target="_blank" rel="noopener"><b>§37.15</b><span>The ordinance text: who must report, what the licence is, and what happens without it.</span></a>
    <a class="card" href="https://www.sf.gov/learn-about-rent-increases-san-francisco" target="_blank" rel="noopener"><b>Rent increases</b><span>The 1.6% rate, base-rent calculation, notice periods and additional occupants.</span></a>
  </div>
</section>
"""
    return page("answers.html", "Your eight questions, answered from the text",
                "Each answer is limited to what the official sources actually say. Where a question cannot be answered from an official source, that is stated rather than filled in.",
                body, eyebrow="Question by question")


def build_units() -> str:
    rows = []
    for u in DATA["units"]:
        rows.append(
            f'<tr><td><b>{esc(u["unit"])}</b><div class="sub2">{esc(u["tenants"])}</div></td>'
            f'<td class="num">{esc(u["base_input"])}<div class="sub2">{esc(u["lease_start"])}</div></td>'
            f'<td>{esc(u["annual"])}<div class="sub2">{esc(u["annual_new"])}</div></td>'
            f'<td>{esc(u["combined"])}<div class="sub2">{esc(u["combined_new"])}</div></td>'
            f'<td>{esc(u["verified_note"])}</td><td>{src_links(u["src"])}</td></tr>')

    body = f"""
<section>
  <h2>What the arithmetic says — and what it does not<span class="sub">The percentages are official; the base rents are the owner's figures, not verified current rents.</span></h2>
  <div class="note">
    <p><strong>Read these as worked examples, not as permission to serve a notice.</strong> Every multiplication was rechecked with exact decimal arithmetic and matches to the cent. But the inputs come from the owner's brief: one base rent is a 2019 lease-start figure, and neither licence, ledger nor lease was available. A different base changes every number below.</p>
  </div>
  {table(["Unit", "Base rent used", "Annual only", "With banked amounts", "Verification status", "Sources"], rows,
         caption="New base rents are shown under each calculation. Percentages from Form 571; method from Rule 4.12 and the Board's banking page.")}
</section>

<section>
  <h2>Unit 1: why the lease matters more than the percentage</h2>
  <p>The reported facts are a lease beginning <strong>1 February 2025</strong> at $3,995.00, with a continuing tenancy attributed to <strong>1 April 2026</strong> at the same $3,995.00, and one original tenant still in place. Two consequences follow, and only one of them is arithmetic.</p>
  {table(["Question", "What the official text says", "What it means for Unit 1", "Source"], [
    ('<tr><td>Can rent be raised during a fixed term?</td><td>“the landlord cannot raise the tenant’s rent during the tenancy, unless the rental agreement expressly allows rent increases.”</td><td>If April 2026 began a term that runs past the intended effective date, a February 2027 increase is premature.</td><td>' + src_links(["S20"]) + '</td></tr>'),
    ('<tr><td>Does a partial occupant change reset the rent?</td><td>The reset applies where the original occupants no longer reside there and “does not apply to partial changes in occupancy … where one or more of the occupants … remains”.</td><td>Because one original tenant remained, the rent is not reset — so the ordinary allowance applies, not a new market rent.</td><td>' + src_links(["S11"]) + '</td></tr>'),
    ('<tr><td>How much is the allowance?</td><td>1.6% for increases effective 1 March 2026 – 28 February 2027.</td><td>$63.92, giving $4,058.92. A further 1.4% ($55.93) is available only if the ledger supports a banked year.</td><td>' + src_links(["S06","S04"]) + '</td></tr>'),
  ], caption="Three separate questions; a correct percentage does not answer the first two.")}
</section>

<section>
  <h2>Unit 2: the largest number rests on the weakest input</h2>
  <p>The reported facts are a lease beginning <strong>1 June 2019</strong> at $3,150.00. Six annual allowances have come and gone since then — 1.8%, 0.7%, 2.3%, 3.6%, 1.7% and 1.4% — and if none was ever taken they add to 11.5%, or $362.25, on top of the current 1.6%.</p>
  <div class="split">
    <div class="kpiv"><div class="k">$412.65</div><div class="lbl">13.1% on $3,150.00 → $3,562.65</div><p>The full conditional illustration. {src_links(["S06","S04"])}</p></div>
    <div class="kpiv blank"><div class="k">—</div><div class="lbl">confirmed current base rent</div><p>Not supplied. Any increase since 2019 reduces the bank and changes the anniversary. <a href="flags.html#F-04">F-04</a></p></div>
  </div>
  <p>Two checks decide whether any of that is available. First, banking requires that no increase was taken in the intervening period; a single increase in one of those years breaks the chain for that year. Second, the 12-month spacing rule means the increase lands on an anniversary, not on an arbitrary date. Both are answerable from the ledger and from neither of the figures supplied. {src_links(["S04","S07"])}</p>
</section>

<section>
  <h2>Notice timing arithmetic<span class="sub">Planning dates only; the eligibility questions above come first.</span></h2>
  {table(["Scenario", "Effective date", "30 days", "Plus 5 for mail", "90 days", "Plus 5 for mail", "Source"], [
    '<tr><td>Unit 1 — annual only, or with the 1.4% banked component (≤10%)</td><td class="num">1 Feb 2027</td><td class="num">2 Jan 2027</td><td class="num">28 Dec 2026</td><td class="num">—</td><td class="num">—</td><td>' + src_links(["S08","S21"]) + '</td></tr>',
    '<tr><td>Unit 2 — annual only (≤10%)</td><td class="num">28 Feb 2027</td><td class="num">29 Jan 2027</td><td class="num">24 Jan 2027</td><td class="num">—</td><td class="num">—</td><td>' + src_links(["S08","S21"]) + '</td></tr>',
    '<tr><td>Unit 2 — combined 13.1% (>10%)</td><td class="num">28 Feb 2027</td><td class="num">—</td><td class="num">—</td><td class="num">30 Nov 2026</td><td class="num">25 Nov 2026</td><td>' + src_links(["S08","S21"]) + '</td></tr>',
  ], caption="Computed by subtracting the statutory period from the effective date. Code of Civil Procedure §1013 extends the period by 5 calendar days for mail inside California, 10 elsewhere in the U.S. and 20 outside it.")}
  <p class="srcrow">Notice periods: {src_links(["S08"])} · mail extension: {src_links(["S21"])} · which percentage applies: {src_links(["S05"])}</p>
  <div class="note"><p><strong>A date on a calendar is not a clearance.</strong> Weekends, court holidays, proof of service and the unresolved questions above all sit between this arithmetic and a notice that survives review. Serve earlier than these dates, not on them.</p></div>
</section>
"""
    return page("units.html", "The two units, recalculated",
                "The percentages are official and the arithmetic is exact. The base rents are the owner's figures, and the records that would confirm them were not available — so every result here is conditional.",
                body, eyebrow="Calculations")


def build_checks() -> str:
    rows = []
    for c in DATA["claims"]:
        rows.append(
            f'<tr id="{esc(c["id"])}"><td class="mono">{esc(c["id"])}</td><td>{esc(c["area"])}</td>'
            f'<td>{esc(c["claim"])}</td><td>{badge(c["status"])}</td>'
            f'<td class="basis">{esc(c["basis"])}</td><td>{src_links(c["src"])}</td></tr>')
    n = len(DATA["claims"])
    n_ok = sum(1 for c in DATA["claims"] if c["status"].startswith("Verified"))
    n_blank = sum(1 for c in DATA["claims"] if c["status"].startswith("Unverified"))
    body = f"""
<section>
  <h2>Every published claim, re-read<span class="sub">{n} statements across six areas. {n_ok} confirmed against the official text; {n_blank} left deliberately blank.</span></h2>
  <div class="note"><p><strong>Method.</strong> Each source was re-fetched on 8 November 2026 and the sentence it is cited for was read in the live page, not taken from the earlier record's summary. A claim was marked verified only if the live text supported it on its own; where the live text supported a narrower statement than the one published, the claim is marked <em>worth qualified</em> and the qualification is written into the basis column.</p></div>
  {table(["ID", "Area", "Claim as published", "Result", "Basis — what the official text actually says", "Sources"], rows,
         caption="A “Verified” result means the source supports the statement. It does not mean the increase is lawful for these units: that depends on the private facts listed on the flags page.")}
</section>
<section>
  <h2>What “left blank” means here<span class="sub">Two claims could not be verified at all, and both keep their cell empty.</span></h2>
  <div class="split">
    <div class="note"><p><strong>The ZIP-level “normal” increase.</strong> No official source publishes one for covered units in 94122. Commercial listing services do publish rent statistics, but they are not official publications and were excluded rather than used to fill the gap. {src_links(["S05"])}</p></div>
    <div class="note"><p><strong>Owner behaviour by entity type.</strong> The sources state rules that bind every landlord; none measures how individuals behave compared with corporations. The absence of data is recorded as an absence, not turned into a claim about either group. {src_links(["S16","S22"])}</p></div>
  </div>
</section>
"""
    return page("checks.html", "Thirty-four claims, checked line by line",
                "Each statement the published record makes about the law, the arithmetic or the practice, with the verdict, the passage that supports it, and the source.",
                body, eyebrow="Verification record")


def build_flags() -> str:
    rows = []
    for f in DATA["flags"]:
        links = src_links(f["src"])
        ev = ev_links(f.get("evidence"))
        if ev:
            links = (links + " " if links else "") + ev
        if not links:
            links = '<span class="muted">Repository record</span>'
        rows.append(
            f'<tr id="{esc(f["id"])}"><td class="mono">{esc(f["id"])}</td><td>{sev_badge(f["sev"])}</td>'
            f'<td><b>{esc(f["item"])}</b><div class="sub2">{esc(f["detail"])}</div></td>'
            f'<td>{esc(f["effect"])}</td><td>{esc(f["action"])}</td><td>{links}</td></tr>')
    n = len(DATA["flags"])
    hi = sum(1 for f in DATA["flags"] if f["sev"] == "High")
    me = sum(1 for f in DATA["flags"] if f["sev"] == "Medium")
    lo = sum(1 for f in DATA["flags"] if f["sev"] == "Low")
    body = f"""
<section>
  <h2>Nothing here is an estimate<span class="sub">{n} items: {hi} high, {me} medium, {lo} low. None of them blocks publication; all of them block serving a notice from this record alone.</span></h2>
  <div class="note"><p><strong>How to read this page.</strong> A high-severity item is one where an unknown fact could change whether an increase is lawful at all — a fixed term, a current base rent, a licence. Medium items change the amount or expose a defect. Low items are wording, housekeeping and presentation problems that are recorded so they are not rediscovered later.</p></div>
  {table(["ID", "Severity", "Item", "Why it matters", "What would close it", "Source or evidence"], rows,
         caption="Every row names the official source that makes the point, or the repository evidence for a housekeeping finding.")}
</section>
<section>
  <h2>The three that would change the answer</h2>
  <div class="grid3">
    <a class="card warn" href="#F-03"><b>F-03 · Unit 1 is a fixed term</b><span>If the April 2026 instrument set a term past the effective date without an escalation clause, a February 2027 increase is premature.</span></a>
    <a class="card warn" href="#F-04"><b>F-04 · Unit 2 base is from 2019</b><span>The $412.65 illustration assumes no increase since 2019. One increase in those years breaks it.</span></a>
    <a class="card warn" href="#F-06"><b>F-06 · Licence not confirmed</b><span>Without a current licence the increase cannot take effect, and the tenant does not owe it for the suspended months.</span></a>
  </div>
</section>
"""
    return page("flags.html", "Flagged for review",
                "Every value that could not be confirmed from an official source, every defect found on an official page, and every repository irregularity — with the source that makes it matter.",
                body, eyebrow="Flagged for review · needs the owner's records")


def build_privacy() -> str:
    rows = [f'<tr><td><b>{esc(p["check"])}</b></td><td>{esc(p["finding"])}</td><td>{badge(p["status"])}</td></tr>'
            for p in DATA["privacy"]]
    body = f"""
<section>
  <h2>Placeholders, not names<span class="sub">The supplied dates and dollar amounts are the substance of the analysis, so they stay exactly as given. The people do not appear.</span></h2>
  {table(["What was checked", "What was found", "Result"], rows,
         caption="A repository-wide scan also looked for standalone one- and two-letter tokens, email addresses and street addresses in every published file.")}
</section>
<section>
  <h2>Why the amounts stay but the names do not</h2>
  <div class="split">
    <div class="note"><p><strong>The figures are the question.</strong> Whether $63.92 on $3,995.00 is the right calculation cannot be checked without the numbers, so 1 February 2025, 1 April 2026, $3,995.00, 1 June 2019 and $3,150.00 are reproduced unchanged. They identify a rent, not a person.</p></div>
    <div class="note"><p><strong>The identities are not needed.</strong> Nothing in the analysis depends on who the tenants are. They appear as “two placeholders” and “one original tenant and one replacement occupant”, which preserves exactly the fact that matters — how many original occupants remained. {src_links(["S11"])}</p></div>
  </div>
  <p>The street address is likewise withheld. The record refers only to the Outer Sunset and ZIP 94122, which is the level at which the Rent Ordinance and the published rate apply.</p>
</section>
<section>
  <h2>What a reader can and cannot infer</h2>
  <p>From this record a reader can learn the applicable rate, the method, the notice periods and the two units' rent history. They cannot identify the tenants, the building or the owner. Earlier drafts in the same repository already used lettered placeholders, and a scan of the current published tree found no raw initials, no email addresses and no street address.</p>
</section>
"""
    return page("privacy.html", "What is withheld, and what is kept",
                "Tenant identities and the street address are withheld. The dates and dollar amounts that the analysis depends on are kept exactly as supplied.",
                body, eyebrow="Privacy")


def build_repo() -> str:
    rows = [f'<tr><td><b>{esc(r["area"])}</b></td><td>{esc(r["finding"])}</td><td>{badge(r["status"])}</td></tr>'
            for r in DATA["repo"]]
    body = f"""
<section>
  <h2>The repository, checked rather than trusted<span class="sub">Sources, quotes, arithmetic, generators, checks and privacy — plus the housekeeping that was wrong.</span></h2>
  {table(["Area", "Finding", "Result"], rows, caption="Compiled on 8 November 2026 against commit 903f649 and this session's branch.")}
</section>
<section>
  <h2>How the checks were run</h2>
  <p>The arithmetic was recomputed independently with exact decimal arithmetic rather than floating point, so a fraction of a cent cannot hide in a rounded display. The six notice dates were recomputed by subtracting the statutory period from the effective date. The published generator was re-run and produced no diff, which shows the committed pages match their data. All seven existing verification suites were executed on this tree and all pass.</p>
  <div class="note"><p><strong>Independent means independent.</strong> This record re-fetched the sources itself and formed its own view of each claim. Where it agreed with the published record it says so; where it found a narrower correct statement, it records the qualification; and where it found a defect it writes the defect down instead of editing around it.</p></div>
</section>
<section>
  <h2>Two things that should be fixed in the repository</h2>
  <div class="split">
    <div class="note"><p><strong>Tracked cache files.</strong> Two compiled Python files are committed and there is no root <code>.gitignore</code>. They change on every local run, which manufactures diffs for the next session that works here. <a href="flags.html#F-12">F-12</a></p></div>
    <div class="note"><p><strong>Two stale pull requests.</strong> Two earlier parallel editions were superseded by the integrated site but their pull requests are still open. They are harmless to the published site and are flagged rather than closed here. <a href="flags.html#F-11">F-11</a></p></div>
  </div>
</section>
"""
    return page("repo.html", "Repository audit",
                "What was verified in the repository itself: the sources it cites, the figures it prints, the generator that produces its pages, and the state of its own housekeeping.",
                body, eyebrow="Repository")


def build_sources() -> str:
    rows = []
    for s in DATA["sources"]:
        rows.append(
            f'<tr id="{esc(s["id"])}"><td class="mono">{esc(s["id"])}</td>'
            f'<td><a href="{attr(s["url"])}" target="_blank" rel="noopener">{esc(s["name"])}</a>'
            f'<div class="sub2">{esc(s["publisher"])}</div></td>'
            f'<td>{esc(s["level"])}</td>'
            f'<td class="quote">“{esc(s["quote"])}”</td>'
            f'<td>{esc(s["used_for"])}</td>'
            f'<td class="nowrap">{esc(s["checked"])}</td></tr>')
    levels = {}
    for s in DATA["sources"]:
        levels[s["level"]] = levels.get(s["level"], 0) + 1
    lv = " · ".join(f"{k} ({v})" for k, v in sorted(levels.items(), key=lambda x: -x[1]))
    body = f"""
<section>
  <h2>Twenty-three official sources, re-fetched<span class="sub">{esc(lv)}</span></h2>
  <p>Every source below was retrieved and read on <strong>8 November 2026</strong>. The quotation is the passage the record relies on, not a paraphrase. Where a page has changed since an earlier review, the current text is what is quoted here.</p>
  {table(["ID", "Source", "Level", "Passage relied on", "Used to confirm", "Checked"], rows,
         caption="All sources are government or legislature publications. No commercial source is cited for any value.")}
</section>
<section>
  <h2>Two sources worth reading in full</h2>
  <div class="split">
    <div class="note"><p><strong>The Housing Inventory page</strong> answers the licence question in a few paragraphs and is the single most useful page for an owner in this position. It also states the effective-date rule and confirms that reporting is free and that late filing is accepted. <a href="https://www.sf.gov/rent-board-housing-inventory" target="_blank" rel="noopener">sf.gov →</a></p></div>
    <div class="note"><p><strong>Form 571</strong> is the only place the full historical rate table appears, and it is what the worked examples in this record are read from — including where the Board's own example pages mislabel a year. <a href="https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf" target="_blank" rel="noopener">Form 571 (PDF) →</a></p></div>
  </div>
</section>
"""
    return page("sources.html", "Sources",
                "Twenty-three official publications, each re-fetched for this check, with the exact passage relied on and what it was used to confirm.",
                body, eyebrow="Source register")


BUILDERS = {
    "index.html": build_index,
    "process.html": build_process,
    "answers.html": build_answers,
    "units.html": build_units,
    "checks.html": build_checks,
    "flags.html": build_flags,
    "privacy.html": build_privacy,
    "repo.html": build_repo,
    "sources.html": build_sources,
}


def main() -> None:
    for fname, _label, _sub in PAGES:
        out = ROOT / fname
        out.write_text(BUILDERS[fname](), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
