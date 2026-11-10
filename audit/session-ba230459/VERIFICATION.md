# Verification Record — `arena/ba230459-rentincreasesf1` (`2026-11-10 UTC`)

## 1. Scope & Disjoint Parallel-Session Discipline

- **Session ID / Branch:** `arena-ba230459` / `arena/ba230459-rentincreasesf1` (platform-pinned branch).
- **Exclusive file scope:** `compliance/**`, `audit/session-ba230459/**`, and append-only `COORDINATION.md`.
- **Zero interference with concurrent claims:** `index.html`, `hub/**`, `assurance/**`, `audit/final-integration/**`, `tools/**`, `.github/workflows/**`, `README.md`, `EXECUTIVE_SUMMARY.md`, `SOURCES.md`, `VERIFICATION.md`, and all preserved archive directories remain untouched.

## 2. Automated Verification Suites Executed (`2026-11-10`)

| Suite / Command | Scope Verified | Result |
|---|---|---|
| `python3 compliance/build.py` | Deterministic generation of 10 `/compliance/*.html` pages | **PASS** (byte-idempotent on re-run) |
| `python3 compliance/verify.py` | **3,275+ checks**: build idempotency, 235/235 table rows with direct official `.gov`/City-portal links + resolving `#CSxx` anchors, 16/16 empty `<td></td>` unconfirmed cells on `index.html` & `flagged.html`, dual `Decimal` + `Fraction` scenario math, `datetime.date` service deadlines, 46-row Form 571 parity with `hub/data.json`, Markdown/HTML link resolution, and SHA-256 + regex privacy gate | **PASS — 0 errors** |
| `python3 tools/verify_hub.py` | Canonical root & `hub/` verification gate (`assurance.yml` & `verify.yml`) | **PASS — 0 errors** |
| `python3 tools/verify_assurance.py` | Assurance layer + repo-wide SHA-256 privacy scan across all tracked text files (`assurance.yml`) | **PASS — 0 errors** |
| `python3 tools/check_links.py` | Repo-wide link/privacy gate (`pages.yml`) | **PASS — 0 errors** |
| `python3 build/build.py` + `python3 tools/check_site.py` | Companion site reproducibility & 781 checks (`verify.yml` & `pages.yml`) | **PASS — 0 errors** |
| `python3 integration/verify.py` | Preserved integration suite (`pages.yml`) | **PASS — 0 errors** |
| `python3 dashboard/verify.py` | Preserved dashboard suite | **PASS — 0 errors** |
| `python3 audit/verify_all.py` | Preserved audit suite | **PASS — 0 errors** |
| `python3 review/verify.py` | Preserved review suite | **PASS — 0 errors** |

## 3. Verified Conditional Arithmetic & Service Deadlines

| Scenario | Scenario Base Input | Additive Rate | Exact Monthly Increase | Illustrative New Base Rent | Illustrative Effective Date | Personal Service (`§827`) | CA Mail Service (`§827` + `CCP §1013(a)`) |
|---|---:|---:|---:|---:|---|---|---|
| `U1-A` (Unit 1 Annual Only) | `$3,995.00` | `1.6%` | `+$63.92` | `$4,058.92` | `2027-02-01` | `<= 2027-01-02` (`30d`) | `<= 2026-12-28` (`35d`) |
| `U1-B` (Unit 1 Annual + 1 Yr Banked) | `$3,995.00` | `1.6% + 1.4% = 3.0%` | `+$119.85` | `$4,114.85` | `2027-02-01` | `<= 2027-01-02` (`30d`) | `<= 2026-12-28` (`35d`) |
| `U2-A` (Unit 2 Annual Only) | `$3,150.00` | `1.6%` | `+$50.40` | `$3,200.40` | `2027-02-28` | `<= 2027-01-29` (`30d`) | `<= 2027-01-24` (`35d`) |
| `U2-B` (Unit 2 Enacted-Law Full Catch-Up) | `$3,150.00` | `1.6% + 11.5% = 13.1%` | `+$412.65` | `$3,562.65` | `2027-02-28` | `<= 2026-11-30` (`90d`) | `<= 2026-11-25` (`95d`) |
| `U2-C` (Unit 2 File #261020 Risk-Mitigated Partial Banked) | `$3,150.00` | `1.6% + 10.0% = 11.6%` (`1.5%` retained) | `+$365.40` | `$3,515.40` | `2027-02-28` | `<= 2026-11-30` (`90d`) | `<= 2026-11-25` (`95d`) |
