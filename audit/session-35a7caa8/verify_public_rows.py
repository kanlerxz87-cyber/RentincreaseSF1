#!/usr/bin/env python3
"""Check direct first-party source links in the published site's HTML tables.

This is a structural, offline check, not legal verification: a link can be
broken, stale, or irrelevant, and a government page cannot authenticate a
private lease or rent ledger. Read and verify the sources separately.

By default every HTML file under the Pages root is checked, including directly
reachable archived editions. Use --canonical to limit the census to index.html,
hub/, and assurance/. Header-only rows are ignored; every row with a <td> must
contain its own direct HTTPS link to an official publisher. Local source-registry
and flag links do not count. For repository-process facts, first-party links to
this repository and GitHub's own documentation also count; they do not prove
legal claims.
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
# These official City publishers do not use .gov hostnames. Exact hosts only:
# never accept an attacker-controlled suffix or arbitrary subdomain.
OFFICIAL_CITY_HOSTS = frozenset({
    "sftreasurer.org", "www.sftreasurer.org", "sfgov.legistar.com",
    "portal.sfrb.org", "sfassessor.org", "www.sfassessor.org",
    "sfplanninggis.org",
})
REPO_PATH = "/kanlerxz87-cyber/rentincreasesf1"
SKIP_DIRS = {".git", "__pycache__", ".cache", "node_modules", ".venv"}


def is_first_party_url(href: str) -> bool:
    """Return whether a link is directly to a known official HTTPS publisher."""
    try:
        parsed = urlsplit(href)
        host = (parsed.hostname or "").lower()
        port = parsed.port  # Force malformed ports to raise ValueError.
    except ValueError:
        return False
    if (parsed.scheme.lower() != "https" or not host or
            parsed.username is not None or parsed.password is not None or
            port not in (None, 443)):
        return False
    if host.endswith(".gov") or host in OFFICIAL_CITY_HOSTS:
        return True
    if host == "docs.github.com":
        return True
    if host == "github.com":
        path = parsed.path.rstrip("/").lower()
        return path == REPO_PATH or path.startswith(REPO_PATH + "/")
    return False


@dataclass
class Row:
    line: int
    has_data_cell: bool = False
    has_first_party_link: bool = False


@dataclass
class Table:
    header_depth: int = 0
    row: Row | None = None


class CitationParser(HTMLParser):
    """Count claim rows; a source in an adjacent, nested or header row is not enough."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[Table] = []
        self.rows = 0
        self.missing_lines: list[tuple[int, int]] = []  # (line, page-wide data-row number)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self.tables.append(Table())
            return
        if not self.tables:
            return
        table = self.tables[-1]
        if tag == "thead":
            table.header_depth += 1
        elif tag == "tr":
            table.row = Row(line=self.getpos()[0])
        elif tag == "td" and table.row is not None:
            table.row.has_data_cell = True
        elif tag == "a" and table.row is not None:
            href = dict(attrs).get("href") or ""
            table.row.has_first_party_link |= is_first_party_url(href)

    def handle_endtag(self, tag: str) -> None:
        if not self.tables:
            return
        table = self.tables[-1]
        if tag == "tr" and table.row is not None:
            if not table.header_depth and table.row.has_data_cell:
                self.rows += 1
                if not table.row.has_first_party_link:
                    self.missing_lines.append((table.row.line, self.rows))
            table.row = None
        elif tag == "thead":
            table.header_depth = max(0, table.header_depth - 1)
        elif tag == "table":
            self.tables.pop()


def audit_html(text: str) -> CitationParser:
    parser = CitationParser()
    parser.feed(text)
    parser.close()
    return parser


def html_files(canonical_only: bool) -> list[Path]:
    paths: list[Path] = []
    for directory, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            if not name.endswith(".html"):
                continue
            path = Path(directory) / name
            rel = path.relative_to(ROOT)
            if canonical_only and not (str(rel) == "index.html" or rel.parts[0] in {"hub", "assurance"}):
                continue
            paths.append(path)
    return sorted(paths)


def main(argv: list[str] | None = None) -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--canonical", action="store_true", help="check only index.html, hub/ and assurance/")
    cli.add_argument("--max-examples", type=int, default=20, help="maximum failing file:line examples")
    cli.add_argument("--report-only", action="store_true", help="print census without returning a failing status")
    args = cli.parse_args(argv)
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    examples: list[str] = []
    for path in html_files(args.canonical):
        rel = path.relative_to(ROOT)
        group = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        parsed = audit_html(path.read_text(encoding="utf-8"))
        counts[group][0] += 1
        counts[group][1] += parsed.rows
        counts[group][2] += len(parsed.missing_lines)
        # Never print the row contents: old versions can contain sensitive data.
        examples.extend(f"{rel}:{line} (data row {row})" for line, row in parsed.missing_lines)
    print("Edition           HTML files   Data rows   Missing direct source")
    for group, (pages, rows, missing) in sorted(counts.items()):
        print(f"{group:18}{pages:>5}{rows:>13}{missing:>24}")
    total = sum(v[2] for v in counts.values())
    print(f"Total missing direct source links: {total}")
    if examples and args.max_examples > 0:
        print("Examples (file and line only):")
        for example in examples[:args.max_examples]:
            print("  " + example)
    if not counts:
        print("No HTML files found.", file=sys.stderr)
        return 2
    return 0 if args.report_only or total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
