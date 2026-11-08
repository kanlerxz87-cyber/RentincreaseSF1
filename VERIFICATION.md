# Verification record

**Verification date:** 2026-11-08
**Canonical edition:** root `index.html` + `hub/`
**Independent assurance:** `assurance/` + `audit/final-integration/`
**Session refresh:** `research/758c724c/` + `assurance/758c724c/`
**Branch:** `arena/758c724c-rentincreasesf1`

## Scope and evidentiary standard

The refresh read the shared coordination board, preserved concurrently merged PR #19 and PR #20 work, re-fetched official material, corrected the existing canonical generator/data, regenerated the site, and independently recomputed every scenario and service date. Earlier editions remain preserved as superseded archives; this record does not claim that every historical sentence was re-certified.

Evidence classes are kept separate:

1. **Official rule/rate:** directly supported by one of the 44 registered official sources.
2. **Owner-brief input:** a date or amount supplied for the two units, not an official record.
3. **Conditional arithmetic:** reproducible calculation on an owner-brief input and an official percentage.
4. **Official confirmation:** private license, parcel, lease, ledger, unit-count, occupant-change, or passthrough evidence that was unavailable; the public cell is blank and flagged.

No personal identity is used in the current site or verification data. Official Housing Inventory filings require truthful owner/contact information and are public; website placeholders are not for official filings.

## Official-source verification

All **44/44** registered sources have recorded retrieval dates and were read from official publishers or the City’s identified official code publisher. The registry is [`hub/data.json`](hub/data.json), the compact index is [`SOURCES.md`](SOURCES.md), and the machine-readable retrieval manifest is [`audit/final-integration/source-manifest.json`](audit/final-integration/source-manifest.json).

Notable checks:

- Individual-owner reporting and effective-date license gate: [§37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing), [Housing Inventory](https://www.sf.gov/rent-board-housing-inventory), [Rule 13.14](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-xiii-reporting-obligations-under-rent).
- Current 1.6% rate and historical rates: [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf).
- Separate Treasurer business-registration question: [lessor guidance](https://sftreasurer.org/information-lessors-residential-real-estate), [Register a Business](https://sftreasurer.org/business/register-business), [§853](https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_business/0-0-0-1875).
- Pending banked-cap proposal, not law: [Legistar File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770).
- Occupant-change rules preserved from PR #20: [§6.14 / Costa-Hawkins overview](https://www.sf.gov/information--rent-increases-under-section-614-and-costa-hawkins), [Rule 6.14](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-vi-rent-increase-justifications), [determination petition](https://www.sf.gov/information--petition-determination-pursuant-section-614-andor-costa-hawkins).
- Personal/mail notice and extensions: [Civil Code §827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827), [CCP §1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013&lawCode=CCP).
- Bond passthrough conditions and worksheet irregularity: [bond worksheets](https://www.sf.gov/information--general-obligation-bond-passthrough-worksheets), [2026–27 worksheet](https://media.api.sf.gov/documents/538_2026-2027_Bond_Measure_Worksheet_10.26.pdf).
- Federal fair-housing statute: [42 U.S.C. §3604 via GovInfo](https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm).

Official-source irregularities are published rather than silently copied: worked-example year errors (H-19), bond worksheet phase-in dates (H-26), multiple-year notice shorthand (H-27), and Ordinance 3-26 effective-date discrepancy (H-28).

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
| Unit 1 annual or combined | 2027-02-01 | 2027-01-02 (30 days) | 2026-12-28 (35 days) | [§827](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827) + [CCP §1013](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013&lawCode=CCP) |
| Unit 2 annual-only | 2027-02-28 | 2027-01-29 (30 days) | 2027-01-24 (35 days) | Same statutes |
| Unit 2 combined | 2027-02-28 | 2026-11-30 (90 days) | 2026-11-25 (95 days) | Same statutes |

These are scenario calculations, not universal last-safe dates or legal clearance.

## Automated and local gates

Canonical and assurance gates were run with `PYTHONDONTWRITEBYTECODE=1`:

| Check | Result at verification |
|---|---|
| `python3 hub/build.py` | Root and eight hub pages regenerated |
| `python3 assurance/build.py` | Assurance page and 44-row source manifest regenerated |
| `python3 tools/verify_hub.py` | **1,806 checks; 0 errors**; 231 claim-table rows with source/flag links |
| `python3 tools/verify_assurance.py` | **2,118 checks; 0 errors**; 33 assurance rows with official sources |
| Current-text privacy scan | **177 files; no forbidden personal token** |
| `python3 review/build.py && python3 review/verify.py` | Archived review edition reproducible after pinning its generation date; all checks passed |
| `git diff --check` | No whitespace errors |

The session gate `tools/verify_758c724c.py` and workflow `.github/workflows/758c724c.yml` add research-registry, row-citation, blank-cell, reproducibility, and legacy-suite checks. CI reproduces builds and fails on stale output.

## Preserved legacy suites

```bash
python3 tools/check_links.py
python3 build/build.py && python3 tools/check_site.py
python3 integration/verify.py
python3 dashboard/verify.py
python3 audit/verify_all.py
python3 review/build.py && python3 review/verify.py
```

Passing an archived edition’s own suite does not mean every archived legal statement was accepted into the canonical edition.

## Remaining limitations

The canonical [Flagged for Review](hub/flags.html) contains 28 items. High-severity unknowns include Unit 1 lease status (H-17), Unit 2 current base/history (H-18/H-03), Unit 1 anniversary/history (H-02), both licenses (H-04), official coverage (H-05), and bond passthrough inputs (H-25). Business-registration facts remain conditional (H-21). File #261020 is pending, not enacted (H-22). Occupant-change notice and co-tenant/subtenant facts remain open (H-23/H-24).

**No scenario is certified as notice-ready. No lawful current maximum or attorney/advocate acceptance is asserted.**

## Deployment history

Prior integration PRs #15, #16, #19, and #20 merged and confirmed GitHub Pages for `main` root. This refresh records its own PR/check/Pages result in `COORDINATION.md` after merge. The public entry remains <https://kanlerxz87-cyber.github.io/RentincreaseSF1/>.
