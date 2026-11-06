# COORDINATION.md — Shared task board

**Repo:** kanlerxz87-cyber/RentincreaseSF1
**Last updated:** 2026-11-06
**Protocol:** Claim a task by writing your session ID + file scope below, then commit and push the claim immediately. Never start a task another session has claimed. If a task needs a file owned by another session, log a request here instead of editing. Run `git pull --rebase` before every push. A claim older than 60 minutes with no commits may be taken over (note the handoff).

## Session register

| Session ID | Branch | Role | Status |
| --- | --- | --- | --- |
| `SESSION-e94ffd3f` | `arena/e94ffd3f-rentincreasesf1` | Research, verification, site build, **final integration + publish** | active |
| `arena/2347590f-rentincreasesf1` | merged to `main` (PR #1) | First draft site under `site/` + `research/` | done, archived |
| `arena/da7cfb4c-rentincreasesf1` | merged to `main` (PR #2) | Draft site under `docs/` + `scripts/` | done, archived |

`SESSION-e94ffd3f` is the final integration session: it merges the branches, re-verifies the combined data,
confirms the site builds with no broken links, and publishes.

## Task board (live)

| # | Task | Status | Owner | Files / scope |
| --- | --- | --- | --- | --- |
| T1 | Verify SF Rent Ordinance coverage, allowable increase, banking, notice, license rules | done | SESSION-e94ffd3f | `research/`,`data/` |
| T2 | Verify state statutes (AB 1482, Civil Code 827, Costa-Hawkins, FEHA, retaliation) | done | SESSION-e94ffd3f | `research/`,`data/` |
| T3 | Verify federal layer (Fair Housing Act) | done | SESSION-e94ffd3f | `research/`,`data/` |
| T4 | Verify how institutional vs individual owners lawfully handle increases | done | SESSION-e94ffd3f | `data/` |
| T5 | Build source register with official links | done | SESSION-e94ffd3f | `data/sources.json`,`sources.html` |
| T6 | Build static site: dashboard, subpages, tables | done | SESSION-e94ffd3f | `build.py`,`assets/`,`*.html` |
| T7 | Anonymisation pass (no personal identifiers in tracked files) | done | SESSION-e94ffd3f | all tracked files |
| T8 | Flagged for Review page | done | SESSION-e94ffd3f | `review.html`,`data/flags.json` |
| T9 | Link check + build check | done | SESSION-e94ffd3f | `check_links.py` |
| T10 | **Integration**: merge `main`, reconcile both boards' figures, re-verify combined data | done | SESSION-e94ffd3f | `COORDINATION.md`,`review.html` |
| T11 | **Privacy remediation** of earlier drafts (identifiers published in `docs/`, `site/`, `research/`) | done | SESSION-e94ffd3f | `docs/`,`site/`,`research/` |
| T12 | Open PR, merge, publish GitHub Pages, record result | in progress | SESSION-e94ffd3f | repo settings |

## Privacy control (top priority)

Personal information is **internal only**. This repository is public and publishes a public site, so no real
names, initials, unit addresses or contact details are stored in any tracked file — including commit messages,
page metadata and the privacy checker itself. Tenants are represented by role labels `Tenant A-1` … `Tenant B-2`.
**Dates and dollar amounts are preserved exactly**, because the legal analysis depends on them.

The mapping from role labels to individuals lives only in the owner's private records (it is derivable from the
original brief) and is intentionally not committed.

### T11 — Privacy remediation (action taken during integration)

An automated initial-pair scan run on the merged tree found real tenant initials in files published by an earlier
session: `docs/executive_summary.md`, `site/discrimination.html`, `site/executive_summary.html`,
`site/flagged.html`, `research/discrimination.md`, and the prior board's own task rows. Because `docs/` is served
by GitHub Pages, that was a live exposure. All six files were rewritten to use the role labels above; a re-scan of
every tracked file now returns zero hits. The scan in `check_links.py` detects the *shape* of an initial pair
rather than storing the identifiers, so the checker cannot itself become a leak.

## Verification log (per task)

### T1 — San Francisco (local)
Sources read directly: sf.gov Rent Board "Learn about rent increases" (S01), Rent Board news release 14 Jan 2026
(S02), Rent Board form 571 allowable-increase table (S03), "Banked rent increases" (S04), "Annual rent increase
for multiple years" (S05), "Learn about San Francisco rental laws" (S06), Rules & Regulations Part IV
§4.10/§4.12 (S07), Administrative Code Ch. 37 as amended 24 Nov 2024 (S08), Housing Inventory / rent increase
licence (S09), Landlord Petitions & Passthroughs (S10), topics 322 (S11) and 323 (S12), Tenant Petitions (S13).

Verified values: **1.6%** for 3/1/2026–2/28/2027; **1.4%** for 3/1/2025–2/28/2026; the full 1982–2027 schedule
transcribed from form 571; §37.3(a)(1),(a)(2),(a)(8),(a)(11),(b) quoted from the ordinance PDF; Rule 4.12(a)/(b)
quoted verbatim.

### T2 — State
Civil Code 1947.12 (S14), 827 (S15), 1954.52 (S16), 1954.53 (S17), 1942.5 (S18), Gov 12955 (S19). Confirmed
§1947.12(d)(3) exempts units under a local ordinance stricter than AB 1482, so the state cap does not govern.

### T3 — Federal
HUD Fair Housing Act overview (S20): race, colour, national origin, religion, sex, familial status, disability.
**No federal statute capping private-market residential rent was located** — recorded as an absence-of-law
finding (F06), not as an affirmative citation.

### T4 — Owner practice
AvalonBay Communities FY2024 Form 10-K (S23) read for the regulatory section and operating-strategy bullets; SF
§37.10C algorithmic-device ban transcribed from the ordinance amendment table (S08). Individual owners: no
separate rule set — §37.2(h) defines "landlord" to include owner, lessor, agent and successor.

### T5 — Sources
24 entries: 21 official (city/state/federal), 1 SEC filing, 1 programme operator, plus the SF Human Rights
Commission division page. Each carries a URL and the specific fact it supports.

### T9 — Checks run
- `python3 build.py` — regenerates 10 pages and asserts the arithmetic: banking totals 10.1/11.5 → 11.7%/13.1%;
  Unit A $63.92; Unit B $50.40. **Pass.**
- `python3 check_links.py` — 10 pages, 24 external links, 0 errors: no broken internal links, no dead fragments,
  no source-less page, no personal identifiers. **Pass.**
- `python scripts/build.py && python scripts/verify.py` — the archived draft's own structural checks (source
  allowlist, internal assets, status schema, exact-cent arithmetic). **Pass** (see T10 note on the two root-path
  assertions).

### T10 — Integration
`origin/main` had advanced by two merged draft PRs while this analysis was in progress. Merged `main` into this
branch; conflicts in `index.html`, `README.md` and `COORDINATION.md` resolved by keeping this dashboard at the
repository root and preserving both prior boards/sites in place.

Cross-session reconciliation of the figures (table also published on `review.html`):

| Item | Earlier draft (`docs/`) | This site | Result |
| --- | --- | --- | --- |
| Current allowable increase | 1.6% | 1.6% | match |
| Unit A | $3,995 × 1.6% = $63.92 → $4,058.92 | same | match |
| Unit B | $3,150 × 1.6% = $50.40 → $3,200.40 | same | match |
| Notice periods | 30 / 90 days | 30 / 90 days (+5 mail) | match |
| Banked allowance for Unit B | flagged, no figure | conditional 11.7%–13.1% range | extended here |
| Source standard | mostly official, some trade blogs in the task log | official only, secondary labelled | tightened here |

Two sessions reading the same Rent Board pages reached identical figures independently — the strongest available
check on the arithmetic. No verified value differs between the drafts.

Root-path change: the earlier draft's root `index.html` was a redirect to `docs/index.html`. The root is now the
dashboard, and `docs/index.html` is linked from the dashboard's integration record and from `review.html`. The
archived draft's `scripts/verify.py` asserted the old redirect; those two assertions were updated to assert the
dashboard plus the presence of the archive link, so CI continues to check the archived site's integrity without
failing on the intended root change.

## Irregularities found (summary — full detail on `review.html`)

1. **F01 High** — Rule 4.12 requires a full **12 months** before a skipped increase banks; the Rent Board's
   explanatory page says **24 months**. Worth 1.4 pp / $44.10 a month on Unit B.
2. **F02** — two official worked examples attach the percentage to the wrong effective period.
3. **F03 High** — Unit A: new tenancy or continuing tenancy with an added occupant?
4. **F04 High** — Unit B rent history 2019–2026 unverified; all banked figures are ceilings.
5. **F05** — coverage inferred from the 1940 build date; certificate of occupancy not yet pulled.
6. **F06** — "no federal rent cap" is an absence-of-law finding.
7. **F07** — the 2027–28 allowable increase is not published yet.
8. **F08** — no official per-ZIP "normal increase" statistic exists; market data excluded by design.
9. **F09–F11** — duplicate dates in the brief, a form-number metadata mismatch, fee amounts omitted.
10. **F12 (remediated)** — an earlier session published real tenant initials in `docs/`, `site/` and `research/`.
    Removed during integration; see T11.

## Handoff / conflict log

- Merge conflicts: `index.html` (add/add), `README.md` (content), `COORDINATION.md` (add/add). Resolved in favour
  of this dashboard at the root, with all prior files retained; no earlier work was discarded.
- No file-scope collision with an active session. Both prior sessions were `done` before integration began.
- No other session's branch needed a cross-scope change beyond T11 (privacy remediation) and the two
  `scripts/verify.py` root assertions, both logged above.

## Publish record

_(appended after merge and deploy confirmation)_


---

## Appendix A — Prior session board, preserved verbatim

_Sanitised for privacy (role labels substituted for initials); otherwise unchanged._

markdown
# COORDINATION.md - RentincreaseSF1

## Shared Task Board

This file coordinates parallel agent sessions working on the RentincreaseSF1 project.

### Tasks

| Task ID | Description | Status | Owning Session ID | Files Touched | Sources / Verification | Irregularities |
|---------|-------------|--------|-------------------|---------------|------------------------|----------------|
| TASK-01 | Create Executive Summary (Internal) | done | arena/da7cfb4c-rentincreasesf1 | `/docs/executive_summary.md`, `/site/executive_summary.html` | [1](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [2](https://landlordos.net/learn/questions/sf-annual-rent-increase-2026) [3](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [4](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [5](https://www.lethub.co/blog/how-much-can-you-raise-rent) [6](https://calandlordtenantlaws.com/rent-control-ab-1482) [7](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) [8](https://www.bancalsf.com/banked-rent-increases-san-francisco) [9](https://christopherleesf.com/san-francisco-rent-control-laws-2025/) [10](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [11](https://www.bancalsf.com/sf-rent-board-housing-inventory) [12](https://rentreboot.com/guide/bay-area-rent-control-by-city-2026) [13](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [14](https://www.leaserunner.com/blog/month-to-month-rent-increase-california) | Internal tenant names (Tenant A-1, Tenant A-2, Tenant A-3, Tenant A-4, Tenant B-1, Tenant B-2) anonymized on site; Unit 1 tenancy change (April 1, 2026) flagged; Unit 2 anniversary (June 1, 2026) flagged; Banking verification needed |
| TASK-02 | Research SF Rent Control Laws & Increases (94122) | done | arena/da7cfb4c-rentincreasesf1 | `/research/sf_laws.md`, `/site/sf_laws.html` | [1](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [2](https://landlordos.net/learn/questions/sf-annual-rent-increase-2026) [3](https://www.bancalsf.com/sf-rent-board-housing-inventory) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [5](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) [6](https://calandlordtenantlaws.com/rent-control-ab-1482) [7](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [8](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [9](https://www.lethub.co/blog/how-much-can-you-raise-rent) | Verified from SF Rent Board, CA state laws, federal laws; 1.4% (2025-26) and 1.6% (2026-27) rates confirmed |
| TASK-03 | Research Corporate vs Individual Owner Practices | done | arena/da7cfb4c-rentincreasesf1 | `/research/practices.md`, `/site/practices.html` | [1](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [2](https://www.bancalsf.com/banked-rent-increases-san-francisco) [3](https://christopherleesf.com/san-francisco-rent-control-laws-2025/) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [5](https://rentreboot.com/guide/bay-area-rent-control-by-city-2026) [6](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [7](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) | Verified corporate vs individual practices; consistent application vs selective increases |
| TASK-04 | Tenant Notification Methods & Reasonable Reasons | done | arena/da7cfb4c-rentincreasesf1 | `/research/notification.md`, `/site/notification.html` | [1](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [2](https://landlordos.net/learn/questions/sf-annual-rent-increase-2026) [3](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [5](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) [6](https://calandlordtenantlaws.com/rent-control-ab-1482) [7](https://www.leaserunner.com/blog/month-to-month-rent-increase-california) [8](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) | 30/90 days notice confirmed; 1.4%/1.6% rates confirmed; capital/operating/utility pass-throughs verified |
| TASK-05 | Discrimination Analysis (Unit 1 vs Unit 2) | done | arena/da7cfb4c-rentincreasesf1 | `/research/discrimination.md`, `/site/discrimination.html` | [1](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [2](https://www.bancalsf.com/banked-rent-increases-san-francisco) [3](https://christopherleesf.com/san-francisco-rent-control-laws-2025/) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [5](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) [6](https://calandlordtenantlaws.com/rent-control-ab-1482) [7](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [8](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) | Recommendation: Raise both units to avoid discrimination; Fair Housing Act compliance verified |
| TASK-06 | Create Site Structure & Landing Page | done | arena/da7cfb4c-rentincreasesf1 | `/site/index.html`, `/site/css/style.css` | [1](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [2](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) | Dashboard created with tables and findings |
| TASK-07 | Populate Tables & Findings | done | arena/da7cfb4c-rentincreasesf1 | `/site/index.html`, `/site/executive_summary.html`, `/site/sf_laws.html`, `/site/practices.html`, `/site/notification.html`, `/site/discrimination.html` | [1](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [2](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) [3](https://www.bancalsf.com/sf-rent-board-housing-inventory) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [5](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [6](https://calandlordtenantlaws.com/rent-control-ab-1482) [7](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [8](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [9](https://www.lethub.co/blog/how-much-can-you-raise-rent) | Tables populated with verified data and source links |\n| TASK-08 | Flagged for Review Page | done | arena/da7cfb4c-rentincreasesf1 | `/site/flagged.html` | [1](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [2](https://landlordos.net/learn/questions/sf-annual-rent-increase-2026) [3](https://www.bancalsf.com/sf-rent-board-housing-inventory) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) | Internal irregularities flagged for manual review |\n| TASK-09 | Integration, Verification & GitHub Pages | done | arena/da7cfb4c-rentincreasesf1 | All site files | [1](https://cityrulelookup.com/rental-property/rent-control/san-francisco-ca) [2](https://www.sf.gov/reports--current-rates-including-rent-increase-relocation-sec-deposit) [3](https://www.bancalsf.com/sf-rent-board-housing-inventory) [4](https://urbantaken.com/understanding-rent-control-in-san-francisco/) [5](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [6](https://calandlordtenantlaws.com/rent-control-ab-1482) [7](https://www.lifetimepm.com/blog/california-rent-increase-guide-2026) [8](https://www.fflw.org/blog/how-much-can-a-landlord-raise-rent) [9](https://www.lethub.co/blog/how-much-can-you-raise-rent) | Site built, verified line by line, GitHub Pages deployment ready |

### Session Claim Instructions
1. Claim a task by writing your session ID (e.g., `arena/da7cfb4c-rentincreasesf1`) and file scope.
2. Commit and push the claim immediately.
3. Work line by line, verify from official sources, provide links.
4. Record sources, verification, and irregularities in this file.
5. Mark task as `done` when finished.

### Current Session
- Session ID: `arena/da7cfb4c-rentincreasesf1`
- Branch: `arena/da7cfb4c-rentincreasesf1`
- Claimed Tasks:
  - TASK-01 (Executive Summary) - Status: done
  - TASK-02 (SF Rent Control Laws) - Status: done
  - TASK-03 (Corporate vs Individual Practices) - Status: done
  - TASK-04 (Tenant Notification & Reasons) - Status: done
  - TASK-05 (Discrimination Analysis) - Status: done
  - TASK-06 (Site Structure) - Status: done
  - TASK-07 (Populate Tables) - Status: done
  - TASK-08 (Flagged for Review) - Status: done
  - TASK-09 (Integration & Deploy) - Status: done

### Notes
- All work must be verified from official sources (SF Rent Board, CA state laws, federal laws, etc.).
- Provide source links for manual review.
- Flag any irregularities.
- Personal information must be anonymized (placeholder names) on the website.
- Keep internal executive summary with actual details (internal only).

## Integration Notes (from main)
- Official sources retrieved: SF annual 2026 announcement, rent guide, coverage, inventory, banking, petitions and tenant/landlord help; California legislative §§827, 1947.12, 1942.5; CRD housing; HUD Fair Housing Act overview. Source URLs are enumerated in docs/data.json and the site's Sources page.
- Row-by-row substantive review separates verified guidance, analysis, derived arithmetic and unverified supplied context. No private fact is marked officially confirmed. No original personal initials were stored.
- Flags F01–F09 published on docs/flagged.html: coverage, ledger, continuity, license/lease, market norms, lawyer approval, source example date errors, privacy limits and verification scope. These are needs review and do not block publication.
- Tests: seven generated pages; 66 rows with official links; source domain/key checks; internal asset/navigation existence; exact-cent calculation checks; JavaScript syntax. No installed browser automation; visual browser testing not claimed. External pages retrieved using official-page tools; no assertion of exhaustive case-law/lease review.
- Initial remote branch pull failed because branch did not exist; rebased against origin/main and pushed the claim. No conflicts and no other sessions found.
- Pages API: existing main-root legacy configuration confirmed. Changing configuration denied 403; using root redirect to docs and legacy deployment instead. No authentication secrets requested.

