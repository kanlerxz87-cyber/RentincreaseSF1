# Independent verification dashboard

This directory is the file scope of session `arena/dd1caa16-rentincreasesf1`. It is
deliberately disjoint from `docs/**`, `site/**`, `research/**`, `data/*.csv`,
`tools/**`, `scripts/**`, `.github/workflows/**`, root `index.html`, and
`README.md`, which are owned by other sessions.

```
python3 build.py     # regenerate index.html and pages/** from data/site_data.json
python3 verify.py    # line-by-line data, source-link, link, nav, arithmetic, privacy checks
```

GitHub Pages serves this dashboard at `https://kanlerxz87-cyber.github.io/RentincreaseSF1/dashboard/`.
No build service, network access, or third-party Python package is required.
