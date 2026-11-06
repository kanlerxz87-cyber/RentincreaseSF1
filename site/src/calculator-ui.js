import { evaluateOrdinaryIncrease, formatMoney } from './rent-math.js';

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

export function initCalculator() {
  const form = document.getElementById('rent-form');
  if (!form) return;
  const output = document.getElementById('calculator-output');
  const value = id => document.getElementById(id).value;
  const checked = id => document.getElementById(id).checked;
  function calculate() {
    const result = evaluateOrdinaryIncrease({
      base: value('base'), effective: value('effective'), anniversary: value('anniversary'),
      lastIncrease: value('last-increase'), noPriorIncrease: checked('no-prior'),
      serviceDate: value('service-date'), serviceMethod: value('service-method'),
      baseVerified: checked('base-verified'), coverageVerified: checked('coverage-verified'),
      complianceVerified: checked('compliance-verified'), exclusionsVerified: checked('exclusions-verified'),
      reviewVerified: checked('review-verified')
    });
    const banner = result.suppliedChecksPass
      ? '<div class="result-banner result-pass"><strong>Supplied checks pass—not legal approval.</strong> This remains a conditional ordinary-increase illustration based on your attestations.</div>'
      : '<div class="result-banner result-conditional"><strong>Conditional illustration only.</strong> One or more inputs or verification checks are unresolved. Do not treat this as an authorized rent or notice.</div>';
    const metrics = result.increaseCents === null ? '' : `<div class="result-grid"><div class="result-metric"><span>Illustrative increase (1.6%)</span><strong>${formatMoney(result.increaseCents)}</strong></div><div class="result-metric"><span>Illustrative new total</span><strong>${formatMoney(result.totalCents)}</strong></div><div class="result-metric"><span>Supplied-date planning minimum</span><strong>${result.earliest ? escapeHTML(result.earliest) : '<span class="inline-flag">Flagged for Review</span>'}</strong></div></div>`;
    const errors = result.errors.length ? `<div class="error-list"><strong>Resolve before relying on timing:</strong><ul>${result.errors.map(error => `<li>${escapeHTML(error)}</li>`).join('')}</ul></div>` : '';
    const checks = `<ul class="result-list">${result.checks.map(check => `<li class="${check.ok ? 'ok' : 'pending'}">${escapeHTML(check.label)}<small>${escapeHTML(check.detail)}</small></li>`).join('')}</ul>`;
    output.innerHTML = `${banner}${metrics}${errors}${checks}<p class="field-help">Rounding is down to whole cents. Banking, petitions, passthroughs, other prior increases, fixed-term lease rights, and program-specific rules are excluded. No input was transmitted or saved.</p>`;
  }
  form.addEventListener('submit', event => event.preventDefault());
  document.getElementById('calculate').addEventListener('click', calculate);
  document.getElementById('reset-calculator').addEventListener('click', () => {
    form.reset();
    output.innerHTML = '<p class="output-placeholder">Enter values to see a conditional illustration. No lawful rent is determined here.</p>';
    document.getElementById('base').focus();
  });
  document.getElementById('use-reported').addEventListener('click', () => {
    document.getElementById('base').value = '3995';
    document.getElementById('base-verified').checked = false;
    calculate();
  });
  const last = document.getElementById('last-increase');
  const noPrior = document.getElementById('no-prior');
  noPrior.addEventListener('change', () => {
    last.disabled = noPrior.checked;
    if (noPrior.checked) last.value = '';
  });
}
