# Rent Increase Review — Outer Sunset, San Francisco (94122)

A source-traced review of what a lawful — and defensible — rent increase looks like for two
rent-controlled flats in a building constructed in 1940 in San Francisco's Outer Sunset.

**Published site:** <https://kanlerxz87-cyber.github.io/RentincreaseSF1/> — GitHub Pages serves
`main` (legacy branch publishing, root `/`). The root `index.html` is the **integrated dashboard**
(below); it links to every earlier edition.

## Entry point — the integrated dashboard (`index.html` + `hub/`)

`index.html` is now a dashboard rather than a redirect. It leads with the owner's first question —
whether an individual owner needs a Rent Board rent-increase licence before raising the rent — and
then routes to eight category pages, each a table-driven page with an official source link on every
claim row.

| Path | Contents |
| --- | --- |
| `index.html` | Landing dashboard: the licence answer, four KPI figures, every question mapped to its page |
| `hub/licensing.html` | The licence and the Rent Board, question by question (§37.15, §37.3, Housing Inventory) |
| `hub/limits.html` | Rate history 1982–2027, local/state/federal layering, both units' arithmetic |
| `hub/notice.html` | Notice contents, computed service deadlines, lawful vs unlawful reasons |
| `hub/practice.html` | Corporate vs individual owners, and the algorithmic-pricing ban |
| `hub/fair-housing.html` | One unit or both: FEHA, the Fair Housing Act, §37.10B(a)(9) |
| `hub/review.html` | The 12-point tenant-lawyer test and where the file stands |
| `hub/flags.html` | Flagged for Review — 16 items, each with its official source link |
| `hub/sources.html` | 19 official sources with the verbatim quote each claim rests on |
| `hub/data.json` | Every figure, quote, link and flag used by the dashboard (single source of truth) |
| `hub/build.py` | Generator; all amounts are computed, never typed |
| `tools/verify_hub.py` | 1,028 checks: per-row citations, links, arithmetic, dates, privacy |

```bash
python3 hub/build.py        # regenerate index.html and hub/*.html from hub/data.json
python3 tools/verify_hub.py # 1,028 checks; exit 0 = clean
```

`verify_hub.py` fails on a table row without an official-source or flag link, a citation to an
unknown source id, a registered source that is never cited, an internal link or anchor that does not
resolve, a navigation that differs between pages, and any dollar figure on the site that cannot be
recomputed from a published percentage or found verbatim in a source quote. That last check is what
keeps an unsourced number from appearing.


## What this repository contains

| Path | Contents |
| --- | --- |
| `docs/` | The published site: plain HTML plus one stylesheet, no build step, no external assets |
| `docs/index.html` | Dashboard and executive summary |
| `docs/units.html` | Anonymised unit records and the year-by-year arithmetic |
| `docs/limits.html` | Published annual allowable increases 2019–2027 and the non-compounding rule |
| `docs/rules.html` | Local, state and federal requirements, each row linked to official text |
| `docs/process.html` | Notice mechanics and lawful versus unlawful reasons |
| `docs/practice.html` | Institutional versus individual owner obligations and practice |
| `docs/discrimination.html` | One unit or both: fair-housing analysis |
| `docs/review.html` | The 12-point test a tenant-side lawyer would run |
| `docs/flagged.html` | Unverified values, conflicting official text, open questions (F1–F12) |
| `docs/sources.html` | Source registry (S1–S31) with links and verification dates |
| `docs/v1/` | Archived earlier version of the site, preserved with a banner linking to the current dashboard |
| `data/units.csv` | Machine-readable unit facts and computed maximums |
| `data/aga-rates.csv` | Annual allowable increase series with source IDs |
| `data/sources.csv` | Machine-readable source registry |
| `EXECUTIVE_SUMMARY.md` | Stand-alone executive summary |
| `COORDINATION.md` | Shared task board, verification record and integration log |
| `tools/check_links.py` | Link, anchor, citation, CSV and privacy checks (run in CI) |
| `research/` | Earlier session's research notes, kept for reference; not published |
| `site/` | Earlier static draft, kept for reference; not published |
| `archive/v1-tooling/` | The v1 site generator (`build.py`) and checker (`verify.py`), kept for reference |

> **Note on the two generations of this site.** Work on this repository proceeded in parallel
> sessions. A first published version lives, unmodified apart from an archive banner, in `docs/v1/`.
> The current version in `docs/` supersedes it: it adds the fair-housing analysis, the tenant-lawyer
> review test, the complete rate series, and a source registry restricted to government sources.
> Nothing from v1 was deleted; `research/`, `site/` and `archive/v1-tooling/` preserve the earlier
> work in the repository.

## Headline findings

* The building dates from 1940, so both units are covered by the San Francisco Rent Ordinance
  (Admin. Code ch. 37) and the local limit governs, not the state's AB 1482 cap of 8.8%.
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
file contains a tenant name, initial, address, telephone number or email address.
`tools/check_links.py` scans every published page (including the archive) for the original initials,
and the CI workflow repeats the scan with `grep`.

## Running the checks locally

```bash
python3 tools/check_links.py
```

The script verifies internal links and anchors, that every CSV parses with a consistent column count,
that every external URL cited in the site is registered in `data/sources.csv`, that all published
pages share the same navigation, and that no tenant initials appear in any published page. It exits
non-zero on failure. The same command runs in `.github/workflows/pages.yml` on every push and pull
request to `main`.

## Not legal advice

This is a research summary with citations, not legal advice. Rates, fees, forms and the ordinance
change; re-verify any figure before relying on it. Free counselling is available from the SF Rent
Board on 415-252-4600.
---

## Companion edition — `docs/v2/`

Session `arena-d52bb8e2` independently built a second, self-contained edition at **`docs/v2/`**
(entry point `docs/v2/index.html`). It does not overwrite or modify anything in `docs/*.html`; the two
sites link to each other. It reached **identical figures to the cent** and is useful because it adds
material the main edition does not duplicate:

| Path | Contents |
| --- | --- |
| `docs/v2/` | The companion site: 13 pages, plain HTML plus one stylesheet, no JavaScript, no CDN |
| `docs/v2/requirements.html` | 31-row requirement matrix across local, state and federal law |
| `docs/v2/rates.html` | Every published allowable increase, 1982–2027, with the years used by each unit marked |
| `docs/v2/review.html` | A 14-point tenant-lawyer review test with a pass condition per question |
| `docs/v2/flags.html` | A 13-item flag register with severity, effect on the numbers and resolution step |
| `docs/v2/reconciliation.html` | Row-by-row comparison of this edition against the main edition |
| `data/v2/*.json` | The companion edition's single source of truth |
| `build/build.py` | Generator for the companion edition (reads `data/v2/`, writes `docs/v2/`) |
| `tools/check_site.py` | 693 checks for the companion edition |
| `EXECUTIVE-SUMMARY.md`, `SOURCES.md`, `VERIFICATION.md` | Companion edition's summary and records |

Rebuild and verify the companion edition:

```bash
python3 build/build.py      # regenerate docs/v2/ from data/v2/
python3 tools/check_site.py # 693 checks; exit 0 = clean
```

`tools/check_site.py` fails on: a broken internal link or anchor, a source URL missing from the site,
an inline reference to an unknown source id, a table row with neither a source link nor an unverified
marker, any personal name in output, a table row whose column count disagrees with its header, or any
dollar figure that does not recompute from the published percentages.

### Agreement between the two editions

Both editions independently reached: Unit 1 at 1.6% = **$63.92** → $4,058.92, or 3.0% = **$119.85** →
$4,114.85 with the banked 1.4%; Unit 2 at 13.1% = **$412.65** → $3,562.65; 30-day notice for Unit 1 and
**90 days** for Unit 2; percentages added and never compounded. Both also independently flagged the
Unit 1 anniversary-date ambiguity and the absence of any official data on how owners behave. See
`docs/v2/reconciliation.html`.

