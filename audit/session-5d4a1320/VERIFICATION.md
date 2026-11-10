# Verification Record — Session `arena/5d4a1320-rentincreasesf1`

- **Verification Date:** `2026-11-10` (UTC)
- **Published Dashboard Path:** `/guide/` (<https://kanlerxz87-cyber.github.io/RentincreaseSF1/guide/>)
- **Audit & Data Artifacts:** `audit/session-5d4a1320/{sources.json, site_data.json, EXECUTIVE_SUMMARY.md, REPO_AUDIT.md, SOURCES.md, VERIFICATION.md}`
- **Deterministic Build & Verifier:** `guide/build.py` + `guide/verify.py`

---

## 1. Line-by-Line Verification Gates Executed

| Gate | Scope | Result | Details |
|---|---|---|---|
| **Live Official-Source Retrieval** | `audit/session-5d4a1320/sources.json` (`GS-01`–`GS-33`) | **PASS (`33 / 33`)** | All 33 primary official sources (`sf.gov`, `portal.sfrb.org`, `sftreasurer.org`, `sfgov.legistar.com`, `leginfo.legislature.ca.gov`, `www4.courts.ca.gov`, `govinfo.gov`, `hud.gov`, `justice.gov`, `census.gov`) were fetched and read live on `2026-11-10` with verbatim passages stored in `sources.json`. |
| **Source Link on Every Table Row** | `guide/*.html` (`10` pages) | **PASS (`174 / 174` rows)** | Every `<tbody><tr>` row across all 10 HTML pages in `guide/` carries a direct clickable HTTPS link to a registered official government URL plus an anchor link to its verbatim quote on `guide/sources.html`. |
| **Strict Blank-Cell Enforcement** | `guide/flagged-for-review.html`, `guide/index.html`, `guide/units-and-rates.html` | **PASS (`23 / 23` blank cells)** | All 15 unverified items on `flagged-for-review.html`, the 7 high-priority gate rows on `index.html`, and the unpublished `2027–2028` `Form 571` row on `units-and-rates.html` render `<td class="blank-official"></td>` (`0` characters — zero inferred values). |
| **Exact Rational & Calendar Arithmetic** | `U1-A`, `U1-B`, `U2-A`, `U2-B`, `U2-C` + 6-year Unit 2 banking | **PASS (Exact to `$0.01`)** | Independently recomputed via Python `fractions.Fraction` and `datetime.timedelta`: Unit 1 (`$3,995 × 1.6% = $63.92 -> $4,058.92`; `3.0% = $119.85 -> $4,114.85`); Unit 2 (`$3,150 × 1.6% = $50.40 -> $3,200.40`; `11.6% = $365.40 -> $3,515.40`; `13.1% = $412.65 -> $3,562.65`); `30/35/90/95` calendar-day service cutoffs verified exact. |
| **Internal Links, Assets, Anchors & Nav** | `guide/**` + `audit/session-5d4a1320/*.md` | **PASS (`0` broken links)** | All 10 HTML pages share identical 10-entry navigation; every relative `href`, `src`, and `#anchor` resolves cleanly. |
| **Deterministic Rebuild Reproducibility** | `python3 guide/build.py` | **PASS (`0` byte diff)** | Re-running `guide/build.py` produces byte-for-byte identical HTML and Markdown outputs with zero system-clock drift. |
| **Privacy & Anonymization Scan** | `guide/**`, `audit/session-5d4a1320/**`, and full repo (`190` text files) | **PASS (`0` personal tokens)** | Scanned against SHA-256 `FORBIDDEN_HASHES` (raw + HTML-stripped text) and email regexes; only neutral placeholders (`Tenant A` through `Tenant F`) appear while preserving exact dates and dollar amounts. |

---

## 2. Full Repository Test Suite Execution (`2026-11-10`)

```text
python3 guide/verify.py            -> PASS: 1,061 checks, 0 errors (10 HTML pages, 174 source-linked rows, 33 official .gov sources, 23 blank unverified cells, 20 files privacy-verified)
python3 tools/verify_hub.py        -> PASS: 1,551 checks, 0 errors
python3 tools/verify_assurance.py  -> PASS: 1,748 checks, 0 errors (190 current text files privacy-scanned)
python3 tools/check_links.py       -> OK: 10 published pages (+7 archived), 0 errors
python3 tools/check_site.py        -> PASS: 781 checks, 0 errors
python3 integration/verify.py      -> PASS: 6 pages, 57 source-linked rows, tracked-text privacy scan
python3 dashboard/verify.py        -> OK: 12 pages, 0 errors
python3 audit/verify_all.py        -> VERIFICATION PASSED: 10 dashboard pages, 137 source-linked rows
python3 review/verify.py           -> All checks PASSED
```
