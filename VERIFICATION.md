# Final integration verification record

**Verification date:** 2026-11-10 (full 29-source live re-verification and repair pass; prior baseline PR #15 verified 2026-11-07)
**Canonical edition:** root `index.html` + `hub/`
**Independent assurance:** `assurance/` + `audit/final-integration/`
**Branch:** `arena/7ab74b3e-rentincreasesf1`

## Scope and evidentiary standard

The final audit read the canonical data and generated prose, re-fetched official material, corrected overstatements in the existing generator, regenerated the site, and independently recomputed every scenario and service date. Earlier editions remain preserved as superseded archives; this record does not claim that every historical sentence was re-certified.

Evidence classes are kept separate:

1. **Official rule/rate:** directly supported by one of the 29 registered official sources.
2. **Owner-brief input:** a date or amount supplied for the two units, not an official record.
3. **Conditional arithmetic:** reproducible calculation on an owner-brief input and an official percentage.
4. **Official confirmation:** private license, parcel, lease, or ledger evidence that was unavailable; the public cell is blank and flagged.

No personal identity is used in the current site or verification data.

## Official-source verification

All **29/29** registered sources were re-fetched and verified live from their official publishers on **2026-11-10** (originally retrieved 2026-11-07 for S01–S23 and 2026-11-08 for S24–S29), alongside File #261020's legislative attachments (`Leg Ver1` / `Leg Dig Ver1`) and `42 U.S.C. §3604` on GovInfo. Each source carries its retrieval date in `hub/data.json` and in the manifest, so a newly added source cannot inherit a stale blanket date. The registry is [`hub/data.json`](hub/data.json), the compact index is [`SOURCES.md`](SOURCES.md), and the machine-readable retrieval manifest is [`audit/final-integration/source-manifest.json`](audit/final-integration/source-manifest.json).

Notable checks (`2026-11-10`):

- Individual-owner reporting and effective-date license gate: [§37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) + [Housing Inventory](https://www.sf.gov/rent-board-housing-inventory).
- Current 1.6% rate and all 46 historical periods: [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf).
- November 9, 2026 official Rent Board warning and BOS File #261020 (`Pending Committee Action — not law`), including proposed `§37.3(h)` (10% of lowest 12-month base rent cap through Dec 31, 2029, carryover Jan 1, 2030, retroactive to banked notices provided on or after Sept 15, 2026) and proposed `§37.15(b)(2)(F)` banked reporting: [Banked rent increases](https://www.sf.gov/information--banked-rent-increases) + [Learn about rent increases](https://www.sf.gov/learn-about-rent-increases-san-francisco) + [File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770).
- 2026–27 Rent Board Fee ($59.00/unit, 50% tenant recovery if in occupancy Nov 1, due March 1) and the **December 14, 2026** exemption-request deadline for the 2027 fee: [Rent Board Fee](https://www.sf.gov/rent-board-fee).
- Banking and notice text, including Rule 4.12(b)’s express non-void provision: [Rules Part IV](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring).
- Occupant-change subsection distinctions (`§6.14(b)` co-occupants 60-day initial notice presumption vs. `§6.14(c)` non-co-occupants 90-day post-vacancy reservation/waiver rule vs. `§6.14(d)` pre-April 25, 2000 departures and Costa-Hawkins): [Rules Part VI](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-vi-rent-increase-justifications).
- Fixed-term limitation: [California Tenants guide](https://www4.courts.ca.gov/documents/California-Tenants-Guide.pdf).
- Personal/mail notice and extensions: [Civil Code §827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827&lawCode=CIV) + [CCP §1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013&lawCode=CCP).
- Retaliation conditions and lawful-cause provisions: [Civil Code §1942.5](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1942.5&lawCode=CIV).
- Corporate-practice example, accurately labeled as allegations/proposed settlement: [DOJ RealPage announcement](https://www.justice.gov/opa/pr/justice-department-requires-realpage-end-sharing-competitively-sensitive-information-and).

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

| Check | Result at verification (`2026-11-13`) |
|---|---|
| `python3 hub/build.py` | Root and nine hub pages regenerated (including `hub/suggestions.html`) |
| `python3 assurance/build.py` | Assurance page and 36-row source manifest regenerated |
| `python3 tools/verify_hub.py` | **1,892 checks; 0 errors**; 238 claim-table rows with source/flag links; 36/36 sources cited |
| `python3 tools/verify_assurance.py` | **2,204 checks; 0 errors**; 39 assurance rows with official sources; 36/36 manifest rows |
| Current-text privacy scan | **270 files; no forbidden personal token** |
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

## Corrections made by the final audit

The 12-row public correction register is rendered at [`assurance/index.html`](assurance/index.html). It covers:

- effective-date versus notice-date license timing;
- Unit 2 lease-start versus current-base labeling;
- Unit 1 fixed-term contingency;
- reconciliation of banking measuring points;
- Rule 4.10/4.12 notice exceptions;
- fact-specific retaliation and repair analysis;
- limits of free-representation claims;
- fair-housing neutrality without safe-harbour claims;
- accurately bounded corporate-practice evidence;
- official worked-example year errors;
- separation of Rent Board Fee recovery from license/base rent;
- blank market-normal and owner-behavior values.

## Remaining limitations

The canonical [Flagged for Review](hub/flags.html) contains 24 items. High-severity unknowns include Unit 1 lease status (H-17), Unit 2 current base/history (H-18/H-03), Unit 1 anniversary/history (H-02), both licenses (H-04), official coverage (H-05), and pending BOS File #261020 (H-22). Repair and protected-activity history (H-09) and Unit 1 occupant-change records (H-23/H-24) also remain open.

**No scenario is certified as notice-ready. No lawful current maximum or attorney/advocate acceptance is asserted.**

## Initial PR #15 deployment record (2026-11-07)

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

## Defects repaired and full-registry update (2026-11-10, `arena/7ab74b3e-rentincreasesf1`)

- Repaired invalid CSS property (`font-size1.02rem` → `font-size:1.02rem`) in `hub/assets/style.css`.
- Replaced stale hardcoded counts and retrieval dates in `hub/build.py` (`13 checks` → dynamic `14 checks`; `Twenty flagged` → dynamic `24 flagged`; `twenty-three` / `14 SF Rent Board` / `7 November 2026` → dynamic `29` sources with accurate City/State/Federal counts and `10 November 2026` retrieval).
- Surfaced pending BOS File #261020 and the Rent Board's November 9, 2026 retroactive notice warning (`September 15, 2026` cutoff; `10%` of lowest 12-month base rent through `December 31, 2029`; carryover `January 1, 2030`; proposed `§37.15(b)(2)(F)` banked reporting) on `hub/limits.html`, `hub/notice.html`, `hub/licensing.html`, `index.html`, and `H-22`.
- Surfaced the **December 14, 2026** 2027 Rent Board Fee exemption-request deadline (`S17`) on `hub/licensing.html` and `EXECUTIVE_SUMMARY.md`.
- Refined `S28`, `H-23`, and occupant-change tables to distinguish `§6.14(b)` (co-occupants: 60-day initial notice presumption) from `§6.14(c)` (non-co-occupants, post-April 25, 2000 departures: 90-day post-vacancy reservation/waiver window) and `§6.14(d)` (pre-April 25, 2000 departures).
- Repaired the broken Markdown table row gap before step 9 in `EXECUTIVE_SUMMARY.md` and reconciled counts (`14` checks, `29` manifest entries) in `README.md`.

## Pull request and deployment history

- Initial final-integration baseline: [PR #15](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/15) merged at `2026-11-07T21:32:24Z` (`3fbd5e195330babacbd5e1568e287171ee4f8e93`); followed by PRs #16–#27 on `main` (through `3a07761`).
- Current `2026-11-10` full 29-source live re-verification and repair pass is tracked in [`COORDINATION.md`](COORDINATION.md) under `arena/7ab74b3e-rentincreasesf1`.
---

# Dated addendum — 2026-11-11 (`arena-e5dc4547`)

**Result: no rate, date, dollar figure, or legal conclusion changed.** Thirteen load-bearing sources
were re-read live from their official publishers on **2026-11-11** (S01 §37.15, S02 §37.3, S03
Housing Inventory, S04 banked increases, S05 learn about rent increases, S06 Form 571, S07 Rules
Part IV §§4.10/4.12, S08 Civil Code §827, S10 AB 1482, S17 Rent Board Fee, S24 Treasurer lessor
guidance, S26 File #261020, S27 §6.14/Costa-Hawkins). Every published claim checked matched the
official text, including: the individual-owner reporting duty with no exemption; the effective-date
licence gate; the 1.6% allowance and the full Form 571 table; banking (24-month guidance / 12-month
Rule 4.12(a), no compounding, no rounding up); 30/90-day notice with +5 mail days; the 8.8% AB 1482
figure and its inapplicability to locally controlled units; the $59.00 Rent Board Fee with the
December 14, 2026 exemption deadline; the conditional sub-four-unit Business Registration carve-out;
File #261020 still `Pending Committee Action — not law` (no final action, no enactment date); and
the §6.14/Costa-Hawkins occupant-change tests. All scenario arithmetic and service dates were
recomputed independently and reproduce to the cent.

**Two findings missing from `main` were ported from stale PR #32** (CONFLICTING; closed as
superseded — see `COORDINATION.md` E5-2/E5-3a), each live-verified 2026-11-11 and added to the
registry as **S30** (adopted Rule §13.14: effective date governs; unlicensed null-and-void increase
does not forfeit banking rights) and **S31** (Notice of Owner Noncompliance: Portal APN/address
licence lookup; Unlawful Rent Increase Petition after the effective date vs. Tenant Summary Petition
before it; rent-refund exposure). Registry: 29 → 31 sources. Also fixed: the `sectionNum=1942.5.`
URL typo in `EXECUTIVE_SUMMARY.md`/`VERIFICATION.md`, and the stale `14-point` review count (15 rows).

**Gates re-run on the combined tree (2026-11-11):** `hub/build.py` (9 pages) and `assurance/build.py`
(31 manifest rows) regenerate cleanly; `tools/verify_hub.py` **1,611 checks, 0 errors** (31/31 sources
cited, 211 claim rows); `tools/verify_assurance.py` **1,852 checks, 0 errors** (31/31 manifest, 214
files privacy-scanned); all preserved legacy suites pass. The `review/build.py` footer-date rebuild
artifact was reverted, as before. All 24 flags remain open; no scenario is certified notice-ready.

## Addendum — 2026-11-11 second pass (`arena/992eb322`)

* **S32** added: the Rent Board's 2027 fee/Housing Inventory notice, read live 2026-11-11. It confirms the
  two obligations are separate — a fee-exemption request by **Monday 14 December 2026**, and the Housing
  Inventory report by **1 March 2027** — and that no licence issues until reporting is complete.
* **S33** added: the enacted text of **42 U.S.C. §3604** on GovInfo, read live 2026-11-11. §3604(b)
  reaches the "terms, conditions, or privileges" of a rental, which covers a rent increase; the federal
  layer therefore no longer rests only on HUD's overview page.
* `tools/verify_assurance.py` approves `www.govinfo.gov` as an official publisher. No check was removed or
  loosened; the allowlist extension is for a source actually read.
* Stale counts in `README.md` (1,592 / 1,812 / 29 manifest entries) replaced with the measured values for
  this pass.
* Registry: **31 → 33 sources.** No rate, date or dollar figure changed. Recorded as assurance
  corrections `A-13` and `A-14`.

## Addendum — 2026-11-13 live re-verification pass (`arena/cab8cfbc`)

* **Load-bearing subset re-read live 2026-11-13** (fetch and read from the official publisher, quote
  checked against the registered passage): **S01** (§37.15 — includes the Ord. No. 265-20 enactment
  note and the §37.15(c) March 1, 2023 phase-in for buildings with fewer than 10 units), **S03**
  (Housing Inventory), **S04** (banked increases, incl. the November 9, 2026 File #261020 notice),
  **S05** (rent increases; 1.6% for 2026-03-01 – 2027-02-28), **S06** (Form 571 — full rate table
  re-matched row by row), **S17** (Rent Board Fee $59.00/unit 2026-27; December 14, 2026 exemption
  deadline), **S26** (Legistar File #261020), **S30** (Rule §13.14), **S32** (2027 fee/Housing
  Inventory notice — names Ordinance No. 265-20 verbatim). No substantive change to any registered
  quote; four quotes extended with passages verified today (S01 §37.15(c)+enactment note, S03
  March-1-2023 sentence, S30 applicability sentence, S32 Ord. 265-20 sentence).
* **File #261020 re-checked live on Legistar 2026-11-13:** still *Pending Committee Action* (Land Use
  and Transportation Committee), no final action, no enactment date — **not law**. Recorded in H-22
  and in every generated warning block.
* **S34 added** (registry 33 → 34): U.S. Census Bureau / HUD press release CB26-TPS.12 for the 2024
  Rental Housing Finance Survey, read live 2026-11-13. It is cited only for the negative finding
  behind H-11 — the dataset is national ("U.S. residential properties with at least one housing rental
  unit") and carries no SF/94122 figure — so the "reasonable and normal market increase for 94122"
  and "corporate vs individual owner behaviour" cells remain blank and flagged, as the verification
  rule requires. `tools/verify_assurance.py` now approves `www.census.gov` as an official publisher
  (federal statistical agency) and accepts `2026-11-13` as a recorded live-verification date; no check
  was removed or loosened. `tools/verify_hub.py` pins S34 positively (host + quote needle), as it
  already did for S24–S26.
* **Owner's "2023 law" question answered in the executive summary forefront** with registered quotes:
  the reporting/licensing duty is **local** (S.F. Admin. Code §37.15, added by Ord. No. 265-20,
  effective January 18, 2021); for buildings with fewer than 10 units it began **March 1, 2023**
  (S01 §37.15(c), S03, S30); the state frameworks (Costa-Hawkins §1954.53, TPA §1947.12) impose
  neither this licence nor this duty.
* **Independent arithmetic re-check (Decimal, by hand from Form 571):** U1 $3,995.00 × 1.6% = $63.92
  (new $4,058.92); U1 combined 3.0% = $119.85 (new $4,114.85); U2 $3,150.00 × 1.6% = $50.40 (new
  $3,200.40); U2 banked 11.5% = $362.25; U2 combined 13.1% = $412.65 (new $3,562.65). Every figure
  matches the canonical pages to the cent; banked components (1.8/0.7/2.3/3.6/1.7/1.4) match the
  Form 571 rows for the anniversary years used.
* **Stale-count irregularities fixed:** `EXECUTIVE_SUMMARY.md` "14-point review" → 15 review rows;
  `SOURCES.md` header "All 29 registered sources live-verified 2026-11-10" → per-source dates through
  2026-11-13; `README.md` "29-source live-retrieval manifest" → 34-source; `VERIFICATION.md` gate
  table refreshed to this pass's measured values. Generator blanket-date wording in `hub/build.py`
  corrected to per-source dates (it previously claimed all sources were read on one date).
* **Gates re-run on this tree (2026-11-13):** `hub/build.py` (9 pages) and `assurance/build.py`
  (34 manifest rows) regenerate cleanly; `tools/verify_hub.py` **1,633 checks, 0 errors**;
  `tools/verify_assurance.py` **1,916 checks, 0 errors**; `tools/check_links.py` OK (10 published
  pages +7 archived); `tools/check_site.py` **781 checks, 0 errors**; all preserved legacy suites
  pass (`handbook/verify.py` 2,112; `integration/verify.py` 57 rows; `audit/verify_all.py` 137 rows;
  `dashboard/verify.py` OK; `review/verify.py` OK). All 24 flags remain open; no scenario is
  certified notice-ready. No personal identifier written to any file or commit.
