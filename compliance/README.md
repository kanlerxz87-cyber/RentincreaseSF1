# `/compliance/` — San Francisco Rent Increase Compliance & Verification Suite

Published at **`https://kanlerxz87-cyber.github.io/RentincreaseSF1/compliance/`** alongside the canonical root dashboard (`../index.html`).

## Key Capabilities & Verification Standards

- **Forefront Individual-Owner Rent Board License Guide:** Explains step-by-step why a non-corporate owner of a reported 2-unit 1940 building in Outer Sunset (`94122`) must report annually on `portal.sfrb.org` to generate a free Rent Increase License (`SF Admin. Code §37.15`), why completing reporting before serving notice prevents suspension challenges, and how the license differs from the `$59.00` Rent Board Fee and the SF Treasurer `<4-unit` Business Registration Certificate carve-out.
- **37/37 Official Government Sources Live-Verified (`2026-11-10`):** Every statute, regulation, rate sheet (`Form 571`), agency guide, pending bill (`BOS File No. 261020` + `Legislative Digest Ver. 1` + `Nov. 9, 2026` Rent Board warning), and statistical survey (`2024 HUD/Census RHFS`) was fetched and read directly from its official publisher on `2026-11-10`.
- **100% Row-Level Official Source Links:** Every `<tbody><tr>` across all 10 HTML pages carries a direct `https://` official `.gov`/City-portal link and a `[CSxx]` source-registry anchor.
- **Zero-Hallucination Blank Cells:** All 16 unverified private case inputs and unconfirmed official benchmarks (`CF-01`–`CF-16`) leave their *Official Confirmed Value* cells physically blank (`<td></td>`) and flagged on [`flagged.html`](flagged.html).
- **100% Anonymized:** Uses synthetic placeholders (`Placeholder Tenant 1A`–`1D`, `Placeholder Tenant 2A`–`2B`) only; verified by SHA-256 digest and regex privacy gates.

## Files in This Scope

| File | Role |
|---|---|
| [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) | Standalone Markdown Executive Summary with beginner licensing checklist and scenario tables |
| [`data/sources.json`](data/sources.json) | 37 live-verified (`2026-11-10`) official government sources with verbatim excerpts |
| [`data/site_data.json`](data/site_data.json) | Anonymized scenario inputs, conditional math, and 46-period Form 571 table |
| [`data/repo_audit.json`](data/repo_audit.json) | Line-by-line repository & official-source audit records (`RA-BA23-01`–`RA-BA23-10`) |
| [`build.py`](build.py) | Deterministic static HTML generator (`0` dynamic date stamps; byte-idempotent) |
| [`verify.py`](verify.py) | Automated reproducibility, link/anchor, row-citation, blank-cell, dual `Decimal`/`Fraction` math, and SHA-256 privacy verifier |
| `index.html` + 9 subpages | Generated dashboard HTML served by GitHub Pages under `/compliance/` |

## Regenerate & Verify

```bash
PYTHONDONTWRITEBYTECODE=1 python3 compliance/build.py
PYTHONDONTWRITEBYTECODE=1 python3 compliance/verify.py
```
