# Session `arena-4329d908` — audit record (11 November 2026)

| File | What it is |
| --- | --- |
| `VERIFICATION.md` | The official pages opened on 2026-11-11, the passage read on each, and whether the dashboard's quotation matches |
| `FINDINGS.md` | Irregularities, each with its official link and whether it was fixed here or requested from the canonical holder |
| `census.py` | Read-only row census of every HTML page GitHub Pages serves: direct official link, indirect link, or none |

## What this session changed

Only the superseded editions and the tooling that guards them (scope recorded in `COORDINATION.md`):

* `tools/legacy_notice.py` — writes the "superseded edition" notice, the `noindex` tag and the direct
  official links; replaces the commercially sourced draft with withdrawal notices; `--check` mode.
* Each archived edition's generator calls it as its last step, so a rebuild reproduces the pages.
* `tools/check_links.py`, which CI already runs, now fails if an archived page loses its notice.

The canonical dashboard (`index.html`, `hub/`, `assurance/`, root Markdown) was **not** edited.

## Reproduce

```
python3 tools/legacy_notice.py --apply      # no file changes on a clean tree
python3 tools/legacy_notice.py --check
python3 audit/session-4329d908/census.py
python3 tools/check_links.py && python3 build/build.py && python3 tools/check_site.py
python3 integration/verify.py && python3 dashboard/verify.py && python3 audit/verify_all.py
python3 review/verify.py && python3 guide/verify.py && python3 compliance/verify.py
```

## Census, before and after

| Edition | Pages | Notice before → after | Rows | Direct official link before → after |
| --- | --- | --- | --- | --- |
| `docs/` | 10 | 0 → 10 | 225 | 31 → 225 |
| `docs/v1/` | 7 | 0 → 7 | 66 | 66 → 66 |
| `docs/v2/` | 13 | 0 → 13 | 220 | 193 → 202 (+18 repository-record rows) |
| `dashboard/` | 12 | 0 → 12 | 269 | 260 → 260 (+9 repository-record rows) |
| `portal/` | 10 | 0 → 10 | 137 | 137 → 137 |
| `review/` | 11 | 0 → 11 | 95 | 79 → 95 |
| `integration/` | 6 | 0 → 6 | 57 | 57 → 57 |
| `guide/` | 10 | 0 → 10 | 174 | 174 → 174 |
| `compliance/` | 10 | 0 → 10 | 235 | 235 → 235 |
| `site/` | 7 | withdrawn | 17 → 0 | commercial citations only → none |

## Limits

* A link to an official rule beside an owner-supplied figure is context. It does not verify the figure.
* The archived editions were marked, not re-certified. Their analysis was not re-read line by line.
* Nothing here changes Git history. Earlier revisions of the withdrawn files remain in history.
