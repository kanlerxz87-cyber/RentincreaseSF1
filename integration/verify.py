#!/usr/bin/env python3
"""Offline checks for integration site and exposed historical identity strings.
External source availability/content requires separately checking the official websites.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from decimal import Decimal
import hashlib, re, subprocess

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'integration'
# Digests avoid putting identifiers themselves in a public verification file.
DIGESTS={'01efd0141d7d80509ee44bbbb2dee48875711d55358bd9a91bf22d5208ffa93d','0b28c4215599de9c8f7019402d7eaeccc8cbdc5103aeca7427774222c2bf2f16','158dc33a8be8ae49804b3fa72e2e116edb683730b51752bdb552435f31f0ba5a','27c9478468718ed43669f8b2bbac3694d1f03287a6347d4c9adadc9d12f9ecf5','399ad8e221e6815cd19b54cd7f313335f9bab0ecc681615af552c64ea3901b0f','569ec6135d377e8ac326be2be2fd4cd8f3538fc3c23f33a89e81a4ed83671b7e'}
OFFICIAL={'www.sf.gov','sf.gov','portal.sfrb.org','leginfo.legislature.ca.gov','www.govinfo.gov'}
errors=[]; rows=0
class Parser(HTMLParser):
 def __init__(self):
  super().__init__(); self.hrefs=[]; self.ids=set(); self.inbody=False; self.inrow=False; self.row_sources=[]; self.rows=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a: self.ids.add(a['id'])
  if tag=='tbody': self.inbody=True
  if tag=='tr' and self.inbody: self.inrow=True; self.row_sources=[]
  if tag in ('a','link') and ('href' in a):
   self.hrefs.append(a['href'])
   if self.inrow and urlsplit(a['href']).hostname in OFFICIAL:self.row_sources.append(a['href'])
 def handle_endtag(self,tag):
  if tag=='tr' and self.inrow: self.rows.append(self.row_sources); self.inrow=False
  if tag=='tbody': self.inbody=False
pages={p:Parser() for p in SITE.glob('*.html')}
for p,parser in pages.items(): parser.feed(p.read_text())
for p,parser in pages.items():
 for row in parser.rows:
  rows+=1
  if not row: errors.append(f'{p.name}: row lacks official source')
 for href in parser.hrefs:
  u=urlsplit(href)
  if u.scheme:
   if u.scheme!='https' or u.hostname not in OFFICIAL: errors.append(f'{p.name}: non-official link {href}')
  else:
   target=(p.parent/unquote(u.path)).resolve() if u.path else p.resolve()
   if not target.is_file(): errors.append(f'{p.name}: missing {href}')
   elif u.fragment and target in pages and u.fragment not in pages[target].ids: errors.append(f'{p.name}: missing fragment {href}')
assert Decimal('3995')*Decimal('.016')==Decimal('63.92')
assert Decimal('3150')*Decimal('.016')==Decimal('50.40')
# Scan tracked public text and new integration files; avoid exposing matched values in output.
files=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
files+=['integration/verify.py']
for rel in set(files):
 p=ROOT/rel
 if not rel or not p.is_file():continue
 try: text=p.read_text(encoding='utf-8')
 except (UnicodeError,OSError): continue
 for token in re.findall(r'\b(?:[A-Z]{2}|[A-Z] [A-Z])\b',text):
  if hashlib.sha256(token.encode()).hexdigest() in DIGESTS:
   errors.append(f'{rel}: private token found'); break
if len(pages)!=6:errors.append(f'expected 6 pages, found {len(pages)}')
if errors:
 print('\n'.join(errors)); raise SystemExit(1)
print(f'PASS: {len(pages)} pages, {rows} source-linked rows, local links, arithmetic, tracked-text privacy scan')
