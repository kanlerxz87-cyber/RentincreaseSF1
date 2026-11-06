# COORDINATION.md — Shared Task Board

**Repository:** `kanlerxz87-cyber/RentincreaseSF1`
**Purpose:** Rental-increase research, verification, and GitHub Pages site for two rent-controlled units in San Francisco 94122.
**Board last updated:** 2026-11-06 (UTC)

## Platform constraints (deviation log)

- This Arena session is **pinned** to branch `arena/2e94d96a-rentincreasesf1`. Platform policy forbids creating, switching to, or pushing any other branch, so the requested `session-<id>/<task>` branches and the "merge the branches" step **cannot be executed literally**. Logged here for transparency.
- Mitigation: a **single integration session** (`session-2e94d96a`) performs all tasks with **strictly non-overlapping file scopes** listed below; all changes are committed to the pinned branch in small, frequent commits; `git pull --rebase` is run before every push.
- `COORDINATION.md` itself is the shared task board and is the only file exempt from scope exclusivity (used for claims, handoffs, and the final log).
- Shared outputs (table data, site index/navigation) are owned by this session **in its capacity as the final integration session**, and are re-verified line by line before publication.
- No other session claims were present when this board was created (repo contained only `README.md`; `git fetch --all` showed only `main` and this branch). Any session reading this board later must not re-claim tasks marked `in progress` or `done`.

## Session registry

| Session ID | Branch | Role | Started |
| --- | --- | --- | --- |
| `session-2e94d96a` | `arena/2e94d96a-rentincreasesf1` | Research + site build + final integration | 2026-11-06 |

## Task board

Status values: `unclaimed` / `in progress` / `done` / `needs review`.
`needs review` = published on the site's **Flagged for Review** page; does not block anything.

| Task | Description | Status | Owner | File scope (exclusive) |
| --- | --- | --- | --- | --- |
| T01 | Create board; audit repo contents line by line | in progress | session-2e94d96a | `COORDINATION.md`, `README.md`, `pages/repo-audit.html` |
| T02 | SF local rent-control law, rates, coverage, notices | in progress | session-2e94d96a | `data/sf-local.json`, `pages/law-local.html` |
| T03 | California state law (AB 1482, CC 827, Costa-Hawkins) | in progress | session-2e94d96a | `data/ca-state.json`, `pages/law-state.html` |
| T04 | Federal law, fair housing, free tenant counsel | in progress | session-2e94d96a | `data/federal.json`, `pages/law-federal.html` |
| T05 | Practice: large corporations vs individual owners; notice procedure; reasonable reasons | in progress | session-2e94d96a | `data/practice.json`, `pages/practice.html` |
| T06 | Anonymized unit facts, calculations, one-unit vs both-units discrimination analysis | in progress | session-2e94d96a | `data/units.json`, `pages/units.html` |
| T07 | Executive summary | in progress | session-2e94d96a | `pages/summary.html` |
| T08 | Flagged for Review page + unverified/irregularity register | in progress | session-2e94d96a | `data/flags.json`, `pages/flagged.html` |
| T09 | Site shell: landing page, navigation, styles, assets | in progress | session-2e94d96a | `index.html`, `assets/*`, `.nojekyll` |
| T10 | Verification + broken-link + build scripts, CI workflow | in progress | session-2e94d96a | `scripts/*`, `.github/workflows/*`, `data/sources.json` |
| T11 | Final integration: re-verify combined data, build, PR, merge, confirm Pages deploy | unclaimed (starts after T01–T10) | session-2e94d96a | `COORDINATION.md` (log only) |

## Privacy rule (applies to every task)

Real tenant names and personal details are **internal only** and must never appear in this repo, the site, commits, or PR text. All site content uses placeholder identifiers (Tenant A, Tenant B, …). Dates and dollar amounts are reproduced exactly as supplied. No addresses beyond ZIP 94122 and neighborhood (Outer Sunset). See `pages/privacy.html` for the public-facing note.

## Verification rule (applies to every task)

- Every table row on the site carries a clickable source link to an **official** source (`.gov`, `leginfo.legislature.ca.gov`, `courts.ca.gov`, `hud.gov`, `bls.gov`, `sf.gov`, `sfrentboard.org`, or official government PDFs).
- If a value cannot be confirmed against an official source, the cell is **left blank** and the item is flagged `UNVERIFIED` on the Flagged for Review page.
- No value is inferred or filled in. Calculations from official rates are labeled as "calculated" and show the official rate source plus the arithmetic.
- "Do not mark anything verified without checking it against an official source, and link that source."

## Handoff / conflict log

| Date (UTC) | Event | Action |
| --- | --- | --- |
| 2026-11-06 | Board created. Repo contained only `README.md` (`# RentincreaseSF1`). No pre-existing data, code, or site to audit; no pre-existing claims. | Recorded as irregularity F-01 (empty repo / no prior findings to verify). |
| 2026-11-06 | Platform pins branch; `session-<id>/<task>` branches not possible. | Logged under "Platform constraints" above. |

## Per-task completion record (sources, verification, irregularities)

_Filled in as each task completes. See also `data/sources.json` for the canonical source register._

- T01 — pending
- T02 — pending
- T03 — pending
- T04 — pending
- T05 — pending
- T06 — pending
- T07 — pending
- T08 — pending
- T09 — pending
- T10 — pending
- T11 — pending

## Pull request / merge / deploy record

- PR: _pending_
- Merge result: _pending_
- GitHub Pages deployment: _pending_ (`https://kanlerxz87-cyber.github.io/RentincreaseSF1/`)
