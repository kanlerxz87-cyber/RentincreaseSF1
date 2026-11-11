# Session `arena-1c0f33a9` — independent arithmetic recompute (2026-11-11 UTC)

Method: Python `Decimal` with `ROUND_HALF_UP` to the cent, from Form 571
percentages (S06, re-read live 2026-11-11) and the owner-brief rents. Percentages
are added, never compounded; no rounding up of the rate. Results compared against
the canonical dashboard figures.

| Scenario | Recompute | Result | Site figure | Agrees |
| --- | --- | --- | --- | --- |
| Unit 1 annual only | $3,995.00 × 1.6% | $63.92 → $4,058.92 | $63.92 → $4,058.92 | Yes |
| Unit 1 banked portion | $3,995.00 × 1.4% | $55.93 | $55.93 | Yes |
| Unit 1 combined 3.0% | $3,995.00 × 3.0% | $119.85 → $4,114.85 | $119.85 → $4,114.85 | Yes |
| Unit 2 annual only | $3,150.00 × 1.6% | $50.40 → $3,200.40 | $50.40 → $3,200.40 | Yes |
| Unit 2 banked 11.5% | 1.8+0.7+2.3+3.6+1.7+1.4 = 11.5%; $3,150.00 × 11.5% | $362.25 | $362.25 | Yes |
| Unit 2 combined 13.1% | $3,150.00 × 13.1% | $412.65 → $3,562.65 | $412.65 → $3,562.65 | Yes |
| Unit 2 fee recovery unit rate | $59.00 × 50% | $29.50 | $29.50 | Yes |
| Unit 1 30-day serve-by (eff. Feb 1, 2027) | Feb 1, 2027 − 30 days | Jan 2, 2027 | Jan 2, 2027 | Yes |
| Unit 1 35-day mail-by | Feb 1, 2027 − 35 days | Dec 28, 2026 | Dec 28, 2026 | Yes |
| Unit 2 30/35-day (eff. Feb 28, 2027) | Feb 28, 2027 − 30/35 days | Jan 29 / Jan 24, 2027 | Jan 29 / Jan 24, 2027 | Yes |
| Unit 2 90/95-day (eff. Feb 28, 2027) | Feb 28, 2027 − 90/95 days | Nov 30 / Nov 25, 2026 | Nov 30 / Nov 25, 2026 | Yes |
| Builder "today + 90 days" (today Nov 11, 2026) | Nov 11, 2026 + 90 days | Feb 9, 2027 | (regenerated) | — |

All figures remain **conditional scenario arithmetic**, not certified lawful rents
or permission to serve notice. Corroborates `arena-53d8f8c1` §2 to the cent.
