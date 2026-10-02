"""
Check the figures quoted in memo.md against analysis/outputs/.

Not part of `run.sh`: the analysis must run on a clean clone whether or not a
memo exists.  Run it after editing the memo:

    python analysis/check_memo_numbers.py

The submission checklist requires that every number in the memo comes from the
run.  This asserts that for the headline figures, so an edit that changes a
digit, or a re-run that moves one, fails loudly instead of silently.

Each entry below is (label, what the memo says, where the run puts it).  The
tolerance is relative; counts use a tight one.
"""
import pathlib
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "outputs"

failures: list[str] = []
checked = 0


def check(label: str, memo_says: float, run_says: float, tol: float = 0.006) -> None:
    global checked
    checked += 1
    if abs(memo_says - run_says) > tol * max(1.0, abs(run_says)):
        failures.append(f"{label}: memo {memo_says}, run {run_says}")


def main() -> None:
    # ---- A1 ----------------------------------------------------------------
    a1 = pd.read_csv(OUT / "a1_baselines.csv").set_index("quantity")["value"].astype(float)
    check("A1 base rate", 0.0929, a1["base rate of churn_next_60d (rows)"])
    check("A1 member-level rate", 0.6998, a1["base rate (members ever churning)"])
    check("A1 trivial-rule accuracy", 0.9071,
          a1["accuracy of predicting 'no churn' for everyone"])
    for col, v in [("avg_session_minutes", 0.681), ("app_opens_last_30d", 0.648),
                   ("days_since_last_login", 0.646), ("tenure_months", 0.502)]:
        check(f"A1 AUC {col}", v, a1[f"AUC, single-variable rule: {col}"])

    # ---- A2 ----------------------------------------------------------------
    a2 = pd.read_csv(OUT / "a2_table.csv")
    for row, v in [(0, 0.968), (1, 0.748), (2, 0.747), (3, 0.644)]:
        check(f"A2 row {row} AUC", v, float(a2.loc[a2.row == row, "auc"].iloc[0]), 0.001)
    check("A2 corporate AUC", 0.404,
          float(a2.loc[a2.change.str.contains("corporate"), "auc"].iloc[0]), 0.002)
    check("A2 other AUC", 0.641,
          float(a2.loc[a2.change.str.contains(": other"), "auc"].iloc[0]), 0.002)
    check("A2 building rows", 21031, float(a2.loc[a2.row == 0, "rows_scored"].iloc[0]), 1e-4)
    check("A2 test rows", 4556, float(a2.loc[a2.row == 3, "rows_scored"].iloc[0]), 1e-4)
    check("A2 test churners", 408, float(a2.loc[a2.row == 3, "churners_scored"].iloc[0]), 1e-4)

    # ---- A3 ----------------------------------------------------------------
    val = pd.read_csv(OUT / "a3_value.csv")

    def policy(pat: str, seg: str) -> pd.Series:
        m = val.policy.str.contains(pat, regex=False) & val.segment.eq(seg)
        return val[m].iloc[0]

    for label, pat, seg, v in [
        ("A3 value at t*, all", "t* = 0.2143", "all", 852),
        ("A3 value, corporate", "t* = 0.2143", "corporate", -78),
        ("A3 value, other", "t* = 0.2143", "other", 930),
        ("A3 offer to everyone", "every member-month", "all", -47736),
        ("A3 at analyst's 0.267", "analyst", "all", 828),
    ]:
        check(label, v, float(policy(pat, seg).value_usd), 0.001)
    row = policy("t* = 0.2143", "all")
    check("A3 offers made", 242, float(row.offers), 0.001)
    check("A3 offers reaching a churner", 62, float(row.offers_to_churners), 0.001)

    by_month = pd.read_csv(OUT / "a3_by_month.csv")
    for month, v in [("2025-10", 48), ("2025-11", 810), ("2025-12", -6)]:
        check(f"A3 {month} value", v,
              float(by_month.loc[by_month.month == month, "value_usd"].iloc[0]), 0.001)

    # ---- B1 ----------------------------------------------------------------
    b1 = pd.read_csv(OUT / "b1_noise_floor.csv").set_index("division")
    for div, sigma2, avoidable in [("H", 148.1, 82.9), ("A", 142.0, 272.0)]:
        check(f"B1 {div} sigma^2", sigma2, float(b1.loc[div, "sigma2_hat"]))
        check(f"B1 {div} avoidable", avoidable,
              float(b1.loc[div, "contractor_best_minus_floor"]))

    # ---- B2 ----------------------------------------------------------------
    b2 = pd.read_csv(OUT / "b2_table.csv")

    def cell(div: str, degree: int, treat: str, col: str) -> float:
        m = b2.division.eq(div) & b2.degree.eq(degree) & b2.treatment.eq(treat)
        return float(b2[m][col].iloc[0])

    for label, div, deg, treat, col, v in [
        ("B2 Apparel d2 ridge CV", "Apparel", 2, "ridge", "cv_mse", 329.80),
        ("B2 Apparel d2 OLS CV", "Apparel", 2, "OLS", "cv_mse", 617.97),
        ("B2 Hardgoods d2 ridge CV", "Hardgoods", 2, "ridge", "cv_mse", 232.98),
        ("B2 Apparel d2 ridge test-floor", "Apparel", 2, "ridge",
         "test_mse_minus_sigma2", 154.15),
        ("B2 terms/row Apparel d2", "Apparel", 2, "ridge", "terms_per_row", 0.457),
        ("B2 terms/row Apparel d1", "Apparel", 1, "ridge", "terms_per_row", 0.061),
        ("B2 terms/row Hardgoods d2", "Hardgoods", 2, "ridge", "terms_per_row", 0.030),
    ]:
        check(label, v, cell(div, deg, treat, col), 0.01)

    # ---- B3 ----------------------------------------------------------------
    b3 = pd.read_csv(OUT / "b3_stability.csv")
    divs = set(b3.division.unique())
    H = "H" if "H" in divs else "Hardgoods"
    A = "A" if "A" in divs else "Apparel"

    def stab(div: str, model: str, col: str) -> float:
        m = b3.division.eq(div) & b3.model.str.contains(model)
        return float(b3[m][col].iloc[0])

    for label, div, model, col, v in [
        ("B3 H deg-1 sd", H, "degree-1 OLS", "mean_sd", 1.14),
        ("B3 H deg-2 OLS sd", H, "degree-2 OLS", "mean_sd", 2.83),
        ("B3 H deg-2 ridge sd", H, "degree-2 ridge", "mean_sd", 2.80),
        ("B3 A deg-1 sd", A, "degree-1 OLS", "mean_sd", 4.33),
        ("B3 A deg-2 OLS sd", A, "degree-2 OLS", "mean_sd", 25.24),
        ("B3 A deg-2 ridge sd", A, "degree-2 ridge", "mean_sd", 7.22),
        ("B3 H deg-1 bias", H, "degree-1 OLS", "mean_abs_bias", 12.65),
        ("B3 H deg-2 bias", H, "degree-2 OLS", "mean_abs_bias", 3.84),
        ("B3 A deg-1 bias", A, "degree-1 OLS", "mean_abs_bias", 16.66),
        ("B3 A deg-2 OLS bias", A, "degree-2 OLS", "mean_abs_bias", 18.78),
        ("B3 A deg-2 ridge bias^2", A, "degree-2 ridge", "bias2_mean", 292.8),
        ("B3 A deg-2 ridge variance", A, "degree-2 ridge", "variance_mean", 52.9),
        ("B3 A deg-2 ridge bias share", A, "degree-2 ridge", "bias_share_pct", 85),
    ]:
        check(label, v, stab(div, model, col), 0.012)

    print(f"{checked} memo figures checked against analysis/outputs/")
    if failures:
        print("MISMATCHES:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print("all match")


if __name__ == "__main__":
    main()
