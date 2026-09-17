"""
Optional, no marks, about two minutes.  Run it and look at the two figures.

    python3 sweep.py

Panel 1 turns the flexibility dial by hand: degree 1, 2 and 3 on the same
twelve fields, fitted by unpenalised least squares, with training error and
5-fold cross-validated error plotted against the number of terms in the basis.
Handout 3 §1.4 describes the shape you are about to see; the point of running it
is that the two divisions do not produce the same shape, and the reason is
sample size.

Panel 2 turns the same dial the other way, continuously: degree-2 ridge across
the whole penalty grid.  Large alpha is a rigid model, small alpha a flexible
one, and the minimum of the cross-validated curve is what B2 tunes to.

Midterm 1 will ask you to read a plot like these.  Worth doing before the exam
even if you have not started Part B.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import cross_val_score

from load import (ALPHA_GRID, DEGREES, FEATURES, TARGET, basis_size, dedup_h,
                  load_a, load_h, make_folds, poly_pipeline)

OUT = Path(__file__).resolve().parent / "sweep_outputs"
CV = make_folds()


def degree_sweep(X, y):
    train, cv = [], []
    for d in DEGREES:
        pipe = poly_pipeline(LinearRegression(), degree=d)
        s = cross_val_score(pipe, X, y, scoring="neg_mean_squared_error",
                            cv=CV, n_jobs=-1)
        cv.append(-s.mean())
        pipe.fit(X, y)
        train.append(mean_squared_error(y, pipe.predict(X)))
    return np.array(train), np.array(cv)


def alpha_sweep(X, y):
    cv = []
    for a in ALPHA_GRID:
        s = cross_val_score(poly_pipeline(Ridge(alpha=a), degree=2), X, y,
                            scoring="neg_mean_squared_error", cv=CV, n_jobs=-1)
        cv.append(-s.mean())
    return np.array(cv)


def main():
    OUT.mkdir(exist_ok=True)
    divisions = (("Hardgoods", dedup_h(load_h())), ("Apparel", load_a()))
    terms = [basis_size(d) for d in DEGREES]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (name, df) in zip(axes, divisions):
        X, y = df[FEATURES].to_numpy(), df[TARGET].to_numpy()
        train, cv = degree_sweep(X, y)
        ax.plot(terms, train, "o-", label="training MSE")
        ax.plot(terms, cv, "s-", label="5-fold CV MSE")
        ax.set_xscale("log")
        ax.set_xticks(terms)
        ax.set_xticklabels([f"deg {d}\n{t} terms" for d, t in zip(DEGREES, terms)])
        ax.set_title(f"{name}  (n = {len(df):,})")
        ax.set_ylabel("MSE")
        ax.legend()
        for d, t, c in zip(DEGREES, terms, cv):
            ax.annotate(f"{c:,.0f}", (t, c), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=8)
    fig.suptitle("Turning the flexibility dial by hand: unpenalised least squares")
    fig.tight_layout()
    fig.savefig(OUT / "degree_sweep.png", dpi=150)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (name, df) in zip(axes, divisions):
        X, y = df[FEATURES].to_numpy(), df[TARGET].to_numpy()
        cv = alpha_sweep(X, y)
        ax.plot(ALPHA_GRID, cv, "-")
        best = int(np.argmin(cv))
        ax.plot(ALPHA_GRID[best], cv[best], "o")
        ax.annotate(f"alpha = {ALPHA_GRID[best]:.3g}\nCV = {cv[best]:,.0f}",
                    (ALPHA_GRID[best], cv[best]), textcoords="offset points",
                    xytext=(10, 10), fontsize=8)
        ax.set_xscale("log")
        ax.set_xlabel("ridge penalty alpha   (rigid <-- ... --> flexible)")
        ax.set_ylabel("5-fold CV MSE")
        ax.set_title(f"{name}  (n = {len(df):,})")
    fig.suptitle("The same dial, continuously: degree-2 ridge across the penalty grid")
    fig.tight_layout()
    fig.savefig(OUT / "alpha_sweep.png", dpi=150)

    print(f"wrote {OUT / 'degree_sweep.png'}")
    print(f"wrote {OUT / 'alpha_sweep.png'}")
    print()
    print("Two things to notice, and one question to take to Part B:")
    print("  * where the cross-validated curve turns up, and whether it turns")
    print("    up at all inside the range plotted, in each division;")
    print("  * how far the best penalty is from zero in each division.")
    print("  * the two divisions record the same twelve fields, by the same")
    print("    job, for the same company. So what is actually different?")


if __name__ == "__main__":
    main()
