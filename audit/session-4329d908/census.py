#!/usr/bin/env python3
"""Row-level census of every HTML page GitHub Pages serves from this repository.

For each table body row it records whether the row carries
  * a DIRECT link to an official publisher,
  * only an INDIRECT link (a local anchor such as sources.html#S01), or
  * NO link at all.
It also lists every external host that is not an official publisher.

Read-only.  Usage:  python3 audit/session-4329d908/census.py [--json] [--rows DIR]
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]

# Official publishers that do not use a .gov host name.
OFFICIAL_EXACT = {
    "sf.gov", "www.sf.gov", "media.api.sf.gov",
    "sfgov.legistar.com",                 # San Francisco Board of Supervisors legislative record
    "portal.sfrb.org", "sfrb.org", "www.sfrb.org",   # San Francisco Rent Board
    "sftreasurer.org", "www.sftreasurer.org",        # SF Treasurer & Tax Collector
    "sfassessor.org", "www.sfassessor.org",          # SF Assessor-Recorder
    "sfplanninggis.org",                              # SF Planning property information map
    "sfdbi.org", "www.sfdbi.org",                    # SF Department of Building Inspection
    "sfbos.org", "www.sfbos.org",                    # SF Board of Supervisors
    "sfgov.org", "www.sfgov.org",
    "leginfo.legislature.ca.gov",                     # California Legislative Information
    "www4.courts.ca.gov", "www.courts.ca.gov", "courts.ca.gov", "selfhelp.courts.ca.gov",
    "codelibrary.amlegal.com",                        # official publisher of the SF Municipal Code
    "uscode.house.gov",                               # Office of the Law Revision Counsel
}


def is_official(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https"):
        return False
    host = (p.hostname or "").lower()
    return host.endswith(".gov") or host in OFFICIAL_EXACT


class Rows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict] = []
        self.hosts: Counter = Counter()
        self._tr: dict | None = None
        self._in_td = False
        self._depth_table = 0
        self.title = ""
        self._in_title = False
        self.text_all: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "table":
            self._depth_table += 1
        if tag == "tr" and self._depth_table:
            self._tr = {"td": 0, "direct": [], "indirect": [], "other": [], "text": []}
        if tag == "td" and self._tr is not None:
            self._tr["td"] += 1
            self._in_td = True
        if tag == "a" and a.get("href"):
            href = a["href"]
            p = urlparse(href)
            if p.scheme in ("http", "https"):
                self.hosts[(p.hostname or "").lower()] += 1
            if self._tr is not None:
                if is_official(href):
                    self._tr["direct"].append(href)
                elif p.scheme in ("http", "https"):
                    self._tr["other"].append(href)
                elif p.scheme == "" and href and not href.startswith("mailto:"):
                    self._tr["indirect"].append(href)

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "td":
            self._in_td = False
        if tag == "tr" and self._tr is not None:
            if self._tr["td"]:
                self._tr["text"] = " ".join("".join(self._tr["text"]).split())
                self.rows.append(self._tr)
            self._tr = None
        if tag == "table" and self._depth_table:
            self._depth_table -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._tr is not None and self._in_td:
            self._tr["text"].append(data)
        self.text_all.append(data)


def edition_of(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) == 1:
        return "(root)"
    if parts[0] == "docs" and len(parts) > 2:
        return "docs/" + parts[1]
    return parts[0]


def census() -> dict:
    out = defaultdict(lambda: {"pages": 0, "rows": 0, "direct": 0, "indirect_only": 0,
                               "unofficial_only": 0, "none": 0, "unofficial_hosts": Counter(),
                               "banner": 0, "problem_rows": []})
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith((".git/", "node_modules/")) or "/." in "/" + rel:
            continue
        p = Rows()
        p.feed(path.read_text(encoding="utf-8", errors="replace"))
        e = out[edition_of(rel)]
        e["pages"] += 1
        if 'data-legacy-notice' in path.read_text(encoding="utf-8", errors="replace"):
            e["banner"] += 1
        for host, n in p.hosts.items():
            if not (host.endswith(".gov") or host in OFFICIAL_EXACT):
                e["unofficial_hosts"][host] += n
        for r in p.rows:
            e["rows"] += 1
            if r["direct"]:
                e["direct"] += 1
            elif r["indirect"]:
                e["indirect_only"] += 1
                e["problem_rows"].append((rel, "indirect", r["text"][:110], r["indirect"][:2]))
            elif r["other"]:
                e["unofficial_only"] += 1
                e["problem_rows"].append((rel, "unofficial", r["text"][:110], r["other"][:2]))
            else:
                e["none"] += 1
                e["problem_rows"].append((rel, "none", r["text"][:110], []))
    return out


def main() -> int:
    data = census()
    if "--json" in sys.argv:
        print(json.dumps({k: {**v, "unofficial_hosts": dict(v["unofficial_hosts"])} for k, v in data.items()},
                         indent=1, ensure_ascii=False))
        return 0
    print(f"{'edition':<14}{'pages':>6}{'banner':>7}{'rows':>6}{'direct':>8}{'indirect':>9}{'unoff.':>7}{'none':>6}  unofficial hosts")
    for k in sorted(data):
        v = data[k]
        hosts = ", ".join(f"{h}×{n}" for h, n in v["unofficial_hosts"].most_common(6))
        print(f"{k:<14}{v['pages']:>6}{v['banner']:>7}{v['rows']:>6}{v['direct']:>8}{v['indirect_only']:>9}{v['unofficial_only']:>7}{v['none']:>6}  {hosts}")
    if "--rows" in sys.argv:
        want = sys.argv[sys.argv.index("--rows") + 1]
        for rel, kind, text, links in data[want]["problem_rows"]:
            print(f"  [{kind}] {rel}: {text} {links}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
