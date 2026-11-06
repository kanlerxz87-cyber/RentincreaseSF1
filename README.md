# Rent Increase SF

A verified, source-linked analysis of what a lawful rent increase is for two rent-controlled units in a 1940 building in San Francisco's Outer Sunset, ZIP 94122.

**Live site:** https://kanlerxz87-cyber.github.io/RentincreaseSF1/

---

## What is here

| Path | What it is |
|---|---|
| `index.html` … `method.html` | The published site. 12 static pages, plain HTML + one CSS file, no JavaScript, no CDN. |
| `EXECUTIVE-SUMMARY.md` | The executive summary as a document. |
| `SOURCES.md` | Human-readable source register. |
| `VERIFICATION.md` | What was checked, how, and what could not be confirmed. |
| `COORDINATION.md` | Shared task board for parallel agent sessions. |
| `data/*.json` | **The single source of truth.** Every fact on the site is read from here. Nothing is hard-coded twice. |
| `build/build.py` | Static site generator. Reads `data/`, writes the HTML. |
| `assets/style.css` | The only stylesheet. |
| `tools/check_site.py` | Verification: internal links, anchors, source links per table row, privacy, arithmetic. |

## Rebuild and verify

```bash
python3 build/build.py     # regenerate all pages from data/
python3 tools/check_site.py # 491 checks; exit 0 = clean
```

`tools/check_site.py` fails the build on: a broken internal link or anchor, a source URL missing from the site, an inline reference to an unknown source id, a table row with neither a source link nor an unverified marker, any personal name appearing in output, or any arithmetic figure that does not recompute from the published percentages.

## Data files

| File | Contents |
|---|---|
| `sources.json` | 36 official sources + tier + retrieval date + what each was verified for |
| `aga.json` | Every published allowable annual increase, 1982–2027, from the Rent Board's official PDF |
| `units.json` | Anonymised unit facts, every calculation scenario, arithmetic notes |
| `requirements.json` | 31 requirements across local, state and federal law |
| `procedure.json` | The 9-step compliant sequence and the lawful/unlawful reasons table |
| `practice.json` | Large-owner vs individual-owner comparison (behaviour rows deliberately blank) |
| `differential.json` | The one-unit-vs-both analysis |
| `tests.json` | The 14-point tenant-lawyer review test |
| `flags.json` | 13 flagged items with severity, impact and resolution |

## Verification standard

Every value in a table is traceable to a numbered source linked in the same row. **Where a value could not be confirmed from an official source it is left blank, marked unverified, and listed on the Flagged for Review page.** Values are never inferred or filled in. Commercial sources are labelled and are never the basis for a number.

## Privacy

Tenant names are replaced with role labels (Tenant A–F) throughout. Dates and dollar amounts are unchanged. **No name map exists in this repository.** Do not add one.

## Notes for future sessions

Read `COORDINATION.md` first. The site's shared outputs (`data/`, the pages, navigation) are only changed by an integration session once any other session's work is complete.

---

*This repository contains an analysis of public law. It is not legal advice.*
