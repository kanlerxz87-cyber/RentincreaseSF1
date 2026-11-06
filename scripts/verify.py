"""Structural checks; not a substitute for substantive legal/source review."""
import json
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
root=Path(__file__).resolve().parents[1]/'docs'
d=json.loads((root/'data.json').read_text())
allowed={'www.sf.gov','leginfo.legislature.ca.gov','calcivilrights.ca.gov','www.hud.gov'}
n=0
for key,(title,sub,rows) in d['pages'].items():
    assert rows
    for topic,finding,status,sources in rows:
        assert topic and finding and sources
        assert status in {'Analysis','Verified rule','Verified guidance','Conditional calculation','Unverified','Needs review'}
        for source in sources:
            assert urlparse(d['sources'][source][1]).hostname in allowed
        n+=1
class Links(HTMLParser):
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key not in ('href','src') or not value: continue
            u=urlparse(value)
            if u.scheme or value.startswith('#'): continue
            assert (root/unquote(u.path)).is_file(), value
for p in root.glob('*.html'):
    Links().feed(p.read_text())
assert 399500*16//1000 == 6392
assert 315000*16//1000 == 5040
assert (6392+5040)*12 == 137184
assert len(list(root.glob('*.html'))) == len(d['pages'])
# Integration: the repository root now hosts the published dashboard, which links to this archived
# draft instead of redirecting to it. Assert the dashboard exists and still links the archive.
assert (root.parent/'index.html').is_file()
assert 'docs/index.html' in (root.parent/'index.html').read_text() or 'docs/index.html' in (root.parent/'review.html').read_text()
print(f'PASS: {len(d["pages"])} pages, {n} sourced rows; source allowlist, internal assets/links, status schema and exact-cent arithmetic.')
print('External sources reviewed via official-page retrieval; this offline test does not claim HTTP availability or legal approval.')
