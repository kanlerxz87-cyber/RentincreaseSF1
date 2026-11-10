# Current-state verification — 2026-11-10

## Scope

This final integration rechecked the two official sources whose content can change the proposed Unit 2 banked-increase scenario and reran the canonical, assurance, arithmetic, privacy, reproducibility, internal-link, and preserved legacy checks. It did not treat the earlier 2026-11-07/08 retrieval record as a fresh retrieval of every source. Each registry and manifest row retains its actual retrieval date.

## New official-source finding

| Official source | Retrieved | Exact verified content | Effect on this repository |
|---|---|---|---|
| [SF Rent Board — Learn about rent increases in San Francisco](https://www.sf.gov/learn-about-rent-increases-san-francisco) | 2026-11-10 | In a section titled “Notice: Proposed Changes to Rent Increase Limitations,” posted November 9, 2026, the Board states that if enacted as currently proposed, File No. 261020 would apply to banked rent increases noticed on or after September 15, 2026 and capital-improvement increases based on petitions filed on or after that date. It expressly states the legislation has not been enacted and is subject to change. | Added to S05 and H-22; prominent warnings added to the landing, limits, and notice pages. Early service is not described as a way to avoid the proposal. No current-law calculation was changed. |
| [SF Board of Supervisors Legistar — File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770) | 2026-11-10 | Status: Pending Committee Action. Introduced 9/15/2026. Land Use and Transportation Committee. No final action, enactment date, or enactment number. The title proposes a total 10% per-year cap on banked and capital-improvement increases for three years. | S26 and H-22 updated to 2026-11-10. The proposal remains unapplied to all figures and clearly labeled not law. |

## Repository irregularities corrected

1. Two landing-page table cells contained the literal template token `{n}` because the question table was constructed before the outer template was formatted. The cells now render the generated counts (15 review checks and 24 flags), and both verification suites reject a recurrence.
2. The canonical registry omitted the Rent Board's November 9 warning about the proposed notice-date reach. S05, S26, H-22, and review check 15 now preserve that distinction between pending legislation and its proposed application date.
3. The common footer previously implied every source had been re-fetched on one date. It now says the registry is verified through the current date and points to each source's actual retrieval date.

## Arithmetic and legal conclusions rechecked

The new proposal does not change current law or the conditional calculations. The independently recomputed amounts remain Unit 1 annual-only $63.92 / $4,058.92 and combined $119.85 / $4,114.85; Unit 2 annual-only $50.40 / $3,200.40 and combined $412.65 / $3,562.65. Unit 2's 13.1% combined scenario remains expressly conditional and unready for notice. Current base, ledger, lease, license, coverage, repairs, retaliation, occupancy, and service facts remain flagged rather than inferred.

## Verification gates

- `python3 hub/build.py`: 9 pages regenerated.
- `python3 assurance/build.py`: assurance page and all 29 manifest rows regenerated with per-source dates.
- `python3 tools/verify_hub.py`: 1,599 checks, 0 errors; 211 source/flag-linked claim rows.
- `python3 tools/verify_assurance.py`: 1,822 checks, 0 errors; 33 source-linked assurance rows; 171 current text files privacy-scanned.
- Added positive assertions requiring the November 9 warning on the landing page, S05/S26 citations on H-22, review check 15, and no unrendered `{n}` token.

Unresolved items remain published on the canonical Flagged for Review page. The historical-Git privacy limitation is not claimed to be fixed by current-file scanning.
