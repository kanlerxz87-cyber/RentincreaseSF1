#!/usr/bin/env python3
"""Superseded-edition notice and direct official links for archived pages.

GitHub Pages publishes this repository from its root, so every earlier edition of
the site is still served next to the current dashboard (``index.html`` + ``hub/``).
This utility makes those archived pages safe to land on:

1. NOTICE    every archived page opens with a "Superseded edition" notice that links
             to the current dashboard, and carries ``<meta name="robots" content="noindex">``.
2. LINKS     every table body row carries a DIRECT link to an official publisher.
             * A row that only pointed at a local registry anchor (``sources.html#S4``)
               gets the official URL that the registry entry itself cites.
             * A row with no source at all (owner-supplied input, arithmetic, analysis,
               or a value left blank as unverified) gets a link to the official rule that
               governs it, labelled as context and as NOT independently verified.
             * A row that records repository history is labelled as a repository record.
3. WITHDRAWN the earliest draft (``site/``, ``research/``, ``docs/v1/executive_summary.md``)
             took most of its statements from commercial websites.  Those files are replaced by a short
             withdrawal notice.  Nothing is removed from Git history.

The transformation is deterministic and idempotent.  Each edition's generator calls
``apply_edition()`` as its last step, so a rebuild reproduces the committed pages.

    python3 tools/legacy_notice.py --apply     rewrite every archived page in place
    python3 tools/legacy_notice.py --check     exit 1 if any archived page is not compliant
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent

# Archived editions.  "docs" means docs/*.html only; docs/v1 and docs/v2 are separate editions.
EDITIONS = ("docs", "docs/v1", "docs/v2", "dashboard", "portal", "review",
            "integration", "guide", "compliance")

# Withdrawn early draft: page -> the current page that covers the same topic.
WITHDRAWN_HTML = {
    "site/index.html": "index.html",
    "site/executive_summary.html": "index.html",
    "site/sf_laws.html": "hub/limits.html",
    "site/notification.html": "hub/notice.html",
    "site/practices.html": "hub/practice.html",
    "site/discrimination.html": "hub/fair-housing.html",
    "site/flagged.html": "hub/flags.html",
}
WITHDRAWN_MD = (
    "research/discrimination.md", "research/notification.md", "research/practices.md",
    "research/sf_laws.md", "docs/v1/executive_summary.md",
)
WITHDRAWN_DATE = "2026-11-11"

CURRENT_HOME = "index.html"
CURRENT_FLAGS = "hub/flags.html"
CURRENT_SOURCES = "hub/sources.html"

# Official publishers that do not use a .gov host name.
OFFICIAL_EXACT = {
    "sf.gov", "www.sf.gov", "api.sf.gov", "media.api.sf.gov",
    "sfgov.legistar.com",
    "portal.sfrb.org", "sfrb.org", "www.sfrb.org",
    "sftreasurer.org", "www.sftreasurer.org",
    "sfassessor.org", "www.sfassessor.org",
    "sfplanninggis.org",
    "sfdbi.org", "www.sfdbi.org",
    "sfbos.org", "www.sfbos.org",
    "sfgov.org", "www.sfgov.org",
    "leginfo.legislature.ca.gov",
    "www4.courts.ca.gov", "www.courts.ca.gov", "courts.ca.gov", "selfhelp.courts.ca.gov",
    "codelibrary.amlegal.com",
}
# Hosts that are the system of record for the repository itself, not a source of law.
RECORD_HOSTS = {"github.com", "docs.github.com", "kanlerxz87-cyber.github.io"}
# Pages whose tables are an inventory of repository editions, not legal claims.
RECORD_PAGES = {"docs/v2/reconciliation.html", "dashboard/pages/repo.html"}

NOTICE_OPEN, NOTICE_CLOSE = "<!--legacy-notice-->", "<!--/legacy-notice-->"
META = '<meta name="robots" content="noindex" data-legacy-notice>'
# Inserted text always starts and ends with a newline, and strip() removes exactly that,
# so apply -> strip returns the generator's original bytes whatever its line layout.
NOTICE_RE = re.compile(r"\n" + re.escape(NOTICE_OPEN) + r".*?" + re.escape(NOTICE_CLOSE) + r"\n", re.S)
META_INSERT = "\n" + META + "\n"
SPAN_RE = re.compile(r'<span class="legacy-direct"[^>]*>.*?</span>', re.S)
ROW_RE = re.compile(r"<tr\b[^>]*>(?:(?!</tr>).)*</tr>", re.S)
_HREF_RE = re.compile(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)')""")
SPAN_STYLE = "display:block;margin-top:.4em;font-size:.85em;line-height:1.35"
LINK_STYLE = "color:#0b4f8a;font-weight:600"

# Official rule that governs a row which cites nothing.  First matching rule wins.
# (key, substring used to find the same source in the edition's own registry, URL, label)
CONTEXT = {
    "ALGO": ("3710c", "https://www.sf.gov/information--sec-3710c-use-and-sale-algorithmic-devices-prohibited",
             "S.F. Admin. Code §37.10C (rent-setting software)"),
    "RETAL": ("sectionNum=1942.5", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1942.5",
              "Cal. Civil Code §1942.5 (retaliation)"),
    "FEHA": ("sectionNum=12955", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=12955",
             "Cal. Gov. Code §12955 (housing discrimination)"),
    "HARASS": ("3710b", "https://www.sf.gov/information--sec-3710b-tenant-harassment",
               "S.F. Admin. Code §37.10B (tenant harassment)"),
    "LICENCE": ("rent-board-housing-inventory", "https://www.sf.gov/rent-board-housing-inventory",
                "SF Rent Board, Housing Inventory and rent increase licence"),
    "OCCUPANT": ("sectionNum=1954.53", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1954.53",
                 "Cal. Civil Code §1954.53 (change of occupants)"),
    "BANK": ("banked-rent-increases", "https://www.sf.gov/information--banked-rent-increases",
             "SF Rent Board, banked rent increases"),
    "NOTICE": ("sectionNum=827", "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827",
               "Cal. Civil Code §827 (notice of rent increase)"),
    "COVERAGE": ("learn-about-san-francisco-rental-laws", "https://www.sf.gov/learn-about-san-francisco-rental-laws",
                 "SF Rent Board, which units are covered"),
    "LIMITS": ("sec-373-rent-limitations", "https://www.sf.gov/information--sec-373-rent-limitations",
               "S.F. Admin. Code §37.3 (rent limitations)"),
    "RENT": ("learn-about-rent-increases-san-francisco", "https://www.sf.gov/learn-about-rent-increases-san-francisco",
             "SF Rent Board, rent increases"),
}
CONTEXT_RULES = (
    ("LIMITS", ("subsidy", "section 8")),
    ("RENT", ("tenant lawyer", "anything still unverified", "reasonable and normal", "no official source",
              "how do big corporations", "how large owners", "how individual owners", "market benchmark",
              "market rent")),
    ("ALGO", ("rent software", "algorithm")),
    ("FEHA", ("protected characteristic", "who we are", "voucher", "disabled", "a child", "discriminat",
              "subsidy", "household income", "differ by", "one unit is increased", "one unit or both",
              "raise both", "raise unit", "larger than the annual component", "and unit 1's is")),
    ("RETAL", ("retaliat", "complained about repairs", "complaint history", "asked for repairs")),
    ("HARASS", ("without an eviction", "get us out", "buyout", "harass")),
    ("LIMITS", ("notice is void", "rounding", "compounding")),
    ("LICENCE", ("licence status", "license status", "rent-increase licence", "rent increase license",
                 "housing inventory")),
    ("OCCUPANT", ("occupancy change", "original tenants", "occupant change", "roommate", "initial tenants")),
    ("COVERAGE", ("year built", "built 1940", "rent-controlled", "c of o", "street address", "location",
                  "bedroom count", "square footage")),
)
# Applied only when no rule above matched.
CONTEXT_PAGE_HINTS = (("process", "NOTICE"), ("notice", "NOTICE"))
CONTEXT_LATE_RULES = (
    ("NOTICE", ("notice required", "service date", "arrived late", "how should tenants be told")),
    ("BANK", ("banked", "banking", "accumulated", "phased", "13.1%", "11.5%", "lawful maximum")),
)


# ----------------------------------------------------------------------------- helpers
def hrefs(fragment: str) -> list[str]:
    """Every href in a fragment, whichever quote style the edition's generator used."""
    return [a or b for a, b in _HREF_RE.findall(fragment) if (a or b)]


def is_official(url: str) -> bool:
    p = urlparse(html.unescape(url))
    if p.scheme not in ("http", "https"):
        return False
    host = (p.hostname or "").lower()
    return host.endswith(".gov") or host in OFFICIAL_EXACT


def host_of(url: str) -> str:
    return (urlparse(html.unescape(url)).hostname or "").lower()


def edition_pages(edition: str) -> list[Path]:
    base = ROOT / edition
    if edition == "docs":
        return sorted(base.glob("*.html"))
    return sorted(base.rglob("*.html"))


def all_archived_pages() -> list[Path]:
    return [p for e in EDITIONS for p in edition_pages(e)]


def prefix_for(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth


def text_of(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


# ----------------------------------------------------------------------------- 1. notice
def notice_block(prefix: str) -> str:
    return (
        f"{NOTICE_OPEN}\n"
        '<aside data-legacy-notice="superseded" role="note" aria-label="Superseded edition" '
        'style="margin:0;padding:14px 18px;background:#fff4ce;color:#3b2f00;'
        "border-bottom:3px solid #b58900;font:15px/1.5 system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif\">"
        "<strong>Superseded edition: kept for the record, not maintained.</strong> "
        "This page has not been re-checked as a whole, and figures or wording on it may have been corrected since it was written. "
        f'For the current, source-linked answer use the <a href="{prefix}{CURRENT_HOME}" style="{LINK_STYLE}">current dashboard</a>; '
        f'open items are on its <a href="{prefix}{CURRENT_FLAGS}" style="{LINK_STYLE}">Flagged for Review</a> page.'
        "</aside>\n"
        f"{NOTICE_CLOSE}\n"
    )


def strip(text: str) -> str:
    """Remove everything this utility ever added, so that apply() is idempotent."""
    text = NOTICE_RE.sub("", text)
    text = text.replace(META_INSERT, "")
    return SPAN_RE.sub("", text)


def add_notice(text: str, prefix: str) -> str:
    if "<head>" not in text or "<body>" not in text:
        raise ValueError("page has no plain <head>/<body> tag")
    text = text.replace("<head>", "<head>" + META_INSERT, 1)
    return text.replace("<body>", "<body>\n" + notice_block(prefix), 1)


# ----------------------------------------------------------------------------- 2. direct links
_file_cache: dict[Path, str] = {}


def _read(path: Path) -> str:
    if path not in _file_cache:
        _file_cache[path] = strip(path.read_text(encoding="utf-8"))
    return _file_cache[path]


def _anchored_fragment(text: str, anchor: str) -> str:
    m = re.search(r"""\bid=["']""" + re.escape(anchor) + r"""["']""", text)
    if not m:
        return ""
    start = text.rfind("<", 0, m.start())
    tag = re.match(r"<(\w+)", text[start:])
    name = tag.group(1).lower() if tag else ""
    if re.fullmatch(r"h[1-6]", name):
        nxt = re.search(r"<h[1-%s]\b" % name[1], text[m.end():])
        end = m.end() + nxt.start() if nxt else len(text)
    else:
        close = text.find(f"</{name}>", m.end()) if name else -1
        end = close if close != -1 else m.end() + 4000
    return text[start:min(end, start + 12000)]


def official_links_for_anchor(page: Path, href: str, depth: int = 0) -> list[str]:
    """Official URLs cited by the element a local '#anchor' link points at."""
    path_part, _, anchor = href.partition("#")
    if not anchor:
        return []
    target = (page.parent / path_part).resolve() if path_part else page
    if not target.is_file() or target.suffix != ".html":
        return []
    fragment = _anchored_fragment(_read(target), anchor)
    found = [u for u in hrefs(fragment) if is_official(u)]
    if not found and depth < 1:
        for u in hrefs(fragment):
            if "#" in u and not u.startswith(("http://", "https://")):
                found += official_links_for_anchor(target, u, depth + 1)
    out: list[str] = []
    for u in found:
        if u not in out:
            out.append(u)
    return out


def registry_url(page: Path, needle: str) -> str | None:
    """The edition's own registered URL for a source, if its registry lists one."""
    for folder in (page.parent, page.parent.parent):
        reg = folder / "sources.html"
        if reg.is_file() and ROOT in reg.resolve().parents:
            for u in hrefs(_read(reg)):
                if is_official(u) and needle in html.unescape(u):
                    return u
    return None


def context_for(row_text: str, page_name: str = "") -> str:
    low = row_text.lower()
    for key, needles in CONTEXT_RULES:
        if any(n in low for n in needles):
            return key
    for needle, key in CONTEXT_PAGE_HINTS:
        if needle in page_name:
            return key
    for key, needles in CONTEXT_LATE_RULES:
        if any(n in low for n in needles):
            return key
    return "RENT"


def _span(kind: str, inner: str) -> str:
    return f'<span class="legacy-direct" data-legacy-{kind} style="{SPAN_STYLE}">{inner}</span>'


def _link(url: str, label: str) -> str:
    return f'<a href="{url}" style="{LINK_STYLE}">{html.escape(label)}</a>'


def add_direct_links(text: str, page: Path) -> str:
    rel = page.relative_to(ROOT).as_posix()

    def fix(match: re.Match) -> str:
        row = match.group(0)
        if "<td" not in row:
            return row
        links = hrefs(row)
        if any(is_official(u) for u in links):
            return row
        external = [u for u in links if u.startswith(("http://", "https://"))]
        if rel in RECORD_PAGES or (external and all(host_of(u) in RECORD_HOSTS for u in external)):
            addition = _span("record", "Repository record, not a statement of law: no government source applies to this row.")
        else:
            resolved: list[str] = []
            for u in links:
                if not u.startswith(("http://", "https://", "mailto:", "tel:")):
                    for found in official_links_for_anchor(page, u):
                        if found not in resolved:
                            resolved.append(found)
            if resolved:
                addition = _span("resolved", "Official source: " + ", ".join(_link(u, host_of(u)) for u in resolved[:3]))
            else:
                key = context_for(text_of(row), page.name)
                needle, fallback, label = CONTEXT[key]
                url = registry_url(page, needle) or html.escape(fallback, quote=True)
                addition = _span(
                    "context",
                    "Governing official rule: " + _link(url, label)
                    + ". This row is owner-supplied, calculated or analysis; it is not independently verified.",
                )
        cut = row.rfind("</td>")
        return row[:cut] + addition + row[cut:]

    return ROW_RE.sub(fix, text)


# ----------------------------------------------------------------------------- 3. withdrawn
def withdrawn_html(target: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
{META}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Withdrawn page | SF rent increase review</title>
</head>
<body style="margin:0;background:#f6f7f9;color:#1b1f24;font:17px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif">
{NOTICE_OPEN}
<main data-legacy-notice="withdrawn" style="max-width:44rem;margin:0 auto;padding:3rem 1.25rem">
<p style="margin:0 0 .5rem;font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;color:#8a5a00">Withdrawn {WITHDRAWN_DATE}</p>
<h1 style="margin:0 0 1rem;font-size:1.9rem;line-height:1.2">This page has been withdrawn</h1>
<p>It was an early draft that took most of its statements from commercial websites (property-management, software and law-firm pages) rather than from official sources. It also applied the 1.6% annual allowance to an increase dated June 1, 2027, although the Rent Board has published that rate only for increases that take effect through February 28, 2027. It has been taken out of publication so that nobody relies on it.</p>
<p style="margin:1.5rem 0"><a href="../{target}" style="display:inline-block;padding:.7rem 1.1rem;background:#0b4f8a;color:#fff;border-radius:6px;text-decoration:none;font-weight:600">Open the current page on this topic</a></p>
<p><a href="../{CURRENT_HOME}" style="{LINK_STYLE}">Dashboard home</a> &middot; <a href="../{CURRENT_FLAGS}" style="{LINK_STYLE}">Flagged for Review</a> &middot; <a href="../{CURRENT_SOURCES}" style="{LINK_STYLE}">Official sources</a></p>
<p style="font-size:.9rem;color:#4a5560">The current dashboard cites government publishers only. Anything that could not be confirmed from one is left blank and flagged.</p>
</main>
{NOTICE_CLOSE}
</body>
</html>
"""


def withdrawn_md(rel: str) -> str:
    up = "../" * (len(Path(rel).parts) - 1)
    return f"""# Withdrawn

<!--legacy-notice-->
This early research note was withdrawn from publication on {WITHDRAWN_DATE}.

It took most of its statements from commercial websites (property-management, software and law-firm
pages) rather than from official sources. The pages built from these notes also applied the 1.6% annual allowance to an increase dated
June 1, 2027, although the Rent Board has published that rate only for increases that take effect
through February 28, 2027. The note has been taken out of publication so that nobody relies on it.

Use the current, source-linked material instead:

- [Executive summary]({up}EXECUTIVE_SUMMARY.md)
- [Official sources]({up}SOURCES.md)
- [Dashboard]({up}index.html) and its [Flagged for Review]({up}hub/flags.html) page
<!--/legacy-notice-->
"""


# ----------------------------------------------------------------------------- apply / check
def transform(path: Path) -> str:
    text = strip(path.read_text(encoding="utf-8"))
    text = add_notice(text, prefix_for(path))
    return add_direct_links(text, path)


def apply_edition(edition: str) -> list[str]:
    """Rewrite one archived edition in place.  Called by that edition's generator."""
    _file_cache.clear()
    changed = []
    pages = edition_pages(edition)
    # Registries are read through the cache in their stripped form, so order does not matter.
    results = {p: transform(p) for p in pages}
    for p, new in results.items():
        if p.read_text(encoding="utf-8") != new:
            p.write_text(new, encoding="utf-8")
            changed.append(p.relative_to(ROOT).as_posix())
    return changed


def apply_withdrawn() -> list[str]:
    changed = []
    for rel, target in WITHDRAWN_HTML.items():
        p, new = ROOT / rel, withdrawn_html(target)
        if not p.is_file() or p.read_text(encoding="utf-8") != new:
            p.write_text(new, encoding="utf-8")
            changed.append(rel)
    for rel in WITHDRAWN_MD:
        p, new = ROOT / rel, withdrawn_md(rel)
        if not p.is_file() or p.read_text(encoding="utf-8") != new:
            p.write_text(new, encoding="utf-8")
            changed.append(rel)
    return changed


def check() -> list[str]:
    """Problems that would let a reader mistake an archived page for the current one."""
    errors: list[str] = []
    _file_cache.clear()
    for target in (CURRENT_HOME, CURRENT_FLAGS, CURRENT_SOURCES):
        if not (ROOT / target).is_file():
            errors.append(f"notice target missing: {target}")
    for edition in EDITIONS:
        pages = edition_pages(edition)
        if not pages:
            errors.append(f"{edition}: no archived pages found")
        for p in pages:
            rel = p.relative_to(ROOT).as_posix()
            text = p.read_text(encoding="utf-8")
            if 'data-legacy-notice="superseded"' not in text:
                errors.append(f"{rel}: no superseded-edition notice")
            if META not in text:
                errors.append(f"{rel}: no noindex tag")
            if text != transform(p):
                errors.append(f"{rel}: differs from what tools/legacy_notice.py --apply writes")
            for row in ROW_RE.findall(text):
                if "<td" not in row:
                    continue
                if "data-legacy-record" in row:
                    continue
                if not any(is_official(u) for u in hrefs(row)):
                    errors.append(f"{rel}: table row without a direct official link: {text_of(row)[:70]}")
            for u in hrefs(text):
                if u.startswith(("http://", "https://")) and not is_official(u) and host_of(u) not in RECORD_HOSTS:
                    errors.append(f"{rel}: link to a non-official host: {host_of(u)}")
    for rel, target in WITHDRAWN_HTML.items():
        p = ROOT / rel
        if not p.is_file() or p.read_text(encoding="utf-8") != withdrawn_html(target):
            errors.append(f"{rel}: is not the withdrawal notice")
        if not (ROOT / target).is_file():
            errors.append(f"{rel}: withdrawal notice points at a missing page: {target}")
    for rel in WITHDRAWN_MD:
        p = ROOT / rel
        if not p.is_file() or p.read_text(encoding="utf-8") != withdrawn_md(rel):
            errors.append(f"{rel}: is not the withdrawal notice")
    return errors


def main(argv: list[str]) -> int:
    if "--apply" in argv:
        changed = apply_withdrawn()
        for edition in EDITIONS:
            changed += apply_edition(edition)
        print(f"legacy_notice: {len(all_archived_pages())} archived pages, "
              f"{len(WITHDRAWN_HTML) + len(WITHDRAWN_MD)} withdrawn files; {len(changed)} file(s) rewritten")
        return 0
    if "--check" in argv:
        errors = check()
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        if errors:
            print(f"\n{len(errors)} error(s)", file=sys.stderr)
            return 1
        print(f"OK: {len(all_archived_pages())} archived pages carry the superseded-edition notice and a noindex tag; "
              f"every table row has a direct official link or is marked as a repository record; "
              f"{len(WITHDRAWN_HTML) + len(WITHDRAWN_MD)} withdrawn files are withdrawal notices")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
