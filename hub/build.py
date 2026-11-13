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
    """Always one decimal place, matching the Rent Board's own form (1.6%, 4.0%, 13.1%)."""
    return "{}%".format(Decimal(str(value)).quantize(Decimal("0.1")))


def d(s: str) -> date:
    return date.fromisoformat(s)


def longdate(s: str) -> str:
    x = d(s)
    return "{} {} {}".format(x.day, x.strftime("%B"), x.year)


def ref_links(ids, page="@@/hub/sources.html") -> str:
    out = []
    for i in ids:
        if i.startswith("H"):
            out.append('<a href="{0}#{1}" title="Flag {1}">{1}</a>'.format(page, i))
        else:
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
    ("@@/hub/suggestions.html", "Suggestions"),
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
    <p><strong>Registry verified {retrieved}.</strong> All {source_count} registered official sources were fetched and read from their official publishers on the retrieval date recorded for each one in the source table (7&ndash;13 November 2026; the load-bearing subset was re-read live on {retrieved}). Dollar results are conditional scenario arithmetic using owner-brief inputs, not certified lawful maxima. Unsupported official-confirmation cells are blank and listed on <a href="@@/hub/flags.html">Flagged for Review</a>.</p>
    <p><strong>Not legal advice.</strong> San Francisco Rent Board counseling is free on 415-252-4600; confirm the licence status, the current rate and any notice before serving it.</p>
  </div>
</footer>
</body>
</html>
""".format(title=esc(title), desc=esc(description), nav=nav_html(current), hero=hero,
           body=body, retrieved=DATA["meta"]["retrieved"], source_count=len(DATA["sources"]))
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
  <h2>Start here — the individual-owner Rent Board answer<span class="sub">The legal gate is licensure on the effective date. The safer operating sequence is to finish reporting before serving notice.</span></h2>
  <div class="answer">
    <h3>Yes. Each tenant-occupied unit needs a current Rent Increase License before an annual or banked increase takes effect — even when the owner is one individual with no corporation.</h3>
    <p>San Francisco Administrative Code §37.15 contains no individual-owner or two-unit exemption. Report each unit through the annual <strong>Housing Inventory</strong>; after substantial reporting compliance, the Rent Board automatically generates the unit's license. Reporting is free. There is <strong>no separate per-increase approval application</strong>, and an ordinary annual/banked notice goes to the tenant, not to the Rent Board.</p>
    <p><strong>Timing, precisely:</strong> the official hard cutoff is a current license on the increase's <strong>effective date</strong>, not necessarily the day the notice is served. Best practice is to complete/update reporting and confirm the license <em>before</em> serving notice so a correctable omission does not become an unenforceable increase. Late reporting is allowed, but restoration is prospective; the tenant does not owe the increase for unlicensed suspension months. The license does not have to be attached to the notice.</p>
    <p><strong>Two different City registrations are often confused — only one gates the rent increase.</strong> The <strong>Rent Increase License</strong> comes from the Rent Board's Housing Inventory and is what makes an annual or banked increase enforceable. A <strong>Business Registration Certificate</strong> comes from the Office of the Treasurer &amp; Tax Collector, is a general business-tax registration, and does not affect the lawfulness of a rent increase. On the reported two units in one building, the Tax Collector's own guidance points to <em>no</em> business registration: rental income from "one residential structure consisting of fewer than four units" is not, "by reason of that fact alone", required to register. That carve-out is conditional — other San Francisco business activity, payroll expense, or short-term rental income can trigger it — so it is published as a conditional determination {s24} {s25} and logged as {h21}, not as a settled fact.</p>
    <p><strong>2027 Rent Board Fee exemption vs Housing Inventory:</strong> the 2027 Informational Notice sets <strong>Monday, 14 December 2026</strong> as the Request for Exemption deadline for the 2027 Rent Board Fee and <strong>1 March 2027</strong> for both annual Housing Inventory reporting and the 2027 Fee bill. Requesting a fee exemption does not satisfy Housing Inventory reporting, and reporting does not satisfy a fee-exemption request {s17} {s32}.</p>
    <p><strong>Use this order:</strong> confirm coverage and lease terms → reconcile the full rent ledger → submit/update the Housing Inventory and confirm both licenses → calculate the amount → serve a conforming written notice → verify the license remains current on the effective date and retain proof. <a href="@@/hub/licensing.html">Full step-by-step answer and official links →</a></p>
    <p><strong>Privacy before reporting:</strong> the City's Housing Inventory submission is public. It can include the unit mailing address, owner or designated manager name and business contact, occupancy information, unit characteristics, and rent reported in $250 increments. Do not assume those details stay private in the City portal. This public research site publishes no tenant names, initials, street address, or contact details. Review the City's <a href="https://www.sf.gov/rent-board-housing-inventory">Housing Inventory disclosure</a> and <a href="https://www.sf.gov/information/sec-3715-reporting-obligations-licensing">§37.15 reporting requirements</a> before submitting.</p>
    <p><strong>Before any large banked catch-up:</strong> Board of Supervisors File #261020 would cap combined banked and capital-improvement increases at 10% per year of the lowest base rent in effect during the preceding 12 months through 31 December 2029 (carryover on/after 1 January 2030), and would add banked-increase reporting to §37.15(b)(2)(F). On 10 November 2026 Legistar showed <strong>Pending Committee Action — not law</strong> {s26} (re-checked 13 November 2026: unchanged — still Pending Committee Action, no final action, no enactment date). On 9 November 2026 the Rent Board posted a formal notice warning that, if enacted as currently proposed, the 10% cap would apply to banked increases <strong>noticed on or after 15 September 2026</strong> {s04} {s05}. Unit 2’s illustrative banked portion alone is 11.5%; do not rely on this scenario to serve notice. Re-check the proposal and seek advice. Logged as {h22}.</p>
  </div>
  <div class="callout red"><p><strong>Privacy alert:</strong> The current site uses placeholders, but earlier public Git history contains tenant initials. Current-file scans do not remove or check historical copies. See <a href="@@/hub/flags.html#history-privacy">the privacy review flag</a>.</p></div>
  <div class="callout red">
    <p><strong>Do not serve notice from these illustrations alone.</strong> Unit 1's April 2026 fixed-term/month-to-month status, Unit 2's current base rent, both ledgers, both licenses, and official coverage are unresolved. The dollar amounts below preserve the supplied figures and show reproducible arithmetic; they are not permission to impose an increase.</p>
  </div>
</section>

<div class="kpis">
  <div class="kpi accent">
    <div class="label">Published annual allowance</div>
    <div class="value">1.6%<small> / year</small></div>
    <div class="note">Only for increases effective 1 Mar 2026 – 28 Feb 2027. Source: SF Rent Board Form 571. <a href="@@/hub/limits.html">Rates and conditions →</a></div>
  </div>
  <div class="kpi">
    <div class="label">Unit 1 — annual-only illustration</div>
    <div class="value">{u1_annual}<small> / mo</small></div>
    <div class="note">1.6% on reported {u1_base} → {u1_annual_rent}, scenario date {u1_eff}. The 3.0% scenario adds {u1_banked}; both require lease, ledger, license, and timing review.</div>
  </div>
  <div class="kpi">
    <div class="label">Unit 2 — annual-only illustration</div>
    <div class="value">{u2_annual}<small> / mo</small></div>
    <div class="note">1.6% on the 2019 lease-start amount {u2_base}. Current base, history, timing, and license are unverified. A separate 13.1% combined scenario ({u2_total} → {u2_total_rent}) is not a recommendation and must not be used to serve notice.</div>
  </div>
  <div class="kpi warn">
    <div class="label">Illustrative 90-day date</div>
    <div class="value">{u2_serve}</div>
    <div class="note">Personal-service arithmetic for a 28 Feb 2027 scenario; California-mail arithmetic is {u2_mail}. Serve earlier and resolve all flags first.</div>
  </div>
</div>

<section>
  <h2>What is on this dashboard<span class="sub">Nine category pages plus an independent assurance record. Every claim-table row links to official material or an explicit flag.</span></h2>
  <div class="grid-2">
    <a class="cardlink" href="@@/hub/licensing.html"><strong>Licence &amp; the Rent Board</strong><span>Individual-owner duty, automatic license generation, late reporting, the effective-date gate, and the correct notice sequence.</span></a>
    <a class="cardlink" href="@@/hub/limits.html"><strong>Limits &amp; amounts</strong><span>Local/state/federal layers, the complete Form 571 table, and conditional calculations for both units.</span></a>
    <a class="cardlink" href="@@/hub/notice.html"><strong>Notice &amp; reasons</strong><span>Written contents, personal/mail timing, defensible bases, and a scenario-only drafting aid.</span></a>
    <a class="cardlink" href="@@/hub/practice.html"><strong>Owner practice</strong><span>Owner-neutral duties, an accurately labeled DOJ enforcement example, and practices not established by official data.</span></a>
    <a class="cardlink" href="@@/hub/fair-housing.html"><strong>One unit or both</strong><span>Why different treatment is not automatically discrimination—and why identical treatment is not immunity.</span></a>
    <a class="cardlink" href="@@/hub/review.html"><strong>Tenant-lawyer test</strong><span>{n} review checks covering license, lease, ledger, repairs, retaliation, occupant status, notice, and neutral selection.</span></a>
    <a class="cardlink" href="@@/hub/flags.html"><strong>Flagged for Review</strong><span>{flag_count} unresolved facts, source irregularities, and explicit blanks.</span></a>
    <a class="cardlink" href="@@/hub/sources.html"><strong>Sources</strong><span>{source_count} official sources with verbatim supporting passages and retrieval dates.</span></a>
    <a class="cardlink" href="assurance/index.html"><strong>Independent assurance</strong><span>What the final audit changed, what was recomputed, and which risks remain open.</span></a>
    <a class="cardlink" href="hub/suggestions.html"><strong>Suggestions &amp; missing information</strong><span>Review-before-implement decision paths, decisions not yet supported, and how to discover what is still unknown.</span></a>
  </div>
</section>

<section>
  <h2>The two units at a glance<span class="sub">Placeholders only; supplied dates and amounts preserved. “Scenario” is not a verified current-legal-rent label.</span></h2>
  {unit_table}
  <p class="small"><strong>Badges.</strong> {b_ok} official rule/rate · {b_calc} reproducible arithmetic · {b_flag} missing evidence or source caution · {b_unv} unsupported official-confirmation value left blank.</p>
</section>

<section>
  <h2>Every question, answered without filling gaps<span class="sub">Each row points to the detailed source-linked table.</span></h2>
  {q_table}
</section>

<section>
<section>
  <h2>State or local law — the 2023 question<span class="sub">Is there a 2023 law requiring Rent Board notification of rent increases?</span></h2>
  <div class="answer">
    <p><strong>It is local San Francisco law — not state law — and it is an annual report, not a per-increase filing.</strong></p>
    <p>The San Francisco Rent Ordinance (Chapter 37 of the San Francisco Administrative Code) requires owners of units subject to Chapter 37 to report information about each unit to the Rent Board on the Housing Inventory form, and a landlord must have a current rent increase license on file before any annual or banked rent increase goes into effect. For units in buildings with fewer than 10 units — including this reported two-unit building — reporting commenced March 1, 2023 and is updated annually by March 1 {s36} {s01} {s03}.</p>
    <p>California has no statewide rent board, and no California statute requires a landlord to notify or file with a rent board before raising rent. SB 567 (Durazo, chaptered September 30, 2023) amends Civil Code sections 1946.2 and 1947.12 — the just-cause termination and rent-cap provisions — including a duty to notify tenants of those rights, and it expressly does not preempt local rent control {s35}. The state notice rule (Civil Code section 827) requires written notice to the tenant — 30 days at 10 percent or less, 90 days above 10 percent — plus five calendar days for California mail: notice to the tenant, not a filing with any board {s08} {s21}.</p>
    <p><strong>What this means for these units:</strong> there is no Rent Board application for approval of an ordinary annual or banked increase, no per-increase notice to the Board, and no state rent increase licence. The steps are: report or update the Housing Inventory each year by March 1; hold a current licence when the increase takes effect (generated after reporting, free); then serve a conforming written notice to the tenant {s03} {s01} {s05}. Coverage, current licences, ledgers, and lease status remain blank and flagged — see <a href="@@/hub/flags.html">Flagged for Review</a>.</p>
    <p class="small"><strong>Scope limits:</strong> this answers the state-versus-local question only. It does not confirm coverage, current licences, ledgers, or lease status — those remain blank and flagged (H-02, H-04, H-05, H-17, H-18).</p>
  </div>
</section>
  <h2>Official confirmations deliberately blank<span class="sub">Owner-brief inputs remain visible as scenario inputs; these official-confirmation cells are not inferred.</span></h2>
  <div class="tablewrap"><table class="data-table">
  <caption>Blank means not independently confirmed, not zero and not “verified.”</caption>
  <thead><tr><th scope="col">Official-confirmation value</th><th scope="col">Confirmed value</th><th scope="col">Why blank</th><th scope="col">Source / flag</th></tr></thead>
  <tbody>
    <tr><td>Current Rent Increase License for each unit</td><td></td><td>Private Rent Board Portal status was not available.</td><td><a href="@@/hub/flags.html#H-04">H-04</a> {s03}</td></tr>
    <tr><td>Certificate of occupancy and exemption check</td><td></td><td>The brief reports a 1940 two-unit rent-controlled building; no parcel record was supplied.</td><td><a href="@@/hub/flags.html#H-05">H-05</a> {s18}</td></tr>
    <tr><td>Unit 1 fixed-term/month-to-month and escalation terms</td><td></td><td>The April 2026 instrument was not supplied.</td><td><a href="@@/hub/flags.html#H-17">H-17</a> {s20}</td></tr>
    <tr><td>Unit 2 current base rent and no-prior-increase history</td><td></td><td>$3,150.00 is supplied only as the 2019 lease-start rent.</td><td><a href="@@/hub/flags.html#H-18">H-18</a>, <a href="@@/hub/flags.html#H-03">H-03</a> {s05}</td></tr>
    <tr><td>2027–28 SF annual allowance</td><td></td><td>Not published as of the verification date.</td><td><a href="@@/hub/flags.html#H-08">H-08</a> {s06}</td></tr>
    <tr><td>Official 94122 “normal” market increase</td><td></td><td>No official ZIP-specific value was located; commercial listings were not substituted.</td><td><a href="@@/hub/flags.html#H-10">H-10</a> {s05}</td></tr>
    <tr><td>Official SF behavior rates by owner type</td><td></td><td>No official comparative dataset was located.</td><td><a href="@@/hub/flags.html#H-11">H-11</a> {s22}</td></tr>
  </tbody></table></div>
</section>

<section>
  <h2>Archived prior work — superseded<span class="sub">Retained for provenance, not re-certified line by line. The corrected root/hub edition and its assurance report are canonical.</span></h2>
  <div class="callout"><p><strong>Do not rely on an older edition where it conflicts with this dashboard.</strong> These links preserve other sessions' work as requested; they are not equally current guidance. Known legacy issues include overconfident “lawful maximum,” notice-void, retaliation, and current-base statements.</p></div>
  <div class="grid-2">
    <a class="cardlink" href="integration/index.html"><strong>Integration edition — archive</strong><span>Six-page parallel edition. Preserved; not the canonical corrected edition.</span></a>
    <a class="cardlink" href="docs/index.html"><strong>Main edition — archive</strong><span>Ten-page earlier narrative. Preserved; contains identified overstatements.</span></a>
    <a class="cardlink" href="docs/v2/index.html"><strong>Companion edition — archive</strong><span>Generated companion with its own matrix and reconciliation.</span></a>
    <a class="cardlink" href="dashboard/index.html"><strong>Verification dashboard — archive</strong><span>Independent earlier build and source registry.</span></a>
    <a class="cardlink" href="portal/index.html"><strong>Compliance portal — archive</strong><span>Earlier category portal and repository audit.</span></a>
    <a class="cardlink" href="review/index.html"><strong>Executive-summary edition — archive</strong><span>Eleven-page parallel /review/ build. Preserved after its merge; not the canonical root.</span></a>
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
        ref_links(["S05", "S06"] if key == "U2" else ["S05", "S06", "S20"]),
    ])

unit_table = table(
    ["Unit", ("Scenario input rent", "num"), "Lease start", "Annual-only arithmetic", "Combined scenario", ("Illustrative new rent", "num"), "Official basis"],
    index_unit_rows,
    caption="Unit 2's $3,150.00 is a lease-start input, not confirmed current rent. All new-rent cells are conditional arithmetic on the Limits page.",
    cls="data-table",
)

q_rows = [
    ["Must an individual owner inform the Rent Board and obtain a license before notifying tenants?", "Each unit needs a current license on the increase's effective date; complete reporting before notice as the safer sequence. No separate per-increase approval or notice filing is required for ordinary annual/banked increases.", '<a href="@@/hub/licensing.html">Licence &amp; Board</a>', ref_links(["S01", "S03", "S04"])],
    ["What is reasonable and normal under local, state, and federal law?", "The routine local scenario is the published 1.6% annual allowance. Properly proven banked amounts are separate. The 8.8% state cap does not apply to these locally controlled units; federal fair-housing rules still apply. No official ZIP-specific market norm was located.", '<a href="@@/hub/limits.html">Limits &amp; amounts</a>', ref_links(["S05", "S09", "S10", "S14", "S33"])],
    ["How do corporate and individual owners handle increases?", "The same SF duties apply. A DOJ enforcement example documents allegations about portfolio-scale pricing tools, not universal corporate behavior; no official SF behavior-by-owner-type dataset was located.", '<a href="@@/hub/practice.html">Owner practice</a>', ref_links(["S02", "S16", "S22"])],
    ["How should tenants be told, and what reasons are defensible?", "Use written notice under Civil Code §827 with dollar amount, percentage, effective date, and annual/banked details; add five calendar days for California mail. Use the published allowance or proven banked basis, not retaliation or a roommate surcharge.", '<a href="@@/hub/notice.html">Notice &amp; reasons</a>', ref_links(["S08", "S21", "S02"])],
    ["Would the notice withstand tenant-side scrutiny?", "Not yet established. {} checks remain, including the fixed-term instrument, current base, ledgers, licenses, repairs, retaliation, occupant status, service evidence, and the pending banked-increase proposal. Arithmetic alone is not a legal clearance.".format(len(DATA["review_rows"])), '<a href="@@/hub/review.html">Lawyer test</a>', ref_links(["S20", "S03", "S23"])],
    ["Does raising one or both units create discrimination risk?", "Raising one is not automatically discrimination; selecting by protected characteristic or retaliating can be unlawful. Identical increases are not a safe harbour, and an ineligible unit should never be raised merely for symmetry.", '<a href="@@/hub/fair-housing.html">One unit or both</a>', ref_links(["S13", "S14", "S15"])],
    ["Does Unit 1's April 2026 occupant change allow a market-rate reset?", "No, on the reported facts. One original occupant remained, and both reset routes are keyed to the last original occupant leaving. Whether a §6.14 notice was served, and whether the incoming occupant is a co-tenant or a subtenant, are open private facts.", '<a href="@@/hub/limits.html">Limits &amp; amounts</a>', ref_links(["S27", "S28", "S29"])],
    ["What is still unverified?", "{} flags, led by Unit 1 lease status, Unit 2 current base and history, both licenses, and official coverage. Unsupported confirmation cells are blank.".format(len(DATA["flags"])), '<a href="@@/hub/flags.html">Flagged for Review</a>', ref_links(["S20", "S04", "S03"])],
]
q_table = table(["Question", "Short answer", "Detail", "Source"], q_rows, cls="data-table")

index_html = page(
    "index.html",
    "SF Rent Increase Compliance Dashboard — Outer Sunset 94122",
    "Official-source dashboard on rent increases for two rent-controlled San Francisco units built in 1940: the Rent Board licence, the 1.6% allowance, banked increases, notice rules, and every figure traced to an official link.",
    hero_block(
        "Executive summary · live-verified {}".format(DATA["meta"]["retrieved"]),
        "Raising the rent on two 1940 flats in the Outer Sunset — what the Rent Board requires, and what the numbers actually are",
        "The brief reports a two-unit 1940 rent-controlled building. On that scope, local law supplies the annual allowance and state law supplies notice rules; official parcel coverage, private lease terms, ledgers, and licenses remain separately unverified.",
        ["ZIP 94122 · owner-brief facts", "Reported 1940 / rent-controlled", "1.6% to 28 Feb 2027", "{} official sources".format(len(DATA["sources"])), "Conditional calculations only"],
    ),
    index_body.format(
        u1_annual=money(u1["annual_amt"]), u1_base=money(u1["base"]), u1_annual_rent=money(u1["annual_rent"]),
        u1_banked=money(u1["banked_amt"]), u1_eff=longdate(DATA["calculations"]["U1"]["annual_effective"]),
        u2_annual=money(u2["annual_amt"]), u2_total=money(u2["total_amt"]), u2_base=money(u2["base"]), u2_total_rent=money(u2["total_rent"]),
        u2_serve=longdate(N["U2"]["serve_by"].isoformat()), u2_mail=longdate(N["U2"]["mail_by"].isoformat()),
        unit_table=unit_table, q_table=q_table,
        flag_count=len(DATA["flags"]), source_count=len(DATA["sources"]),
        n=len(DATA["review_rows"]),
        s03=ref_links(["S03"]), s04=ref_links(["S04"]), s05=ref_links(["S05"]), s06=ref_links(["S06"]),
        s18=ref_links(["S18"]), s20=ref_links(["S20"]), s22=ref_links(["S22"]),
        s24=ref_links(["S24"]), s25=ref_links(["S25"]), s26=ref_links(["S26"]),
        s17=ref_links(["S17"]), s32=ref_links(["S32"]),
        s01=ref_links(["S01"]), s08=ref_links(["S08"]), s21=ref_links(["S21"]), s35=ref_links(["S35"]), s36=ref_links(["S36"]),
        h21='<a href="@@/hub/flags.html#H-21">H-21</a>', h22='<a href="@@/hub/flags.html#H-22">H-22</a>',
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
        ref_links(step["sources"]),
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
        ref_links(s["sources"]),
    ])
proc_table = table(["Step", "Action", "What to do, and why", "Status", "Source"], proc_rows,
                   caption="The compliance sequence, in order. Steps 1 and 2 decide whether the rest is usable.", cls="data-table")

challenge_rows = [
    ["No current license on the effective date", "Authority is suspended; the tenant need not pay the increase for suspension months. Restoration is prospective.", ref_links(["S01", "S03"])],
    ["Annual/banked itemisation or banked dates omitted", "Include them. Section 37.3(b)(5) states a null-and-void rule, but Rule 4.10(b) has an amount-based exception and Rule 4.12(b) expressly says banked-date omission does not itself void the increase.", ref_links(["S02", "S07"])],
    ["Wrong rate for the effective period, compounding, or rounding up", "The calculation exceeds the published allowance; use Form 571 and additive arithmetic.", ref_links(["S05", "S06", "S07"])],
    ["Increase during a fixed term without an agreement permitting it", "Official state guidance says the rent cannot be increased during the fixed term; review Unit 1's April 2026 instrument.", ref_links(["S20"])],
    ["Short personal/mail notice", "Use 30 days at ≤10%, 90 days above 10%, and five extra calendar days for California mail; longer mail extensions can apply elsewhere.", ref_links(["S08", "S21"])],
    ["Protected activity or repairs in the history", "Section 1942.5 requires fact-specific retaliation analysis, not an automatic 180-day bar. A qualifying repair petition can defer an annual increase.", ref_links(["S12", "S23"])],
    ["Bad-faith pressure to vacate or protected-class selection", "Harassment and fair-housing exposure; parallel percentages do not cure motive.", ref_links(["S15", "S13", "S14"])],
    ["A rent increase solely because an occupant joined", "Prohibited even if a lease purports to allow it. Any separate cost petition is not established by this record.", ref_links(["S02", "S05"])],
]
challenge_table = table(["What a tenant or advocate would challenge", "Consequence", "Source"], challenge_rows, cls="data-table")

not_licence_rows = [
    ["A fee", "The licence is free: &ldquo;Reporting is free and can be done online 24/7&rdquo;.", ref_links(["S03"])],
    ["Approval of the percentage", "Banked increases &ldquo;do not have to be approved by the Rent Board&rdquo;; the allowance is published by the Board for everyone.", ref_links(["S04", "S05"])],
    ["A copy of the notice sent to the Board", "No such filing appears in §37.3 (what the tenant must be told) or §37.15 (what the Board must be told).", ref_links(["S02", "S01"])],
    ["The same thing as the annual Rent Board fee", "$59.00 per dwelling unit for 2026-2027, due 1 March unless exempt. After full payment, 50% may be recoverable only from tenants in occupancy on the applicable November 1; penalties are not recoverable. Keep any recovery separate from base rent.", ref_links(["S17", "S03"])],
    ["Attached to the notice", "&ldquo;The rent increase license does not need to be included with your rent increase notice.&rdquo;", ref_links(["S03"])],
]
not_licence_table = table(["The licence is not…", "What the official text says", "Source"], not_licence_rows, cls="data-table")

licensing_body = """
<section>
  <h2>The short answer<span class="sub">§37.15 and current Housing Inventory guidance, read together.</span></h2>
  <div class="answer">
    <h3>Yes — an individual owner needs a current license for each tenant-occupied unit. No — the Rent Board does not pre-approve each annual or banked increase.</h3>
    <p>The reporting duty applies to owners of units subject to Chapter 37, including buildings with fewer than 10 units. Corporate form is irrelevant. Once the owner substantially complies with reporting, a license is automatically generated for a non-owner-occupied unit. It is free and need not be attached to the tenant notice.</p>
    <p><strong>Before notice or before effectiveness?</strong> The official rule is that a current license must be on file when the annual/banked increase goes into effect. Completing the inventory and confirming the license before serving notice is the recommended risk-control sequence, not a claim that the statute always makes pre-notice licensure the hard cutoff. Late submission is possible, but an increase is unenforceable for the unlicensed period and restoration is prospective.</p>
  </div>
  <div class="callout">
    <p><strong>Ordinary annual/banked route:</strong> report/update inventory → confirm license → verify lease and ledger → calculate → serve the tenant with a conforming notice → confirm licensure on the effective date. Do not send an ordinary annual/banked notice to the Board as an approval request. Separate petition-based increases have different procedures.</p>
  </div>
  <div class="callout red" role="note" aria-label="Housing Inventory privacy warning">
    <p><strong>Privacy warning before you submit:</strong> SF.gov says Housing Inventory information is public. The required submission can include the unit mailing address, the owner's or designated manager's name and business contact information, occupancy dates, unit details, and the base rent reported in $250 increments. Do not assume those details will remain confidential in the City portal. This public research site does not publish tenant names, initials, street address, or contact details. Review the City's <a href="https://www.sf.gov/rent-board-housing-inventory">Housing Inventory disclosure</a> and <a href="https://www.sf.gov/information/sec-3715-reporting-obligations-licensing">§37.15 reporting requirements</a> before submitting.</p>
  </div>
</section>
<section>
<section>
  <h2>State versus local — whose law?<span class="sub">Sec. 37.15 is San Francisco local law; the 2023 state law creates no Rent Board filing duty.</span></h2>
  <div class="answer">
    <p><strong>The duty is local, not state.</strong> The San Francisco Rent Ordinance is Chapter 37 of the San Francisco Administrative Code {s36}. Section 37.15 requires owners of units subject to Chapter 37 to report information about each unit to the Rent Board on the Housing Inventory form, and a landlord must have a current rent increase license on file before any annual or banked rent increase goes into effect. For units in buildings with fewer than 10 units — including this reported two-unit building — reporting commenced March 1, 2023 and is updated annually by March 1 {s36} {s01} {s03}.</p>
    <p>California has no statewide rent board, and no California statute requires a landlord to notify or file with a rent board before raising rent. SB 567 (Durazo, chaptered September 30, 2023) amends Civil Code sections 1946.2 and 1947.12 — the just-cause termination and rent-cap provisions — including a duty to notify tenants of those rights, and it expressly does not preempt local rent control {s35}. The state notice rule (Civil Code section 827) requires written notice to the tenant — 30 days at 10 percent or less, 90 days above 10 percent — plus five calendar days for California mail: notice to the tenant, not a filing with any board {s08} {s21}.</p>
    <p><strong>What this means practically:</strong> there is no Rent Board application for approval of an ordinary annual or banked increase, no per-increase notice to the Board, and no state rent increase licence {s03} {s01} {s05}. Annual and banked increases do not have to be approved by the Rent Board {s04}. The compliance steps are: report or update the Housing Inventory each year by March 1; hold a current licence when the increase takes effect (generated after reporting, free); then serve a conforming written notice to the tenant.</p>
  </div>
</section>
  <h2>Question by question<span class="sub">Every answer has an official link; private license status remains blank.</span></h2>
  {lic_table}
</section>
<section>
  <h2>Do this in order<span class="sub">Steps 2 and 3 prevent the current dashboard's arithmetic from being mistaken for verified inputs.</span></h2>
  {proc_table}
  <p class="small">This is a conservative workflow. It does not convert owner-brief facts into official findings or replace advice on the actual lease.</p>
</section>
<section>
  <h2>What a tenant-side reviewer can challenge<span class="sub">Text-specific consequences, not categorical shortcuts.</span></h2>
  {challenge_table}
  <p class="small">A tenant does not need a lawyer to petition the Rent Board. The Board's referral list identifies legal-assistance resources, including a Sunset office, but does not guarantee free representation for every person or issue; eligibility and capacity must be confirmed (<a href="@@/hub/flags.html#H-20">H-20</a>). {s19}</p>
</section>
<section>
  <h2>What the license is not<span class="sub">Five common confusions, including the separate Rent Board Fee.</span></h2>
  {not_licence_table}
</section>
<section>
  <h2>What remains unknown for these units<span class="sub">The legal duty is verified; actual compliance is not.</span></h2>
  <ul>
    <li><strong>License status is blank.</strong> Check the Rent Board Portal before notice and again for the effective date. Note that pending BOS File #261020 (<em>Pending Committee Action — not law</em>) would also amend §37.15(b)(2)(F) to add Housing Inventory reporting of banked increases imposed in the prior 12 months. {s26} See <a href="@@/hub/flags.html#H-04">H-04</a>.</li>
    <li><strong>Reporting can be late.</strong> There is no monetary late-reporting penalty stated on the Housing Inventory page, but do not backdate or collect for an unlicensed period. {s03}</li>
    <li><strong>The annual fee is separate — watch the 14 December 2026 exemption deadline.</strong> For the 2027 Rent Board fee (due 1 March 2027), any Request for Exemption must be submitted by <strong>14 December 2026</strong>. Exemptions, payment, and 50% recovery conditions must be checked independently; do not fold a recovery into base rent, and requesting a fee exemption does not satisfy Housing Inventory reporting. {s17}</li>
    <li><strong>Separate City tax registration check (Q8–Q10 above).</strong> A Business Registration Certificate from the Treasurer &amp; Tax Collector is not a rent-increase license; on the reported two units in one building the sub-four-unit carve-out points to no registration unless other SF business activity, payroll expense, or short-term rentals trigger it. {s24} {s25} See <a href="@@/hub/flags.html#H-21">H-21</a>.</li>
  </ul>
</section>

""".format(lic_table=lic_table, proc_table=proc_table, challenge_table=challenge_table,
           not_licence_table=not_licence_table, s19=ref_links(["S19"]),
           s03=ref_links(["S03"]), s17=ref_links(["S17"]),
           s24=ref_links(["S24"]), s25=ref_links(["S25"]), s26=ref_links(["S26"]),
           s01=ref_links(["S01"]), s04=ref_links(["S04"]), s05=ref_links(["S05"]), s08=ref_links(["S08"]), s21=ref_links(["S21"]), s35=ref_links(["S35"]), s36=ref_links(["S36"]))

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
        ref_links(["S06"]),
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
            badge("flag", "Scenario — verify ledger") if b["conditional"] else badge("ok", "Banked"),
            ref_links(["S04", "S06"]),
        ])
    bank_rows.extend(rows)
bank_rows.append(["Unit 1", "Current annual component; scenario effective " + longdate(N["U1"]["effective"].isoformat()), pct(N["U1"]["annual_pct"]), money(N["U1"]["annual_amt"]), badge("calc", "Arithmetic only"), ref_links(["S05", "S06", "S20"])])
bank_rows.append(["Unit 2", "Current annual component; scenario effective " + longdate(N["U2"]["effective"].isoformat()), pct(N["U2"]["annual_pct"]), money(N["U2"]["annual_amt"]), badge("calc", "Arithmetic only"), ref_links(["S05", "S06"])])
bank_table = table(["Unit", "Anniversary the allowance belongs to", ("Allowance", "num"), ("Monthly value", "num"), "Status", "Source"], bank_rows,
                   caption="Banked and current allowances, unit by unit. The percentages are added, never compounded.", cls="data-table")

layer_rows = [
    ["Local — SF Rent Ordinance", "1.6% annual allowance for increases effective 1 Mar 2026 – 28 Feb 2027; properly proven banked amounts are added without compounding or rounding up; license and notice rules apply.", "Controls the routine annual scenario on the brief's rent-controlled premise; official coverage and private facts remain unverified.", ref_links(["S02", "S05", "S06", "S07"])],
    ["State — AB 1482 / Civil Code §1947.12", "5% + CPI or 10%, whichever is lower; 8.8% for San Francisco from 1 Aug 2026 to 31 Jul 2027.", "The rent-cap provision excludes housing under a local ordinance restricting annual increases below the state cap. This does not erase other applicable state duties.", ref_links(["S09", "S10"])],
    ["State — Costa-Hawkins, Civil Code §1954.53", "Vacancy rules depend on original occupants and partial changes in occupancy.", "The brief says one original Unit 1 occupant remains, so no vacancy reset is supported by that reported fact. Continuous occupancy and occupant status still require documents.", ref_links(["S11", "S02"])],
    ["State — fixed-term guidance", "During a fixed term, rent cannot be increased unless the agreement permits it; renewal is another possible increase point.", "Unit 1's April 2026 instrument is indispensable. If an unmodified fixed term ends March 31, 2027, the February scenario is unavailable.", ref_links(["S20"])],
    ["State — Civil Code §827 / CCP §1013", "30 days at ≤10%; 90 days above 10%; five extra calendar days for California-to-California mail, with longer extensions in other cases.", "Sets notice procedure, not permission to override a fixed term or missing license.", ref_links(["S08", "S21"])],
    ["Federal — fair housing", "The Fair Housing Act prohibits discrimination in rental terms and conditions. No general federal percentage cap for private unsubsidized housing was located in this scoped review; subsidy-specific rules were not evaluated.", "Owner-neutral selection and retaliation analysis still applies. This is a scoped negative finding, not a claim about every possible federal program.", ref_links(["S14", "S33"])],
]
layer_table = table(["Level", "What it says", "Effect on these two units", "Source"], layer_rows, cls="data-table")

u1_rows = [
    ["Scenario input rent", money(N["U1"]["base"]), "Reported at lease start and again April 1, 2026; current composition and ledger unverified. " + '<a href="@@/hub/flags.html#H-02">H-02</a> ' + ref_links(["S05"])],
    ["Lease gate", "Fixed-term/month-to-month unknown", "Do not use February 1, 2027 until the April 2026 instrument is checked. " + '<a href="@@/hub/flags.html#H-17">H-17</a> ' + ref_links(["S20"])],
    ["Annual-only arithmetic", "1.6% × {0} = {1}; illustrative new rent {2}".format(money(N["U1"]["base"]), money(N["U1"]["annual_amt"]), money(N["U1"]["annual_rent"])), "Conditional scenario, not a certified current lawful rent. " + ref_links(["S05", "S06"])],
    ["Skipped-allowance arithmetic", "1.4% × {0} = {1}".format(money(N["U1"]["base"]), money(N["U1"]["banked_amt"])), "Potential component only if the actual history supports it. " + ref_links(["S06", "S07"])],
    ["Combined scenario", "3.0% = {0}; illustrative new rent {1}".format(money(N["U1"]["total_amt"]), money(N["U1"]["total_rent"])), badge("flag", "Conditional") + ' <a href="@@/hub/flags.html#H-02">H-02</a> <a href="@@/hub/flags.html#H-17">H-17</a> ' + ref_links(["S04", "S07"])],
    ["Banking measuring points", "February 1, 2027 satisfies both in this scenario", "24 months without an increase and 12 months after the skipped allowance became available; this is not a proven 12/24 conflict. " + '<a href="@@/hub/flags.html#H-01">H-01</a> ' + ref_links(["S04", "S07"])],
    ["Notice band if the scenario is otherwise lawful", "30 days; 35 days for California mail", "Notice never cures fixed-term, license, ledger, or coverage defects. " + ref_links(["S08", "S21"])],
]
u1_table = table(["Item", "Value", "Basis and source"], u1_rows, cls="data-table")

u2_rows = [
    ["Scenario input rent", money(N["U2"]["base"]), "Supplied only as the June 1, 2019 lease-start rent, not expressly as current base. " + '<a href="@@/hub/flags.html#H-18">H-18</a> ' + ref_links(["S05"])],
    ["Annual-only arithmetic", "1.6% × {0} = {1}; illustrative new rent {2}".format(money(N["U2"]["base"]), money(N["U2"]["annual_amt"]), money(N["U2"]["annual_rent"])), "Conditional on actual current base, timing, license, and notice. " + ref_links(["S05", "S06"])],
    ["Potentially banked components", "1.8 + 0.7 + 2.3 + 3.6 + 1.7 + 1.4 = 11.5% = {0}".format(money(N["U2"]["banked_amt"])), "Six components, conditional on a no-prior-increase ledger and valid anniversaries. " + '<a href="@@/hub/flags.html#H-03">H-03</a> ' + ref_links(["S04", "S06", "S07"])],
    ["Combined illustration", "13.1% = {0}; illustrative new rent {1}".format(money(N["U2"]["total_amt"]), money(N["U2"]["total_rent"])), badge("flag", "Not a certified lawful maximum") + ' <a href="@@/hub/flags.html#H-18">H-18</a> <a href="@@/hub/flags.html#H-03">H-03</a> ' + ref_links(["S04", "S07"])],
    ["Compounding", "Not used", "Percentages are added and not rounded up. " + ref_links(["S07", "S04"])],
    ["Notice band for the combined illustration", "90 days; 95 days for California mail", "The 10% threshold concerns notice, not a cap on valid banked totals. " + ref_links(["S04", "S08", "S21"])],
    ["Latest date for the 1.6% component", longdate("2027-02-28"), "Later effective dates require the unpublished 2027–28 rate; its official value is blank. " + '<a href="@@/hub/flags.html#H-08">H-08</a> ' + ref_links(["S06"])],
]
u2_table = table(["Item", "Value", "Basis and source"], u2_rows, cls="data-table")

occupancy_rows_html = []
for r in DATA["occupancy_rows"]:
    occupancy_rows_html.append([
        "<strong>{}</strong>".format(esc(r["situation"])),
        esc(r["rule"]),
        esc(r["effect"]),
        ref_links(r["sources"]),
    ])
occupancy_table = table(["Situation", "What the official rule says", "Effect on these units", "Source"],
                        occupancy_rows_html,
                        caption="Occupant changes are governed by Rules and Regulations §6.14 and Civil Code §1954.53(d). "
                                "Every row is quoted or paraphrased from the linked official page.",
                        cls="data-table")

limits_body = """
<section>
  <h2>What “reasonable and normal” can mean here<span class="sub">A routine planning scenario is not an official market average or a legal clearance.</span></h2>
  <p>The simplest routine scenario is the published <strong>1.6% annual allowance</strong>, applied only after the lease, ledger, anniversary, license, coverage, and notice checks. Valid banked amounts may lawfully exceed that current annual percentage. Other petition, passthrough, and vacancy routes have their own rules; this record does not establish them.</p>
  <div class="callout"><p><strong>No official 94122 “normal increase” was located.</strong> The value remains blank and flagged <a href="@@/hub/flags.html#H-10">H-10</a>. No commercial listing average is substituted.</p></div>
</section>
<section>
  <h2>Local, state and federal layers<span class="sub">Each row names both the rule and its limit.</span></h2>
  {layer_table}
</section>
<section>
  <h2>The Rent Board's published allowances<span class="sub">Form 571 controls the periods and rates; erroneous example-year labels are flagged H-19.</span></h2>
  {rate_table}
</section>
<section>
  <h2>Unit 1 — conditional scenarios on {u1_base}<span class="sub">The February 1, 2027 date satisfies both banking measuring points in the assumed history, but the April 2026 lease instrument may independently prevent it.</span></h2>
  {u1_table}
  <div class="callout red"><p><strong>Fixed-term contingency.</strong> If April 1, 2026 began an unmodified fixed term ending March 31, 2027, the February scenario is unavailable. An April 1, 2027 renewal scenario would use the 2027–28 rate, whose official value is blank as of verification. See <a href="@@/hub/flags.html#H-17">H-17</a>.</p></div>
</section>
<section>
  <h2>Unit 2 — conditional scenarios on the 2019 amount {u2_base}<span class="sub">Six potentially banked components plus current 1.6%; not seven banked increases and not a verified current lawful maximum.</span></h2>
  {u2_table}
  <p class="small">Every Unit 2 result assumes both that $3,150.00 is the actual current base and that no intervening increase occurred. Neither fact was established. Rebuild the calculation from the full ledger before drafting any notice.</p>
  <div class="callout red"><p><strong>Pending legislation warning (BOS File #261020 — not law):</strong> Legistar on 10 November 2026 shows File #261020 as <em>Pending Committee Action</em> (introduced 15 September 2026; re-checked 13 November 2026 — still Pending Committee Action, no final action, no enactment date). On 9 November 2026 the Rent Board posted a notice warning that, if enacted as currently proposed, §37.3(h) would cap combined banked (§37.3(a)(2)) and capital-improvement (§37.3(a)(3)) increases at <strong>10% per year of the lowest base rent in effect during the preceding 12 months</strong> through 31 December 2029 (excess accumulated for imposition on or after 1 January 2030), applying to <strong>banked rent increases noticed on or after 15 September 2026</strong>. Unit 2's illustrative banked component alone is 11.5% (13.1% combined). Do not use this scenario to serve notice without checking File #261020 and obtaining advice. {s04} {s05} {s26} See <a href="@@/hub/flags.html#H-22">H-22</a>.</p></div>
</section>
<section>
  <h2>Component arithmetic, line by line<span class="sub">Published rates are official; availability of each component is conditional on private facts.</span></h2>
  {bank_table}
  <div class="callout"><p><strong>Banking rule used here:</strong> skipped allowances can be preserved under Rule 4.12, then added without compounding or rounding up. The 24-month guidance and 12-month rule measure different events; February 1, 2027 satisfies both for Unit 1's scenario. {s04} {s07}</p></div>
</section>
<section>
  <h2>Occupant changes, §6.14 and Costa-Hawkins<span class="sub">Why Unit 1's April 2026 change does not reset the rent, and what still needs documenting.</span></h2>
  <p>Unit 1 was reported with three occupants at the February 2025 lease start and two on 1 April 2026, one of them a replacement. Under the official rules, a market-rate reset is keyed to the <em>last original occupant</em> leaving. On the reported facts one original occupant remained, so the 1.6% allowance still governs. Two private facts remain open and are flagged: whether a §6.14 notice was served under §6.14(b) for a co-occupant (<a href="@@/hub/flags.html#H-23">H-23</a>), and whether the incoming occupant is a co-tenant or a non-co-occupant subtenant governed by §6.14(c) and Costa-Hawkins (<a href="@@/hub/flags.html#H-24">H-24</a>). {s28}</p>
  {occupancy_table}
  <div class="callout red"><p><strong>Do not read this as permission to reset the rent.</strong> Nothing here establishes that either route is available. If the last original occupant later vacates, re-run the whole analysis from the records and consider the optional Rent Board determination petition first. {s29}</p></div>
</section>

""".format(layer_table=layer_table, rate_table=rate_table, u1_table=u1_table, u2_table=u2_table,
           bank_table=bank_table, occupancy_table=occupancy_table,
           u1_base=money(N["U1"]["base"]), u2_base=money(N["U2"]["base"]),
           u1_banked=money(N["U1"]["banked_amt"]), s04=ref_links(["S04"]), s05=ref_links(["S05"]),
           s07=ref_links(["S07"]), s26=ref_links(["S26"]), s28=ref_links(["S28"]), s29=ref_links(["S29"]))

limits_html = page(
    "hub/limits.html",
    "Increase limits, rates and the arithmetic — SF Rent Increase Compliance",
    "Published annual allowances from 1982 to 2027, legal layers, and clearly labeled conditional scenarios for the two units.",
    hero_block(
        "Question 2 of 6 · limits and amounts",
        "Conditional increase scenarios, reproduced to the cent",
        "The published current allowance is 1.6%. Scenario arithmetic gives {0} and {1} on the supplied inputs. Unit 2's 13.1% illustration adds six potentially banked components (11.5%) to current 1.6%; current base and history are not verified.".format(money(u1["annual_amt"]), money(u2["annual_amt"])),
        ["Local cap controls", "AB 1482 does not apply", "No compounding", "No rounding up"],
    ),
    limits_body,
)

# --------------------------------------------------------------------------- notice
notice_rows_html = []
for r in DATA["notice_rows"]:
    notice_rows_html.append([esc(r["item"]), esc(r["detail"]), ref_links(r["sources"])])
notice_table = table(["Required element", "Detail", "Source"], notice_rows_html, cls="data-table")

deadline_rows = [
    ["Unit 1 — annual-only scenario", money(N["U1"]["annual_amt"]), "30 days", longdate(N["U1"]["short_serve_by"].isoformat()), longdate(N["U1"]["short_mail_by"].isoformat()), longdate(N["U1"]["effective"].isoformat()), ref_links(["S08", "S20", "S21"])],
    ["Unit 1 — combined scenario", money(N["U1"]["total_amt"]), "30 days", longdate(N["U1"]["serve_by"].isoformat()), longdate(N["U1"]["mail_by"].isoformat()), longdate(N["U1"]["effective"].isoformat()), ref_links(["S08", "S20", "S21"])],
    ["Unit 2 — annual-only scenario", money(N["U2"]["annual_amt"]), "30 days", longdate(N["U2"]["short_serve_by"].isoformat()), longdate(N["U2"]["short_mail_by"].isoformat()), longdate(N["U2"]["effective"].isoformat()), ref_links(["S08", "S21"])],
    ["Unit 2 — combined scenario", money(N["U2"]["total_amt"]), "90 days", longdate(N["U2"]["serve_by"].isoformat()), longdate(N["U2"]["mail_by"].isoformat()), longdate(N["U2"]["effective"].isoformat()), ref_links(["S08", "S21"])],
]
deadline_table = table(["Scenario", ("Increase", "num"), "Notice", "Personal-service arithmetic", "California-mail arithmetic", "Illustrative effective date", "Source"], deadline_rows,
                       caption="Calendar subtraction only, not universal last-safe dates. Fixed-term, ledger, license, coverage, and repair flags must be resolved first.", cls="data-table")

reason_rows = []
for r in DATA["reasons"]:
    lawful = r["lawful"]
    cls = "ok" if lawful.startswith("Yes") else ("flag" if "petition" in lawful or "within" in lawful or lawful.startswith("Review") else "high")
    reason_rows.append([esc(r["reason"]), badge(cls, lawful), esc(r["detail"]), ref_links(r["sources"])])
reason_table = table(["Reason for the increase", "Lawful for a sitting tenant?", "What is required", "Source"], reason_rows, cls="data-table")

notice_body = """
<section>
  <h2>Notice requirements, without overstating the consequences<span class="sub">Use the strict conservative content checklist; do not claim every omission has the same legal result.</span></h2>
  <p>Civil Code §827 sets written notice periods. Section 37.3(b)(5) states a null-and-void rule, while Rules 4.10(b) and 4.12(b) contain text-specific exceptions—including an express statement that omission of banked dates does not itself void the increase. The safe practice is to include every element rather than litigate an exception.</p>
  {notice_table}
</section>
<section>
  <h2>Illustrative service-date arithmetic<span class="sub">Dates are computed from the scenarios, not represented as universal last-safe dates.</span></h2>
  {deadline_table}
  <div class="callout red">
    <p><strong>Unit 1 may not be eligible for its listed date at all.</strong> Check the April 2026 fixed-term instrument first. For Unit 2's conditional 13.1% scenario with a 28 February 2027 effective date, subtraction gives {u2_serve} for personal delivery and {u2_mail} for California mail. Serve earlier and allow for proof, longer-distance mail, and legal review. Today is {today}; 90 calendar days later is {earliest}, but that does not clear any other requirement.</p>
    <p><strong>Proposed retroactive cutoff (15 September 2026) on banked notices:</strong> Those illustrative Unit 2 notice dates—and any banked notice served on or after 15 September 2026—fall inside the proposed applicability window of BOS File #261020 (<em>Pending Committee Action — not law</em>; re-checked 13 November 2026: unchanged). Per the Rent Board's 9 November 2026 notice, if enacted as currently proposed it would cap combined banked and capital-improvement increases at 10% per year of the lowest base rent in the prior 12 months through 31 December 2029. Re-check File #261020 and seek legal advice before serving any banked increase. {s04} {s26} See <a href="@@/hub/flags.html#H-22">H-22</a>.</p>
  </div>
</section>
<section>
  <h2>Defensible and prohibited bases<span class="sub">Use the actual legal component, not a market-or-occupancy pretext.</span></h2>
  {reason_table}
  <p class="small">For annual/banked components, state the calculation and banked basis dates. Other petition or passthrough routes require their own analysis; no such facts are established here.</p>
</section>
<section>
  <h2>Scenario-only notice skeleton<span class="sub">A review aid, not an official form and not ready to serve.</span></h2>
  <div class="callout red"><p><strong>Stop:</strong> resolve H-02, H-03, H-04, H-05, H-17, H-18, and H-22 before converting any scenario into a tenant notice. Replace all scenario inputs with verified records and obtain legal review for a banked or fixed-term issue.</p></div>
  <dl class="kv">
    <dt>To</dt><dd>[Tenant placeholders], [Unit and service address kept private]</dd>
    <dt>Illustrative subject</dt><dd>Notice of rent increase effective {u1_eff_long} — only if lease and license checks permit</dd>
    <dt>Reported scenario base</dt><dd>{u1_base} per month; verify current base and temporary passthroughs</dd>
    <dt>Annual-only component</dt><dd>{u1_annual} per month (1.6%)</dd>
    <dt>Official basis</dt><dd>Form 571 allowance for 1 March 2026 – 28 February 2027, applied to the verified eligible effective date</dd>
    <dt>Banked component</dt><dd>None in the annual-only illustration. If proven, state 1.4%, {u1_banked}, and February 1, 2026 separately.</dd>
    <dt>Illustrative new base</dt><dd>{u1_annual_rent} per month for the annual-only scenario; no rounding up or compounding</dd>
    <dt>Review information</dt><dd>Include Rent Board contact and petition information. Referral resources are not a promise of free counsel.</dd>
  </dl>
  <p class="small">If a Unit 2 combined scenario is ever supported, itemise 1.8% (June 1, 2020), 0.7% (June 1, 2021), 2.3% (June 1, 2022), 3.6% (June 1, 2023), 1.7% (June 1, 2024), 1.4% (June 1, 2025), plus current 1.6%—and replace the unverified base before calculating the notice.</p>
</section>

""".format(notice_table=notice_table, deadline_table=deadline_table, reason_table=reason_table,
           today=longdate(N["today"].isoformat()), earliest=longdate(N["earliest_90"].isoformat()),
           u2_serve=longdate(N["U2"]["serve_by"].isoformat()), u2_mail=longdate(N["U2"]["mail_by"].isoformat()),
           u1_eff_long=longdate(DATA["calculations"]["U1"]["annual_effective"]),
           u1_base=money(N["U1"]["base"]), u1_annual=money(N["U1"]["annual_amt"]),
           u1_banked=money(N["U1"]["banked_amt"]), u1_annual_rent=money(N["U1"]["annual_rent"]),
           u2_total=money(N["U2"]["total_amt"]), u2_total_rent=money(N["U2"]["total_rent"]),
           s04=ref_links(["S04"]), s26=ref_links(["S26"]))

notice_html = page(
    "hub/notice.html",
    "Notice requirements and lawful reasons — SF Rent Increase Compliance",
    "What a San Francisco rent increase notice must contain, the last safe service dates for each unit, and which reasons are lawful versus unlawful.",
    hero_block(
        "Question 3 of 6 · telling the tenants",
        "How to serve the increase, and what counts as a reason",
        "A correct scenario still needs a lawful lease basis, license, full history, and timely written notice. Include dollar amount, percentage, effective date, annual/banked components, and banked basis dates; consequences of omissions are text-specific.",
        ["30 / 90 days", "+5 if mailed", "Itemise annual vs banked", "No rounding up"],
    ),
    notice_body,
)

# --------------------------------------------------------------------------- practice
practice_rows_html = []
for r in DATA["practice_rows"]:
    practice_rows_html.append([esc(r["topic"]), esc(r["corporate"]), esc(r["individual"]), ref_links(r["sources"])])
practice_table = table(["Topic", "Large / corporate owners", "Individual owners", "Source"], practice_rows_html, cls="data-table")

practice_body = """
<section>
  <h2>The honest answer about practice<span class="sub">Binding duties are verified; typical behavior by owner type is not.</span></h2>
  <p>The same allowance, license, notice, banking, harassment, and fair-housing rules apply to an individual and a corporate landlord. San Francisco also prohibits covered algorithmic devices using nonpublic competitor data. While the U.S. Census Bureau and HUD released the 2024 Rental Housing Finance Survey (CB26-TPS.12) on 19 February 2026 tracking national property, mortgage, and ownership-entity structure {s34}, no official dataset measures typical rent-increase behavior for San Francisco owners by corporate form; the comparative rate remains blank at <a href="@@/hub/flags.html#H-11">H-11</a>.</p>
  <div class="answer"><h3>What an individual owner should take from this</h3><p>Use the same per-unit controls expected of any compliant operator: current reporting and license evidence, actual lease and ledger, reproducible calculation, neutral selection, timely notice, and proof of service. That is a recommendation, not a claim that small owners are inherently informal or large owners inherently compliant.</p></div>
</section>
<section>
  <h2>Side by side<span class="sub">Owner-neutral duties and accurately bounded differences.</span></h2>
  {practice_table}
</section>
<section>
  <h2>A documented corporate-practice example<span class="sub">Enforcement allegations and a proposed settlement—not a universal stereotype or final adjudication.</span></h2>
  <ul>
    <li><strong>DOJ alleged</strong> that RealPage's revenue-management software relied on landlords' nonpublic competitively sensitive information and included features aligning pricing. Its November 24, 2025 announcement described a <strong>proposed</strong> settlement subject to court approval. This is evidence about that enforcement matter, not about every corporation. {s22}</li>
    <li><strong>San Francisco's rule is direct:</strong> §37.10C prohibits a landlord from using a covered algorithmic device that analyzes nonpublic competitor data to recommend rents or occupancy. General property-management software is not banned merely because it is software. {s16}</li>
    <li><strong>Owner type can matter in a different state-law context:</strong> the AB 1482 single-family/condominium exemption has entity and notice conditions. It does not replace this building's lower local cap on the brief's rent-controlled premise. {s09} {s10}</li>
  </ul>
</section>
<section>
  <h2>Practical recommendation<span class="sub">A compliance calendar for any owner, not an unsupported claim about how each group behaves.</span></h2>
  <p>Track the March 1 inventory/fee dates, each verified anniversary or lease event, the correct notice period, and the February 28, 2027 end of the current rate. Re-fetch the official rate before any later effective date.</p>
</section>

""".format(practice_table=practice_table, s16=ref_links(["S16"]), s09=ref_links(["S09"]),
           s02=ref_links(["S02"]), s01=ref_links(["S01"]),
           s22=ref_links(["S22"]), s10=ref_links(["S10"]), s34=ref_links(["S34"]))

practice_html = page(
    "hub/practice.html",
    "Corporate vs individual owner practice — SF Rent Increase Compliance",
    "How large real estate corporations and individual San Francisco owners are treated by the same rent ordinance, and the one pricing practice San Francisco bans.",
    hero_block(
        "Question 4 of 6 · owner practice",
        "Big owners, small owners, same ordinance",
        "Individual and institutional landlords share the core SF duties. A federal enforcement example illustrates one alleged portfolio-scale practice; San Francisco's covered algorithm ban applies to every landlord.",
        ["Owner-neutral duties", "§37.10C pricing ban", "No official behaviour data"],
    ),
    practice_body,
)

# --------------------------------------------------------------------------- fair housing
fh_rows = []
for r in DATA["fair_housing_rows"]:
    fh_rows.append([esc(r["point"]), esc(r["finding"]), status_badge(r["status"]), ref_links(r["sources"])])
fh_table = table(["Question", "Answer", "Status", "Source"], fh_rows, cls="data-table")

fh_body = """
<section>
  <h2>One unit or both?<span class="sub">Different treatment is not automatically discrimination; identical treatment is not immunity.</span></h2>
  <div class="answer">
    <h3>Raising one unit and not the other is not, by itself, a fair-housing violation. The reason, evidence, and independent lawfulness of each increase control.</h3>
    <p>Chapter 37 and the cited fair-housing statutes do not require parallel increases. They prohibit discrimination or harassment because of protected characteristics, and state/local law separately addresses retaliation and bad-faith conduct. Use verified lease terms, current base rent, anniversary, and banked history—not assumptions or protected traits.</p>
  </div>
  <p class="small">This is a reading of cited law, not a prediction or legal clearance. Unit 2's current base and both full histories remain unverified.</p>
</section>
<section>
  <h2>Fair-housing analysis, point by point<span class="sub">Official rule, reading, or missing evidence is labeled in each row.</span></h2>
  {fh_table}
</section>
<section>
  <h2>A neutral, reviewable policy<span class="sub">Use the same method, not necessarily the same percentage.</span></h2>
  <ol>
    <li><strong>Write the method once:</strong> review each unit annually against its actual lease, verified base, last increase, published rate, and proven banked components. {s05}</li>
    <li><strong>Keep a per-unit calculation and decision record,</strong> including a decision not to raise an ineligible unit.</li>
    <li><strong>Do not add rent solely because a roommate joined.</strong> Section 37.3(a)(11) prohibits that surcharge; a separate cost petition is a different, unproven route. {s02}</li>
    <li><strong>Review protected activity and repairs.</strong> A 180-day event is a trigger for §1942.5 analysis, not an automatic ban; repair petitions can independently defer increases. {s12} {s23}</li>
    <li><strong>Do not use covered pricing algorithms</strong> that analyze nonpublic competitor data. {s16}</li>
  </ol>
</section>
<section>
  <h2>Why “raise both to be safe” is not a safe harbour<span class="sub">Uniformity cannot cure retaliation, protected-class motive, bad arithmetic, or an early fixed-term increase.</span></h2>
  <p>A neutral method and complete records reduce avoidable ambiguity; they do not guarantee acceptance by a tenant, advocate, Rent Board judge, or court. Do not raise an ineligible unit merely to make the building look symmetrical.</p>
</section>

""".format(fh_table=fh_table, u1_base=money(N["U1"]["base"]), u2_base=money(N["U2"]["base"]),
           s02=ref_links(["S02"]), s12=ref_links(["S12"]), s16=ref_links(["S16"]),
           s05=ref_links(["S05"]), s23=ref_links(["S23"]))

fair_housing_html = page(
    "hub/fair-housing.html",
    "One unit or both — discrimination analysis — SF Rent Increase Compliance",
    "Whether raising one unit's rent and not the other creates fair-housing exposure in San Francisco, the protected classes under federal and California law, and how to document an objective difference.",
    hero_block(
        "Question 5 of 6 · one unit or both",
        "Is it safe to raise one rent and not the other?",
        "Not automatically. Neutral documented differences are distinct from protected-class selection, retaliation, or bad-faith pressure. Both units must independently satisfy every rent-increase requirement.",
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
        ref_links(r["sources"]),
    ])
review_table = table(["#", "What a tenant-side lawyer checks", "Evidence needed", "Where this file stands", "Source"], review_rows_html,
                     caption="{n} checks. Official rules and arithmetic can be verified here; actual legal sufficiency requires private records and notice evidence.".format(n=len(DATA["review_rows"])), cls="data-table")

review_body = """
<section>
  <h2>The test, run honestly<span class="sub">No attorney reviewed this file and no “pass” verdict is claimed.</span></h2>
  <p>A tenant-side reviewer can test the license, coverage, lease authority, current base, anniversary, banking, calculation, notice, service, repairs, retaliation, protected-class selection, and algorithm use. This dashboard verifies official rules and scenario arithmetic; it cannot clear the private facts.</p>
  {review_table}
</section>
<section>
  <h2>Where the file stands<span class="sub">Arithmetic verified; readiness to serve notice unresolved.</span></h2>
  <div class="grid-2">
    <div class="cardlink"><strong>Verified here</strong><span>Current 1.6% rate and period, additive arithmetic, service-date subtraction, and the individual-owner license rule.</span></div>
    <div class="cardlink"><strong>Needs evidence</strong><span>Coverage, licenses, Unit 1 lease instrument, Unit 2 current base, both ledgers, repairs, protected activity, actual notice, and service.</span></div>
    <div class="cardlink"><strong>Banking distinction</strong><span>Unit 1's scenario satisfies both measuring points on February 1, 2027; that does not resolve fixed-term or ledger facts. See <a href="@@/hub/flags.html#H-01">H-01</a>.</span></div>
    <div class="cardlink"><strong>No guaranteed outcome</strong><span>A tenant, advocate, administrative judge, or court can evaluate facts and arguments not present here.</span></div>
  </div>
</section>
<section>
  <h2>Official tenant-review routes<span class="sub">Available routes are not a promise of free representation.</span></h2>
  <ul>
    <li><strong>Check license reporting:</strong> the Housing Inventory page says tenants can search the Rent Board Portal for license status. {s03}</li>
    <li><strong>Petition without counsel:</strong> the Rent Board expressly says a lawyer is not required. {s19}</li>
    <li><strong>Repair-based deferral:</strong> a qualifying Failure to Repair and Maintain petition is due no later than 60 days after receipt of the increase notice. {s23}</li>
    <li><strong>Referral resources:</strong> the official list includes Open Door Legal's Sunset office and other organizations. Contact the provider about eligibility, issue coverage, capacity, and cost; do not assume free representation. {s19}</li>
    <li><strong>Rent Board counseling:</strong> 415-252-4600 on published weekday hours. {s18}</li>
  </ul>
</section>

""".format(review_table=review_table, s03=ref_links(["S03"]), s19=ref_links(["S19"]),
           s18=ref_links(["S18"]), s23=ref_links(["S23"]))

review_html = page(
    "hub/review.html",
    "Tenant-lawyer review test — SF Rent Increase Compliance",
    "Tenant-side review checks and the evidence still needed before any notice could be defended.",
    hero_block(
        "Question 6 of 6 · withstanding scrutiny",
        "Would a San Francisco tenant lawyer find a defect?",
        "Run the review before notice. Official rates and arithmetic are reproducible; lease, ledger, license, repair, retaliation, and service facts remain open.",
        ["{} checks".format(len(DATA["review_rows"])), "No attorney verdict", "Evidence before service"],
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
        ref_links(f["sources"]),
        esc(f["action"]),
    ])
flag_table = table(["ID", "Severity", "Item", "Detail and effect", "Official source", "Action for reviewer"], flag_rows,
                   caption="{n} items. High items can change an amount or prevent an increase; low items include source and repository irregularities.".format(n=len(DATA["flags"])), cls="data-table")

flags_body = """
<section>
  <h2>Flagged for Review<span class="sub">Unresolved facts do not block publication, but they do block treating a scenario as notice-ready.</span></h2>
  <div class="callout red" id="history-privacy"><p><strong>High-priority privacy flag — public Git history:</strong> A prior commit contains tenant initials in an older file. The current-file privacy scan passes, but it does not scan or erase historical commits, branches, pull requests, caches, forks, or clones. Do not interpret the current site redaction as removal from history.</p><p><strong>Action:</strong> Coordinate sensitive-data cleanup with repository collaborators and GitHub support as appropriate. History rewriting affects commit IDs and open work, and copies may persist. This session has not rewritten history or changed repository visibility. <a href="https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository">GitHub's official sensitive-data removal guidance</a>.</p></div>
  <p><strong>High</strong> items can change an amount or prevent an increase. <strong>Medium</strong> items affect documentation or process. <strong>Low</strong> items record source distinctions, judgement limits, or repository irregularities. Every row has an official link.</p>
  <div class="callout red"><p><strong>Read H-17 and H-18 first.</strong> Unit 1's lease may prevent a February increase; Unit 2's $3,150.00 is only a lease-start input. Then resolve the ledgers, licenses, and coverage. H-01 records why the banking formulations are not treated as a proven conflict, and H-15 preserves Rule 4.12(b)'s express non-void language.</p></div>
  {flag_table}
</section>
<section>
  <h2>Official-confirmation values deliberately blank<span class="sub">No official source, no confirmed value. Blank is not zero.</span></h2>
  <div class="tablewrap"><table class="data-table">
  <caption>Private owner-brief inputs are shown elsewhere only as scenario inputs.</caption>
  <thead><tr><th scope="col">Value</th><th scope="col">Official confirmation</th><th scope="col">What would verify it</th><th scope="col">Official source / flag</th></tr></thead>
  <tbody>
    <tr><td>License status, both units</td><td></td><td>Dated Rent Board Portal evidence on notice and effective dates.</td><td>{s03}<br><a href="@@/hub/flags.html#H-04">H-04</a></td></tr>
    <tr><td>Certificate of occupancy / coverage</td><td></td><td>City record and exemption analysis for the actual property.</td><td>{s18}<br><a href="@@/hub/flags.html#H-05">H-05</a></td></tr>
    <tr><td>Unit 1 fixed-term and escalation terms</td><td></td><td>Signed April 2026 instrument and amendments.</td><td>{s20}<br><a href="@@/hub/flags.html#H-17">H-17</a></td></tr>
    <tr><td>Unit 2 current base rent</td><td></td><td>Current lease and full ledger, not only the 2019 start amount.</td><td>{s05}<br><a href="@@/hub/flags.html#H-18">H-18</a></td></tr>
    <tr><td>Both units' prior increases and banked entitlement</td><td></td><td>Every notice and payment record across the claimed period.</td><td>{s04}<br><a href="@@/hub/flags.html#H-02">H-02</a>, <a href="@@/hub/flags.html#H-03">H-03</a></td></tr>
    <tr><td>Market “normal” increase for 94122</td><td></td><td>No official value located; do not substitute commercial listings.</td><td>{s05}<br><a href="@@/hub/flags.html#H-10">H-10</a></td></tr>
    <tr><td>2027–28 allowance</td><td></td><td>Future Form 571 when officially published.</td><td>{s06}<br><a href="@@/hub/flags.html#H-08">H-08</a></td></tr>
    <tr><td>Corporate versus individual behavior rate</td><td></td><td>No official SF comparative dataset located.</td><td>{s22}<br><a href="@@/hub/flags.html#H-11">H-11</a></td></tr>
  </tbody></table></div>
</section>

""".format(flag_table=flag_table, s03=ref_links(["S03"]), s04=ref_links(["S04"]),
           s05=ref_links(["S05"]), s06=ref_links(["S06"]), s18=ref_links(["S18"]),
           s20=ref_links(["S20"]), s22=ref_links(["S22"]))


# --------------------------------------------------------------------------- suggestions
def flag_links(ids) -> str:
    out = []
    for i in ids:
        out.append('<a href="{0}#{1}" title="Flag {1}">{1}</a>'.format("@@/hub/flags.html", i))
    return '<span class="src">' + " ".join(out) + "</span>"


def mixed_links(ids) -> str:
    out = []
    for i in ids:
        if i.startswith("H"):
            out.append('<a href="{0}#{1}" title="Flag {1}">{1}</a>'.format("@@/hub/flags.html", i))
        else:
            s = SRC[i]
            out.append(
                '<a href="{}#{}" title="{} — {}">{}</a>'.format(
                    "@@/hub/sources.html", i, esc(s["publisher"]), esc(s["title"]), i
                )
            )
    return '<span class="src">' + " ".join(out) + "</span>"


steps_rows = []
for s in DATA["decision_suggestions"]:
    steps_rows.append([
        '<span class="mono">{}</span>'.format(s["id"]),
        "<strong>{}</strong>".format(esc(s["suggestion"])),
        esc(s["why"]),
        esc(s["official_basis"]) + mixed_links(s["links"]),
        status_badge(s["status"]),
    ])
steps_table = table(["#", "Suggested step", "Why it matters", "Official basis", "Status"], steps_rows,
                    caption="Operating suggestions, not legal requirements. Each step cites its official basis where one exists.", cls="data-table")

missing_rows = []
for m in DATA["missing_info_rows"]:
    missing_rows.append([
        '<span class="mono">{}</span>'.format(m["id"]),
        "<strong>{}</strong>".format(esc(m["information"])),
        esc(m["have"]),
        esc(m["blocks"]),
        esc(m["discover"]),
        mixed_links(m["links"]),
    ])
missing_table = table(["#", "Information or question", "Have / don't have", "Why it blocks a decision", "How to discover it", "Source"], missing_rows, cls="data-table")

site_rows = [
    ["SS-01", "Pre-serve review gate", "No notice is drafted until the licence, lease, ledger, anniversary, coverage, and repair checks are signed off and dated.", mixed_links(["S03", "S01", "H-04", "H-17", "H-09"])],
    ["SS-02", "Decision log / change register", "Record each considered path (raise neither, Unit 1 only, Unit 2 only, both) with reasons, inputs, and sources so differences follow records rather than assumptions.", mixed_links(["H-13", "S13", "S14", "S15"])],
    ["SS-03", "Rate watch", "Re-fetch Form 571 each March 1 and archive prior versions so an outdated or unpublished percentage is never applied.", mixed_links(["S06", "H-08"])],
    ["SS-04", "Independent review step", "An attorney, advocate, or Rent Board counselor reviews the draft notice before it reaches tenants; arithmetic alone is not a legal clearance.", mixed_links(["S18", "S19", "H-20"])],
    ["SS-05", "Public/private split", "Never paste Rent Board Portal screenshots, ledgers, or tenant/owner contact details into the site; private verification happens off-site.", mixed_links(["S03"])],
    ["SS-06", "One change at a time", "Do not bundle a rent increase with other lease or fee changes; each change keeps its own notice, timing, and legal basis.", mixed_links(["S02", "S08"])],
]
site_table = table(["#", "Site-improvement suggestion", "How it improves decision-making", "Basis / related flag"], site_rows, cls="data-table")

suggestions_body = """
<section>
  <h2>Suggestions — review every path before implementing anything<span class="sub">A dedicated review section: suggested operating steps, decisions not yet supported, and how to discover what is still unknown.</span></h2>
  <div class="answer">
    <p>This section collects suggestions for how the owner should proceed and how this site can support better decisions. None of it is legal advice. Each suggested step carries its official basis where one exists; every unsupported private fact is left blank and flagged rather than assumed.</p>
    <p><strong>Choose a path before acting:</strong> raise neither unit until the flags are resolved; raise Unit 1 only (annual-only, once the lease instrument and licence are confirmed); raise Unit 2 only (annual-only once the current base is verified); or raise both on the same verified schedule. The site records the reasons for whichever path is chosen — neutral, documented differences reduce, but do not eliminate, discrimination or retaliation exposure.</p>
  </div>
</section>
<section>
  <h2>Suggested operating steps before serving any notice<span class="sub">Sequence, not legal requirements; official basis cited where one exists.</span></h2>
  {steps_table}
</section>
<section>
  <h2>Decisions not yet supported — what must be resolved first<span class="sub">Information the owner has and does not have, and how to discover the rest.</span></h2>
  {missing_table}
</section>
<section>
  <h2>Suggestions for improving this site's decision support<span class="sub">For whoever maintains the site: review-before-implement paths and change control.</span></h2>
  {site_table}
</section>
<section>
  <h2>Decision log template<span class="sub">Record the chosen path and its basis before any change is implemented.</span></h2>
  <table>
  <caption>Fill in before implementing; keep with the dated evidence file.</caption>
  <thead><tr><th scope="col">Field</th><th scope="col">Entry</th></tr></thead>
  <tbody>
    <tr><td>Date of decision</td><td></td></tr>
    <tr><td>Path chosen</td><td>Raise neither &middot; raise Unit 1 only &middot; raise Unit 2 only &middot; raise both</td></tr>
    <tr><td>Inputs used</td><td>Lease, full ledger, current base rent, rate period, banked components</td></tr>
    <tr><td>Calculation (additive, not compounded, not rounded up)</td><td></td></tr>
    <tr><td>Notice date and service method</td><td>30 days at 10% or less; 90 days above 10%; +5 days for California mail</td></tr>
    <tr><td>Licence check (Rent Board Portal, before notice and on the effective date)</td><td></td></tr>
    <tr><td>Independent review (attorney, advocate, or Rent Board counseling)</td><td></td></tr>
    <tr><td>Flags resolved first</td><td>List H-numbers resolved</td></tr>
    <tr><td>Retained with</td><td>Dated evidence file: notices, proof of service, licence confirmation, calculation worksheet</td></tr>
  </tbody>
  </table>
</section>
"""
suggestions_html = page(
    "hub/suggestions.html",
    "Suggestions and missing information — SF Rent Increase Compliance",
    "Review-before-implement decision paths, decisions not yet supported, missing-information discovery, and site-improvement suggestions. No suggestion is legal advice; no blank is filled in.",
    hero_block(
        "Suggestions · review before implementing",
        "Review every path before implementing anything",
        "Suggested operating steps, decisions not yet supported, missing-information discovery, and site-improvement suggestions. No suggestion is legal advice; no blank is filled in.",
        ["Review before implement", "Missing information", "Official sources only", "Decision log"],
    ),
    suggestions_body.format(
        steps_table=steps_table,
        missing_table=missing_table,
        site_table=site_table,
    ),
)

flags_html = page(
    "hub/flags.html",
    "Flagged for Review — SF Rent Increase Compliance",
    "{} flagged private facts, source distinctions, and repository irregularities, each linked to official material.".format(len(DATA["flags"])),
    hero_block(
        "Flagged for Review · {} items".format(len(DATA["flags"])),
        "Where the record is incomplete or easy to misread",
        "High-severity unknowns can change an amount or prevent an increase. They remain visible instead of being filled with guesses.",
        ["{} high".format(sum(f["severity"] == "high" for f in DATA["flags"])),
         "{} medium".format(sum(f["severity"] == "medium" for f in DATA["flags"])),
         "{} low / source / repository".format(sum(f["severity"] == "low" for f in DATA["flags"]))],
    ),
    flags_body,
)

# --------------------------------------------------------------------------- sources
src_count = len(DATA["sources"])
rb_count = sum(1 for s in DATA["sources"] if "Rent Board" in s["publisher"])
treas_count = sum(1 for s in DATA["sources"] if "Treasurer" in s["publisher"])
bos_count = sum(1 for s in DATA["sources"] if "Board of Supervisors" in s["publisher"])
ca_stat_count = sum(1 for s in DATA["sources"] if "California Legislative Information" in s["publisher"])
ca_guide_count = sum(1 for s in DATA["sources"] if "California Department of Real Estate" in s["publisher"])
fed_count = sum(1 for s in DATA["sources"] if s["level"].startswith("Federal"))
assert rb_count + treas_count + bos_count + ca_stat_count + ca_guide_count + fed_count == src_count

src_rows = []
for s in DATA["sources"]:
    src_rows.append([
        '<span class="mono" id="{}">{}</span>'.format(s["id"], s["id"]),
        "<strong><a href=\"{}\" rel=\"noopener noreferrer\">{}</a></strong><br><span class=\"small\">{} · {} · verified {}</span>".format(
            esc(s["url"]), esc(s["title"]), esc(s["publisher"]), esc(s["level"]), esc(s.get("retrieved", DATA["meta"]["retrieved"]))),
        "&ldquo;{}&rdquo;".format(esc(s["quote"])),
        esc(s["used_for"]),
    ])
src_table = table(["ID", "Source", "Verbatim quote used", "Used for"], src_rows,
                  caption="All {} official sources were fetched and read from their official publishers on the retrieval date recorded for each one (7–13 November 2026; the load-bearing subset was re-read live on {}). The quote column holds the passage used.".format(src_count, longdate(DATA["meta"]["retrieved"])), cls="source-table")

sources_body = """
<section>
  <h2>Source registry<span class="sub">{src_count} official sources. Commercial sources are not used for legal values or market conclusions.</span></h2>
  <p>Every claim-table row links to official material or an explicit flag. Official rules and rates are distinguished from owner-brief scenario inputs. Unsupported official-confirmation values are blank. <a href="@@/hub/flags.html#H-01">H-01</a> reconciles the banking measuring points; <a href="@@/hub/flags.html#H-19">H-19</a> flags the agencies' own worked-example year errors; <a href="@@/hub/flags.html#H-22">H-22</a> records the 9 November 2026 Rent Board warning on File #261020.</p>
  {src_table}
</section>

<section>
  <h2>Publisher coverage<span class="sub">City, state and federal ({src_count} total).</span></h2>
  <dl class="kv">
    <dt>San Francisco Rent Board / SF.gov</dt><dd>{rb_count} sources: ordinance (§§37.3, 37.10B, 37.10C, 37.15), adopted Rules (Parts IV and VI §6.14), Form 571, current guidance, fees, repairs, AB 1482 note, and referral resources.</dd>
    <dt>SF Office of the Treasurer &amp; Tax Collector</dt><dd>{treas_count} sources: lessor guidance and Business Registration Certificate triggers/carve-out.</dd>
    <dt>SF Board of Supervisors (Legistar)</dt><dd>{bos_count} legislative file (#261020, pending committee action — not law, including Leg Ver1 and Legislative Digest attachments).</dd>
    <dt>California Legislative Information</dt><dd>{ca_stat_count} statutes: Civil Code §§827, 1942.5, 1947.12, 1954.53, Code of Civil Procedure §1013, and Government Code §12955.</dd>
    <dt>California Department of Real Estate</dt><dd>{ca_guide_count} official state guide: fixed-term and notice guidance.</dd>
    <dt>Federal official sources</dt><dd>{fed_count} sources: the enacted text of 42 U.S.C. §3604 on GovInfo, HUD's Fair Housing Act overview, and DOJ's accurately labeled RealPage proposed-settlement announcement.</dd>
  </dl>
  <p class="small">The federal statute behind the HUD page, 42 U.S.C. §3604, was cited in an earlier edition through the Office of Law Revision Counsel site; that URL returned &ldquo;Page Not Found&rdquo; when checked on 7 November 2026, so this edition cites the HUD overview page, which was live-verified again on 10 November 2026 (and 42 U.S.C. §3604 was additionally verified on GovInfo). The broken link is repaired in the repository and logged as H-14.</p>
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
""".format(src_count=src_count, rb_count=rb_count, treas_count=treas_count, bos_count=bos_count,
           ca_stat_count=ca_stat_count, ca_guide_count=ca_guide_count, fed_count=fed_count,
           src_table=src_table, s18=ref_links(["S18"]))

sources_html = page(
    "hub/sources.html",
    "Sources — SF Rent Increase Compliance",
    "The {} official sources behind the legal analysis and conditional calculations, with supporting passages and retrieval dates.".format(src_count),
    hero_block(
        "Verification · {} official sources".format(src_count),
        "Every claim, traced to the sentence it came from",
        "City ordinance, legislative records and agency guidance, California statutes, and federal fair-housing material. All {} sources were fetched and read from their official publishers on the retrieval date recorded for each one (7–13 November 2026; the load-bearing subset was re-read live on {}); the quote column holds the exact passage used.".format(src_count, longdate(DATA["meta"]["retrieved"])),
        ["{} SF Rent Board".format(rb_count),
         "{} SF Treasurer + {} SF BOS".format(treas_count, bos_count),
         "{} California statutes + {} state guide".format(ca_stat_count, ca_guide_count),
         "{} federal official sources".format(fed_count)],
    ),
    sources_body,
)

# --------------------------------------------------------------------------- write
PAGES = {
    "hub/suggestions.html": suggestions_html,
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
