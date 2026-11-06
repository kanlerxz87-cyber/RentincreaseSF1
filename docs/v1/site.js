const search = document.querySelector('#filter');
const rows = [...document.querySelectorAll('tbody tr')];
search.addEventListener('input', () => {
  const term = search.value.trim().toLowerCase();
  for (const row of rows) row.hidden = !row.textContent.toLowerCase().includes(term);
  document.querySelector('#count').textContent = `${rows.filter(row => !row.hidden).length} of ${rows.length} findings`;
});
