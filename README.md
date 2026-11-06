# Rent Increase SF — 94122

A verified, source-linked analysis of what may lawfully be charged for two rent-controlled units in a
1940 building in San Francisco's Outer Sunset (ZIP 94122), answering the full question set: how large an
increase is normal, how owners actually impose them, how tenants must be notified, and why the two units
may lawfully receive different increases.

**Live site:** GitHub Pages, repository root (`index.html`) — https://kanlerxz87-cyber.github.io/RentincreaseSF1/

## Repository layout

| Path | Purpose |
| --- | --- |
| `index.html` … `sources.html` | **The published site.** Ten static pages, no build step at serve time |
| `assets/` | Stylesheet and the table-filter script for the published site |
| `build.py` | Generates every published page from `data/*.json`; asserts the arithmetic |
| `check_links.py` | Internal links, fragments, privacy scan, source-coverage check |
| `data/sources.json` | 24-entry source register (city, state, federal, SEC filing) |
| `data/increases.json` | Every published allowable annual increase, 1982–2027 |
| `data/units.json` | Anonymised unit ledger |
| `data/flags.json` | The 11 items on Flagged for Review |
| `research/verified-notes.md` | Note-by-note record taken while reading each primary source |
| `COORDINATION.md` | Shared task board, verification log, integration record, publish record |
| `docs/` | **Archive** — the earlier draft published by a parallel session, left intact and reachable |
| `site/`, `research/*.md`, `scripts/` | **Archive** — that session's earlier pages, notes and build/verify scripts |
| `.github/workflows/pages.yml` | CI: rebuilds and verifies the archived `docs/` site is unchanged |

## Rebuild and verify

```bash
python3 build.py            # regenerate the published pages + assets (with arithmetic assertions)
python3 check_links.py      # must print LINK CHECK OK before publishing
python scripts/build.py && python scripts/verify.py   # the archived draft's own checks
```

## Content rules used

1. Every factual claim carries a source id (`S01`–`S24`) linking to the official document.
2. No value is inferred. Where no official source exists, the cell is blank and the item appears on the
   Flagged for Review page.
3. Percentages are copied from the Rent Board's own schedule; dollar figures are computed from them and
   asserted by `build.py`.
4. No personal identifiers appear anywhere in this repository — including commit messages and the privacy
   checker itself. Tenants are role labels only. Dates and amounts are preserved exactly, because the
   legal analysis depends on them.

## Key verified figures

| Item | Value | Source |
| --- | --- | --- |
| Allowable annual increase, 1 Mar 2026 – 28 Feb 2027 | 1.6% | S01, S02, S03 |
| Prior period, 1 Mar 2025 – 28 Feb 2026 | 1.4% | S02, S03 |
| Absolute annual ceiling in the Ordinance | 7% | S08 §37.3(a)(1) |
| Unit A — $3,995.00 at 1.6% | +$63.92 → $4,058.92 | S01, S02 |
| Unit B — $3,150.00 at 1.6% | +$50.40 → $3,200.40 | S01, S02 |
| Unit B with full banked history (conditional) | 11.7% – 13.1% → $3,518.55 – $3,562.65 | S03, S04, S07 |

Not legal advice.
