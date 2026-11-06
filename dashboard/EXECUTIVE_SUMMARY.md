# Executive summary — anonymized published version

Compiled 2026-11-06. No real tenant names, initials, addresses, or other personal identifiers are stored in this repository. Only placeholder labels (Unit A, Unit B, Tenant A1, etc.) and the user-supplied dates and amounts are used; those case facts are flagged unverified. Informational summary of official sources, not legal advice.

## Purpose

Collect, organize, and analyze a full list of requirements for two rent-controlled residential units in a San Francisco 94122-area building that the user says was built in 1940. Real tenant identifiers are not included in this public repository; placeholder labels are used.

## Case facts (user-supplied, unverified)

| Unit | Field | User-supplied value | Verified value |
|---|---|---|---|
| Both | Location / ZIP | San Francisco, Outer Sunset, ZIP 94122 | |
| Both | Building construction year | 1940 | |
| Both | Rent-control coverage of the specific building | User states units are rent controlled | |
| Both | Rent increase license status | Not supplied | |
| Unit A | Last lease start date | February 1, 2025 | |
| Unit A | Monthly rent at last lease start | $3,995 per month | |
| Unit A | Initial lease tenants | 3 placeholder tenants (Tenant A1, A2, A3) | |
| Unit A | Continuing tenancy date | April 1, 2026 | |
| Unit A | Continuing tenancy monthly rent | $3,995 per month | |
| Unit A | Current tenants | 2 placeholder tenants (Tenant A1, A4) | |
| Unit A | Roommate / 6.14 / Costa-Hawkins notice | Not supplied | |
| Unit B | Last lease start date | June 1, 2019 | |
| Unit B | Monthly rent at last lease start | $3,150 per month | |
| Unit B | Tenants | 2 placeholder tenants (Tenant B1, B2) | |
| Unit B | Rent increase history | No increase history supplied | |
| Both | Prior notices, petitions, or passthroughs | Not supplied | |
| Both | Subsidy / Section 8 / other exemption status | Not supplied | |

## Bottom line

- The ordinary lawful annual increase for a covered, licensed unit is **1.6% of base rent**, effective March 1, 2026 – February 28, 2027, once every 12 months, with 30 days' written notice (90 days above 10%; +5 days if mailed). Sources: [S01](https://www.sf.gov/learn-about-rent-increases-san-francisco), [S02](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit), [S29](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827), [S13](https://www.sf.gov/rent-board-housing-inventory).
- California's AB 1482 cap for the San Francisco area is 8.8% for August 1, 2026 – July 31, 2027, but official state and city guidance says the more protective local rule applies to units covered by the SF Rent Ordinance. Sources: [S27](https://www.sf.gov/reports--california-tenant-protection-act-2019-ab-1482), [S28](https://oag.ca.gov/rentcaps).
- No federal numeric rent-increase cap for private unsubsidized housing was confirmed from an official source; the value is blank and flagged. Sources: [S39](https://archives.hud.gov/local/nv/goodstories/2006-04-06glos.cfm), [S37](https://www.hud.gov/helping-americans/fair-housing-act-overview), [S38](https://www.ecfr.gov/current/title-24/part-100/section-100.500).
- Any increase can be challenged by a tenant before a Rent Board Administrative Law Judge at no charge with no time limit. Sources: [S18](https://www.sf.gov/report-unlawful-rent-increase-or-request-review-your-rent-history/), [S41](https://www.sf.gov/reports--rent-board-forms-forms-center/).
- No official source was found requiring both units to be raised or providing a discrimination safe harbor; a uniform, documented, objective policy is recommended for tenant-lawyer review. Sources: [S12](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring), [S37](https://www.hud.gov/helping-americans/fair-housing-act-overview), [S33](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=GOV&sectionNum=12955).

## Irregularities

21 items are published on the site's Flagged for Review page with official source links. They include unverified building coverage, Unit A's occupancy change and anniversary ambiguity, Unit B's missing rent history, missing license/notice information, conflicting secondary-source percentages, and the absence of a confirmed federal cap. Flagged items do not block the build or merge.

## Deliverables

- `dashboard/index.html` — landing dashboard
- `dashboard/pages/**` — subpages by category, all with source-linked tables
- `dashboard/data/site_data.json` — single verified data registry
- `dashboard/SOURCES.md`, `dashboard/RESEARCH.md` — line-by-line manual-review documents
- `dashboard/build.py`, `dashboard/verify.py` — generator and verification gate
