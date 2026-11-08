# Independent current-state check — 8 November 2026

This is a targeted recheck, not a fresh line-by-line certification of all legacy editions. The prior final-integration record documents the line-by-line review and official retrieval dated 7 November 2026. The public canonical edition is the root and `hub/`; legacy editions are labeled superseded.

## Official source spot checks

| Topic | Check | Official source |
|---|---|---|
| Inventory and license | Individual owners report; reporting is free; a current license must be on file before an annual or banked increase goes into effect. The license need not be attached to the notice. | [Rent Board Housing Inventory](https://www.sf.gov/rent-board-housing-inventory) and [§37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) |
| Current allowance | 1.6% effective March 1, 2026 through February 28, 2027; previous year 1.4%. | [Current rates](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) |
| Banking and notices | Banked increases do not need prior Board approval; no compounding; ordinary notice periods and the mailing extension are explained by the Board. | [Banked rent increases](https://www.sf.gov/information--banked-rent-increases) and [rent increase guidance](https://www.sf.gov/learn-about-rent-increases-san-francisco) |
| State rent-cap distinction | The Board states that its current 8.8% state cap does not apply to units under SF rent-increase limitations. | [SF AB 1482 guidance](https://www.sf.gov/reports--california-tenant-protection-act-2019-ab-1482) |
| Repair petitions | A qualifying petition must be filed no later than 60 days after receipt of the increase notice, and an increase can be deferred if granted. | [Failure to Repair and Maintain petitions](https://www.sf.gov/information--failure-repair-and-maintain-petitions) |
| Historical privacy | An earlier public Git commit contains tenant initials. Current-file checks do not scan Git history. No identifiers or direct links to old blobs are reproduced here. Coordinated cleanup may affect other work and may not remove copies. | [GitHub sensitive-data removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository) |

## Test evidence and limits

- Canonical generator and assurance generator completed; `tools/verify_hub.py` passed 1,337 checks; `tools/verify_assurance.py` passed 1,560 checks. These validate current text, internal links/anchors, source references, dates, and arithmetic; they are not live verification of every external link.
- `tools/check_links.py`, `tools/check_site.py` (781 checks), `integration/verify.py`, `dashboard/verify.py`, `audit/verify_all.py`, and `review/verify.py` passed. The archived `review/build.py` uses the build date in generated footers and therefore changes that date on regeneration; those test-only changes were restored. The canonical and assurance generated outputs are reproducible.
- Live Pages at the root and the Pages API were checked before the new PR. The prior main deployment was successful. Deployment for this session will be recorded in the coordination log.
- Exact current license status, lease terms, ledgers, official coverage, and actual attorney review remain unknown. No private records were accessed. No legal clearance is claimed.
- No history rewrite, force-push of other branches, visibility change, or GitHub support request was performed. The platform confines work to this session's branch and a public-history cleanup requires coordination beyond a normal PR. See the privacy flag on the canonical Flagged for Review page.
