# SF Rental Review

Privacy-first, source-linked research dashboard for two anonymized San Francisco rental units.

**Site:** https://kanlerxz87-cyber.github.io/RentincreaseSF1/

## Run and verify

Requires Python 3 (standard library only):

```sh
python scripts/build.py
python scripts/verify.py
python -m http.server 8000 --bind 0.0.0.0 --directory docs
```

`docs/data.json` is the canonical, anonymized row dataset. `scripts/build.py` produces the committed HTML. All navigation and assets are relative for project-based GitHub Pages. No analytics, third-party fonts, external runtime dependencies or user-input storage. Search runs entirely in the browser. GitHub Actions verifies the site. Existing GitHub Pages legacy publishing serves main at the repository root; root `index.html` forwards to `docs/index.html`. Changing Pages settings was denied (403), so the existing publishing configuration is preserved.

## Verification and boundaries

Official sources were retrieved on November 6, 2026 using official-page retrieval, with statements checked against the relevant sections. Source links accompany every finding. See Sources & Methodology and Flagged for Review on the site. Automated verification checks source domains and keys, row schema, internal file links, reproducible generation and exact-cent illustrative calculations. It does **not** certify external availability forever, legal validity, complete case law, private leases or property records.

User-supplied dates/rents appear in a separate narrative context and are not claimed as official-confirmed values. Official-confirmation cells remain empty for unverified facts, analysis and calculations. No original personal initials, identity map, street address, parcel or private documents are stored. Public dates/rents/area still present residual re-identification risk. No rent notices have been served and no legal approval is asserted.

Reviewed agency sources include SF Rent Board rules, annual rate announcement, housing inventory, banking, coverage and petitions; California Civil Code §§827, 1947.12 and 1942.5; California CRD; HUD; and SF tenant/landlord resources. Search snippets were not preferred over retrieved official page content. Inconsistent dates in official SF worked examples are explicitly flagged; examples were not used to override the announced effective periods.

No empirical official source was established for typical corporate, individual-owner or Outer Sunset market increases; those values remain unverified. No speculative banking total, legal anniversary, coverage determination or effective date is supplied.
