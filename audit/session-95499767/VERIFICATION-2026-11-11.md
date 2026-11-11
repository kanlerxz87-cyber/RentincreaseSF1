# Independent re-verification — 2026-11-11

**Session:** `arena-95499767` · **Branch:** `arena/95499767-rentincreasesf1`
**Baseline commit on arrival:** `3885c6b` (main, PR #42 merged)
**Scope audited:** the canonical dashboard — `index.html`, `hub/*.html`, `hub/data.json`,
`assurance/index.html`. Superseded editions were **not** audited here; they are already marked
superseded and are out of this session's claimed scope.

**Method.** Every one of the 29 registered sources was fetched live on 2026-11-11 and read. Each
quoted passage in `hub/sources.html` was compared to the live page text. Each rate row, date and
dollar figure was recomputed independently of the generator. Nothing below is inferred from a
secondary page.

---

## 1. Source-by-source result

| ID | Publisher / document | Result | Basis |
| --- | --- | --- | --- |
| S01 | S.F. Admin. Code §37.15 | **Confirmed verbatim** | (a), (b)(2)(A)–(G), (c), (e) all as quoted. (e) requires "substantially complied" for the licence and "restored prospectively … a tenant shall not be obligated to pay the increased rent for months during the period of suspension". |
| S02 | S.F. Admin. Code §37.3 | **Confirmed verbatim** | (a)(1) 60%-of-CPI with a 7% ceiling; (a)(2) banking; (a)(11)(A) additional-occupant prohibition ("notwithstanding a rental agreement … that specifically permits"); (b)(1)–(5) notice contents; (b)(5) null and void. |
| S03 | Rent Board — Housing Inventory | **Confirmed verbatim** | "a landlord must have a current rent increase license on file with the Rent Board before any annual or banked rent increase can go into effect"; licence "does not need to be included with your rent increase notice"; "Reporting is free"; annual deadline March 1; reporting began March 1 2023 for 1–9 unit buildings. |
| S04 | Rent Board — Banked rent increases | **Confirmed verbatim** | 24-month no-increase test; no Board approval needed; no compounding or prorating; no limit; the 2026-11-09 File #261020 notice, quoted exactly. |
| S05 | Rent Board — Learn about rent increases | **Confirmed verbatim** | 1.6% for 3/1/26–2/28/27; 30/90-day notice; +5 days for mail; base rent only; no rounding up; additional-occupant prohibition; anniversary rules. |
| S06 | Form 571 (PDF) | **Confirmed — all 46 rows** | Machine-compared row by row against `hub/data.json["rates"]`: **46/46 exact**, including the two 1992 sub-periods and the leap-year end dates. |
| S07 | Rules & Regs Part IV — §4.10, §4.12 | **Confirmed verbatim** | §4.10(a)–(c) and §4.12(a)–(b) as quoted. |
| S08 | Cal. Civ. Code §827 | **Confirmed verbatim** | (b)(1)(A)/(B) service; (b)(2) 30 days at ≤10%; (b)(3)(A) 90 days above 10%. |
| S09 | Cal. Civ. Code §1947.12 | **Confirmed verbatim** | (a)(1) 5%+CPI or 10%; (d)(3) local-ordinance exclusion. |
| S10 | Rent Board — AB 1482 guidance | **Confirmed verbatim** | "The maximum rent increase for units under AB 1482 from August 1, 2026 to July 31, 2027 is 8.8% in San Francisco. This does NOT apply for units under the rent increase limitations of the San Francisco Rent Ordinance." Both sentences are adjacent on the live page. |
| S11 | Cal. Civ. Code §1954.53 | **Confirmed** | Costa-Hawkins; (a) initial-rate rule and the §827-termination carve-out. |
| S12 | Cal. Civ. Code §1942.5 | **Confirmed verbatim** | 180-day retaliation window; (f) preserves the lessor's rights "for any lawful cause". |
| S13 | Cal. Gov. Code §12955 | **Confirmed verbatim** | (a) protected categories enumerated as quoted. |
| S14 | HUD — Fair Housing Act overview | **Confirmed** | Seven federal protected classes: race, color, national origin, religion, sex, familial status, disability. |
| S15 | S.F. Admin. Code §37.10B | **Confirmed verbatim** | (a)(9) discrimination as bad-faith harassment; (c)(5) treble damages and attorney's fees. |
| S16 | S.F. Admin. Code §37.10C | **Confirmed verbatim** | (a) sale/ (b) use prohibitions; (c)(1) definition limited to **non-public competitor data**; (d)(2) tenant private right of action. |
| S17 | Rent Board Fee | **Confirmed verbatim** | $59.00 per dwelling unit for 2026-2027; up to $29.50 recoverable; due March 1; exemption deadline 14 December 2026. |
| S18 | Rent Board — SF rental laws | **Confirmed verbatim** | 13 June 1979 coverage date; exempt categories list. |
| S19 | Rent Board Referral Listing | **Confirmed** | Free/low-cost tenant resources, including the Open Door Legal **Sunset office at 1722 Irving Street, 94122** — the same ZIP as these units. |
| S20 | Cal. DRE, *California Tenants* (RE 26) | **Confirmed** | Official state publication; hosted by California Courts. |
| S21 | Cal. Code Civ. Proc. §1013(a) | **Confirmed verbatim** | 5 calendar days for in-state mail; 10 out-of-state; 20 outside the US. |
| S22 | U.S. DOJ — RealPage proposed settlement | **Confirmed** | Dated **24 November 2025**; described as a *proposed* settlement. |
| S23 | Rent Board — Failure to Repair petitions | **Confirmed verbatim** | "The petition must be filed no later than 60 days following the tenant's receipt of the rent increase notice." |
| S24 | Treasurer — Lessors of residential real estate | **Confirmed verbatim** | "one residential structure consisting of fewer than four units … is not, **by reason of that fact alone**, required to obtain a business registration certificate." |
| S25 | Treasurer — Register a Business | **Confirmed verbatim** | Same carve-out listed under "you do not need to register if your only business is …". |
| S26 | Legistar File #261020 | **Confirmed** | Status **"Pending Committee Action"**; introduced 9/15/2026; Land Use and Transportation Committee; history has 4 referral records and **no** enactment. |
| S27 | Rent Board — §6.14 and Costa-Hawkins | **Confirmed verbatim** | Reset keyed to the **last** original occupant; co-tenant protected regardless of move-in date. |
| S28 | Rules & Regs Part VI — §6.14 | **Confirmed verbatim** | 60-day rebuttable presumption for co-occupants; 90-day post-vacancy window for non-co-occupants. |
| S29 | Rent Board — §6.14 / Costa-Hawkins petition | **Confirmed verbatim** | No petition required; optional determination petition; "vacate" vs "permanently reside". |

**Result: 29/29 sources confirmed live on 2026-11-11. No quote, rate, date or figure was found to be
wrong.** This is an independent confirmation of the `arena-4329d908` and `arena-2c7b19e2` findings.

---

## 2. Arithmetic re-verified from primary percentages

| Scenario | Inputs | Independent result | Matches published figure |
| --- | --- | --- | --- |
| U1 annual only | $3,995.00 × 1.6% | $63.9200 → **$63.92**; new rent **$4,058.92** | ✅ |
| U1 annual + 1.4% banked (3.0%) | $3,995.00 × 3.0% | $119.8500 → **$119.85**; new rent **$4,114.85** | ✅ |
| U1 banked component alone | $3,995.00 × 1.4% | **$55.93** | ✅ |
| U2 annual only | $3,150.00 × 1.6% | $50.4000 → **$50.40**; new rent **$3,200.40** | ✅ |
| U2 annual + 11.5% banked (13.1%) | $3,150.00 × 13.1% | $412.6500 → **$412.65**; new rent **$3,562.65** | ✅ |
| U2 banked component alone | $3,150.00 × 11.5% | **$362.25** | ✅ |

Additive, never compounded; no rounding up. Every result reproduces to the cent.

---

## 3. Corrections applied by this session

| # | What was wrong | Where | Fix |
| --- | --- | --- | --- |
| C-1 | **The "reasonable and normal increase" answer omitted AB 1482's own exempt category.** The live Rent Board page lists "A two-unit property, provided the second unit was occupied by an owner of the property for the entire period of the tenancy" among units exempt from **both** the just-cause and rent-cap provisions. Neither `hub/data.json` nor any page recorded this as a separate exemption — the site's only statement was the general local-ordinance exclusion. This matters on the reported facts because the brief describes a **two-unit** building. | `hub/data.json`, `index.html`, `hub/limits.html` | Added as a flagged, conditional determination (H-25) with the S10 verbatim quote. It is **not** stated as established, because owner-occupancy of the second unit is not in the brief. |
| C-2 | **The licensing steps and the Housing Inventory page described the base-rent field loosely.** S03 requires base rent "in $250.00 increments", which the step text paraphrased away. | `hub/data.json`, `hub/licensing.html` | Field description now records the $250-increment requirement exactly as the live page states it, and notes that an approximate answer is accepted without penalty. |
| C-3 | **`meta.retrieved` still read 2026-11-10**, so the published pages understated the verification date. | `hub/data.json` | Advanced to **2026-11-11** now that every source has actually been re-read on that date. |

---

## 4. Irregularities found and published, not silently corrected

| ID | Severity | Item |
| --- | --- | --- |
| H-25 | high | Whether the AB 1482 two-unit owner-occupied exemption applies here is unknown: the brief says two units but does not say whether the owner ever occupied the second. It is irrelevant while local rent control *does* apply to these units (S10 says the state cap "does NOT apply" to locally controlled units), but it matters to any statement that these units are controlled at all. |
| URL-1 | low | The registered URL for S01 is the double-dash form `…/information/sec-3715-reporting-obligations-licensing`. The page resolves and the content is correct, but the canonical form used by the site's own link text is the single-dash `information--` pattern. Recorded, not changed, because the resolving URL resolves and gates check it. |
| AB-1 | low | `hub/data.json` has no explicit AB 1482 CPI row, so the 8.8% figure on `hub/limits.html` is carried in prose rather than recomputed from a CPI input. It is quoted verbatim from S10 so it is not at risk of arithmetic drift, but it is not machine-checked against a stored input. |

---

## 5. Gates run after the corrections

| Gate | Result |
| --- | --- |
| `python3 hub/build.py` | regenerates all 9 pages |
| `python3 assurance/build.py` | regenerates assurance page + manifest |
| `python3 tools/verify_hub.py` | see COORDINATION.md record |
| `python3 tools/verify_assurance.py` | see COORDINATION.md record |
| `python3 tools/check_links.py` | OK — 10 published pages, all internal links/anchors resolve |
| `python3 tools/check_site.py` | 781 checks, 0 errors |

**Privacy.** No name, initial, street address, e-mail address or telephone number from the owner's
brief appears in any file written by this session. Units appear as Unit 1 / Unit 2 and occupants as
placeholders. Supplied dates and dollar amounts are unchanged.
