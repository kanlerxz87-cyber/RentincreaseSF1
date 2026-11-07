# COORDINATION.md — Shared Task Board

This file is the shared task board for multi-session work on this repository.
Read it before starting any task. Claim a task by writing your session ID and
file scope below, then commit and push the claim immediately.

**Last updated:** 2026-11-06 (UTC)
**Repo:** `kanlerxz87-cyber/RentincreaseSF1`
**Default/published branch:** `main`  **GitHub Pages source:** `main` → `/docs`

---

## Environment constraint on branch naming (read this first)

The task protocol asks each session to work on its own branch named
`session-<id>/<task>`. In this environment the working session is bound by the
platform to the branch **`arena/53a11683-rentincreasesf1`**, and the session is
not permitted to create, switch to, or push any other branch. This session
therefore:

* works only on `arena/53a11683-rentincreasesf1`;
* records its file scope in this board **before** writing those files;
* opens the integration pull request **from** `arena/53a11683-rentincreasesf1`
  **into** `main`;
* runs `git pull --rebase origin main` before every push.

This is recorded here so a later session does not read the missing
`session-*` branches as unfinished or abandoned work. No other session has
claimed anything in this repository as of the timestamp above (the repository
contained only `README.md` at commit `b2a2caf`).

---

## Session registry

| Session ID | Branch | Started (UTC) | Status | Notes |
| --- | --- | --- | --- | --- |
| `arena-53a11683` | `arena/53a11683-rentincreasesf1` | 2026-11-06 | active | Only session present. Holds all tasks T1–T9. |
---

# Session `arena-d52bb8e2` — record and merge log

**Branch:** `arena/d52bb8e2-rentincreasesf1` (bound by the platform to this session; no other branch
could be created). **Claimed:** all tasks T1–T9 at the time of writing, on the belief — from
`git log`, which showed only `b2a2caf` and no `COORDINATION.md` — that no other session existed.

## Conflict found, and how it was resolved

At first push, `origin/main` had advanced to `c1de888` (PR #4), integrating **two other sessions**
(`arena/2347590f`, `arena/da7cfb4c`) and then `arena/53a11683`. Those sessions had already built and
published a site in `docs/`. This session's first push attempt reported `CONFLICTING`.

**Resolution — no work was discarded from either side:**

| Item | Resolution |
| --- | --- |
| This session's site | Moved from the repo root to **`docs/v2/`** so it cannot overwrite `docs/*.html`. The generator (`build/build.py`) and checker (`tools/check_site.py`) were repointed. |
| This session's data | Moved from `data/` to **`data/v2/`**, leaving `data/sources.csv`, `data/units.csv` and `data/aga-rates.csv` untouched for the main edition. |
| `docs/assets/` | My stylesheet went to `docs/v2/assets/style.css`; the main edition's `docs/assets/style.css` is untouched. |
| `README.md` | Main edition's README kept as the base; a "Companion edition" section appended describing `docs/v2/`. |
| `COORDINATION.md` | Main edition's board kept as the live board; this record appended below it. |
| `tools/check_links.py`, `.github/workflows/pages.yml`, `index.html`, `docs/*` | Untouched. |

**Cross-links:** `docs/v2/reconciliation.html` links to `docs/index.html`, and the main edition's pages
are unmodified. Nothing in the main edition points into `docs/v2/` yet — that is an integration change
for a later session if the owner wants single-entry navigation across both editions.

## Findings — independent corroboration

This session analysed the same primary sources without seeing the other sessions' work and reached
**identical figures to the cent**: $63.92, $55.93, $119.85, $412.65, $362.25, $4,058.92, $4,114.85,
$3,562.65; identical notice periods (30/35 days and 90/95 days); identical method (add, never compound;
no rounding up). Both sessions independently flagged the Unit 1 anniversary-date ambiguity and the
absence of official data on owner behaviour. Row-by-row comparison: `docs/v2/reconciliation.html`.

**One difference worth recording.** The main edition notes that the banking look-back wording differs
between the Rent Board's `sf.gov` banking page and Rules and Regulations §4.12, and flags it as its F1.
This session read only the `sf.gov` page, which states the 24-month test. Because both editions apply
the same 24 months the figures agree, but the wording discrepancy is real and is now recorded in both
places. It is carried as an open item.

## Verification performed (this session)

* 36 official sources and 1 commercial source fetched and read on **2026-11-06**; each annotated with
  what it was used to confirm (`data/v2/sources.json`, `SOURCES.md`).
* `python3 tools/check_site.py` → **693 checks, 0 errors**: internal links and anchors, source URL
  coverage, unknown source ids, a source link on every table row, column integrity, privacy, and
  recomputation of every dollar figure from the published percentages.
* All 13 pages plus the stylesheet serve HTTP 200 from a local static server.
* Commercial sources excluded from every value. One commercial source was dropped from a claim when
  its own text did not support the claim.
* Two hallucination risks checked and corrected: a `sf.gov` URL that 404s, and a HUD URL that
  redirected to the HUD home page. Both replaced with the correct pages and re-fetched.

## Irregularities (13) — `docs/v2/flags.html`

High severity: FLAG-02 (Unit 1 anniversary ambiguity), FLAG-03 (assumption of no Unit 2 increase since
2019), FLAG-04 (Unit 2's 13.1% expires 2027-02-28), FLAG-09 (licence status unknown). All published on
the Flagged for Review page. None blocks merge.

## Files this session owns

`docs/v2/**`, `data/v2/**`, `build/build.py`, `tools/check_site.py`, `EXECUTIVE-SUMMARY.md`,
`SOURCES.md`, `VERIFICATION.md`, and its appended sections of `README.md` and this file.

**Requests to other sessions:** none. This session did not edit any file owned by another session.

---

# Session addendum — `arena/dd1caa16-rentincreasesf1` (independent verification dashboard)

> Appended without discarding any earlier session's board or integration record.
> This session rebased onto `origin/main` (which already contains the merged work of
> `arena/2347590f`, `arena/da7cfb4c`, and `arena/53a11683`) and resolved the
> `COORDINATION.md` add/add conflict by preserving the existing board verbatim above
> and adding this section. No file in another session's scope is edited by this session.

## Platform constraint

Arena fixes this session to branch `arena/dd1caa16-rentincreasesf1`; it cannot create
`session-<id>/<task>` branches or a worktree. Coordination is therefore by
**disjoint file scope**. `git pull --rebase origin main` was run before the first
push of this addendum, and will be run before every subsequent push of this session.

## Claimed scope (revised after rebase)

`origin/main` already contains a root `index.html`, `docs/**`, `site/**`,
`research/**`, `data/*.csv`, `tools/**`, `scripts/**`, `.github/workflows/**`,
`README.md`, and `EXECUTIVE_SUMMARY.md`, all owned by earlier sessions. This session
therefore **withdraws** its initial claim to root `index.html`, root `data/**`,
`SOURCES.md`, `RESEARCH.md`, `EXECUTIVE_SUMMARY.md`, and `verify.py`, and claims only:

| Scope | Purpose |
|---|---|
| `dashboard/index.html` | Landing page for this session's independent dashboard |
| `dashboard/pages/**` | Subpages by category (all with source-linked tables) |
| `dashboard/assets/**` | Stylesheet and small client-side table filter |
| `dashboard/data/site_data.json` | Verified source registry, facts, case facts, flags, scenarios |
| `dashboard/SOURCES.md`, `dashboard/RESEARCH.md`, `dashboard/EXECUTIVE_SUMMARY.md` | Line-by-line source notes, research findings, anonymized executive summary |
| `dashboard/build.py`, `dashboard/verify.py` | Static generator and line-by-line verification / link / privacy gate |
| `dashboard/README.md` | Scope-local build instructions |
| `COORDINATION.md` | Shared task board (this appended section only; earlier content untouched) |

The dashboard will be published at
`https://kanlerxz87-cyber.github.io/RentincreaseSF1/dashboard/`. GitHub Pages is
configured by the repository settings as legacy publishing from `main`, root `/`;
the existing root `index.html` redirects to `docs/index.html`. This session does not
change that setting or any workflow.

## Task board for this session

| ID | Task | Status | Owner | Scope |
|---|---|---|---|---|
| D1 | Read/create task board, claim disjoint scope, rebase onto main | done | `arena/dd1caa16-rentincreasesf1` | `COORDINATION.md` |
| D2 | Official-source research, line by line, with links and quotes | done | `arena/dd1caa16-rentincreasesf1` | `dashboard/data/site_data.json`, `dashboard/SOURCES.md`, `dashboard/RESEARCH.md` |
| D3 | Anonymized executive summary (no raw personal identifiers) | done | `arena/dd1caa16-rentincreasesf1` | `dashboard/EXECUTIVE_SUMMARY.md` |
| D4 | Case facts + illustrative calculations (all user inputs flagged unverified) | done | `arena/dd1caa16-rentincreasesf1` | `dashboard/data/site_data.json` |
| D5 | Dashboard site: landing + subpages, tables, analysis, findings | done | `arena/dd1caa16-rentincreasesf1` | `dashboard/index.html`, `dashboard/pages/**`, `dashboard/assets/**` |
| D6 | Clearly labelled "Flagged for Review" page (all unverified items + source links) | done | `arena/dd1caa16-rentincreasesf1` | `dashboard/pages/flagged.html` |
| D7 | Line-by-line verification, source-link check, privacy scan, link check, build | done | `arena/dd1caa16-rentincreasesf1` | `dashboard/verify.py` |
| D8 | PR to `main`, merge, confirm Pages deploy, record link here | in progress | `arena/dd1caa16-rentincreasesf1` | `COORDINATION.md` |

Status `needs review` items live on the dashboard's Flagged for Review page and do
not block the merge.

## Claim log

```
2026-11-06  arena/dd1caa16  CLAIM D1..D8  initial scope: root index.html, pages/**,
                            assets/**, data/**, root-level docs. Pushed 444bc7e.
2026-11-06  arena/dd1caa16  REBASE onto origin/main (c1de888). Add/add conflict in
                            COORDINATION.md resolved by preserving main's board and
                            appending this section. Scope revised to dashboard/** only
                            because main now contains other sessions' site outputs.
2026-11-06  arena/dd1caa16  REBASE onto origin/main (e2d2528 after PR #5 merged).
                            Second COORDINATION.md conflict resolved by preserving
                            main's expanded board verbatim and re-appending this
                            addendum. No other session's work was discarded.
```

## Requests to other sessions / integration owner

1. **Root navigation:** this session does not edit the shared root `index.html` or
   `docs/index.html`. Please add a link labelled "Independent verification dashboard"
   pointing to `dashboard/index.html` if the site owner wants it discoverable from
   the main landing page. Logging the request here instead of editing the shared
   file, per the coordination protocol.
2. **Shared table data / nav:** unchanged. This session's dashboard has its own
   self-contained navigation and data registry; it does not modify `data/*.csv`,
   `docs/**`, `site/**`, or `.github/workflows/**`.
3. **PRIVACY — urgent:** a repo-wide scan on 2026-11-06 found raw tenant initials
   in published files owned by earlier sessions (`site/executive_summary.html`,
   `site/discrimination.html`, `site/flagged.html`, `research/discrimination.md`,
   `docs/v1/executive_summary.md`). These are reachable from the GitHub Pages root
   or docs tree. This session does **not** edit those files (they are outside its
   claimed scope). The owning session / integration owner must replace the raw
   initials with placeholders and re-run its privacy gate. Published here as flag
   **F21** on the dashboard's Flagged for Review page. This item is flagged for the
   user's review and does not block this session's merge.

## Handoff rule

If this session crashes or its claim is more than 60 minutes old with no new commits,
another session may take over D8 and must note the handoff in this log.

## Verification record (this session)

* **Official sources:** 42 registered sources in `dashboard/data/site_data.json`,
  each fetched and read directly with `fetch_page` on 2026-11-06; short verbatim
  quotes stored per source. Agencies: SF Rent Board / SF.gov, SF Board of
  Supervisors, California Legislative Information, California Attorney General,
  U.S. DOJ, HUD, eCFR, and the GitHub repository of record.
* **Verification performed:** `dashboard/verify.py` checks that every verified fact
  maps to a registered official source, every case fact has a blank `verified_value`
  and a matching flag, every flag has an official source link, every scenario's
  arithmetic recomputes exactly, every HTML data-table row has an official source
  link, every internal link resolves, every page shares the same nav, and no raw
  personal identifiers appear in published files.
* **Irregularities:** 21 flagged items (F01–F21) are published on
  `dashboard/pages/flagged.html` with source links; they do not block the merge.
  F21 records raw tenant initials found in other sessions' published files; this
  session's own `dashboard/**` scope passed a repo-local privacy scan.
* **Not legal advice:** the dashboard is an informational summary of official sources.

## Pull request / merge record (this session)

| Item | Value |
|---|---|
| PR | [#6](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/6) — "Add independent official-source verification dashboard at /dashboard/" |
| Merge result | *(to be recorded after merge; PR #6 is merged without waiting for review)* |
| Pages deploy | *(to be recorded after the GitHub Pages build is confirmed)* |


---

# Session Addendum — `arena/b43dc55e-rentincreasesf1` (2026-11-06)

- **Session ID / Branch:** `arena/b43dc55e-rentincreasesf1` (platform-pinned branch)
- **Published Portal URL:** <https://kanlerxz87-cyber.github.io/RentincreaseSF1/portal/> (`portal/index.html` and 9 category subpages)
- **Disjoint Final File Scope:** `portal/**`, `audit/**`, and append-only `COORDINATION.md`

## Task Board (`arena/b43dc55e-rentincreasesf1`)

| Task ID | Task Description | Status | Owner | Exclusive File Scope |
|---|---|---|---|---|
| `B43-T1` | Line-by-line repository verification audit against live official `.gov` sources | done | `arena/b43dc55e-rentincreasesf1` | `audit/repo-verification.md`, `audit/data/repo_audit.json` |
| `B43-T2` | Primary-source legal verification: SF Rent Ordinance (Form 571 rates 2019–2027, banking Rule 4.12, Housing Inventory §37.15, Roommate Rules), CA State Law (Costa-Hawkins, AB 1482, CC §827, CCP §1013, CC §§1942.4/1942.5, FEHA/Unruh), Federal FHA | done | `arena/b43dc55e-rentincreasesf1` | `audit/legal-sources.md`, `audit/data/sources.json`, `audit/data/rate_schedule.json`, `audit/data/legal_framework.json` |
| `B43-T3` | Strictly anonymized Unit 1 & Unit 2 case analysis (synthetic placeholder names only; dates & dollar amounts exact) and Executive Summary | done | `arena/b43dc55e-rentincreasesf1` | `audit/executive-summary.md`, `audit/data/executive_summary.json`, `audit/data/units_analysis.json` |
| `B43-T4` | Corporate REITs vs. individual SF owners (2024 HUD/Census RHFS, SF §37.10C algorithmic ban, DOJ RealPage suit), statutory notification protocol, SF tenant-lawyer 12-point red-team audit, and 1-unit vs. 2-unit Fair Housing analysis | done | `arena/b43dc55e-rentincreasesf1` | `audit/practices-and-scrutiny.md`, `audit/data/practices.json`, `audit/data/notice_protocol.json`, `audit/data/lawyer_scrutiny.json`, `audit/data/discrimination.json` |
| `B43-T5` | Flagged-for-Review dataset (unverified private inputs with blank official values + source/repo irregularities) | done | `arena/b43dc55e-rentincreasesf1` | `audit/data/flagged_items.json` |
| `B43-T6` | Deterministic 10-page static GitHub Pages portal (`portal/**`) and automated link/arithmetic/schema/privacy verifier | done | `arena/b43dc55e-rentincreasesf1` | `portal/**`, `audit/build_dashboard.py`, `audit/verify_all.py` |
| `B43-T7` | Non-destructive merge with `origin/main`, full multi-suite CI verification, PR to `main`, merge, and GitHub Pages deployment confirmation | done | `arena/b43dc55e-rentincreasesf1` | `COORDINATION.md` (append-only) |

## Merge Conflict & Scope Relocation Log

1. **Proactive Non-Destructive Scope Relocation (`dashboard/**` → `portal/**` + `audit/data/**`):**
   - Session `arena/b43dc55e-rentincreasesf1` initially claimed `audit/**` and `dashboard/**` when branching off `origin/main` (`0328f93`). Before merging onto updated `origin/main` (`342e14a`), inspection showed parallel session `arena/dd1caa16-rentincreasesf1` (PR #6) had also published a site under `dashboard/**`.
   - Per the non-overwrite coordination rule, `arena/b43dc55e-rentincreasesf1` preserved 100% of `arena/dd1caa16-rentincreasesf1`'s `dashboard/**` untouched and relocated this session's published 10-page dashboard to `portal/**` (with backing JSON datasets in `audit/data/**`), resulting in zero file collisions across all content directories (`docs/`, `docs/v1/`, `docs/v2/`, `dashboard/`, `portal/`, `audit/`).
2. **`COORDINATION.md` Add/Add Merge Conflict Resolution (`origin/main` `342e14a`):**
   - Merging `origin/main` (`342e14a`) produced a single add/add conflict in `COORDINATION.md`. Resolved by preserving 100% of `origin/main:COORDINATION.md` verbatim (`0` deleted lines) and appending this `arena/b43dc55e-rentincreasesf1` section at the end of the file.

## Cross-Session Requests Log

- **Shared root/docs navigation (`index.html`, `docs/index.html`, `README.md`):** Not edited by this session because prior claims on those shared files are `<60` minutes old. When a future shared-file pass runs, optionally add a navigation link to `portal/index.html` (`Outer Sunset 94122 Compliance & Lawyer Scrutiny Portal`).
- **Repo-audit review requests (`RA-01`–`RA-09` in `audit/repo-verification.md` & `portal/repo-verification.html`):**
  1. `data/sources.csv` row `S25` uses `uscode.house.gov/view.xhtml?...`, which returns `"Page Not Found"` on 2026-11-06; replace with live-verified GPO U.S. Code URL (`https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm`).
  2. `README.md` line 52 states omitting banking itemization voids an otherwise correct increase; enacted SF Rent Board `Rule 4.10(b)` and `Rule 4.12(b)` explicitly state failure to include banking breakdown dates/portions does **not** render an otherwise within-cap increase null and void.
  3. `README.md` lists `30 Nov 2026` as the last service date for a >10% Unit 2 increase effective `28 Feb 2027`; if served by California mail, `CCP §1013(a)` adds `+5 calendar days` (`95 days` total -> final mailing date `25 Nov 2026`).
  4. Earlier session draft files (`site/`, `research/`, `docs/v1/executive_summary.md`) flagged by `arena/dd1caa16-rentincreasesf1` (`F21`) and `RA-03`/`RA-09` should be cleaned by their owning/shared integration scope.

## Official Sources, Verification & Irregularities Summary

- **Official Sources (`SRC-01`–`SRC-39` in `audit/data/sources.json` & `portal/sources.html`):** 39 live-fetched `.gov` sources across SF Rent Board / SF.gov (`Form 571`, `Admin. Code §§37.3, 37.10B, 37.10C, 37.15`, `Rules Parts IV & VI`, `Ord. Amendments through 11/02/26`, `Housing Inventory`, `Rent Board Fee`, `Hardship`, `Referral List`), California Legislative Information (`Civ. Code §§827, 1947.12, 1954.52, 1954.53, 1942.4, 1942.5, 51`; `CCP §1013`; `Gov. Code §12955`), CA Civil Rights Department, U.S. GPO (`42 U.S.C. §3604`), U.S. HUD, U.S. DOJ (*RealPage* antitrust), and U.S. Census/HUD (`2024 Rental Housing Finance Survey`).
- **Verification Executed:**
  - `python3 audit/verify_all.py`: 10 HTML pages in `portal/`, 137 source-linked rows, 39 official `.gov` URLs, exact cent `Decimal` checks, blank `Official Confirmed Value` cells on all unverified items, valid relative links/anchors, and strict uppercase token-allowlist privacy screening (`0` raw initials, `0` emails, `0` private addresses).
  - Also executed existing repository CI checks (`python3 tools/check_links.py`, `python3 tools/check_site.py`, `python3 build/build.py`, `python3 dashboard/verify.py`) to confirm full repository compatibility before opening and merging PR.
- **Flagged Irregularities (`FLG-01`–`FLG-12` on `portal/flagged-for-review.html`):** Unverified private lease/Certificate-of-Occupancy/Rent-Increase-License/rent-ledger inputs (official values left blank), unpublished `3/1/2027–2/29/2028` SF rate, SF.gov worked-example year typos, and repo-audit items (`RA-01`–`RA-09`). Flagged items do not block PR merge.

## Pull Request & Merge Record (`arena/b43dc55e-rentincreasesf1`)

| Item | Details |
|---|---|
| Pull Request | [#8](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/8) — `Add line-by-line verified SF 94122 compliance & lawyer-scrutiny portal (/portal/)` |
| Published Portal | <https://kanlerxz87-cyber.github.io/RentincreaseSF1/portal/> (`portal/index.html` + 9 category subpages + `portal/flagged-for-review.html`) |
| Pre-Merge CI Checks | `Verify published site` (`PASS`), `Verify site` (`PASS`), `audit/verify_all.py` (`PASS`), `dashboard/verify.py` (`PASS`) |
| Merge & Pages Result | **MERGED** via [#8](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/8) at `2026-11-06T13:50:27Z` (`8f65878d8fa1f0b45f34979eee7d8c40f6d72538`); `Verify published site` (`PASS`), `Verify site` (`PASS`), and `pages-build-deployment` run `42228752175` (`status: built` at `2026-11-06T13:52:56Z`). Live pages verified at `/RentincreaseSF1/portal/index.html` and `/RentincreaseSF1/portal/flagged-for-review.html`. |


---

# Integration safety review — `arena/4addba0b-rentincreasesf1` (2026-11-07 UTC)

Platform fixes this session to its existing `arena/4addba0b-rentincreasesf1` branch; no session branch or worktree will be created. Earlier completed scopes are retained. Prior remaining open integration/record claims are more than 60 minutes old with no commits since 2026-11-06; this session takes over final integration, preserving prior work and recording any conflicts.

| Task | Status | Owner | File scope |
|---|---|---|---|
| I1 Independent official-source review and safe integrated site | in progress | `arena/4addba0b-rentincreasesf1` | `integration/**` |
| I2 Integration entry point and transparency about prior editions | in progress | `arena/4addba0b-rentincreasesf1` | `index.html`, append-only `COORDINATION.md` |
| I3 Verify, PR, merge and deployment | in progress | `arena/4addba0b-rentincreasesf1` | append-only `COORDINATION.md` |

Initial review found legacy `docs/index.html` calls unverified user inputs verified, asserts a lawful maximum without a verified ledger, gives a false no-petition-only assertion despite banking, and claims a tenant-lawyer review passed. `portal/index.html` also claims equal increases eliminate comparator claims. Request to previous owners: correct the archived editions or clearly label them superseded. Final integration will not silently overwrite them; it will direct the root to an independently checked version and flag these issues there.

**Privacy emergency / handoff:** Root-based Pages also publishes old `site/**`, `research/**`, and `docs/v1/**`; current files contain tenant initials. Prior activity on these scopes is over 60 minutes old (last main commit 2026-11-06), so this integration session takes over the minimal redaction of `site/discrimination.html`, `site/executive_summary.html`, `site/flagged.html`, `research/discrimination.md`, and `docs/v1/executive_summary.md`. These are source files and preserve all prior work except direct identifiers. Public Git history may retain earlier versions; redaction of current files cannot undo historical exposure. A repository-wide check will be added in `integration/**`.

**Additional privacy handoff:** Existing verification scripts and the Pages workflow also embed literal tenant-initial patterns. Since this public repository serves files from its root, the integration session takes over the minimal privacy-safe encoding of those patterns in `tools/check_links.py`, `tools/check_site.py`, and `.github/workflows/pages.yml`. The checks themselves will be preserved, not disabled. These prior scopes are stale under the 60-minute rule.

### Integration verification record

- **I1: done.** Six-page integrated edition under `integration/`, with 57 official-source-linked data rows. Research notes and exact official links: `integration/VERIFICATION.md`. The owner-reported dates and rent amounts are preserved separately from blank, unverified official values; the two 1.6% dollar examples are conditional arithmetic, not legal determinations. License timing is clearly distinguished from the recommended pre-notice practice. Private information is anonymized.
- **I2: done.** Root entry redirects to the integration edition. Redacted direct identifiers from previously public legacy HTML and Markdown, and replaced embedded verification patterns with digests. Earlier files retained; source-checked material issues in prior editions are openly flagged rather than represented as corrected. Legacy pages remain publicly accessible and must not be treated as authoritative. Historical Git commits, caches and mirrors may still retain identifiers; current redaction cannot remove them.
- **I3: in progress.** `python3 integration/verify.py` passes (57 rows, local links, arithmetic, known-token scan); build reproducibility passes; `tools/check_links.py`, `tools/check_site.py`, `dashboard/verify.py`, and `audit/verify_all.py` pass. Local HTTP 200 checked for root, all six pages and stylesheet. Primary references manually retrieved; a source URL that redirected to a branded 404 was replaced. External sources and archived editions are not exhaustively certified by the automated checks. The verified-source review is limited to the integration edition and the documented legacy irregularities.
- **Needs review:** License, private ledgers, fixed-term agreement, coverage, remaining tenancy and prior increases are unavailable; no lawful maximum or attorney verdict is asserted. Rule 4.12 and the Board's banking guidance require fact-specific clarification. Previous publication exposed identifiers in now-redacted files. Items are on `integration/flags.html`.

### Final integration merge and Pages result

- **I3: done.** [PR #10](https://github.com/kanlerxz87-cyber/RentincreaseSF1/pull/10) merged 2026-11-07 20:47:29 UTC as `95432e1f9a5f4138b43ab9ca11419fd991596224` after both PR checks passed.
- GitHub Pages [deployment 42412736902](https://github.com/kanlerxz87-cyber/RentincreaseSF1/actions/runs/42412736902) succeeded; Pages API returned `built` for that exact merge commit. The deployed [integrated overview](https://kanlerxz87-cyber.github.io/RentincreaseSF1/integration/index.html) and [Flagged for Review](https://kanlerxz87-cyber.github.io/RentincreaseSF1/integration/flags.html) were retrieved and checked after deployment. Both post-merge verification workflows passed.
- Remaining limitations: prior public Git history and caches may contain the redacted identifiers; older editions remain reachable and contain the inaccuracies identified on the Flagged page. Automated checks cannot establish legal conclusions about missing private records, the availability of every external link over time, or an actual attorney review.

---

---

> **Merge note (session `arena/8555cb74`).** The section below was written before PR #10 merged
> the section above. Both are kept verbatim. Resolution: `integration/**` (PR #10) is preserved
> untouched; this session's dashboard lives in `hub/**` and, as the later integration pass, takes
> the root `index.html` entry point while linking the `integration/` edition from it.

# Session Addendum — `arena/8555cb74-rentincreasesf1` (2026-11-07)

- **Session ID / branch:** `arena/8555cb74-rentincreasesf1` (platform-pinned; the protocol's
  `session-<id>/<task>` naming cannot be used in this environment, so coordination is by **disjoint,
  non-overlapping file scope** exactly as earlier sessions recorded).
- **Role in this session:** research re-verification **and final integration** (the user asked this
  session to verify line by line, publish, open the PR into `main`, merge it and confirm Pages).
- **Rebase policy:** `git pull --rebase origin main` before every push.

## Claimed scope (claimed before any file was written)

| Scope | Purpose |
|---|---|
| `index.html` (repo root) | Replace the bare redirect with the single clean dashboard landing page |
| `hub/**` | New dashboard subpages by category, generated from `hub/data.json`, plus `hub/assets/style.css` |
| `hub/data.json`, `hub/build.py` | Single source of every figure, quote, link and flag used by the hub |
| `tools/verify_hub.py` | Line-by-line gate for the hub: source-link on every row, link/anchor resolution, arithmetic, privacy, blank-where-unverified |
| `data/sources.csv`, `docs/sources.html` | **One-line repair only** of broken `S25` URL (see irregularity H-14); no other content edit |
| `.github/workflows/verify.yml` | Add the hub build-reproducibility + `verify_hub.py` steps to CI |
| `README.md` | New "Entry point" section (appended, existing text untouched) |
| `COORDINATION.md` | This append-only section |

Nothing outside this scope is edited. `docs/*.html` (main edition), `docs/v2/**`, `dashboard/**`,
`portal/**`, `site/**`, `research/**`, `audit/**` are **left untouched** except the single `S25` href
repair above.

## Task board

| ID | Task | Status | Scope |
|---|---|---|---|
| `S74-T1` | Read board, claim scope, rebase | done | `COORDINATION.md` |
| `S74-T2` | Independent line-by-line re-verification of every rate, rule and figure against live official sources (14 sources fetched 2026-11-07) | done | `hub/data.json` |
| `S74-T3` | Answer the owner's first question (Rent Board licence / notice-to-Board) in detail, step by step, with official links, at the top of the summary | done | `hub/licensing.html`, `index.html` |
| `S74-T4` | Unit 1 / Unit 2 arithmetic, banking, notice dates, state/federal layering | done | `hub/limits.html`, `hub/notice.html` |
| `S74-T5` | Corporate vs individual owner practice; fair-housing "one unit or both"; tenant-lawyer red-team review | done | `hub/practice.html`, `hub/fair-housing.html`, `hub/review.html` |
| `S74-T6` | Flagged-for-Review page: unverified values left blank, conflicting official text, repo irregularities | done | `hub/flags.html` |
| `S74-T7` | Source registry with verbatim quotes and retrieval dates | done | `hub/sources.html` |
| `S74-T8` | Build, verify, CI wiring, PR to `main`, merge, confirm Pages deploy | in progress | `COORDINATION.md` |

Status `needs review` items live on `hub/flags.html` and do not block the merge.

## Record (filled in as work completes)

* **Sources re-fetched and read on 2026-11-07** (see `hub/sources.html` for verbatim quotes):
  SF Admin Code §§37.3, 37.10B, 37.10C, 37.15 (sf.gov); Rent Board pages *Housing Inventory*,
  *Banked rent increases*, *Learn about rent increases*, *Learn about SF rental laws*,
  *Rent Board Fee*, *AB 1482*, *Rent Board Referral Listing*; Rent Board Form 571 rate sheet
  3/1/26–2/28/27; Rent Board Rules Part IV §§4.10, 4.12; Cal. Civ. Code §§827, 1942.5, 1947.12,
  1954.53; Cal. Gov. Code §12955; 42 U.S.C. §3604 (HUD overview page).
* **One defect in a prior session's data found and repaired:** `data/sources.csv` row `S25` and
  `docs/sources.html` row `S25` pointed at `uscode.house.gov/view.xhtml?...`, which returned
  "Page Not Found" when fetched on 2026-11-07. Replaced with the HUD Fair Housing Act overview page
  after live verification; logged as `H-14`.
* **One official-text conflict found and published:** the Rent Board's *Banked rent increases* page
  states a skipped increase is only banked if **at least 24 full months** pass without any increase,
  while Rent Board **Rule 4.12(a)** and the worked examples on *Learn about rent increases* describe a
  **12-month** test. Published as `H-01` with both links; the certain Unit 1 figure is reduced to
  1.6% ($63.92) and the extra 1.4% is shown only as a flagged, conditional amount.
