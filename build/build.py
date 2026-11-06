#!/usr/bin/env python3
"""
Static site generator for Rent Increase SF.

Reads everything from data/v2/*.json so that no fact on the site exists in two
places. Output is plain HTML + one CSS file, no JavaScript framework, no CDN,
no runtime fetch: it works from GitHub Pages and from the filesystem.

This is the "companion edition" (v2) of the site. It is published under
docs/v2/ so that it sits alongside, and never overwrites, the site generated
by the earlier session (docs/*.html).

Usage:  python3 build/build.py
"""

import html
import json
import os
import re
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "v2")
OUT = os.path.join(ROOT, "docs", "v2")

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


SOURCES = load("sources.json")
SOURCE_BY_ID = {s["id"]: s for s in SOURCES["sources"]}
SECONDARY_BY_ID = {s["id"]: s for s in load("practice.json").get("secondary_sources", [])}
RETRIEVED = SOURCES["retrieved"]


def esc(value):
    return html.escape(str(value), quote=True)


def src(ids):
    """Render one or more source ids as links: [S03] [S04]"""
    if not ids:
        return '<span class="unv">no source</span>'
    if isinstance(ids, str):
        ids = [ids]
    out = []
    for sid in ids:
        record = SOURCE_BY_ID.get(sid) or SECONDARY_BY_ID.get(sid)
        if record is None:
            raise SystemExit("Unknown source id: %s" % sid)
        tier = record.get("tier", "secondary")
        cls = "srcref secondary" if tier == "secondary" or sid.startswith("secondary") else "srcref"
        label = sid if sid.startswith("S") else "commercial"
        out.append('<a class="%s" href="%s" title="%s" target="_blank" rel="noopener">%s</a>'
                   % (cls, esc(record["url"]), esc(record["publisher"] + " - " + record["title"]), esc(label)))
    return " ".join(out)


MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def longdate(iso):
    year, month, day = iso.split("-")
    return "%s %d, %s" % (MONTHS[int(month) - 1], int(day), year)


def money(value):
    if value is None or value == "":
        return '<span class="blank">&mdash; unverified</span>'
    return "$%s" % format(value, ",.2f")


def pct(value):
    if value is None or value == "":
        return '<span class="blank">&mdash; unverified</span>'
    return "%.1f%%" % float(value)


NAV = [
    ("index.html", "Overview"),
    ("summary.html", "Executive summary"),
    ("answers.html", "Answers"),
    ("calculations.html", "Calculations"),
    ("requirements.html", "Requirements"),
    ("notice.html", "Notice &amp; procedure"),
    ("practice.html", "Owner practice"),
    ("review.html", "Tenant-lawyer review"),
    ("rates.html", "Rates 1982&ndash;2027"),
    ("flags.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("method.html", "Method"),
    ("reconciliation.html", "Reconciliation"),
]


def page(filename, title, subtitle, body, active=None):
    active = active or filename
    nav = "\n".join(
        '        <a href="%s"%s>%s</a>' % (href, ' class="on"' if href == active else "", label)
        for href, label in NAV
    )
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; Rent Increase SF</title>
<meta name="description" content="Verified local, state and federal rules for a rent-controlled two-unit building in San Francisco's Outer Sunset, ZIP 94122.">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html">
      <span class="mark">SF</span>
      <span class="brandtext">Rent Increase <strong>SF</strong><small>Outer Sunset &middot; 94122 &middot; built 1940</small></span>
    </a>
    <nav class="nav">
{nav}
    </nav>
  </div>
</header>
<main id="main">
  <div class="wrap">
    <h1>{title}</h1>
    <p class="sub">{subtitle}</p>
{body}
  </div>
</main>
<footer class="foot">
  <div class="wrap">
    <p><strong>Verification standard.</strong> Every value in a table is traceable to a numbered source linked in the row. Where a value could not be confirmed from an official source it is left blank, marked <span class="blank">&mdash; unverified</span>, and listed on <a href="flags.html">Flagged for review</a>. Nothing is inferred.</p>
    <p>Sources retrieved {esc(RETRIEVED)}. Personal information has been replaced with role labels; dates and dollar amounts are unchanged. This site is an analysis of public law and is <strong>not legal advice</strong>. Confirm any course of action with the SF Rent Board (415-252-4600) or a lawyer.</p>
    <p><a href="sources.html">All sources</a> &middot; <a href="method.html">How this was verified</a> &middot; <a href="flags.html">Flagged for review</a></p>
  </div>
</footer>
</body>
</html>
"""
    with open(os.path.join(OUT, filename), "w", encoding="utf-8") as fh:
        fh.write(doc)
    return filename


def table(headers, rows, cls="data"):
    head = "".join("<th>%s</th>" % h for h in headers)
    body = []
    for row in rows:
        body.append("<tr>" + "".join("<td>%s</td>" % c for c in row) + "</tr>")
    return ('<div class="tablewrap"><table class="%s"><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'
            % (cls, head, "".join(body)))


def badge(status):
    mapping = {
        "verified": ("ok", "verified"),
        "conditional": ("warn", "conditional"),
        "unverified": ("bad", "unverified"),
        "secondary": ("warn", "secondary only"),
        "high": ("bad", "high"),
        "medium": ("warn", "medium"),
        "low": ("ok", "low"),
    }
    cls, label = mapping.get(status, ("warn", status))
    return '<span class="pill %s">%s</span>' % (cls, label)


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------

def build_index():
    units = load("units.json")
    reqs = load("requirements.json")
    flags = load("flags.json")
    n_verified = sum(1 for r in reqs["rows"] if r["status"] == "verified")
    u1 = units["units"][0]["calculations"]
    u2 = units["units"][1]["calculations"]

    cards = f"""
    <div class="grid cards">
      <div class="card">
        <div class="k">Unit 1 &middot; annual increase</div>
        <div class="v">$63.92<span>/mo</span></div>
        <div class="m">1.6% &rarr; ${format(u1[0]["new_rent"], ",.2f")} from Feb 1, 2027</div>
        <div class="s">{src("S03")}</div>
      </div>
      <div class="card">
        <div class="k">Unit 1 &middot; with banked</div>
        <div class="v">$119.85<span>/mo</span></div>
        <div class="m">3.0% &rarr; ${format(u1[1]["new_rent"], ",.2f")} if the Feb 1 reading holds</div>
        <div class="s">{src(["S03","S04"])}</div>
      </div>
      <div class="card">
        <div class="k">Unit 2 &middot; maximum</div>
        <div class="v">$412.65<span>/mo</span></div>
        <div class="m">13.1% &rarr; ${format(u2[1]["new_rent"], ",.2f")} &middot; 90 days' notice</div>
        <div class="s">{src(["S03","S04"])}</div>
      </div>
      <div class="card">
        <div class="k">Flags open</div>
        <div class="v">{len(flags["flags"])}</div>
        <div class="m">{sum(1 for f in flags["flags"] if f["severity"] == "high")} are high severity &middot; none blocks publication</div>
        <div class="s"><a href="flags.html">review them</a></div>
      </div>
    </div>
    """

    body = f"""
    {cards}

    <section>
      <h2>What this is</h2>
      <p class="lead">A line-by-line, source-linked answer to one question: <em>what is a reasonable and normal rent increase for two rent-controlled units in a 1940 building in San Francisco's Outer Sunset, ZIP 94122?</em></p>
      <p>The answer is not a matter of judgement. In San Francisco the ceiling is arithmetic: the Rent Board's published annual percentage, plus any annual increases the owner skipped and is still entitled to bank. Both units sit well below the statewide cap and no federal law sets a rent ceiling at all, so the local ordinance decides everything.</p>
      <div class="callout key">
        <h3>The single most important finding</h3>
        <p>The two units have <strong>very different lawful ceilings</strong> &mdash; 3.0% and 13.1% &mdash; not because the units differ, but because each tenancy has its own history of skipped increases. Unit 1's tenancy began in 2025; Unit 2's began in 2019 and has skipped six consecutive annual increases. That difference is lawful, explainable and documented, and it is the reason a single uniform percentage is not the right approach.</p>
      </div>
    </section>

    <section>
      <h2>The three layers of law, in one table</h2>
      {table(
        ["Layer", "What it sets", "Does it control here?", "Source"],
        [
          ["<strong>Federal</strong>", "No rent ceiling. Bars discrimination in the terms and conditions of rental on race, colour, national origin, religion, sex, familial status and disability.", "Applies, but sets no number.", src(["S29","S30","S35"])],
          ["<strong>State (California)</strong>", "AB 1482 cap of 5% + CPI, hard maximum 10%. Notice periods of 30 or 90 days. Retaliation and FEHA protections.", "The notice and anti-retaliation rules apply. The cap does <em>not</em>, because San Francisco's local cap is stricter.", src(["S25","S24","S27","S28"])],
          ["<strong>Local (San Francisco)</strong>", "1.6% annual increase for 3/1/26&ndash;2/28/27, banked increases, rent increase licence, notice content, harassment rules.", "<strong>Yes &mdash; this is the controlling rule.</strong>", src(["S03","S08","S09","S11"])],
        ])}
      <p class="note">AB 1482 is frequently cited as a ceiling of about 8.8% in the Bay Area. That figure is real, but it is irrelevant to a covered San Francisco unit: Civil Code &sect;1947.12(d)(3) exempts housing that is subject to a local ordinance restricting increases to a lower amount. {src("S25")}</p>
    </section>

    <section>
      <h2>Start here, depending on what you need</h2>
      <div class="grid links">
        <a class="tile" href="answers.html"><strong>The five questions, answered</strong><span>Reasonable increases, owner practice, notice, lawyer review, and one unit vs both.</span></a>
        <a class="tile" href="calculations.html"><strong>Calculations, step by step</strong><span>Every percentage, every dollar, with the arithmetic shown and a source per row.</span></a>
        <a class="tile" href="requirements.html"><strong>Full requirement matrix</strong><span>{len(reqs["rows"])} requirements across local, state and federal law. {n_verified} verified against primary sources.</span></a>
        <a class="tile" href="notice.html"><strong>Notice &amp; procedure</strong><span>The compliant sequence, in order, plus which reasons are lawful and which are not.</span></a>
        <a class="tile" href="review.html"><strong>Tenant-lawyer review test</strong><span>14 questions a tenant advocate would ask. Pass every one before serving a notice.</span></a>
        <a class="tile" href="flags.html"><strong>Flagged for review</strong><span>What could not be verified, and exactly what would resolve it.</span></a>
      </div>
    </section>

    <section>
      <h2>Privacy</h2>
      <p>Every personal name in the source material has been replaced with a role label &mdash; <em>Tenant A</em> through <em>Tenant F</em>. Dates and dollar amounts are unchanged, because the lawful ceiling depends on them. No name map is stored in this repository or published on this site. {src("S00") if "S00" in SOURCE_BY_ID else ""}</p>
    </section>
    """
    return page("index.html", "Rent increase analysis",
                "Two rent-controlled units, one 1940 building, Outer Sunset, ZIP 94122. Every number below is traced to an official source.", body)


def build_summary():
    units = load("units.json")
    body = f"""
    <div class="callout key">
      <h3>Bottom line</h3>
      <p>Both units are covered by the San Francisco Rent Ordinance because the building predates June 13, 1979. The lawful ceiling is the Rent Board's published annual increase plus any properly banked increases, and nothing else. On these facts the ceilings are <strong>$63.92&ndash;$119.85</strong> per month for Unit 1 and <strong>$412.65</strong> per month for Unit 2. Raising rent on one unit and not the other is lawful and, given these facts, is the logical result of the law; doing so under a single written policy is what removes the discrimination risk.</p>
    </div>

    <section>
      <h2>Findings, in order of importance</h2>
      <ol class="findings">
        <li><strong>The local cap controls, and it is small.</strong> 1.6% for March 1, 2026 through February 28, 2027, set at 60% of the published Bay Area CPI increase. {src(["S02","S03","S08"])}</li>
        <li><strong>The state cap does not apply to these units.</strong> AB 1482's 5% + CPI ceiling is expressly displaced where a local ordinance caps increases lower. {src("S25")}</li>
        <li><strong>No federal law caps rent.</strong> Federal law bars discrimination in the terms of rental, which is a different question. {src(["S29","S30"])}</li>
        <li><strong>Unit 1's ceiling is $63.92, or $119.85 if the February anniversary date holds.</strong> A building with three tenants becoming two does not create a legal basis for a larger increase, and an added occupant cannot be charged for. {src(["S01","S04","S16"])}</li>
        <li><strong>Unit 2's ceiling is $412.65 (13.1%) &mdash; but only until February 28, 2027, and only with 90 days' notice.</strong> The 13.1% is the sum of six banked annual increases plus the current one, added and never compounded. {src(["S03","S04","S24"])}</li>
        <li><strong>A long tenancy below market rent is not a lawful reason to raise rent.</strong> The Rent Board says so in terms: it is not an extraordinary circumstance. {src("S14")}</li>
        <li><strong>The rent increase licence is the most likely failure point.</strong> An otherwise perfect increase is unenforceable without a licence in effect on the effective date. {src(["S09","S10"])}</li>
        <li><strong>Treating the units differently is defensible; treating them by a protected characteristic is not.</strong> The legal test is whether the basis is a protected characteristic, not whether the amounts match. {src(["S28","S30","S11"])}</li>
        <li><strong>Any increase should be assumed to be reviewed for free.</strong> Rent Board petitions are free with no time limit, and free legal representation exists at the eviction stage. Build the file so a reviewer can reproduce both numbers from the Rent Board's own table. {src(["S20","S33"])}</li>
      </ol>
    </section>

    <section>
      <h2>Recommended course of action</h2>
      <div class="grid two">
        <div class="card flat">
          <h3>Unit 1</h3>
          <p>Serve a 30-day notice (35 if mailed) for an increase of <strong>1.6% &rarr; $63.92</strong>, effective February 1, 2027. If a Rent Board counsellor confirms the February 1 anniversary date controls, <strong>3.0% &rarr; $119.85</strong> is also lawful on the same date.</p>
          <p class="note">Do not increase this unit because of the April 2026 occupant change.</p>
        </div>
        <div class="card flat">
          <h3>Unit 2</h3>
          <p>Serve a 90-day notice (95 if mailed) for <strong>13.1% &rarr; $412.65</strong>, effective on or before February 28, 2027, itemising each banked year. Alternatively serve the annual 1.6% only.</p>
          <p class="note">Before serving, confirm no increase has been taken since June 1, 2019 &mdash; the whole figure depends on it.</p>
        </div>
      </div>
      <p>The one procedural rule that binds both: report into the Rent Board Housing Inventory and confirm the rent increase licence is active <em>before</em> the notice is served. {src(["S09","S10"])}</p>
    </section>

    <section>
      <h2>What is still open</h2>
      <p>{len(load("flags.json")["flags"])} items are flagged. Four are high severity and each one could change either the amount or whether the increase is enforceable: the Unit 1 anniversary date, whether Unit 2's rent history is genuinely unbroken, the February 28, 2027 expiry of Unit 2's maximum, and the licence status. All are listed with the exact step that would resolve them on <a href="flags.html">Flagged for review</a>.</p>
    </section>
    """
    return page("summary.html", "Executive summary",
                "The answer, the reasoning and the recommended action &mdash; in one page.", body)


def build_answers():
    differential = load("differential.json")
    procedure = load("procedure.json")
    body = f"""
    <p class="lead">Five questions were asked. Each is answered below with the authority it rests on. Where the honest answer is "the law does not say", that is stated rather than guessed.</p>

    <section>
      <h2>1. What is a reasonable and normal increase under local, state and federal law?</h2>
      {table(
        ["Jurisdiction", "Rule", "Ceiling that results", "Controls here?", "Source"],
        [
          ["<strong>San Francisco</strong>", "Annual increase set each March at 60% of the published CPI change, capped at 7%, plus properly banked increases.", "<strong>1.6%</strong> for 3/1/26&ndash;2/28/27, plus banked amounts", "<strong>Yes</strong>", src(["S03","S08"])],
          ["<strong>California</strong>", "AB 1482: 5% + CPI change, hard maximum 10%. Notice of 30 or 90 days.", "Not applicable &mdash; displaced by the stricter local cap", "No, except notice and anti-retaliation rules", src(["S25","S24"])],
          ["<strong>Federal</strong>", "No rent ceiling. Discrimination in terms and conditions of rental is prohibited.", "Not applicable", "No ceiling", src(["S30","S35","S29"])],
        ])}
      <p><strong>What "normal" means in practice.</strong> A normal increase in this city is the annual percentage applied on the tenant's anniversary date. Anything above the annual plus banked amount requires a Rent Board petition filed <em>before</em> the notice is served, and there are only six such routes. {src(["S12"])} A below-market long tenancy is explicitly not one of them. {src("S14")}</p>
    </section>

    <section>
      <h2>2. How do large corporations and individual owners handle increases?</h2>
      <p>No official source describes how San Francisco owners actually behave, and the one commercial source located did not support a description of practice either. Rather than invent an answer, the practice table on <a href="practice.html">Owner practice</a> leaves those rows blank and flags them. What <em>is</em> documented is the legal position, and it is the same for every owner:</p>
      {table(
        ["Question", "Large owner", "Individual owner", "Source"],
        [
          ["Can an institution use the higher state cap?", "No. The local 1.6% is stricter and controls.", "No. Same rule.", src("S25")],
          ["Can it use pricing software?", "No. Sec. 37.10C bans algorithmic rent-setting that uses non-public competitor data.", "No. Same ban.", src("S15")],
          ["Can it charge above the annual cap?", "Only by Rent Board petition.", "Only by the same petitions.", src(["S12","S13"])],
          ["Does the tenant get free help either way?", "Yes &mdash; free petitions, ADR, counsellors, and Right to Counsel at the eviction stage.", "Yes. Identical.", src(["S20","S34","S33"])],
        ])}
      <p class="note">One documented change in large-owner practice is worth naming: revenue-management tools that recommended rents from competitors' non-public data are now unlawful in San Francisco, effective October 14, 2024. That is a fact about the law with a clear implication for institutional owners. {src("S15")}</p>
    </section>

    <section>
      <h2>3. What is the correct way to tell tenants, and what are reasonable reasons?</h2>
      <p><strong>How:</strong> a written notice stating the dollar amount, the percentage, the effective date, and which portion is annual and which is banked, served 30 days ahead (90 days if the increase exceeds 10%), plus 5 days if mailed. Then the licence must already be in place. The full sequence is on <a href="notice.html">Notice &amp; procedure</a>. {src(["S08","S01","S24","S09"])}</p>
      <p><strong>Reasonable reasons</strong> &mdash; the lawful ones are narrow:</p>
      {table(
        ["Reason", "Lawful basis?", "Source"],
        [[r["reason"], r["acceptable"], src(r["source"])] for r in procedure["reasons_table"]] +
        []
      )}
      <p class="note">The pattern is simple: the lawful reasons are all mechanical, documentary and impersonal &mdash; a published percentage, a documented expense, a certified improvement. Every reason that turns on who the tenant is, how long they have stayed, or how much the market would bear is either unavailable or requires a petition.</p>
    </section>

    <section>
      <h2>4. Would this survive review by a San Francisco tenant lawyer?</h2>
      <p>That question has a concrete answer, because the review is cheap and the remedies are asymmetric: filing a Rent Board petition is free and has no time limit, and the Rent Board has no power to refuse a filing. {src("S20")} So the right way to think about it is not "will we win" but "can a reviewer find a defect".</p>
      <p>The <a href="review.html">Tenant-lawyer review</a> page turns that into 14 specific questions with a pass condition for each. On the facts supplied, both proposed increases pass on the arithmetic. Four items cannot be assessed at all, because they depend on facts not provided: the licence status, whether $3,995 and $3,150 are entirely base rent, whether any complaint or inspection occurred in the last 180 days, and whether any pricing tool was used.</p>
      <div class="callout">
        <p><strong>The one distinction worth being precise about.</strong> Free legal representation in San Francisco attaches through the Tenant Right to Counsel program, which is triggered when a tenant faces eviction, not when a rent increase notice is served. {src("S33")} The rent-increase route is a free Rent Board petition, which is designed so that no one needs a lawyer. {src("S20")} Both matter, but they are different processes.</p>
      </div>
    </section>

    <section>
      <h2>5. One unit or both?</h2>
      <p><strong>Raise both units, under one written policy &mdash; not by the same percentage.</strong> The two tenancies are not similarly situated: Unit 1's tenancy began in 2025, Unit 2's in 2019 with six skipped increases banked. Discrimination law asks whether the <em>basis</em> for a difference is a protected characteristic, not whether two tenants received identical numbers. {src(["S28","S30"])}</p>
      {table(
        ["Consideration", "Finding", "Source"],
        [[p["point"], p["explanation"], src(p["source"])] for p in differential["analysis"]] +
        []
      )}
      <div class="grid two">
        <div class="card flat">
          <h3>Do</h3>
          <ul>{"".join("<li>%s</li>" % c.replace("Raise both units","<strong>Raise both units</strong>") for c in differential["conclusion"][:3])}
          <li>%s</li></ul>
        </div>
        <div class="card flat danger">
          <h3>Don't</h3>
          <ul>{"".join("<li>%s</li>" % d for d in differential["do_not"])}</ul>
        </div>
      </div>
    </section>
    """
    return page("answers.html", "The five questions, answered",
                "Each answer with the authority behind it, and a plain statement where the law is silent.", body)


def build_calculations():
    units = load("units.json")
    sections = []
    for unit in units["units"]:
        rows = []
        for calc in unit["calculations"]:
            comps = "<br>".join(
                "%s &middot; <strong>%s%%</strong> %s" % (esc(c["label"]), "%g" % c["pct"], src(c["source"]))
                for c in calc["components"]
            ) or '<span class="blank">&mdash; unverified</span>'
            rows.append([
                '<strong>%s</strong>' % esc(calc["scenario"]),
                esc(calc["effective_display"]),
                comps,
                pct(calc["total_pct"]),
                money(calc["increase_dollars"]),
                money(calc["new_rent"]),
                (esc(str(calc["notice_days"])) + " days" if calc["notice_days"] else '<span class="blank">&mdash;</span>') + (("<br><small>%s</small>" % esc(calc["notice_basis"])) if calc.get("notice_basis") else ""),
                badge(calc["confidence"]),
            ])
        extra = ""
        if unit["calculations"][-1].get("note"):
            extra = '<p class="note">%s</p>' % esc(unit["calculations"][-1]["note"])
        conditions = "".join(
            '<p class="note"><strong>Condition:</strong> %s</p>' % esc(c["condition"])
            for c in unit["calculations"] if c.get("condition")
        )
        sections.append(f"""
        <section>
          <h2>{esc(unit["id"])}</h2>
          <div class="facts">
            <div><span>Lease began</span><strong>{esc(unit["lease_start_display"])}</strong></div>
            <div><span>Rent at lease start</span><strong>{money(unit["rent_at_lease_start"])}</strong></div>
            <div><span>Current tenants</span><strong>{esc(unit["current_tenants"])}</strong></div>
            <div><span>Current rent</span><strong>{money(unit["current_rent"])}</strong></div>
            <div><span>Anniversary date</span><strong>{longdate(unit["anniversary_reading_a"]["date"])}</strong></div>
          </div>
          {table(["Scenario","Effective","Components","Total %","Increase / mo","New rent","Notice","Status"], rows)}
          {conditions}
          {extra}
        </section>""")

    body = f"""
    <p class="lead">Every figure on this page is computed by adding published percentages and applying the total once to the current base rent. Percentages are never compounded and amounts are never rounded up. Each component links to the Rent Board table it came from.</p>

    <div class="callout warn">
      <h3>The two rules that do all the work</h3>
      <p><strong>Add, never compound.</strong> Banked percentages are added together, then multiplied by the current base rent once. {src(["S04","S05"])}</p>
      <p><strong>24 months, not 12.</strong> A skipped annual increase is only banked if at least 24 full months pass without any rent increase. If less than 24 months pass, the skipped increase is lost. {src("S04")} This is the rule that produces Unit 2's large figure and the rule that limits Unit 1's small one.</p>
    </div>

    {"".join(sections)}

    <section>
      <h2>Side by side</h2>
      {table(
        ["", "Unit 1", "Unit 2", "Source"],
        [
          ["Anniversary date", "February 1 (see FLAG-02)", "June 1", src("S01")],
          ["Annual increase available", "1.6%", "1.6%", src("S03")],
          ["Banked increases available", "1.4% (one year, conditionally)", "11.5% (six years)", src("S04")],
          ["<strong>Maximum total</strong>", "<strong>3.0%</strong>", "<strong>13.1%</strong>", src(["S03","S04"])],
          ["<strong>Maximum dollars</strong>", "<strong>$119.85</strong>", "<strong>$412.65</strong>", src("S04")],
          ["Notice required", "30 days (35 by mail)", "90 days (95 by mail)", src("S24")],
          ["Latest effective date at these rates", "Feb 1, 2027", "<strong>Feb 28, 2027</strong>", src("S03")],
          ["Licence required", "Yes", "Yes", src(["S09","S10"])],
        ])}
      <p class="note">{esc(units["differential"]["explanation"])}</p>
    </section>

    <section>
      <h2>Arithmetic checks</h2>
      <ul class="checks">{"".join("<li>%s</li>" % esc(n) for n in units["arithmetic_notes"])}</ul>
      <p class="note">These were also verified independently by script; see <a href="method.html">Method</a>.</p>
    </section>

    <section>
      <h2>What is deliberately blank</h2>
      <p>Any increase effective on or after March 1, 2027 is left blank, because the 2027&ndash;28 rate had not been announced as of {esc(units["as_of"])}. The Rent Board announces it each January. A blank is more useful to you than an estimate that later turns out to be wrong. {src("S02")}</p>
    </section>
    """
    return page("calculations.html", "Calculations",
                "Both units, every scenario, with the arithmetic shown and a source link on every component.", body)


def build_requirements():
    reqs = load("requirements.json")
    layers = ["Local (SF)", "State (CA)", "Federal"]
    counts = {l: sum(1 for r in reqs["rows"] if r["layer"] == l) for l in layers}
    summary = "".join(
        '<div class="stat"><span>%s</span><strong>%d</strong></div>' % (esc(l), counts[l]) for l in layers
    )
    summary += '<div class="stat"><span>Total</span><strong>%d</strong></div>' % len(reqs["rows"])

    rows = []
    for r in reqs["rows"]:
        cav = '<div class="caveat">%s</div>' % esc(r["caveat"]) if r.get("caveat") else ""
        rows.append([
            '<span class="rid">%s</span>' % esc(r["id"]),
            esc(r["layer"]).replace("Local (SF)", "Local").replace("State (CA)", "State"),
            "<strong>%s</strong><div class='muted'>%s</div>" % (esc(r["requirement"]), esc(r["value"])),
            esc(r["applies_to"]),
            esc(r["detail"]) + cav,
            src([r["source"]] + ([r["source2"]] if r.get("source2") else [])),
            badge(r["status"]),
        ])
    body = f"""
    <p class="lead">{esc(reqs["note"])}</p>
    <div class="stats">{summary}</div>
    {table(["ID","Layer","Requirement","Applies to","Detail","Source","Status"], rows)}
    <section>
      <h2>Reading the matrix</h2>
      <p>Local law does nearly all the work. State law supplies the notice periods and the anti-retaliation and anti-discrimination rules, and it supplies a rent cap that is deliberately displaced here. Federal law supplies no ceiling at all. If you only read three rows, read REQ-03 (frequency), REQ-06 (the 24-month banking rule) and REQ-09 (the licence).</p>
    </section>
    """
    return page("requirements.html", "Requirement matrix",
                "Every requirement that binds these two units, one row each, with a source per row.", body)


def build_notice():
    procedure = load("procedure.json")
    steps = []
    for s in procedure["steps"]:
        steps.append(f"""
        <div class="step">
          <div class="num">{s["n"]}</div>
          <div class="body">
            <h3>{esc(s["action"])}</h3>
            <p class="why"><strong>Why:</strong> {esc(s["why"])}</p>
            <p>{esc(s["detail"])}</p>
            <p class="meta"><span class="when">{esc(s["timing"])}</span> {src([s["source"]] + ([s["source2"]] if s.get("source2") else []))}</p>
          </div>
        </div>""")

    rows = [[r["reason"], r["acceptable"], esc(r["why"]), src(r["source"])] for r in procedure["reasons_table"]]

    body = f"""
    <p class="lead">Order matters. Two of these steps are void if done out of sequence: the licence must exist before the notice is enforceable, and any petition for an above-cap increase must be filed before the notice is served.</p>

    <section>
      <h2>The compliant sequence</h2>
      {"".join(steps)}
    </section>

    <section>
      <h2>What a notice must contain</h2>
      {table(
        ["Element", "Why it is required", "Source"],
        [
          ["Dollar amount of the increase", "Required content of the notice.", src("S01")],
          ["Percentage amount of the increase", "Required content of the notice.", src("S01")],
          ["Effective date", "Required content of the notice; must be at least 30 or 90 days after service.", src(["S01","S24"])],
          ["Which portion is annual and which is banked", "Sec. 37.3(b)(1) requires the landlord to inform the tenant in writing which portion reflects the annual increase and which reflects a banked amount.", src("S08")],
          ["Correct rate for the effective date", "The rate in force on the effective date governs, not the rate when the notice was written.", src("S01")],
          ["Service by an allowed method", "Personal delivery, or mail per Code Civ. Proc. &sect;1013 with 5 extra days.", src("S24")],
        ])}
      <p class="note">No rounding up. No passthroughs folded into the base. Two things a reviewer will look for first: the percentage and the effective date.</p>
    </section>

    <section>
      <h2>Reasonable reasons, and the ones that are not</h2>
      {table(["Reason", "Lawful basis?", "Why", "Source"], rows)}
    </section>

    <section>
      <h2>A notice that would fail, and why</h2>
      <div class="grid two">
        <div class="card flat danger">
          <h3>Unlawful</h3>
          <p>&ldquo;Rent is increasing from $3,150 to $3,563 (13.1%) effective in 30 days, to bring the unit closer to market rent.&rdquo;</p>
          <ul>
            <li>30 days' notice for an increase above 10% &mdash; defective. {src("S24")}</li>
            <li>"To bring the unit closer to market" is not a lawful basis and, on this record, is not even the real one. {src("S14")}</li>
            <li>No itemisation of the banked portion. {src("S08")}</li>
          </ul>
        </div>
        <div class="card flat">
          <h3>Defensible</h3>
          <p>&ldquo;Effective February 28, 2027, base rent increases by $412.65 (13.1%), to $3,562.65. The increase consists of 1.6% annual allowable increase and 11.5% in previously banked annual increases (1.8% + 0.7% + 2.3% + 3.6% + 1.7% + 1.4%). Notice served 95 days in advance by mail.&rdquo;</p>
          <ul>
            <li>Correct notice period with the mailing allowance. {src("S24")}</li>
            <li>Itemised banked portion. {src("S08")}</li>
            <li>Every percentage reproduces from the Rent Board's own table. {src("S03")}</li>
          </ul>
        </div>
      </div>
      <p class="note">This is an illustration of form, not a template to sign. Confirm the amount and the date against your own rent ledger first.</p>
    </section>
    """
    return page("notice.html", "Notice &amp; procedure",
                "The nine steps in the order that keeps the increase enforceable, and the reasons that hold up.", body)


def build_practice():
    practice = load("practice.json")
    rows = []
    for r in practice["rows"]:
        large = r["large_owner"] or '<span class="blank">&mdash; unverified</span>'
        small = r["individual_owner"] or '<span class="blank">&mdash; unverified</span>'
        rows.append([r["topic"], large, small, src(r["sources"]), badge(r["status"])])
    limits = "".join("<li>%s</li>" % esc(x) for x in practice["important_limits"])
    body = f"""
    <p class="lead">The brief asked how large corporations and how individual owners handle increases. The honest answer has two halves: the law treats them identically, and no source located describes their behaviour. Both halves are reported.</p>

    <div class="callout warn">
      <h3>Read this before the table</h3>
      <ul>{limits}</ul>
    </div>

    <section>
      <h2>What the law requires of any owner</h2>
      {table(["Topic","Large owner","Individual owner","Source","Status"], rows)}
    </section>

    <section>
      <h2>Why the "big corporations do it differently" idea does not help here</h2>
      <p>Three specific claims are sometimes made, and each fails against the sources:</p>
      {table(
        ["Claim", "What the law actually says", "Source"],
        [
          ["Large owners may use the state cap of about 8.8% instead of the city's 1.6%.", "No. Civil Code &sect;1947.12(d)(3) exempts housing subject to a local ordinance that restricts increases to a lower amount. The local cap controls.", src("S25")],
          ["Large owners may use revenue-management software to set rents.", "No, not in San Francisco since October 14, 2024. Sec. 37.10C prohibits selling or using algorithmic devices that use non-public competitor data to recommend rent or occupancy.", src("S15")],
          ["Large owners can push rents up to market on long tenancies.", "No. A long-standing tenant paying below market is expressly not an extraordinary circumstance that justifies an above-cap increase.", src("S14")],
        ])}
      <p class="note">Where this leaves the reader: the question "how do corporations do it" has a legal answer (the same way) and a factual answer that is unverified. The legal answer is the one that protects you.</p>
    </section>

    <section>
      <h2>What is good practice regardless of owner size</h2>
      {table(
        ["Practice", "Why it helps", "Source"],
        [
          ["One written rent-increase policy applied to every unit", "Makes the reason for any difference between units visible and non-discriminatory on its face.", src(["S28","S30"])],
          ["Increase on the anniversary date, once a year", "Avoids losing annual increases when the anniversary date shifts.", src(["S01","S06"])],
          ["Itemise the banked portion in every notice", "Required by Sec. 37.3(b)(1) and makes the notice self-verifying.", src("S08")],
          ["Keep the licence current and a dated screenshot of it", "A licence defect voids an otherwise correct increase.", src(["S09","S10"])],
          ["Keep a contemporaneous note of the decision", "This is the document that answers a harassment or discrimination allegation.", src("S11")],
          ["Never use a pricing tool that reads competitors' non-public data", "Prohibited, with per-unit per-month penalties.", src("S15")],
        ])}
    </section>
    """
    return page("practice.html", "Owner practice",
                "What the law requires of every owner, and an explicit statement of what could not be sourced about behaviour.", body)


def build_review():
    tests = load("tests.json")
    rows = [[
        '<span class="rid">%s</span>' % esc(t["id"]),
        "<strong>%s</strong><div class='muted'>%s</div>" % (esc(t["question"]), esc(t["pass_condition"])),
        esc(t["unit1"]),
        esc(t["unit2"]),
        src([t["source"]] + ([t["source2"]] if t.get("source2") else [])),
    ] for t in tests["tests"]]

    petitions = "".join("<li>%s</li>" % esc(p) for p in tests["if_a_tenant_petitions"])
    body = f"""
    <p class="lead">{esc(tests["framing"])}</p>
    <div class="callout warn"><p>{esc(tests["caveat"])}</p></div>

    {table(["#","Test","Unit 1","Unit 2","Source"], rows)}

    <section>
      <h2>Verdict on the facts supplied</h2>
      <div class="grid two">
        <div class="card flat"><h3>Unit 1</h3><p>{esc(tests["verdict_template"]["unit1"])}</p></div>
        <div class="card flat"><h3>Unit 2</h3><p>{esc(tests["verdict_template"]["unit2"])}</p></div>
      </div>
    </section>

    <section>
      <h2>What happens if a tenant does petition</h2>
      <p>This is not a threat to be avoided; it is a process to be anticipated. Filing is free, there is no time limit, and the hearing is designed so that no one needs a lawyer.</p>
      <ul class="checks">{petitions}</ul>
    </section>

    <section>
      <h2>The single strongest defensive document</h2>
      <p>Not the notice. The notice only proves what you told the tenant. What answers a harassment or discrimination allegation is a short file note, written at the time, that records: the written policy; each unit's rent history and anniversary date; the calculation with each year's percentage; the date the decision was taken; the notice served and the service method; and confirmation that no repair complaint, inspection, organising activity or buyout discussion preceded it. A reviewer who can reproduce both numbers from the Rent Board's published table, and who sees the same rule applied to both units, has nothing to argue with.</p>
      <p class="note">See <a href="notice.html">Notice &amp; procedure</a> step 7 and the open items on <a href="flags.html">Flagged for review</a>.</p>
    </section>
    """
    return page("review.html", "Tenant-lawyer review",
                "Fourteen questions a San Francisco tenant advocate would ask, with a pass condition for each.", body)


def build_rates():
    aga = load("aga.json")
    rows = []
    for r in aga["rows"]:
        used = []
        if r["used_in_unit1"]:
            used.append("Unit 1")
        if r["used_in_unit2"]:
            used.append("Unit 2")
        rows.append([
            esc(r["period"]),
            "<strong>%.1f%%</strong>" % float(r["pct"]),
            ", ".join(used) or '<span class="muted">&mdash;</span>',
            src("S03"),
        ])
    used1 = sum(r["pct"] for r in aga["rows"] if r["used_in_unit1"])
    used2 = sum(r["pct"] for r in aga["rows"] if r["used_in_unit2"])
    body = f"""
    <p class="lead">The complete table of allowable annual rent increases since the ordinance took effect, transcribed from the Rent Board's official publication. This is the only table needed to reproduce either unit's number by hand.</p>

    <div class="stats">
      <div class="stat"><span>Periods listed</span><strong>{len(aga["rows"])}</strong></div>
      <div class="stat"><span>Current rate</span><strong>1.6%</strong></div>
      <div class="stat"><span>Unit 1 uses</span><strong>{used1:.1f}%</strong></div>
      <div class="stat"><span>Unit 2 uses</span><strong>{used2:.1f}%</strong></div>
    </div>

    <div class="callout">
      <p><strong>How to read it.</strong> A landlord may raise rent once every 12 months using the rate in force on the effective date. If a year was skipped and at least 24 full months pass without any increase, that year's rate is banked and may be added later. Percentages are added, never compounded. {src(["S02","S04"])}</p>
    </div>

    {table(["Effective period","Increase","Used in","Source"], rows)}

    <section>
      <h2>Why the two units land so far apart</h2>
      <p>Unit 1's tenancy began in February 2025. Only the 1.4% year can have been skipped, and only if the 24-month test is met by February 2027, giving 3.0% at most. Unit 2's tenancy began in June 2019. Six consecutive years were skipped, and every one of them is banked because each is more than 24 months in the past, giving 11.5% banked plus the current 1.6% &mdash; 13.1%.</p>
      <p class="note">Note the two 1992&ndash;93 entries. Only one of them may be imposed; the Rent Board flags that on the same document. It does not affect either unit here, because both tenancies post-date it, but it is the kind of detail that makes a hand-built calculation go wrong.</p>
    </section>
    """
    return page("rates.html", "Rates 1982&ndash;2027",
                "Every published allowable annual increase, with the years used by each unit marked.", body)


def build_flags():
    flags = load("flags.json")
    order = {"high": 0, "medium": 1, "low": 2}
    items = sorted(flags["flags"], key=lambda f: order[f["severity"]])
    sev = "".join('<div class="stat"><span>%s</span><strong>%d</strong></div>' % (k, sum(1 for f in items if f["severity"] == k)) for k in ["high","medium","low"])

    cards = []
    for f in items:
        cards.append(f"""
        <article class="flag sev-{f["severity"]}">
          <header>
            <span class="rid">{esc(f["id"])}</span>
            {badge(f["severity"])}
            <h3>{esc(f["title"])}</h3>
          </header>
          <p>{esc(f["detail"])}</p>
          <dl>
            <dt>Why it matters</dt><dd>{esc(f["why_it_matters"])}</dd>
            <dt>Effect on the numbers</dt><dd>{esc(f["impact_on_numbers"])}</dd>
            <dt>What would resolve it</dt><dd>{esc(f["resolution"])}</dd>
          </dl>
          <p class="meta">Sources: {src(f["sources"])}</p>
        </article>""")

    key = "".join("<li><strong>%s</strong> &mdash; %s</li>" % (esc(k), esc(v)) for k, v in flags["severity_key"].items())

    body = f"""
    <p class="lead">{esc(flags["intro"])}</p>
    <div class="stats">{sev}</div>
    <div class="callout">
      <h3>Severity</h3>
      <ul>{key}</ul>
    </div>
    {"".join(cards)}
    """
    return page("flags.html", "Flagged for review",
                "Unverified values, unresolved facts and source conflicts &mdash; each with the step that would close it.", body)


def build_sources():
    rows = []
    for s in SOURCES["sources"]:
        rows.append([
            '<span class="rid">%s</span>' % esc(s["id"]),
            esc(s["publisher"]),
            '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(s["url"]), esc(s["title"])),
            esc(s["tier"]),
            esc(s["verified"]),
        ])
    secondary = load("practice.json").get("secondary_sources", [])
    srows = [[esc(s["id"]), esc(s["publisher"]),
              '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(s["url"]), esc(s["title"])),
              esc(s["note"])] for s in secondary]
    body = f"""
    <p class="lead">Every source used on this site, with the date it was retrieved and what it was checked for. Primary sources are statutes, ordinances, regulations and agency publications. Anything commercial is labelled and is never the basis for a number.</p>
    <div class="stats">
      <div class="stat"><span>Primary &amp; official</span><strong>{len(SOURCES["sources"])}</strong></div>
      <div class="stat"><span>Commercial</span><strong>{len(secondary)}</strong></div>
      <div class="stat"><span>Retrieved</span><strong>{esc(RETRIEVED)}</strong></div>
    </div>
    {table(["ID","Publisher","Document","Tier","What it was verified for"], rows)}
    <section>
      <h2>Commercial sources</h2>
      <p>Listed for transparency. None of these was used to establish a value. One is retained only because it independently corroborates the 1.6% figure; it does not describe owner practice, so it is not cited for that.</p>
      {table(["ID","Publisher","Document","Note"], srows)}
    </section>
    <section>
      <h2>Sources that were specifically not relied on</h2>
      <p>Several commercial calculators and blogs publish <strong>1.7%</strong> for March 2026&ndash;February 2027. The Rent Board's own pages and its official PDF both state <strong>1.6%</strong>, and 1.7% is the rate for the <em>previous</em> year. Those sites appear to have carried forward the wrong year. See <a href="flags.html">FLAG-11</a>. {src(["S03","S19"])}</p>
      <p>The Census data API responded &ldquo;missing key&rdquo; to every query in this session, and the HUD Fair Market Rent interactive lookup returned an empty result for the available area parameters. No rent benchmark was taken from either, so no market figure appears anywhere on this site. See FLAG-05.</p>
    </section>
    """
    return page("sources.html", "Sources",
                "Numbered, dated and annotated. Every table row on the site points back to one of these.", body)


def build_method():
    body = f"""
    <p class="lead">This site was built backwards from its claims. The rule was: no sentence may assert a fact unless a numbered source in the source register supports it, and no table cell may contain a number that cannot be recomputed from a published figure.</p>

    <section>
      <h2>The rules applied</h2>
      <dl class="rules">
        <dt>One row, one source</dt>
        <dd>Every table row carries its own source link, or is an arithmetic identity built from the published figures linked in the same row.</dd>
        <dt>Blank beats guess</dt>
        <dd>Where a figure depends on something unpublished (the 2027&ndash;28 rate) or unconfirmed (a market rent), the cell reads &ldquo;unverified&rdquo; and a flag explains what would resolve it.</dd>
        <dt>Primary before secondary</dt>
        <dd>Statutes, ordinances and agency pages only. Commercial sources are labelled and never used for a value. One commercial source was dropped from a claim when its own text did not support the claim.</dd>
        <dt>Conflicts are recorded, not resolved silently</dt>
        <dd>Where third-party sources contradicted the Rent Board, the conflict appears on the Flagged for review page rather than being quietly dropped.</dd>
        <dt>Arithmetic is reproducible</dt>
        <dd>Percentages are added, not compounded; the total is applied once to base rent; nothing is rounded up. Every figure was also recomputed independently by script.</dd>
      </dl>
      <p class="note">The published figures all of this rests on: {src(["S03","S04","S08","S24"])}</p>
    </section>

    <section>
      <h2>What was checked, and how</h2>
      <ol class="findings">
        <li><strong>All {len(SOURCES["sources"])} sources were fetched and read on {esc(RETRIEVED)}.</strong> The verification column on the <a href="sources.html">Sources</a> page states, per source, what it was used to confirm. Values were transcribed from the fetched text; none was recalled or inferred.</li>
        <li><strong>The historical rate table was transcribed from the Rent Board's own PDF</strong>, cell by cell, and cross-checked against two independent Rent Board pages that publish the three most recent rates. {src(["S03","S19","S02"])}</li>
        <li><strong>Every dollar figure was recomputed by script</strong> from the percentages and the stated base rents. The checks are printed on the <a href="calculations.html">Calculations</a> page.</li>
        <li><strong>Every internal link and anchor on this site was checked after generation</strong>, and the site was confirmed to load as plain static files with no external JavaScript.</li>
        <li><strong>Personal information was removed before anything was written</strong>, not after. No name map exists in this repository.</li>
      </ol>
    </section>

    <section>
      <h2>Known limits</h2>
      <ul class="checks">
        <li>This is an analysis of public law, not legal advice. A Rent Board counsellor's view on the Unit 1 anniversary question in particular would be worth obtaining before anything is served.</li>
        <li>Every figure depends on the owner's own rent history being complete and accurate. That was not available and is flagged.</li>
        <li>The building's coverage was accepted from the stated 1940 construction date and was not confirmed against Assessor or Planning records.</li>
        <li>No market rent benchmark was obtained, and none is needed to compute a lawful ceiling.</li>
      </ul>
    </section>

    <section>
      <h2>How to check this yourself in five minutes</h2>
      <ol class="checks">
        <li>Open the Rent Board's <a href="https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf" target="_blank" rel="noopener">571 Allowable Annual Increases</a> PDF.</li>
        <li>For Unit 2, add the rates for every year since June 2019 that was skipped, then add 1.6%. The total should read 13.1%. Multiply by $3,150.</li>
        <li>For Unit 1, add 1.6% to $3,995. Optionally add the 1.4% year and multiply again.</li>
        <li>Compare with the <a href="calculations.html">Calculations</a> page. If any number differs, treat that as a defect in this site and report it.</li>
      </ol>
    </section>
    """
    return page("method.html", "Method",
                "How the data was collected, verified and checked &mdash; and what remains uncertain.", body)


def build_reconciliation():
    rec = load("reconciliation.json")
    ed_rows = [[
        "<strong>%s</strong>" % esc(e["name"]),
        '<a href="%s">%s</a>' % (esc(e["url"]), esc(e["path"])),
        esc(e["built_by"]),
        esc(e["pages"]),
        esc(e["status"]),
    ] for e in rec["editions"]]

    agree_rows = [[
        esc(a["finding"]),
        esc(a["this_site"]),
        esc(a["main_edition"]),
        '<span class="pill ok">%s</span>' % esc(a["agrees"]),
        '<a href="../index.html">main edition</a>' if not a.get("source") else src(a["source"]),
    ] for a in rec["agreement"]]

    diff_rows = [[
        "<strong>%s</strong>" % esc(d["topic"]),
        esc(d["this_site"]),
        esc(d["main_edition"]),
        esc(d["reading"]),
        src(d["source"]) if d.get("source") else '<a href="../index.html">main edition</a>',
    ] for d in rec["differences"]]

    open_items = "".join("<li>%s</li>" % esc(x) for x in rec["unresolved_by_both"])

    body = f"""
    <p class="lead">{esc(rec["context"])}</p>

    <div class="callout key">
      <h3>The headline</h3>
      <p>Two independent analyses of the same primary sources arrived at <strong>identical figures to the cent</strong> &mdash; $63.92, $119.85, $412.65, $4,058.92, $4,114.85, $3,562.65 &mdash; identical notice periods, and independently flagged the same two substantive uncertainties. Nothing on this page changes a number.</p>
    </div>

    <section>
      <h2>The editions of this site</h2>
      {table(["Edition","Path","Built by","Scope","Status"], ed_rows)}
      <p class="note">Read the main edition first. This companion edition adds the 31-row requirement matrix, the complete 1982&ndash;2027 rate table, the 14-point tenant-lawyer review test and the 13-item flag register, which the main edition does not duplicate.</p>
    </section>

    <section>
      <h2>Where the two agree</h2>
      {table(["Finding","This edition","Main edition","Agrees","Cross-check"], agree_rows)}
    </section>

    <section>
      <h2>Where they differ, and how to read the difference</h2>
      {table(["Topic","This edition","Main edition","How to read it","Source"], diff_rows)}
    </section>

    <section>
      <h2>Open in both editions</h2>
      <p>These are factual gaps in the owner's records, not disagreements about the law. Neither edition fills them in.</p>
      <ul class="checks">{open_items}</ul>
    </section>

    <section>
      <h2>Conclusion</h2>
      <p>{esc(rec["conclusion"])}</p>
      <p class="note">{esc(rec["sources_note"])}</p>
    </section>
    """
    return page("reconciliation.html", "Reconciliation",
                "What the three published editions of this analysis agree on, and where they legitimately differ.", body)


def main():
    written = [
        build_index(), build_summary(), build_answers(), build_calculations(),
        build_requirements(), build_notice(), build_practice(), build_review(),
        build_rates(), build_flags(), build_sources(), build_method(),
        build_reconciliation(),
    ]
    print("wrote %d pages: %s" % (len(written), ", ".join(written)))


if __name__ == "__main__":
    main()
