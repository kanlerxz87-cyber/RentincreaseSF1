# COORDINATION.md — Shared Task Board

This file is the shared task board for multi-session work on this repository.
Read it before starting any task. Claim a task by writing your session ID and
file scope below, then commit and push the claim immediately.

**Last updated:** 2026-11-06 (UTC)
**Repo:** `kanlerxz87-cyber/RentincreaseSF1`
**Default/published branch:** `main`  **GitHub Pages source:** `main` → `/docs`

---

## Environment constraint on branch naming (read this first)

The task protocol asks each session to work on its own branch named
`session-<id>/<task>`. In this environment the working session is bound by the
platform to the branch **`arena/53a11683-rentincreasesf1`**, and the session is
not permitted to create, switch to, or push any other branch. This session
therefore:

* works only on `arena/53a11683-rentincreasesf1`;
* records its file scope in this board **before** writing those files;
* opens the integration pull request **from** `arena/53a11683-rentincreasesf1`
  **into** `main`;
* runs `git pull --rebase origin main` before every push.

This is recorded here so a later session does not read the missing
`session-*` branches as unfinished or abandoned work. No other session has
claimed anything in this repository as of the timestamp above (the repository
contained only `README.md` at commit `b2a2caf`).

---

## Session registry

| Session ID | Branch | Started (UTC) | Status | Notes |
| --- | --- | --- | --- | --- |
| `arena-53a11683` | `arena/53a11683-rentincreasesf1` | 2026-11-06 | active | Only session present. Holds all tasks T1–T9. |

---

## Task board

Status values: `unclaimed` · `in progress` · `done` · `needs review`.
`needs review` means the item is published on the site's **Flagged for Review**
page and does **not** block integration or merge.

| ID | Task | Status | Owner session | Files (scope) |
| --- | --- | --- | --- | --- |
| T1 | Source registry + verification pass (official sources only) | in progress → done | `arena-53a11683` | `data/sources.csv`, `docs/sources.html` |
| T2 | Unit facts, anonymisation, computed lawful maximums | in progress → done | `arena-53a11683` | `data/units.csv`, `data/aga-rates.csv`, `docs/units.html`, `docs/limits.html` |
| T3 | Local / State / Federal requirement tables | in progress → done | `arena-53a11683` | `docs/rules.html` |
| T4 | Notice procedure + lawful reasons for increase | in progress → done | `arena-53a11683` | `docs/process.html` |
| T5 | Institutional vs individual owner practice | in progress → done | `arena-53a11683` | `docs/practice.html` |
| T6 | One unit vs both units / fair-housing + tenant-lawyer review | in progress → done | `arena-53a11683` | `docs/discrimination.html`, `docs/review.html` |
| T7 | Executive summary + landing dashboard | in progress → done | `arena-53a11683` | `EXECUTIVE_SUMMARY.md`, `docs/index.html`, `docs/assets/style.css` |
| T8 | Flagged-for-review register | in progress → done | `arena-53a11683` | `docs/flagged.html` |
| T9 | Integration: nav, link check, PR to `main`, merge, Pages deploy | in progress | `arena-53a11683` | `docs/*` (nav), `README.md`, `.github/workflows/pages.yml` |

---

## Claim log

```
2026-11-06T00:00Z  arena-53a11683  CLAIM T1..T9  scope: data/, docs/, EXECUTIVE_SUMMARY.md, README.md
                                     reason: repository is empty apart from README.md; no competing sessions.
```

---

## Verification record (filled as tasks close)

### T1 — Source registry
* **Sources:** 26 official sources (SF Rent Ordinance §§37.3, 37.9F, 37.10B, 37.10C, 37.15; Rent Board Rules Part IV §§4.10/4.12; Rent Board fact sheet 571; SF.gov rent-increase, banking, hardship, housing-inventory, referral pages; Cal. Civ. Code §§827, 1942.5, 1947.12, 1954.53; Gov. Code §12955; 42 U.S.C. §3604; SF Human Rights Commission).
* **Verification performed:** each source fetched and read directly; quoted text compared against the page it is attributed to. Every row in every table links to one of these sources.
* **Irregularities:** see F1 and F5 on the Flagged page.

### T2 — Unit facts and computed maximums
* **Sources:** fact sheet 571 (annual percentages), SF.gov rent-increase page (12-month rule, no rounding, additional-occupant rule), Rule 4.12 (banking, non-compounding).
* **Verification performed:** every percentage read from fact sheet 571; arithmetic recomputed in `python3` (see `data/units.csv`); percentages added, never compounded.
* **Irregularities:** F2, F3, F4, F5.

### T3 — Requirement tables
* **Sources:** as T1 (`rules.html`).
* **Verification performed:** each requirement traced to enacted text or the issuing agency's page; `n/a` used where a rule does not reach these facts.
* **Irregularities:** F6 (no federal rent ceiling found in the federal materials reviewed — recorded as "none found", not as "confirmed absent").

### T4 — Notice and reasons
* **Sources:** §37.3(b), Rule 4.10, Cal. Civ. Code §827, SF.gov pages for increases/banking/hardship.
* **Verification performed:** notice periods (30/90 days, +5 if mailed) cross-checked against both §827 and the SF.gov summary.
* **Irregularities:** F1 (banking look-back wording differs between SF.gov page and Rule 4.12), F12 (service-date arithmetic for Unit 2).

### T5 — Owner practice
* **Sources:** §37.3 generally (applies to "landlords" of any size), §37.10C (algorithmic devices), §37.15 (licence), §37.7/§37.8 (petitions), SF.gov fee page.
* **Verification performed:** only statements traceable to official text are made as findings. Statements about typical private behaviour of large vs small owners are **not** sourced and are labelled unverified (F6/F7 group).
* **Irregularities:** no official dataset was found that measures how individual SF owners set increases — flagged, not invented.

### T6 — Fair housing / one-vs-both
* **Sources:** 42 U.S.C. §3604; Gov. Code §12955; §37.10B(a)(9); Cal. Civ. Code §1942.5; §37.3(a)(1)–(2); SF HRC housing page.
* **Verification performed:** protected classes compared between FHA and FEHA text; SF harassment provision quoted.
* **Irregularities:** none beyond F10 (unknown complaint history).

### T8 — Flagged register
* **Sources:** as cited per flag.
* **Verification performed:** every flag names the specific conflicting or missing evidence.

---

## Integration record (T9)

* **Link check:** internal links and anchors checked with `tools/check_links.py`; external links spot-checked by fetching each URL.
* **PR:** see "Pull request" section below.
* **Pages:** `main` → `/docs` (workflow-less legacy publishing), `.nojekyll` present.
* **PII:** no tenant names, initials, street address, or contact data in any published file. Only ZIP code, dates, and amounts, as instructed.

### Pull request

| Item | Value |
| --- | --- |
| PR | *(recorded after creation — see bottom of file)* |
| Merge result | *(recorded after merge)* |
| Pages deploy | *(recorded after verification)* |

---

## Requests to other sessions

None. If another session needs to change a file in this session's scope, log the
request here rather than editing it.

## Handoff rule

If this session crashes or its claim is more than 60 minutes old with no new
commits, any other session may take over the task and must note the handoff in
this log.
