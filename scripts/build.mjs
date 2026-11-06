import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { assertNoSensitiveStructure, containsPrivateIdentifier, loadLocalPrivateIdentifiers } from './privacy.mjs';

const DEFAULT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const STATUSES = new Set(['verified', 'conditional', 'reported', 'flagged', 'historical', 'context']);
const STATUS_LABELS = { verified: 'Verified rule / data', conditional: 'Conditional', reported: 'Reported · unverified', flagged: 'Flagged for Review', historical: 'Historical', context: 'Context only' };
const SECTION_TYPES = new Set(['callout', 'stats', 'table', 'prose', 'links', 'calculator', 'flag-register', 'source-register']);

export function isOfficialUrl(value) {
  let url;
  try { url = new URL(value); } catch { return false; }
  if (url.protocol !== 'https:') return false;
  const host = url.hostname.toLowerCase();
  const officialHosts = ['sf.gov', 'leginfo.legislature.ca.gov', 'calcivilrights.ca.gov', 'hud.gov', 'huduser.gov', 'justice.gov', 'govinfo.gov'];
  if (officialHosts.some(domain => host === domain || host.endsWith(`.${domain}`))) return true;
  if (host === 'codelibrary.amlegal.com') return url.pathname.startsWith('/codes/san_francisco/');
  if (host === 'services.arcgis.com') return url.pathname.includes('/HUD_PDR_Small_Area_Fair_Market_Rents/');
  return false;
}

function esc(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function badge(status) {
  if (!STATUSES.has(status)) throw new Error(`Unknown status: ${status}`);
  return `<span class="badge badge-${status}">${esc(STATUS_LABELS[status])}</span>`;
}

function sourceLinks(ids, sources, label = true) {
  if (!Array.isArray(ids) || ids.length === 0) throw new Error('Missing official source reference');
  return `<span class="source-links">${label ? '<span class="source-label">Official source</span>' : ''}${ids.map(id => {
    const source = sources.get(id);
    if (!source) throw new Error(`Unknown source ID: ${id}`);
    return `<a class="source-link" href="${esc(source.url)}" target="_blank" rel="noopener noreferrer" title="${esc(source.title)}">${esc(id)}<span aria-hidden="true"> ↗</span><span class="sr-only"> (opens in a new tab)</span></a>`;
  }).join('')}</span>`;
}

function cell(value) {
  if (value === null || value === undefined || value === '') return '<span class="blank-cell"><span class="blank-value" aria-label="Value intentionally blank"></span><span class="inline-flag">Flagged for Review</span></span>';
  return esc(value);
}

function tableControls(page) {
  const jurisdictions = page.id === 'sources' ? '<label> Jurisdiction<select id="jurisdiction-filter"><option value="">All jurisdictions</option><option>San Francisco</option><option>California</option><option>Federal</option></select></label>' : '';
  return `<div class="table-controls" aria-label="Table filters"><label class="search-label">Filter tables on this page<input id="table-search" type="search" placeholder="Search rows, sources, or review notes…" autocomplete="off"></label><label>Status<select id="status-filter"><option value="">All statuses</option>${[...STATUSES].map(status => `<option value="${status}">${esc(STATUS_LABELS[status])}</option>`).join('')}</select></label>${jurisdictions}<button class="button button-quiet" id="clear-filters" type="button">Clear filters</button><p id="filter-summary" class="filter-summary" aria-live="polite"></p></div>`;
}

function renderTable(section, sources) {
  const columns = section.columns;
  const head = columns.map(column => `<th scope="col">${esc(column.label)}</th>`).join('') + '<th scope="col">Evidence status</th><th scope="col">Official source</th>';
  const rows = section.rows.map(row => {
    if (!row.source_ids?.length) throw new Error(`Table ${section.id} has an unsourced row`);
    const cells = columns.map(column => `<td data-label="${esc(column.label)}">${cell(row[column.key])}</td>`).join('');
    return `<tr data-status="${esc(row.status)}">${cells}<td data-label="Evidence status">${badge(row.status)}</td><td data-label="Official source">${sourceLinks(row.source_ids, sources, false)}</td></tr>`;
  }).join('');
  return `<section class="table-section" aria-labelledby="${esc(section.id)}-title"><div class="section-heading"><h2 id="${esc(section.id)}-title">${esc(section.title)}</h2>${section.description ? `<p>${esc(section.description)}</p>` : ''}</div><p class="scroll-hint">Scroll horizontally on narrow screens. Blank values are intentional and flagged.</p><div class="table-wrap" tabindex="0" role="region" aria-label="${esc(section.title)} table"><table id="${esc(section.id)}"><thead><tr>${head}</tr></thead><tbody>${rows}</tbody></table></div><p class="table-empty" hidden>No rows match the current filters.</p></section>`;
}

function renderSourceRegister(section, sources) {
  const rows = [...sources.values()].map(source => `<tr data-status="verified" data-jurisdiction="${esc(source.jurisdiction.startsWith('San Francisco') ? 'San Francisco' : source.jurisdiction.startsWith('California') ? 'California' : 'Federal')}"><td data-label="Source"><a href="${esc(source.url)}" target="_blank" rel="noopener noreferrer"><strong>${esc(source.id)}</strong><span aria-hidden="true"> ↗</span><span class="sr-only"> (opens in a new tab)</span></a><div class="cell-subtitle">${esc(source.title)}</div></td><td data-label="Publisher">${esc(source.publisher)}</td><td data-label="Jurisdiction">${esc(source.jurisdiction)}</td><td data-label="Source type">${esc(source.kind)}</td><td data-label="What it supports">${esc(source.evidence)}</td><td data-label="Verification note">${esc(source.verification_note)}<div class="cell-subtitle">Retrieved ${esc(source.verified_on)}</div></td></tr>`).join('');
  return `<section class="table-section" aria-labelledby="source-register-title"><div class="section-heading"><h2 id="source-register-title">${esc(section.title)}</h2><p>${esc(section.description)}</p></div><p class="scroll-hint">Every row links to the official source. Primary law, guidance, context, and benchmarks are labeled separately.</p><div class="table-wrap" tabindex="0" role="region" aria-label="Official source register"><table id="source-register"><thead><tr><th scope="col">Source</th><th scope="col">Publisher</th><th scope="col">Jurisdiction</th><th scope="col">Source type</th><th scope="col">What it supports</th><th scope="col">Verification note</th></tr></thead><tbody>${rows}</tbody></table></div><p class="table-empty" hidden>No sources match the current filters.</p></section>`;
}

function renderFlags(section, data, sources) {
  const rows = data.flags.map(flag => `<tr data-status="flagged"><td data-label="Flag">${esc(flag.id)}</td><td data-label="Topic">${esc(flag.topic)}</td><td data-label="Open item">${esc(flag.item)}</td><td data-label="Missing value">${cell(flag.missing)}</td><td data-label="Next evidence / action">${esc(flag.action)}</td><td data-label="Evidence status">${badge('flagged')}</td><td data-label="Official source">${sourceLinks(flag.source_ids, sources, false)}</td></tr>`).join('');
  return `<section class="table-section" aria-labelledby="flag-register-title"><div class="section-heading"><h2 id="flag-register-title">${esc(section.title)}</h2><p>${esc(section.description)}</p></div><div class="table-wrap" tabindex="0" role="region" aria-label="Open review flags"><table id="flag-register"><thead><tr><th scope="col">Flag</th><th scope="col">Topic</th><th scope="col">Open item</th><th scope="col">Missing value</th><th scope="col">Next evidence / action</th><th scope="col">Evidence status</th><th scope="col">Official source</th></tr></thead><tbody>${rows}</tbody></table></div><p class="table-empty" hidden>No flags match the current filters.</p></section>`;
}

function renderCalculator() {
  return `<section class="calculator" aria-labelledby="calculator-title"><div class="calculator-intro"><h2 id="calculator-title">Enter non-identifying planning inputs</h2><p>No names, addresses, or resident information. Inputs remain in this page and are not saved.</p><button type="button" class="button button-quiet" id="use-reported">Use reported Unit 1 amount ($3,995) — unverified</button></div><form id="rent-form" autocomplete="off"><div class="form-grid"><label>Base rent ($)<input id="base" type="number" min="0.01" max="1000000" step="0.01" inputmode="decimal" placeholder="Verified base rent only" aria-describedby="base-help"><span id="base-help" class="field-help">Do not enter a stale lease-start amount as verified rent.</span></label><label>Proposed effective date<input id="effective" type="date" min="2026-03-01" max="2027-02-28"></label><label>Verified rent-increase anniversary<input id="anniversary" type="date"></label><label>Last increase effective date<input id="last-increase" type="date" aria-describedby="last-help"><span id="last-help" class="field-help">Leave blank only with the explicit no-prior-increase attestation.</span></label><label class="checkbox-label"><input id="no-prior" type="checkbox"> I attest there was no prior increase in this tenancy.</label><label>Planned actual service date<input id="service-date" type="date"></label><label>Service method<select id="service-method"><option value="personal">Personal delivery</option><option value="mail-ca">Mail — within California (+5 calendar days)</option><option value="mail-us">Mail — elsewhere in US (+10 calendar days)</option><option value="mail-intl">Mail — outside US (+20 calendar days)</option><option value="overnight">Qualifying overnight delivery (+2 planning days)</option></select></label></div><fieldset class="attestations"><legend>Independent verification attestations</legend><p>Unchecked items keep the result conditional. Checking a box records your assertion only; it is not evidence or approval.</p><label class="checkbox-label"><input id="base-verified" type="checkbox"> I verified this is the current lawful base rent.</label><label class="checkbox-label"><input id="coverage-verified" type="checkbox"> I confirmed this unit is subject to the SF local annual cap.</label><label class="checkbox-label"><input id="compliance-verified" type="checkbox"> I verified inventory/license compliance, anniversary, lease terms, and required notice content.</label><label class="checkbox-label"><input id="exclusions-verified" type="checkbox"> This is a standalone ordinary increase: no banking, petition, passthrough, other prior-12-month increase, or program-specific rule applies.</label><label class="checkbox-label"><input id="review-verified" type="checkbox"> Independent legal review of notice, nondiscrimination, retaliation, and unit selection is complete.</label></fieldset><div class="calculator-actions"><button type="button" class="button button-primary" id="calculate">Calculate illustration</button><button type="button" class="button button-quiet" id="reset-calculator">Reset all inputs</button></div></form><div id="calculator-output" class="calculator-output" aria-live="polite" aria-atomic="true"><p class="output-placeholder">Enter values to see a conditional illustration. No lawful rent is determined here.</p></div></section>`;
}

function renderSection(section, data, sources) {
  switch (section.type) {
    case 'table': return renderTable(section, sources);
    case 'source-register': return renderSourceRegister(section, sources);
    case 'flag-register': return renderFlags(section, data, sources);
    case 'calculator': return renderCalculator();
    case 'callout': return `<aside class="callout callout-${esc(section.tone)}" aria-label="${esc(section.title)}"><h2>${esc(section.title)}</h2><p>${esc(section.text)}</p>${sourceLinks(section.source_ids, sources)}</aside>`;
    case 'stats': return `<div class="stat-grid">${section.items.map(item => `<article class="stat-card">${badge(item.status)}<p class="stat-label">${esc(item.label)}</p><p class="stat-value">${esc(item.value)}</p><p class="stat-detail">${esc(item.detail)}</p>${sourceLinks(item.source_ids, sources)}</article>`).join('')}</div>`;
    case 'prose': return `<section class="prose-section"><h2>${esc(section.title)}</h2>${section.paragraphs.map(paragraph => `<p>${esc(paragraph.text)} ${sourceLinks(paragraph.source_ids, sources, false)}</p>`).join('')}</section>`;
    case 'links': return `<section class="link-section"><h2>${esc(section.title)}</h2><div class="link-grid">${section.items.map(item => { const external = /^https?:/.test(item.url); return `<article class="link-card"><a href="${esc(item.url)}"${external ? ' target="_blank" rel="noopener noreferrer"' : ''}><strong>${esc(item.label)} <span aria-hidden="true">→</span></strong></a><span>${esc(item.description)}</span>${sourceLinks(item.source_ids, sources)}</article>`; }).join('')}</div></section>`;
    default: throw new Error(`Unknown section type: ${section.type}`);
  }
}

function layout(page, data, body, { notFound = false } = {}) {
  const nav = data.pages.map(item => `<a href="${esc(item.file)}"${item.id === page.id && !notFound ? ' aria-current="page"' : ''}><span>${esc(item.nav)}</span>${item.id === 'review' ? '<span class="nav-dot" aria-label="Open review flags"></span>' : ''}</a>`).join('');
  const hasTables = page.sections.some(section => ['table', 'source-register', 'flag-register'].includes(section.type));
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; base-uri 'self'; form-action 'none'"><meta name="description" content="${esc(page.description)}"><title>${esc(notFound ? 'Page not found' : page.nav)} · ${esc(data.title)}</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/styles.css"><script type="module" src="assets/app.js"></script></head>
<body><a class="skip-link" href="#main">Skip to content</a><div class="app-shell"><aside class="sidebar" id="sidebar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 32 32" fill="none"><path d="M5 27V12l11-7 11 7v15H5Z" stroke="currentColor" stroke-width="2"/><path d="M11 27v-8h10v8M10 13h3m6 0h3M16 5v-2" stroke="currentColor" stroke-width="2"/></svg></span><span>SF Rent Review<small>Official-source research</small></span></a><p class="sidebar-context">Outer Sunset · 94122<br>Reported two-unit property</p><nav aria-label="Main navigation">${nav}</nav><div class="sidebar-note"><strong>Evidence before assumptions</strong><p>Unknown values stay blank and flagged. No attorney endorsement is claimed.</p></div></aside><div class="content-shell"><header class="topbar"><button class="menu-button" id="menu-toggle" type="button" aria-expanded="false" aria-controls="sidebar"><span aria-hidden="true">☰</span><span class="sr-only">Toggle navigation</span></button><span class="topbar-title">${esc(data.title)}</span><span class="asof">Research cutoff <time datetime="${esc(data.as_of)}">Nov 6, 2026</time></span><button class="button button-quiet print-button" id="print-page" type="button">Print</button></header><main id="main" tabindex="-1"><header class="page-header"><p class="eyebrow">${esc(page.eyebrow)}</p><h1>${esc(page.title)}</h1><p class="page-description">${esc(page.description)}</p><div class="privacy-banner"><strong>Privacy & evidence</strong><p>${esc(data.privacy_notice)}</p></div></header>${hasTables && !notFound ? tableControls(page) : ''}${body}</main><footer class="site-footer"><p>${esc(data.disclaimer)}</p><p>Static site · no analytics · no account · calculator inputs are not transmitted or saved. <a href="sources.html">Official sources</a> · <a href="review.html">Flagged for Review</a> · <a href="https://github.com/kanlerxz87-cyber/RentincreaseSF1" target="_blank" rel="noopener noreferrer">Public repository ↗</a></p></footer></div></div></body></html>`;
}

function csv(rows) {
  return rows.map(row => row.map(value => `"${String(value ?? '').replace(/"/g, '""')}"`).join(',')).join('\n') + '\n';
}

function validateData(data, sourceList) {
  const sources = new Map(sourceList.map(source => [source.id, source]));
  if (sources.size !== sourceList.length) throw new Error('Duplicate source ID');
  for (const source of sourceList) {
    for (const field of ['id', 'title', 'publisher', 'jurisdiction', 'kind', 'url', 'verified_on', 'evidence', 'verification_note']) if (!source[field]) throw new Error(`Source ${source.id} missing ${field}`);
    if (!isOfficialUrl(source.url)) throw new Error(`Non-official source URL: ${source.id}`);
  }
  const files = new Set();
  for (const page of data.pages) {
    if (!/^[a-z0-9-]+\.html$/.test(page.file) || files.has(page.file)) throw new Error(`Invalid or duplicate page file: ${page.file}`);
    files.add(page.file);
    for (const section of page.sections) {
      if (!SECTION_TYPES.has(section.type)) throw new Error(`Invalid section type: ${section.type}`);
      if (section.source_ids) for (const id of section.source_ids) if (!sources.has(id)) throw new Error(`Unknown source ${id}`);
      if (section.type === 'table') {
        for (const row of section.rows) {
          if (!STATUSES.has(row.status) || !row.source_ids?.length) throw new Error(`Invalid table row in ${section.id}`);
          for (const id of row.source_ids) if (!sources.has(id)) throw new Error(`Unknown source ${id}`);
          for (const column of section.columns) if (!(column.key in row)) throw new Error(`Missing column ${column.key} in ${section.id}`);
        }
      }
      if (section.type === 'stats' || section.type === 'links' || section.type === 'prose') {
        const items = section.items ?? section.paragraphs;
        for (const item of items) for (const id of item.source_ids ?? []) if (!sources.has(id)) throw new Error(`Unknown source ${id}`);
      }
    }
  }
  for (const flag of data.flags) {
    if (flag.missing !== null || !flag.source_ids?.length) throw new Error(`Invalid flag ${flag.id}`);
    for (const id of flag.source_ids) if (!sources.has(id)) throw new Error(`Unknown source ${id}`);
  }
  assertNoSensitiveStructure(data);
  assertNoSensitiveStructure(sourceList);
  return sources;
}

function validateGeneratedLinks(outDir) {
  const htmlFiles = fs.readdirSync(outDir).filter(file => file.endsWith('.html'));
  const idsByFile = new Map(htmlFiles.map(file => [file, new Set([...fs.readFileSync(path.join(outDir, file), 'utf8').matchAll(/\bid="([^"]+)"/g)].map(match => match[1]))]));
  for (const file of [...htmlFiles, 'assets/app.js', 'assets/calculator-ui.js']) {
    const text = fs.readFileSync(path.join(outDir, file), 'utf8');
    const refs = [...text.matchAll(/(?:href|src)="([^"]+)"/g)].map(match => match[1]);
    for (const ref of refs) {
      if (/^(https?:|mailto:|tel:|data:)/.test(ref)) continue;
      const [target, anchor] = ref.split('#');
      const resolved = target ? path.resolve(path.dirname(path.join(outDir, file)), target) : path.join(outDir, file);
      if (!resolved.startsWith(path.resolve(outDir) + path.sep) || !fs.existsSync(resolved)) throw new Error(`Broken local link in ${file}: ${ref}`);
      if (anchor && target?.endsWith('.html') && !idsByFile.get(target)?.has(anchor)) throw new Error(`Broken anchor in ${file}: ${ref}`);
      if (anchor && !target && !idsByFile.get(file)?.has(anchor)) throw new Error(`Broken page anchor in ${file}: ${ref}`);
    }
  }
}

export function buildSite({ root = DEFAULT_ROOT, outDir = path.join(DEFAULT_ROOT, 'site', 'public') } = {}) {
  const data = JSON.parse(fs.readFileSync(path.join(root, 'analysis', 'dashboard.json'), 'utf8'));
  const sourceList = JSON.parse(fs.readFileSync(path.join(root, 'research', 'sources.json'), 'utf8')).sources;
  const sources = validateData(data, sourceList);
  const privateIdentifiers = loadLocalPrivateIdentifiers(root);
  fs.mkdirSync(outDir, { recursive: true });
  fs.mkdirSync(path.join(outDir, 'assets'), { recursive: true });
  fs.mkdirSync(path.join(outDir, 'data'), { recursive: true });
  for (const page of data.pages) {
    const body = page.sections.map(section => renderSection(section, data, sources)).join('\n');
    fs.writeFileSync(path.join(outDir, page.file), layout(page, data, body));
  }
  const notFoundPage = { ...data.pages[0], title: 'That page is not in this research project', description: 'Use the navigation to return to the overview or open the official-source register.', eyebrow: '404', sections: [] };
  fs.writeFileSync(path.join(outDir, '404.html'), layout(notFoundPage, data, '<p><a class="button button-primary" href="index.html">Return to the overview</a></p>', { notFound: true }));
  for (const asset of ['styles.css', 'app.js', 'rent-math.js', 'calculator-ui.js', 'favicon.svg']) fs.copyFileSync(path.join(root, 'site', 'src', asset), path.join(outDir, 'assets', asset));
  fs.writeFileSync(path.join(outDir, 'data', 'sources.json'), JSON.stringify({ verified_on: data.as_of, sources: sourceList }, null, 2) + '\n');
  fs.writeFileSync(path.join(outDir, 'data', 'dashboard.json'), JSON.stringify(data, null, 2) + '\n');
  const benchmarkTable = data.pages.find(page => page.id === 'market').sections.find(section => section.id === 'hud-benchmarks');
  fs.writeFileSync(path.join(outDir, 'data', 'official-benchmarks.csv'), csv([['geography', 'fiscal_year', '0br', '1br', '2br', '3br', '4br', 'status', 'official_sources'], ...benchmarkTable.rows.map(row => [row.geography, row.year, row.br0, row.br1, row.br2, row.br3, row.br4, row.status, row.source_ids.map(id => sources.get(id).url).join(' | ')])]));
  fs.writeFileSync(path.join(outDir, 'data', 'review-flags.csv'), csv([['id', 'topic', 'item', 'missing_value', 'next_action', 'official_sources'], ...data.flags.map(flag => [flag.id, flag.topic, flag.item, '', flag.action, flag.source_ids.map(id => sources.get(id).url).join(' | ')])]));
  fs.writeFileSync(path.join(outDir, '.nojekyll'), '');
  fs.writeFileSync(path.join(outDir, 'robots.txt'), 'User-agent: *\nAllow: /\n');
  const publicFiles = [];
  function collect(dir) { for (const entry of fs.readdirSync(dir, { withFileTypes: true })) { const full = path.join(dir, entry.name); if (entry.isDirectory()) collect(full); else publicFiles.push(full); } }
  collect(outDir);
  for (const file of publicFiles) {
    if (/\.(html|js|json|csv|txt)$/.test(file) && containsPrivateIdentifier(fs.readFileSync(file, 'utf8'), privateIdentifiers)) throw new Error(`Private identifier detected in generated file: ${path.relative(outDir, file)}`);
  }
  validateGeneratedLinks(outDir);
  return { outDir, pages: data.pages.length + 1, sources: sourceList.length, flags: data.flags.length, publicFiles: publicFiles.length };
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const outIndex = process.argv.indexOf('--out');
  const rootIndex = process.argv.indexOf('--root');
  const root = rootIndex >= 0 ? path.resolve(process.argv[rootIndex + 1]) : DEFAULT_ROOT;
  const outDir = outIndex >= 0 ? path.resolve(process.argv[outIndex + 1]) : path.join(root, 'site', 'public');
  const result = buildSite({ root, outDir });
  console.log(`Built ${result.pages} pages, ${result.sources} official sources, and ${result.flags} open flags into ${path.relative(root, outDir) || outDir}. Local links and privacy checks passed.`);
}
