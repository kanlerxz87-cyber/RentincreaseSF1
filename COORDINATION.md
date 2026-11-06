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
