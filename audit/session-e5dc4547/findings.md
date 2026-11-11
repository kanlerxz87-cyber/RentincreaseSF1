# Session `arena-e5dc4547` — 2026-11-11 verification findings

**Branch:** `arena/e5dc4547-rentincreasesf1` · **Base:** `main` @ `3885c6b` (PR #42)
**Privacy:** placeholders only; dates and dollar amounts unchanged; no personal identifier from the
owner's brief appears in this file.

## E5-1 — Fresh 2026-11-11 live re-verification (13 load-bearing sources)

Each source below was fetched and read live from its official publisher on 2026-11-11. "Matches"
means the published claim was confirmed against the official text; no figure, date, or conclusion
changed.

| ID | Official source | Claim checked | Outcome |
| --- | --- | --- | --- |
| S01 | [§37.15 Reporting Obligations; Licensing](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) | Duty attaches to "owners of residential dwelling units subject to this Chapter 37" (no individual/small-owner exemption); licence suspended during non-compliance, restored prospectively, tenant not obligated for suspension months | Matches |
| S03 | [Rent Board Housing Inventory](https://www.sf.gov/rent-board-housing-inventory) | "All owners of residential property are required to report"; reporting free; licence automatically generated for tenant-occupied units; "notice will not be enforceable without having a rent increase license on the effective date"; licence need not be attached to notice; March 1 deadline, late submission allowed | Matches |
| S06 | [Form 571 (PDF)](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) | 1.6% for 3/1/26–2/28/27; full 1982–2027 table incl. 1.4%, 1.7%, 3.6%, 2.3%, 0.7%, 1.8% used in Unit 1/Unit 2 scenarios | Matches |
| S02 | [§37.3 Rent Limitations](https://www.sf.gov/information--sec-373-rent-limitations) | Annual = 60% of CPI, max 7%; licence condition via §37.15; banking (a)(2) | Matches |
| S04 | [Banked rent increases](https://www.sf.gov/information--banked-rent-increases) | 24-month no-increase statement; no Board approval; no compounding/proration; 30/90-day +5 mail; notice contents; Nov 9, 2026 File #261020 warning (notices on/after Sept 15, 2026) | Matches |
| S05 | [Learn about rent increases](https://www.sf.gov/learn-about-rent-increases-san-francisco) | 1.6%; licence required; base-rent-only; no rounding up; 12-month timing; 30/90 +5; additional-occupant prohibition; Nov 9, 2026 warning. Worked-example year labels still inconsistent with Form 571 (H-19 stands) | Matches |
| S07 | [Rules Part IV §§4.10/4.12](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring) | Rule 4.12(a): 12 months from when skipped allowance could have been imposed; no compounding/rounding; Rule 4.12(b): omission of banked dates does not itself void; Rule 4.10(b) 0.5% exception | Matches |
| S08 | [Civil Code §827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827&lawCode=CIV) | 30 days at ≤10%, 90 days above 10% (12-month look-back); mail via CCP §1013 | Matches |
| S10 | [AB 1482 guidance](https://www.sf.gov/reports--california-tenant-protection-act-2019-ab-1482) | 8.8% Aug 1, 2026–Jul 31, 2027; "does NOT apply for units under the rent increase limitations of the San Francisco Rent Ordinance" | Matches |
| S17 | [Rent Board Fee](https://www.sf.gov/rent-board-fee) | $59.00/dwelling unit; $29.50 (50%) recoverable if in occupancy Nov 1; March 1 deadline; Dec 14, 2026 exemption deadline for 2027 fee; fee exemption ≠ Housing Inventory reporting | Matches |
| S24 | [Treasurer lessor guidance](https://sftreasurer.org/information-lessors-residential-real-estate) | "One residential structure consisting of fewer than four units … not, by reason of that fact alone, required to obtain a business registration certificate"; other activity/payroll/short-term rental can trigger it (H-21 conditional) | Matches |
| S26 | [File #261020 (Legistar)](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770) | Status `Pending Committee Action`; Final action blank; Enactment date blank; introduced 9/15/2026 | Matches — still not law |
| S27 | [§6.14 and Costa-Hawkins](https://www.sf.gov/information--rent-increases-under-section-614-and-costa-hawkins) | §6.14 keyed to last original occupant "vacates" (60-day reasonableness); Costa-Hawkins keyed to no longer "permanently resides"; co-tenant outside Costa-Hawkins; no pre-filing required | Matches |

### Independent arithmetic recomputation (no repo helpers)

| Scenario | Result | Published? |
| --- | --- | --- |
| Unit 1 annual 1.6% × $3,995.00 | $63.92 → $4,058.92 | Yes |
| Unit 1 banked 1.4% | $55.93; combined 3.0% $119.85 → $4,114.85 | Yes |
| Unit 2 banked 1.8+0.7+2.3+3.6+1.7+1.4 | 11.5% = $362.25 | Yes |
| Unit 2 annual 1.6% × $3,150.00 | $50.40 → $3,200.40 | Yes |
| Unit 2 combined 13.1% | $412.65 → $3,562.65 | Yes |
| Service dates (2027-02-01 −30/−35; 2027-02-28 −30/−35/−90/−95) | 2027-01-02, 2026-12-28, 2027-01-29, 2027-01-24, 2026-11-30, 2026-11-25 | Yes |

### Suites re-run (2026-11-11, combined tree)

| Suite | Result |
| --- | --- |
| `hub/build.py` + `assurance/build.py` | 9 pages + 31 manifest rows; reproducible |
| `tools/verify_hub.py` | **1,611 checks, 0 errors**; 31/31 cited; 211 claim rows |
| `tools/verify_assurance.py` | **1,852 checks, 0 errors**; 31/31 manifest; 214 files privacy-scanned |
| `tools/check_links.py`, `build/build.py`+`check_site.py` (781), `integration/verify.py` (57), `dashboard/verify.py`, `audit/verify_all.py` (137), `review/verify.py` | All pass. `review/build.py` footer-date artifact reverted, as before |

## E5-2 — Triage of stale PRs #29 and #32

| PR | Content | Decision |
| --- | --- | --- |
| #29 (`arena/68f1fe88`) | COORDINATION.md only: T1–T5 status flips + completion record. Outcomes already on `main` via PR #27/#30 (VERIFICATION.md records the re-verification; Pages `built`). CONFLICTING. | **Close as superseded.** Nothing missing from `main`. |
| #32 (`arena/4700b525`) | Canonical files: 5 new sources (S30 §13.14, S31 2027 Notice, S32 42 U.S.C. §3604, S33 Noncompliance Notice, S34 Census/HUD RHFS), template/count fixes, §1942.5 URL fix. CONFLICTING (based on pre-PR #38–#42 `main`). | **Close as superseded; port the genuinely missing findings** (E5-3a). Direct merge would regress canonical files. |

### Ported (E5-3a) — live-verified 2026-11-11

- **S30 Rule §13.14** ([Rules Part XIII](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-xiii-reporting-obligations-under-rent)): effective date (not service date) governs; unlicensed increase null and void but "Nothing in this Regulation shall affect a landlord's banking rights or the ability to accumulate otherwise lawful rent increases that were found to be null and void." Cited in licensing steps 4–5.
- **S31 Notice of Owner Noncompliance** ([SF.gov](https://www.sf.gov/notice-of-owner-noncompliance-with-housing-inventory)): Portal APN/address licence lookup; Tenant Petition for Unlawful Rent Increase (after effective date) vs. Tenant Summary Petition (before); rent-refund exposure. Cited in licensing step 7.
- **§1942.5 URL typo** (`sectionNum=1942.5.` → `sectionNum=1942.5`) fixed in `EXECUTIVE_SUMMARY.md` and `VERIFICATION.md` (leginfo resolves both identically; canonical form restored).
- **Stale `14-point` review count** corrected to 15 in `EXECUTIVE_SUMMARY.md` and `README.md` (15 rows in `hub/data.json`).

### Deliberately not ported

- **S31 (PR #32 numbering) 2027 Informational Notice:** redundant — December 14, 2026 deadline and fee-exemption ≠ reporting already on `main` via S17/S03.
- **S32 42 U.S.C. §3604 registry entry:** URL already cited in `EXECUTIVE_SUMMARY.md` §7; HUD S14 covers the federal layer. Registry addition deferred (not fetched this session).
- **S34 Census/HUD RHFS:** national ownership-structure data; does not answer the SF 94122 behaviour question. Flag H-11 blank stands.

## Irregularities

- None new. All 24 flags remain open and published on the Flagged for Review page. No scenario is
  certified notice-ready. The pre-existing Git-history privacy flag (tenant initials in earlier
  history) remains open; current-file scans (214 files) show no personal tokens.
