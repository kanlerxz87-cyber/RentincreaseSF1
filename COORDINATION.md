# Coordination — San Francisco rent increase research

## Session and branch constraints

- Active session: `arena-832c7b0c`.
- Arena fixes this session to `arena/832c7b0c-rentincreasesf1`. Work, commits, pushes, and the pull request must use this branch; separate `session-*` or integration branches are not permitted by the hosting environment.
- The logical tasks below have non-overlapping file scopes. This session will perform final integration only after the research and site tasks are done. Re-read this board before each task and before publishing shared outputs.
- Status vocabulary: unclaimed / in progress / done / needs review. Published review items do not block integration.
- Never place identifying tenant information in tracked files or the public website. Use neutral unit and resident aliases publicly. Private supplied terms are not official-source verification.

## Task board

| Task | Status | Owner | Files exclusively owned by this task |
| --- | --- | --- | --- |
| R1 — Official-source legal and market-practice research | done | arena-832c7b0c | `research/**`, `sources/**` |
| R2 — Privacy-preserving case assessment and executive summary | in progress | arena-832c7b0c | `analysis/**`, `private/**` (local-only, ignored) |
| S1 — Static dashboard, category pages, anonymized public data, tests | in progress | arena-832c7b0c | `site/**`, `tests/**`, `scripts/**`, `package.json`, `package-lock.json`, `.gitignore` |
| I1 — Final integration, shared index/navigation/data, PR, merge, Pages deployment | unclaimed | — | `README.md`, `.github/workflows/**`, `COORDINATION.md`, generated shared outputs; publication of `site/**` only after R1/R2/S1 completion |

## Change requests

None.

## Work log

- Initial repository review: only `README.md` (one heading) exists; no existing application, data, research, workflows, or coordination board. No prior implementation to verify.
- Created this board and claimed R1 before starting source research. No tenant identifiers recorded.
- Verification standard: legal/rate claims require official government or primary statutory sources. Private lease amounts and coverage cannot be confirmed without authoritative records; do not infer them. Calculations, if used, must be explicitly conditional and must not populate verified-value fields.
- R1 completed: saved 33 official-source entries and a scoped legal/market synthesis. Verified the 1.6% local interval, state/local interaction, notice/service, banking mechanics, retaliation/fair housing, petition routes, algorithm restrictions, and FY 2027 metropolitan benchmarks. The November 2, 2026 amendment list was checked for relevant rent-limitation changes.
- R1 unresolved items remain published flags: exact coverage/address/APN, current lawful rents, banking history, inventory/license, exemptions/subsidy, owner form, bedrooms/utilities, FY 2027 ZIP SAFMRs, and actual attorney review. HUD's accessible ZIP service is FY 2026 and is labeled historical; no current ZIP value was inferred.
- Claimed R2 and S1 sequentially after R1 completion; scopes do not overlap. S1 will first establish local-only privacy ignores before R2 writes private intake. S1 tests may build only into ignored `.tmp/`; shared navigation/index/public output is reserved for I1 after R1/R2/S1 completion.
