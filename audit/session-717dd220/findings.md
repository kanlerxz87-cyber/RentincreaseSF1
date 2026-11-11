# Session `arena-717dd220` — independent verification findings (2026-11-11 UTC)

**Scope:** `audit/session-717dd220/**` only. This session did **not** edit `index.html`, `hub/**`, `assurance/**`, the verifiers, or root Markdown — those are held by the live canonical integration. This file records an **independent** verification pass and a request log.

**Privacy:** placeholders only. No name, initial, street address, e-mail or telephone number from the owner's brief appears here. Dates and supplied dollar amounts are preserved as anonymized scenario inputs.

**Method:** each official page below was fetched and read live on 2026-11-11. Every scenario dollar figure and notice date was recomputed independently with `Decimal` arithmetic. Every local verification suite was run on the combined tree. The live GitHub Pages site was fetched to confirm it serves.

**State at time of writing:** `main` at `74ccba5` (PR #48 + #55 merged). Registry now **33 sources** — S30 (§13.14) and S31 (Noncompliance) added by PR #47; **S32 (42 U.S.C. §3604, govinfo.gov) and S33 (Notice of Owner Noncompliance) added by PR #48**. S34 (2024 RHFS) remains pending under PR #49 (`arena/c119d0f9`, open).

---

## 1. Live official-source re-verification (2026-11-11)

| # | Official source | URL | Result on 2026-11-11 |
| --- | --- | --- | --- |
| 1 | SF Administrative Code §37.15 — Reporting Obligations; Licensing (S01) | https://www.sf.gov/information/sec-3715-reporting-obligations-licensing | **Confirmed.** §37.15(a) requires owners of Chapter 37 units to report; §37.15(c) sets annual March 1 updates (buildings with fewer than 10 units from March 1, 2023); §37.15(e) grants the license on substantial compliance, suspends it during noncompliance, restores it prospectively, and states the tenant is not obligated for suspension months. **No individual-owner or two-unit exemption** appears in the text. Matches the canonical individual-owner answer. |
| 2 | SF Rent Board — Housing Inventory (S03) | https://www.sf.gov/rent-board-housing-inventory | **Confirmed.** "All owners of residential property are required to report"; reporting is free; tenant-occupied units receive a license after submission; "a landlord must have a current rent increase license on file … before any annual or banked rent increase can go into effect"; "the rent increase license does not need to be included with your rent increase notice"; deadline March 1 of every year; "your rent increase notice will not be enforceable without having a rent increase license on the effective date of the notice." Matches the landing-page answer. |
| 3 | SF Rent Board Rules and Regulations, Part XIII — §13.14 Licensing (S30) | https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-xiii-reporting-obligations-under-rent | **Confirmed.** "Any rent increase under Ordinance Sections 37.3(a)(1)-(2) purporting to be effective while the landlord is unlicensed shall render the entire rent increase null and void; provided, however, that the effective date of the rent increase, not the date of service, shall be used to determine whether or not the increase conforms"; "Nothing in this Regulation shall affect a landlord's banking rights"; applies to increases effective on/after July 1, 2022 (March 1, 2023 for buildings <10 units). |
| 4 | Notification of 2027 Rent Board Fee and Housing Inventory Requirements (S31) | https://www.sf.gov/notice-of-rent-board-fee-and-housing-inventory-requirement/ | **Confirmed.** 2027 fee exemption deadline Monday, December 14, 2026; Housing Inventory deadline March 1, 2027 and annually; "Requesting a Rent Board Fee exemption does not satisfy Rent Board Housing Inventory reporting requirements"; "Reporting into the Rent Board Housing Inventory does not satisfy requesting an exemption of the Rent Board Fee"; "Some rent increases given without a license will be null and void." |
| 5 | 42 U.S.C. §3604 — Fair Housing Act (S32, integrated in `main` by PR #48) | https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm | **Confirmed.** Primary federal statute text: §3604(b) prohibits discrimination in terms, conditions, or privileges of rental; §3604(c) prohibits discriminatory notices/statements/advertisements; protected classes race, color, religion, sex, familial status, national origin, handicap. Live govinfo.gov text (the uscode.house.gov link flagged in H-14 returns "Page Not Found"; this govinfo.gov URL is the correct official publisher). |
| 6 | Notice of Owner Noncompliance with Housing Inventory (S33, integrated in `main` by PR #48) | https://www.sf.gov/notice-of-owner-noncompliance-with-housing-inventory | **Confirmed.** Tenants can search the Rent Board Portal by address/APN for license status on the effective date; "A rent increase notice that goes into effect while the unit is unlicensed may be null and void"; tenants may file a Tenant Petition for Unlawful Rent Increase (after effective date) or a Tenant Summary Petition (before effective date). |
| 7 | 2024 Rental Housing Finance Survey (RHFS) release CB26-TPS.12 (S34, pending under PR #49) | https://www.census.gov/newsroom/press-releases/2026/2024-rhfs-data.html | **Confirmed.** Released February 19, 2026 by U.S. Census Bureau & HUD; tracks national property, mortgage, and ownership-entity characteristics of rental properties — **not** San Francisco 94122 rate-increase behavior. Correctly supports the H-11 statement that no official SF owner-type behavior dataset exists. |

**Conclusion on sources:** every load-bearing fact re-checked live on 2026-11-11 agrees with the canonical dashboard. No correction to any figure or proposition is required under this claim.

## 2. Independent arithmetic recompute (Decimal, 2026-11-11)

Additive method (add, never compound; no rounding up), recomputed from the published percentages:

| Scenario | Recompute | Result | Site figure | Agrees |
| --- | --- | ---: | ---: | --- |
| Unit 1 annual only | $3,995.00 × 1.6% | $63.92 → $4,058.92 | $63.92 → $4,058.92 | Yes |
| Unit 1 banked portion | $3,995.00 × 1.4% | $55.93 | $55.93 | Yes |
| Unit 1 combined 3.0% | $3,995.00 × 3.0% | $119.85 → $4,114.85 | $119.85 → $4,114.85 | Yes |
| Unit 2 annual only | $3,150.00 × 1.6% | $50.40 → $3,200.40 | $50.40 → $3,200.40 | Yes |
| Unit 2 banked 11.5% (1.8+0.7+2.3+3.6+1.7+1.4) | $3,150.00 × 11.5% | $362.25 (sum of components = direct) | $362.25 | Yes |
| Unit 2 combined 13.1% | $3,150.00 × 13.1% | $412.65 → $3,562.65 | $412.65 → $3,562.65 | Yes |
| Unit 1 30/35-day dates for Feb 1, 2027 | Feb 1, 2027 − 30/35 days | Jan 2, 2027 / Dec 28, 2026 | Jan 2, 2027 / Dec 28, 2026 | Yes |
| Unit 2 30/35-day dates for Feb 28, 2027 | Feb 28, 2027 − 30/35 days | Jan 29, 2027 / Jan 24, 2027 | Jan 29, 2027 / Jan 24, 2027 | Yes |
| Unit 2 90/95-day dates for Feb 28, 2027 (13.1%) | Feb 28, 2027 − 90/95 days | Nov 30, 2026 / Nov 25, 2026 | Nov 30, 2026 / Nov 25, 2026 | Yes |

All figures remain **conditional scenario arithmetic**, not certified lawful rents. Unit 1's April 2026 fixed-term/month-to-month status, Unit 2's current base rent, both ledgers, both licenses, and official coverage remain unresolved and flagged.

## 3. Local suite run (2026-11-11, combined tree = `main` at `74ccba5` + this session's records)

| Suite | Result |
| --- | --- |
| `tools/verify_hub.py` | 1,627 checks, 0 errors (211 source/flag-linked claim rows, 33 sources) |
| `tools/verify_assurance.py` | 1,902 checks, 0 errors (224 current text files privacy-scanned) |
| `tools/check_links.py` | OK — 10 published pages (+7 archived), all internal links/anchors resolve, CSVs consistent, external citations registered, no personal tokens |
| `tools/check_site.py` | 781 checks, 0 errors |

Every claim-table row on the canonical pages carries a direct official-source link or an explicit flag; unconfirmed values remain blank. No personal identifier was found in current text files by the privacy scans.

## 4. Live GitHub Pages confirmation (2026-11-11)

* Pages source: `main`, root `/`, legacy build type, status `built`, HTTPS enforced (latest build 2026-11-11T04:34:18Z).
* Landing page fetched: serves the individual-owner Rent Board answer, the 1.6% allowance KPI, both unit illustrations, and the File #261020 warning — all with official source links.
* `hub/sources.html` fetched: serves the **33 official source** registry (confirmed with a cache-busting parameter; a non-cache-busted fetch returns the prior CDN-cached 31-source build, a known artifact documented by `arena-992eb322`). Each row has a live official URL, verbatim quote, publisher, level, and retrieval date. No commercial source is used for a legal value.
* The two most load-bearing sources (§37.15, Housing Inventory) were re-fetched live today and confirm the canonical individual-owner answer.

## 5. Request log for the canonical holders

* **S32 (42 U.S.C. §3604) and S33 (Notice of Owner Noncompliance)** — already integrated into `main` by PR #48 (`arena/992eb322`, merged 2026-11-11T04:31:08Z). Verified live today; no action needed.
* **S34 (2024 RHFS)** — still pending under PR #49 (`arena/c119d0f9`, open, CONFLICTING). Verified live today; it supports the H-11 statement that no official SF owner-type behavior dataset exists. **Request to PR #49's owner:** carry S34 into the registry when the branch is rebased.
* The `uscode.house.gov/view.xhtml` string appears only inside flag **H-14's** documentation text (the historical broken-link record); the active federal-statute source is S32 at govinfo.gov. **No link-repair request is needed.**

**Requests:** one outstanding — S34 to be carried by PR #49. Everything else this session independently confirmed is already in `main`.

## 6. Irregularities and flags (none block publication)

1. **Pending File #261020** — still `Pending Committee Action` on 2026-11-11 (Legistar). Any banked notice served on or after September 15, 2026 falls inside the proposed retroactive window. Flag `H-22` stands; do not serve notice from the illustrations without re-checking the file and obtaining advice.
2. **Unresolved private facts** — Unit 1 lease status, Unit 2 current base, both ledgers, both licenses, official coverage, and the absence of an official 94122 "normal market increase" (H-10) or owner-type behavior dataset (H-11). All remain blank/flagged on `hub/flags.html`. No value was inferred.
3. **Historical privacy** — earlier public Git history may contain tenant initials; current-file scans do not remediate history. Already disclosed on the landing page and in the flags page. No new identifier was introduced by this session.
4. **Stale PRs #29 and #32** — already closed as superseded by `arena-e5dc4547` (E5-2) and `arena-3e212173` (F3). Re-confirmed: PR #32's §13.14 (S30) and Noncompliance/2027 (S31) content is in `main`; S32–S33 are in `main` (PR #48); S34 is pending under PR #49. Nothing further to carry from PR #32.

## 7. Answers to the owner's questions (summary; full text on the site)

* **Individual owner vs. corporation:** yes — an individual owner must report each tenant-occupied unit through the Housing Inventory and hold a current Rent Increase License on the effective date. §37.15 has no individual-owner or two-unit exemption; adopted Rule §13.14 sets the effective-date (not service-date) test. Ordinary annual/banked notices go to the tenant, not to the Board for approval.
* **Reasonable/normal increase:** the only official "normal" figure is the Rent Board annual allowance (1.6% for Mar 1, 2026 – Feb 28, 2027) plus any valid banked percentages, added without compounding. No official 94122 market-normal figure exists (H-10, blank and flagged).
* **How owners handle increases:** the same SF duties bind every owner. 42 U.S.C. §3604 (federal Fair Housing Act) and FEHA govern non-discrimination; no official SF owner-type behavior dataset exists (H-11, blank and flagged). The 2024 Census/HUD RHFS tracks national property structure only.
* **One unit or both:** different treatment is not automatically discrimination and identical treatment is not immunity; the neutral, documented, ledger-based selection process matters. No attorney verdict is promised.

*This file is research, not legal advice. Resolve all high-severity flags and review the actual lease, ledger, license record, and notice before serving. SF Rent Board counseling: 415-252-4600.*
