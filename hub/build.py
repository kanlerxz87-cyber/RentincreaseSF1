#!/usr/bin/env python3
"""
Generator for the integrated SF rent-increase compliance dashboard.

Reads hub/data.json (verified sources, quotes, rates, unit facts, flags) and
writes:

    index.html                 landing dashboard (repository root, GitHub Pages entry)
    hub/licensing.html         the Rent Board licence / notification answer
    hub/limits.html            rates, local-state-federal layering, the two units
    hub/notice.html            notice contents, deadlines, lawful reasons
    hub/practice.html          corporate vs individual owners
    hub/fair-housing.html      one unit or both
    hub/review.html            tenant-lawyer red-team test
    hub/flags.html             Flagged for Review
    hub/sources.html           source registry with verbatim quotes

Every money figure is computed here from a published percentage and a rent that
came from the owner's records, never typed as a literal. tools/verify_hub.py
recomputes them independently from the HTML and from data.json.

Usage: python3 hub/build.py
"""

from __future__ import annotations

import html
import json
import os
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = os.path.join(ROOT, "hub")
DATA = json.load(open(os.path.join(HUB, "data.json"), encoding="utf-8"))

C = Decimal("0.01")
SRC = {s["id"]: s for s in DATA["sources"]}
TODAY = date.fromisoformat(DATA["meta"]["retrieved"])


# --------------------------------------------------------------------------- helpers
def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def money(value: Decimal) -> str:
    return "${:,.2f}".format(value)


def pct(value) -> str:
    return "{}%".format(Decimal(str(value)).normalize())


def d(s: str) -> date:
    return date.fromisoformat(s)


def longdate(s: str) -> str:
    x = d(s)
    return "{} {} {}".format(x.day, x.strftime("%B"), x.year)


def src_links(ids, page="@@/hub/sources.html") -> str:
    out = []
    for i in ids:
        s = SRC[i]
        out.append(
            '<a href="{}#{}" title="{} — {}">{}</a>'.format(
                page, i, esc(s["publisher"]), esc(s["title"]), i
            )
        )
    return '<span class="src">' + " ".join(out) + "</span>"


def badge(kind: str, text: str) -> str:
    return '<span class="badge b-{}">{}</span>'.format(kind, esc(text))


STATUS_BADGE = {
    "verified": ("ok", "Verified"),
    "pass": ("ok", "Pass"),
    "pass (owner records)": ("ok", "Pass — owner records"),
    "pass (if served on time)": ("ok", "Pass if served on time"),
    "calculated": ("calc", "Calculated"),
    "reading of cited text": ("calc", "Reading of cited text"),
    "recommended": ("calc", "Recommended"),
    "needs-evidence": ("flag", "Needs evidence"),
    "needs evidence": ("flag", "Needs evidence"),
    "flag": ("flag", "Flag"),
    "no official source": ("unv", "Not verified"),
}


def status_badge(value: str) -> str:
    kind, text = STATUS_BADGE.get(value, ("unv", value))
    return badge(kind, text)


def table(headers, rows, caption=None, cls="") -> str:
    out = ['<div class="tablewrap"><table{}>'.format(' class="%s"' % cls if cls else "")]
    if caption:
        out.append("<caption>{}</caption>".format(caption))
    out.append("<thead><tr>")
    for h in headers:
        if isinstance(h, tuple):
            label, klass = h
            out.append('<th scope="col" class="{}">{}</th>'.format(klass, label))
        else:
            out.append('<th scope="col">{}</th>'.format(h))
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        for cell in row:
            if isinstance(cell, tuple):
                value, klass = cell
                out.append('<td class="{}">{}</td>'.format(klass, value))
            else:
                out.append("<td>{}</td>".format(cell))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


# --------------------------------------------------------------------------- arithmetic
def compute() -> dict:
    out = {}
    for key in ("U1", "U2"):
        unit = DATA["units"][key]
        calc = DATA["calculations"][key]
        base = Decimal(unit["base_rent"])
        annual_pct = Decimal(calc["annual_pct"])
        banked_pct = Decimal(calc["banked_total_pct"])
        total_pct = Decimal(calc["total_pct"])
        annual_amt = (base * annual_pct / Decimal(100)).quantize(C, rounding=ROUND_HALF_UP)
        banked_amt = (base * banked_pct / Decimal(100)).quantize(C, rounding=ROUND_HALF_UP)
        total_amt = (base * total_pct / Decimal(100)).quantize(C, rounding=ROUND_HALF_UP)
        assert annual_pct + banked_pct == total_pct, (key, annual_pct, banked_pct, total_pct)
        assert annual_amt + banked_amt == total_amt, (key, annual_amt, banked_amt, total_amt)
        eff = d(calc["annual_effective"])
        notice = int(calc["notice_days"])
        out[key] = {
            "base": base,
            "annual_pct": annual_pct,
            "banked_pct": banked_pct,
            "total_pct": total_pct,
            "annual_amt": annual_amt,
            "banked_amt": banked_amt,
            "total_amt": total_amt,
            "annual_rent": base + annual_amt,
            "total_rent": base + total_amt,
            "effective": eff,
            "notice": notice,
            "serve_by": eff - timedelta(days=notice),
            "mail_by": eff - timedelta(days=notice + 5),
            "short_serve_by": eff - timedelta(days=30),
            "short_mail_by": eff - timedelta(days=35),
        }
    out["earliest_90"] = TODAY + timedelta(days=90)
    out["today"] = TODAY
    return out


N = compute()

# --------------------------------------------------------------------------- nav + shell
NAV = [
    ("@@/index.html", "Dashboard"),
    ("@@/hub/licensing.html", "Licence &amp; Board"),
    ("@@/hub/limits.html", "Limits &amp; amounts"),
    ("@@/hub/notice.html", "Notice &amp; reasons"),
    ("@@/hub/practice.html", "Owner practice"),
    ("@@/hub/fair-housing.html", "One unit or both"),
    ("@@/hub/review.html", "Lawyer test"),
    ("@@/hub/flags.html", "Flagged"),
    ("@@/hub/sources.html", "Sources"),
]


def nav_html(current: str) -> str:
    items = []
    for href, label in NAV:
        here = ' aria-current="page"' if href.split("/")[-1] == current else ""
        items.append('<a href="{}"{}>{}</a>'.format(href, here, label))
    return '<nav class="main" aria-label="Main">' + "".join(items) + "</nav>"


def page(filename: str, title: str, description: str, hero: str, body: str) -> str:
    current = filename.split("/")[-1]
    depth = filename.count("/")
    doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="@@/hub/assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap navwrap">
    <a class="brand" href="@@/index.html"><span class="mark">SF</span><span>Rent Increase Compliance<small>Outer Sunset &middot; 94122</small></span></a>
    {nav}
  </div>
</header>
{hero}
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p><strong>Anonymised.</strong> Tenant names and initials are replaced with placeholders. Dates and dollar amounts are unchanged, as instructed.</p>
    <p><strong>Verified {retrieved}.</strong> Every figure is quoted from an official source fetched on that date or is arithmetic performed on those published figures. Items that could not be confirmed from an official source are left blank and listed on <a href="@@/hub/flags.html">Flagged for Review</a>.</p>
    <p><strong>Not legal advice.</strong> San Francisco Rent Board counseling is free on 415-252-4600; confirm the licence status, the current rate and any notice before serving it.</p>
  </div>
</footer>
</body>
</html>
""".format(title=esc(title), desc=esc(description), nav=nav_html(current), hero=hero,
           body=body, retrieved=DATA["meta"]["retrieved"])
    if depth == 0:
        return doc.replace("@@/", "")
    return doc.replace("@@/hub/", "").replace("@@/", "../")


def hero_block(eyebrow: str, heading: str, lede: str, pills=None) -> str:
    pills = pills or []
    pill_html = ""
    if pills:
        pill_html = '<div class="pillrow">' + "".join(
            '<span class="pill">{}</span>'.format(esc(p)) for p in pills
        ) + "</div>"
    return """<section class="hero"><div class="wrap">
<p class="eyebrow">{eyebrow}</p>
<h1>{heading}</h1>
<p class="lede">{lede}</p>
{pills}
</div></section>""".format(eyebrow=esc(eyebrow), heading=heading, lede=lede, pills=pill_html)


u1, u2 = N["U1"], N["U2"]

# --------------------------------------------------------------------------- index
index_body = """
<section>
  <h2>Start here — the Rent Board question<span class="sub">Your first question, answered before anything else, because it decides whether the rest of the arithmetic can be used at all.</span></h2>

  <div class="answer">
    <h3>Do you, as a single individual owner, need a Rent Board rent-increase licence before you tell the tenants about an increase? Yes.</h3>
    <p>San Francisco Administrative Code §37.15 requires <em>owners of residential dwelling units subject to Chapter 37</em> to report their units to the Rent Board. The Board then issues a <strong>rent increase licence</strong>. The Rent Board's own guidance says <em>"Property owners who report that a unit is tenant-occupied will receive a rent increase license that allows them to impose annual allowable and banked rent increases"</em> and that a current licence must be on file <em>"before any annual or banked rent increase can go into effect"</em>. Nothing in the ordinance or the guidance exempts an individual owner, a two-unit building, or a landlord who is not a corporation.</p>
    <p><strong>But the licence is not an application about your increase, and you do not send the Rent Board the notice.</strong> It is generated automatically when you file the annual <em>Housing Inventory</em> report online, it costs nothing, and it is renewed by filing again each year by 1&nbsp;March. Banked increases <em>"do not have to be approved by the Rent Board"</em>. Beyond that report, the Board's role is petition-driven: a landlord petition if you want to exceed the allowance, or a tenant petition if the increase is challenged.</p>
    <p><strong>So the sequence you read about is real, but narrower than it sounds:</strong> file the annual Housing Inventory report → receive the licence → calculate the lawful amount → serve a notice that contains every required element → keep the proof. Skip step 1 and a perfectly calculated increase is unenforceable for the months the licence was suspended. <a href="@@/hub/licensing.html">Full step-by-step answer, with the exact text and links →</a></p>
  </div>

  <div class="callout">
    <p><strong>One number to act on now.</strong> The current allowance of 1.6% applies only to increases effective between 1 March 2026 and 28 February 2027. If Unit 2's accumulated 13.1% is to be imposed at that rate with the 90 days' notice a >10% increase requires, the notice has to be served by <strong>{u2_serve}</strong> ({u2_mail} if mailed). After that, the effective date falls into a rate period the Rent Board has not yet published.</p>
  </div>
</section>

<div class="kpis">
  <div class="kpi accent">
    <div class="label">Current annual allowance</div>
    <div class="value">1.6%<small> / year</small></div>
    <div class="note">Effective 1 Mar 2026 – 28 Feb 2027. Published by the SF Rent Board (Form 571). <a href="@@/hub/limits.html">Rate history →</a></div>
  </div>
  <div class="kpi">
    <div class="label">Unit 1 — certain increase</div>
    <div class="value">{u1_annual}<small> / mo</small></div>
    <div class="note">1.6% on {u1_base} → {u1_annual_rent}, effective {u1_eff}. A further 1.4% ({u1_banked}) is conditional on the banking test in flag H-01.</div>
  </div>
  <div class="kpi">
    <div class="label">Unit 2 — lawful maximum</div>
    <div class="value">{u2_total}<small> / mo</small></div>
    <div class="note">13.1% on {u2_base} → {u2_total_rent}, from six banked anniversaries plus the current year. Requires 90 days' notice.</div>
  </div>
  <div class="kpi warn">
    <div class="label">Notice deadline</div>
    <div class="value">{u2_serve}</div>
    <div class="note">Last service date for Unit 2's 13.1% to take effect 28 Feb 2027, the final day of the 1.6% rate.</div>
  </div>
</div>

<section>
  <h2>What is on this dashboard<span class="sub">Nine pages, one question each. Every table row carries a link to the official source it rests on.</span></h2>
  <div class="grid-2">
    <a class="cardlink" href="@@/hub/licensing.html"><strong>Licence &amp; the Rent Board</strong><span>The seven questions about the licence and the Board, answered from §37.15, §37.3 and the Housing Inventory guidance — and what makes an increase challengeable.</span></a>
    <a class="cardlink" href="@@/hub/limits.html"><strong>Limits &amp; amounts</strong><span>Local, state and federal layering; the Rent Board's published percentages back to 1982; the arithmetic for both units, additive and never compounded.</span></a>
    <a class="cardlink" href="@@/hub/notice.html"><strong>Notice &amp; reasons</strong><span>What the notice must contain, the last safe service dates, and which reasons are lawful and which are not.</span></a>
    <a class="cardlink" href="@@/hub/practice.html"><strong>Owner practice</strong><span>How large operators and individual owners are treated by the same ordinance, and the one practice San Francisco bans outright.</span></a>
    <a class="cardlink" href="@@/hub/fair-housing.html"><strong>One unit or both</strong><span>Whether raising one rent and not the other creates discrimination exposure, and what actually does.</span></a>
    <a class="cardlink" href="@@/hub/review.html"><strong>Tenant-lawyer test</strong><span>The twelve checks a tenant-side lawyer would run, the evidence each needs, and where this file currently stands.</span></a>
    <a class="cardlink" href="@@/hub/flags.html"><strong>Flagged for Review</strong><span>Sixteen items: conflicting official text, values left blank because no official source confirms them, and repository defects.</span></a>
    <a class="cardlink" href="@@/hub/sources.html"><strong>Sources</strong><span>Nineteen official sources with the verbatim sentence each is used for and the date it was fetched.</span></a>
  </div>
</section>

<section>
  <h2>The two units at a glance<span class="sub">Placeholder tenant names; dates and dollar amounts exactly as supplied.</span></h2>
  {unit_table}
  <p class="small"><strong>Badges.</strong> {b_ok} quoted from an official source · {b_calc} arithmetic performed on official percentages · {b_flag} needs evidence or has conflicting official text · {b_unv} no official source found, value left blank.</p>
</section>

<section>
  <h2>Every question you asked, and where it is answered<span class="sub">Nothing is answered only in prose: each row points at the page holding the source-linked table.</span></h2>
  {q_table}
</section>

<section>
  <h2>What this file does not contain<span class="sub">Left blank on purpose, because no official source confirms it.</span></h2>
  <div class="tablewrap"><table>
  <caption>Unverified values are never inferred or filled in.</caption>
  <thead><tr><th scope="col">Value</th><th scope="col">Status</th><th scope="col">Why it is blank</th><th scope="col">Flag</th></tr></thead>
  <tbody>
    <tr><td>Whether both units hold a current rent increase licence</td><td>{b_unv}</td><td>The record lives in the Rent Board Portal, which this session cannot access.</td><td><a href="@@/hub/flags.html#H-04">H-04</a></td></tr>
    <tr><td>Certificate-of-occupancy date and coverage confirmation</td><td>{b_unv}</td><td>Year built 1940 is supplied by the owner; the official record was not checked.</td><td><a href="@@/hub/flags.html#H-05">H-05</a></td></tr>
    <tr><td>Rent ledger showing no increase since 2019 (Unit 2) or since Feb 2025 (Unit 1)</td><td>{b_unv}</td><td>Owner statement only.</td><td><a href="@@/hub/flags.html#H-03">H-03</a>, <a href="@@/hub/flags.html#H-02">H-02</a></td></tr>
    <tr><td>A &ldquo;normal&rdquo; market-level increase for 94122</td><td>{b_unv}</td><td>No official source publishes one for covered units; commercial listing data is not official and was not used.</td><td><a href="@@/hub/flags.html#H-10">H-10</a></td></tr>
    <tr><td>The 2027-28 allowance percentage</td><td>{b_unv}</td><td>Set by the Rent Board on 1 March 2027.</td><td><a href="@@/hub/flags.html#H-08">H-08</a></td></tr>
    <tr><td>How corporations vs individual owners typically behave</td><td>{b_unv}</td><td>No official dataset exists; only the binding rules are verified.</td><td><a href="@@/hub/flags.html#H-11">H-11</a></td></tr>
  </tbody></table></div>
</section>

<section>
  <h2>Other editions in this repository<span class="sub">Earlier sessions built independent editions from the same primary sources. They are preserved unchanged; this dashboard is the single entry point.</span></h2>
  <div class="grid-2">
    <a class="cardlink" href="integration/index.html"><strong>Integration edition — six pages</strong><span>Built in parallel on the same day by another session, deliberately more cautious: owner-supplied facts are left blank rather than calculated, and no attorney verdict is claimed. Preserved unchanged; its flags are linked here.</span></a>
    <a class="cardlink" href="docs/index.html"><strong>Main edition — ten pages</strong><span>Full narrative treatment: limits, rules by level, process, practice, discrimination and a 12-point review test.</span></a>
    <a class="cardlink" href="docs/v2/index.html"><strong>Companion edition — thirteen pages</strong><span>Generated from its own dataset, with a 31-row requirement matrix and a row-by-row reconciliation against the main edition.</span></a>
    <a class="cardlink" href="dashboard/index.html"><strong>Verification dashboard</strong><span>Independent build with a client-side table filter and its own 42-source registry.</span></a>
    <a class="cardlink" href="portal/index.html"><strong>Compliance portal</strong><span>Ten category pages including a repository verification audit and a flagged-for-review register.</span></a>
  </div>
</section>
"""

index_unit_rows = []
for key, n in (("U1", u1), ("U2", u2)):
    unit = DATA["units"][key]
    index_unit_rows.append([
        "<strong>{}</strong><br><span class=\"small\">{}</span><br><span class=\"small\">{}</span>".format(unit["label"], esc(unit["placeholder"]), esc(unit["occupancy_note"])),
        ('<span class="num">' + money(n["base"]) + "</span>", "num"),
        longdate(unit["lease_start"]),
        "{} = {}".format(pct(n["annual_pct"]), money(n["annual_amt"])),
        "{} = {}".format(pct(n["total_pct"]), money(n["total_amt"])),
        '<span class="num">' + money(n["total_rent"]) + "</span>",
        src_links(["S05", "S06"] if key == "U2" else ["S05"]),
    ])

unit_table = table(
    ["Unit", ("Base rent", "num"), "Last lease start", "Current year (1.6%)", "Maximum if banked", ("New rent at maximum", "num"), "Source"],
    index_unit_rows,
    caption="Rent figures are the owner's amounts; percentages are the Rent Board's published allowances. Every dollar figure is recomputed on the Limits page.",
    cls="data-table",
)

q_rows = [
    ["Do I need a Rent Board licence, and must I inform the Board before notifying tenants?", "Yes to the licence (free, automatic on the annual Housing Inventory report, required on the effective date); no to filing the notice — annual and banked increases are not approved by the Board.", '<a href="@@/hub/licensing.html">Licence &amp; Board</a>', src_links(["S01", "S03", "S04"])],
    ["Is the increase lawfully capped, and at what number, under local, state and federal law?", "Local: 1.6% plus any properly banked percentages. State: AB 1482's 8.8% does not apply to locally controlled units. Federal: no rent ceiling; fair housing is the binding rule.", '<a href="@@/hub/limits.html">Limits &amp; amounts</a>', src_links(["S05", "S09", "S10", "S14"])],
    ["How do large real estate corporations handle increases, and how do individual owners?", "Identical legal duties; the observable difference is that San Francisco bans the algorithmic pricing tools large operators use elsewhere, and no official dataset measures behaviour by owner type.", '<a href="@@/hub/practice.html">Owner practice</a>', src_links(["S02", "S16"])],
    ["How should tenants be told, and what is a reasonable reason?", "A written notice served under Civil Code §827 with the dollar amount, percentage, effective date and annual-vs-banked split. The reason is the published allowance itself; market catch-up is not a lawful reason.", '<a href="@@/hub/notice.html">Notice &amp; reasons</a>', src_links(["S08", "S02"])],
    ["Would a tenant lawyer and tenant advocates accept it?", "Twelve checks; seven pass on the documents as described, five need evidence (licence status, coverage, ledger, complaint history, policy record).", '<a href="@@/hub/review.html">Lawyer test</a>', src_links(["S03", "S12", "S15"])],
    ["Is it lawful to raise one unit and not the other?", "Yes. Nothing in Chapter 37 or the fair housing statutes requires parallel treatment; what is unlawful is a difference that is because of a protected characteristic, or a retaliatory or bad-faith increase.", '<a href="@@/hub/fair-housing.html">One unit or both</a>', src_links(["S13", "S14", "S15"])],
    ["What is still unverified?", "Sixteen flags, including the 24-month vs 12-month banking conflict that makes Unit 1's extra 1.4% conditional.", '<a href="@@/hub/flags.html">Flagged for Review</a>', src_links(["S04", "S07"])],
]
q_table = table(["Question", "Short answer", "Detail", "Source"], q_rows, cls="data-table")

index_html = page(
    "index.html",
    "SF Rent Increase Compliance Dashboard — Outer Sunset 94122",
    "Official-source dashboard on rent increases for two rent-controlled San Francisco units built in 1940: the Rent Board licence, the 1.6% allowance, banked increases, notice rules, and every figure traced to an official link.",
    hero_block(
        "Executive summary · verified {}".format(DATA["meta"]["retrieved"]),
        "Raising the rent on two 1940 flats in the Outer Sunset — what the Rent Board requires, and what the numbers actually are",
        "Both units were built in 1940, so both are covered by the San Francisco Rent Ordinance. That single fact decides almost every question here: local law sets the ceiling, the Rent Board publishes it once a year, and the Board's licence — not the notice — is the step that decides whether an increase can be enforced at all.",
        ["ZIP 94122", "Built 1940 → Chapter 37", "1.6% allowance to 28 Feb 2027", "19 official sources, all re-fetched 7 Nov 2026", "Tenant data anonymised"],
    ),
    index_body.format(
        u1_annual=money(u1["annual_amt"]), u1_base=money(u1["base"]), u1_annual_rent=money(u1["annual_rent"]),
        u1_banked=money(u1["banked_amt"]), u1_eff=longdate(DATA["calculations"]["U1"]["annual_effective"]),
        u2_total=money(u2["total_amt"]), u2_base=money(u2["base"]), u2_total_rent=money(u2["total_rent"]),
        u2_serve=longdate(N["U2"]["serve_by"].isoformat()), u2_mail=longdate(N["U2"]["mail_by"].isoformat()),
        unit_table=unit_table, q_table=q_table,
        b_ok=badge("ok", "Verified"), b_calc=badge("calc", "Calculated"),
        b_flag=badge("flag", "Flag"), b_unv=badge("unv", "Unverified"),
    ),
)

# --------------------------------------------------------------------------- licensing
lic_rows = []
for step in DATA["licensing_steps"]:
    lic_rows.append([
        '<span class="mono">Q{}</span>'.format(step["step"]),
        "<strong>{}</strong>".format(esc(step["question"])),
        esc(step["answer"]),
        status_badge(step["status"]),
        src_links(step["sources"]),
    ])
lic_table = table(
    ["#", "Question", "Answer, from the official text", "Status", "Source"],
    lic_rows,
    caption="The licence question, in the order an owner needs it answered.",
    cls="data-table",
)

proc_rows = []
for s in DATA["process_steps"]:
    proc_rows.append([
        '<span class="mono">{}</span>'.format(s["step"]),
        "<strong>{}</strong>".format(esc(s["action"])),
        esc(s["detail"]),
        status_badge(s["status"]),
        src_links(s["sources"]),
    ])
proc_table = table(["Step", "Action", "What to do, and why", "Status", "Source"], proc_rows,
                   caption="The compliance sequence, in order. Steps 1 and 2 decide whether the rest is usable.", cls="data-table")

challenge_rows = [
    ["No rent increase licence in force on the effective date", "Licence suspended; tenant is not obligated to pay the increase for the suspended months", src_links(["S01"])],
    ["The notice omits the annual/banked itemisation", "Ordinance treats a nonconforming increase as null and void", src_links(["S02", "S07"])],
    ["The percentage used is not the one in force on the effective date", "Incorrect amount; the difference is unenforceable", src_links(["S05"])],
    ["The increase is compounded, or rounded up", "Amount exceeds the allowance", src_links(["S07", "S04"])],
    ["The notice period is short (30 days for ≤10%, 90 days for >10%, +5 if mailed)", "Effective date is not valid", src_links(["S08"])],
    ["The increase is within 180 days of a habitability complaint", "Statutory retaliation bar", src_links(["S12"])],
    ["The increase is bad faith pressure to vacate", "Harassment: treble damages and attorney's fees", src_links(["S15"])],
    ["The difference between units tracks a protected characteristic", "FEHA / Fair Housing Act exposure, and harassment under the local ordinance", src_links(["S13", "S14", "S15"])],
    ["A charge was added because an occupant joined (April 2026)", "Expressly unlawful as an increase", src_links(["S02", "S05"])],
]
challenge_table = table(["What a tenant or advocate would challenge", "Consequence", "Source"], challenge_rows, cls="data-table")

not_licence_rows = [
    ["A fee", "The licence is free: &ldquo;Reporting is free and can be done online 24/7&rdquo;.", src_links(["S03"])],
    ["Approval of the percentage", "Banked increases &ldquo;do not have to be approved by the Rent Board&rdquo;; the allowance is published by the Board for everyone.", src_links(["S04", "S05"])],
    ["A copy of the notice sent to the Board", "No such filing appears in §37.3 (what the tenant must be told) or §37.15 (what the Board must be told).", src_links(["S02", "S01"])],
    ["The same thing as the annual Rent Board fee", "$59.00 per dwelling unit for 2026-2027, due 1 March, up to $29.50 recoverable; a fee exemption does not satisfy the inventory requirement.", src_links(["S17", "S03"])],
    ["Attached to the notice", "&ldquo;The rent increase license does not need to be included with your rent increase notice.&rdquo;", src_links(["S03"])],
]
not_licence_table = table(["The licence is not…", "What the official text says", "Source"], not_licence_rows, cls="data-table")

licensing_body = """
<section>
  <h2>The short answer<span class="sub">§37.15 and the Rent Board's Housing Inventory guidance, read together.</span></h2>
  <div class="answer">
    <h3>Yes — a sole individual owner of a two-unit building needs the rent increase licence. No — the Rent Board does not approve, license or receive the individual increase.</h3>
    <p>The licence requirement is drafted by reference to the <em>unit</em>, not the owner's size or corporate form: &ldquo;Owners of residential dwelling units subject to this Chapter 37 shall be required to report certain information about their units to the Rent Board&rdquo;. The Board's guidance repeats that <em>all</em> owners must report, that reporting began for buildings with fewer than 10 units on 1 March 2023, and that a tenant-occupied unit reported in the Housing Inventory <em>receives</em> a licence.</p>
    <p>What you read is therefore half right in a way that matters. The licence is the anti-challenge step — an increase without it cannot be enforced. But it is not an application, and there is no separate &ldquo;inform the Rent Board of my increase&rdquo; filing for an annual or banked increase. You earn the licence once a year by reporting, and you spend it by serving a conforming notice.</p>
  </div>
  <div class="callout">
    <p><strong>Two prerequisites can void an otherwise perfect increase:</strong> (1) no licence on the effective date, and (2) a notice that does not conform. Both are cheap to fix before service and expensive to fix after it. Neither is affected by the owner being an individual rather than a corporation.</p>
  </div>
</section>

<section>
  <h2>Question by question<span class="sub">Each answer quotes or paraphrases a single official page, linked in the last column.</span></h2>
  {lic_table}
</section>

<section>
  <h2>Do this, in this order, before the tenants hear anything<span class="sub">Steps 1 and 2 are the ones the question was really about.</span></h2>
  {proc_table}
  <p class="small">This sequence adds nothing to the ordinance; it only orders what §§37.3, 37.15 and Civil Code §827 already require, plus the records needed to prove it later.</p>
</section>

<section>
  <h2>What actually makes a rent increase challengeable<span class="sub">This is the list a tenant-side advocate works from. Each row is a defect with a citation, not an opinion.</span></h2>
  {challenge_table}
  <p class="small">A tenant does not need a lawyer to raise any of these: &ldquo;you do not need a lawyer to file a petition at the Rent Board&rdquo;, and free representation is available in 94122 — Open Door Legal lists a Sunset office at 1722 Irving Street. {s19}</p>
</section>

<section>
  <h2>What the licence is not<span class="sub">The four confusions that cost owners money or time.</span></h2>
  {not_licence_table}
</section>

<section>
  <h2>Where this leaves these two units<span class="sub">The licence question is answerable today; the licence status is not, and that is the one thing to check first.</span></h2>
  <ul>
    <li><strong>Both units need a current licence on the effective date.</strong> The reporting obligation started on 1 March 2023 for a building of this size, so it is not new.</li>
    <li><strong>Filing is free and takes one annual report.</strong> The $59.00 per-unit fee is separate and does not create or replace the licence.</li>
    <li><strong>The licence is not consent to a particular increase.</strong> The arithmetic and the notice still have to be right — see <a href="@@/hub/limits.html">Limits &amp; amounts</a> and <a href="@@/hub/notice.html">Notice &amp; reasons</a>.</li>
    <li><strong>Status is unverified here.</strong> The Rent Board Portal holds the record and tenants can search it, so assume it will be checked. See flag <a href="@@/hub/flags.html#H-04">H-04</a>.</li>
  </ul>
</section>
""".format(lic_table=lic_table, proc_table=proc_table, challenge_table=challenge_table,
           not_licence_table=not_licence_table, s19=src_links(["S19"]))

licensing_html = page(
    "hub/licensing.html",
    "Rent Board licence and notification — SF Rent Increase Compliance",
    "Does an individual San Francisco owner need a Rent Board rent-increase licence before raising rent? Yes: §37.15, the Housing Inventory report, and what the licence does and does not do.",
    hero_block(
        "Question 1 of 6 · the rent increase licence",
        "Do you have to apply to the Rent Board before raising the rent?",
        "You need the licence — but not the application you were probably imagining. Here is the exact duty, the exact mechanism, and the exact consequence of skipping it, for a sole owner of a two-unit building in 94122.",
        ["§37.15", "§37.3", "Housing Inventory", "Free licence", "Required on the effective date"],
    ),
    licensing_body,
)

# --------------------------------------------------------------------------- limits
rate_rows = []
for r in DATA["rates"]:
    cur = r.get("current")
    rate_rows.append([
        ("<strong>{}</strong>".format(pct(r["pct"])) if cur else pct(r["pct"]), "num"),
        "{} – {}".format(r["start"].replace("-", "/"), r["end"].replace("-", "/")),
        badge("ok", "Current") if cur else "",
        src_links(["S06"]),
    ])
rate_table = table([("Allowance", "num"), "Effective period", "Status", "Source"], rate_rows,
                   caption="Every percentage published by the Rent Board, 1982 to 2027, from Form 571.", cls="data-table")

bank_rows = []
for key, label in (("U1", "Unit 1"), ("U2", "Unit 2")):
    calc = DATA["calculations"][key]
    n = N[key]
    rows = []
    for b in calc["banked"]:
        rows.append([
            label,
            longdate(b["for_date"]),
            pct(b["pct"]),
            money((n["base"] * Decimal(b["pct"]) / Decimal(100)).quantize(C, rounding=ROUND_HALF_UP)),
            badge("flag", "Conditional — H-01") if b["conditional"] else badge("ok", "Banked"),
            src_links(["S06"]),
        ])
    bank_rows.extend(rows)
bank_rows.append(["Unit 1", "Current year: " + pct(N["U1"]["annual_pct"]) + " effective " + longdate(N["U1"]["effective"].isoformat()), pct(N["U1"]["annual_pct"]), money(N["U1"]["annual_amt"]), badge("ok", "Available"), src_links(["S05", "S06"])])
bank_rows.append(["Unit 2", "Current year: " + pct(N["U2"]["annual_pct"]) + " effective " + longdate(N["U2"]["effective"].isoformat()), pct(N["U2"]["annual_pct"]), money(N["U2"]["annual_amt"]), badge("ok", "Available"), src_links(["S05", "S06"])])
bank_table = table(["Unit", "Anniversary the allowance belongs to", ("Allowance", "num"), ("Monthly value", "num"), "Status", "Source"], bank_rows,
                   caption="Banked and current allowances, unit by unit. The percentages are added, never compounded.", cls="data-table")

layer_rows = [
    ["Local — SF Rent Ordinance", "1.6% annual allowance for increases effective 1 Mar 2026 – 28 Feb 2027, plus any properly banked allowance; 7% absolute ceiling on the annual increase; one increase every 12 months; no compounding; no rounding up.", "Controls the result for these units.", src_links(["S02", "S05", "S06"])],
    ["State — AB 1482 / Civil Code §1947.12", "5% + CPI, or 10%, whichever is lower; 8.8% for San Francisco from 1 Aug 2026 to 31 Jul 2027.", "Does not apply: the section excludes housing under a local ordinance that restricts increases to less than the state cap.", src_links(["S09", "S10"])],
    ["State — Costa-Hawkins, Civil Code §1954.53", "Allows an owner to set a new initial rent when the last original occupant has left; expressly does not apply to a partial change of occupancy.", "Does not reset either unit: Unit 1 kept an original tenant through the April 2026 change; Unit 2's tenancy never ended.", src_links(["S11"])],
    ["State — Civil Code §827", "30 days' notice for an increase of 10% or less; 90 days for more; +5 days if mailed.", "Sets the notice clock for both units.", src_links(["S08"])],
    ["Federal", "No federal statute or regulation setting a rent ceiling for private, unsubsidised housing was located in this review. The binding federal rule identified is the Fair Housing Act's prohibition on discrimination in the terms and conditions of a rental.", "Applies to how the increase is applied, not how much it is. Flagged as a negative finding (H-11).", src_links(["S14"])],
]
layer_table = table(["Level", "What it says", "Effect on these two units", "Source"], layer_rows, cls="data-table")

u1_rows = [
    ["Base rent", money(N["U1"]["base"]), "Owner record — not verified against a lease in this session (flag <a href=\"@@/hub/flags.html#H-02\">H-02</a>)."],
    ["10% notice threshold", "Increase ≤ 10% → 30 days' notice", src_links(["S08"])],
    ["Annual allowance at 1 Feb 2027", "1.6% × {0} = {1}".format(money(N["U1"]["base"]), money(N["U1"]["annual_amt"])), src_links(["S05", "S06"])],
    ["New rent, annual increase only", "<strong>{}</strong>".format(money(N["U1"]["annual_rent"])), "Certain, if served at least 30 days before the effective date. " + src_links(["S05"])],
    ["Skipped 1.4% from 1 Feb 2026", "1.4% × {0} = {1}".format(money(N["U1"]["base"]), money(N["U1"]["banked_amt"])), src_links(["S06"])],
    ["Total if the banked 1.4% is allowed", "3.0% = {0}; new rent {1}".format(money(N["U1"]["total_amt"]), money(N["U1"]["total_rent"])), badge("flag", "Conditional") + ' <a href="@@/hub/flags.html#H-01">H-01</a>'],
    ["7% annual ceiling", "Not engaged: 1.6% is far below it.", src_links(["S02"])],
    ["Earliest date that satisfies the stricter banking test", longdate("2027-02-01") + " — exactly 24 months after the last rent took effect.", src_links(["S04"])],
]
u1_table = table(["Item", "Value", "Basis and source"], u1_rows, cls="data-table")

u2_rows = [
    ["Base rent", money(N["U2"]["base"]), "Owner record — not verified against a lease or ledger in this session (flag <a href=\"@@/hub/flags.html#H-03\">H-03</a>)."],
    ["10% notice threshold", "Increase > 10% → 90 days' notice, +5 if mailed", src_links(["S08"])],
    ["Banked allowances, 2020-2025", "1.8 + 0.7 + 2.3 + 3.6 + 1.7 + 1.4 = 11.5% = {0}".format(money(N["U2"]["banked_amt"])), src_links(["S04", "S06"])],
    ["Current annual allowance", "1.6% = {0}".format(money(N["U2"]["annual_amt"])), src_links(["S05", "S06"])],
    ["Lawful maximum", "13.1% = {0}; new rent {1}".format(money(N["U2"]["total_amt"]), money(N["U2"]["total_rent"])), "Percentages added, not compounded; not rounded up. " + src_links(["S05", "S04"])],
    ["What compounding would have produced", "A larger figure than {0} — and unlawful.".format(money(N["U2"]["total_amt"])), src_links(["S07", "S04"])],
    ["Is a total above 10% permitted?", "Yes: banked increases are not capped in total; the 10% figure is a notice threshold, not a cap.", src_links(["S04", "S08"])],
    ["Latest effective date at the 1.6% rate", longdate("2027-02-28"), src_links(["S06"])],
]
u2_table = table(["Item", "Value", "Basis and source"], u2_rows, cls="data-table")

limits_body = """
<section>
  <h2>What &ldquo;reasonable and normal&rdquo; means in law<span class="sub">The only defensible benchmark is the published allowance. There is no official &ldquo;market&rdquo; figure for a covered unit.</span></h2>
  <p>For a sitting tenant in a covered unit, the ordinance is a price-control scheme, not a fairness standard. The lawful increase is the published percentage, plus anything properly banked, and nothing more without a petition. That is also the number a tenant lawyer will compare against, which is why it is the only figure worth planning around.</p>
  <div class="callout">
    <p><strong>Unverified on purpose:</strong> no official source publishes a &ldquo;normal&rdquo; increase for 94122, and commercial listing data is not an official source, so no market figure appears anywhere on this site. The value is blank and flagged <a href="@@/hub/flags.html#H-10">H-10</a>.</p>
  </div>
</section>

<section>
  <h2>Local, state and federal law on one page<span class="sub">Local law sets the ceiling; state law sets the notice; federal law governs how the increase may be applied.</span></h2>
  {layer_table}
</section>

<section>
  <h2>The Rent Board's published allowances<span class="sub">Form 571, re-fetched 7 November 2026. Every row links to the same official PDF.</span></h2>
  {rate_table}
  <p class="small">The Board calculates the annual figure as 60% of the change in the Bay Area CPI, with a 7% absolute ceiling. At current rates the ceiling has never been the binding constraint.</p>
</section>

<section>
  <h2>Unit 1 — {u1_base} a month, anniversary 1 February<span class="sub">The certain increase is 1.6%. A further 1.4% depends on which banking test the Board applies.</span></h2>
  {u1_table}
  <div class="callout">
    <p><strong>Why the extra 1.4% is conditional.</strong> The Rent Board's banking page says a skipped increase is banked only if at least 24 full months pass without any increase; Rule 4.12(a) and the Board's worked examples use a 12-month test. 1 February 2027 is exactly 24 months after the last rent took effect, so it satisfies both readings — but confirm before including the extra {u1_banked}. See <a href="@@/hub/flags.html#H-01">H-01</a>.</p>
  </div>
</section>

<section>
  <h2>Unit 2 — {u2_base} a month, unchanged since 1 June 2019<span class="sub">Seven anniversaries were never used. Added, they are 13.1%, not 13.1% compounded.</span></h2>
  {u2_table}
  <p class="small">Both maximums assume the base rent on record and the absence of any intervening increase since 2019-06-01; those are owner records, not official records, and are flagged H-02 and H-03. If a ledger shows otherwise, the banked percentages and both figures change.</p>
  <p class="small">13.1% is lawful but conspicuous. It is economically an average of about 1.9% a year over the seven years it accumulated, which is the point to make in any conversation with the tenants — the arithmetic, not the percentage, is the explanation.</p>
</section>

<section>
  <h2>Banked and current allowances, line by line<span class="sub">Each anniversary's published percentage and its dollar value on that unit's base rent.</span></h2>
  {bank_table}
  <div class="callout">
    <p><strong>Banking rules, from the two official pages:</strong> a skipped increase can be saved and imposed later; banked increases do not expire during a tenancy; there is no limit on the total that can be banked; they cannot be compounded or prorated; they do not carry over to a new tenant; and they do not need the Board's approval. {s04}</p>
  </div>
</section>
""".format(layer_table=layer_table, rate_table=rate_table, u1_table=u1_table, u2_table=u2_table,
           bank_table=bank_table, u1_base=money(N["U1"]["base"]), u2_base=money(N["U2"]["base"]),
           u1_banked=money(N["U1"]["banked_amt"]), s04=src_links(["S04"]))

limits_html = page(
    "hub/limits.html",
    "Increase limits, rates and the arithmetic — SF Rent Increase Compliance",
    "The Rent Board's published annual allowances from 1982 to 2027, local/state/federal layering, and the lawful maximum for each of the two Outer Sunset units.",
    hero_block(
        "Question 2 of 6 · limits and amounts",
        "What a lawful increase is, to the cent, for both units",
        "1.6% is the allowance for increases effective between 1 March 2026 and 28 February 2027. On these two rents that is {0} and {1} a month. Unit 2's six unused anniversaries add another 11.5%, which is lawful, additive, and the number most likely to be questioned.".format(money(u1["annual_amt"]), money(u2["annual_amt"])),
        ["Local cap controls", "AB 1482 does not apply", "No compounding", "No rounding up"],
    ),
    limits_body,
)

# --------------------------------------------------------------------------- notice
notice_rows_html = []
for r in DATA["notice_rows"]:
    notice_rows_html.append([esc(r["item"]), esc(r["detail"]), src_links(r["sources"])])
notice_table = table(["Required element", "Detail", "Source"], notice_rows_html, cls="data-table")

deadline_rows = [
    ["Unit 1 — 1.6% only", money(N["U1"]["annual_amt"]), "30 days", longdate(N["U1"]["short_serve_by"].isoformat()), longdate(N["U1"]["short_mail_by"].isoformat()), longdate(N["U1"]["effective"].isoformat()), src_links(["S08"])],
    ["Unit 1 — 1.6% + banked 1.4% (3.0%)", money(N["U1"]["total_amt"]), "30 days", longdate(N["U1"]["serve_by"].isoformat()), longdate(N["U1"]["mail_by"].isoformat()), longdate(N["U1"]["effective"].isoformat()), src_links(["S08"])],
    ["Unit 2 — 1.6% only (a modest increase)", money(N["U2"]["annual_amt"]), "30 days", longdate(N["U2"]["short_serve_by"].isoformat()), longdate(N["U2"]["short_mail_by"].isoformat()), longdate(N["U2"]["effective"].isoformat()), src_links(["S08"])],
    ["Unit 2 — full 13.1%", money(N["U2"]["total_amt"]), "90 days", longdate(N["U2"]["serve_by"].isoformat()), longdate(N["U2"]["mail_by"].isoformat()), longdate(N["U2"]["effective"].isoformat()), src_links(["S08"])],
]
deadline_table = table(["Structure", ("Increase", "num"), "Notice", "Serve in person by", "Mail by", "Earliest effective date", "Source"], deadline_rows,
                       caption="Computed from the intended effective date, adding the statutory period and 5 more days for mailed service.", cls="data-table")

reason_rows = []
for r in DATA["reasons"]:
    lawful = r["lawful"]
    cls = "ok" if lawful.startswith("Yes") else ("flag" if "petition" in lawful or "within" in lawful else "high")
    reason_rows.append([esc(r["reason"]), badge(cls, lawful), esc(r["detail"]), src_links(r["sources"])])
reason_table = table(["Reason for the increase", "Lawful for a sitting tenant?", "What is required", "Source"], reason_rows, cls="data-table")

notice_body = """
<section>
  <h2>The notice is where increases fail<span class="sub">Not the percentage. A conforming amount in a nonconforming notice is void.</span></h2>
  <p>San Francisco treats notice defects strictly: §37.3(b)(5) provides that &ldquo;any rent increase which does not conform with the provisions of this section shall be null and void&rdquo;. Civil Code §827 separately sets the minimum notice period. Both must be satisfied, plus the licence, before the increase can be enforced.</p>
  {notice_table}
  <p class="small">Rule 4.10(b) adds its own version of the same rule and an exception for an amount that equals the allowable annual plus banked increase; the safe course is to satisfy the strictest reading. See flag <a href="@@/hub/flags.html#H-15">H-15</a>.</p>
</section>

<section>
  <h2>The last safe service dates<span class="sub">Computed from 28 February 2027 — the final day of the 1.6% rate and the last day an increase at that rate can take effect.</span></h2>
  {deadline_table}
  <div class="callout red">
    <p><strong>The Unit 2 window closes first.</strong> A 13.1% increase needs 90 days' notice. Served today ({today}), the earliest effective date is {earliest} — inside the 1.6% period, but the last permissible service date is {u2_serve} ({u2_mail} if mailed). After that, the effective date moves into the rate period that begins 1 March 2027, whose percentage the Board has not yet published.</p>
  </div>
</section>

<section>
  <h2>Lawful and unlawful reasons<span class="sub">&ldquo;What is a reasonable reason?&rdquo; has a short answer: for a sitting tenant, the reason is the published allowance itself.</span></h2>
  {reason_table}
  <p class="small">No justification letter is required for the annual or banked portion. What is required is that the notice state what parts of the increase are annual and banked, and the dates the banked amount is based on.</p>
</section>

<section>
  <h2>A notice skeleton that a reviewer can follow<span class="sub">A drafting aid, not an official form. It adds no requirement — it only orders the required elements.</span></h2>
  <dl class="kv">
    <dt>To</dt><dd>Tenant 1A and Tenant 1B, Unit 1 <span class="small">(address withheld from this site)</span></dd>
    <dt>Subject</dt><dd>Notice of rent increase effective {u1_eff_long}</dd>
    <dt>Current base rent</dt><dd>{u1_base} per month</dd>
    <dt>Amount of increase</dt><dd>{u1_annual} per month (1.6%)</dd>
    <dt>Basis</dt><dd>The annual allowable increase of 1.6% for 1 March 2026 – 28 February 2027, published by the San Francisco Rent Board, applied to the 1 February anniversary date.</dd>
    <dt>Banked portion</dt><dd>None. <span class="small">If the 1.4% from 1 February 2026 is claimed, state it separately with its date: {u1_banked} per month.</span></dd>
    <dt>New base rent</dt><dd>{u1_annual_rent} per month, effective {u1_eff_long}</dd>
    <dt>No rounding / no passthrough</dt><dd>State both expressly.</dd>
    <dt>Tenant's rights</dt><dd>Name the Rent Board and 415-252-4600; state that the tenant may petition the Board at no cost and does not need a lawyer to do so.</dd>
  </dl>
  <p class="small">For Unit 2 at 13.1%, the banked paragraph must itemise each year: 1.8% (1 June 2020), 0.7% (1 June 2021), 2.3% (1 June 2022), 3.6% (1 June 2023), 1.7% (1 June 2024), 1.4% (1 June 2025), plus the 1.6% annual increase in force on the effective date — total 13.1%, {u2_total}, new rent {u2_total_rent}.</p>
</section>
""".format(notice_table=notice_table, deadline_table=deadline_table, reason_table=reason_table,
           today=longdate(N["today"].isoformat()), earliest=longdate(N["earliest_90"].isoformat()),
           u2_serve=longdate(N["U2"]["serve_by"].isoformat()), u2_mail=longdate(N["U2"]["mail_by"].isoformat()),
           u1_eff_long=longdate(DATA["calculations"]["U1"]["annual_effective"]),
           u1_base=money(N["U1"]["base"]), u1_annual=money(N["U1"]["annual_amt"]),
           u1_banked=money(N["U1"]["banked_amt"]), u1_annual_rent=money(N["U1"]["annual_rent"]),
           u2_total=money(N["U2"]["total_amt"]), u2_total_rent=money(N["U2"]["total_rent"]))

notice_html = page(
    "hub/notice.html",
    "Notice requirements and lawful reasons — SF Rent Increase Compliance",
    "What a San Francisco rent increase notice must contain, the last safe service dates for each unit, and which reasons are lawful versus unlawful.",
    hero_block(
        "Question 3 of 6 · telling the tenants",
        "How to serve the increase, and what counts as a reason",
        "A conforming percentage can still be void if the notice is late or incomplete. The notice must state the dollar amount, the percentage, the effective date, and which part of the increase is annual and which is banked — with the dates the banked part rests on.",
        ["30 / 90 days", "+5 if mailed", "Itemise annual vs banked", "No rounding up"],
    ),
    notice_body,
)

# --------------------------------------------------------------------------- practice
practice_rows_html = []
for r in DATA["practice_rows"]:
    practice_rows_html.append([esc(r["topic"]), esc(r["corporate"]), esc(r["individual"]), src_links(r["sources"])])
practice_table = table(["Topic", "Large / corporate owners", "Individual owners", "Source"], practice_rows_html, cls="data-table")

practice_body = """
<section>
  <h2>The honest answer about practice<span class="sub">Official sources state the rules; they do not measure behaviour.</span></h2>
  <p>The question &ldquo;how do big corporations handle increases, and how do individual owners?&rdquo; has a verified half and an unverified half. The verified half is that the same ordinance applies to both — the same allowance, licence, notice period and banking rules — and that San Francisco prohibits algorithmic rent-setting that draws on non-public competitor data, for every landlord, large or small. That prohibition is the clearest official statement about how rents may be set at scale in this city. The unverified half is what typical owners actually do — no official dataset measures it, so nothing is asserted here. See flag <a href="@@/hub/flags.html#H-11">H-11</a>.</p>
  <div class="answer">
    <h3>What this means for you as an individual owner</h3>
    <p>You are held to exactly the standard a large owner is held to, and you have none of their administrative slack. That cuts both ways: the compliance burden is small and fixed (one annual report, one notice, one calculation), and a small owner who does those three things properly is, on the documents, indistinguishable from a compliant institution.</p>
  </div>
</section>

<section>
  <h2>Side by side<span class="sub">Same duties, different machinery.</span></h2>
  {practice_table}
</section>

<section>
  <h2>What large operators do differently, where it is verified<span class="sub">Two citable differences, one of them a prohibition.</span></h2>
  <ul>
    <li><strong>Pricing software is banned in San Francisco.</strong> §37.10C makes it unlawful to use an algorithmic device that performs calculations on non-public competitor data to advise a landlord on rent or occupancy, and gives tenants and tenant nonprofits a private right of action. It applies to every landlord, including you. {s16}</li>
    <li><strong>Corporate form closes a state-law exemption.</strong> The AB 1482 exemption for single-family homes and condominiums is unavailable to a REIT, a corporation, or an LLC with a corporate member. That exemption is irrelevant to these two units — both are already under the lower local cap — but it is the one place where owner type changes the analysis. {s09}</li>
    <li><strong>Everything else in the file is owner-neutral:</strong> the allowance, the licence, the notice period, the banking rules, the harassment and fair-housing exposure. {s02} {s01}</li>
  </ul>
  <p class="small">Earlier editions in this repository reached the same conclusion from the same sources, and also found no official quantitative dataset on owner behaviour.</p>
</section>

<section>
  <h2>The practical difference that does exist<span class="sub">Not legal, but worth naming.</span></h2>
  <p>Institutional owners run a compliance calendar; individual owners run the same rules from memory. The four dates that matter here are the annual 1 March Housing Inventory deadline, the anniversary date for each unit, the 90-day threshold for Unit 2's 13.1%, and the 28 February 2027 end of the 1.6% rate. Writing those four down is the entire difference between the two modes of practice.</p>
</section>
""".format(practice_table=practice_table, s16=src_links(["S16"]), s09=src_links(["S09"]),
           s02=src_links(["S02"]), s01=src_links(["S01"]))

practice_html = page(
    "hub/practice.html",
    "Corporate vs individual owner practice — SF Rent Increase Compliance",
    "How large real estate corporations and individual San Francisco owners are treated by the same rent ordinance, and the one pricing practice San Francisco bans.",
    hero_block(
        "Question 4 of 6 · owner practice",
        "Big owners, small owners, same ordinance",
        "Institutional landlords and a sole owner of two flats are held to identical rent-increase rules in San Francisco. Algorithmic rent-setting, the tool most associated with portfolio-scale pricing, is unlawful here for everyone.",
        ["Owner-neutral duties", "§37.10C pricing ban", "No official behaviour data"],
    ),
    practice_body,
)

# --------------------------------------------------------------------------- fair housing
fh_rows = []
for r in DATA["fair_housing_rows"]:
    fh_rows.append([esc(r["point"]), esc(r["finding"]), status_badge(r["status"]), src_links(r["sources"])])
fh_table = table(["Question", "Answer", "Status", "Source"], fh_rows, cls="data-table")

fh_body = """
<section>
  <h2>One unit or both?<span class="sub">The question is not what you do to the second unit; it is why the two units differ.</span></h2>
  <div class="answer">
    <h3>Raising one unit's rent and not the other is lawful. Raising either in a way that tracks a protected characteristic, or in bad faith, is not.</h3>
    <p>Nothing in Chapter 37, Civil Code §1947.12, Government Code §12955 or the federal Fair Housing Act requires an owner to treat two tenancies identically. What the statutes prohibit is discrimination or harassment <em>because of</em> a protected characteristic, retaliation, and bad-faith pressure to vacate. The two units here differ for objective reasons that are already in the file: base rents of {u1_base} and {u2_base}, different anniversary dates, and seven years of accumulated allowances on one side and one on the other.</p>
  </div>
  <p class="small">This is a reading of the cited statutory text, not legal advice, and not a prediction. Confirm with counsel or a Rent Board counselor if either tenancy involves a protected characteristic, a complaint, or a pending dispute.</p>
</section>

<section>
  <h2>The fair-housing analysis, point by point<span class="sub">Each row is either quoted from a statute or marked as a reading of it.</span></h2>
  {fh_table}
</section>

<section>
  <h2>What to do so that the difference is provably objective<span class="sub">Five records, none of them burdensome.</span></h2>
  <ol>
    <li><strong>Write the policy once.</strong> &ldquo;Each unit's rent is reviewed annually against the Rent Board allowance; differences reflect base rent, anniversary date and banked history.&rdquo; Apply it to both units, including the unit you choose not to raise.</li>
    <li><strong>Keep a per-unit calculation sheet</strong> showing base rent, percentage, dollar amount and effective date — the tables on <a href="@@/hub/limits.html">Limits &amp; amounts</a> are that sheet.</li>
    <li><strong>Never tie an increase to occupancy.</strong> The April 2026 change in Unit 1 cannot support a charge of any kind, even if the lease says it can. {s02}</li>
    <li><strong>Keep the 180-day retaliation window clear</strong> of habitability complaints, inspections or disputes. {s12}</li>
    <li><strong>Never use pricing software</strong> that draws on non-public competitor data. {s16}</li>
  </ol>
</section>

<section>
  <h2>Why &ldquo;raise both to be safe&rdquo; is not a safe harbour<span class="sub">There is no official rule that says parallel treatment cures a risk.</span></h2>
  <p>Treating both units the same does not make a difference disappear if the reason for an increase was unlawful, and treating them differently is not itself a violation. What an investigator or a tenant lawyer asks is: what is the documented reason, and does it stand up? Here it does — but only because each unit has its own arithmetic.</p>
  <p class="small">If you prefer a visible, uniform gesture, the lawful version is to apply the same <em>method</em> (annual review against the published allowance, same notice template, same documentation) rather than the same <em>percentage</em>, which the law does not require and the banked history does not support.</p>
</section>
""".format(fh_table=fh_table, u1_base=money(N["U1"]["base"]), u2_base=money(N["U2"]["base"]),
           s02=src_links(["S02"]), s12=src_links(["S12"]), s16=src_links(["S16"]))

fair_housing_html = page(
    "hub/fair-housing.html",
    "One unit or both — discrimination analysis — SF Rent Increase Compliance",
    "Whether raising one unit's rent and not the other creates fair-housing exposure in San Francisco, the protected classes under federal and California law, and how to document an objective difference.",
    hero_block(
        "Question 5 of 6 · one unit or both",
        "Is it safe to raise one rent and not the other?",
        "Yes, if the difference is explained by the arithmetic and the record. Fair-housing law prohibits discrimination because of a protected characteristic, retaliation and bad-faith pressure to vacate — not differences in rent between two tenancies.",
        ["FEHA", "Fair Housing Act", "§37.10B(a)(9)", "Documented reasons"],
    ),
    fh_body,
)

# --------------------------------------------------------------------------- review
review_rows_html = []
for r in DATA["review_rows"]:
    review_rows_html.append([
        '<span class="mono">{}</span>'.format(r["n"]),
        "<strong>{}</strong>".format(esc(r["test"])),
        esc(r["evidence"]),
        status_badge(r["result"]) if r["result"] in STATUS_BADGE else badge("calc", r["result"]),
        src_links(r["sources"]),
    ])
review_table = table(["#", "What a tenant-side lawyer checks", "Evidence needed", "Where this file stands", "Source"], review_rows_html,
                     caption="Twelve checks. Seven can be answered from this file; five need documents only you hold.", cls="data-table")

review_body = """
<section>
  <h2>The test, run honestly<span class="sub">A tenant lawyer's first question is procedural, not arithmetic.</span></h2>
  <p>Tenant-side review in San Francisco follows a predictable order: does the owner hold the licence, is the unit covered, is the percentage right, was the notice conforming and timely, and is there any sign of retaliation or discrimination. Most successful challenges fail an increase on the first or fourth question, which is why they are worth checking before the notice is served rather than after.</p>
  {review_table}
</section>

<section>
  <h2>Where this file stands right now<span class="sub">Six pass, five need evidence, one is conditional.</span></h2>
  <div class="grid-2">
    <div class="cardlink"><strong>Passes on the documents</strong><span>Rate in force, additive arithmetic, no rounding, no compounding, 12-month spacing on both units, and the notice design relative to the licence.</span></div>
    <div class="cardlink"><strong>Needs evidence before service</strong><span>Coverage record, licence status, base-rent composition, notice draft, and 180-day complaint history.</span></div>
    <div class="cardlink"><strong>Conditional</strong><span>Unit 1's banked 1.4% depends on the banking test in <a href="@@/hub/flags.html#H-01">H-01</a>. Serving 1.6% only removes the question entirely.</span></div>
    <div class="cardlink"><strong>Unverified by design</strong><span>Anything that requires the Rent Board Portal or your own ledger. Those values are blank on <a href="flags.html">Flagged for Review</a>, not guessed.</span></div>
  </div>
</section>

<section>
  <h2>What a tenant can do, at no cost<span class="sub">This is not a threat model; it is the reason the procedural steps matter.</span></h2>
  <ul>
    <li><strong>Check the licence.</strong> Tenants can search the Rent Board Portal for the landlord's licence status. {s03}</li>
    <li><strong>Petition without a lawyer.</strong> &ldquo;You do not need a lawyer to file a petition at the Rent Board.&rdquo; {s19}</li>
    <li><strong>Get free representation in 94122.</strong> The Board's referral listing includes Open Door Legal, Sunset office, 1722 Irving Street, plus the Housing Rights Committee, the Tenants Union and Bay Area Legal Aid. {s19}</li>
    <li><strong>Call the Board for a free check of the arithmetic.</strong> 415-252-4600, weekdays. {s18}</li>
  </ul>
  <p class="small">An increase that survives this page is one where every question has a document behind it. That is achievable here: the arithmetic is right, and the remaining five items are records rather than judgement calls.</p>
</section>
""".format(review_table=review_table, s03=src_links(["S03"]), s19=src_links(["S19"]), s18=src_links(["S18"]))

review_html = page(
    "hub/review.html",
    "Tenant-lawyer review test — SF Rent Increase Compliance",
    "The twelve checks a San Francisco tenant-side lawyer would run against a rent increase, the evidence each requires, and where these two units currently stand.",
    hero_block(
        "Question 6 of 6 · withstanding scrutiny",
        "Would a San Francisco tenant lawyer find a defect?",
        "Run the review before the notice goes out. Seven checks pass on the documents in this file; five need records only you hold; one is conditional on the banking question.",
        ["12 checks", "Licence first", "Then notice", "Then arithmetic"],
    ),
    review_body,
)

# --------------------------------------------------------------------------- flags
flag_rows = []
for f in DATA["flags"]:
    sev = f["severity"]
    cls = {"high": "high", "medium": "flag", "low": "unv"}[sev]
    flag_rows.append([
        '<span class="mono" id="{}">{}</span>'.format(f["id"], f["id"]),
        badge(cls, sev.upper()),
        "<strong>{}</strong>".format(esc(f["item"])),
        esc(f["detail"]) + '<br><span class="small"><strong>Effect:</strong> ' + esc(f["effect"]) + "</span>",
        src_links(f["sources"]),
        esc(f["action"]),
    ])
flag_table = table(["ID", "Severity", "Item", "Detail and effect", "Official source", "Action for reviewer"], flag_rows,
                   caption="Sixteen items. A flag does not make a figure wrong; it marks where the record is incomplete or the official text conflicts.", cls="data-table")

flags_body = """
<section>
  <h2>Flagged for Review<span class="sub">Published so you can review after the site is live. None of these blocks publication; several change a number if resolved the other way.</span></h2>
  <p>Three severities. <strong>High</strong> items can change an amount or make an increase unenforceable. <strong>Medium</strong> items affect documentation or the calendar. <strong>Low</strong> items are judgement calls or repository defects. Every row links to the official source it concerns, and where an official value is missing the value is left blank elsewhere on the site rather than inferred.</p>
  <div class="callout">
    <p><strong>Read H-01 first.</strong> Two official Rent Board publications describe different banking look-back tests — 24 months on the &ldquo;Banked rent increases&rdquo; page, 12 months in Rule 4.12(a) and in the worked examples on &ldquo;Learn about rent increases&rdquo;. The Unit 1 figure of {u1_total} includes a 1.4% banked portion that depends on which reading applies; the figure that does not depend on it is {u1_annual}.</p>
  </div>
  {flag_table}
</section>

<section>
  <h2>Values deliberately left blank<span class="sub">No official source, no number.</span></h2>
  <div class="tablewrap"><table>
  <caption>These are the only categories of unverified value on this site.</caption>
  <thead><tr><th scope="col">Value</th><th scope="col">Why blank</th><th scope="col">What would verify it</th></tr></thead>
  <tbody>
    <tr><td>Licence status, both units</td><td>Held in the Rent Board Portal, which this session cannot access.</td><td>A dated screenshot of the Portal licence record.</td></tr>
    <tr><td>Certificate of occupancy / coverage</td><td>Year built supplied by the owner, not checked against City records.</td><td>City Property Information Map printout, or a Rent Board counselor's confirmation.</td></tr>
    <tr><td>Rent ledger, both units</td><td>Owner statement only.</td><td>Leases, notices and bank records since 2019 / 2025.</td></tr>
    <tr><td>Market &ldquo;normal&rdquo; increase for 94122</td><td>No official figure exists for covered units; commercial data is not official.</td><td>Nothing official — this value should stay blank.</td></tr>
    <tr><td>2027-28 allowance</td><td>Set on 1 March 2027.</td><td>Form 571 for 2027-28, once published.</td></tr>
    <tr><td>Corporation vs individual behaviour data</td><td>No official dataset.</td><td>Nothing official — rely on the rules, not the averages.</td></tr>
  </tbody></table></div>
</section>
""".format(flag_table=flag_table, u1_total=money(N["U1"]["total_amt"]), u1_annual=money(N["U1"]["annual_amt"]))

flags_html = page(
    "hub/flags.html",
    "Flagged for Review — SF Rent Increase Compliance",
    "Sixteen flagged items: conflicting official Rent Board text on banking, unverified private records left blank, and repository defects, each with its official source link.",
    hero_block(
        "Flagged for Review · 16 items",
        "Where the record is incomplete, and where the official text conflicts",
        "Published with source links so you can review and request changes after the site is live. High-severity items can change an amount; they are listed first.",
        ["3 high", "5 medium", "8 low / repository"],
    ),
    flags_body,
)

# --------------------------------------------------------------------------- sources
src_rows = []
for s in DATA["sources"]:
    src_rows.append([
        '<span class="mono" id="{}">{}</span>'.format(s["id"], s["id"]),
        "<strong><a href=\"{}\" rel=\"noopener noreferrer\">{}</a></strong><br><span class=\"small\">{} · {}</span>".format(
            esc(s["url"]), esc(s["title"]), esc(s["publisher"]), esc(s["level"])),
        "&ldquo;{}&rdquo;".format(esc(s["quote"])),
        esc(s["used_for"]),
    ])
src_table = table(["ID", "Source", "Verbatim quote used", "Used for"], src_rows,
                  caption="All nineteen sources were fetched and read on 7 November 2026. The quote column holds the sentence the claim rests on.", cls="source-table")

sources_body = """
<section>
  <h2>Source registry<span class="sub">Nineteen official sources. No commercial or secondary source is used for any value on this site.</span></h2>
  <p>Every table row on every page links to one of these nineteen sources. The rule applied throughout was: if a value could not be confirmed from an official source it was left blank and flagged, rather than inferred from a secondary summary. Where two official sources disagree — as they do on the banking look-back — both are cited and the conflict is published (H-01).</p>
  {src_table}
</section>

<section>
  <h2>Publisher coverage<span class="sub">City, state and federal.</span></h2>
  <dl class="kv">
    <dt>San Francisco Rent Board / SF.gov</dt><dd>13 sources: the enacted ordinance (§§37.3, 37.10B, 37.10C, 37.15), the adopted Rules Part IV, and the Board's own guidance pages, forms and referral listing.</dd>
    <dt>California Legislative Information</dt><dd>5 statutes: Civil Code §§827, 1942.5, 1947.12, 1954.53 and Government Code §12955 — the official text of each section.</dd>
    <dt>U.S. Department of Housing and Urban Development</dt><dd>1 source: the Fair Housing Act overview, for the federal protected classes and the complaint route.</dd>
  </dl>
  <p class="small">The federal statute behind the HUD page, 42 U.S.C. §3604, was cited in an earlier edition through the Office of Law Revision Counsel site; that URL returned &ldquo;Page Not Found&rdquo; when checked on 7 November 2026, so this edition cites the HUD overview page, which was fetched and reads as quoted. The broken link is repaired in the repository and logged as H-14.</p>
</section>

<section>
  <h2>How to check any row yourself<span class="sub">Four steps, no subscription.</span></h2>
  <ol>
    <li>Open the source link on the row you are checking.</li>
    <li>Search the page for the quoted sentence in the third column above.</li>
    <li>For an amount, multiply the base rent by the published percentage — additive, never compounded, never rounded up.</li>
    <li>For a date, subtract the statutory notice period (and five more days if mailing) from the intended effective date.</li>
  </ol>
  <p class="small">The Rent Board's free counseling line is 415-252-4600, weekdays; it will check a rate or a notice over the phone and cannot give legal advice. {s18}</p>
</section>
""".format(src_table=src_table, s18=src_links(["S18"]))

sources_html = page(
    "hub/sources.html",
    "Sources — SF Rent Increase Compliance",
    "The nineteen official San Francisco, California and federal sources behind every figure, with the verbatim sentence each claim rests on and the date fetched.",
    hero_block(
        "Verification · 19 official sources",
        "Every claim, traced to the sentence it came from",
        "City ordinance and agency guidance, California statutes, and federal fair-housing material. Each source was fetched on 7 November 2026; the quote column holds the exact sentence used.",
        ["13 SF Rent Board", "5 California statutes", "1 federal agency"],
    ),
    sources_body,
)

# --------------------------------------------------------------------------- write
PAGES = {
    "index.html": index_html,
    "hub/licensing.html": licensing_html,
    "hub/limits.html": limits_html,
    "hub/notice.html": notice_html,
    "hub/practice.html": practice_html,
    "hub/fair-housing.html": fair_housing_html,
    "hub/review.html": review_html,
    "hub/flags.html": flags_html,
    "hub/sources.html": sources_html,
}

for rel, content in PAGES.items():
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)

print("wrote {} pages: {}".format(len(PAGES), ", ".join(sorted(PAGES))))
print("U1 annual {0} / total {1} -> {2} / {3}".format(money(u1["annual_amt"]), money(u1["total_amt"]), money(u1["annual_rent"]), money(u1["total_rent"])))
print("U2 annual {0} / total {1} -> {2} / {3}".format(money(u2["annual_amt"]), money(u2["total_amt"]), money(u2["annual_rent"]), money(u2["total_rent"])))
