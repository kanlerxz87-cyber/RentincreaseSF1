# SF Rent Increase Compliance — Outer Sunset 94122

An anonymized, official-source review for two reported rent-controlled units in a 1940 San Francisco building. The canonical dashboard is the repository root plus `hub/`; an independent assurance layer records corrections, arithmetic, source retrieval, and unresolved facts.

**Published entry:** <https://kanlerxz87-cyber.github.io/RentincreaseSF1/>
**Executive summary:** [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md)
**Flagged for Review:** [`hub/flags.html`](hub/flags.html)
**Independent assurance:** [`assurance/index.html`](assurance/index.html)

## Answer first

**Yes.** An individual owner must report each tenant-occupied unit through the Rent Board Housing Inventory and have a current Rent Increase License when an annual or banked increase takes effect. No corporation is required and no individual-owner exemption applies. The safer sequence is to finish reporting before serving notice; the statutory hard gate is licensure on the **effective date**. Ordinary annual/banked notices go to the tenant, not to the Board for per-increase approval.

Official sources: [SF Administrative Code §37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) and [Rent Board Housing Inventory](https://www.sf.gov/rent-board-housing-inventory).

The published current annual allowance is **1.6% for March 1, 2026–February 28, 2027**. [Rent Board Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf)

All dollar results in this repository are **conditional scenario arithmetic**, not certified current lawful rents or permission to serve notice. Unit 1’s April 2026 fixed-term/month-to-month status is unknown. Unit 2’s $3,150 is supplied only as its June 2019 lease-start rent, not expressly as current base. Both ledgers, both licenses, and official coverage require private review.

## Canonical files

| Path | Purpose |
|---|---|
| `index.html` | Landing dashboard; individual-owner answer first; archived editions clearly labeled superseded |
| `hub/licensing.html` | Housing Inventory, automatic license generation, late reporting, effective-date gate, correct sequence |
| `hub/limits.html` | Local/state/federal layers, complete Form 571 table, conditional calculations |
| `hub/notice.html` | Notice contents, personal/mail arithmetic, lawful bases, scenario-only drafting aid |
| `hub/practice.html` | Owner-neutral duties, SF algorithm ban, accurately bounded DOJ enforcement example |
| `hub/fair-housing.html` | One unit or both; protected-class and retaliation analysis without safe-harbour claims |
| `hub/review.html` | 13 tenant-side review checks; no attorney verdict |
| `hub/flags.html` | 20 unresolved facts and source/repository irregularities; official-confirmation blanks |
| `hub/sources.html` | 23 official sources with supporting passages |
| `hub/data.json` | Single canonical source for official rules, rates, owner-brief inputs, and flags |
| `hub/build.py` | Reproducible root/hub generator |
| `assurance/` | Independent correction register, recomputed arithmetic/dates, and assurance generator |
| `audit/final-integration/` | Machine-readable findings and 23-source live-retrieval manifest |
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

The assurance workflow fails if either generator changes committed output. At the final local verification, the suites passed **1,336 canonical checks** and **1,556 assurance checks**, including 194 source/flag-linked canonical claim rows, 33 source-linked assurance rows, 23 live-source manifest entries, and a privacy scan of 170 current text files.

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
