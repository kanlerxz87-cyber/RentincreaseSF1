# Coordination

Session: arena-2347590f. Branch: arena/2347590f-rentincreasesf1 (platform-fixed; separate session branches cannot be created here).

| Task | Status | Owner | File scope |
|---|---|---|---|
| Official-source research, privacy-safe dashboard, verification and final integration | in progress | arena-2347590f | COORDINATION.md, README.md, index.html, .nojekyll, docs/**, scripts/**, .github/workflows/** |

Initial inspection: repository contains only README.md; no other claims or implementation found. No personal identifiers will be committed. User-provided dates and amounts will be explicitly unverified, not represented as official records. Shared integration owned by this session because no other tasks are claimed.

Scope expansion: final integration owns root index.html and .nojekyll to accommodate existing GitHub Pages legacy publication from main root. API update to workflow publishing returned 403; preserve the existing configuration rather than require user input.

## Research / integration review — 2026-11-06
- Official sources retrieved: SF annual 2026 announcement, rent guide, coverage, inventory, banking, petitions and tenant/landlord help; California legislative §§827, 1947.12, 1942.5; CRD housing; HUD Fair Housing Act overview. Source URLs are enumerated in docs/data.json and the site's Sources page.
- Row-by-row substantive review separates verified guidance, analysis, derived arithmetic and unverified supplied context. No private fact is marked officially confirmed. No original personal initials were stored.
- Flags F01–F09 published on docs/flagged.html: coverage, ledger, continuity, license/lease, market norms, lawyer approval, source example date errors, privacy limits and verification scope. These are needs review and do not block publication.
- Tests: seven generated pages; 66 rows with official links; source domain/key checks; internal asset/navigation existence; exact-cent calculation checks; JavaScript syntax. No installed browser automation; visual browser testing not claimed. External pages retrieved using official-page tools; no assertion of exhaustive case-law/lease review.
- Initial remote branch pull failed because branch did not exist; rebased against origin/main and pushed the claim. No conflicts and no other sessions found.
- Pages API: existing main-root legacy configuration confirmed. Changing configuration denied 403; using root redirect to docs and legacy deployment instead. No authentication secrets requested.

---

## Parallel Session Claim — `arena/b43dc55e-rentincreasesf1` (2026-11-06)

- **Session ID:** `arena/b43dc55e-rentincreasesf1`
- **Platform branch note:** Arena pins this session to branch `arena/b43dc55e-rentincreasesf1` (creating/switching to `session-<id>/<task>` branches is prohibited by platform configuration). Non-overlapping file scopes are strictly enforced instead.
- **Respecting prior claims:** Session `arena-2347590f` claimed `README.md`, `index.html`, `.nojekyll`, `docs/**`, `scripts/**`, and `.github/workflows/**` (<60 minutes old). Session `arena/b43dc55e-rentincreasesf1` will **not** modify any files in `arena-2347590f`'s claimed scope; any cross-links or updates to those files are logged under Cross-Session Requests below.

### Task Board (`arena/b43dc55e-rentincreasesf1` — disjoint scopes `audit/**` and `dashboard/**`)

| Task ID | Task Description | Status | Owning Session ID | Exclusive File Scope |
|---|---|---|---|---|
| `B43-T1` | Line-by-line repository review & verification audit of existing `docs/data.json`, `scripts/`, and Pages setup against live official sources | done | `arena/b43dc55e-rentincreasesf1` | `audit/repo-verification.md`, `dashboard/data/repo_audit.json` |
| `B43-T2` | Official-source legal verification: SF Rent Ordinance (rates 2019–2027, banking, Roommate Rules, Housing Inventory License), CA State Law (Costa-Hawkins, AB 1482, CC §827, CCP §1013/§1162, CC §1942.5, FEHA/Unruh), Federal FHA | in progress | `arena/b43dc55e-rentincreasesf1` | `audit/legal-sources.md`, `dashboard/data/legal_framework.json`, `dashboard/data/rate_schedule.json`, `dashboard/data/sources.json` |
| `B43-T3` | Anonymized Unit 1 & Unit 2 case analysis, historical/current calculation schedules, Costa-Hawkins continuity, and Executive Summary (strictly placeholder names; zero personal initials) | unclaimed | `arena/b43dc55e-rentincreasesf1` | `audit/executive-summary.md`, `dashboard/data/executive_summary.json`, `dashboard/data/units_analysis.json` |
| `B43-T4` | Corporate vs. individual SF owner practices, statutory notice protocol, reasonable reasons, SF tenant-lawyer red-team audit, and 1-unit vs. 2-unit Fair Housing analysis | unclaimed | `arena/b43dc55e-rentincreasesf1` | `audit/practices-and-scrutiny.md`, `dashboard/data/practices.json`, `dashboard/data/notice_protocol.json`, `dashboard/data/lawyer_scrutiny.json`, `dashboard/data/discrimination.json` |
| `B43-T5` | Irregularities & unverified-items register (`Flagged for Review` dataset) | unclaimed | `arena/b43dc55e-rentincreasesf1` | `dashboard/data/flagged_items.json` |
| `B43-T6` | Build GitHub Pages static dashboard (`dashboard/**`: clean landing page + category subpages + tables + source links + Flagged for Review page) & automated link/schema/privacy verifier | unclaimed | `arena/b43dc55e-rentincreasesf1` | `dashboard/**`, `audit/build_dashboard.py`, `audit/verify_all.py` |
| `B43-T7` | Final session integration, full line-by-line re-verification, link check, PR to `main`, merge, and GitHub Pages deployment confirmation | unclaimed | `arena/b43dc55e-rentincreasesf1` | `COORDINATION.md` (append-only integration/PR log) |

### Cross-Session Requests Log
- **Request from `arena/b43dc55e-rentincreasesf1` to `arena-2347590f` & `arena-53a11683`** (`index.html`, `README.md`, `docs/**`, `data/**`):
  1. Optional cross-link from `docs/index.html` / `README.md` to `dashboard/index.html` once `B43-T6` publishes the expanded multi-category dashboard under `/dashboard/`.
  2. Review repo-audit irregularities `RA-01`–`RA-08` documented in `audit/repo-verification.md` (broken `uscode.house.gov` link in `data/sources.csv` row `S25`, `Rule 4.10(b)/4.12(b)` non-voidness proviso vs. `README.md` line 52, `CCP §1013(a)` +5 calendar day mail extension cutoff `2026-11-25` vs. `2026-11-30`, and Unit 1 April 1, 2026 fixed-term vs. month-to-month ambiguity). No edits made to other sessions' claimed files.

### Task Completion & Verification Log (`arena/b43dc55e-rentincreasesf1`)
- **`B43-T1` (`done`):** Audited all files across `origin/main` line by line against directly fetched official `.gov` sources (`https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf`, `https://www.sf.gov/reports/december-2022/rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring`, `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=827.&lawCode=CIV`, `https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1013.&lawCode=CCP`, `https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm`). Logged 8 irregularities (`RA-01`–`RA-08`) and verified zero PII exposure (`RA-09`).


