import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { buildSite, isOfficialUrl } from '../scripts/build.mjs';
import { containsPrivateIdentifier, loadLocalPrivateIdentifiers } from '../scripts/privacy.mjs';

const root = path.resolve(import.meta.dirname, '..');
const outDir = path.join(root, '.tmp', 'site-test');
const result = buildSite({ root, outDir });
const data = JSON.parse(fs.readFileSync(path.join(root, 'analysis/dashboard.json'), 'utf8'));
const sources = JSON.parse(fs.readFileSync(path.join(root, 'research/sources.json'), 'utf8')).sources;

test('build produces every categorized page and public data exports', () => {
  assert.equal(result.pages, data.pages.length + 1);
  assert.equal(result.sources, 33);
  assert.equal(result.flags, 16);
  for (const page of data.pages) assert.ok(fs.existsSync(path.join(outDir, page.file)), page.file);
  for (const file of ['data/sources.json', 'data/dashboard.json', 'data/official-benchmarks.csv', 'data/review-flags.csv', '404.html', '.nojekyll']) assert.ok(fs.existsSync(path.join(outDir, file)), file);
});
test('every generated substantive table row has an official source link', () => {
  let rows = 0;
  for (const page of data.pages) {
    const html = fs.readFileSync(path.join(outDir, page.file), 'utf8');
    for (const match of html.matchAll(/<tr data-status="[^"]+"[^>]*>([\s\S]*?)<\/tr>/g)) {
      rows += 1;
      const links = [...match[1].matchAll(/href="(https:[^"]+)"/g)].map(link => link[1].replace(/&amp;/g, '&'));
      assert.ok(links.length > 0, `Unsourced row in ${page.file}`);
      assert.ok(links.every(isOfficialUrl), `Non-official row link in ${page.file}`);
    }
  }
  assert.ok(rows >= 120);
});
test('blank values are visibly flagged and no unknown is silently zero-filled', () => {
  const units = fs.readFileSync(path.join(outDir, 'units.html'), 'utf8');
  const market = fs.readFileSync(path.join(outDir, 'market.html'), 'utf8');
  const review = fs.readFileSync(path.join(outDir, 'review.html'), 'utf8');
  assert.match(units, /blank-value[\s\S]*?Flagged for Review/);
  assert.match(market, /FY 2027[\s\S]*?blank-value[\s\S]*?Flagged for Review/);
  assert.match(review, /Missing value/);
  const flags = JSON.parse(fs.readFileSync(path.join(outDir, 'data/dashboard.json'), 'utf8')).flags;
  assert.ok(flags.every(flag => flag.missing === null));
});
test('public output contains no private structure or local intake path', () => {
  for (const file of ['data/dashboard.json', 'data/sources.json', 'index.html', 'units.html']) {
    const text = fs.readFileSync(path.join(outDir, file), 'utf8');
    assert.ok(!/resident_initials|alias_map|private\/intake/.test(text), file);
  }
  const identifiers = loadLocalPrivateIdentifiers(root);
  if (identifiers.length) {
    for (const file of fs.readdirSync(outDir).filter(file => file.endsWith('.html'))) assert.equal(containsPrivateIdentifier(fs.readFileSync(path.join(outDir, file), 'utf8'), identifiers), false, file);
  }
  assert.equal(containsPrivateIdentifier('Public research notes contain ordinary words.', ['X Y']), false);
});
test('official URL policy rejects arbitrary hosts and accepts primary publishers', () => {
  assert.ok(isOfficialUrl('https://www.sf.gov/reports--rent-ordinance'));
  assert.ok(isOfficialUrl('https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=CIV&sectionNum=827.'));
  assert.ok(isOfficialUrl('https://codelibrary.amlegal.com/codes/san_francisco/latest/sf_admin/0-0-0-70881'));
  assert.ok(!isOfficialUrl('https://example.com/legal'));
  assert.ok(!isOfficialUrl('http://www.sf.gov/page'));
  assert.ok(!isOfficialUrl('https://codelibrary.amlegal.com/codes/other_city/latest/page'));
});
test('all source references resolve and navigation is present on every page', () => {
  const ids = new Set(sources.map(source => source.id));
  for (const page of data.pages) {
    const html = fs.readFileSync(path.join(outDir, page.file), 'utf8');
    for (const item of data.pages) assert.ok(html.includes(`href="${item.file}"`), `${page.file} missing ${item.file}`);
    for (const section of page.sections) if (section.type === 'table') for (const row of section.rows) for (const id of row.source_ids) assert.ok(ids.has(id));
  }
});
test('CSV exports retain official source URLs on every data row', () => {
  for (const file of ['official-benchmarks.csv', 'review-flags.csv']) {
    const lines = fs.readFileSync(path.join(outDir, 'data', file), 'utf8').trim().split('\n');
    for (const line of lines.slice(1)) assert.match(line, /https:\/\//);
  }
});
test('build rejects an unsourced table row', () => {
  const fixture = path.join(root, '.tmp', 'invalid-fixture');
  fs.mkdirSync(path.join(fixture, 'analysis'), { recursive: true });
  fs.mkdirSync(path.join(fixture, 'research'), { recursive: true });
  fs.cpSync(path.join(root, 'site', 'src'), path.join(fixture, 'site', 'src'), { recursive: true });
  fs.copyFileSync(path.join(root, 'research/sources.json'), path.join(fixture, 'research/sources.json'));
  const broken = structuredClone(data);
  const table = broken.pages.flatMap(page => page.sections).find(section => section.type === 'table');
  table.rows[0].source_ids = [];
  fs.writeFileSync(path.join(fixture, 'analysis/dashboard.json'), JSON.stringify(broken));
  assert.throws(() => buildSite({ root: fixture, outDir: path.join(fixture, 'public') }), /Invalid table row/);
});
