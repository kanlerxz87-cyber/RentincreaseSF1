# Final integration verification record

**Verification date:** 2026-11-10 (original final audit 2026-11-07; full live re-verification 2026-11-10)
**Canonical edition:** root `index.html` + `hub/`
**Independent assurance:** `assurance/` + `audit/final-integration/`
**Branch:** `arena/4700b525-rentincreasesf1` (following merged PR #15 / `3fbd5e1` through PR #20)

## Scope and evidentiary standard

The final audit read the canonical data and generated prose, re-fetched official material, corrected overstatements in the existing generator, regenerated the site, and independently recomputed every scenario and service date. On 2026-11-10, all 29 prior official sources plus 5 additional official `.gov` sources were re-fetched live, template/count defects were fixed, and the November 9, 2026 Rent Board File #261020 alert (`September 15, 2026` retroactive notice trigger), adopted Rule §13.14, and the December 14, 2026 2027 Rent Board Fee exemption cutoff were incorporated. Earlier editions remain preserved as superseded archives; this record does not claim that every historical sentence was re-certified.

Evidence classes are kept separate:

1. **Official rule/rate:** directly supported by one of the 34 registered official sources.
2. **Owner-brief input:** a date or amount supplied for the two units, not an official record.
3. **Conditional arithmetic:** reproducible calculation on an owner-brief input and an official percentage.
4. **Official confirmation:** private license, parcel, lease, or ledger evidence that was unavailable; the public cell is blank and flagged.

No personal identity is used in the current site or verification data.

## Official-source verification

All **34/34** registered sources were live-fetched and verified from their official publishers on **2026-11-10** (S01–S34). Each source carries its retrieval date in `hub/data.json` and in the manifest, so a newly added source cannot inherit a stale blanket date. The registry is [`hub/data.json`](hub/data.json), the compact index is [`SOURCES.md`](SOURCES.md), and the machine-readable retrieval manifest is [`audit/final-integration/source-manifest.json`](audit/final-integration/source-manifest.json).

Notable checks:

- Individual-owner reporting and effective-date license gate (plus preserved banking rights): [§37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) + [Rule §13.14](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-xiii-reporting-obligations-under-rent) + [Housing Inventory](https://www.sf.gov/rent-board-housing-inventory) + [Noncompliance Notice](https://www.sf.gov/notice-of-owner-noncompliance-with-housing-inventory).
- 2027 Rent Board Fee exemption cutoff (`December 14, 2026`) and `March 1, 2027` Housing Inventory deadline: [Rent Board Fee](https://www.sf.gov/rent-board-fee) + [2027 Informational Notice](https://www.sf.gov/notice-of-rent-board-fee-and-housing-inventory-requirement/).
- Pending File #261020 (`Pending Committee Action`, not law) and November 9, 2026 Rent Board warning regarding the September 15, 2026 retroactive notice trigger in `Leg Ver1` / `Leg Dig Ver1`: [Legistar File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770) + [Banked rent increases](https://www.sf.gov/information--banked-rent-increases).
- Current 1.6% rate and all historical rates: [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf).
- Banking and notice text, including Rule 4.12(b)’s express non-void provision: [Rules Part IV](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring).
- Fixed-term limitation: [California Tenants guide](https://www4.courts.ca.gov/documents/California-Tenants-Guide.pdf).
- Personal/mail notice and extensions: [Civil Code §827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827&lawCode=CIV) + [CCP §1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013&lawCode=CCP).
- Retaliation conditions and lawful-cause provisions: [Civil Code §1942.5](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1942.5&lawCode=CIV).
- Fair Housing Act federal statute and HUD guidance: [42 U.S.C. §3604 (U.S. GPO)](https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm) + [HUD overview](https://www.hud.gov/helping-americans/fair-housing-act-overview).
- Corporate-practice example and national ownership dataset: [DOJ RealPage announcement](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and) + [2024 Census/HUD RHFS (CB26-TPS.12)](https://www.census.gov/newsroom/press-releases/2026/2024-rhfs-data.html).

Official Rent Board worked-example year-label errors were not copied. Form 571 controls every rate period; the discrepancies are public as H-19.

## Arithmetic independently recomputed

| Scenario | Formula | Increase | Illustrative new rent | Official rate source |
|---|---|---:|---:|---|
| Unit 1 annual-only | $3,995.00 × 1.6% | $63.92 | $4,058.92 | [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) |
| Unit 1 combined | $3,995.00 × (1.4% + 1.6%) | $119.85 | $4,114.85 | [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) + [Rule 4.12](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring) |
| Unit 2 annual-only | $3,150.00 × 1.6% | $50.40 | $3,200.40 | [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) |
| Unit 2 combined | $3,150.00 × (1.8% + 0.7% + 2.3% + 3.6% + 1.7% + 1.4% + 1.6%) | $412.65 | $3,562.65 | [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) + [Rule 4.12](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring) |

Percentages are added, not compounded, and not rounded up. Unit 2 has six **potentially banked** components plus current annual 1.6%, not seven banked increases. The Unit 2 input is only the supplied 2019 lease-start rent; current base and no-prior-increase history are not verified.

Service-date subtraction was independently checked:

| Scenario | Effective date | Personal service | California mail | Official basis |
|---|---|---|---|---|
| Unit 1 annual or combined | 2027-02-01 | 2027-01-02 (30 days) | 2026-12-28 (35 days) | [§827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827&lawCode=CIV) + [CCP §1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013&lawCode=CCP) |
| Unit 2 annual-only | 2027-02-28 | 2027-01-29 (30 days) | 2027-01-24 (35 days) | Same statutes |
| Unit 2 combined | 2027-02-28 | 2026-11-30 (90 days) | 2026-11-25 (95 days) | Same statutes |

These are scenario calculations, not universal last-safe dates or legal clearance.

## Automated and local gates

Canonical and assurance gates were run with `PYTHONDONTWRITEBYTECODE=1`:

| Check | Result at verification |
|---|---|
| `python3 hub/build.py` | Root and eight hub pages regenerated |
| `python3 assurance/build.py` | Assurance page and 34-row source manifest regenerated |
| `python3 tools/verify_hub.py` | **1,700 checks; 0 errors**; 210 claim-table rows with source/flag links |
| `python3 tools/verify_assurance.py` | **1,961 checks; 0 errors**; 35 assurance rows with official sources |
| Current-text privacy scan | **170 files; no forbidden personal token** |
| `git diff --check` | No whitespace errors |

The canonical verifier checks internal links/anchors, navigation, source registry completeness and use, every claim-table row’s source/flag citation, official dollar/rate traceability, service dates, placeholders, corrected categorical-label regressions, required flags, and explicit official-confirmation blanks.

The independent verifier additionally checks all canonical and assurance links, assurance-row sources, official-host allowlisting, manifest agreement, private-input caveats, conditional Unit 2 components, stale-overstatement absence, required blank cells, and current-text privacy across the repository.

CI reproduces both builds and fails on stale output through [`.github/workflows/assurance.yml`](.github/workflows/assurance.yml).

## Preserved legacy suites

The following existing checks are retained and run during integration:

```bash
python3 tools/check_links.py
python3 build/build.py && python3 tools/check_site.py
python3 integration/verify.py
python3 dashboard/verify.py
python3 audit/verify_all.py
python3 review/build.py && python3 review/verify.py
```

Passing an archived edition’s own suite does not mean every archived legal statement was accepted into the canonical edition. Corrections and their official bases are enumerated in [`audit/final-integration/findings.json`](audit/final-integration/findings.json).

## Corrections made by the final audit and 2026-11-10 update

The 13-row public correction register is rendered at [`assurance/index.html`](assurance/index.html). It covers:

- effective-date versus notice-date license timing (Rule §13.14 and preserved banking rights);
- Unit 2 lease-start versus current-base labeling;
- Unit 1 fixed-term contingency;
- reconciliation of banking measuring points;
- Rule 4.10/4.12 notice exceptions;
- fact-specific retaliation and repair analysis;
- limits of free-representation claims;
- fair-housing neutrality without safe-harbour claims;
- accurately bounded corporate-practice evidence (DOJ + 2024 Census/HUD RHFS);
- official worked-example year errors;
- separation of Rent Board Fee recovery (`December 14, 2026` exemption cutoff) from license/base rent;
- blank market-normal and owner-behavior values;
- `2026-11-10` live re-verification, File #261020 September 15, 2026 retroactive notice trigger warning, template `{n}` placeholder repair, and stale count/date/URL fixes (`A-13`).

## Remaining limitations

The canonical [Flagged for Review](hub/flags.html) contains 24 items. High-severity unknowns include Unit 1 lease status (H-17), Unit 2 current base/history (H-18/H-03), Unit 1 anniversary/history (H-02), both licenses (H-04), and official coverage (H-05). Repair and protected-activity history also remains open (H-09).

**No scenario is certified as notice-ready. No lawful current maximum or attorney/advocate acceptance is asserted.**

## Pull request and deployment result

- [PR #15](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/15) merged at `2026-11-07T21:32:24Z` as `3fbd5e195330babacbd5e1568e287171ee4f8e93` after all three PR workflows passed.
- Post-merge `Verify site` run `42416341845`, `Verify published site` run `42416341852`, and `Final assurance` run `42416341861` all succeeded.
- GitHub Pages build/deployment run `42416341186` succeeded; the Pages API reported `built` for `main` `/`.
- The deployed root, `assurance/index.html`, and `hub/flags.html` were retrieved after deployment and confirmed to contain the corrected license answer, 12 corrections, 29 official sources, and 24 flags.

---

# Dated re-verification — 2026-11-10

**Session:** `arena/68f1fe88-rentincreasesf1` · **Base:** `main` @ `7eb20dc` · **Result: no claim, figure,
date or rate changed.**

This pass re-opened every load-bearing official source against the text the site publishes, instead of
trusting the earlier sessions' notes. Sixteen sources were re-fetched and read in full on **2026-11-10**:
S01, S02, S03, S04, S05, S06, S07, S08, S10, S16, S17, S18, S19, S24, S26, S27. Ten sources stand at
their 2026-11-07 retrieval date and three at 2026-11-08; their published passages were left unchanged
because they were not re-opened in this pass. Every source keeps its own retrieval date.

## What was checked, and the outcome

| Claim as published | Official text re-read | Outcome |
|---|---|---|
| 1.6% for increases effective 1 Mar 2026 – 28 Feb 2027 | Form 571, and the learn-about-rent-increases page | Matches |
| Complete 1982–2027 rate table (46 rows) | Form 571 full table, read row by row | Every row matches |
| No individual-owner or small-building exemption from reporting/licence | §37.15 (a)–(e) | Matches: duty attaches to "owners"; licence suspended during non-compliance and restored prospectively |
| Licence is automatic after reporting, free, and need not be attached to the notice | Housing Inventory page + licence FAQ | Matches |
| Hard gate is a current licence on the **effective date**, not the notice date | Housing Inventory "Deadline" block | Matches |
| One increase per 12 months; 30-day notice at ≤10%, 90 days above 10%; +5 days if mailed | §37.3(a), Civil Code §827(b)(2)–(3), CCP §1013 | Matches |
| Notice must state dollar amount, percentage, effective date, and which part is banked | Learn-about page, banked page, §4.10(a), §4.12(b) | Matches |
| Banked amounts are added, never compounded, never rounded up, and need no Board approval | Banked page + §4.12(a) | Matches |
| No surcharge merely because an additional occupant moved in | Learn-about page "Additional occupants" | Matches |
| AB 1482 is 8.8% for SF (1 Aug 2026 – 31 Jul 2027) and does **not** apply to units under the local cap | AB 1482 page | Matches exactly |
| Rent Board Fee is $59.00 per dwelling unit, $29.50 recoverable, due 1 March | Rent Board Fee page | Matches |
| Coverage date test is units built on or before 13 June 1979 | Learn about SF rental laws | Matches |
| Algorithmic-device ban binds "a landlord" and needs no corporate form | §37.10C (a)–(d) | Matches |
| Business Registration Certificate: sub-four-unit carve-out is conditional | Treasurer lessor guidance | Matches: "by reason of that fact alone", other activity may trigger registration |
| File #261020 is pending, not law, no enactment date | Legistar record | Matches: Status "Pending Committee Action", Final action blank, Enactment date blank |
| Discriminatory rent increase is bad-faith harassment | §37.10B(a)(9) | Matches |
| Certified O&M increase capped at 7% above the annual allowance | §6.10(d) | Matches |
| §6.14 notice served on later occupants within a reasonable time (~60 days); co-tenants are outside Costa-Hawkins | §6.14 / Costa-Hawkins page | Matches |
| Free legal help is a referral list, not guaranteed representation | Rent Board Referral Listing | Matches: "The Rent Board cannot refer you to individual attorneys"; Sunset office listed |

## Arithmetic re-derived independently

Recomputed from the transcribed Form 571 table with cent truncation (never rounding up), not with the
repository's own helper:

| Scenario | Result | Reproduces published? |
|---|---|---|
| Unit 1 annual, 1.6% × $3,995.00 | $63.92 → $4,058.92 | Yes |
| Unit 1 skipped 1.4% (available 2026-02-01) | $55.93 | Yes |
| Unit 1 combined 3.0% | $119.85 → $4,114.85 | Yes |
| Unit 2 six skipped components 1.8+0.7+2.3+3.6+1.7+1.4 | 11.5% = $362.25 | Yes |
| Unit 2 annual 1.6% | $50.40 → $3,200.40 | Yes |
| Unit 2 combined 13.1% | $412.65 → $3,562.65 | Yes |
| Unit 2 2026-06-01 allowance vs 2027-02-28 effective date | 272 days elapsed — **not** banked, lost | Yes, matches the flag |
| Notice dates: 2027-02-01 − 30/−35 days; 2027-02-28 − 90/−95 days | 2027-01-02, 2026-12-28, 2026-11-30, 2026-11-25 | Yes |

## Privacy

Published files contain no tenant names, initials, street address, or contact details; placeholders are
used and the supplied dates and dollar amounts are unchanged. Re-scanned all current text files
(170 files) plus a targeted search for the supplied initials and for any street-address pattern: no hits.
The pre-existing flag about tenant initials in earlier **Git history** remains open and is not fixed by a
current-file scan; the human-readable repository now contains nine commits, none of which adds such text.

## Gates re-run on the combined tree (2026-11-10)

| Suite | Result |
|---|---|
| `hub/build.py` | 9 pages; arithmetic unchanged |
| `assurance/build.py` | `assurance/index.html` + 29 manifest rows |
| `tools/verify_hub.py` | **1,551 checks, 0 errors**; 210 cited rows; 29/29 sources cited |
| `tools/verify_assurance.py` | **1,748 checks, 0 errors**; 29/29 manifest; 170 files privacy-scanned |
| `tools/check_links.py` | OK — 10 published + 7 archived pages, no personal tokens |
| `build/build.py` + `tools/check_site.py` | 781 checks, 0 errors |
| `integration/verify.py` | PASS, 57 source-linked rows |
| `dashboard/verify.py` | OK |
| `audit/verify_all.py` | VERIFICATION PASSED, 137 rows |
| `review/build.py` + `review/verify.py` | PASSED (regenerated footer date reverted, as before) |

## Flagged for review — nothing new, nothing closed

All 24 existing flags remain open and are published on the Flagged for Review page. This pass added no
new irregularity and closed none. The one item refreshed is `H-22`: the Rent Board's **9 November 2026**
notice states that, if File #261020 is enacted as currently proposed, it would apply to banked increases
noticed on or after **15 September 2026** — a date already past. The ordinance is still not law, no
figure changes, and the flag now says plainly that a notice served today could be affected if the
proposal becomes law as described. Unverified official-confirmation cells (licence status, parcel
coverage, current base rents, ledgers, lease status) remain blank.
