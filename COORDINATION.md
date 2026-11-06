# COORDINATION.md — shared task board

Session ID for this board: `arena-0acf08c3`

## Platform constraint (read first)

Arena pins this session to the single branch `arena/0acf08c3-rentincreasesf1`; it cannot create,
switch to, push, or merge from `session-<id>/<task>` branches. Therefore **branch-based isolation is
not available here**. Isolation is instead enforced with **non-overlapping file scopes** listed below,
plus small frequent commits, `git pull --rebase` before every push, and conflict-preserving rebases.
The integration step is performed on the same branch as the final task in this session, and the PR is
opened from `arena/0acf08c3-rentincreasesf1` into `main`.

## Tasks

| Task | Status | Owner session | File scope |
| --- | --- | --- | --- |
| T0 Coordination board | done | arena-0acf08c3 | `COORDINATION.md` (owned by this session only; other sessions append via the log below) |
| T1 Legal research / verified source dataset | in progress | arena-0acf08c3 | `research/*`, `data/*.json`, `sources/*` |
| T2 Anonymized unit & tenancy data | unclaimed | arena-0acf08c3 | `data/units.json`, `data/privacy.md` |
| T3 Site build (landing + category subpages, tables) | unclaimed | arena-0acf08c3 | `site/*`, `docs/*` |
| T4 Line-by-line verification + Flagged for Review page | unclaimed | arena-0acf08c3 | `site/flagged.html`, `data/verification.json` |
| T5 Final integration, build/link check, Pages enable, PR + merge | unclaimed | arena-0acf08c3 | `COORDINATION.md`, `.github/workflows/*`, `README.md` |

Rules: never start a task another session has claimed; if a task requires changing another session's
file, log the request in the handoff log instead of editing it. Shared outputs (table data, index,
navigation) are touched only by the final integration session. A `needs review` item is published on
the site's **Flagged for Review** page and does not block anything. Stale claims (>60 min, no commits)
may be taken over with a handoff note.

## Handoff / conflict log

- (none yet)

## Completion records (sources used, verification performed, irregularities)

- (none yet)
