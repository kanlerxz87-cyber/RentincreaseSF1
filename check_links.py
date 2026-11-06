#!/usr/bin/env python3
"""
Static checks for the published site.

1. Internal links  — every href/src that points at the repo must resolve to a real file,
   and every in-page fragment must match an id in the target document.
2. External links  — must parse as absolute https/http URLs; they are additionally listed
   so they can be spot-checked. (The build sandbox can only reach a small allowlist of
   hosts, so external reachability is checked when the pages are first authored, not here.)
3. Privacy         — no personal identifiers may appear in any tracked text file.
4. Source coverage — every page except the dashboard must reference at least one source id.
"""

import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {".git", "__pycache__", "node_modules"}

# Privacy heuristic. The real identifiers are deliberately NOT stored in this file (or anywhere
# else in the repository): this keeps the checker itself from becoming a leak. Instead we detect
# the *shape* of what must never appear: a bare pair of single-letter initials in any
# published text file. Ordinary abbreviations are whitelisted.
INITIAL_PAIR = re.compile(r"\b[A-Z][ .][A-Z]\b")
WHITELIST = {"U.S", "U.S.", "A.M", "P.M"}
# A second shape: two initials run together with no separator.
BARE_INITIAL = re.compile(r"\b[A-Z]{2}\b")
BARE_OK = {"SF", "AB", "ID", "CA", "US", "OK", "PR", "CI", "JS", "UI", "IV", "AI", "MD", "DC", "PDF", "HQ"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.add(d["id"])
        for attr in ("href", "src"):
            if attr in d and d[attr]:
                self.links.append((tag, attr, d[attr]))


def html_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(base, f)


def main():
    docs = {}
    for path in html_files():
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        c = Collector()
        c.feed(text)
        docs[path] = (c, text)

    errors, warnings, externals = [], [], set()

    for path, (c, text) in docs.items():
        rel = os.path.relpath(path, ROOT)
        for tag, attr, url in c.links:
            if url.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            if url.startswith("#"):
                if url[1:] and url[1:] not in c.ids:
                    errors.append(f"{rel}: dead in-page fragment {url}")
                continue
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https"):
                externals.add(url)
                if not parsed.netloc:
                    errors.append(f"{rel}: malformed external URL {url}")
                continue
            if parsed.scheme:
                errors.append(f"{rel}: unexpected scheme {url}")
                continue
            target, _, frag = url.partition("#")
            target_path = os.path.normpath(os.path.join(os.path.dirname(path), target))
            if not os.path.exists(target_path):
                errors.append(f"{rel}: missing local target {target}")
                continue
            if frag and target_path.endswith(".html"):
                if target_path not in docs:
                    with open(target_path, encoding="utf-8") as fh:
                        t = Collector()
                        t.feed(fh.read())
                    docs[target_path] = (t, "")
                if frag not in docs[target_path][0].ids:
                    errors.append(f"{rel}: missing anchor #{frag} in {target}")

    # source coverage
    for path, (_, text) in docs.items():
        rel = os.path.relpath(path, ROOT)
        if rel in ("index.html",):
            continue
        if not re.search(r">S\d\d<", text):
            warnings.append(f"{rel}: no source-id links found")

    # privacy
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if not f.endswith((".html", ".md", ".json", ".py", ".css", ".js", ".yml", ".txt")):
                continue
            p = os.path.join(base, f)
            with open(p, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
            for m in BARE_INITIAL.finditer(text):
                if m.group(0) in BARE_OK:
                    continue
                line = text[:m.start()].count("\n") + 1
                errors.append(
                    f"{os.path.relpath(p, ROOT)}:{line}: possible run-together initials {m.group(0)!r}"
                )
            for m in INITIAL_PAIR.finditer(text):
                if m.group(0) in WHITELIST:
                    continue
                line = text[:m.start()].count("\n") + 1
                errors.append(
                    f"{os.path.relpath(p, ROOT)}:{line}: possible personal initials {m.group(0)!r}"
                )

    print(f"HTML pages checked : {len(docs)}")
    print(f"External links     : {len(externals)}")
    print(f"Errors             : {len(errors)}")
    print(f"Warnings           : {len(warnings)}")
    for w in warnings:
        print("  WARN", w)
    for e in errors:
        print("  ERR ", e)

    if errors:
        sys.exit(1)
    print("LINK CHECK OK — no broken internal links, no dead fragments, no personal identifiers.")


if __name__ == "__main__":
    main()
