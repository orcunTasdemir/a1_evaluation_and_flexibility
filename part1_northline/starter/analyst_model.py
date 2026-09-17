"""
The junior analyst's pipeline, exactly as they ran it.

This file is given to you so that you do not have to reverse-engineer the
headline number.  It runs, it reproduces the figures quoted in the brief, and
it is wrong.  Your job is to find out *why* it is wrong -- not to rebuild it.

Read it.  Every line is a defensible-looking choice, and several of them are
the assignment.  Note in particular that the modelling itself is careful: the
encoder and the scaler are fitted inside each fold, so there is no
preprocessing leak here.  Whatever is wrong with this number is wrong at the
level of the protocol, not the pipeline.

    python3 analyst_model.py

Expected output (Python 3.10+, scikit-learn >= 1.3; small version drift is
normal and does not matter):

    rows                       33,340
    5-fold cross-validated AUC  0.967
    5-fold cross-validated AP   0.899
    estimated programme value   $19,774 per quarter
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")

DATA = Path(__file__).resolve().parents[1] / "data" / "member_months.csv"

# Economics from the finance team, per the brief.
OFFER_COST = 18.0        # cost of extending one retention offer, USD
MEMBER_LTV = 240.0       # value of a member who stays, USD
OFFER_CONVERSION = 0.35  # fraction of would-be churners retained by the offer

TARGET = "churn_next_60d"
# The analyst dropped only the identifier and the two date strings, on the
# grounds that they are not numeric features.  Everything else was kept:
# "figured the model can decide what's useful."
NOT_FEATURES = (TARGET, "member_id", "snapshot_month", "signup_month")


def analyst_pipeline(categorical, numeric) -> Pipeline:
    """One-hot the categoricals, standardise the rest, fit logistic regression.

    Everything fitted from data lives inside this object, so when it is fitted
    on a fold's training portion the encoder and the scaler see only that
    portion.  This much the analyst got right.
    """
    return Pipeline([
        ("prep", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), categorical),
            ("num", StandardScaler(), numeric),
        ])),
        ("est", LogisticRegression(max_iter=2000)),
    ])


def main() -> None:
    df = pd.read_csv(DATA)
    y = df[TARGET].to_numpy()

    features = [c for c in df.columns if c not in NOT_FEATURES]
    categorical = [c for c in features if not pd.api.types.is_numeric_dtype(df[c])]
    numeric = [c for c in features if c not in categorical]
    X = df[features]

    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    oof = np.zeros(len(df))
    for train_idx, test_idx in folds.split(X, y):
        model = analyst_pipeline(categorical, numeric)
        model.fit(X.iloc[train_idx], y[train_idx])
        oof[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]

    auc = roc_auc_score(y, oof)
    ap = average_precision_score(y, oof)

    # Value of one targeting decision: offer a churner and you net
    # LTV * conversion - cost; offer a non-churner and you lose the cost.
    realised = y * MEMBER_LTV * OFFER_CONVERSION - OFFER_COST
    grid = np.linspace(0.005, 0.6, 400)
    values = [float(np.sum((oof > t) * realised)) for t in grid]
    best = int(np.argmax(values))
    # 24 months of data = 8 quarters.
    per_quarter = values[best] / 8.0

    print(f"rows                        {len(df):,}")
    print(f"unique members              {df['member_id'].nunique():,}")
    print(f"features used               {len(features)}")
    print(f"base rate                   {y.mean():.4f}")
    print()
    print(f"5-fold cross-validated AUC  {auc:.3f}")
    print(f"5-fold cross-validated AP   {ap:.3f}")
    print(f"optimal threshold           {grid[best]:.3f}")
    print(f"estimated programme value   ${per_quarter:,.0f} per quarter")
    print()
    print("Recommendation: strong signal, move to production this quarter.")


if __name__ == "__main__":
    main()
