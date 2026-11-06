# Rent Increase Review — Outer Sunset, San Francisco (94122)

A source-traced review of what a lawful — and defensible — rent increase looks like for two
rent-controlled flats in a building constructed in 1940 in San Francisco's Outer Sunset.

**Published site:** <https://kanlerxz87-cyber.github.io/RentincreaseSF1/> (GitHub Pages, `main` → `/docs`)

## What this repository contains

| Path | Contents |
| --- | --- |
| `docs/` | The published GitHub Pages site (plain HTML + one stylesheet, no build step) |
| `docs/index.html` | Dashboard and executive summary |
| `docs/units.html` | Anonymised unit records and the year-by-year arithmetic |
| `docs/limits.html` | Published annual allowable increases 2019–2027 and the non-compounding rule |
| `docs/rules.html` | Local, state and federal requirements, each row linked to official text |
| `docs/process.html` | Notice mechanics and lawful versus unlawful reasons |
| `docs/practice.html` | Institutional versus individual owner obligations and practice |
| `docs/discrimination.html` | One unit or both: fair-housing analysis |
| `docs/review.html` | The 12-point test a tenant-side lawyer would run |
| `docs/flagged.html` | Unverified values, conflicting official text, open questions |
| `docs/sources.html` | Source registry with links and verification dates |
| `data/units.csv` | Machine-readable unit facts and computed maximums |
| `data/aga-rates.csv` | Annual allowable increase series with source IDs |
| `data/sources.csv` | Machine-readable source registry |
| `EXECUTIVE_SUMMARY.md` | Stand-alone executive summary |
| `COORDINATION.md` | Shared task board and verification record |
| `tools/check_links.py` | Link, anchor, CSV and source-registry checks |

## Headline findings

* The building dates from 1940, so both units are covered by the San Francisco Rent Ordinance
  (Admin. Code ch. 37) and the local limit governs, not the state's AB 1482 cap.
* The allowable annual increase for increases effective **1 March 2026 – 28 February 2027 is 1.6%**.
* **Unit 1** ($3,995.00, tenancy from 1 Feb 2025): 1.6% = **$63.92** → $4,058.92, effective
  1 Feb 2027 after 30 days' notice. A further 1.4% ($55.93) may be banked — see flag F1.
* **Unit 2** ($3,150.00, tenancy from 1 Jun 2019): the lawful maximum is **13.1% = $412.65** →
  $3,562.65, being seven unused annual allowances added, not compounded. Requires 90 days' notice,
  so the last practical service date for an effective date of 28 Feb 2027 is 30 Nov 2026.
* Raising one unit and not the other is lawful. Discrimination, retaliation and bad-faith pressure
  to vacate are the real risks, and all three are addressed on the site.
* Two administrative prerequisites can void an otherwise correct increase: a current rent-increase
  licence (§37.15) and a notice that itemises the annual and banked portions (§37.3(b), Rule 4.10).

## Verification standard

* Every table row links to a government source: the San Francisco Rent Ordinance, the Rent Board
  Rules and Regulations, SF.gov agency pages, California statutes, or federal statute and agency pages.
* Every percentage was read from the Rent Board's own rate sheet (fact sheet 571), not from a summary.
* Every dollar figure was recomputed from the official percentages and the supplied base rent.
* Where no official source confirmed a value (market rent, owner-behaviour statistics, bedroom counts),
  the value is **left blank** and listed on the Flagged for review page. Nothing is inferred.
* Flags are numbered F1–F12 and cross-referenced between pages and `COORDINATION.md`.

## Privacy

Tenant names and initials are replaced with placeholders (Tenant 1A, 1B, 1C, 1D, 2A, 2B). The street
address is omitted entirely. **Dates and dollar amounts are unchanged**, as instructed. No published
file contains a tenant name, initial, address, telephone number or email address. See
`tools/check_links.py`, which also scans the published pages for the original initials.

## Running the checks locally

```bash
python3 tools/check_links.py
```

The script verifies internal links and anchors, that every CSV parses with a consistent column count,
that every external URL cited in the site is registered in `data/sources.csv`, and that no tenant
initials appear in the published pages. It exits non-zero on failure.

## Not legal advice

This is a research summary with citations, not legal advice. Rates, fees, forms and the ordinance
change; re-verify any figure before relying on it. Free counselling is available from the SF Rent
Board on 415-252-4600.
