import test from 'node:test';
import assert from 'node:assert/strict';
import { addCalendarDays, addMonthsClamped, evaluateOrdinaryIncrease, formatMoney, moneyToCents, ordinaryIncreaseCents, parseISODate, statutoryNoticeDays, toISODate } from '../site/src/rent-math.js';

const valid = { base: '3995', effective: '2026-11-06', anniversary: '2026-02-01', lastIncrease: '2025-02-01', noPriorIncrease: false, serviceDate: '2026-10-01', serviceMethod: 'personal', baseVerified: true, coverageVerified: true, complianceVerified: true, exclusionsVerified: true, reviewVerified: true };

test('reported Unit 1 illustration truncates to exact cents', () => {
  assert.equal(moneyToCents('3995'), 399500);
  assert.equal(ordinaryIncreaseCents(399500), 6392);
  assert.equal(formatMoney(6392), '$63.92');
  assert.equal(formatMoney(405892), '$4,058.92');
});
test('rounding is down, never up', () => {
  assert.equal(ordinaryIncreaseCents(moneyToCents('1999.99')), 3199);
  assert.equal(ordinaryIncreaseCents(moneyToCents('0.01')), 0);
  assert.equal(ordinaryIncreaseCents(moneyToCents('1234.56')), 1975);
});
test('invalid money is rejected', () => {
  for (const value of ['', '0', '-1', '1.001', '1e3', 'NaN', 'Infinity', '1000000.01', '$3,995']) assert.equal(moneyToCents(value), null, value);
});
test('strict calendar parsing rejects impossible dates', () => {
  assert.equal(parseISODate('2026-02-29'), null);
  assert.equal(parseISODate('2026-13-01'), null);
  assert.equal(parseISODate('2026-1-01'), null);
  assert.equal(toISODate(parseISODate('2028-02-29')), '2028-02-29');
});
test('twelve-month spacing clamps leap-day anniversaries', () => {
  assert.equal(toISODate(addMonthsClamped(parseISODate('2028-02-29'), 12)), '2029-02-28');
  assert.equal(toISODate(addMonthsClamped(parseISODate('2026-01-31'), 12)), '2027-01-31');
});
test('mail extensions are calendar-day planning additions', () => {
  assert.equal(toISODate(addCalendarDays(parseISODate('2026-10-01'), 35)), '2026-11-05');
  assert.equal(toISODate(addCalendarDays(parseISODate('2026-10-01'), 40)), '2026-11-10');
  assert.equal(toISODate(addCalendarDays(parseISODate('2026-10-01'), 50)), '2026-11-20');
});
test('state notice threshold is inclusive at ten percent', () => {
  assert.equal(statutoryNoticeDays(1.6), 30);
  assert.equal(statutoryNoticeDays(10), 30);
  assert.equal(statutoryNoticeDays(10.01), 90);
  assert.equal(statutoryNoticeDays(-1), null);
});
test('complete synthetic inputs pass only supplied checks', () => {
  const result = evaluateOrdinaryIncrease(valid);
  assert.equal(result.errors.length, 0);
  assert.equal(result.suppliedChecksPass, true);
  assert.equal(result.increaseCents, 6392);
  assert.equal(result.totalCents, 405892);
  assert.equal(result.earliest, '2026-10-31');
});
test('missing legal review never passes readiness', () => {
  const result = evaluateOrdinaryIncrease({ ...valid, reviewVerified: false });
  assert.equal(result.suppliedChecksPass, false);
  assert.equal(result.increaseCents, 6392);
});
test('unverified reported base remains conditional', () => {
  assert.equal(evaluateOrdinaryIncrease({ ...valid, baseVerified: false }).suppliedChecksPass, false);
});
test('outside the official interval fails', () => {
  for (const effective of ['2026-02-28', '2027-03-01']) assert.equal(evaluateOrdinaryIncrease({ ...valid, effective }).suppliedChecksPass, false);
});
test('twelve-month spacing and anniversary control the planning minimum', () => {
  const result = evaluateOrdinaryIncrease({ ...valid, lastIncrease: '2026-01-15', anniversary: '2026-02-01' });
  assert.equal(result.earliest, '2027-01-15');
  assert.equal(result.suppliedChecksPass, false);
});
test('mailing extension changes the planning minimum', () => {
  assert.equal(evaluateOrdinaryIncrease({ ...valid, serviceMethod: 'mail-ca' }).earliest, '2026-11-05');
  assert.equal(evaluateOrdinaryIncrease({ ...valid, serviceMethod: 'mail-us' }).earliest, '2026-11-10');
  assert.equal(evaluateOrdinaryIncrease({ ...valid, serviceMethod: 'mail-intl' }).earliest, '2026-11-20');
});
test('missing prior increase requires explicit attestation', () => {
  assert.equal(evaluateOrdinaryIncrease({ ...valid, lastIncrease: '' }).errors.length > 0, true);
  assert.equal(evaluateOrdinaryIncrease({ ...valid, lastIncrease: '', noPriorIncrease: true }).errors.length, 0);
});
test('unknown service method is rejected', () => {
  assert.equal(evaluateOrdinaryIncrease({ ...valid, serviceMethod: 'email' }).errors.length > 0, true);
});
