"""
B1 -- the noise floor.  Cascade Outdoor.

Each group of ten rows in replicates.csv is identical on all twelve recorded
fields and differs only in `units`, so the spread within a group is variation
no model built from those fields could have predicted.  Pooling it over the
45 configurations in a division estimates that division's irreducible error
(Handout 1 eq. 2, Handout 3 s3.3):

    sigma^2_hat = sum_g sum_r (y_gr - ybar_g)^2 / sum_g (m_g - 1)

reported with the approximate standard error the brief specifies,

    se = sigma^2_hat * sqrt(2 / dof),      dof = sum_g (m_g - 1)

which is 45 x 9 = 405 when every configuration has ten replicates.

The estimator assumes the twelve fields really are constant within a
config_id.  The data dictionary says so; this script checks it and raises if
not, because if a feature varied inside a group then part of the within-group
spread would be signal and the floor would be overstated.

Nothing is fitted here and nothing is selected.  Reading `units` from the
replicate extract for this purpose is one of its two sanctioned uses.

Outputs, in analysis/outputs/:
    b1_noise_floor.csv       sigma^2, its SE, sigma, dof, per division
    b1_config_check.csv      per division, that the 12 fields are constant
                             within every config_id and every group has 10 rows
    b1_variance_shape.csv    whether the floor is level-dependent, so the memo
                             can say "average unavoidable error" and defend it
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "analysis" / "outputs"

sys.path.insert(0, str(ROOT / "part2_cascade" / "starter"))
from load import QUERY_CONFIGS, FEATURES, TARGET, test_extract  # noqa: E402

DIVISIONS = {"H": "Hardgoods", "A": "Apparel"}

# The contractor's cross-validated MSEs, quoted from the brief.  Not computed
# here; B2 refits these specifications under the prescribed protocol and will
# say whether they reproduce.
CONTRACTOR_CV_MSE = {("H", 1): 336, ("H", 2): 231,
                     ("A", 1): 414, ("A", 2): 618}


def check_configs(df: pd.DataFrame, division: str) -> dict:
    """The twelve fields must be constant inside every config_id."""
    sizes = df.groupby("config_id").size()
    varying = {}
    for col in FEATURES:
        n_distinct = df.groupby("config_id")[col].nunique()
        bad = int((n_distinct > 1).sum())
        if bad:
            varying[col] = bad
    row = {
        "division": division,
        "configs": int(df["config_id"].nunique()),
        "rows": len(df),
        "group_sizes": ",".join(str(s) for s in sorted(sizes.unique())),
        "all_groups_size_10": bool((sizes == 10).all()),
        "fields_checked": len(FEATURES),
        "fields_varying_within_a_config": len(varying),
        "units_varies_within_a_config": bool(
            (df.groupby("config_id")[TARGET].nunique() > 1).all()),
    }
    if varying:
        raise RuntimeError(
            f"division {division}: these recorded fields are not constant "
            f"within a config_id, so within-group spread is not pure noise: {varying}")
    return row


def noise_floor(df: pd.DataFrame, division: str) -> dict:
    """Pooled within-configuration variance, and its approximate SE."""
    g = df.groupby("config_id")[TARGET]
    # sum_g sum_r (y_gr - ybar_g)^2, accumulated directly from the definition
    ss_within = float(((df[TARGET] - g.transform("mean")) ** 2).sum())
    dof = int((g.size() - 1).sum())
    sigma2 = ss_within / dof
    se = sigma2 * np.sqrt(2.0 / dof)

    # Cross-check: with equal group sizes the pooled variance is the mean of
    # the per-group sample variances.  Two routes agreeing is the check.
    mean_of_group_vars = float(g.var(ddof=1).mean())
    if df.groupby("config_id").size().nunique() == 1:
        assert abs(sigma2 - mean_of_group_vars) < 1e-9, (sigma2, mean_of_group_vars)

    return {
        "division": division,
        "name": DIVISIONS[division],
        "configs": int(df["config_id"].nunique()),
        "replicates_per_config": int(df.groupby("config_id").size().iloc[0]),
        "rows": len(df),
        "dof": dof,
        "sigma2_hat": round(sigma2, 2),
        "se_sigma2_hat": round(se, 2),
        "sigma_hat": round(float(np.sqrt(sigma2)), 2),
        "mean_units": round(float(df[TARGET].mean()), 2),
        "contractor_best_cv_mse": min(CONTRACTOR_CV_MSE[(division, 1)],
                                      CONTRACTOR_CV_MSE[(division, 2)]),
    }


def variance_mean_relationship(df: pd.DataFrame, division: str) -> dict:
    """Is the floor the same everywhere, or does it grow with demand?

    sigma^2 is written as one number in Handout 3 eq. (4) -- Bias^2 and Var
    carry bars for averaging over x and sigma^2 does not -- which assumes the
    floor does not depend on where you are in feature space.  `units` is a
    count, and Handout 1 s4.7 warns that for counts "the variance typically
    grows with the mean", so this is worth testing rather than assuming.

    Regressing a configuration's variance on its mean gives slope 1 under a
    Poisson-like law and slope 0 under a constant floor.  Each configuration's
    variance comes from ten observations, so it is a very noisy point and the
    slope's standard error is correspondingly wide; an inconclusive answer is
    the honest one and is reported as such.
    """
    g = df.groupby("config_id")[TARGET]
    m, v = g.mean().to_numpy(), g.var(ddof=1).to_numpy()
    slope, intercept = np.polyfit(m, v, 1)
    resid = v - (intercept + slope * m)
    se_slope = float(resid.std(ddof=2) / (m.std(ddof=0) * np.sqrt(len(m))))
    sigma2 = float(v.mean())
    return {
        "division": division,
        "name": DIVISIONS[division],
        "config_mean_min": round(float(m.min()), 1),
        "config_mean_max": round(float(m.max()), 1),
        "slope_var_on_mean": round(float(slope), 3),
        "se_slope": round(se_slope, 3),
        "consistent_with_poisson_slope_1": bool(abs(slope - 1) < 2 * se_slope),
        "consistent_with_constant_variance_slope_0": bool(abs(slope) < 2 * se_slope),
        "overdispersion_vs_poisson": round(sigma2 / float(m.mean()), 2),
        "se_of_one_config_variance": round(0.4714 * sigma2, 1),
        # How wide the spread actually is.  Some of this is real
        # heteroscedasticity and some is ten-observation noise; the slope above
        # is what tries, and fails, to tell them apart.  Reported so the memo's
        # word "average" can be defended with a range rather than a hedge.
        "config_var_min": round(float(v.min()), 1),
        "config_var_max": round(float(v.max()), 1),
        "config_sd_min": round(float(np.sqrt(v.min())), 1),
        "config_sd_max": round(float(np.sqrt(v.max())), 1),
        "pooled_sd": round(float(np.sqrt(sigma2)), 1),
    }


def query_point_yardsticks(df: pd.DataFrame, division: str) -> pd.DataFrame:
    """The B3 yardstick at each query point, not pooled.

    B3 judges a bias against sigma_hat/sqrt(10), about 3.85 units in Hardgoods.
    That is the pooled figure.  If the floor varies by configuration then the
    yardstick does too, so this reports it per query point.  It changes no B3
    conclusion, because the biases that matter are 15 to 32 units, but it is
    the honest version of "a bias under about four units is indistinguishable
    from zero".
    """
    g = df.groupby("config_id")[TARGET]
    sd = np.sqrt(g.var(ddof=1))
    rows = []
    for i, cid in enumerate(QUERY_CONFIGS[division], start=1):
        rows.append({
            "division": division,
            "name": DIVISIONS[division],
            "query_point": f"q{i}",
            "config_id": cid,
            "config_mean_units": round(float(g.mean().loc[cid]), 2),
            "config_sd_units": round(float(sd.loc[cid]), 2),
            "yardstick_sd_over_sqrt10": round(float(sd.loc[cid]) / np.sqrt(10), 2),
        })
    return pd.DataFrame(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    checks, floors, shapes, yards = [], [], [], []
    for code in DIVISIONS:
        df = test_extract(code)
        checks.append(check_configs(df, code))
        floors.append(noise_floor(df, code))
        shapes.append(variance_mean_relationship(df, code))
        yards.append(query_point_yardsticks(df, code))

    check = pd.DataFrame(checks)
    floor = pd.DataFrame(floors)

    # How much of the contractor's best number is floor, and how much is not.
    floor["contractor_best_minus_floor"] = (
        floor["contractor_best_cv_mse"] - floor["sigma2_hat"]).round(2)
    floor["share_of_contractor_best_that_is_floor"] = (
        floor["sigma2_hat"] / floor["contractor_best_cv_mse"]).round(4)

    shape = pd.DataFrame(shapes)
    yard = pd.concat(yards, ignore_index=True)
    shape.to_csv(OUT / "b1_variance_shape.csv", index=False)
    yard.to_csv(OUT / "b1_query_yardsticks.csv", index=False)
    check.to_csv(OUT / "b1_config_check.csv", index=False)
    floor.to_csv(OUT / "b1_noise_floor.csv", index=False)

    print("configuration check (the estimator's assumption)")
    print(check.to_string(index=False))
    print()
    print("B1 -- the noise floor")
    print(floor.to_string(index=False))
    print()
    h = floor.set_index("division").loc["H"]
    a = floor.set_index("division").loc["A"]
    print(f"Hardgoods sigma^2 = {h.sigma2_hat:,.1f} +/- {h.se_sigma2_hat:,.1f} "
          f"(sigma = {h.sigma_hat:,.1f} units)")
    print(f"Apparel   sigma^2 = {a.sigma2_hat:,.1f} +/- {a.se_sigma2_hat:,.1f} "
          f"(sigma = {a.sigma_hat:,.1f} units)")
    diff = a.sigma2_hat - h.sigma2_hat
    se_diff = float(np.hypot(h.se_sigma2_hat, a.se_sigma2_hat))
    print(f"difference (A - H) = {diff:,.1f} with a standard error of "
          f"{se_diff:,.1f}, i.e. {abs(diff) / se_diff:.2f} standard errors")
    # The memo does not claim the floors are equal, only that the data cannot
    # tell them apart and that no admissible difference explains the
    # contractor's gap.  Both halves need the interval, not just the point.
    lo, hi = diff - 1.96 * se_diff, diff + 1.96 * se_diff
    widest = max(abs(lo), abs(hi))
    best_h = min(CONTRACTOR_CV_MSE[("H", d)] for d in (1, 2))
    best_a = min(CONTRACTOR_CV_MSE[("A", d)] for d in (1, 2))
    gap = best_a - best_h
    print(f"95% interval on the difference: {lo:,.1f} to {hi:,.1f} units^2, so the "
          f"floors differ by at most {widest:,.0f} even at its edge")
    print(f"against the contractor's own gap of {gap:,.0f} ({best_a:,.0f} - "
          f"{best_h:,.0f}), that is at most {100 * widest / gap:.0f}% of what he "
          f"attributed to difficulty")
    print()
    print("is the floor the same everywhere?  variance against demand level")
    print(shape.to_string(index=False))
    print("  (slope 1 = Poisson-like, slope 0 = constant floor; a configuration's")
    print("   variance comes from ten rows, so the slope is poorly determined and")
    print("   an inconclusive answer is the honest one)")
    print()
    for r in shape.itertuples():
        print(f"{r.name}: per-configuration variance spans {r.config_var_min:,.0f} to "
              f"{r.config_var_max:,.0f}, i.e. a per-week sd of {r.config_sd_min} to "
              f"{r.config_sd_max} units against a pooled {r.pooled_sd}")
    print()
    print("B3's yardstick per query point, rather than pooled")
    print(yard.to_string(index=False))
    print("  (changes no B3 conclusion: the biases that matter are 15 to 32 units)")
    print()
    print("Scope of the estimate: the two caveats compound.  A constant floor")
    print("would make hand-picked configurations harmless, and randomly sampled")
    print("configurations would make a varying floor average out.  It is only")
    print("chosen points AND a possibly varying floor together that limit this")
    print("figure to the floor where these 45 configurations sit.")
    print("Note what is NOT affected: B2's test MSE averages over the same 45")
    print("configurations with the same weights that sigma^2_hat pools over, so")
    print("test MSE - sigma^2_hat compares two averages over an identical set of")
    print("points and the split is exact however the floor varies.")
    print()
    print(f"wrote {OUT / 'b1_noise_floor.csv'}, b1_config_check.csv, "
          f"b1_variance_shape.csv, b1_query_yardsticks.csv")


if __name__ == "__main__":
    main()
