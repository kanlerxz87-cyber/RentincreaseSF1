# Session `arena-53d8f8c1` — independent re-verification (2026-11-11 UTC)

**Scope:** `audit/session-53d8f8c1/**` only. No canonical file (`index.html`, `hub/**`, `assurance/**`, root Markdown) was edited under this claim. If a correction had been proved necessary it would have been logged as a request in `COORDINATION.md`; none was needed.

**Privacy:** placeholders only. Dates and supplied dollar amounts are preserved as anonymized scenario inputs. No name, initial, street address, e-mail or telephone number from the owner's brief appears in this file.

**Method:** each official page below was fetched and read live on 2026-11-11. Dollar figures were recomputed independently with `Decimal` arithmetic. Every local suite was then run on the combined tree.

## 1. Live official-source re-verification (2026-11-11)

| # | Official source | URL | Result on 2026-11-11 |
| --- | --- | --- | --- |
| 1 | SF Administrative Code §37.15 — Reporting Obligations; Licensing | https://www.sf.gov/information/sec-3715-reporting-obligations-licensing | **Confirmed.** §37.15(a) requires owners of units subject to Chapter 37 to report; §37.15(c) sets annual March 1 updates (buildings with fewer than 10 units from March 1, 2023); §37.15(e) grants the license only on substantial compliance, suspends it during noncompliance, restores it prospectively, and states the tenant is not obligated for suspension months. No individual-owner or two-unit exemption appears in the text. Matches `hub/licensing.html` and `EXECUTIVE_SUMMARY.md` §1. |
| 2 | SF Rent Board — Housing Inventory | https://www.sf.gov/rent-board-housing-inventory | **Confirmed.** "All owners of residential property are required to report"; reporting is free; tenant-occupied units receive a license after submission; the license is automatically generated for non-owner-occupied units; a current license must be on file on the effective date; the license need not be included with the notice. Matches the landing-page answer. |
| 3 | SF Rent Board — Learn about rent increases | https://www.sf.gov/learn-about-rent-increases-san-francisco | **Confirmed.** Allowed increase **1.6% effective March 1, 2026 – February 28, 2027** (60% of Bay Area CPI-U); calculated on base rent only; no rounding up; 30-day notice (90 days if >10%); +5 days if mailed; license required before imposing. The November 9, 2026 File #261020 notice is displayed on the page. Matches `hub/limits.html`. |
| 4 | SF Rent Board — Banked rent increases | https://www.sf.gov/information--banked-rent-increases | **Confirmed.** Skipped increase banked only if at least 24 full months pass without an increase; banked increases are added, never compounded or prorated; no Rent Board approval needed; license required; 30/90-day notice with banked portion identified. Matches `hub/limits.html` and the Rule 4.12 distinction recorded in the executive summary. |
| 5 | SF Administrative Code §37.3 — Rent Limitations | https://www.sf.gov/information--sec-373-rent-limitations | **Confirmed.** §37.3(a)(1) caps the annual increase at 60% of the published CPI increase (7% ceiling) for landlords who have reported under §37.15; §37.3(a)(2) permits banking subject to §37.15. Matches the local-layer description. |
| 6 | California Civil Code §827 | https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827&lawCode=CIV | **Confirmed.** §827(b)(2): 30 days if the increase is 10% or less (alone or combined over the prior 12 months); §827(b)(3): 90 days if greater than 10%. Matches `hub/notice.html` bands. |
| 7 | Board of Supervisors File #261020 (Legistar) | https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770 | **Confirmed — still not law.** Status **Pending Committee Action**; introduced 9/15/2026; no final action, no enactment date. Matches flag `H-22` and the landing-page warning. |
| 8 | SF Treasurer & Tax Collector — Information for Lessors of Residential Real Estate | https://sftreasurer.org/information-lessors-residential-real-estate | **Confirmed.** "One residential structure consisting of fewer than four units" is not, "by reason of that fact alone", required to obtain a business registration certificate; other business activity, payroll expense, or short-term rental income can change that. Matches the conditional determination (flag `H-21`). |

**Conclusion on sources:** every load-bearing fact re-checked live on 2026-11-11 agrees with the canonical dashboard. No correction to `hub/data.json`, `hub/build.py`, `index.html`, or the root Markdown is required under this claim.

## 2. Independent arithmetic recompute (Decimal)

| Scenario | Recompute | Result | Site figure | Agrees |
| --- | --- | --- | --- | --- |
| Unit 1 annual only | $3,995.00 × 1.6% | $63.92 → $4,058.92 | $63.92 → $4,058.92 | Yes |
| Unit 1 banked portion | $3,995.00 × 1.4% | $55.93 | $55.93 | Yes |
| Unit 1 combined 3.0% | $3,995.00 × 3.0% | $119.85 → $4,114.85 | $119.85 → $4,114.85 | Yes |
| Unit 2 annual only | $3,150.00 × 1.6% | $50.40 → $3,200.40 | $50.40 → $3,200.40 | Yes |
| Unit 2 banked 11.5% (1.8+0.7+2.3+3.6+1.7+1.4) | $3,150.00 × 11.5% | $362.25 | $362.25 | Yes |
| Unit 2 combined 13.1% | $3,150.00 × 13.1% | $412.65 → $3,562.65 | $412.65 → $3,562.65 | Yes |
| Unit 2 90-day personal-service date for Feb 28, 2027 | Feb 28, 2027 − 90 days | Nov 30, 2026 | Nov 30, 2026 | Yes |
| Unit 2 95-day mail date for Feb 28, 2027 | Feb 28, 2027 − 95 days | Nov 25, 2026 | Nov 25, 2026 | Yes |
| Unit 1 30/35-day dates for Feb 1, 2027 | Feb 1, 2027 − 30/35 days | Jan 2, 2027 / Dec 28, 2026 | Jan 2, 2027 / Dec 28, 2026 | Yes |

All figures remain **conditional scenario arithmetic**, not certified lawful rents. Unit 1's April 2026 fixed-term/month-to-month status, Unit 2's current base rent, both ledgers, both licenses, and official coverage remain unresolved and flagged (see `hub/flags.html`).

## 3. Local suite run (2026-11-11, combined tree)

| Suite | Result |
| --- | --- |
| `hub/build.py` + `assurance/build.py` reproducibility | No diff to committed pages |
| `tools/verify_hub.py` | 1,599 checks, 0 errors (211 source/flag-linked claim rows, 29 sources) |
| `tools/verify_assurance.py` | 1,822 checks, 0 errors (214 current text files privacy-scanned) |
| `tools/check_links.py` | OK (10 published pages, links/anchors/CSVs resolve) |
| `tools/check_site.py` | 781 checks, 0 errors |
| `integration/verify.py` | PASS |
| `dashboard/verify.py` | OK |
| `audit/verify_all.py` | OK |
| `review/verify.py` | PASS |
| `compliance/verify.py` | 3,277 checks, 0 errors |

Every claim-table row on the canonical pages carries a direct official-source link or an explicit flag; unconfirmed values remain blank. No personal identifier was found in current text files by the privacy scans.

## 4. Irregularities and flags (none block publication)

1. **Stale open PRs #29 and #32** (both `CONFLICTING`, last updated 2026-11-10 05:5x UTC). Their findings were already carried into `main` through PR #42; this session recommends closing both as superseded. Recorded here; no file change made to their branches.
2. **Pending File #261020** — still `Pending Committee Action` on 2026-11-11 (see §1, row 7). Any banked notice served on or after September 15, 2026 falls inside the proposed retroactive window. Flag `H-22` stands; do not serve notice from the illustrations without re-checking the file and obtaining advice.
3. **Unresolved private facts** — Unit 1 lease status, Unit 2 current base, both ledgers, both licenses, official coverage, and the absence of an official 94122 "normal market increase" or owner-type behavior dataset. All remain blank/flagged on `hub/flags.html` (24 flags). No value was inferred.
4. **Historical privacy** — earlier public Git history may contain tenant initials; current-file scans do not remediate history. Already disclosed on the landing page and in the flags page. No new identifier was introduced by this session.

## 5. Answers to the owner's questions (summary; full text on the site)

* **Individual owner vs. corporation:** yes, an individual owner must report each tenant-occupied unit through the Housing Inventory and hold a current Rent Increase License on the effective date. No corporation and no individual-owner exemption. Ordinary annual/banked notices go to the tenant, not to the Board for approval. See `hub/licensing.html`.
* **Reasonable/normal increase:** the only official "normal" figure is the Rent Board's annual allowance (1.6% for Mar 1, 2026 – Feb 28, 2027) plus any valid banked percentages, added without compounding. No official 94122 market-normal figure was located; that cell stays blank and flagged.
* **How owners handle increases:** official sources state owner-neutral duties (license, base-rent-only calculation, written notice, repair/retaliation compliance). No official dataset on corporation-vs-individual behavior was located; that cell stays blank and flagged.
* **One unit or both:** different treatment is not automatically discrimination and identical treatment is not immunity; the neutral, documented, ledger-based selection process matters. See `hub/fair-housing.html` and the 15-check tenant-lawyer test on `hub/review.html`. No attorney verdict is promised.

*This file is research, not legal advice. Resolve all high-severity flags and review the actual lease, ledger, license record, and notice before serving. SF Rent Board counseling: 415-252-4600.*
