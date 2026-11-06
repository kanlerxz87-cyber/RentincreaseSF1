# Verification record

Retrieval date for every source: **2026-11-06**.

## 1. What was checked, and how

| # | Check | Method | Result |
|---|---|---|---|
| 1 | Every source URL resolves and says what is claimed | Each URL fetched and the relevant text read on 2026-11-06; the specific point relied on is recorded per source in `data/sources.json` (`verified` field) and `SOURCES.md` | 37/37 fetched and read |
| 2 | Values transcribed, not recalled | Values copied from the fetched text of the statute/agency page; no value taken from memory or from a search-result snippet alone | Done |
| 3 | Historical rate table | Transcribed cell by cell from the Rent Board's official PDF `571 Allowable Annual Increases 26-27`; the three most recent years cross-checked against two other Rent Board pages | 46 rows match; 3 recent years confirmed independently |
| 4 | Everything in the "used" years adds up | `tools/check_site.py` sums the AGA rows flagged for each unit and compares to the stated totals (3.0%, 13.1%) | Pass |
| 5 | Every dollar figure recomputes | `tools/check_site.py` recomputes increase = current rent × total %, and new rent = current + increase, for every scenario | Pass |
| 6 | Blank means blank | Any row with a blank percentage must have blank dollar amounts; unverified cells carry an explicit marker | Pass |
| 7 | One source link per table row | `tools/check_site.py` walks every `<tr>` in every table; a row must carry a source link or an explicit unverified marker | Pass (693 checks, 0 errors) |
| 8 | Every registered source is actually linked on the site | URL presence check against rendered HTML | Pass |
| 9 | No inline reference to an unknown source | Regex on rendered output vs. the register | Pass |
| 10 | Internal links and anchors | Every `href` resolved against the generated files and every `#anchor` resolved against the target page's ids | Pass |
| 11 | Table integrity | Column count of every row checked against its header row | Pass |
| 12 | Privacy | Six known personal-name strings searched across all output pages | Pass — none present |
| 13 | Site serves | All 12 pages plus the stylesheet return HTTP 200 from a local server; no external JS, CSS or font requests | Pass |

Reproduce with:

```bash
python3 build/build.py && python3 tools/check_site.py
```

## 2. Sources that were checked and then **not** relied on

| Source | What happened |
|---|---|
| Several commercial SF rent-increase calculators and blogs | Publish **1.7%** for 3/1/26–2/28/27. The Rent Board's pages and official PDF both say **1.6%**; 1.7% is the figure for 3/1/24–2/28/25. Excluded from all calculations. Recorded as FLAG-11. |
| ReLISTO blog | Fetched in full. Agrees on 1.6% and on the missing October 2025 CPI as the reason for the estimated figure. It does **not** describe how owners set rents, so an earlier draft claim that it did was removed. Retained only as corroboration of 1.6%. |
| U.S. Census data API | Returned `Missing Key` for every query. No Census figure used. |
| HUD Fair Market Rent documentation system | The interactive lookup returned empty/placeholder output for the area parameters reachable in this session. No FMR figure used. Recorded as FLAG-05. |
| HUD Fair Housing Act overview (first attempt) | The URL in an earlier draft redirected to the HUD home page. Replaced with `hud.gov/helping-americans/fair-housing-act-overview`, which was fetched and read. |
| `sf.gov/information--tenant-harassment` | 404 on fetch. Replaced with the actual ordinance text at `sf.gov/information--sec-3710b-tenant-harassment`. |
| `sf.gov/information/sec-373-rent-increases` | 404 on fetch. Correct path is `sf.gov/information/sec-373-rent-limitations`. |

## 3. Irregularities found (full detail on the site's Flagged for Review page)

| ID | Severity | Irregularity |
|---|---|---|
| FLAG-01 | medium | Building year (1940) is owner-supplied; not confirmed against Assessor or Planning records |
| FLAG-02 | high | Unit 1 anniversary date ambiguous between Feb 1 and Apr 1 after the April 2026 tenant change at unchanged rent |
| FLAG-03 | high | Assumption that Unit 2 has had no increase since 2019 — the 13.1% depends entirely on it |
| FLAG-04 | high | Unit 2's 13.1% maximum expires 2027-02-28; the 2027–28 rate is unpublished |
| FLAG-05 | low | No verified ZIP-level market rent obtained; none used anywhere |
| FLAG-06 | medium | Whether $3,995 / $3,150 are entirely base rent is unconfirmed |
| FLAG-07 | medium | Whether the added Unit 1 tenant is a co-tenant or subtenant is unknown |
| FLAG-08 | low | No sourced description of how large or individual owners actually set rents |
| FLAG-09 | high | Rent increase licence status unknown; without it the increase is unenforceable |
| FLAG-10 | medium | No facts on complaints, inspections, organising or buyout discussions |
| FLAG-11 | low | Third-party **1.7%** vs official **1.6%** for the same period |
| FLAG-12 | low | The 1.6% rate is itself an estimate because October 2025 CPI was never published |
| FLAG-13 | low | Tenant names held internally; no name map in the repository |

## 4. Statement of limits

- This is an analysis of public law, not legal advice.
- Every figure depends on the owner's own rent history being complete; that history was not available.
- Coverage was accepted from the stated 1940 construction date; the certificate-of-occupancy date and dwelling-unit count were not independently confirmed.
- The 2027–28 allowable increase had not been announced as of 2026-11-06 and is left blank wherever it would appear.
