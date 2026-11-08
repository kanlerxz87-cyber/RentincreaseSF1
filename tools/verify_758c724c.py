#!/usr/bin/env python3
"""Session 758c724c gate: research registry, canonical citations, blanks, privacy, reproducibility."""
from __future__ import annotations
import hashlib, html, json, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from check_links import FORBIDDEN_HASHES  # noqa: E402
errors=[]; checks=0

def check(cond,msg):
    global checks; checks+=1
    if not cond: errors.append(msg)

def load(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8'))
research=load('research/758c724c/official-sources.json')
hub=load('hub/data.json')
findings=load('research/758c724c/findings.json')['findings']
rids=[s['id'] for s in research]; hids=[s['id'] for s in hub['sources']]
check(len(research)==44 and len(set(rids))==44,'research registry must contain 44 unique sources')
check(rids==hids,'canonical source IDs/order differ from research registry')
rby={s['id']:s for s in research}; hby={s['id']:s for s in hub['sources']}
for s in research:
    check(s.get('official') is True,f"{s['id']}: not marked official")
    check(s['url'].startswith('https://'),f"{s['id']}: non-HTTPS source")
    check(bool(s.get('quote','').strip()),f"{s['id']}: empty supporting passage")
    check(s.get('retrieved') in ('2026-11-07','2026-11-08'),f"{s['id']}: unexpected retrieval date")
    check(hashlib.sha256(s['quote'].encode()).hexdigest()==s.get('excerpt_sha256'),f"{s['id']}: excerpt digest mismatch")
    h=hby.get(s['id'],{})
    check(h.get('url')==s['url'],f"{s['id']}: canonical URL mismatch")
    check(h.get('quote')==s['quote'],f"{s['id']}: canonical passage mismatch")
    check(h.get('retrieved')==s['retrieved'],f"{s['id']}: canonical retrieval date mismatch")
ids=set(hids)
for f in findings:check(set(f['sources'])<=ids,f"{f['id']}: unknown source")
for key in ('licensing_steps','process_steps','notice_rows','reasons','practice_rows','fair_housing_rows','review_rows','flags'):
    for i,row in enumerate(hub[key]):
        check(bool(row.get('sources')),f"{key}[{i}]: missing official sources")
        check(set(row.get('sources',[]))<=ids,f"{key}[{i}]: unknown source")
check(len(hub['flags'])>=28,'expected at least 28 flags')
check(len(hub['review_rows'])>=16,'expected at least 16 review checks')
check(len(hub['licensing_steps'])>=10,'expected at least 10 licensing Q&A rows')
check(len(hub['process_steps'])>=10,'expected at least 10 process steps')
check(len(hub['notice_rows'])>=12,'expected at least 12 notice elements')
check(len(hub['reasons'])>=11,'expected at least 11 reason rows')
for row in hub['notice_rows']:
    check(row['item'].startswith(('Required','Conditional','Recommended','Prohibited')),f"notice row lacks status prefix: {row['item']}")
flag={f['id']:f for f in hub['flags']}
for fid in ('H-21','H-22','H-23','H-24','H-25','H-26','H-27','H-28'):check(fid in flag,f'missing flag {fid}')
check('not established' in flag['H-21']['detail'].lower() or 'Not established' in hub['licensing_steps'][8]['answer'],'business-registration answer must remain conditional')
check('No passthrough dollar amount' in flag['H-25']['detail'],'bond amount must remain explicitly uncalculated')
check('Pending Committee Action' in flag['H-22']['detail'] and 'not law' in flag['H-22']['detail'],'pending cap must not be treated as law')
for rel,minimum,needles in (('index.html',9,('H-21','H-25')),('hub/flags.html',10,('H-21','H-25'))):
    doc=(ROOT/rel).read_text(encoding='utf-8')
    check(doc.count('<td></td>')>=minimum,f'{rel}: unsupported blank cells were filled')
    for n in needles:check(f'flags.html#{n}' in doc,f'{rel}: missing blank-row flag link {n}')
# Current-text privacy scan over the published/canonical/research surface.
token_re=re.compile(r'\b[A-Z]\.(?:[A-Z]\.)+\b|\b[A-Z]{2,}\b')
email_re=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
scanned=0
for base in ('index.html','hub','assurance','research/758c724c','EXECUTIVE_SUMMARY.md','SOURCES.md','VERIFICATION.md','README.md'):
    p=ROOT/base
    files=[p] if p.is_file() else sorted(p.rglob('*')) if p.is_dir() else []
    for path in files:
        if not path.is_file() or path.suffix.lower() not in {'.html','.json','.md','.py','.css','.txt'}:continue
        text=path.read_text(encoding='utf-8',errors='ignore');scanned+=1
        visible=html.unescape(re.sub(r'<[^>]+>',' ',text))
        for token in token_re.findall(visible):
            check(hashlib.sha256(token.encode()).hexdigest() not in FORBIDDEN_HASHES,f'{path.relative_to(ROOT)}: forbidden personal token')
        check(not email_re.search(text),f'{path.relative_to(ROOT)}: email address present')
check(scanned>=20,f'privacy scan covered too few files: {scanned}')
# Reproducibility: regenerate and require no drift in committed generated surfaces.
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for cmd in (['python3','hub/build.py'],['python3','assurance/build.py'],['python3','review/build.py'],['python3','build/build.py']):
    proc=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True)
    check(proc.returncode==0,f"builder failed: {' '.join(cmd)}: {proc.stderr[-300:]}")
drift=subprocess.run(['git','diff','--quiet','--','index.html','hub/','assurance/','audit/final-integration/source-manifest.json','review/','docs/v2/'],cwd=ROOT,env=env)
check(drift.returncode==0,'generated output drift after rebuild; commit regenerated files')
check('datetime.date.today()' not in (ROOT/'review/build.py').read_text(encoding='utf-8'),'review generator still stamps wall-clock date')
check((ROOT/'assurance/758c724c/index.html').is_file(),'missing session assurance report')
print(f'session sources: {len(research)}; flags: {len(hub["flags"])}; review checks: {len(hub["review_rows"])}')
print(f'privacy files scanned: {scanned}')
print(f'checks passed: {checks-len(errors)}')
if errors:
    for e in errors:print('FAIL:',e,file=sys.stderr)
    raise SystemExit(1)
print('no errors')
