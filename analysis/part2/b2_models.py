"""
B2 -- four models per division, compared against the noise floor.

Two degrees {1, 2} crossed with two treatments {OLS, ridge}, in both
divisions: eight cells.  The protocol is the brief's, and the fixtures come
from the supplied part2_cascade/starter/load.py, unchanged:

    tune    5-fold CV with make_folds() (seed 575) on the division's own
            training extract.  poly_pipeline(estimator, degree=d) fits the
            basis expansion and the scaler inside each fold.  Ridge is tuned
            over ALPHA_GRID (25 log-spaced values, 1e-2 .. 1e4) by the
            lowest *cross-validated* MSE.  The test extract selects nothing.
    refit   each tuned configuration on all rows of that training extract.
    test    score once on test_extract(division).
    report  tuned penalty, CV MSE with its standard error across folds,
            test MSE, and test MSE - sigma^2_hat from B1.

Two decisions behind this, both recorded in NOTES.md:

  * The penalty is tuned to the CV *minimum*, not by the one-standard-error
    rule.  The 1-SE choice is computed and reported beside it as a
    diagnostic, because B2's question 2 asks where that rule bears on the
    answer.
  * The CV MSE is the *average of the five fold MSEs*, not a single MSE
    pooled over all out-of-fold predictions.  The standard error across
    folds only exists if the five are kept.  (A2 pooled, correctly: AUC is
    not an average of per-row losses.  Apparel's folds are 40/40/39/39/39,
    so here the two differ slightly.)

Outputs, all in analysis/outputs/:
    b2_table.csv            the B2 exhibit: eight cells
    b2_alpha_curves.csv     CV MSE per alpha per ridge cell; the endpoint
                            check and the 1-SE rule both read off this
    b2_penalties.csv        the tuned alphas, frozen here for B3 to read
    b2_contractor_check.csv our OLS CV MSEs against the quoted 336/231/414/618
    b2_differences.csv      every pairwise CV MSE difference within a
                            division, paired across folds, with its SE
    b2_test_decomposition.csv  the exact split of each test MSE into the
                            floor and the part a better model could remove
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "analysis" / "outputs"

# The supplied fixtures, imported rather than reimplemented.
sys.path.insert(0, str(ROOT / "part2_cascade" / "starter"))
from load import (ALPHA_GRID, FEATURES, TARGET, basis_size, dedup_h,  # noqa: E402
                  load_a, load_h, make_folds, poly_pipeline, test_extract)

DEGREES_USED = (1, 2)          # the brief's four models; no degree 3
DIVISIONS = ("H", "A")
DIVISION_NAME = {"H": "Hardgoods", "A": "Apparel"}

# The contractor's quoted 5-fold CV MSEs, from the brief's table.  Quoted,
# not reproduced -- the point of checking is to find out whether our refits
# under the prescribed protocol land anywhere near them.
CONTRACTOR_CV = {("H", 1): 336.0, ("H", 2): 231.0,
                 ("A", 1): 414.0, ("A", 2): 618.0}


def training_extract(division: str) -> pd.DataFrame:
    """The division's training rows.  Hardgoods goes through dedup_h()."""
    return dedup_h(load_h()) if division == "H" else load_a()


def fold_mses(df: pd.DataFrame, degree: int, estimator_factory) -> np.ndarray:
    """MSE within each of the five folds, preprocessing fitted inside each.

    estimator_factory is called once per fold so no state crosses folds.
    """
    X, y = df[FEATURES], df[TARGET].to_numpy()
    out = []
    for train_idx, held_idx in make_folds().split(X):
        model = poly_pipeline(estimator_factory(), degree=degree)
        model.fit(X.iloc[train_idx], y[train_idx])
        out.append(mean_squared_error(y[held_idx], model.predict(X.iloc[held_idx])))
    return np.asarray(out)


def cv_summary(mses: np.ndarray) -> tuple[float, float]:
    """Mean of the fold MSEs and its standard error across folds.

    SE = sd(MSE_1..MSE_K) / sqrt(K), the form in Handout 2 s4.5.  The K
    training sets overlap heavily, so the fold errors are correlated and
    this treats them as independent; it is a heuristic, which is how the
    one-standard-error rule uses it.
    """
    return float(mses.mean()), float(mses.std(ddof=1) / np.sqrt(len(mses)))


def tune_ridge(df: pd.DataFrame, degree: int) -> tuple[pd.DataFrame, dict]:
    """CV MSE for every alpha in ALPHA_GRID; pick the minimum.

    Also records the one-standard-error choice: the *largest* alpha (the
    simplest model, since a bigger penalty shrinks harder) whose CV MSE is
    within one SE of the minimum's CV MSE.
    """
    rows = []
    for alpha in ALPHA_GRID:
        mses = fold_mses(df, degree, lambda a=alpha: Ridge(alpha=a))
        mean, se = cv_summary(mses)
        rows.append({"alpha": alpha, "cv_mse": mean, "cv_se": se,
                     **{f"fold{k + 1}_mse": m for k, m in enumerate(mses)}})
    curve = pd.DataFrame(rows)

    best = curve.loc[curve["cv_mse"].idxmin()]
    within = curve.loc[curve["cv_mse"] <= best["cv_mse"] + best["cv_se"]]
    one_se = within.loc[within["alpha"].idxmax()]

    # The brief's endpoint warning: a winner on either end of the grid means
    # the optimum is outside it.
    on_endpoint = bool(np.isclose(best["alpha"], ALPHA_GRID[0])
                       or np.isclose(best["alpha"], ALPHA_GRID[-1]))
    return curve, {"alpha": float(best["alpha"]), "cv_mse": float(best["cv_mse"]),
                   "cv_se": float(best["cv_se"]), "on_endpoint": on_endpoint,
                   "alpha_1se": float(one_se["alpha"]),
                   "cv_mse_1se": float(one_se["cv_mse"]),
                   "fold_mses": np.array([best[f"fold{k + 1}_mse"] for k in range(5)],
                                         dtype=float)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # The floor from B1, read from its output rather than retyped.
    floor = pd.read_csv(OUT / "b1_noise_floor.csv").set_index("division")
    sigma2 = {d: float(floor.loc[d, "sigma2_hat"]) for d in DIVISIONS}

    print(f"terms in each basis on {len(FEATURES)} inputs: "
          f"degree 1 = {basis_size(1)}, degree 2 = {basis_size(2)}")
    print()

    rows, curves, folds_by_cell, decomp = [], [], {}, []

    for div in DIVISIONS:
        train = training_extract(div)
        test = test_extract(div)
        n_train = len(train)
        print(f"--- {DIVISION_NAME[div]}: {n_train:,} training rows, "
              f"{len(test):,} test rows, sigma^2_hat = {sigma2[div]:.2f}")

        for degree in DEGREES_USED:
            terms = basis_size(degree)
            for treatment in ("OLS", "ridge"):
                if treatment == "OLS":
                    mses = fold_mses(train, degree, LinearRegression)
                    cv_mse, cv_se = cv_summary(mses)
                    alpha = np.nan
                    extra = {"alpha_1se": np.nan, "cv_mse_1se": np.nan,
                             "alpha_on_grid_endpoint": ""}
                    estimator = LinearRegression()
                else:
                    curve, tuned = tune_ridge(train, degree)
                    curve.insert(0, "division", DIVISION_NAME[div])
                    curve.insert(1, "degree", degree)
                    curves.append(curve)
                    mses = tuned["fold_mses"]
                    cv_mse, cv_se = tuned["cv_mse"], tuned["cv_se"]
                    alpha = tuned["alpha"]
                    extra = {"alpha_1se": tuned["alpha_1se"],
                             "cv_mse_1se": tuned["cv_mse_1se"],
                             "alpha_on_grid_endpoint": "YES" if tuned["on_endpoint"] else "no"}
                    estimator = Ridge(alpha=alpha)
                    if tuned["on_endpoint"]:
                        print(f"    WARNING: tuned alpha is on a grid endpoint "
                              f"({alpha:g}); the optimum lies outside ALPHA_GRID")

                # Refit on all training rows, then score the test extract once.
                model = poly_pipeline(estimator, degree=degree)
                model.fit(train[FEATURES], train[TARGET].to_numpy())
                pred = model.predict(test[FEATURES])
                test_mse = float(mean_squared_error(test[TARGET], pred))

                cell = f"{DIVISION_NAME[div]} degree-{degree} {treatment}"
                folds_by_cell[cell] = mses
                rows.append({
                    "division": DIVISION_NAME[div], "degree": degree,
                    "treatment": treatment, "terms": terms,
                    "training_rows": n_train,
                    "terms_per_row": round(terms / n_train, 4),
                    "tuned_alpha": alpha,
                    "cv_mse": round(cv_mse, 2), "cv_se": round(cv_se, 2),
                    "test_mse": round(test_mse, 2),
                    "test_mse_minus_sigma2": round(test_mse - sigma2[div], 2),
                    **extra,
                })
                print(f"    degree {degree} {treatment:<5s} "
                      f"alpha={'' if np.isnan(alpha) else f'{alpha:9.3f}':>9s} "
                      f"CV {cv_mse:8.2f} +/- {cv_se:6.2f}   "
                      f"test {test_mse:8.2f}   test - sigma^2 {test_mse - sigma2[div]:8.2f}")

                # Exact split of the test MSE.  All ten replicates of a
                # configuration are identical on every feature, so the model
                # predicts one value for the group and the MSE separates into
                # the within-group scatter (the floor) and the squared error
                # against the group means (what a better model could remove).
                g = test.groupby("config_id")
                ybar = g[TARGET].mean()
                yhat = pd.Series(pred, index=test.index).groupby(test["config_id"]).first()
                within_ss = float(((test[TARGET] - test["config_id"].map(ybar)) ** 2).sum())
                struct = float(((ybar - yhat) ** 2).mean())
                decomp.append({
                    "division": DIVISION_NAME[div], "degree": degree,
                    "treatment": treatment, "test_mse": round(test_mse, 2),
                    "floor_part": round(within_ss / len(test), 2),
                    "structural_part": round(struct, 2),
                    "identity_check": round(within_ss / len(test) + struct - test_mse, 10),
                    "test_mse_minus_sigma2": round(test_mse - sigma2[div], 2),
                })
        print()

    table = pd.DataFrame(rows)
    table.to_csv(OUT / "b2_table.csv", index=False)
    pd.concat(curves, ignore_index=True).to_csv(OUT / "b2_alpha_curves.csv", index=False)
    table.loc[table["treatment"].eq("ridge"),
              ["division", "degree", "tuned_alpha", "alpha_1se"]] \
         .to_csv(OUT / "b2_penalties.csv", index=False)
    pd.DataFrame(decomp).to_csv(OUT / "b2_test_decomposition.csv", index=False)

    # Our OLS CV MSEs against the contractor's quoted figures.
    check = []
    for (div, degree), quoted in CONTRACTOR_CV.items():
        m = table.query("division == @DIVISION_NAME[@div] and degree == @degree "
                        "and treatment == 'OLS'").iloc[0]
        check.append({"division": DIVISION_NAME[div], "degree": degree,
                      "contractor_quoted": quoted, "ours_cv_mse": m["cv_mse"],
                      "ours_cv_se": m["cv_se"],
                      "difference": round(m["cv_mse"] - quoted, 2),
                      "ses_from_quoted": round((m["cv_mse"] - quoted) / m["cv_se"], 2)})
    check = pd.DataFrame(check)
    check.to_csv(OUT / "b2_contractor_check.csv", index=False)

    # Every pairwise CV difference inside a division, paired across the five
    # shared folds.  Pairing is the right comparison: the folds are identical
    # across cells, so the fold-to-fold variation cancels.
    diffs = []
    for div in DIVISIONS:
        cells = [c for c in folds_by_cell if c.startswith(DIVISION_NAME[div])]
        for i, a in enumerate(cells):
            for b in cells[i + 1:]:
                d = folds_by_cell[a] - folds_by_cell[b]
                mean, se = cv_summary(d)
                diffs.append({"division": DIVISION_NAME[div],
                              "model_a": a.replace(DIVISION_NAME[div] + " ", ""),
                              "model_b": b.replace(DIVISION_NAME[div] + " ", ""),
                              "mean_difference": round(mean, 2),
                              "se_of_difference": round(se, 2),
                              "ses_from_zero": round(mean / se, 2) if se else np.nan})
    diffs = pd.DataFrame(diffs)
    diffs.to_csv(OUT / "b2_differences.csv", index=False)

    print("B2 exhibit")
    print(table[["division", "degree", "treatment", "terms", "terms_per_row",
                 "tuned_alpha", "cv_mse", "cv_se", "test_mse",
                 "test_mse_minus_sigma2"]].to_string(index=False))
    print()
    print("tuned penalty vs the one-standard-error choice (diagnostic)")
    print(table.loc[table["treatment"].eq("ridge"),
                    ["division", "degree", "tuned_alpha", "cv_mse", "cv_se",
                     "alpha_1se", "cv_mse_1se", "alpha_on_grid_endpoint"]]
               .to_string(index=False))
    print()
    print("our OLS CV MSE against the contractor's quoted figures")
    print(check.to_string(index=False))
    print()
    print("pairwise CV differences, paired across the five shared folds")
    print(diffs.to_string(index=False))
    print()
    print("exact split of each test MSE (floor part + structural part)")
    print(pd.DataFrame(decomp).to_string(index=False))
    print()
    print(f"wrote {OUT / 'b2_table.csv'}, b2_alpha_curves.csv, b2_penalties.csv, "
          f"b2_contractor_check.csv, b2_differences.csv, b2_test_decomposition.csv")


if __name__ == "__main__":
    main()
