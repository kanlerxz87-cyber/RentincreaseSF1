#!/usr/bin/env python3
"""Automated line-by-line verification suite for /compliance/ and audit/session-ba230459/."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from decimal import Decimal, ROUND_DOWN
from fractions import Fraction
from html.parser import HTMLParser
from urllib.parse import urlparse

COMPLIANCE_DIR = pathlib.Path(__file__).resolve().parent
REPO_ROOT = COMPLIANCE_DIR.parent
AUDIT_DIR = REPO_ROOT / "audit" / "session-ba230459"

sys.path.insert(0, str(REPO_ROOT / "tools"))
from check_links import FORBIDDEN_HASHES  # noqa: E402

ALLOWED_OFFICIAL_HOSTS = {
    "www.sf.gov",
    "sf.gov",
    "portal.sfrb.org",
    "sftreasurer.org",
    "sfgov.legistar.com",
    "leginfo.legislature.ca.gov",
    "www4.courts.ca.gov",
    "www.govinfo.gov",
    "www.hud.gov",
    "www.justice.gov",
    "www.census.gov",
}

ALLOWED_PUBLIC_PHONES = {
    "415-252-4600",
    "415-701-2311",
    "415-735-4124",
    "415-703-8644",
    "415-947-9085",
    "415-282-6622",
    "415-659-9184",
    "415-982-1300",
    "415-647-2419",
    "415-255-2288",
    "415-989-1616",
}

EXPECTED_HTML_FILES = [
    "index.html",
    "licensing.html",
    "units-and-rates.html",
    "notice-and-reasons.html",
    "practices.html",
    "fair-housing.html",
    "lawyer-scrutiny.html",
    "repo-audit.html",
    "flagged.html",
    "sources.html",
]


class PageAuditParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.has_viewport = False
        self.has_title = False
        self.in_title = False
        self.title_text = ""
        self.in_tbody = False
        self.in_tr = False
        self.in_td = False
        self.current_tr_links: list[str] = []
        self.current_tr_tds: list[tuple[str, str]] = []
        self.current_td_class = ""
        self.current_td_buf: list[str] = []
        self.tbody_rows: list[tuple[list[str], list[tuple[str, str]]]] = []
        self.aria_current: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = {k: (v or "") for k, v in attrs}
        if amap.get("id"):
            self.ids.add(amap["id"])
        if tag == "meta" and amap.get("name") == "viewport" and "width=device-width" in amap.get("content", ""):
            self.has_viewport = True
        if tag == "title":
            self.in_title = True
            self.has_title = True
        if tag in ("a", "link", "script"):
            target = amap.get("href") or amap.get("src")
            if target:
                self.links.append(target)
                if self.in_tr and tag == "a" and amap.get("href"):
                    self.current_tr_links.append(amap["href"])
            if tag == "a" and amap.get("aria-current") == "page":
                self.aria_current.append(amap.get("href", ""))
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.current_tr_links = []
            self.current_tr_tds = []
        elif tag == "td" and self.in_tr:
            self.in_td = True
            self.current_td_class = amap.get("class", "")
            self.current_td_buf = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text += data
        if self.in_td:
            self.current_td_buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "td" and self.in_td:
            self.in_td = False
            self.current_tr_tds.append((self.current_td_class, "".join(self.current_td_buf)))
        elif tag == "tr" and self.in_tr:
            self.in_tr = False
            self.tbody_rows.append((self.current_tr_links, self.current_tr_tds))
        elif tag == "tbody":
            self.in_tbody = False


def trunc_cents_decimal(base: Decimal, pct: Decimal) -> Decimal:
    return (base * pct / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def trunc_cents_fraction(base_str: str, pct_str: str) -> Decimal:
    f_val = Fraction(base_str) * Fraction(pct_str) / Fraction(100)
    cents = int(f_val * 100)
    return Decimal(cents) / Decimal(100)


def main() -> int:
    checks = 0
    errors: list[str] = []

    def ok(cond: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not cond:
            errors.append(msg)

    # 1. Byte-idempotent build check
    before = {
        f: (COMPLIANCE_DIR / f).read_bytes()
        for f in EXPECTED_HTML_FILES
        if (COMPLIANCE_DIR / f).exists()
    }
    res = subprocess.run(
        [sys.executable, str(COMPLIANCE_DIR / "build.py")],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    ok(res.returncode == 0, f"compliance/build.py exited non-zero: {res.stderr}")
    after = {f: (COMPLIANCE_DIR / f).read_bytes() for f in EXPECTED_HTML_FILES}
    ok(before == after, "compliance/build.py is not byte-idempotent with committed HTML")

    # 2. Load & verify official sources
    sources = json.loads((COMPLIANCE_DIR / "data" / "sources.json").read_text(encoding="utf-8"))
    audit_sources = json.loads((AUDIT_DIR / "sources_2026_11_10.json").read_text(encoding="utf-8"))
    ok(sources == audit_sources, "compliance/data/sources.json and audit/session-ba230459/sources_2026_11_10.json differ")
    ok(len(sources) == 37, f"Expected 37 official sources, got {len(sources)}")

    official_urls: set[str] = set()
    source_ids: set[str] = set()
    for s in sources:
        sid = s["id"]
        source_ids.add(sid)
        parsed = urlparse(s["url"])
        ok(parsed.scheme == "https", f"{sid}: non-HTTPS URL {s['url']}")
        ok(parsed.netloc in ALLOWED_OFFICIAL_HOSTS, f"{sid}: unauthorized host {parsed.netloc}")
        ok(s["retrieved"] == "2026-11-10", f"{sid}: expected retrieved 2026-11-10, got {s['retrieved']}")
        ok(len(s["quote"].strip()) >= 40, f"{sid}: quote too short")
        official_urls.add(s["url"])

    # 3. Independent dual arithmetic & calendar verification
    site_data = json.loads((COMPLIANCE_DIR / "data" / "site_data.json").read_text(encoding="utf-8"))
    hub_data = json.loads((REPO_ROOT / "hub" / "data.json").read_text(encoding="utf-8"))

    # Cross-check all 46 Form 571 periods against canonical hub/data.json
    ok(len(site_data["rates"]) == 46, f"Expected 46 Form 571 rows, got {len(site_data['rates'])}")
    for idx, (r_comp, r_hub) in enumerate(zip(site_data["rates"], hub_data["rates"])):
        ok(
            (r_comp["start"], r_comp["end"], r_comp["pct"]) == (r_hub["start"], r_hub["end"], r_hub["pct"]),
            f"Form 571 mismatch at index {idx}: {r_comp} vs {r_hub}",
        )

    # Verify Unit 2 banked components
    u2_pct_sum = Decimal("0")
    u2_amt_sum = Decimal("0")
    for comp in site_data["u2_banked_components"]:
        d_amt = trunc_cents_decimal(Decimal("3150.00"), Decimal(comp["pct"]))
        f_amt = trunc_cents_fraction("3150.00", comp["pct"])
        ok(d_amt == f_amt == Decimal(comp["dollar_on_3150"]), f"U2 banked math mismatch on {comp['anniversary']}")
        u2_pct_sum += Decimal(comp["pct"])
        u2_amt_sum += d_amt
    ok(u2_pct_sum == Decimal("11.5"), f"Expected U2 banked sum 11.5%, got {u2_pct_sum}")
    ok(u2_amt_sum == Decimal("362.25"), f"Expected U2 banked dollars $362.25, got {u2_amt_sum}")

    # Verify all 5 scenarios (Decimal + Fraction + Date math)
    for scen in site_data["scenarios"]:
        base = Decimal(scen["base_rent"])
        ann = Decimal(scen["annual_pct"])
        bnk = Decimal(scen["banked_pct"])
        tot = Decimal(scen["total_pct"])
        ok(ann + bnk == tot, f"{scen['id']}: non-additive pct {ann} + {bnk} != {tot}")
        d_inc = trunc_cents_decimal(base, tot)
        f_inc = trunc_cents_fraction(scen["base_rent"], scen["total_pct"])
        ok(d_inc == f_inc == Decimal(scen["increase_amt"]), f"{scen['id']}: increase_amt mismatch")
        ok(base + d_inc == Decimal(scen["new_rent"]), f"{scen['id']}: new_rent mismatch")

        eff = dt.date.fromisoformat(scen["effective_date"])
        exp_days = 90 if tot > Decimal("10.0") else 30
        ok(scen["personal_notice_days"] == exp_days, f"{scen['id']}: wrong personal notice days")
        ok(scen["ca_mail_days"] == exp_days + 5, f"{scen['id']}: wrong CA mail notice days")
        ok(
            dt.date.fromisoformat(scen["personal_by"]) == eff - dt.timedelta(days=exp_days),
            f"{scen['id']}: wrong personal_by date",
        )
        ok(
            dt.date.fromisoformat(scen["ca_mail_by"]) == eff - dt.timedelta(days=exp_days + 5),
            f"{scen['id']}: wrong ca_mail_by date",
        )

    # 4. Parse all 10 HTML pages & verify every table row, blank cell, and link
    parsed_pages: dict[str, PageAuditParser] = {}
    for fname in EXPECTED_HTML_FILES:
        fpath = COMPLIANCE_DIR / fname
        ok(fpath.exists(), f"Missing generated HTML page: {fname}")
        parser = PageAuditParser()
        parser.feed(fpath.read_text(encoding="utf-8"))
        parsed_pages[fname] = parser
        ok(parser.has_viewport, f"{fname}: missing responsive viewport meta")
        ok(parser.has_title and len(parser.title_text.strip()) > 10, f"{fname}: missing title")
        ok(parser.aria_current == [fname], f"{fname}: expected aria-current={[fname]}, got {parser.aria_current}")
        ok(len(parser.tbody_rows) > 0, f"{fname}: expected at least 1 data table row")

    total_tbody_rows = 0
    blank_cells_index = 0
    blank_cells_flagged = 0

    for fname, parser in parsed_pages.items():
        for row_idx, (tr_links, tr_tds) in enumerate(parser.tbody_rows, start=1):
            total_tbody_rows += 1
            has_official_ext = any(link in official_urls for link in tr_links)
            has_source_ref = any(
                link.startswith("sources.html#CS") and link.split("#", 1)[1] in parsed_pages["sources.html"].ids
                for link in tr_links
            )
            ok(has_official_ext, f"{fname} row {row_idx}: missing direct official .gov source link")
            ok(has_source_ref, f"{fname} row {row_idx}: missing resolving sources.html#CSxx anchor")
            for td_cls, td_txt in tr_tds:
                if "blank-unverified" in td_cls:
                    ok(td_txt == "", f"{fname} row {row_idx}: blank-unverified cell must be empty, got {td_txt!r}")
                    if fname == "index.html":
                        blank_cells_index += 1
                    elif fname == "flagged.html":
                        blank_cells_flagged += 1

        # Verify all local links & anchors resolve
        for link in parser.links:
            if link.startswith(("https://", "http://", "mailto:", "tel:")):
                ok(not link.startswith("http://"), f"{fname}: insecure http:// link {link}")
                continue
            path_part, _, frag = link.partition("#")
            target_path = (COMPLIANCE_DIR / path_part).resolve() if path_part else (COMPLIANCE_DIR / fname).resolve()
            ok(target_path.exists(), f"{fname}: broken relative link {link}")
            if frag and target_path.parent == COMPLIANCE_DIR and target_path.name in parsed_pages:
                ok(
                    frag in parsed_pages[target_path.name].ids,
                    f"{fname}: broken anchor #{frag} in {target_path.name}",
                )

    ok(blank_cells_index == 16, f"index.html: expected 16 blank unverified cells, got {blank_cells_index}")
    ok(blank_cells_flagged == 16, f"flagged.html: expected 16 blank unverified cells, got {blank_cells_flagged}")

    # 5. Markdown relative-link check + strict SHA-256 & pattern privacy scan
    md_link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    token_re = re.compile(r"\b(?:[A-Z]{2}|[A-Z] [A-Z])\b")
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone_re = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")

    scoped_files = sorted(
        p for base in (COMPLIANCE_DIR, AUDIT_DIR) for p in base.rglob("*") if p.is_file()
    )
    for fpath in scoped_files:
        text = fpath.read_text(encoding="utf-8")
        if fpath.suffix == ".md":
            for m in md_link_re.finditer(text):
                raw_target = m.group(1).strip()
                if raw_target.startswith(("https://", "http://", "#")):
                    ok(not raw_target.startswith("http://"), f"{fpath.name}: insecure http:// link {raw_target}")
                    continue
                rel_part = raw_target.split("#", 1)[0]
                ok((fpath.parent / rel_part).resolve().exists(), f"{fpath}: broken Markdown link {raw_target}")

        for tok in token_re.findall(text):
            digest = hashlib.sha256(tok.encode("utf-8")).hexdigest()
            ok(digest not in FORBIDDEN_HASHES, f"PRIVACY VIOLATION in {fpath}: matched forbidden initial token")

        for em in email_re.findall(text):
            ok(em.endswith("@sfgov.org"), f"Unexpected email address in {fpath}: {em}")

        for ph in phone_re.findall(text):
            norm = re.sub(r"[.\s]", "-", ph)
            ok(norm in ALLOWED_PUBLIC_PHONES, f"Unexpected phone number in {fpath}: {ph}")

    print(
        f"compliance/verify.py: PASS — {checks} checks, 0 errors "
        f"({len(EXPECTED_HTML_FILES)} HTML pages, {total_tbody_rows} source-linked table rows, "
        f"{len(sources)} live-verified official sources, {len(scoped_files)} scoped files privacy-scanned)."
        if not errors
        else f"compliance/verify.py: FAIL — {len(errors)} error(s) out of {checks} checks:\n  - "
        + "\n  - ".join(errors)
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
