# Session `arena-509488b5` — findings and verification record (2026-11-13 UTC)

Branch: `arena/509488b5-rentincreasesf1`. Exclusive file scope: `decision/**`,
`audit/session-509488b5/**`, append-only `COORDINATION.md`. No file owned by
another session was edited.

---

## 1. The question that led the brief: is the 2023 Rent Board rule state or local?

**Answer: local.** Verified line by line against the issuing body.

| Proposition | Official source | Verified passage |
|---|---|---|
| It is a City ordinance | S01 — S.F. Admin. Code §37.15 (sf.gov) | Footnote on the City's own page: *"[Added by Ord. No. 265-20, effective January 18, 2021]"* |
| City describes it as its own law | S21 — Rent Board press release, 2023-02-01 | *"A new law passed by the City and County of San Francisco requires all residential property owners to provide certain information to the Rent Board about their property each year. In addition, the law creates new licensing requirements for landlords."* |
| Why 2023 is the remembered year | S01(c) | *"For condominium units and units in buildings with fewer than 10 units, the information shall be reported commencing March 1, 2023 and updated annually by March 1 of each successive year."* |
| Same staggered date in the adopted rule | S09 — Rent Board Rule §13.14 | *"…with respect to condominium units and buildings with less than ten residential units, this section shall only apply to rent increases that are effective on or after March 1, 2023."* |
| Same staggered date in Board guidance | S02 | *"Reporting requirements began March 1, 2023 for condominiums and units in buildings with fewer than 10 units."* |
| Same date on the tenant-facing page | S08 | *"Owners of condominiums and buildings with less than 10 residential units have been required to report since March 1, 2023"* |

The **notice** rule is state law (Civ. Code §827, S14). The **anti-discrimination**
rules are state and federal (Gov. Code §12955, S18; 42 U.S.C. §3604, S19). AB 1482's
statewide cap does **not** apply, because Civ. Code §1947.12(d)(3) (S15) exempts
housing already under a stricter local rent-control regime.

## 2. Individual owner vs. corporation

§37.15(a) reads *"Owners of residential dwelling units subject to this Chapter 37
shall be required to report…"*. No individual-owner, small-building or two-unit
exemption appears anywhere in the section, in Rule §13.14, or in the Board's
published guidance. The only officially published difference between a large
portfolio and a small one is **when the duty started** (1 July 2022 for buildings
with 10+ units; 1 March 2023 for condominiums and buildings with fewer than 10).

**Mechanism correction.** There is no licence *application* and no approval step.
Reporting into the Housing Inventory generates the licence automatically; the Board
states *"Landlords are not required to file a petition with the City to impose these
types of rent increases"* (S05). An ordinary annual or banked notice goes to the
tenant, not to the Board.

**Timing test.** Rule §13.14: *"the effective date of the rent increase, not the date
of service, shall be used"*; an unlicensed increase is *"null and void"*; and *"Nothing
in this Regulation shall affect a landlord's banking rights"*.

## 3. Figures re-derived independently on 2026-11-13

Rate in force: **1.6%**, 1 March 2026 – 28 February 2027 (S03, S06, S07).
Form 571 rate history transcribed line by line: 46 published periods (S06).

| Scenario | Effective | Banked | Annual | Total | Increase | New rent | Notice | Serve by | Mailed |
|---|---|---|---|---|---|---|---|---|---|
| A-1 annual only | 1 Feb 2027 | 0% | 1.6% | 1.6% | $63.92 | $4,058.92 | 30 d | 2 Jan 2027 | 28 Dec 2026 |
| A-2 annual + banked | 1 Feb 2027 | 1.4% | 1.6% | 3.0% | $119.85 | $4,114.85 | 30 d | 2 Jan 2027 | 28 Dec 2026 |
| A-3 if anniversary is 1 Apr | 1 Apr 2027 | 1.4% | not published | not published | $55.93 (banked part only) | $4,050.93 | 30 d | 2 Mar 2027 | 25 Feb 2027 |
| B-1 banked only 2020–2026 | 1 Jun 2027 | 13.1% | 0% | 13.1% | $412.65 | $3,562.65 | 90 d | 3 Mar 2027 | 26 Feb 2027 |
| B-2 banked + annual | 1 Jun 2027 | 13.1% | not published | not published | blank | blank | 90 d | 3 Mar 2027 | 26 Feb 2027 |

Banked B = 1.8 + 0.7 + 2.3 + 3.6 + 1.7 + 1.4 + 1.6 = **13.1%** (added, not compounded — S04/S05).
All dollar amounts are exact to the cent; no rounding was required. Notice periods
re-derived from Civ. Code §827(b)(2)-(3) with the +5 mailing extension from CCP §1013.

**Deliberately blank:** the annual percentage in force from 1 March 2027 (not
published until that date), any combined total depending on it, the ZIP 94122
"normal/reasonable" market figure (no official source publishes one), and
owner-behaviour-by-entity-type (no official dataset).

## 4. Live legislation

File No. 261020 — *Administrative Code - Cap On Rent Increases for Rent-Controlled
Units*. Legistar on 2026-11-13: **Status "Pending Committee Action"**, introduced
15 September 2026, in control of the Land Use and Transportation Committee,
sponsors Sauter, Chan, Mahmood. As drafted it would cap combined banked and
capital-improvement increases at 10% per year for three years, reaching banked
increases **noticed on or after 15 September 2026**. Unit B's banked portion alone
(13.1%) is above that. Logged as flag F-10.

## 5. Verification performed

`python3 decision/verify.py` — **1,157 checks, 0 failures**, covering:

* 12 generated pages present; every internal link resolves; every `#anchor`
  resolves to an `id`; navigation identical across all 12 pages;
* **293 data-table rows**, each carrying at least one official source link
  (the source-registry table is exempted because it *is* the registry);
* every external URL registered in `decision/data/sources.json`;
* all five scenarios re-derived from `rates.json` with `Decimal`, independently of
  `build.py`, and matched against the rendered HTML on two pages;
* 46 rate rows present and the current rate confirmed as 1.6%;
* all 20 flags and all 22 sources anchored, each source carrying a verified passage;
* privacy scan for e-mail addresses, telephone numbers, street addresses and the
  tenant initials from the brief — across all generated HTML **and** the JSON that
  generates it. Only the Rent Board's own published public line (415-252-4600)
  appears, allow-listed explicitly rather than by loosening the pattern;
* 16 deliberately blank "unverified" cells rendered.

Pre-existing suites re-run on the combined tree, all green:
`tools/verify_hub.py` 1,627 / 0 · `tools/verify_assurance.py` 1,902 / 0 ·
`tools/check_site.py` 781 / 0 · `tools/check_links.py` OK ·
`integration/verify.py` PASS · `build/build.py` reproducible (no diff) ·
`hub/build.py` + `assurance/build.py` reproducible (no diff).

## 6. Irregularities flagged

20 flags (F-01 … F-20) and 7 repository irregularities (R-01 … R-07), all published
on the site's **Flagged for Review** and **Repository audit** pages with source links.

Highest-severity items: F-03 (licence status unknown for both units), F-04/F-05
(Unit B rent and both ledgers unconfirmed), F-06 (whether Unit B's original
occupants remain — banked increases do not survive a new tenancy), F-09 (rate from
1 March 2027 not published), F-10 (File No. 261020), F-15 (pre-redaction blobs in
Git history), F-18 (Housing Inventory submissions are public).

## 7. Scope discipline

This session edited **no** file owned by another session. The root `index.html` is
generated by `hub/build.py` and enforced by the "Final assurance" workflow, so the
consolidated edition is published additively at `/decision/` rather than replacing
the root. That constraint is recorded on the site (flag F-14, suggestion S-16) so
the owner can decide whether to have one session take over the root.
