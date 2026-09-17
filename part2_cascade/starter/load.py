"""
Assignment 1, Part B starter -- Cascade Outdoor weekly unit forecasting.

Everything that would otherwise differ between submissions for no good reason
is fixed here: the fold assignments, the polynomial bases, the penalty grids,
the bootstrap resamples and the query points.

Nothing here cleans the data, estimates the floor, fits a model, chooses a
penalty or interprets anything.  Those are the assignment.

Usage:
    from load import (load_h, load_a, load_replicates, test_extract,
                      dedup_h, FEATURES, TARGET, make_folds,
                      poly_pipeline, DEGREES, ALPHA_GRID,
                      bootstrap_indices, QUERY_CONFIGS, query_frame,
                      N_BOOTSTRAP)
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

DATA = Path(__file__).resolve().parents[1] / "data"

TARGET = "units"
ID_COLS = ("store_id", "week_id")

# The twelve recorded predictor fields, in extract order.  Both divisions
# record all twelve.  Whether all twelve matter is not stated anywhere.
FEATURES = [
    "promo_depth_pct", "own_price_index", "competitor_price_index",
    "marketing_spend_k", "temp_f", "loyalty_share", "store_sqft_k",
    "inventory_cover_wks", "assortment_breadth", "catalog_pages",
    "returns_rate", "staffing_hours",
]

# ---------------------------------------------------------------- loaders

def load_h() -> pd.DataFrame:
    """Hardgoods store-weeks, exactly as the pipeline delivered them.

    Read the pipeline note in the data dictionary before you model on this.
    """
    return pd.read_csv(DATA / "division_h.csv")


def load_a() -> pd.DataFrame:
    """Apparel store-weeks.  Already cleaned -- see the data dictionary."""
    return pd.read_csv(DATA / "division_a.csv")


def load_replicates() -> pd.DataFrame:
    """The controlled repeat-observation extract, and the final test set.

    Use it for two things and no others: estimating the noise floor, and
    scoring each tuned model exactly once at the end.
    """
    return pd.read_csv(DATA / "replicates.csv")


def test_extract(division: str) -> pd.DataFrame:
    """The replicate rows for one division ('H' or 'A').  Your test set.

    Score each tuned configuration on this exactly once, at the end.
    """
    r = load_replicates()
    return r.loc[r["division"] == division].reset_index(drop=True)


def dedup_h(df: pd.DataFrame) -> pd.DataFrame:
    """The Hardgoods extract with the duplicated block removed.

    The load behind `division_h.csv` was re-run and appended rather than
    replaced (ticket CO-4471), so affected store-weeks appear twice.  Use
    this for everything in Part B.
    """
    return df.drop_duplicates(subset=["week_id"]).reset_index(drop=True)


# ------------------------------------------------- the fixed CV protocol

CV_SEED = 575


def make_folds(n_splits: int = 5) -> KFold:
    """The fold assignment every submission uses.  Do not change the seed."""
    return KFold(n_splits=n_splits, shuffle=True, random_state=CV_SEED)


# The flexibility dial for this assignment.  Degree 1 is the twelve recorded
# fields as they come; degree 2 adds every square and every pairwise product;
# degree 3 adds every triple.  The term counts are worth knowing before you
# fit anything, and `basis_size()` prints them.
DEGREES = (1, 2, 3)


def basis_size(degree: int, p: int = len(FEATURES)) -> int:
    """Number of terms in the degree-`degree` basis on `p` inputs."""
    from math import comb
    return comb(p + degree, degree) - 1


def poly_pipeline(estimator, degree: int = 2) -> Pipeline:
    """Degree-`degree` basis -> standardise -> estimator, as one pipeline.

    Fitting this inside a cross-validation fold fits the expansion and the
    scaler on the training part of that fold only, which is the point.
    Passing the estimator a pre-expanded, pre-scaled matrix would leak the
    held-out rows into the preprocessing; see Handout 1 §7.2.

    Standardising *before* the penalty is not optional.  Ridge penalises
    coefficients, so it penalises a term measured in thousands far less than
    the same term measured in units; on a raw polynomial basis the result is
    approximately OLS wearing a penalty's name.  Handout 3 §5.2.
    """
    return Pipeline([
        ("poly", PolynomialFeatures(degree=degree, include_bias=False)),
        ("scale", StandardScaler()),
        ("est", estimator),
    ])


# 25 penalties, log-spaced.  Both divisions' best value falls inside this
# range at every degree; if yours lands on an endpoint, something upstream
# is wrong.
ALPHA_GRID = np.logspace(-2, 4, 25)


# ------------------------------------------------------- Part B3 fixtures

N_BOOTSTRAP = 20

# Three configurations per division -- low, middle and high demand.  Each one
# also appears in replicates.csv, so the average of its ten replicate weeks is
# an estimate of the true mean demand there, accurate to about sigma/sqrt(10).
QUERY_CONFIGS = {
    "H": ["H43", "H16", "H01"],
    "A": ["A10", "A08", "A07"],
}


def query_frame(division: str) -> pd.DataFrame:
    """The three query points for a division, one row each, FEATURES columns.

    Indexed by config_id and in the order given by QUERY_CONFIGS.
    """
    r = load_replicates()
    r = r.loc[r["division"] == division]
    first = r.groupby("config_id")[FEATURES].first()
    return first.loc[QUERY_CONFIGS[division]]


def bootstrap_indices(n: int, n_draws: int = N_BOOTSTRAP, seed: int = CV_SEED):
    """Yield `n_draws` index arrays, each a bootstrap resample of size n.

    Fixed so that everyone's B3 resamples the same way and differences
    between submissions come from the modelling, not the plumbing.
    """
    rng = np.random.default_rng(seed)
    for _ in range(n_draws):
        yield rng.integers(0, n, n)


# ------------------------------------------------------------------ sanity

if __name__ == "__main__":
    for name, df in (("division_h", load_h()), ("division_a", load_a())):
        print(f"{name:12s} rows={len(df):5,}  features={len(FEATURES)}  "
              f"units: mean={df[TARGET].mean():7.1f} sd={df[TARGET].std():6.1f} "
              f"min={df[TARGET].min():7.1f} max={df[TARGET].max():8.1f}")
    r = load_replicates()
    print(f"replicates   rows={len(r):5,}  configs={r['config_id'].nunique()}  "
          f"divisions={sorted(r['division'].unique())}  "
          f"rows per config={sorted(r.groupby('config_id').size().unique())}")
    print()
    print("terms in each basis, on 12 inputs:")
    for d in DEGREES:
        print(f"  degree {d}: {basis_size(d):5,} terms")
    for d in ("H", "A"):
        print(f"query points {d}: {QUERY_CONFIGS[d]}")
