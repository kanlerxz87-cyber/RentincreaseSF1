#!/usr/bin/env python3
"""Comprehensive line-by-line quality gate for /guide/ and audit/session-5d4a1320/.

Verifies:
  1. Byte-identical deterministic build reproducibility of all 10 HTML pages + SOURCES.md
  2. Official government domain allowlist & 2026-11-10 retrieval metadata on all 33 sources
  3. 100% of <tbody><tr> rows across all 10 pages carry a direct registered official URL link
  4. 100% of internal href/src relative links and #anchors resolve cleanly + 10-page nav parity
  5. Strict blank-cell enforcement (<td class="blank-official"></td> == "") on all unverified items
  6. Independent exact rational (fractions.Fraction) & calendar arithmetic for all scenarios
  7. SHA-256 digest & regex privacy scan confirming zero personal tokens or private emails
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
from datetime import date, timedelta
from decimal import Decimal
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
GUIDE_DIR = ROOT / "guide"
AUDIT_DIR = ROOT / "audit" / "session-5d4a1320"

sys.path.insert(0, str(ROOT / "tools"))
from check_links import FORBIDDEN_HASHES  # noqa: E402

OFFICIAL_DOMAINS = {
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

EXPECTED_PAGES = [
    "index.html",
    "licensing.html",
    "units-and-rates.html",
    "legal-framework.html",
    "market-practices.html",
    "tenant-notice.html",
    "lawyer-scrutiny.html",
    "repo-audit.html",
    "sources.html",
    "flagged-for-review.html",
]

errors: list[str] = []
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    if not cond:
        errors.append(msg)


class PageInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.nav_hrefs: list[str] = []
        self.in_nav = False
        self.in_tbody = False
        self.in_tr = False
        self.tr_links: list[str] = []
        self.rows: list[list[str]] = []
        self.in_blank_td = False
        self.blank_td_contents: list[str] = []
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = dict(attrs)
        if ad.get("id"):
            self.ids.add(ad["id"] or "")
        if tag == "nav":
            self.in_nav = True
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.tr_links = []
        elif tag == "td" and "blank-official" in (ad.get("class") or ""):
            self.in_blank_td = True
            self._buf = []
        if tag in ("a", "link", "script") and ad.get("href" if tag != "script" else "src"):
            val = (ad.get("href") if tag != "script" else ad.get("src")) or ""
            self.links.append(val)
            if self.in_nav and tag == "a":
                self.nav_hrefs.append(val)
            if self.in_tr and tag == "a":
                self.tr_links.append(val)

    def handle_data(self, data: str) -> None:
        if self.in_blank_td:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav":
            self.in_nav = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "tr" and self.in_tr:
            self.rows.append(self.tr_links)
            self.in_tr = False
        elif tag == "td" and self.in_blank_td:
            self.blank_td_contents.append("".join(self._buf))
            self.in_blank_td = False


def main() -> int:
    sources = json.loads((AUDIT_DIR / "sources.json").read_text(encoding="utf-8"))
    data = json.loads((AUDIT_DIR / "site_data.json").read_text(encoding="utf-8"))

    # 1. Source registry verification
    check(len(sources) == 33, f"expected 33 official sources, got {len(sources)}")
    registered_urls: set[str] = set()
    for s in sources:
        sid = s["id"]
        u = urlsplit(s["url"])
        check(u.scheme == "https", f"{sid}: URL must use https ({s['url']})")
        check(u.hostname in OFFICIAL_DOMAINS, f"{sid}: non-official host {u.hostname}")
        check(s.get("retrieved") == "2026-11-10", f"{sid}: expected retrieved=2026-11-10")
        check(len(s.get("verbatim_quote", "").strip()) >= 40, f"{sid}: verbatim quote missing/short")
        registered_urls.add(s["url"])

    # 2. Deterministic build check
    before = {p: (GUIDE_DIR / p).read_bytes() for p in EXPECTED_PAGES if (GUIDE_DIR / p).is_file()}
    before_md = (AUDIT_DIR / "SOURCES.md").read_bytes()
    sys.path.insert(0, str(GUIDE_DIR))
    import build as guide_build  # noqa: E402
    guide_build.main()
    for p in EXPECTED_PAGES:
        check((GUIDE_DIR / p).is_file(), f"missing generated page guide/{p}")
        if p in before:
            check((GUIDE_DIR / p).read_bytes() == before[p], f"non-deterministic rebuild diff in guide/{p}")
    check((AUDIT_DIR / "SOURCES.md").read_bytes() == before_md, "non-deterministic rebuild diff in SOURCES.md")

    # 3. Parse all 10 pages
    parsed: dict[str, PageInspector] = {}
    for p in EXPECTED_PAGES:
        ins = PageInspector()
        ins.feed((GUIDE_DIR / p).read_text(encoding="utf-8"))
        parsed[p] = ins

    # 4. Navigation parity, link/anchor resolution, and source-per-row verification
    ref_nav = parsed["index.html"].nav_hrefs
    check(ref_nav == EXPECTED_PAGES, f"index.html nav mismatch: {ref_nav}")
    total_rows = 0
    total_blank_cells = 0

    for p, ins in parsed.items():
        check(ins.nav_hrefs == ref_nav, f"{p}: nav differs from index.html")
        for idx, row_links in enumerate(ins.rows, start=1):
            total_rows += 1
            official_row_links = [h for h in row_links if h in registered_urls]
            check(bool(official_row_links), f"guide/{p} row #{idx}: missing registered official source URL link")

        for btxt in ins.blank_td_contents:
            total_blank_cells += 1
            check(btxt == "", f"guide/{p}: blank-official cell is non-empty ({btxt!r})")

        for href in ins.links:
            if href.startswith(("mailto:", "tel:")):
                continue
            u = urlsplit(href)
            if u.scheme:
                check(u.scheme == "https" and u.hostname in OFFICIAL_DOMAINS, f"guide/{p}: non-official external link {href}")
            else:
                target_path = (GUIDE_DIR / unquote(u.path)).resolve() if u.path else (GUIDE_DIR / p).resolve()
                check(target_path.is_file(), f"guide/{p}: broken relative link {href}")
                if u.fragment and target_path.parent == GUIDE_DIR.resolve() and target_path.name in parsed:
                    check(u.fragment in parsed[target_path.name].ids, f"guide/{p}: missing anchor #{u.fragment} in {target_path.name}")

    # Verify exact blank-cell counts (7 on index.html, 1 on units-and-rates.html, 15 on flagged-for-review.html = 23)
    check(len(parsed["flagged-for-review.html"].blank_td_contents) == 15, "flagged-for-review.html must have 15 strictly blank official-value cells")
    check(len(parsed["index.html"].blank_td_contents) == 7, "index.html must have 7 strictly blank official-value cells")
    check(len(parsed["units-and-rates.html"].blank_td_contents) == 1, "units-and-rates.html must have 1 strictly blank 2027-2028 rate cell")

    # 5. Independent exact arithmetic & calendar date verification (using fractions.Fraction)
    for sc in data["scenarios"]:
        sid = sc["scenario_id"]
        base = Fraction(sc["base_rent"])
        ann_pct = Fraction(sc["annual_pct"])
        bnk_pct = Fraction(sc["banked_pct"])
        tot_pct = Fraction(sc["total_pct"])
        check(ann_pct + bnk_pct == tot_pct, f"{sid}: annual_pct + banked_pct != total_pct")

        ann_dlr = base * ann_pct / 100
        bnk_dlr = base * bnk_pct / 100
        tot_dlr = base * tot_pct / 100
        check(ann_dlr == Fraction(sc["annual_dollars"]), f"{sid}: annual_dollars mismatch ({ann_dlr})")
        check(bnk_dlr == Fraction(sc["banked_dollars"]), f"{sid}: banked_dollars mismatch ({bnk_dlr})")
        check(tot_dlr == Fraction(sc["total_increase_dollars"]), f"{sid}: total_increase_dollars mismatch ({tot_dlr})")
        check(base + tot_dlr == Fraction(sc["new_base_rent"]), f"{sid}: new_base_rent mismatch")

        eff = date.fromisoformat(sc["illustrative_effective_date"])
        exp_p_days = 90 if tot_pct > Fraction(10) else 30
        check(sc["personal_service_days"] == exp_p_days, f"{sid}: wrong personal_service_days")
        check(sc["ca_mail_days"] == exp_p_days + 5, f"{sid}: wrong ca_mail_days")
        check(date.fromisoformat(sc["personal_service_deadline"]) == eff - timedelta(days=exp_p_days), f"{sid}: personal_service_deadline mismatch")
        check(date.fromisoformat(sc["ca_mail_deadline"]) == eff - timedelta(days=exp_p_days + 5), f"{sid}: ca_mail_deadline mismatch")

    # Verify Unit 2 year-by-year banking sum
    u2_base = Fraction("3150.00")
    bank_rows = data["unit2_banked_breakdown"]
    six_pct_sum = sum(Fraction(r["pct"]) for r in bank_rows[:6])
    six_dlr_sum = sum(Fraction(r["dollar_on_3150"]) for r in bank_rows[:6])
    check(six_pct_sum == Fraction("11.5"), f"Unit 2 6-year banked pct sum != 11.5 ({six_pct_sum})")
    check(six_dlr_sum == Fraction("362.25"), f"Unit 2 6-year banked dollar sum != 362.25 ({six_dlr_sum})")
    for r in bank_rows:
        check(u2_base * Fraction(r["pct"]) / 100 == Fraction(r["dollar_on_3150"]), f"Unit 2 row {r['anniversary_date']} dollar mismatch")
        check(Decimal(r["dollar_on_3150"]) >= 0, "negative component")

    # 6. Markdown link check inside audit/session-5d4a1320/
    for md_path in sorted(AUDIT_DIR.glob("*.md")):
        txt = md_path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", txt):
            if target.startswith(("https://", "http://", "mailto:", "tel:", "#")):
                continue
            rel_file = target.split("#", 1)[0]
            if rel_file:
                check((md_path.parent / rel_file).exists(), f"{md_path.name}: broken relative link {target}")

    # 7. SHA-256 Personal-Identifier & Privacy Scan across guide/** and audit/session-5d4a1320/**
    token_re = re.compile(r"\b(?:[A-Z]{2}|[A-Z] [A-Z])\b")
    email_re = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    scanned_files = 0
    for folder in (GUIDE_DIR, AUDIT_DIR):
        for fp in sorted(folder.rglob("*")):
            if not fp.is_file() or "__pycache__" in fp.parts:
                continue
            scanned_files += 1
            raw = fp.read_text(encoding="utf-8")
            for tok in token_re.findall(raw):
                if hashlib.sha256(tok.encode()).hexdigest() in FORBIDDEN_HASHES:
                    errors.append(f"{fp.relative_to(ROOT)}: forbidden personal token detected")
            for tok in token_re.findall(html.unescape(re.sub(r"<[^>]+>", " ", raw))):
                if hashlib.sha256(tok.encode()).hexdigest() in FORBIDDEN_HASHES:
                    errors.append(f"{fp.relative_to(ROOT)}: forbidden personal token detected in stripped text")
            for em in email_re.findall(raw):
                errors.append(f"{fp.relative_to(ROOT)}: unexpected email address {em}")

    check(scanned_files >= 18, f"expected >=18 files scanned in scope, got {scanned_files}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"\n{len(errors)} error(s) out of {checks} checks.", file=sys.stderr)
        return 1

    print(
        f"PASS: {checks} checks, 0 errors | {len(EXPECTED_PAGES)} HTML pages | "
        f"{total_rows} source-linked table rows | {len(sources)} official .gov sources | "
        f"{total_blank_cells} strictly blank unverified cells | {scanned_files} files privacy-verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
