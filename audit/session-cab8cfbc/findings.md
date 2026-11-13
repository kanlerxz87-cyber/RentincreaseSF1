# Line-by-line repo review — `arena-cab8cfbc`, 2026-11-13 (UTC)

Scope: canonical edition (`index.html`, `hub/**`, `assurance/**`, `audit/final-integration/**`,
`tools/**`), root Markdown, and a structural review of the preserved editions
(`docs/**`, `site/**`, `portal/**`, `hub`, `review/**`, `integration/**`, `dashboard/**`,
`handbook/**`, `guide/**`, `compliance/**`, `assurance/**`, `archive/**`, `data/**`, `build/**`).
Method: every load-bearing legal claim was checked against the official publisher live on
2026-11-13 or against the per-source manifest of a recorded live read; every dollar figure was
recomputed independently with `Decimal` from the Form 571 table re-read live today.

## Verified live 2026-11-13 (fetch + read from the official publisher)

| Source | URL | What it confirmed |
|---|---|---|
| S01 §37.15 | https://www.sf.gov/information/sec-3715-reporting-obligations-licensing | Reporting duty; licence on substantial compliance; §37.15(c) March 1, 2023 phase-in for <10-unit buildings; "[Added by Ord. No. 265-20, effective January 18, 2021]" |
| S03 Housing Inventory | https://www.sf.gov/rent-board-housing-inventory | All owners must report; tenant-occupied report generates the licence; March 1 deadline; "Reporting requirements began March 1, 2023 for condominiums and units in buildings with fewer than 10 units" |
| S04 Banked increases | https://www.sf.gov/information--banked-rent-increases | 24-full-month banking test; no cap on banked amount; add-not-compound; Nov 9, 2026 File #261020 warning present |
| S05 Rent increases | https://www.sf.gov/learn-about-rent-increases-san-francisco | 1.6% effective 2026-03-01 – 2027-02-28; 60% of Bay Area CPI-U; 30/90-day notice, +5 days if mailed; licence precondition; 1–9-unit buildings from March 1, 2023 |
| S06 Form 571 | https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf | Full 1982–2027 rate table re-matched row by row against `hub/data.json` `rates` — all rows agree |
| S17 Rent Board Fee | https://www.sf.gov/rent-board-fee | $59.00/dwelling unit 2026-27; 50% recoverable from tenants in occupancy on Nov 1; Dec 14, 2026 exemption deadline |
| S26 File #261020 | https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770 | **Still Pending Committee Action** (Land Use and Transportation), no final action, no enactment date — not law |
| S30 Rule §13.14 | https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-xiii-reporting-obligations-under-rent | Effective-date (not service-date) test; unlicensed increase null and void without forfeiting banking; applies to small buildings only for increases effective on/after March 1, 2023 |
| S32 2027 notice | https://www.sf.gov/notice-of-rent-board-fee-and-housing-inventory-requirement | Dec 14, 2026 exemption window; Mar 1, 2027 report; "A new law requires all owners … [Ordinance No. 265-20]" |
| S34 RHFS (new) | https://www.census.gov/newsroom/press-releases/2026/2024-rhfs-data.html | National dataset only ("U.S. residential properties with at least one housing rental unit"); no SF/94122 figure — H-10/H-11 blanks are verified absences |

## Independent arithmetic re-check (Decimal, from Form 571)

| Scenario | Recomputed | Canonical | Match |
|---|---|---|---|
| U1 annual 1.6% of $3,995.00 | $63.92 → $4,058.92 | $63.92 → $4,058.92 | ✔ |
| U1 combined 3.0% (1.4+1.6) | $119.85 → $4,114.85 | $119.85 → $4,114.85 | ✔ |
| U2 annual 1.6% of $3,150.00 | $50.40 → $3,200.40 | $50.40 → $3,200.40 | ✔ |
| U2 banked 11.5% (1.8+0.7+2.3+3.6+1.7+1.4) | $362.25 | $362.25 | ✔ |
| U2 combined 13.1% | $412.65 → $3,562.65 | $412.65 → $3,562.65 | ✔ |

Banked components map to the Form 571 rows for anniversaries 2020-06-01 … 2025-06-01 exactly.

## Irregularities found in this review

| # | Finding | Severity | Disposition |
|---|---|---|---|
| IR-1 | `SOURCES.md` header claimed "All 29 registered sources live-verified 2026-11-10" while the registry held 33 with mixed per-source dates | medium | **Fixed** — header now states per-source dates 2026-11-07 → 2026-11-13 |
| IR-2 | `README.md` file-map row said "29-source live-retrieval manifest" (actual 33, now 34 rows) | low | **Fixed** |
| IR-3 | `EXECUTIVE_SUMMARY.md` said "14-point review"; `hub/data.json` holds 15 review rows and `index.html` says 15 (open request RA-FB3-02 from `arena-fb3db9a1`) | low | **Fixed** — 15-point, topics re-listed to match the rows |
| IR-4 | `VERIFICATION.md` gate table was stale (dated 2026-11-10, "29-row manifest", "170 files") while later addenda recorded 31/33-row manifests | low | **Fixed** — refreshed to the 2026-11-13 measured values |
| IR-5 | `hub/build.py` blanket wording "All N registered official sources were fetched and read on {retrieved}" overstated mixed per-source dates | medium | **Fixed** — wording now points at the per-source dates; only the load-bearing subset is claimed re-read on the registry date |
| IR-6 | S34 (2024 RHFS) sat unmerged under PR #49 (OPEN + CONFLICTING since 2026-11-11 04:21 UTC, no commits) — the only outstanding source-integration request | medium | **Taken over per the 60-minute rule**; S34 integrated and verified live; PR #49 closed with a takeover note |
| IR-7 | File #261020 is time-sensitive (would cap banked + capital-improvement increases at 10%/yr; Unit 2's conditional 13.1% exceeds it) | high (external) | **Re-verified live 2026-11-13: still Pending Committee Action — not law.** H-22 and all generated warnings updated with the re-check date. Re-check again before serving any banked notice |
| IR-8 | Historical privacy: pre-redaction blobs (tenant initials from the owner's brief) remain in public Git history below PR #10 | high (privacy) | **Cannot be fixed by any session** — requires a repo-admin history rewrite. Flagged on the site's Flagged for Review page with GitHub's official cleanup guidance; no identifier reproduced |
| IR-9 | No official source publishes a "reasonable/normal" 94122 market increase, or corporate-vs-individual owner behaviour data | medium | **Left blank and flagged (H-10, H-11)** — S34 now documents that the federal dataset was checked and is national only. Not filled in by inference |

## Items that remain open (do not block merge; published on Flagged for Review)

- H-17: Unit 1 fixed-term vs month-to-month instrument (owner-supplied fact).
- H-18 / H-03: Unit 2 current base rent and full increase history ($3,150 is the June 2019 figure).
- H-02: Unit 1 anniversary / prior-increase history (banked 1.4% scenario is conditional).
- H-04: Current rent-increase licence status for each unit (private fact; check portal.sfrb.org).
- H-05: Official coverage/exemption review against the parcel record.
- H-21: Business Registration Certificate determination is conditional on owner-supplied facts.
- H-22: Pending File #261020 — re-check before serving any banked increase.
- H-10 / H-11: verified blank — no official 94122 market figure; no owner-behaviour dataset.

## Privacy

No name, initial, street address, e-mail or telephone number from the owner's brief appears in any
file written by this session. Placeholder tenant labels only; supplied dates and dollar amounts
unchanged. `tools/verify_assurance.py` privacy scan: 246 current text files, no forbidden token.

## Suites (2026-11-13, this tree)

`tools/verify_hub.py` 1,633/0 · `tools/verify_assurance.py` 1,916/0 · `tools/check_links.py` OK ·
`tools/check_site.py` 781/0 · `handbook/verify.py` 2,112/0 · `integration/verify.py` PASS (57 rows) ·
`audit/verify_all.py` PASS (137 rows) · `dashboard/verify.py` OK · `review/verify.py` PASS.
