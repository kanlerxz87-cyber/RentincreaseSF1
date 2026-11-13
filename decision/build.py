#!/usr/bin/env python3
"""Deterministic generator for the /decision/ edition.

Reads  : decision/data/sources.json, decision/data/rates.json, decision/data/site.json
Writes : decision/*.html and decision/assets/style.css

Rules enforced here (and re-checked independently by verify.py):
  * every data-table row carries at least one official source link;
  * a value that cannot be confirmed from an official source is rendered as a
    deliberately blank, visually flagged cell - never estimated;
  * all money uses exact Decimal arithmetic on the reported figures;
  * no tenant name, initial, street address, e-mail or phone number is written.
"""

from __future__ import annotations

import json
import os
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE

TODAY = date(2026, 11, 13)

SRC = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
RATES = json.loads((DATA / "rates.json").read_text(encoding="utf-8"))
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))

SOURCES = {s["id"]: s for s in SRC["sources"]}
PERIODS = RATES["periods"]
PAGES = SITE["pages"]
FLAGS = SITE["flags"]
META = SITE["meta"]

CENT = Decimal("0.01")


# --------------------------------------------------------------------- helpers
def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def money(value: Decimal) -> str:
    return "${:,.2f}".format(value.quantize(CENT, rounding=ROUND_HALF_UP))


def pct(value: Decimal) -> str:
    return "{}%".format(value.normalize())


def d(text: str) -> date:
    y, m, dd = (int(x) for x in str(text).split("-"))
    return date(y, m, dd)


def longdate(value: date) -> str:
    return "{d.day} {m} {d.year}".format(
        d=value,
        m=["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"][value.month - 1],
    )


def longperiod(p) -> str:
    return "{} – {}".format(longdate(d(p["start"])), longdate(d(p["end"])))


def rate_at(when: date):
    """Published percentage in force on `when`, or None if not yet published."""
    for p in PERIODS:
        if d(p["start"]) <= when <= d(p["end"]):
            return Decimal(p["pct"])
    return None


def src_links(ids) -> str:
    out = []
    for sid in ids or []:
        if sid not in SOURCES:
            raise SystemExit("unknown source id: {}".format(sid))
        s = SOURCES[sid]
        out.append(
            '<a class="srcref" href="sources.html#S{id}" title="{t} — {p}">S{id}</a>'.format(
                id=sid.lstrip("S"), t=esc(s["title"]), p=esc(s["publisher"])
            )
        )
    return " ".join(out)


def blank_cell() -> str:
    return '<span class="blank" title="No official source publishes this value. Left blank on purpose.">unverified</span>'


# ----------------------------------------------------------------- computations
UNITS = {
    "A": {
        "label": "Unit A",
        "start": date(2025, 2, 1),
        "base": Decimal("3995.00"),
        "occupants_start": 3,
        "occupants_now": 2,
        "last_change": "2026-04-01 — occupant change recorded; rent unchanged at $3,995.00",
        "anniversary": "Unresolved — 1 February or 1 April (see F-01)",
        "anniversary_md": "(unresolved)",
    },
    "B": {
        "label": "Unit B",
        "start": date(2019, 6, 1),
        "base": Decimal("3150.00"),
        "occupants_start": 2,
        "occupants_now": 2,
        "last_change": "None recorded since the 2019-06-01 tenancy start (see F-05)",
        "anniversary": "1 June",
        "anniversary_md": "06-01",
    },
}

BANKED_B = ["2020-06-01", "2021-06-01", "2022-06-01", "2023-06-01",
            "2024-06-01", "2025-06-01", "2026-06-01"]

SCENARIOS = [
    {
        "id": "A-1", "unit": "A", "eff": "2027-02-01",
        "title": "Annual increase only",
        "banked": [], "annual": "rate",
        "note": "Ignores the skipped 2026 increase, which stays banked for later.",
        "src": ["S03", "S06", "S14"],
    },
    {
        "id": "A-2", "unit": "A", "eff": "2027-02-01",
        "title": "Annual increase plus the one banked year",
        "banked": ["2026-02-01"], "annual": "rate",
        "note": "1.4% (2025-26) added to 1.6% (2026-27). Added, not compounded. Assumes the anniversary is 1 February (F-01).",
        "src": ["S03", "S04", "S06", "S14"],
    },
    {
        "id": "A-3", "unit": "A", "eff": "2027-04-01",
        "title": "If the anniversary moved to 1 April — banked component only",
        "banked": ["2026-02-01"], "annual": "unknown",
        "note": "The annual component from 1 March 2027 is not yet published, so only the banked part is computable. Dollars shown are the banked component alone.",
        "src": ["S03", "S04", "S06", "S14"],
    },
    {
        "id": "B-1", "unit": "B", "eff": "2027-06-01",
        "title": "Banked component only (2020 – 2026)",
        "banked": BANKED_B, "annual": "none",
        "note": "Seven skipped years, added not compounded. Above 10%, so the 90-day notice rule applies. Above the cap proposed in File No. 261020 (F-10).",
        "src": ["S04", "S05", "S06", "S14", "S20"],
    },
    {
        "id": "B-2", "unit": "B", "eff": "2027-06-01",
        "title": "Banked component plus the annual increase",
        "banked": BANKED_B, "annual": "unknown",
        "note": "The annual percentage in force on 1 June 2027 is not published until 1 March 2027, so the combined total is left blank rather than estimated. The banked floor alone is already above 10%, so 90 days applies either way.",
        "src": ["S04", "S05", "S06", "S14", "S20"],
    },
]


def compute_scenarios():
    rows = []
    for sc in SCENARIOS:
        u = UNITS[sc["unit"]]
        eff = d(sc["eff"])
        base = u["base"]

        banked_pct = Decimal("0")
        for ymd in sc["banked"]:
            r = rate_at(d(ymd))
            if r is None:
                raise SystemExit("no published rate for banked year {}".format(ymd))
            banked_pct += r
        banked_pct = banked_pct.quantize(Decimal("0.1"))

        if sc["annual"] == "rate":
            annual_pct = rate_at(eff)
            annual_known = annual_pct is not None
        elif sc["annual"] == "none":
            annual_pct = Decimal("0")
            annual_known = True
        else:  # unknown
            annual_pct = None
            annual_known = False

        if annual_known:
            total = (banked_pct + annual_pct).quantize(Decimal("0.1"))
            amount = (base * total / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
            new_rent = (base + amount).quantize(CENT, rounding=ROUND_HALF_UP)
        else:
            total = None
            if sc["id"] == "A-3":
                # show the banked component alone, clearly labelled
                amount = (base * banked_pct / Decimal("100")).quantize(CENT, rounding=ROUND_HALF_UP)
                new_rent = (base + amount).quantize(CENT, rounding=ROUND_HALF_UP)
            else:
                amount = None
                new_rent = None

        threshold = total if total is not None else banked_pct
        days = 90 if threshold > Decimal("10") else 30
        serve_by = eff - timedelta(days=days)
        mail_by = eff - timedelta(days=days + 5)

        rows.append({
            "id": sc["id"], "unit": u["label"], "eff": eff, "title": sc["title"],
            "banked_pct": banked_pct, "annual_pct": annual_pct,
            "annual_known": annual_known, "total": total,
            "amount": amount, "new_rent": new_rent,
            "days": days, "serve_by": serve_by, "mail_by": mail_by,
            "note": sc["note"], "src": sc["src"],
        })
    return rows


SCEN = compute_scenarios()


# ------------------------------------------------------------------- fragments
def unit_summary_table():
    head = ["Unit", "Tenancy start", "Rent at start (as reported)", "Occupants then → now",
            "Last recorded change", "Anniversary date", "Next anniversary after today",
            "Rent Increase Licence on file", "Source"]
    rows = []
    for key in ("A", "B"):
        u = UNITS[key]
        md = u["anniversary_md"]
        if md == "(unresolved)":
            nxt = "2027-02-01 or 2027-04-01 — see F-01"
        else:
            mm, dd = (int(x) for x in md.split("-"))
            cand = date(TODAY.year, mm, dd)
            nxt = longdate(cand if cand > TODAY else date(TODAY.year + 1, mm, dd))
        rows.append({
            "cells": [
                "<strong>{}</strong>".format(u["label"]),
                longdate(u["start"]),
                money(u["base"]),
                "{} → {}".format(u["occupants_start"], u["occupants_now"]),
                u["last_change"],
                u["anniversary"],
                nxt,
                blank_cell(),
                "",
            ],
            "src": ["S03", "S04", "S02"],
        })
    return {
        "type": "table",
        "caption": "The two units, exactly as reported — anonymised, dates and amounts unchanged",
        "head": head,
        "rows": rows,
    }


def scenario_table():
    head = ["Scenario", "Unit", "Effective date", "Banked %", "Annual %", "Total %",
            "Monthly increase", "New monthly rent", "Notice", "Serve by",
            "Serve by (if mailed)", "Notes", "Source"]
    rows = []
    for r in SCEN:
        annual_cell = pct(r["annual_pct"]) if r["annual_known"] else blank_cell()
        if r["total"] is not None:
            total_cell = pct(r["total"])
        else:
            total_cell = blank_cell()
        amount_cell = money(r["amount"]) if r["amount"] is not None else blank_cell()
        rent_cell = money(r["new_rent"]) if r["new_rent"] is not None else blank_cell()
        rows.append({
            "cells": [
                '<strong>{}</strong><br><span class="muted">{}</span>'.format(
                    esc(r["id"]), esc(r["title"])),
                r["unit"],
                longdate(r["eff"]),
                pct(r["banked_pct"]),
                annual_cell,
                total_cell,
                amount_cell,
                rent_cell,
                "{} days".format(r["days"]),
                longdate(r["serve_by"]),
                longdate(r["mail_by"]),
                '<span class="muted">{}</span>'.format(esc(r["note"])),
                "",
            ],
            "src": r["src"],
        })
    return {
        "type": "table",
        "caption": "Scenario arithmetic — reproducible from the published rate table and the reported rents. "
                   "These are calculations, not certified lawful maxima: see the flagged items below each table.",
        "head": head,
        "rows": rows,
    }


def rate_table():
    head = ["Effective period", "Allowable increase", "Note", "Source"]
    rows = []
    for p in PERIODS:
        rows.append({
            "cells": [longperiod(p), "<strong>{}%</strong>".format(p["pct"]),
                      esc(p["caution"]) or "", ""],
            "src": ["S06"],
        })
    return {
        "type": "table",
        "caption": "Rent Board Form 571 — Allowable Annual Increases, transcribed line by line "
                   "({} published periods)".format(len(PERIODS)),
        "head": head,
        "rows": rows,
    }


def flag_table(ids=None):
    head = ["Flag", "Severity", "Item", "What it means", "Source"]
    rows = []
    for f in FLAGS:
        if ids is not None and f["id"] not in ids:
            continue
        rows.append({
            "cells": [
                '<span id="{i}" class="flagid">{i}</span>'.format(i=f["id"]),
                '<span class="sev sev-{}">{}</span>'.format(f["severity"], f["severity"]),
                "<strong>{}</strong>".format(esc(f["title"])),
                esc(f["detail"]),
                "",
            ],
            "src": f["src"],
        })
    return {"type": "table", "caption": "Flagged items", "head": head, "rows": rows}


def source_table():
    head = ["ID", "Publisher", "Title", "Type", "Passage relied on", "Link"]
    rows = []
    for s in SRC["sources"]:
        rows.append({
            "cells": [
                '<span id="{i}" class="flagid">{i}</span>'.format(i=s["id"]),
                esc(s["publisher"]),
                esc(s["title"]),
                esc(s["kind"]),
                '<span class="muted">{}</span>'.format(esc(s["verified_passage"])),
                '<a class="ext" href="{u}" rel="noopener noreferrer" target="_blank">official source &nearr;</a>'.format(
                    u=esc(s["url"])),
            ],
            "src": [],  # the source table IS the registry; links are external and official
        })
    return {
        "type": "table",
        "caption": "All {} official sources, fetched and read on {}. No secondary source is used as a "
                   "substitute for a primary one.".format(len(SRC["sources"]), SRC["retrieved"]),
        "head": head,
        "rows": rows,
    }


INCLUDES = {
    "unit_summary_table": unit_summary_table,
    "scenario_table": scenario_table,
    "rate_table": rate_table,
    "flag_table": flag_table,
    "source_table": source_table,
}


def resolve_include(name, arg=None):
    if name == "flag_table_cond":
        ids = {"F-02", "F-03", "F-07", "F-08", "F-13", "F-17", "F-18", "F-20"}
        t = flag_table(ids)
        t["caption"] = "Flagged items that bear on the licence question"
        return t
    return INCLUDES[name]()


# ---------------------------------------------------------------------- render
def render_table(block):
    head, rows = block["head"], block["rows"]
    out = ['<div class="tablewrap"><table class="data-table">']
    if block.get("caption"):
        out.append('<caption>{}</caption>'.format(block["caption"]))
    out.append("<thead><tr>")
    for h in head:
        out.append("<th>{}</th>".format(h))
    out.append("</tr></thead><tbody>")
    for row in rows:
        cells = list(row["cells"])
        links = src_links(row.get("src"))
        if head[-1] == "Source":
            cells[-1] = links
        else:
            cells.append(links)
        out.append("<tr>")
        for c in cells:
            cls = ' class="c-src"' if c == links and links else ""
            out.append("<td{}>{}</td>".format(cls, c if c != "" else '<span class="muted">&mdash;</span>'))
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def render_block(block):
    kind = block["type"]
    if kind == "include":
        return render_block(resolve_include(block["name"], block.get("arg")))
    if kind == "table":
        return render_table(block)
    if kind == "callout":
        return ('<section class="callout {cls}"><h3>{h}</h3>{b}</section>'.format(
            cls=block.get("cls", ""), h=block["head"], b=block["body"]))
    if kind == "cards":
        items = "".join(
            '<a class="cardlink" href="{h}"><strong>{t}</strong><span>{d}</span></a>'.format(
                h=i["href"], t=i["title"], d=i["desc"])
            for i in block["items"])
        return '<h2>{}</h2><div class="cards">{}</div>'.format(block["head"], items)
    if kind == "prose":
        return "<section>{}</section>".format(block["body"])
    raise SystemExit("unknown block type: {}".format(kind))


NAV = [(p["file"], p["nav"]) for p in PAGES]


def nav_html(current: str) -> str:
    items = []
    for href, label in NAV:
        here = ' aria-current="page"' if href == current else ""
        items.append('<a href="{}"{}>{}</a>'.format(href, here, label))
    return '<nav class="main" aria-label="Main">' + "".join(items) + "</nav>"


def page_html(p: dict) -> str:
    body = "\n".join(render_block(b) for b in p["blocks"])
    pills = "".join('<span class="pill">{}</span>'.format(x) for x in p["pills"])
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap navwrap">
    <a class="brand" href="index.html"><span class="mark">SF</span><span>Rent Increase<small>Decision pack &middot; Outer Sunset 94122</small></span></a>
    {nav}
  </div>
</header>
<section class="hero"><div class="wrap">
<p class="eyebrow">{eyebrow}</p>
<h1>{h1}</h1>
<p class="lede">{lede}</p>
<div class="pillrow">{pills}</div>
</div></section>
<main class="wrap" id="main">
{body}
</main>
<footer class="site-footer"><div class="wrap">
<p><strong>Anonymised.</strong> {privacy}</p>
<p><strong>Verified live {retrieved}.</strong> All {n} registered official sources were fetched and read on that date. Dollar figures are conditional scenario arithmetic on the reported rents, not certified lawful maxima. Values that no official source publishes are left blank and listed on <a href="flagged.html">Flagged for Review</a>.</p>
<p><strong>{legal}</strong></p>
<p class="muted">This is the <code>/decision/</code> edition, published alongside the repository's existing editions. It is additive: it changes none of them. <a href="repoaudit.html">Repository audit &rarr;</a></p>
</div></footer>
</body>
</html>
""".format(
        title=esc(p["title"]), desc=esc(p["desc"]), nav=nav_html(p["file"]),
        eyebrow=p["eyebrow"], h1=p["h1"], lede=p["lede"], pills=pills, body=body,
        privacy=META["privacy_note"], retrieved=META["retrieved"],
        n=len(SRC["sources"]), legal=META["not_legal_advice"],
    )


CSS = """
:root{
  --ink:#12181f; --ink2:#3d4a58; --muted:#6b7887; --line:#e2e8ef; --line2:#eef2f7;
  --bg:#f6f8fb; --card:#ffffff; --brand:#1f4e79; --brand2:#2c6aa8;
  --ok:#1a7f5a; --warn:#8a5a00; --bad:#a3272b; --flag:#7a5ab8;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.62 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:1180px;margin:0 auto;padding:0 22px}
a{color:var(--brand2)}
a:hover{color:var(--brand)}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px 12px;z-index:99;border-radius:6px}

.site-header{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.navwrap{display:flex;flex-wrap:wrap;align-items:center;gap:18px;padding-top:12px;padding-bottom:12px}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-weight:700}
.brand .mark{display:grid;place-items:center;width:32px;height:32px;border-radius:8px;
  background:var(--brand);color:#fff;font-size:14px;letter-spacing:.5px}
.brand small{display:block;font-weight:500;color:var(--muted);font-size:11.5px;letter-spacing:.3px}
nav.main{display:flex;flex-wrap:wrap;gap:2px;margin-left:auto}
nav.main a{padding:7px 11px;border-radius:7px;text-decoration:none;color:var(--ink2);font-size:13.5px;font-weight:600}
nav.main a:hover{background:var(--line2);color:var(--brand)}
nav.main a[aria-current]{background:var(--brand);color:#fff}

.hero{background:linear-gradient(180deg,#ffffff,#eef3f9);border-bottom:1px solid var(--line);padding:34px 0 30px}
.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:11.5px;color:var(--brand2);font-weight:700;margin:0 0 10px}
.hero h1{margin:0 0 14px;font-size:clamp(26px,3.6vw,40px);line-height:1.18;letter-spacing:-.02em;max-width:26ch}
.lede{margin:0;font-size:17px;color:var(--ink2);max-width:82ch}
.pillrow{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.pill{background:#fff;border:1px solid var(--line);border-radius:999px;padding:5px 13px;font-size:12.5px;color:var(--ink2);font-weight:600}

main{padding:30px 0 60px}
main section{margin:0 0 34px}
h2{font-size:22px;letter-spacing:-.01em;margin:38px 0 14px;padding-bottom:8px;border-bottom:2px solid var(--line)}
h3{font-size:17.5px;margin:0 0 10px}
p{margin:0 0 12px}
.muted{color:var(--muted)}
code{background:var(--line2);padding:1px 5px;border-radius:4px;font-size:13px}

.callout{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--brand2);
  border-radius:10px;padding:20px 22px;margin:0 0 22px}
.callout h3{margin-top:0}
.callout.answer{border-left-color:var(--ok);background:#f4fbf7}
.callout.warn{border-left-color:var(--warn);background:#fffaf0}
.callout.steps{border-left-color:var(--brand)}
.callout p:last-child{margin-bottom:0}

ol.steps{margin:8px 0 0;padding-left:22px}
ol.steps li{margin:0 0 11px}
ul.plain{margin:8px 0 0;padding-left:20px}
ul.plain li{margin:0 0 8px}

.tablewrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px;margin:0 0 24px}
table.data-table{width:100%;border-collapse:collapse;font-size:14px}
table.data-table caption{caption-side:top;text-align:left;padding:15px 18px 11px;font-size:13.5px;
  color:var(--ink2);font-weight:600;border-bottom:1px solid var(--line)}
table.data-table th{background:#f8fafc;text-align:left;padding:11px 14px;font-size:12px;
  text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);border-bottom:1px solid var(--line);white-space:nowrap}
table.data-table td{padding:11px 14px;border-bottom:1px solid var(--line2);vertical-align:top}
table.data-table tbody tr:last-child td{border-bottom:0}
table.data-table tbody tr:hover{background:#fbfdff}
td.c-src{white-space:nowrap;width:1%}

.srcref{display:inline-block;background:#eaf2fa;color:var(--brand);border:1px solid #cfe0ef;
  border-radius:5px;padding:1px 6px;font-size:11.5px;font-weight:700;text-decoration:none;margin:1px 2px 1px 0}
.srcref:hover{background:var(--brand);color:#fff}
.blank{display:inline-block;background:#f3eefb;color:var(--flag);border:1px dashed #cbb8ea;
  border-radius:5px;padding:1px 7px;font-size:11.5px;font-weight:700}
.flagid{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;font-weight:700;color:var(--brand)}
.sev{display:inline-block;border-radius:5px;padding:1px 7px;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.04em}
.sev-high{background:#fdecec;color:var(--bad)}
.sev-medium{background:#fff5e0;color:var(--warn)}
.sev-info{background:#eaf2fa;color:var(--brand2)}
.ext{white-space:nowrap;font-weight:600}

.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(268px,1fr));gap:12px;margin-top:14px}
.cardlink{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;
  padding:15px 16px;text-decoration:none;color:var(--ink)}
.cardlink:hover{border-color:var(--brand2);box-shadow:0 3px 14px rgba(31,78,121,.10)}
.cardlink strong{display:block;margin-bottom:4px;color:var(--brand)}
.cardlink span{display:block;font-size:13px;color:var(--ink2)}

.site-footer{background:#0f1720;color:#b9c6d4;padding:30px 0 40px;font-size:13.5px}
.site-footer a{color:#8fc3ea}
.site-footer .muted{color:#7d8d9d}
.site-footer p{margin:0 0 9px;max-width:95ch}

@media (max-width:720px){
  .navwrap{gap:10px}
  nav.main{margin-left:0;width:100%}
  .hero{padding:24px 0 22px}
  table.data-table{font-size:13px}
}
"""


def main() -> None:
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "assets" / "style.css").write_text(CSS.lstrip(), encoding="utf-8")
    written = []
    for p in PAGES:
        (OUT / p["file"]).write_text(page_html(p), encoding="utf-8")
        written.append(p["file"])
    print("wrote {} pages: {}".format(len(written), ", ".join(written)))
    print("sources: {} | rates: {} | flags: {} | scenarios: {}".format(
        len(SRC["sources"]), len(PERIODS), len(FLAGS), len(SCEN)))


if __name__ == "__main__":
    main()
