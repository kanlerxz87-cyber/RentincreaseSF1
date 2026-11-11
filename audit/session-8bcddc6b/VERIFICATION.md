# Verification record — session arena-8bcddc6b (2026-11-11 UTC) — Outer Sunset 94122

**Scope:** `audit/session-8bcddc6b/**` only, plus append-only `COORDINATION.md`. No canonical file (`index.html`, `hub/**`, `assurance/**`, `audit/final-integration/**`, `tools/verify_*.py`, root Markdown) was edited by this session. Findings that would require a canonical edit are logged as requests in `COORDINATION.md`.

**Live site confirmed:** GitHub Pages legacy publishing from `main`, root `/`, status `built` (checked via `gh api repos/.../pages` on 2026-11-11). Landing page fetched live and read: [https://kanlerxz87-cyber.github.io/RentincreaseSF1/](https://kanlerxz87-cyber.github.io/RentincreaseSF1/) — individual-owner answer first, scenario cards, nine category pages. No new site edition was created; creating a duplicate would fragment the published record. This session's deliverable is the fresh dated verification plus the anonymized executive summary in this folder.

## 1. Live official-source verification (2026-11-11)

All 29 canonical sources (S01–S29) were re-fetched and read live on 2026-11-11. Per-source notes, including which chunks were read and what each confirms, are in `sources.json`. Summary of what changed versus the 2026-11-10 verification:

| Item | 2026-11-10 position | 2026-11-11 re-check | Result |
|---|---|---|---|
| Annual allowance 1.6% (Mar 1, 2026 – Feb 28, 2027) | Form 571 | Form 571 PDF re-read; table matches `hub/data.json` for every period 2019–2027 | Confirmed, no change |
| Licence gate (effective date) | §37.15 + Housing Inventory | Both pages re-read; wording unchanged | Confirmed, no change |
| Banking (24-month test, add-don't-compound) | Banking page + Rule 4.12 | Both re-read; Rule 4.12(a)/(b) verbatim confirmed | Confirmed, no change |
| Notice (30/90 days + 5 mail) | Civil Code §827 + CCP §1013 | Both re-read; thresholds unchanged | Confirmed, no change |
| File #261020 status | Pending Committee Action | Legistar re-read 2026-11-11: Pending Committee Action, introduced 9/15/2026, no final action, no enactment date | Confirmed, still not law |
| Rent Board Fee $59.00; exemption deadline Dec 14, 2026 | Fee page | Fee page re-read; amounts and deadline unchanged | Confirmed, no change |
| Business Registration carve-out | Treasurer lessor guidance | Both Treasurer pages re-read; fewer-than-four-units wording unchanged | Confirmed, no change |
| AB 1482 8.8% inapplicable to SF-controlled units | SF AB 1482 report + §1947.12(d)(3) | Both re-read | Confirmed, no change |

**Irregularities found this session:** none that change any figure or legal proposition. Two scope limits are recorded honestly rather than overstated: (a) S02 was re-read only in chunk 0 of 5, so later-chunk propositions (§37.3(b) notice detail, §37.3(a)(11) occupant rule) are not re-asserted from S02 in this session's summary beyond what chunk 0 shows — the summary cites S05 for the occupant rule instead; (b) S20 (California Tenants guide) chunks read did not include the rent-increase pages, so this session does not quote S20 for any proposition. Both limits are noted in `sources.json`. No value was inferred or filled in.

## 2. Line-by-line arithmetic recomputation

Recomputed independently with exact `Decimal` arithmetic (see `verify.py`). All match the canonical edition to the cent:

| Scenario | Recomputed | Canonical | Match |
|---|---|---|---|
| Unit 1 annual 1.6% on $3,995.00 | $63.92 → $4,058.92 | $63.92 → $4,058.92 | Yes |
| Unit 1 banked 1.4% on $3,995.00 | $55.93 | $55.93 | Yes |
| Unit 1 combined 3.0% | $119.85 → $4,114.85 | $119.85 → $4,114.85 | Yes |
| Unit 2 annual 1.6% on $3,150.00 | $50.40 → $3,200.40 | $50.40 → $3,200.40 | Yes |
| Unit 2 banked 11.5% (1.8+0.7+2.3+3.6+1.7+1.4) | $362.25 | $362.25 | Yes |
| Unit 2 combined 13.1% | $412.65 → $3,562.65 | $412.65 → $3,562.65 | Yes |
| Unit 2 File #261020 illustration 11.6% | $365.40 → $3,515.40 | $365.40 → $3,515.40 | Yes |
| Unit 2 90-day personal / 95-day mail to Feb 28, 2027 | Nov 30, 2026 / Nov 25, 2026 | Nov 30, 2026 / Nov 25, 2026 | Yes |
| Unit 1 30-day personal / 35-day mail to Feb 1, 2027 | Jan 2, 2027 / Dec 28, 2026 | Jan 2, 2027 / Dec 28, 2026 | Yes |

Method confirmed: percentages are **added, never compounded**; no rounding up. Sources: [Form 571](https://www.sf.gov/documents/34344/571_Allowable_Annual_Increases_26-27_1.pdf) · [Banking](https://www.sf.gov/information--banked-rent-increases) · [Rule 4.12](https://www.sf.gov/reports--december-2022--rent-board-rules-and-regulations-part-iv-rent-increases-not-requiring).

## 3. Table-row source check

Every table row in this session's `EXECUTIVE_SUMMARY.md` carries either a direct link to an official publisher (sf.gov, leginfo.legislature.ca.gov, sftreasurer.org, sfgov.legistar.com, hud.gov, justice.gov, courts.ca.gov) or an explicit blank/flagged marker. Enforced by `verify.py` §4 (≥30 rows checked). Canonical edition separately enforces the same rule via `tools/verify_hub.py` (211 claim-table rows with official source or flag link).

## 4. Privacy scan

This session's files use placeholders only (Unit 1 — Tenants 1A and 1B; Unit 2 — Tenants 2A and 2B). `verify.py` §5 scans every session file for two-letter initial patterns and street-address markers: 0 hits. Canonical suites re-run this session also passed their privacy scans (`verify_assurance.py`: 214 current text files scanned). **Known limitation (carried, not introduced here):** earlier public Git history contains tenant initials; current-file scans do not remove or check historical copies. This is published on the canonical Flagged for Review page and is not repeated here.

## 5. Build and link checks (re-run 2026-11-11)

| Suite | Result |
|---|---|
| `python3 hub/build.py` + `python3 assurance/build.py` | Reproducible; no diff to committed output |
| `python3 tools/verify_hub.py` | 1,599 checks, 0 errors |
| `python3 tools/verify_assurance.py` | 1,822 checks, 0 errors |
| `python3 tools/check_links.py` | OK: all internal links/anchors resolve, no personal tokens |
| `python3 audit/session-8bcddc6b/verify.py` | All session checks passed (see §6) |

## 6. Session checks

Run: `python3 audit/session-8bcddc6b/verify.py`. Covers dollar recomputation, date arithmetic, Form 571 cross-check, per-row source/flag enforcement, privacy scan, and re-runs of the three canonical suites as subprocesses. Exit code is non-zero on any failure.

## 7. Requests to the canonical holder (arena-2c7b19e2 K3–K6)

None. No correction to `index.html`, `hub/**`, `assurance/**`, `audit/final-integration/**`, `tools/verify_*.py`, or root Markdown is requested by this session, because the 2026-11-11 live re-check confirms every figure and proposition those files publish. Stale PRs #29 and #32 remain with K7 and were not touched.
