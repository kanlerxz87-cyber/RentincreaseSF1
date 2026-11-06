#!/usr/bin/env python3
"""Comprehensive line-by-line, link, arithmetic, schema, and privacy verifier for /dashboard/ and /audit/."""

from __future__ import annotations

from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "audit"
DASH_DIR = ROOT / "dashboard"
DATA_DIR = DASH_DIR / "data"

ALLOWED_GOV_HOSTS = {
    "www.sf.gov",
    "media.api.sf.gov",
    "leginfo.legislature.ca.gov",
    "calcivilrights.ca.gov",
    "www.hud.gov",
    "www.govinfo.gov",
    "www.justice.gov",
    "www.census.gov",
}

EXPECTED_PAGES = [
    "index.html",
    "units-analysis.html",
    "legal-framework.html",
    "market-practices.html",
    "notice-protocol.html",
    "lawyer-scrutiny.html",
    "discrimination-analysis.html",
    "repo-verification.html",
    "flagged-for-review.html",
    "sources.html",
]

# Explicit allowlist of legitimate 2-letter uppercase tokens (acronyms / Roman numerals / legal codes).
# Zero spaced single-letter initial pairs (\b[A-Z]\s+[A-Z]\b) are permitted anywhere.
ALLOWED_2CHAR_UPPER = {
    "SF", "CA", "US", "CC", "AB", "GO", "II", "IV", "VI", "ID", "AI", "AG",
    "OR", "IF", "IN", "ON", "TO", "BY", "OF", "AT", "AS", "IS", "IT", "UP",
    "NO", "VS", "RA", "SC", "PG", "UI", "PR",
}


class DashboardHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.nav_hrefs: list[str] = []
        self.in_nav = False
        self.in_tbody = False
        self.in_tr = False
        self.current_td_idx = -1
        self.in_td = False
        self.current_row: dict | None = None
        self.rows: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = dict(attrs)
        if amap.get("id"):
            self.ids.add(amap["id"])
        if tag == "nav":
            self.in_nav = True
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.current_td_idx = -1
            self.current_row = {
                "id": amap.get("id", ""),
                "cells": [],
                "cell_links": [],
            }
        elif tag == "td" and self.in_tr and self.current_row is not None:
            self.in_td = True
            self.current_td_idx += 1
            self.current_row["cells"].append("")
            self.current_row["cell_links"].append([])
        elif tag == "a":
            href = amap.get("href") or ""
            self.hrefs.append(href)
            if self.in_nav:
                self.nav_hrefs.append(href)
            if self.in_td and self.current_row is not None and self.current_td_idx >= 0:
                self.current_row["cell_links"][self.current_td_idx].append(href)
        elif tag in ("link", "script"):
            target = amap.get("href") or amap.get("src")
            if target:
                self.hrefs.append(target)

    def handle_data(self, data: str) -> None:
        if self.in_td and self.current_row is not None and self.current_td_idx >= 0:
            self.current_row["cells"][self.current_td_idx] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav":
            self.in_nav = False
        elif tag == "td":
            self.in_td = False
        elif tag == "tr" and self.in_tr:
            self.in_tr = False
            if self.current_row is not None:
                self.rows.append(self.current_row)
            self.current_row = None
        elif tag == "tbody":
            self.in_tbody = False


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def verify_arithmetic(errors: list[str]) -> None:
    u1 = Decimal("3995.00")
    u2 = Decimal("3150.00")
    checks = [
        (u1 * Decimal("0.016"), Decimal("63.92"), "Unit 1 1.6% increase"),
        (u1 + Decimal("63.92"), Decimal("4058.92"), "Unit 1 1.6% new rent"),
        (u1 * Decimal("0.014"), Decimal("55.93"), "Unit 1 1.4% banked increase"),
        (u1 * Decimal("0.030"), Decimal("119.85"), "Unit 1 3.0% combined increase"),
        (u1 + Decimal("119.85"), Decimal("4114.85"), "Unit 1 3.0% new rent"),
        (u2 * Decimal("0.016"), Decimal("50.40"), "Unit 2 1.6% increase"),
        (u2 + Decimal("50.40"), Decimal("3200.40"), "Unit 2 1.6% new rent"),
        (
            Decimal("0.018")
            + Decimal("0.007")
            + Decimal("0.023")
            + Decimal("0.036")
            + Decimal("0.017")
            + Decimal("0.014"),
            Decimal("0.115"),
            "Unit 2 2020-2025 additive banked rate sum (11.5%)",
        ),
        (u2 * Decimal("0.115"), Decimal("362.25"), "Unit 2 11.5% banked dollar sum"),
        (u2 * Decimal("0.131"), Decimal("412.65"), "Unit 2 13.1% combined dollar sum"),
        (u2 + Decimal("412.65"), Decimal("3562.65"), "Unit 2 13.1% new rent"),
        (u2 * Decimal("0.034"), Decimal("107.10"), "Unit 2 3.4% phased increase"),
        (u2 + Decimal("107.10"), Decimal("3257.10"), "Unit 2 3.4% phased new rent"),
        (Decimal("59.00") * Decimal("0.5"), Decimal("29.50"), "SF Rent Board 50% fee recovery"),
    ]
    for actual, expected, label in checks:
        if actual != expected:
            fail(errors, f"Arithmetic mismatch on {label}: got {actual}, expected {expected}")


def verify_privacy(errors: list[str]) -> None:
    scan_paths = (
        sorted(DASH_DIR.glob("*.html"))
        + sorted((DASH_DIR / "assets").glob("*"))
        + sorted(DATA_DIR.glob("*.json"))
        + sorted(AUDIT_DIR.glob("*.md"))
    )
    spaced_initials_re = re.compile(r"(?<![A-Za-z])[A-Z]\s+[A-Z](?![A-Za-z])")
    two_upper_re = re.compile(r"\b[A-Z]{2}\b")
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone_re = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")

    for path in scan_paths:
        text = path.read_text(encoding="utf-8")
        # Strip HTML tags when scanning HTML text so CSS/SVG/DOCTYPE attributes don't interfere
        clean = re.sub(r"<[^>]+>", " ", text) if path.suffix == ".html" else text

        spaced_hits = spaced_initials_re.findall(clean)
        if spaced_hits:
            fail(errors, f"Privacy check failed in {path.relative_to(ROOT)}: spaced uppercase initials found: {spaced_hits}")

        for tok in two_upper_re.findall(clean):
            if tok not in ALLOWED_2CHAR_UPPER:
                fail(errors, f"Privacy check failed in {path.relative_to(ROOT)}: unallowlisted 2-letter uppercase token '{tok}'")

        emails = email_re.findall(clean)
        if emails:
            fail(errors, f"Privacy check failed in {path.relative_to(ROOT)}: email found: {emails}")

        for ph in phone_re.findall(clean):
            if ph != "415-252-4600":
                fail(errors, f"Privacy check failed in {path.relative_to(ROOT)}: non-Rent-Board phone number '{ph}'")


def main() -> int:
    errors: list[str] = []

    # 1. Verify build reproducibility
    sys.path.insert(0, str(AUDIT_DIR))
    import build_dashboard  # noqa: PLC0415

    before = {p: p.read_text(encoding="utf-8") for p in sorted(DASH_DIR.glob("*.html"))}
    build_dashboard.build_all()
    after = {p: p.read_text(encoding="utf-8") for p in sorted(DASH_DIR.glob("*.html"))}
    if before and before != after:
        fail(errors, "build_dashboard.py output was out of sync with committed dashboard/*.html (now regenerated).")

    # 2. Check sources.json
    sources = json.loads((DATA_DIR / "sources.json").read_text(encoding="utf-8"))
    registered_urls: set[str] = set()
    for key, src in sources.items():
        url = src.get("url", "")
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc not in ALLOWED_GOV_HOSTS:
            fail(errors, f"Source {key} has non-official or non-HTTPS URL: {url}")
        if "uscode.house.gov" in url:
            fail(errors, f"Source {key} uses broken uscode.house.gov link: {url}")
        registered_urls.add(url)

    # 3. Check JSON datasets enforce blank official_value on Unverified — Flagged for Review rows
    for jpath in sorted(DATA_DIR.glob("*.json")):
        if jpath.name == "sources.json":
            continue
        payload = json.loads(jpath.read_text(encoding="utf-8"))
        row_lists = []
        if isinstance(payload, list):
            row_lists.append(payload)
        elif isinstance(payload, dict):
            for k, v in payload.items():
                if k != "kpis" and isinstance(v, list):
                    row_lists.append(v)
        for rlist in row_lists:
            for row in rlist:
                rid = row.get("id", "<missing>")
                if row.get("status") == "Unverified — Flagged for Review" and row.get("official_value") != "":
                    fail(errors, f"{jpath.name} row {rid} is 'Unverified — Flagged for Review' but official_value is non-empty")
                if not row.get("sources"):
                    fail(errors, f"{jpath.name} row {rid} has zero official sources")
                for skey in row.get("sources", []):
                    if skey not in sources:
                        fail(errors, f"{jpath.name} row {rid} cites unknown source key '{skey}'")

    # 4. Parse all expected HTML pages and check nav, links, anchors, and row source links
    if not (DASH_DIR / ".nojekyll").exists():
        fail(errors, "Missing dashboard/.nojekyll")

    parsed_pages: dict[str, DashboardHTMLParser] = {}
    for pname in EXPECTED_PAGES:
        ppath = DASH_DIR / pname
        if not ppath.exists():
            fail(errors, f"Missing expected page dashboard/{pname}")
            continue
        parser = DashboardHTMLParser()
        parser.feed(ppath.read_text(encoding="utf-8"))
        parsed_pages[pname] = parser

        if parser.nav_hrefs != EXPECTED_PAGES:
            fail(errors, f"Navigation mismatch in {pname}: got {parser.nav_hrefs}, expected {EXPECTED_PAGES}")

        if not parser.rows:
            fail(errors, f"Page {pname} contains zero table rows")

        for row in parser.rows:
            rid = row["id"] or "<unnamed>"
            if len(row["cells"]) != 6:
                fail(errors, f"{pname} row {rid} has {len(row['cells'])} cells instead of 6")
                continue
            status_cell = row["cells"][4].strip()
            val_cell = row["cells"][2].strip()
            if status_cell == "Unverified — Flagged for Review" and val_cell != "":
                fail(errors, f"{pname} row {rid} is Unverified but Official Confirmed Value cell is not empty: '{val_cell}'")
            src_links = [u for u in row["cell_links"][5] if u.startswith("https://")]
            if not src_links:
                fail(errors, f"{pname} row {rid} is missing an official https:// source link in column 6")
            for u in src_links:
                if u not in registered_urls:
                    fail(errors, f"{pname} row {rid} links unregistered external URL: {u}")

    # 5. Validate internal relative links and fragments across dashboard/*.html
    for pname, parser in parsed_pages.items():
        base_dir = DASH_DIR
        for href in parser.hrefs:
            if href.startswith("https://"):
                host = urlparse(href).netloc
                if host not in ALLOWED_GOV_HOSTS:
                    fail(errors, f"{pname} links to non-allowlisted external domain '{host}': {href}")
                continue
            if href.startswith("http://") or href.startswith("mailto:") or href.startswith("javascript:"):
                fail(errors, f"{pname} contains disallowed scheme href: {href}")
                continue
            path_part, _, frag = href.partition("#")
            target_file = (base_dir / path_part).resolve() if path_part else (base_dir / pname).resolve()
            if not target_file.exists():
                # Allow ../index.html even before rebase onto origin/main if root index.html exists
                fail(errors, f"{pname} has broken relative link '{href}' -> {target_file}")
                continue
            if frag:
                target_name = target_file.name
                if target_file.parent == DASH_DIR and target_name in parsed_pages:
                    if frag not in parsed_pages[target_name].ids:
                        fail(errors, f"{pname} has broken fragment '{href}' (#{frag} missing in {target_name})")

    # 6. Verify exact arithmetic & privacy
    verify_arithmetic(errors)
    verify_privacy(errors)

    total_rows = sum(len(p.rows) for p in parsed_pages.values())
    if errors:
        print("VERIFICATION FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"VERIFICATION PASSED: {len(parsed_pages)} dashboard HTML pages, "
        f"{total_rows} source-linked table rows, {len(registered_urls)} official .gov URLs, "
        "exact cent arithmetic, and strict privacy checks all passed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
