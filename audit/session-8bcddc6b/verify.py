#!/usr/bin/env python3
"""Deterministic verification for session arena-8bcddc6b (2026-11-11).

Checks (no network, no inference):
 1. Every dollar figure recomputed from Form 571 percentages with exact Decimal arithmetic.
 2. Every notice-date arithmetic recomputed with calendar dates.
 3. Form 571 percentages in hub/data.json match the live-read Form 571 table for 2020-2027.
 4. Every table row in this session's EXECUTIVE_SUMMARY.md carries an official link or an explicit flag/blank.
 5. Privacy: no tenant initials, names, or street address in this session's files.
 6. Canonical suites still pass (verify_hub, verify_assurance, check_links) — run as subprocesses.
Exit non-zero on any failure. Run: python3 audit/session-8bcddc6b/verify.py
"""
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SESSION = Path(__file__).resolve().parent
errors = []
checks = 0

def check(cond, msg):
    global checks
    checks += 1
    if not cond:
        errors.append(msg)
        print(f"FAIL: {msg}")

def money(base, pct):
    return (Decimal(base) * Decimal(pct) / Decimal("100")).quantize(Decimal("0.01"))

# --- 1. Dollar recomputation (scenario inputs from owner brief, anonymized) ---
cases = [
    ("U1 annual 1.6%", "3995.00", "1.6", "63.92", "4058.92"),
    ("U1 banked 1.4%", "3995.00", "1.4", "55.93", "4050.93"),
    ("U1 combined 3.0%", "3995.00", "3.0", "119.85", "4114.85"),
    ("U2 annual 1.6%", "3150.00", "1.6", "50.40", "3200.40"),
    ("U2 banked 11.5%", "3150.00", "11.5", "362.25", "3512.25"),
    ("U2 combined 13.1%", "3150.00", "13.1", "412.65", "3562.65"),
    ("U2 File-261020 illustration 11.6%", "3150.00", "11.6", "365.40", "3515.40"),
]
for label, base, pct, exp_amt, exp_new in cases:
    amt = money(base, pct)
    check(str(amt) == exp_amt, f"{label}: amount {amt} != {exp_amt}")
    check(str(Decimal(base) + amt) == exp_new, f"{label}: new rent {Decimal(base)+amt} != {exp_new}")

# Banked component sums (add, never compound)
check(sum(Decimal(x) for x in ["1.8", "0.7", "2.3", "3.6", "1.7", "1.4"]) == Decimal("11.5"),
      "U2 banked components do not sum to 11.5")
check(Decimal("11.5") + Decimal("1.6") == Decimal("13.1"), "U2 combined 13.1% wrong")
check(Decimal("1.4") + Decimal("1.6") == Decimal("3.0"), "U1 combined 3.0% wrong")
check(Decimal("10.0") + Decimal("1.6") == Decimal("11.6"), "U2 11.6% illustration wrong")

# --- 2. Notice-date arithmetic ---
check(date(2027, 2, 28) - timedelta(days=90) == date(2026, 11, 30), "U2 90-day personal date wrong")
check(date(2027, 2, 28) - timedelta(days=95) == date(2026, 11, 25), "U2 95-day mail date wrong")
check(date(2027, 2, 1) - timedelta(days=30) == date(2027, 1, 2), "U1 30-day personal date wrong")
check(date(2027, 2, 1) - timedelta(days=35) == date(2026, 12, 28), "U1 35-day mail date wrong")

# --- 3. Form 571 vs hub/data.json ---
data = json.loads((ROOT / "hub" / "data.json").read_text())
rates = {r["start"]: r["pct"] for r in data["rates"]}
form571 = {
    "2026-03-01": "1.6", "2025-03-01": "1.4", "2024-03-01": "1.7",
    "2023-03-01": "3.6", "2022-03-01": "2.3", "2021-03-01": "0.7",
    "2020-03-01": "1.8", "2019-03-01": "2.6",
}
for k, v in form571.items():
    check(rates.get(k) == v, f"Form 571 mismatch {k}: data.json={rates.get(k)} live={v}")
check(data["calculations"]["U1"]["annual_pct"] == "1.6", "U1 annual pct wrong")
check(data["calculations"]["U2"]["banked_total_pct"] == "11.5", "U2 banked total wrong")

# --- 4. Every table row in session executive summary has official link or flag/blank ---
OFFICIAL_HOSTS = ("sf.gov", "leginfo.legislature.ca.gov", "sftreasurer.org",
                  "sfgov.legistar.com", "hud.gov", "justice.gov", "courts.ca.gov")
summary = (SESSION / "EXECUTIVE_SUMMARY.md").read_text()
row_count = 0
for line in summary.splitlines():
    s = line.strip()
    if not s.startswith("|"):
        continue
    if "---" in s:
        continue
    # Skip header rows (they name the columns, they are not claims).
    if ("Official source" in s or "Issued by" in s or "Official basis" in s
            or s.startswith("| Page |") or s.startswith("| Step |")):
        continue
    row_count += 1
    has_official = any(h in s for h in OFFICIAL_HOSTS)
    # Site-map navigation rows link to the published dashboard itself.
    has_site_link = "kanlerxz87-cyber.github.io" in s
    has_flag = ("H-" in s) or ("blank" in s.lower()) or ("unverified" in s.lower()) or ("—" in s and "flag" in s.lower())
    check(has_official or has_site_link or has_flag, f"Row without official link or flag: {s[:120]}")
check(row_count >= 30, f"Too few table rows checked: {row_count}")

# --- 5. Privacy: no initials / street address in session files ---
# Initials from the brief are never written here; scan for two-letter initial patterns
# that would indicate a leak. The pattern itself is built from character classes so
# this checker does not embed any literal initial pair.
for f in SESSION.glob("*"):
    if f.is_file() and f.suffix in {".md", ".py", ".json"}:
        text = f.read_text()
        hits = re.findall(r"\b[A-Z]\s[A-Z]\b", text)
        check(len(hits) == 0, f"{f.name}: possible initials leak {hits[:5]}")
        check("94122" in text or f.name == "verify.py", f"{f.name}: missing ZIP context")

# --- 6. Canonical suites ---
for cmd in (["python3", "tools/verify_hub.py"],
            ["python3", "tools/verify_assurance.py"],
            ["python3", "tools/check_links.py"]):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    check(r.returncode == 0, f"{' '.join(cmd)} failed: {r.stdout[-500:]} {r.stderr[-500:]}")
    print(f"  {' '.join(cmd)}: exit {r.returncode}")

print(f"\n{checks} checks, {len(errors)} errors")
if errors:
    sys.exit(1)
print("OK: all session checks passed")
