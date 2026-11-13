# SF Rent Increase Compliance — Outer Sunset 94122

An anonymized, official-source review for two reported rent-controlled units in a 1940 San Francisco building. The canonical dashboard is the repository root plus `hub/`; an independent assurance layer records corrections, arithmetic, source retrieval, and unresolved facts.

**Published entry:** <https://kanlerxz87-cyber.github.io/RentincreaseSF1/>
**Executive summary:** [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)
**Flagged for Review:** [`hub/flags.html`](hub/flags.html)
**Independent assurance:** [`assurance/index.html`](assurance/index.html)

## Answer first

**Yes.** An individual owner must report each tenant-occupied unit through the Rent Board Housing Inventory and have a current Rent Increase License when an annual or banked increase takes effect. No corporation is required and no individual-owner exemption applies. The safer sequence is to finish reporting before serving notice; the statutory hard gate is licensure on the **effective date**. Ordinary annual/banked notices go to the tenant, not to the Board for per-increase approval.

Official sources: [SF Administrative Code §37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) and [Rent Board Housing Inventory](https://www.sf.gov/rent-board-housing-inventory).

**The Rent Increase License is not the only City registration, and the two are commonly confused.** A **Business Registration Certificate** is issued by the Office of the Treasurer & Tax Collector, is a general business-tax registration, and does not affect whether a rent increase is lawful. On the reported two units in one building, the Tax Collector's own guidance points to *no* business registration: rental income from "one residential structure consisting of fewer than four units" is not, "by reason of that fact alone", required to register. The carve-out is conditional — other San Francisco business activity, payroll expense, or short-term rental income can trigger it — so it is published as a conditional determination ([lessor guidance](https://sftreasurer.org/information-lessors-residential-real-estate), [register a business](https://sftreasurer.org/business/register-business), flag `H-21`), not as a settled fact.

**November 10, 2026 update — pending File #261020 & Rent Board warning:** On `2026-11-09`, the [Rent Board](https://www.sf.gov/information--banked-rent-increases) posted a formal notice warning that [Board of Supervisors File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770), if enacted as currently proposed, would add `§37.3(h)` capping combined banked (`§37.3(a)(2)`) and capital-improvement (`§37.3(a)(3)`) increases at **10% per year of the lowest base rent in effect during the preceding 12 months** through December 31, 2029 (carryover imposable on or after January 1, 2030), would apply retroactively to **banked increases noticed on or after September 15, 2026** (and capital-improvement petitions filed on or after that date), and would amend `§37.15(b)(2)(F)` to require Housing Inventory reporting of prior-12-month banked increases. Re-checked on Legistar on `2026-11-10` (with `Leg Ver1` / `Leg Dig Ver1`) and again on `2026-11-13`: **Pending Committee Action — not law**, no final action, no enactment date, and subject to change. It is not applied to any figure here, but Unit 2’s conditional scenario includes 11.5% banked before the separate 1.6% annual allowance (13.1% total) — both above 10% — and any newly served banked notice falls on or after September 15, 2026; do not use it to serve notice without checking File #261020 and obtaining advice (flag `H-22`). Also note the **December 14, 2026** deadline to submit a Request for Exemption for the 2027 Rent Board fee ($59.00/unit, due March 1, 2027).

The published current annual allowance is **1.6% for March 1, 2026–February 28, 2027**. [Rent Board Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf)

All dollar results in this repository are **conditional scenario arithmetic**, not certified current lawful rents or permission to serve notice. Unit 1’s April 2026 fixed-term/month-to-month status is unknown. Unit 2’s $3,150 is supplied only as its June 2019 lease-start rent, not expressly as current base. Both ledgers, both licenses, and official coverage require private review.

## Canonical files

| Path | Purpose |
|---|---|
| `index.html` | Landing dashboard; individual-owner answer first; archived editions clearly labeled superseded |
| `hub/licensing.html` | Housing Inventory, automatic license generation, late reporting, effective-date gate, correct sequence, and the separate Business Registration Certificate question |
| `hub/limits.html` | Local/state/federal layers, complete Form 571 table, conditional calculations, and the §6.14 / Costa-Hawkins occupant-change rules |
| `hub/notice.html` | Notice contents, personal/mail arithmetic, lawful bases, scenario-only drafting aid |
| `hub/practice.html` | Owner-neutral duties, SF algorithm ban, accurately bounded DOJ enforcement example |
| `hub/fair-housing.html` | One unit or both; protected-class and retaliation analysis without safe-harbour claims |
| `hub/review.html` | 15 tenant-side review checks; no attorney verdict |
| `hub/flags.html` | 24 unresolved facts and source/repository irregularities; official-confirmation blanks |
| `hub/sources.html` | 34 official sources with supporting passages and per-source retrieval dates |
| `hub/data.json` | Single canonical source for official rules, rates, owner-brief inputs, and flags |
| `hub/build.py` | Reproducible root/hub generator |
| `assurance/` | Independent correction register, recomputed arithmetic/dates, and assurance generator |
| `audit/final-integration/` | Machine-readable findings and 34-source live-retrieval manifest |
| `tools/verify_hub.py` | Canonical link, source, arithmetic, privacy, and corrected-label regression checks |
| `tools/verify_assurance.py` | Independent cross-checks plus current-text privacy scan across the repository |
| `.github/workflows/assurance.yml` | Rebuild and verification gate on pull requests and `main` |

## Build and verify

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 hub/build.py
python3 assurance/build.py
python3 tools/verify_hub.py
python3 tools/verify_assurance.py
```

The assurance workflow fails if either generator changes committed output. At the final local verification (`2026-11-13`), the suites passed **1,633 canonical checks** and **1,916 assurance checks**, including 211 source/flag-linked canonical claim rows, 39 source-linked assurance rows, 34 live-source manifest entries (each dated with the pass that read it, `2026-11-07` to `2026-11-13`), and a privacy scan of 246 current text files. Count assertions are floors plus positive content assertions, so a later session cannot silently drop a verified row.

## Preserved prior work

Earlier parallel sessions produced `docs/`, `docs/v2/`, `dashboard/`, `portal/`, `integration/`, `review/`, `site/`, `research/`, and related datasets/tooling. They are retained and linked from the root as **superseded archives**, not equally current guidance. No legacy implementation is deleted by this integration. Known historical overstatements are corrected in the canonical edition and documented in `audit/final-integration/findings.json`.

Their checks are preserved and run during integration:

```bash
python3 tools/check_links.py
python3 build/build.py && python3 tools/check_site.py
python3 integration/verify.py
python3 dashboard/verify.py
python3 audit/verify_all.py
python3 review/build.py && python3 review/verify.py
```

These legacy suites validate their own editions; they do not certify every archived legal statement against the corrected canonical analysis.

## Privacy and evidentiary limits

- No tenant names, initials, street address, or tenant contact details are published in current text files.
- Dates and supplied dollar amounts are preserved as anonymized scenario inputs.
- Owner-brief facts are not relabeled as official facts.
- Unsupported official-confirmation values are blank and linked to a flag.
- No official 94122 market-normal increase or SF behavior-by-owner-type dataset was located.
- Official Rent Board worked-example year errors are flagged; Form 571 controls rate periods.
- No attorney reviewed this repository, and no tenant/advocate acceptance is promised.

This is a research summary, not legal advice. Resolve all high-severity flags and review the actual lease, ledger, license record, and notice before serving. SF Rent Board counseling: 415-252-4600.
