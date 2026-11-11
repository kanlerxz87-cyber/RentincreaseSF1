# Focused official-source and repository verification — 2026-11-11

## Scope and limits

This is a focused follow-up to the repository's existing canonical source audit, not a claim that all 29 canonical sources were fetched again today. The latest published canonical source inventory records 29 official sources verified on 2026-11-10. On 2026-11-11, the official pages directly relevant to individual-owner licensing, public Housing Inventory disclosure, current annual allowance, annual/banked notice rules, the state rent cap, and proposed San Francisco legislation were fetched and read. The current published suite was then rerun. Personal names, tenant initials, street address, and contact details from the owner's brief are not reproduced here.

## Official sources fetched and read on 2026-11-11

| Official source | Verified finding used in this review |
|---|---|
| [SF Administrative Code §37.15 — Reporting Obligations; Licensing](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) | Owners of covered Chapter 37 units report; the ordinance specifies unit mailing address and, for non-owner-occupied units, information including owner or designated property-manager business contact, occupancy history and base rent in $250 increments. Substantial reporting compliance generates a license for §37.3(a)(1)–(2) increases; noncompliance suspends it, with restoration prospective. |
| [SF Rent Board Housing Inventory](https://www.sf.gov/rent-board-housing-inventory) | The page says all residential property owners report, describes the March 1 annual deadline and late submission, states that the information submitted is public, and says a current rent-increase license must be on file before an annual/banked increase takes effect. License generation is automatic for reported tenant-occupied units; the license need not be attached to the tenant notice. |
| [SF Rent Board Form 571 — Allowable Annual Increases](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) | The allowance is 1.6% for effective dates March 1, 2026–February 28, 2027; the official preceding rates read for scenario calculations include 1.4%, 1.7%, 3.6%, 2.3%, 0.7%, and 1.8%. |
| [SF Rent Board — Learn about rent increases](https://www.sf.gov/learn-about-rent-increases-san-francisco) | The page restates the 1.6% period, license prerequisite, base-rent calculation, notice contents and 30-/90-day bands; it cautions that the 90-day band applies when an increase alone or combined in the relevant 12-month period is over 10%, and that mail adds five days. It also carries the November 9 notice about proposed legislation. |
| [SF Rent Board — Banked rent increases](https://www.sf.gov/information--banked-rent-increases) | The page says banking does not require per-increase Rent Board approval; calculations are additive, not compounded; it describes notice contents and 30-/90-day timing. Its November 9, 2026 notice states the proposed cap has not been enacted. |
| [California Civil Code §827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827) | Current statutory text supports personal or qualifying mail service and 30 days for increases no more than 10%, versus 90 days for increases over 10%, measured with other increases in the prior 12 months. |
| [California Civil Code §1947.12](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12) | The text states the statewide cap formula and excludes housing where valid local rent control restricts annual increases below that state cap. The dashboard does not substitute the state cap for the reported SF-controlled units. |
| [San Francisco Board of Supervisors File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770) | Live Legistar status remained **Pending Committee Action** on November 11, with no final action or enactment date. The proposal is not law. |
| [SF Rent Board Rules Part IV — §§4.10/4.12](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring) | The official text supports notice itemization and additive/noncompounding bank calculations. Its more specific annual-rule language is already distinguished from the public-facing banking summary in the canonical flag. |

## Privacy finding and change made

The public SF.gov Housing Inventory page expressly says **the information entered is public**. The official page lists potentially public owner/business-contact and unit information; §37.15 specifies reporting fields. The main site previously mentioned public information in a licensing Q&A, but did not foreground the disclosure before the reporting workflow. To avoid implying that this public website or the City portal keeps every submission confidential, the canonical landing page, licensing page, and executive summary now prominently warn owners before reporting, list the categories the official sources identify, and link directly to the official disclosure and ordinance. No tenant or owner identifier was added. The site continues to use placeholders for people and suppresses the street address and contact details.

This correction does **not** erase or remove earlier public Git history. The canonical Flagged for Review page already records that historical privacy issue. Current-file privacy tests pass, but a current-file scan cannot make old commits, branches, pull requests, caches, forks, or clones private; that flag remains open and is not represented as resolved.

## Current published answers checked

- A sole individual owner of covered tenant-occupied units is not exempt from Housing Inventory reporting or the Rent Increase License requirement merely because the owner is not incorporated. The hard requirement for ordinary annual/banked increases is a current license on the effective date. Completing reporting and checking the license before service is stated as the safer workflow, not misrepresented as the statutory cutoff.
- Ordinary annual/banked notices go to tenants and are not per-increase pre-approved by the Rent Board; other petition-based increase routes are distinct.
- The 1.6% figure is limited to increases effective March 1, 2026–February 28, 2027. The dollar amounts remain conditional arithmetic, not a certified rent or notice recommendation. Unit 1's lease/anniversary/ledger conditions and Unit 2's current base and history remain unresolved and flagged.
- No 94122-specific official market “normal” percentage or official SF comparison of individual- versus corporate-owner behavior is asserted. Unsupported figures remain blank/flagged.
- File #261020 remains a pending proposal, not current law. The dashboard does not apply it as enacted; the existing high-severity warning tells readers to recheck before serving any affected banked notice.

## Verification commands and results after the change

- `python3 hub/build.py` — regenerated 9 canonical HTML pages; conditional unit arithmetic reproduced: Unit 1 annual `$63.92`, annual-plus-bank illustration `$119.85`; Unit 2 annual `$50.40`, combined illustration `$412.65`.
- `python3 tools/verify_hub.py` — **1,599 checks, 0 errors**; 211 claim-table rows linked to sources or flags; 29 sources registered/cited; no pressured dollar figures.
- `python3 tools/verify_assurance.py` — **1,822 checks, 0 errors**; 37 assurance rows source-linked; 29/29 manifest entries; 214 current text files privacy-scanned.
- `python3 integration/verify.py` — pass; 6 pages and 57 source-linked rows.
- `python3 tools/check_links.py` — **781 checks, 0 errors**; published/internal/anchor/CSV/citation/privacy checks pass.
- `python3 tools/check_site.py` — pass; 42 official sources, 67 facts, 17 blank-verified case facts, 21 flags, 3 scenarios, 12 pages; linked rows and identifiers checked.
- `python3 dashboard/verify.py` — pass; 10 pages, 137 source-linked rows, 39 official `.gov` URLs, exact arithmetic and privacy checks.
- `python3 audit/verify_all.py` — pass; 11 pages, 14 registered source IDs, recomputed Unit 1 `$63.92`, Unit 2 `$50.40`, and conditional Unit 2 combined 13.1% / `$412.65`.
- `python3 review/verify.py` — pass.
- `python3 guide/verify.py` — **1,060 checks, 0 errors**.
- `python3 compliance/verify.py` — **3,277 checks, 0 errors**.
- `python3 -m compileall -q hub`, `git diff --check`, and explicit assertions for a visible Housing Inventory privacy warning plus official link on `index.html`, `hub/licensing.html`, and `EXECUTIVE_SUMMARY.md` — pass.

## Open irregularities that remain flagged

1. The current status of both private Rent Increase Licenses, actual property coverage, Unit 1 lease term/anniversary, Unit 2 current base and full rent ledgers cannot be confirmed from public sources; no value is inferred.
2. The public Git history privacy flag remains open; this change only keeps current publication anonymous and makes the City's separate public disclosure more explicit.
3. No official ZIP-specific market norm or owner-type behavior dataset is claimed.
4. File #261020 is pending and could change the treatment of banked/capital-improvement increases if enacted; re-check its official status and obtain advice before serving any affected notice.
5. The repository was not reviewed by a tenant lawyer, and no actual notice or attorney acceptance is claimed.
