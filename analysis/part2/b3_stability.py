"""
B3 -- the stability experiment.

The loop is the supplied one.  This file does not copy or edit
part2_cascade/starter/stability.py; it imports that module and supplies the
three things it leaves blank:

    * RIDGE_ALPHA_DEG1 / RIDGE_ALPHA_DEG2, read from analysis/outputs/
      b2_penalties.csv so the penalties are literally the B2 values and
      cannot drift from them.  The brief forbids re-tuning inside the
      resamples.
    * build_models(), returning a fresh unfitted pipeline per call.
    * OUT, redirected to analysis/outputs/ so B3's table and figure sit
      beside B1's and B2's rather than in a script-adjacent folder.
      (This overrides the session-1 decision to keep the starter's
      b3_outputs/ name; one consistent output location won.)

Everything measured here comes from the starter's own run(): 20 bootstrap
resamples from bootstrap_indices(), the three QUERY_CONFIGS per division,
the standard deviation of the 20 predictions at each query point, and the
difference between their mean and the replicate-based truth.

This file adds one column the starter does not compute, signed_mean_bias,
the signed average of the three per-point biases.  The starter's
mean_abs_bias is the headline, since signed biases at three points can
cancel; the signed version says whether a model runs high or low overall.

Reading the output: the truth at each query point is itself an average of
ten weeks, so it carries a standard error of sigma/sqrt(10), about 3.85
units in Hardgoods and 3.77 in Apparel.  A measured bias smaller than that
is indistinguishable from zero.  And a standard deviation estimated from 20
draws has roughly 16% relative uncertainty of its own, so small differences
in mean_sd between models are not real.

Output:
    b3_stability.csv   per division and model: sd and bias at each of the
                       three query points, mean sd, mean |bias|, signed mean,
                       and the same in units^2 (bias^2, variance, their sum
                       and the bias share) so the two can be compared
    b3_stability.png   the figure the brief asks for
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "analysis" / "outputs"

# The starter module, imported and run as issued.
sys.path.insert(0, str(ROOT / "part2_cascade" / "starter"))
import stability  # noqa: E402
from load import dedup_h, load_a, load_h, poly_pipeline  # noqa: E402

DIVISION_NAME = {"H": "Hardgoods", "A": "Apparel"}


def b2_penalties() -> tuple[dict, dict]:
    """The tuned alphas from B2, read from its output rather than retyped."""
    p = pd.read_csv(OUT / "b2_penalties.csv")
    code = {v: k for k, v in DIVISION_NAME.items()}
    by_degree = {}
    for degree in (1, 2):
        rows = p.loc[p["degree"] == degree]
        by_degree[degree] = {code[r.division]: float(r.tuned_alpha)
                             for r in rows.itertuples()}
    return by_degree[1], by_degree[2]


def build_models(division: str) -> dict:
    """The four B2 models, fresh and unfitted, for one division.

    A new pipeline per call, so the starter's loop cannot accidentally refit
    an already-fitted object.  poly_pipeline() puts the basis expansion and
    the scaler inside the model, so both are refitted on each resample.
    """
    a1 = stability.RIDGE_ALPHA_DEG1[division]
    a2 = stability.RIDGE_ALPHA_DEG2[division]
    return {
        "degree-1 OLS": poly_pipeline(LinearRegression(), degree=1),
        "degree-1 ridge": poly_pipeline(Ridge(alpha=a1), degree=1),
        "degree-2 OLS": poly_pipeline(LinearRegression(), degree=2),
        "degree-2 ridge": poly_pipeline(Ridge(alpha=a2), degree=2),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    deg1, deg2 = b2_penalties()
    stability.RIDGE_ALPHA_DEG1 = deg1
    stability.RIDGE_ALPHA_DEG2 = deg2
    stability.build_models = build_models
    stability.OUT = OUT

    print("penalties held at the B2 values (not re-tuned inside the resamples):")
    print(f"  degree 1: H {deg1['H']:.4f}   A {deg1['A']:.4f}")
    print(f"  degree 2: H {deg2['H']:.4f}   A {deg2['A']:.4f}")

    floor = pd.read_csv(OUT / "b1_noise_floor.csv").set_index("division")
    for d in ("H", "A"):
        s = float(floor.loc[d, "sigma_hat"])
        print(f"  yardstick precision, {DIVISION_NAME[d]:9s}: "
              f"sigma/sqrt(10) = {s / np.sqrt(10):.2f} units")
    print()

    # The starter's loop, unmodified.
    tables = pd.concat([stability.run("H", dedup_h(load_h())),
                        stability.run("A", load_a())], ignore_index=True)

    bias_cols = [f"bias_q{i}" for i in (1, 2, 3)]
    sd_cols = [f"sd_q{i}" for i in (1, 2, 3)]
    tables["signed_mean_bias"] = tables[bias_cols].mean(axis=1)

    # Bias and variance can only be compared or added in squared units, and
    # the decomposition holds at each query point, so square first and then
    # average: mean of squares, not square of the mean.
    tables["bias2_mean"] = (tables[bias_cols] ** 2).mean(axis=1)
    tables["variance_mean"] = (tables[sd_cols] ** 2).mean(axis=1)
    tables["bias2_plus_variance"] = tables["bias2_mean"] + tables["variance_mean"]
    tables["bias_share_pct"] = (100 * tables["bias2_mean"]
                                / tables["bias2_plus_variance"]).round(1)

    tables["division_name"] = tables["division"].map(DIVISION_NAME)
    tables.to_csv(OUT / "b3_stability.csv", index=False)

    show = ["division_name", "model", "mean_sd", "mean_abs_bias", "signed_mean_bias"]
    print("B3 exhibit: spread of 20 bootstrap predictions, and distance from the truth")
    print(tables[show].to_string(index=False, float_format=lambda v: f"{v:8.2f}"))
    print()
    print("per query point (q1 low, q2 middle, q3 high demand)")
    print(tables[["division_name", "model"] + [f"sd_q{i}" for i in (1, 2, 3)] + bias_cols]
          .to_string(index=False, float_format=lambda v: f"{v:8.2f}"))
    print()

    print("the same rows in units^2, where bias and variance are comparable")
    print(tables[["division_name", "model", "bias2_mean", "variance_mean",
                  "bias2_plus_variance", "bias_share_pct"]]
          .to_string(index=False, float_format=lambda v: f"{v:9.1f}"))
    print()

    # The two dials, side by side.  This is the evidence for section 2's
    # central claim, and it needs both scripts' output to assemble:
    #
    #   number of terms  -> bias, PROVIDED there are rows to estimate them
    #   terms per row    -> variance, monotonically and then explosively
    #
    # The second is clean.  The first carries its proviso because Apparel
    # degree 2 has more terms than degree 1 and *worse* bias: at 2.2 rows per
    # coefficient the fit is so unconstrained that even its average over
    # resamples is displaced.
    b2 = pd.read_csv(OUT / "b2_table.csv")
    rows = []
    for r in tables.itertuples():
        degree = int(r.model.split("-")[1][0])
        treatment = "OLS" if "OLS" in r.model else "ridge"
        c = b2[(b2.division == r.division_name) & (b2.degree == degree)
               & (b2.treatment == treatment)].iloc[0]
        rows.append({"division": r.division_name, "model": r.model,
                     "terms": int(c.terms), "training_rows": int(c.training_rows),
                     "terms_per_row": c.terms_per_row, "rows_per_term": c.rows_per_term,
                     "tuned_alpha": c.tuned_alpha,
                     "bias2": round(r.bias2_mean, 1),
                     "variance": round(r.variance_mean, 1)})
    ledger = pd.DataFrame(rows)
    ledger.to_csv(OUT / "b3_flexibility_ledger.csv", index=False)
    print("the two dials: terms govern bias (given rows), terms per row govern variance")
    print(ledger.sort_values(["terms", "terms_per_row"]).to_string(index=False))
    print("  unpenalised cells sorted by terms per row show variance rising monotonically:")
    o = ledger[ledger.model.str.contains("OLS")].sort_values("terms_per_row")
    print("   " + "  ->  ".join(f"{r.terms_per_row:.4f}: var {r.variance:,.1f}"
                                for r in o.itertuples()))
    print("  at 12 terms bias is 224 and 294; at 90 terms it is 16 where rows allow")
    print("  and 475 where they do not, which is the proviso.")
    print()

    stability.figure(tables)
    print(f"wrote {OUT / 'b3_stability.csv'}, b3_stability.png")


if __name__ == "__main__":
    main()
