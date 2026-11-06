"""Build a dependency-free, accessible, static research dashboard."""
import json
from html import escape as e
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'docs'
data=json.loads((out/'data.json').read_text())
for slug,(title,subtitle,rows) in data['pages'].items():
    nav=''.join(f'<a {"aria-current=page" if key==slug else ""} href="{key}.html">{e(page[0])}</a>' for key,page in data['pages'].items())
    body=''
    for i,(topic,finding,status,sources) in enumerate(rows,1):
        links='<br>'.join(f'<a href="{e(data["sources"][s][1],quote=True)}">{e(data["sources"][s][0])} ↗</a>' for s in sources)
        cls='verified' if status.startswith('Verified') else 'review' if status in ('Unverified','Needs review') else 'analysis'
        # An empty official-confirmed value is intentional for unverified private facts.
        value='Source-backed rule' if cls=='verified' else ''
        body+=f'<tr id="row-{i}"><th scope="row">{e(topic)}</th><td>{e(finding)}</td><td>{value}</td><td><span class="tag {cls}">{e(status)}</span></td><td>{links}</td></tr>'
    cards=''
    if slug=='index':
        cards='<div class="cards"><a href="law.html"><small>Published annual allowance</small><strong>1.6%</strong><span>Mar 2026 – Feb 2027 · covered units</span></a><a href="units.html"><small>Research scope</small><strong>2 units</strong><span>Anonymized · supplied rents unverified</span></a><a href="flagged.html"><small>Before implementation</small><strong>Review gates</strong><span>Coverage · ledger · license · notice</span></a></div>'
    html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Privacy-first San Francisco rent-control research with official sources and transparent review flags."><title>{e(title)} | SF Rental Review</title><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#main">Skip to findings</a><aside><a class="brand" href="index.html"><span class="mark">SF</span> Rental Review</a><p class="side-label">RESEARCH DASHBOARD</p><nav aria-label="Main navigation">{nav}</nav><div class="side-note">Public research only<br>No personal identifiers<br><b>As of {data['checked']}</b></div></aside>
<main id="main"><header><span>HOUSING / SAN FRANCISCO</span><button type="button" onclick="window.print()">Print / save PDF</button></header><p class="eyebrow">OUTER SUNSET · 94122 · ANONYMIZED</p><h1>{e(title)}</h1><p class="subtitle">{e(subtitle)}</p>{cards}<div class="notice"><b>Know what is verified.</b> Official rules are distinguished from analysis, conditional arithmetic and unverified supplied facts. Blank official-confirmation cells mean no official-confirmed value. A linked agency guide does not verify a private lease. This is not legal advice.</div><section aria-label="Research findings"><div class="table-heading"><h2>Findings & evidence</h2><label>Filter this page <input type="search" id="filter" placeholder="Search findings…"></label></div><p class="table-hint">Every row links to official guidance. Calculations are derived, not official determinations. On small screens, scroll the table horizontally.</p><div class="table-wrap"><table><caption class="sr-only">{e(title)} findings with verification status and official sources</caption><thead><tr><th scope="col">Topic</th><th scope="col">Finding / supplied context</th><th scope="col">Official confirmation</th><th scope="col">Status</th><th scope="col">Official sources</th></tr></thead><tbody>{body}</tbody></table></div><p id="count" aria-live="polite">{len(rows)} findings</p></section><footer>SF Rental Review · Official sources retrieved November 6, 2026 · No tracking, accounts, or external assets.<br>Read <a href="flagged.html">Flagged for Review</a> before relying on any illustration. Research publication is not authorization to increase rent.</footer></main><script src="site.js"></script></body></html>'''
    (out/f'{slug}.html').write_text(html)
(out/'.nojekyll').touch()
print(f'Built {len(data["pages"])} pages')
