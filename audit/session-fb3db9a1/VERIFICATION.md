# Verification Record — `arena/fb3db9a1-rentincreasesf1` (`2026-11-11` UTC)

- **Scope verified:** `handbook/**`, `audit/session-fb3db9a1/**`, append-only `COORDINATION.md` (strictly disjoint from every concurrent session claim).
- **Live sources:** 42 official sources (`HS01`–`HS42`) fetched and read on `2026-11-11` from `sf.gov`, `portal.sfrb.org`, `sftreasurer.org`, `sfgov.legistar.com`, `leginfo.legislature.ca.gov`, `www4.courts.ca.gov`, `govinfo.gov`, `hud.gov`, `justice.gov`, `census.gov`. Registry: `handbook/data/sources.json` (mirrored at `audit/session-fb3db9a1/sources_2026_11_11.json`).
- **BOS File #261020 live status on `2026-11-11`:** `Pending Committee Action` — no agenda, final action or enactment date (not law).

## Handbook verifier (`python3 handbook/verify.py`)

```text
handbook pages: 10
official sources: 42
claim-table rows with direct official links: 212
files privacy-scanned (handbook + session audit): 21
checks passed: 2111
no errors
```

Checks include: 42 unique allowlisted sources all retrieved `2026-11-11` and all cited; exact `Decimal` recomputation of all 6 scenarios (U1-A `$63.92 → $4,058.92`; U1-B `$119.85 → $4,114.85`; U2-A `$50.40 → $3,200.40`; U2-B `$412.65 → $3,562.65`; U2-C1 `$365.40 → $3,515.40`; U2-C2 `$315.00 → $3,465.00`); day-exact `§827`/`CCP §1013` service dates; every claim-table row carries a direct official-host link plus a registry link; internal links/anchors/nav resolve; all 24 flag + 8 audit-finding confirmation cells remain truly blank (`<td></td>`); unpublished 2027–28 rate remains blank; SHA-256 privacy scan (shared digests, no identifier stored/printed); `build.py` reproducibility (re-run changes nothing).

## Full repository suites on the final combined tree (after `git pull --rebase origin main`)

| Command | Result |
|---|---|
| `python3 handbook/build.py` + `python3 handbook/verify.py` | PASS — 2,111 checks, 212 source-linked rows, 0 errors |
| `python3 tools/verify_hub.py` | PASS — 1,627 checks, 33/33 sources, 211 cited rows, 0 errors |
| `python3 tools/verify_assurance.py` | PASS — 1,902 checks, 39 assurance rows, 33/33 manifest, 245 text files privacy-scanned, 0 errors |
| `python3 tools/check_links.py` | PASS — 10 published (+7 archived) pages, links/anchors/CSVs/citations/privacy OK |
| `python3 tools/check_site.py` | PASS — 781 checks, 0 errors |
| `python3 integration/verify.py` | PASS — 6 pages, 57 source-linked rows |
| `python3 dashboard/verify.py` | PASS — 42 sources, 67 verified facts, 21 flagged items, 12 pages |
| `python3 audit/verify_all.py` | PASS — 10 pages, 137 source-linked rows, 39 official `.gov` URLs |
| `python3 review/verify.py` | PASS — 11 pages, 14 sources; U1 `$63.92`, U2 `$50.40`, U2 banked+current `13.1% = $412.65` recomputed |
| `python3 guide/verify.py` | PASS — 1,060 checks, 174 source-linked rows, 33 sources, 0 errors |
| `python3 compliance/verify.py` | PASS — 3,277 checks, 235 source-linked rows, 37 sources, 0 errors |
| `python3 hub/build.py && python3 assurance/build.py && python3 build/build.py` | Reproducible — `git status` clean afterwards (matches CI regeneration gates) |
| Local preview `python3 -m http.server 8000` | `GET /handbook/`, `/handbook/flagged-for-review.html`, `/handbook/sources.html` → HTTP 200 |

## Audit corrections made during verification

- `RA-FB3-01` (trailing-dot statute URLs) was **withdrawn**: a precise query-value check found zero trailing-dot `sectionNum` values on current `main`; the initial loose-regex hit matched sentence punctuation. Recorded in `REPO_AUDIT.md` so no session fixes a non-defect.
- `FL-18` was replaced (fee payment/exemption status per unit) so the flagged list contains only genuinely unverified items; flag count remains 24.
- `RA-FB3-05` was narrowed to the two primaries still absent as direct canonical registry entries (`Civ. Code §1942.4`, Topic 363), now supplied as handbook `HS30`/`HS32`.

## Privacy

Zero personal identifiers in `handbook/**`, `audit/session-fb3db9a1/**`, commit messages or PR metadata. Placeholders only (`Placeholder Tenant 1A`–`1D`, `2A`–`2B`); dates/dollars exactly as supplied. Pre-redaction Git history (`FL-24`/`RA-FB3-08`) is disclosed without reproducing any identifier and without linking to historical revisions.
