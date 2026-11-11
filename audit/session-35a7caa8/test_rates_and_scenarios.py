"""Independent exact arithmetic and Form 571 transcription checks.

These tests establish neither eligibility nor the truth of private inputs.
The CSV is a manual transcription of the official SF Rent Board Form 571
retrieved 2026-11-11. The form's 1992 one-of-two-rates caveat also needs to be
shown when the historical table is presented.
"""
import csv
import json
import unittest
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def rate_on(day, official_rates):
    matches = [r for r in official_rates if date.fromisoformat(r["start"]) <= day <= date.fromisoformat(r["end"])]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one official rate for {day}, got {len(matches)}")
    return Fraction(matches[0]["pct"])


class RatesAndScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hub = json.loads((ROOT / "hub/data.json").read_text(encoding="utf-8"))
        with (HERE / "form571-2026-11-11.csv").open(encoding="utf-8", newline="") as f:
            cls.official_rates = list(csv.DictReader(f))

    def test_all_published_rate_periods_match_the_transcription(self):
        actual = [(r["start"], r["end"], r["pct"]) for r in self.hub["rates"]]
        expected = [(r["start"], r["end"], r["pct"]) for r in self.official_rates]
        self.assertEqual(len(expected), 46)
        self.assertEqual(actual, expected)

    def test_rate_periods_cover_each_day_without_gaps_or_overlap(self):
        ordered = sorted(self.official_rates, key=lambda r: r["start"])
        for left, right in zip(ordered, ordered[1:]):
            self.assertEqual(date.fromisoformat(left["end"]) + timedelta(days=1),
                             date.fromisoformat(right["start"]))

    def test_every_banked_component_matches_its_published_date(self):
        for unit, calc in self.hub["calculations"].items():
            with self.subTest(unit=unit):
                for item in calc["banked"]:
                    self.assertTrue(item["conditional"])
                    self.assertEqual(Fraction(item["pct"]),
                                     rate_on(date.fromisoformat(item["for_date"]), self.official_rates))
                self.assertEqual(sum((Fraction(i["pct"]) for i in calc["banked"]), Fraction()),
                                 Fraction(calc["banked_total_pct"]))
                self.assertEqual(Fraction(calc["banked_total_pct"]) + Fraction(calc["annual_pct"]),
                                 Fraction(calc["total_pct"]))
                self.assertEqual(Fraction(calc["annual_pct"]),
                                 rate_on(date.fromisoformat(calc["annual_effective"]), self.official_rates))

    def test_exact_scenario_arithmetic_without_rounding(self):
        expected = {
            "U1": ("3995.00", "63.92", "4058.92", "119.85", "4114.85"),
            "U2": ("3150.00", "50.40", "3200.40", "412.65", "3562.65"),
        }
        for unit, (base, annual, annual_total, combined, combined_total) in expected.items():
            with self.subTest(unit=unit):
                u, c = self.hub["units"][unit], self.hub["calculations"][unit]
                self.assertEqual(Fraction(u["base_rent"]), Fraction(base))
                annual_raw = Fraction(base) * Fraction(c["annual_pct"]) / 100
                combined_raw = Fraction(base) * Fraction(c["total_pct"]) / 100
                # Exact cent values for these inputs; no rounding is needed.
                self.assertEqual(annual_raw, Fraction(annual))
                self.assertEqual(combined_raw, Fraction(combined))
                self.assertEqual(Fraction(base) + annual_raw, Fraction(annual_total))
                self.assertEqual(Fraction(base) + combined_raw, Fraction(combined_total))

    def test_notice_subtraction_is_only_calendar_arithmetic(self):
        # These dates assume the relevant notice band, method, mailing location,
        # and all private legal prerequisites; they do not establish eligibility.
        expected = {
            ("U1", 30): ("2027-01-02", "2026-12-28"),
            ("U2", 30): ("2027-01-29", "2027-01-24"),
            ("U2", 90): ("2026-11-30", "2026-11-25"),
        }
        for (unit, days), (personal, ca_mail) in expected.items():
            with self.subTest(unit=unit, days=days):
                effective = date.fromisoformat(self.hub["calculations"][unit]["annual_effective"])
                self.assertEqual((effective - timedelta(days=days)).isoformat(), personal)
                self.assertEqual((effective - timedelta(days=days + 5)).isoformat(), ca_mail)


if __name__ == "__main__":
    unittest.main()
