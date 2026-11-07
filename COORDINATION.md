# COORDINATION.md — Shared Task Board (Update 2026-11-07)

This file is the shared task board for multi-session work on this repository.
Read it before starting any task. Claim a task by writing your session ID and
file scope below, then commit and push the claim immediately.

**Last updated:** 2026-11-07 (UTC)
**Repo:** `kanlerxz87-cyber/RentincreaseSF1`
**Default/published branch:** `main`  **GitHub Pages source:** `main` → `/docs`

---

## Environment constraint on branch naming (read this first)

The task protocol asks each session to work on its own branch named
`session-<id>/<task>`. In this environment the working session is bound by the
platform to the branch **`arena/30f3000e-rentincreasesf1`**, and the session is
not permitted to create, switch to, or push any other branch. This session
therefore:

* works only on `arena/30f3000e-rentincreasesf1`;
* records its file scope in this board **before** writing those files;
* opens the integration pull request **from** `arena/30f3000e-rentincreasesf1`
  **into** `main`;
* runs `git pull --rebase origin main` before every push.

---

## Session registry

| Session ID | Branch | Started (UTC) | Status | Notes |
| --- | --- | --- | --- | --- |
| `arena-53a11683` | `arena/53a11683-rentincreasesf1` | 2026-11-06 | active | Only session present. Holds all tasks T1–T9. |
| `arena-d52bb8e2` | `arena/d52bb8e2-rentincreasesf1` | 2026-11-06 | merged | Companion edition v2. PR #6 merged. |
| `arena-b43dc55e` | `arena/b43dc55e-rentincreasesf1` | 2026-11-06 | merged | Portal edition. PR #8 merged. |
| `arena-30f3000e` | `arena/30f3000e-rentincreasesf1` | 2026-11-07 | active | **Current session.** Focus: Executive summary update (forefront Rent Board license/notification process), anonymized unit details, verified reasonable increases, corporate vs individual handling, notification/reasons, lawyer scrutiny, discrimination analysis, and site integration verification. Scope: `EXECUTIVE-SUMMARY.md`, coordination log append. |

---

## Session Addendum — `arena/30f3000e-rentincreasesf1` (2026-11-07)

- **Session ID / Branch:** `arena/30f3000e-rentincreasesf1` (platform-pinned branch)
- **Published Site Reference:** https://kanlerxz87-cyber.github.io/RentincreaseSF1/ (Main edition `docs/index.html` and `portal/index.html` already live from prior sessions)
- **Disjoint Final File Scope:** `EXECUTIVE-SUMMARY.md` (root), append-only `COORDINATION.md`

## Task Board (`arena/30f3000e-rentincreasesf1`)

| ID | Task | Status | Owner | Exclusive File Scope |
|---|---|---|---|---|
| `30F-T1` | Research and understand Rent Board license/notification process for individual owner (Forefront of Executive Summary) | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T2` | Anonymize personal info (internal only) and preserve dates/amounts | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T3` | Verify reasonable/normal increases (Local/State/Federal) with official links | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T4` | Corporate vs Individual owner handling analysis | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T5` | Correct notification method and reasonable reasons | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T6` | Scrutiny by SF tenant advocates/lawyers (12-point test) | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T7` | Discrimination analysis: One unit vs Both units | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T8` | Line-by-line verification and link to official sources | done | `arena/30f3000e-rentincreasesf1` | `EXECUTIVE-SUMMARY.md` |
| `30F-T9` | Site creation/integration check (landing page, subpages, dashboard) | done | `arena/30f3000e-rentincreasesf1` | N/A (existing `docs/`, `portal/`, `dashboard/` untouched) |
| `30F-T10` | Record PR/Merge and Flagged for Review page update | in progress | `arena/30f3000e-rentincreasesf1` | `COORDINATION.md` |

## Verification performed (this session)

* **Official sources:** SF Rent Board (.gov) [1](https://www.sf.gov/rent-board-housing-inventory) [4](https://www.sf.gov/learn-about-rent-increases-san-francisco/), CA Legislature (.gov), U.S. GPO (.gov) [42 U.S.C. §3604](https://www.govinfo.gov/content/pkg/USCODE-2023-title42/html/USCODE-2023-title42-chap45-subchapI-sec3604.htm).
* **Privacy:** All personal identifiers in `EXECUTIVE-SUMMARY.md` replaced with placeholders (Tenant A–D). Dates and amounts preserved.
* **Forefront Process:** Confirmed individual owner must report to Housing Inventory → receive automatic license → notify tenants (Step-by-step with links) [2](https://www.bancalsf.com/sf-rent-board-housing-inventory) [4](https://www.sf.gov/rent-board-housing-inventory) [6](https://www.sf.gov/learn-about-rent-increases-san-francisco/).
* **Site Integration:** Verified existing `docs/index.html` (Main edition), `portal/index.html` (Portal edition), and `dashboard/index.html` (Independent edition) are live and link to official sources. No conflict with current branch scope.

## Irregularities (Updated)

* **FLAG-02:** Unit 1 anniversary ambiguity (Feb 1 vs Apr 1) [EXECUTIVE-SUMMARY.md].
* **FLAG-03:** Unit 2 increase assumption since 2019 [EXECUTIVE-SUMMARY.md].
* **FLAG-04:** Unit 2 13.1% expiration Feb 28, 2027 [EXECUTIVE-SUMMARY.md].
* **FLAG-09:** License status unknown [EXECUTIVE-SUMMARY.md].
* **FLAG-21:** Raw initials in other session files (Internal scan) [COORDINATION.md].

## Pull Request / Merge Record (`arena/30f3000e-rentincreasesf1`)

| Item | Details |
|---|---|
| PR | **Pending** — "Update EXECUTIVE-SUMMARY.md with forefront Rent Board license/notification process, anonymized unit details, verified reasonable increases, corporate vs individual handling, notification/reasons, lawyer scrutiny, discrimination analysis, and site integration status" |
| Merge result | **Pending** (Will merge after verification) |
| Pages deploy | **Confirmed** (Existing sites `docs/`, `portal/`, `dashboard/` already deployed and verified in previous sessions) |

---

## Requests to other sessions / integration owner

1. **Executive Summary Update:** The root `EXECUTIVE-SUMMARY.md` has been updated with the forefront Rent Board license/notification process and all requested analysis.
2. **Site Verification:** The existing site (`docs/index.html`, `portal/index.html`, `dashboard/index.html`) already contains the categorized subpages and table formats requested. No new files were needed to avoid collisions; existing verified links were preserved.
3. **Flagged for Review:** All irregularities (FLAG-02, FLAG-03, FLAG-04, FLAG-09, FLAG-21) are recorded in `EXECUTIVE-SUMMARY.md` and the coordination log.

## Claim log

```
2026-11-07  arena/30f3000e  CLAIM T1..T10  scope: EXECUTIVE-SUMMARY.md, COORDINATION.md append. Pushed efe08ca.
```
