# COORDINATION.md — shared task board

Session ID for this board: `arena-0acf08c3`

## Platform constraint (read first)

Arena pins this session to the single branch `arena/0acf08c3-rentincreasesf1`; it cannot create,
switch to, push, or merge from `session-<id>/<task>` branches. Therefore **branch-based isolation is
not available here**. Isolation is instead enforced with **non-overlapping file scopes** listed below,
plus small frequent commits, `git pull --rebase` before every push, and conflict-preserving rebases.
The integration step is performed on the same branch as the final task in this session, and the PR is
opened from `arena/0acf08c3-rentincreasesf1` into `main`.

Only one session is present on this board at this time. No task has been claimed by another session.

## Tasks

| Task | Status | Owner session | File scope |
| --- | --- | --- | --- |
| T0 Coordination board | done | arena-0acf08c3 | `COORDINATION.md` (owned by this session only; other sessions append via the log below) |
| T1 Legal research / verified source registry | in progress | arena-0acf08c3 | `research/*`, `sources/*` (research notes and source registry draft only; **no final shared table data**) |
| T2 Anonymized unit & tenancy input notes | unclaimed | arena-0acf08c3 | `research/unit-notes/*` (owner-supplied facts, placeholder mapping, privacy notes) |
| T3 Site framework (templates, styles, build tools) | unclaimed | arena-0acf08c3 | `assets/*`, `tools/*`, `templates/*` (no root `index.html`, no navigation, no final shared table data) |
| T4 Verification draft & Flagged for Review draft | unclaimed | arena-0acf08c3 | `research/verification-draft/*` (no root `flagged.html`) |
| T5 Final integration, build/link check, Pages enable, PR + merge | unclaimed | arena-0acf08c3 | `data/*.json`, root `*.html`, `.nojekyll`, `README.md`, `EXECUTIVE_SUMMARY.md`, `research/SOURCES.md`, `research/VERIFICATION.md`, `.github/workflows/*`, `COORDINATION.md` (shared outputs: table data, index, navigation, flagged page) |

Rules: never start a task another session has claimed; if a task requires changing another session's
file, log the request in the handoff log instead of editing it. Shared outputs (table data, index,
navigation, final Flagged for Review page) are touched **only by the final integration session (T5)**.
A `needs review` item is published on the site's **Flagged for Review** page and does not block anything.
Stale claims (>60 min, no commits) may be taken over with a handoff note.

## Handoff / conflict log

- (none yet)

## Completion records (sources used, verification performed, irregularities)

- (none yet)
