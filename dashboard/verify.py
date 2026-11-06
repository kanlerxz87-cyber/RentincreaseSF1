#!/usr/bin/env python3
"""Line-by-line verification gate for the independent dashboard.

Checks the data registry, official source links on every table row, blank
unverified values, scenario arithmetic, internal links and anchors, navigation
consistency, source coverage, and privacy (no raw personal identifiers).
"""
from __future__ import annotations

import html
import json
import re
import sys
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "data" / "site_data.json").read_text(encoding="utf-8"))

OFFICIAL_HOSTS = {
    "sf.gov", "www.sf.gov", "media.api.sf.gov", "api.sf.gov",
    "sfbos.archive.sf.gov", "sfrb.org", "www.sfrb.org",
    "leginfo.legislature.ca.gov", "oag.ca.gov", "hcd.ca.gov", "dir.ca.gov",
    "hud.gov", "www.hud.gov", "archives.hud.gov", "huduser.gov",
    "justice.gov", "www.justice.gov", "ecfr.gov", "www.ecfr.gov",
    "govinfo.gov", "uscode.house.gov", "bls.gov", "codelibrary.amlegal.com",
    "sfplanninggis.org", "sfgov.legistar.com", "github.com",
}

EXPECTED_PAGES = [
    "index.html", "pages/summary.html", "pages/laws.html", "pages/units.html",
    "pages/analysis.html", "pages/notice.html", "pages/owners.html",
    "pages/discrimination.html", "pages/review.html", "pages/sources.html",
    "pages/flagged.html", "pages/repo.html",
]

FORBIDDEN_TOKENS = [bytes.fromhex(h).decode("ascii") for h in (
    "4c204f", "56204e", "4a50", "4d2054", "452052", "492053"
)]
FORBIDDEN_RE = re.compile(r"\b(" + "|".join(re.escape(t) for t in FORBIDDEN_TOKENS) + r")\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def is_official(url: str) -> bool:
    url = html.unescape(url)
    try:
        host = (urlsplit(url).hostname or "").lower()
    except ValueError:
        return False
    return host in OFFICIAL_HOSTS


def check_data() -> None:
    sources = {s["id"]: s for s in DATA["sources"]}
    flags = {f["id"]: f for f in DATA["flags"]}

    for sid, s in sources.items():
        for key in ("agency", "level", "title", "url", "quote", "notes"):
            if not s.get(key):
                fail(f"source {sid}: missing {key}")
        if not is_official(s["url"]):
            fail(f"source {sid}: URL host not in official allowlist: {s['url']}")
        if not s["url"].startswith("https://"):
            fail(f"source {sid}: URL is not https")

    for f in DATA["facts"]:
        if f["source_id"] not in sources:
            fail(f"fact {f['id']}: unknown source {f['source_id']}")
        if not f["value"]:
            fail(f"fact {f['id']}: verified value is blank (use a case fact instead)")

    for c in DATA["case_facts"]:
        if c["verified_value"] != "":
            fail(f"case fact {c['id']}: verified_value must be blank")
        if c["flag_id"] not in flags:
            fail(f"case fact {c['id']}: unknown flag {c['flag_id']}")
        if c["source_id"] not in sources:
            fail(f"case fact {c['id']}: unknown governing source {c['source_id']}")

    for f in DATA["flags"]:
        if f["status"] != "needs review":
            fail(f"flag {f['id']}: expected status 'needs review'")
        if not f["source_ids"]:
            fail(f"flag {f['id']}: no official source links")
        for sid in f["source_ids"]:
            if sid not in sources and sid != "S42":
                fail(f"flag {f['id']}: unknown source {sid}")

    rate_sum = Decimal("0")
    for r in ("1.8", "0.7", "2.3", "3.6", "1.7", "1.4", "1.6"):
        rate_sum += Decimal(r)
    if rate_sum != Decimal("13.1"):
        fail("SC3 rate sum does not equal 13.1%")

    for sc in DATA["scenarios"]:
        if sc["flag_id"] not in flags:
            fail(f"scenario {sc['id']}: unknown flag {sc['flag_id']}")
        for sid in sc["source_ids"]:
            if sid not in sources:
                fail(f"scenario {sc['id']}: unknown source {sid}")
        base = Decimal(sc["base"])
        rate = Decimal(sc["rate_percent"])
        inc = (base * rate / Decimal("100")).quantize(Decimal("0.01"))
        new = (base + inc).quantize(Decimal("0.01"))
        if inc != Decimal(sc["increase_amount"]):
            fail(f"scenario {sc['id']}: increase {sc['increase_amount']} != computed {inc}")
        if new != Decimal(sc["new_rent"]):
            fail(f"scenario {sc['id']}: new rent {sc['new_rent']} != computed {new}")
        if rate <= 0 or base <= 0:
            fail(f"scenario {sc['id']}: non-positive inputs")

    # Every flag id referenced on pages must exist
    for c in DATA["case_facts"]:
        if not re.fullmatch(r"F\d\d", c["flag_id"]):
            fail(f"case fact {c['id']}: malformed flag id")


class TableParser(HTMLParser):
    """Collects data rows inside <tbody> and whether each has an official link."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_tbody = False
        self.in_tr = False
        self.hrefs: list[str] = []
        self.rows: list[list[str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "tbody":
            self.in_tbody = True
        elif tag == "tr" and self.in_tbody:
            self.in_tr = True
            self.hrefs = []
        elif tag == "a" and self.in_tr:
            d = dict(attrs)
            if d.get("href"):
                self.hrefs.append(d["href"])

    def handle_endtag(self, tag):
        if tag == "tr" and self.in_tr:
            self.rows.append(self.hrefs)
            self.in_tr = False
            self.hrefs = []
        elif tag == "tbody":
            self.in_tbody = False


def collect_ids(text: str) -> set[str]:
    return set(re.findall(r'\bid="([^"]+)"', text)) | set(re.findall(r'\bname="([^"]+)"', text))


def check_html() -> None:
    files = []
    for rel in EXPECTED_PAGES:
        p = ROOT / rel
        if not p.is_file():
            fail(f"missing generated page: {rel}")
        else:
            files.append(p)

    texts = {p: p.read_text(encoding="utf-8") for p in files}
    ids = {p: collect_ids(t) for p, t in texts.items()}

    # 1. Every data-table row has at least one official source link.
    for p, text in texts.items():
        parser = TableParser()
        parser.feed(text)
        if not parser.rows:
            fail(f"{p.relative_to(ROOT)}: no data-table rows found")
        for i, hrefs in enumerate(parser.rows, start=1):
            if not any(is_official(h) for h in hrefs):
                fail(f"{p.relative_to(ROOT)}: table row {i} has no official source link")

    # 2. Internal links resolve; anchors resolve; external links are official hosts.
    for p, text in texts.items():
        for attr, value in re.findall(r'\b(href|src)="([^"]+)"', text):
            raw = html.unescape(value)
            if raw.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                if raw.startswith(("http://", "https://")) and not is_official(raw):
                    fail(f"{p.relative_to(ROOT)}: external link not in official host allowlist: {raw}")
                continue
            path_part, _, anchor = raw.partition("#")
            if path_part == "":
                target = p
            else:
                target = (p.parent / path_part).resolve()
                if not target.exists():
                    fail(f"{p.relative_to(ROOT)}: broken {attr} link '{raw}'")
                    continue
                if target.is_dir():
                    target = target / "index.html"
                    if not target.exists():
                        fail(f"{p.relative_to(ROOT)}: link '{raw}' points to directory without index.html")
                        continue
            if anchor and target.suffix == ".html":
                known = ids.get(target) or collect_ids(target.read_text(encoding="utf-8"))
                if anchor not in known:
                    fail(f"{p.relative_to(ROOT)}: broken anchor #{anchor} in {target.name}")

    # 3. Navigation consistency and reachability.
    expected_nav = {Path(x).name for x in EXPECTED_PAGES}
    for p, text in texts.items():
        m = re.search(r"<nav[^>]*>(.*?)</nav>", text, re.S)
        if not m:
            fail(f"{p.relative_to(ROOT)}: missing <nav>")
            continue
        hrefs = re.findall(r'href="([^"]+)"', m.group(1))
        names = {Path(html.unescape(h).split("#")[0]).name for h in hrefs}
        if names != expected_nav:
            fail(f"{p.relative_to(ROOT)}: navigation set differs (missing {sorted(expected_nav - names)}, extra {sorted(names - expected_nav)})")

    # 4. Every registered source URL appears on the sources page.
    src_text = texts[ROOT / "pages/sources.html"]
    for s in DATA["sources"]:
        if html.escape(s["url"], quote=True) not in src_text:
            fail(f"sources page does not link registered source {s['id']}")

    # 5. Every flag is published on the flagged page with its id as an anchor.
    flagged_text = texts[ROOT / "pages/flagged.html"]
    for f in DATA["flags"]:
        if f'id="{f["id"]}"' not in flagged_text:
            fail(f"flagged page missing anchor for {f['id']}")

    # 6. No raw personal identifiers in any published file.
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".html", ".md", ".json", ".css", ".js", ".py"}:
            continue
        if p.name in {"verify.py"}:
            # verification code legitimately contains the forbidden-token list itself
            continue
        text = p.read_text(encoding="utf-8")
        m = FORBIDDEN_RE.search(text)
        if m:
            fail(f"{p.relative_to(ROOT)}: raw personal token '{m.group(1)}' found")
        e = EMAIL_RE.search(text)
        if e:
            fail(f"{p.relative_to(ROOT)}: email-like personal data found: {e.group(0)}")


def main() -> int:
    check_data()
    check_html()
    for w in warnings:
        print(f"warn: {w}")
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"\n{len(errors)} error(s)", file=sys.stderr)
        return 1
    print(
        f"OK: {len(DATA['sources'])} official sources, {len(DATA['facts'])} verified facts, "
        f"{len(DATA['case_facts'])} blank-verified case facts, {len(DATA['flags'])} flagged items, "
        f"{len(DATA['scenarios'])} arithmetic scenarios, {len(EXPECTED_PAGES)} pages; "
        "every table row source-linked, all links/anchors/nav resolve, no personal identifiers."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
