# Session `arena-3e212173` — final integration findings (2026-11-11 UTC)

**Branch:** `arena/3e212173-rentincreasesf1` · **Base:** `main` at `3885c6b` (PR #42)
**Scope:** F1–F5 per `COORDINATION.md`. No personal identifier from the owner's brief appears in this file.

## F4 — Independent live re-verification (2026-11-11)

Each page below was fetched and read live on 2026-11-11. All core answers on the canonical dashboard still hold.

| # | Official source (live 2026-11-11) | What was confirmed | Dashboard support |
| --- | --- | --- | --- |
| 1 | [SF Admin Code §37.15](https://www.sf.gov/information/sec-3715-reporting-obligations-licensing) | Owners of units subject to Ch. 37 must report; §37.15(e): substantial compliance → licence for §37.3(a)(1)–(2); noncompliance → temporary suspension; restoration prospective; tenant owes nothing for suspension months | S01; licensing page; executive summary §1 steps 4–5 |
| 2 | [Rent Board Housing Inventory](https://www.sf.gov/rent-board-housing-inventory) | All residential owners must report; tenant-occupied units receive a licence; reporting free; March 1 annual deadline; late submission allowed; licence required on the **effective date**; licence need not be attached to notice | S03; licensing page |
| 3 | [Banked rent increases](https://www.sf.gov/information--banked-rent-increases) | Nov 9, 2026 notice: File #261020 would cap combined banked + capital-improvement at 10%/yr if enacted; applies to banked notices on/after Sept 15, 2026; **not enacted, subject to change**; 24-month banking test; no compounding | S04; limits page; flag H-22 |
| 4 | [Legistar File #261020](https://sfgov.legistar.com/LegislationDetail.aspx?ID=8217304&GUID=7EDA4662-EBFB-4AF5-962F-C669B64AA770) | Status: **Pending Committee Action**; introduced 9/15/2026; no final action; no enactment date; Leg Ver1 / Leg Dig Ver1 attached | S26; flag H-22 |
| 5 | [Rules Part XIII §13.14](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-xiii-reporting-obligations-under-rent) | Effective date (not service date) governs licence conformity; unlicensed increase null and void; **banking rights unaffected** | Corroborates S01/S07 (see F3) |
| 6 | [2027 Fee/Inventory Notice](https://www.sf.gov/notice-of-rent-board-fee-and-housing-inventory-requirement/) | Exemption request deadline **Monday, Dec 14, 2026**; Housing Inventory deadline **March 1, 2027**; the two are mutually non-substitutable | Corroborates S17 (see F3) |
| 7 | [Notice of Owner Noncompliance](https://www.sf.gov/notice-of-owner-noncompliance-with-housing-inventory) | Unlicensed increase may be null and void; tenant may file Unlawful Rent Increase Petition (Form 516C) or Tenant Summary Petition (Form 518); licence check via Portal by address/APN | Corroborates S01/S03 (see F3) |
| 8 | [42 U.S.C. §3604 (GPO)](https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm) | Statutory text: unlawful to discriminate in terms/conditions of rental because of race, color, religion, sex, familial status, national origin, handicap | Corroborates S14 (see F3) |
| 9 | [2024 Census/HUD RHFS (CB26-TPS.12)](https://www.census.gov/newsroom/press-releases/2026/2024-rhfs-data.html) | National property/mortgage/ownership survey; no SF 94122 rate-setting behaviour data | Corroborates H-11 blank (see F3) |

No figure, rate, date, or legal conclusion on the canonical dashboard required change after this re-verification.

## F3 — Stale PR triage

### PR #29 — "Record PR #27 merge and Pages deploy in COORDINATION.md" (docs-only, 1 file)
- **Verdict: superseded, close.** The PR only appends a coordination record for PR #27. That record's substance (T1–T5 done, 20 sources, recomputation) has been overtaken by later merged PRs (#40, #42) and by the current 29-source canonical edition. Merging now would append a stale record and conflict with the live board. Nothing in it is needed for the site. **Action:** close with a comment pointing to this triage.

### PR #32 — "2026-11-10 full official-source verification (34/34), Rule §13.14, 2027 deadlines, File #261020 alert, template/count bugfixes" (22 files)
- **Verdict: substance already in `main` via later PRs; close after carrying forward the one remaining defect (F2).** Item-by-item:
  - *Template `{n}` placeholders + stale counts/dates* — **already fixed on `main`** (verified: no `{n}` in `index.html`/`hub/*.html`; counts read 14 checks / 24 flags / 29 sources). Nothing to carry.
  - *File #261020 Sept 15, 2026 retroactive trigger + Nov 9 Rent Board warning* — **already in `main`** (README, EXECUTIVE_SUMMARY, hub pages, flag H-22, source S04/S26). Nothing to carry.
  - *Dec 14, 2026 exemption deadline + March 1, 2027 Inventory deadline* — **already in `main`** via S17 quote and executive summary. Nothing to carry.
  - *Trailing-dot §1942.5 URLs* — **NOT in `main`** (4 occurrences). **Carried forward as F2** in this session's branch.
  - *Five additional sources S30–S34* — each verified live above (rows 5–9). They are **corroborating, not load-bearing**: every claim they support is already supported by a registered source on `main` (S01/S07 for §13.14; S17 for the 2027 notice; S14 for §3604; S01/S03 for noncompliance; H-11 blank for RHFS). Adding five registry entries would require coordinated changes to `hub/data.json`, `hub/build.py`, both verifiers, and the manifest for zero change to any figure, rate, or conclusion. **Decision:** do not add as separate registry entries; record the live verification here so the findings are not lost. A future session may promote any of them if it wants the corroboration in the registry.
- **Action:** close with a comment summarising the above and linking to this file.

## F2 — Defect fixed in this branch
- `EXECUTIVE_SUMMARY.md` (3 URLs) and `VERIFICATION.md` (1 URL): `sectionNum=1942.5.` → `sectionNum=1942.5`. Matches the canonical `hub/data.json` S12 URL. No other trailing-dot URLs remain in root Markdown (archived `audit/data/sources.json` copies are superseded archives, left untouched).

## F1 — Suite results (run after F2 fix, on the combined tree)

| Suite | Result |
| --- | --- |
| `hub/build.py` (canonical rebuild) | 9 pages written; deterministic (matches committed `index.html`/`hub/*.html` byte for byte — `git status` clean) |
| `assurance/build.py` (assurance rebuild) | assurance/index.html + 29-row manifest written; deterministic |
| `tools/verify_hub.py` | **1599 checks passed, 0 errors** — 211 claim rows source-linked, 29/29 sources cited, pressured figures rejected: 0 |
| `tools/verify_assurance.py` | **1822 checks passed, 0 errors** — 37 assurance rows source-linked, 29/29 manifest rows, 215 current text files privacy-scanned |
| `tools/check_links.py` | OK — all internal links/anchors resolve; no personal tokens |
| `tools/check_site.py` | **781 checks passed, 0 errors** |
| `integration/verify.py` | PASS — 57 source-linked rows, local links, arithmetic |
| `dashboard/verify.py` | OK — 42 sources, 67 verified facts, 21 flagged items, 12 pages; every table row source-linked |
| `audit/verify_all.py` | VERIFICATION PASSED — 137 source-linked rows, 39 .gov URLs, exact-cent arithmetic, privacy checks passed |

Note: `review/build.py` was executed to confirm the archive suite still passes ("All checks PASSED"). It regenerates archived pages with a 2026-11-11 generated-date stamp only; those files (`review/**`) are outside this session's claimed scope, so the regenerated timestamps were discarded with `git checkout -- review/`. No archived-page content was changed.

## Irregularities / flags
- None new. The 24 existing flags on `hub/flags.html` stand. Historical Git history privacy disclosure (index.html alert) stands and is out of scope for current-file edits.

## Addendum — 2026-11-11 (after rebase onto `origin/main` at `33fe8af`)

Later the same day, parallel sessions merged PR #46 (`arena-8bcddc6b`, audit-only) and PR #47 (`arena-e5dc4547`) into `main`. PR #47: (a) carries the **identical** fix for the four trailing-dot `sectionNum=1942.5.` URLs (verified byte-identical to this session's F2 — this branch's copies vanished on rebase); (b) ports **S30** (adopted Rules Part XIII §13.14 — effective date governs licence conformity; unlicensed null-and-void increase preserves banking rights) and **S31** (Notice of Owner Noncompliance — Portal licence lookup by address/APN; Unlawful Rent Increase Petition after the effective date vs. Tenant Summary Petition before it; rent-refund exposure) into the registry, raising the registry from 29 to **31 sources**. Every claim those two sources support was already in this session's F4 live verification above. Nothing in this addendum changes any figure, rate, date, or conclusion.
