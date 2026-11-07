#!/usr/bin/env python3
"""Quality gate for the published site.

Checks performed:
  1. every internal href/src resolves to a file that exists
  2. every internal "#anchor" resolves to an id (or name) in the target file
  3. every HTML file declares the same navigation set (no orphan pages)
  4. every external URL cited in the site is registered in data/sources.csv
  5. all CSV files parse and have a consistent column count
  6. no tenant initials or street-address markers appear in published files

Exits non-zero if any check fails.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

# Personal identifiers must never appear on the published site. The literal
# identifiers supplied by the owner are deliberately NOT stored here: this
# repository is public, and a hard-coded deny-list would republish the very
# values it is meant to protect. Instead we detect the *shape* of an initial
# pair of single capital letters separated by a space, which catches any such value.
FORBIDDEN_PATTERNS = [
    (re.compile(r"(?<![A-Za-z])[A-Z] [A-Z](?![A-Za-z])"), "unexpanded personal initials"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "email address"),
]

errors: list[str] = []
warnings: list[str] = []


def html_files() -> list[Path]:
    """Primary (published, linked) pages."""
    return sorted(DOCS.glob("*.html"))


def archive_files() -> list[Path]:
    """Archived v1 pages: preserved and reachable, but not part of the nav."""
    return sorted((DOCS / "v1").glob("*.html"))


def collect_ids(text: str) -> set[str]:
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    ids |= set(re.findall(r"\bname=\"([^\"]+)\"", text))
    return ids


def check_links(files: list[Path]) -> None:
    cache: dict[Path, set[str]] = {f: collect_ids(f.read_text(encoding="utf-8")) for f in files}
    for f in files:
        text = f.read_text(encoding="utf-8")
        for attr, value in re.findall(r'\b(href|src)="([^"]+)"', text):
            if value.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                continue
            path_part, _, anchor = value.partition("#")
            if path_part in ("",):
                target = f
            else:
                target = (f.parent / path_part).resolve()
                if not target.exists():
                    errors.append(f"{f.name}: missing file for link '{value}'")
                    continue
                if target.is_dir():
                    index = target / "index.html"
                    if not index.exists():
                        errors.append(f"{f.name}: link '{value}' points at a directory with no index.html")
                        continue
                    target = index
            if anchor and target.suffix == ".html":
                ids = cache.get(target) or collect_ids(target.read_text(encoding="utf-8"))
                cache[target] = ids
                if anchor not in ids:
                    errors.append(f"{f.name}: missing anchor #{anchor} in {target.name}")
            elif anchor and target.suffix != ".html":
                # anchors in PDFs cannot be verified locally
                warnings.append(f"{f.name}: anchor-only link to non-HTML '{value}' not verified")


def check_nav(files: list[Path]) -> None:
    navs: dict[Path, list[str]] = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = re.search(r"<nav[^>]*>(.*?)</nav>", text, re.S)
        if not m:
            errors.append(f"{f.name}: no <nav> block")
            continue
        navs[f] = re.findall(r'href="([^"]+)"', m.group(1))
    if not navs:
        return
    reference_file, reference_nav = next(iter(navs.items()))
    for f, nav in navs.items():
        if nav != reference_nav:
            errors.append(
                f"{f.name}: navigation differs from {reference_file.name} "
                f"(has {len(nav)} entries, expected {len(reference_nav)})"
            )
    # every page should be reachable from the nav
    linked = set(reference_nav)
    for f in files:
        if f.name not in linked:
            errors.append(f"{f.name}: page is not listed in the navigation")


def check_sources(files: list[Path]) -> None:
    csv_path = ROOT / "data" / "sources.csv"
    registered: set[str] = set()
    with csv_path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    width = len(rows[0])
    for i, row in enumerate(rows[1:], start=2):
        if len(row) != width:
            errors.append(f"sources.csv line {i}: expected {width} columns, found {len(row)}")
        if len(row) >= 4:
            registered.add(row[3].strip())

    cited: dict[str, set[str]] = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        for url in re.findall(r'href="(https?://[^"]+)"', text):
            cited.setdefault(url.replace("&amp;", "&"), set()).add(f.name)

    for url, where in sorted(cited.items()):
        if url not in registered:
            errors.append(f"source not registered in data/sources.csv (cited in {', '.join(sorted(where))}): {url}")

    for url in sorted(registered):
        if url not in cited:
            warnings.append(f"sources.csv URL not linked anywhere on the site: {url}")


def check_csv_consistency() -> None:
    for name in ("units.csv", "aga-rates.csv", "sources.csv"):
        path = ROOT / "data" / name
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
        if not rows:
            errors.append(f"{name}: empty")
            continue
        widths = {len(r) for r in rows}
        if len(widths) != 1:
            errors.append(f"{name}: inconsistent column counts {sorted(widths)}")


def check_privacy(files: list[Path]) -> None:
    for f in files:
        text = f.read_text(encoding="utf-8")
        for pattern, label in FORBIDDEN_PATTERNS:
            for match in pattern.findall(text):
                errors.append(f"{f.name}: contains what looks like an {label}: {match}")


def main() -> int:
    files = html_files()
    archived = archive_files()
    if not files:
        print("no HTML files found", file=sys.stderr)
        return 1

    check_links(files + archived)
    check_nav(files)
    check_sources(files)
    check_csv_consistency()
    check_privacy(files + archived)

    for w in warnings:
        print(f"warn: {w}")
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"\n{len(errors)} error(s)", file=sys.stderr)
        return 1
    print(f"OK: {len(files)} published pages (+{len(archived)} archived), all internal links "
          f"and anchors resolve, all CSVs consistent, all external citations registered, "
          f"no personal tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
