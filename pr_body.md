## Summary

Adds a clean 11-page dashboard at `/review/` that puts the owner's most important question — "As an individual (non-corporate) small-property owner, do I need a Rent Board rent-increase license before notifying tenants?" — at the top of the landing page, answered directly from official SF.gov sources.

## Front-and-centre answer (from SF.gov)

**Yes.** San Francisco Administrative Code §37.15 (Ordinance 265-20, eff. 1/18/2021) requires ALL owners of residential property to report into the Rent Board Housing Inventory and hold a current rent-increase license on the effective date of any annual or banked increase. There is NO individual/small-building exemption. For buildings with fewer than 10 units the requirement took effect 3/1/2023. The license is generated automatically when you report a tenant-occupied unit via the Rent Board Portal. An increase imposed while unlicensed is null and void even if the arithmetic is correct.

## Pages in `/review/`

1. Executive Summary (landing page with key numbers)
2. Rent Board License Q&A
3. Step-by-step Process (8 steps)
4. Unit Calculations (Unit 1 +$63.92; Unit 2 +$50.40 annual / +$412.65 banked max at 13.1%)
5. Allowable Rates history
6. Notice Protocol and lawful/unlawful reasons
7. Market Practices (corporate vs individual)
8. Discrimination and Scrutiny (raising one unit vs both)
9. Tenant-Lawyer Checklist
10. Sources (14 official)
11. Flagged for Review (9 items)

## Sources used (all official .gov)

- SF.gov / SF Rent Board: Learn about rent increases; Housing Inventory FAQ; Ordinance 265-20; 1.6% rate announcement for 3/1/2026–2/28/2027; current rates page; Form 571; Rent Board fee page; Rent Board Portal.
- California Legislative Information: Civil Code §827 (notice); CCP §1013 (mail service +5 days); Civil Code §1947.12 (state cap — preempted by stricter SF local law); Gov. Code §12955 (FEHA).
- U.S. Government Publishing Office: 42 U.S.C. §3604 (Fair Housing Act).

## Verification

- `python3 review/verify.py` passes: 11 pages, 14 sources, all relative links resolve, privacy scan clean, decimal arithmetic recomputed exactly ($63.92, $50.40, $412.65, 13.1%).
- Local HTTP smoke test via `python3 -m http.server`: 200 OK on all 12 URLs.
- Privacy: no tenant names, initials, emails or street address appear in `review/**`; dates/rents/percentages preserved.
- One additive change to root `index.html`: a single card link added in the "Other editions" grid pointing to `review/`.

## Flagged items (do not block merge; published on Flagged for Review)

F1 license status unverified, F2 Unit 1 banking look-back ambiguity, F3 Unit 2 zero-increase assumption, F4 Unit 1 occupant-change classification, F5 retaliation-window maintenance history, F6 2027-28 rate not yet published, F7 beds/sqft not supplied, F8 subsidy status, F9 street address intentionally withheld for privacy.

Not legal advice — informational summary of official sources.
