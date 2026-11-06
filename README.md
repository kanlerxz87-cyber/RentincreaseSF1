# Rent Increase SF — 94122

A verified, source-linked analysis of what may lawfully be charged for two rent-controlled units in a
1940 building in San Francisco's Outer Sunset (ZIP 94122), plus the tenant-facing question set: how
large an increase is normal, how owners actually impose them, how tenants must be notified, and why
the two units may lawfully receive different increases.

**Live site:** published from this branch through GitHub Pages.

## What is here

| Path | Purpose |
| --- | --- |
| `index.html` … `sources.html` | The published site (static HTML, no build step at serve time) |
| `build.py` | Generates every page from `data/*.json`; also runs the consistency check |
| `check_links.py` | Internal-link, fragment, privacy and source-coverage checks |
| `data/sources.json` | 24-entry source register (city, state, federal, SEC filing) |
| `data/increases.json` | Every published allowable annual increase, 1982–2027 |
| `data/units.json` | Anonymised unit ledger |
| `data/flags.json` | The 11 items on Flagged for Review |
| `COORDINATION.md` | Shared task board: task status, ownership, verification log, publish record |
| `research/verified-notes.md` | Raw notes taken while reading each primary source |

## Rebuild

```bash
python3 build.py          # regenerate HTML + assets, with the arithmetic assertions
python3 check_links.py    # must print LINK CHECK OK before publishing
```

## Content rules used

1. Every factual claim carries a source id (`S01`–`S24`) that links to the official document.
2. No value is inferred. Where an official source does not exist, the cell is blank and the item is
   listed on the Flagged for Review page.
3. Percentages are copied from the Rent Board's own schedule; dollar figures are computed from them.
4. No personal identifiers appear in this repository. Tenants are role labels only. Dates and
   dollar amounts are preserved exactly, because the legal analysis depends on them.

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
