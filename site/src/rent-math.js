export const RATE_BASIS_POINTS = 160;
export const INTERVAL_START = '2026-03-01';
export const INTERVAL_END = '2027-02-28';
export const SERVICE_EXTENSIONS = Object.freeze({ personal: 0, 'mail-ca': 5, 'mail-us': 10, 'mail-intl': 20, overnight: 2 });

export function parseISODate(value) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return null;
  const [year, month, day] = value.split('-').map(Number);
  if (year < 1900 || year > 2100) return null;
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
  return date;
}

export function toISODate(date) {
  return date.toISOString().slice(0, 10);
}

export function addCalendarDays(date, days) {
  const result = new Date(date.getTime());
  result.setUTCDate(result.getUTCDate() + days);
  return result;
}

export function addMonthsClamped(date, months) {
  const day = date.getUTCDate();
  const result = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + months, 1));
  const lastDay = new Date(Date.UTC(result.getUTCFullYear(), result.getUTCMonth() + 1, 0)).getUTCDate();
  result.setUTCDate(Math.min(day, lastDay));
  return result;
}

export function moneyToCents(value) {
  const text = String(value ?? '').trim();
  if (!/^\d+(?:\.\d{1,2})?$/.test(text)) return null;
  const [whole, fraction = ''] = text.split('.');
  const cents = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
  if (!Number.isSafeInteger(cents) || cents <= 0 || cents > 100000000) return null;
  return cents;
}

export function ordinaryIncreaseCents(baseCents) {
  if (!Number.isSafeInteger(baseCents) || baseCents <= 0) return null;
  return Math.floor((baseCents * RATE_BASIS_POINTS) / 10000);
}

export function formatMoney(cents) {
  if (!Number.isSafeInteger(cents)) return '';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(cents / 100);
}

export function statutoryNoticeDays(combinedIncreasePercent) {
  if (!Number.isFinite(combinedIncreasePercent) || combinedIncreasePercent < 0) return null;
  return combinedIncreasePercent <= 10 ? 30 : 90;
}

export function evaluateOrdinaryIncrease(input) {
  const errors = [];
  const baseCents = moneyToCents(input.base);
  if (baseCents === null) errors.push('Enter a positive base rent with no more than two decimal places (maximum $1,000,000).');
  const effective = parseISODate(input.effective);
  const anniversary = parseISODate(input.anniversary);
  const service = parseISODate(input.serviceDate);
  if (!effective) errors.push('Enter a valid proposed effective date.');
  if (!anniversary) errors.push('Enter the verified rent-increase anniversary.');
  if (!service) errors.push('Enter the planned actual service date.');
  if (!Object.hasOwn(SERVICE_EXTENSIONS, input.serviceMethod)) errors.push('Select a listed service method.');
  let last = null;
  if (!input.noPriorIncrease) {
    last = parseISODate(input.lastIncrease);
    if (!last) errors.push('Enter the last increase effective date, or explicitly attest that there was no prior increase.');
  }
  const increaseCents = baseCents === null ? null : ordinaryIncreaseCents(baseCents);
  const totalCents = baseCents === null ? null : baseCents + increaseCents;
  const extension = SERVICE_EXTENSIONS[input.serviceMethod] ?? 0;
  const noticeDays = 30 + extension;
  let earliest = null;
  if (effective && anniversary && service) {
    const spacing = last ? addMonthsClamped(last, 12) : null;
    const notice = addCalendarDays(service, noticeDays);
    earliest = new Date(Math.max(anniversary.getTime(), notice.getTime(), spacing ? spacing.getTime() : 0));
  }
  const checks = [
    { label: 'Effective date is inside the official 1.6% interval', ok: Boolean(effective && effective >= parseISODate(INTERVAL_START) && effective <= parseISODate(INTERVAL_END)), detail: `${INTERVAL_START} through ${INTERVAL_END}.` },
    { label: 'Effective date is on or after the supplied anniversary', ok: Boolean(effective && anniversary && effective >= anniversary), detail: 'The anniversary must be independently verified.' },
    { label: 'Twelve-month spacing is satisfied on the supplied dates', ok: Boolean(effective && (input.noPriorIncrease || (last && effective >= addMonthsClamped(last, 12)))), detail: input.noPriorIncrease ? 'Using your no-prior-increase attestation.' : 'Uses the last increase effective date plus twelve calendar months.' },
    { label: 'Planning notice lead time is satisfied', ok: Boolean(effective && service && effective >= addCalendarDays(service, noticeDays)), detail: `30 days plus ${extension} planning day(s) for the selected method; not a service adjudication.` },
    { label: 'Base rent independently verified', ok: Boolean(input.baseVerified), detail: 'A reported or stale lease amount is not enough.' },
    { label: 'Local coverage independently confirmed', ok: Boolean(input.coverageVerified), detail: 'The state cap and exempt/program units are outside this tool.' },
    { label: 'Inventory, license, lease terms, and notice content verified', ok: Boolean(input.complianceVerified), detail: 'These are separate legal requirements.' },
    { label: 'Ordinary-only route confirmed', ok: Boolean(input.exclusionsVerified), detail: 'No banking, petition, passthrough, other prior-12-month increase, or program-specific rule.' },
    { label: 'Independent legal review completed', ok: Boolean(input.reviewVerified), detail: 'Notice, nondiscrimination, retaliation, and unit-selection reasons require review.' }
  ];
  if (effective && earliest && effective < earliest) errors.push(`The proposed effective date precedes the supplied-date planning minimum of ${toISODate(earliest)}.`);
  return { errors, baseCents, increaseCents, totalCents, earliest: earliest ? toISODate(earliest) : null, noticeDays, checks, suppliedChecksPass: errors.length === 0 && checks.every(check => check.ok) };
}
