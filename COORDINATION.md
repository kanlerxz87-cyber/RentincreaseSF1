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
