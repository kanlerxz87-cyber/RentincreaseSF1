# Coordination

Session: arena-2347590f. Branch: arena/2347590f-rentincreasesf1 (platform-fixed; separate session branches cannot be created here).

| Task | Status | Owner | File scope |
|---|---|---|---|
| Official-source research, privacy-safe dashboard, verification and final integration | in progress | arena-2347590f | COORDINATION.md, README.md, index.html, .nojekyll, docs/**, scripts/**, .github/workflows/** |

Initial inspection: repository contains only README.md; no other claims or implementation found. No personal identifiers will be committed. User-provided dates and amounts will be explicitly unverified, not represented as official records. Shared integration owned by this session because no other tasks are claimed.

Scope expansion: final integration owns root index.html and .nojekyll to accommodate existing GitHub Pages legacy publication from main root. API update to workflow publishing returned 403; preserve the existing configuration rather than require user input.

## Research / integration review — 2026-11-06
- Official sources retrieved: SF annual 2026 announcement, rent guide, coverage, inventory, banking, petitions and tenant/landlord help; California legislative §§827, 1947.12, 1942.5; CRD housing; HUD Fair Housing Act overview. Source URLs are enumerated in docs/data.json and the site's Sources page.
- Row-by-row substantive review separates verified guidance, analysis, derived arithmetic and unverified supplied context. No private fact is marked officially confirmed. No original personal initials were stored.
- Flags F01–F09 published on docs/flagged.html: coverage, ledger, continuity, license/lease, market norms, lawyer approval, source example date errors, privacy limits and verification scope. These are needs review and do not block publication.
- Tests: seven generated pages; 66 rows with official links; source domain/key checks; internal asset/navigation existence; exact-cent calculation checks; JavaScript syntax. No installed browser automation; visual browser testing not claimed. External pages retrieved using official-page tools; no assertion of exhaustive case-law/lease review.
- Initial remote branch pull failed because branch did not exist; rebased against origin/main and pushed the claim. No conflicts and no other sessions found.
- Pages API: existing main-root legacy configuration confirmed. Changing configuration denied 403; using root redirect to docs and legacy deployment instead. No authentication secrets requested.
