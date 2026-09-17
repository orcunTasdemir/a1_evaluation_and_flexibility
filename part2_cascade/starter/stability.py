"""
B3 -- the stability experiment.  The loop is written; the models are yours.

    python3 stability.py

What this measures.  A fitted model is a random object: it depends on which
training sample you happened to get (Handout 3 §2).  Refit the same procedure
on 20 bootstrap resamples of a division's extract, predict the same three
configurations each time, and you get 20 predictions per configuration.  Their
**spread** estimates variance.  The distance from their **average** to the
truth estimates bias.  The truth is available here because each query
configuration also appears in replicates.csv ten times, so the mean of those
ten estimates the true mean demand to within about sigma/sqrt(10) ~ 4 units.

What you have to do.  Fill in `build_models()` with the four B2 models, using
the penalties you tuned in B2 -- do NOT re-tune inside the resamples, or you
will be measuring something else.  Then read the output.

Everything else is fixed: 20 resamples from `bootstrap_indices()`, three query
points per division from `QUERY_CONFIGS`, the same seed for everyone.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge  # noqa: F401

from load import (FEATURES, N_BOOTSTRAP, QUERY_CONFIGS, TARGET,
                  bootstrap_indices, dedup_h, load_a, load_h, load_replicates,
                  poly_pipeline, query_frame)

OUT = Path(__file__).resolve().parent / "b3_outputs"

# ---------------------------------------------------------------------------
# YOUR B2 PENALTIES.  Replace these with the values your own B2 tuning chose.
# They are per division and per degree, and they are not all the same number --
# at one of the two degrees the two divisions land in the same place, and at the
# other they do not.  Which is which is part of what B2 asked you to notice.
# ---------------------------------------------------------------------------
RIDGE_ALPHA_DEG1 = {"H": None, "A": None}
RIDGE_ALPHA_DEG2 = {"H": None, "A": None}


def build_models(division: str) -> dict:
    """The four B2 models, ready to fit.  Fill this in.

    Return a dict mapping a label to a fresh, unfitted estimator.  A fresh one
    every call -- if you build them once outside the loop, every resample will
    refit the same object and you will still get the right answer, but it is
    easy to get wrong in a way that silently reuses a fitted model.

    Use `poly_pipeline(estimator, degree=d)` so that the basis and the scaler
    are fitted on each resample rather than once on the whole extract.

    The four:
        degree-1 OLS     poly_pipeline(LinearRegression(), degree=1)
        degree-1 ridge   poly_pipeline(Ridge(alpha=...), degree=1)
        degree-2 OLS     poly_pipeline(LinearRegression(), degree=2)
        degree-2 ridge   poly_pipeline(Ridge(alpha=...), degree=2)
    """
    raise NotImplementedError("fill in build_models()")


# ---------------------------------------------------------------------------
# Fixed below this line.
# ---------------------------------------------------------------------------

def truth_at_queries(division: str) -> np.ndarray:
    """Replicate-based estimate of true mean demand at the three query points."""
    r = load_replicates()
    r = r.loc[r["division"] == division]
    return (r.groupby("config_id")[TARGET].mean()
            .loc[QUERY_CONFIGS[division]].to_numpy())


def run(division: str, train: pd.DataFrame) -> pd.DataFrame:
    X = train[FEATURES].to_numpy()
    y = train[TARGET].to_numpy()
    Xq = query_frame(division).to_numpy()
    truth = truth_at_queries(division)

    draws = {label: [] for label in build_models(division)}
    for idx in bootstrap_indices(len(X), N_BOOTSTRAP):
        for label, model in build_models(division).items():
            model.fit(X[idx], y[idx])
            draws[label].append(model.predict(Xq))

    rows = []
    for label, preds in draws.items():
        P = np.asarray(preds)                       # (N_BOOTSTRAP, 3)
        sd = P.std(axis=0, ddof=1)                  # variance, per query point
        bias = P.mean(axis=0) - truth               # bias, per query point
        rows.append({
            "division": division,
            "model": label,
            **{f"sd_q{i + 1}": v for i, v in enumerate(sd)},
            **{f"bias_q{i + 1}": v for i, v in enumerate(bias)},
            "mean_sd": sd.mean(),
            "mean_abs_bias": np.abs(bias).mean(),
        })
    return pd.DataFrame(rows)


def figure(tables: pd.DataFrame) -> None:
    """One compact figure: mean spread against mean |bias|, by division."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=False)
    for ax, d in zip(axes, ("H", "A")):
        t = tables.loc[tables.division == d]
        ax.scatter(t.mean_abs_bias, t.mean_sd)
        for _, r in t.iterrows():
            ax.annotate(r.model, (r.mean_abs_bias, r.mean_sd),
                        textcoords="offset points", xytext=(6, 4), fontsize=8)
        ax.set_xlabel("mean |bias| across the three query points")
        ax.set_ylabel("mean sd of the 20 predictions")
        ax.set_title({"H": "Hardgoods", "A": "Apparel"}[d])
    fig.suptitle("B3: what flexibility and what a penalty do to bias and variance")
    fig.tight_layout()
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / "b3_stability.png", dpi=150)
    print(f"wrote {OUT / 'b3_stability.png'}")


def main() -> None:
    tables = pd.concat([run("H", dedup_h(load_h())), run("A", load_a())],
                       ignore_index=True)
    cols = ["division", "model", "mean_sd", "mean_abs_bias"]
    print(tables[cols].to_string(index=False, float_format=lambda v: f"{v:8.2f}"))
    OUT.mkdir(exist_ok=True)
    tables.to_csv(OUT / "b3_stability.csv", index=False)
    print(f"\nwrote {OUT / 'b3_stability.csv'}")
    figure(tables)
    print()
    print("Three questions, each answerable from a number in that table:")
    print("  1. What did raising the degree do to bias, and to variance,")
    print("     in each division?")
    print("  2. What did the penalty do to each, at each degree?")
    print("  3. The same four procedures, the same twelve fields, two")
    print("     divisions. Why is the answer not the same in both?")


if __name__ == "__main__":
    main()
