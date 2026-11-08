# Final integration verification record

**Verification date:** 2026-11-07
**Canonical edition:** root `index.html` + `hub/`
**Independent assurance:** `assurance/` + `audit/final-integration/`
**Branch:** `arena/1abdce92-rentincreasesf1`

## Scope and evidentiary standard

The final audit read the canonical data and generated prose, re-fetched official material, corrected overstatements in the existing generator, regenerated the site, and independently recomputed every scenario and service date. Earlier editions remain preserved as superseded archives; this record does not claim that every historical sentence was re-certified.

Evidence classes are kept separate:

1. **Official rule/rate:** directly supported by one of the 29 registered official sources.
2. **Owner-brief input:** a date or amount supplied for the two units, not an official record.
3. **Conditional arithmetic:** reproducible calculation on an owner-brief input and an official percentage.
4. **Official confirmation:** private license, parcel, lease, or ledger evidence that was unavailable; the public cell is blank and flagged.

No personal identity is used in the current site or verification data.

## Official-source verification

All **29/29** registered sources were retrieved and read from their official publishers: S01–S23 on 2026-11-07 and S24–S29 on 2026-11-08. Each source carries its own retrieval date in `hub/data.json` and in the manifest, so a newly added source cannot inherit a stale blanket date. The registry is [`hub/data.json`](hub/data.json), the compact index is [`SOURCES.md`](SOURCES.md), and the machine-readable retrieval manifest is [`audit/final-integration/source-manifest.json`](audit/final-integration/source-manifest.json).

Notable checks:

- Individual-owner reporting and effective-date license gate: [§37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) + [Housing Inventory](https://www.sf.gov/rent-board-housing-inventory).
- Current 1.6% rate and all historical rates: [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf).
- Banking and notice text, including Rule 4.12(b)’s express non-void provision: [Rules Part IV](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring).
- Fixed-term limitation: [California Tenants guide](https://www4.courts.ca.gov/documents/California-Tenants-Guide.pdf).
- Personal/mail notice and extensions: [Civil Code §827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827&lawCode=CIV) + [CCP §1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013&lawCode=CCP).
- Retaliation conditions and lawful-cause provisions: [Civil Code §1942.5](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1942.5.&lawCode=CIV).
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

| Check | Result at verification |
|---|---|
| `python3 hub/build.py` | Root and eight hub pages regenerated |
| `python3 assurance/build.py` | Assurance page and 29-row source manifest regenerated |
| `python3 tools/verify_hub.py` | **1,545 checks; 0 errors**; 210 claim-table rows with source/flag links |
| `python3 tools/verify_assurance.py` | **1,742 checks; 0 errors**; 33 assurance rows with official sources |
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

The canonical [Flagged for Review](hub/flags.html) contains 24 items. High-severity unknowns include Unit 1 lease status (H-17), Unit 2 current base/history (H-18/H-03), Unit 1 anniversary/history (H-02), both licenses (H-04), and official coverage (H-05). Repair and protected-activity history also remains open (H-09).

**No scenario is certified as notice-ready. No lawful current maximum or attorney/advocate acceptance is asserted.**

## Pull request and deployment result

- [PR #15](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/15) merged at `2026-11-07T21:32:24Z` as `3fbd5e195330babacbd5e1568e287171ee4f8e93` after all three PR workflows passed.
- Post-merge `Verify site` run `42416341845`, `Verify published site` run `42416341852`, and `Final assurance` run `42416341861` all succeeded.
- GitHub Pages build/deployment run `42416341186` succeeded; the Pages API reported `built` for `main` `/`.
- The deployed root, `assurance/index.html`, and `hub/flags.html` were retrieved after deployment and confirmed to contain the corrected license answer, 12 corrections, 29 official sources, and 24 flags.
