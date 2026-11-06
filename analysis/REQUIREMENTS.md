# Project requirements and acceptance checklist

This checklist preserves the requested scope in privacy-safe form. Official links identify the verification standard; they do not authenticate user-reported lease facts.

## Required deliverables

- [x] Review the existing repository before implementation; record the initial one-file state and coordination claims in `COORDINATION.md`.
- [x] Research local, state, and federal rent-increase, notice, nondiscrimination, retaliation, ownership-form, and pricing-tool rules using official sources. [SF § 37.3](https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-70881); [Civil Code § 1947.12](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12.); [HUD fair housing](https://www.hud.gov/stat/fheo/rights-obligations).
- [x] Separate verified rules/benchmarks from reported private facts, conditional calculations, and unknowns. [SF coverage guidance](https://www.sf.gov/learn-about-san-francisco-rental-laws); [tenant rent-history review](https://www.sf.gov/report-unlawful-rent-increase-or-request-review-your-rent-history).
- [x] Preserve reported dates and amounts while replacing identifying resident information with neutral aliases in public output. [SF tenant petition evidence guidance](https://www.sf.gov/report-unlawful-rent-increase-or-request-review-your-rent-history).
- [x] Keep raw private intake local-only and gitignored in this public repository; never place identifiers in tracked files or history. [SF coverage/records guidance](https://www.sf.gov/learn-about-san-francisco-rental-laws).
- [x] Explain ordinary annual increases, banking, exceptional petition/passthrough routes, and why market rent is not a stand-alone authorization. [SF § 37.3](https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-70881); [Topic 323](https://www.sf.gov/information/topic-no-323-special-circumstances-petitions-based-rents-comparable-units).
- [x] Explain corporate versus individual ownership without inventing a normal-practice percentage or stereotyping either group. [Civil Code § 1947.12(d)](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12.).
- [x] Analyze one-unit versus two-unit selection, protected characteristics, consistent reasons, and retaliation. [California Civil Rights Department](https://calcivilrights.ca.gov/housing/); [Civil Code § 1942.5](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1942.5.).
- [x] Provide proper-notice and service analysis, including the 30/90-day thresholds and mailing extensions. [Civil Code § 827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827.); [CCP § 1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CCP&sectionNum=1013.).
- [x] Include official market context with exact geography/year labels; leave unverified ZIP/current-unit matches blank. [HUD FY 2027 metropolitan summary](https://www.huduser.gov/datasets/fmr/fmr2027/summary?year=2027&reporttype=hmfa&hmfa=METRO41860MM7360); [HUD methodology](https://www.govinfo.gov/link/cfr/24/888?link-type=pdf&sectionnum=113&year=mostrecent).
- [x] Build an executive summary, categorized tables, source register, analysis, and a clearly labeled Flagged for Review section. [SF Rent Ordinance index](https://www.sf.gov/reports--rent-ordinance).
- [x] Give every substantive public table row an official-source link; a private-fact row explicitly distinguishes the review rule from the unverified fact. [SF § 37.3](https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-70881).
- [x] Provide a conditional ordinary-increase calculator that excludes banking/petitions/passthroughs and does not persist inputs. [SF rate announcement](https://www.sf.gov/news--annual-rent-increase-3126-22827-announced); [Rule 4.12](https://www.sf.gov/reports/february-2024/rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring).
- [x] Prepare a tenant-advocate/lawyer challenge packet and official referrals without claiming actual review or endorsement. [SF referral directory](https://www.sf.gov/information/rent-board-referral-listing).
- [ ] Final integration: generate shared navigation/index/data only after R1/R2/S1 completion; run privacy, source, calculation, link, and browser checks. [SF publication/verification context](https://www.sf.gov/reports--rent-ordinance).
- [ ] Open a PR from the fixed Arena branch to `main`, merge without waiting for approval, and confirm the public GitHub Pages deployment. [Official SF source publication model](https://www.sf.gov/reports--rent-ordinance).

## Non-negotiable evidence boundaries

1. No inferred address, APN, current rent, bedroom count, owner form, subsidy status, exemption, banking amount, or protected characteristic. [SF coverage](https://www.sf.gov/learn-about-san-francisco-rental-laws); [Civil Code § 1947.12](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=1947.12.).
2. Unknown values are `null` in data and blank plus **Flagged for Review** in the interface. [SF Housing Inventory](https://www.sf.gov/rent-board-housing-inventory).
3. Agency summaries do not override primary statutes/rules; disclose the banking wording discrepancy. [Rule 4.12](https://www.sf.gov/reports/february-2024/rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring); [banking summary](https://www.sf.gov/information--banked-rent-increases).
4. DOJ enforcement context is not evidence about this owner, and a proposed decree is not a final liability finding. [DOJ announcement](https://www.justice.gov/opa/pr/justice-department-reaches-proposed-consent-decree-pinnacle-one-americas-largest-landlords).
5. Publish unresolved flags with sources; do not delay publication for facts that cannot be verified autonomously, and do not convert them into assumptions. [SF tenant review route](https://www.sf.gov/report-unlawful-rent-increase-or-request-review-your-rent-history).

## Coordination and hosting

The repository was initially only a README. Work is divided into R1 research, R2 case analysis, S1 site/tests, and I1 final integration, with claims and commits recorded in `COORDINATION.md`. Arena fixes the branch to `arena/832c7b0c-rentincreasesf1`; this overrides requested alternative session/integration branch names. Shared outputs are reserved for final integration. The public site must remain usable without a backend, external fonts, analytics, or private data.
