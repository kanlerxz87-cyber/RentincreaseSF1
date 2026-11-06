import { initCalculator } from './calculator-ui.js';

const sidebar = document.getElementById('sidebar');
const menuToggle = document.getElementById('menu-toggle');
function closeMenu() {
  sidebar?.classList.remove('open');
  menuToggle?.setAttribute('aria-expanded', 'false');
}
menuToggle?.addEventListener('click', () => {
  const open = sidebar.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
});
sidebar?.querySelectorAll('nav a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && sidebar?.classList.contains('open')) {
    closeMenu();
    menuToggle?.focus();
  }
});
document.addEventListener('click', event => {
  if (sidebar?.classList.contains('open') && !sidebar.contains(event.target) && !menuToggle.contains(event.target)) closeMenu();
});
document.getElementById('print-page')?.addEventListener('click', () => window.print());

const search = document.getElementById('table-search');
const status = document.getElementById('status-filter');
const jurisdiction = document.getElementById('jurisdiction-filter');
const summary = document.getElementById('filter-summary');
const tables = [...document.querySelectorAll('table')];
function applyFilters() {
  if (!search || !status) return;
  const query = search.value.trim().toLowerCase();
  let visible = 0;
  let total = 0;
  for (const table of tables) {
    let tableVisible = 0;
    for (const row of table.tBodies[0].rows) {
      total += 1;
      const matches = (!query || row.textContent.toLowerCase().includes(query))
        && (!status.value || row.dataset.status === status.value)
        && (!jurisdiction?.value || row.dataset.jurisdiction === jurisdiction.value);
      row.hidden = !matches;
      if (matches) { visible += 1; tableVisible += 1; }
    }
    const empty = table.closest('.table-section')?.querySelector('.table-empty');
    if (empty) empty.hidden = tableVisible !== 0;
  }
  summary.textContent = `Showing ${visible} of ${total} rows.`;
}
search?.addEventListener('input', applyFilters);
status?.addEventListener('change', applyFilters);
jurisdiction?.addEventListener('change', applyFilters);
document.getElementById('clear-filters')?.addEventListener('click', () => {
  search.value = '';
  status.value = '';
  if (jurisdiction) jurisdiction.value = '';
  applyFilters();
  search.focus();
});
applyFilters();
initCalculator();
