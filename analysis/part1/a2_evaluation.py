"""
A2 -- an evaluation that matches deployment.  Northline Fitness churn.

Four changes to the analyst's protocol, one at a time, cumulative, in the
order 1 -> 2 -> 3 -> 4, with the AUC recorded after each.  The model itself
is never touched: every row fits the supplied analyst_pipeline() unchanged.

    harness check   analyst's protocol on the raw file, all months
                    (should reproduce the printed 0.967; selects nothing,
                    appears in no exhibit)
    row 0           analyst's protocol on deduplicated rows in the building
                    window (months <= TRAIN_END), 5-fold stratified CV
    row 1           + admissible columns only
    row 2           + one member never in both fitting and held-out fold
    row 3           + past to future: fit on the building window, score the
                    test window (months >= TEST_START) once
    row 4           + the row-3 scores split by segment

Rows 0-2 are cross-validated on the building window.  Rows 3-4 are the test
window.  The validation month (VALID_MONTH) is not used: A2 makes no choice
by looking at data.

Outputs, all in analysis/outputs/:
    a2_table.csv        the A2 exhibit, one line per row above
    a2_columns.csv      every column in the file, kept or dropped, with the
                        timing note from the data dictionary that decides it
    a2_test_scores.csv  the test-window predictions from row 3, saved so A3
                        reads them and never refits or rescores the test set
    a2_fold_overlap.csv how many building-window members have rows in more
                        than one fold under the analyst's random split; the
                        overlap change 2 removes
    a2_odds_ratios.csv  the row-3 model's coefficients as odds ratios, a
                        diagnostic for reading what the model learned
                        (Handout 2 s7.2); fitted on the building window only
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "analysis" / "outputs"

sys.path.insert(0, str(HERE))
from prep import TARGET, TRAIN_END, TEST_START, load_clean, load_raw  # noqa: E402

# The analyst's pipeline and column rule, imported unmodified.
sys.path.insert(0, str(ROOT / "part1_northline" / "starter"))
from analyst_model import NOT_FEATURES, analyst_pipeline  # noqa: E402

SEED = 0          # the analyst's random_state
N_SPLITS = 5      # the analyst's fold count

# ---------------------------------------------------------------------------
# Change 1: which columns exist at the moment of scoring.  One line per
# column in the file, decided from the data dictionary's timing note, kept
# and dropped alike.  "scoring moment" = the start of snapshot_month.
# ---------------------------------------------------------------------------
COLUMN_DECISIONS = [
    # column, decision, timing per dictionary, reason
    ("member_id", "id", "identifier",
     "not a feature; used to group rows by member"),
    ("snapshot_month", "id", "the month the row describes",
     "not a feature; April 2026 is a value never seen in training"),
    ("signup_month", "id", "month of first paid subscription",
     "not a feature; redundant with tenure_months"),
    ("acquisition_channel", "keep", "fixed at signup",
     "known before the month; also the segment for change 4"),
    ("plan_tier", "keep", "billing; no timing note",
     "read as the plan on the billing snapshot at the start of the month; "
     "a mid-month change would not be visible, which the dictionary does not rule out"),
    ("monthly_price", "keep", "list price of the plan; no timing note",
     "same reading as plan_tier; list price, not discounted"),
    ("city_tier", "keep", "self-reported at signup",
     "known before the month"),
    ("tenure_months", "keep", "as of the start of snapshot_month",
     "explicitly at the scoring moment"),
    ("sessions_last_30d", "keep", "30 days ending on the last day of the previous month",
     "window closes before the month starts"),
    ("app_opens_last_30d", "keep", "same 30-day window",
     "window closes before the month starts"),
    ("avg_session_minutes", "keep", "same 30-day window",
     "window closes before the month starts"),
    ("days_since_last_login", "keep", "to the last day of the previous month, capped at 90",
     "window closes before the month starts"),
    ("support_tickets_last_30d", "keep", "same 30-day window",
     "window closes before the month starts"),
    ("payment_failures_last_90d", "keep", "90 days ending on the last day of the previous month",
     "window closes before the month starts"),
    ("referrals_made", "keep", "same 30-day window",
     "window closes before the month starts"),
    ("winback_offer_sent", "drop", "contact about this month, from a list circulated after month close",
     "recorded after the month; on 1 April 2026 it is 0 for everyone"),
    ("exit_survey_started", "drop", "opened the cancellation exit survey; no window stated",
     "the cancellation flow itself; recorded during the month, not before it"),
    (TARGET, "target", "60 days from the end of snapshot_month",
     "the label"),
]
ADMISSIBLE = [c for c, d, _, _ in COLUMN_DECISIONS if d == "keep"]


def split_types(df: pd.DataFrame, features: list[str]) -> tuple[list[str], list[str]]:
    """Categorical / numeric split, exactly as the analyst does it: by dtype."""
    categorical = [c for c in features if not pd.api.types.is_numeric_dtype(df[c])]
    numeric = [c for c in features if c not in categorical]
    return categorical, numeric


def oof_auc(df: pd.DataFrame, features: list[str], folds, groups=None) -> float:
    """Out-of-fold AUC with the analyst's pipeline fitted inside each fold."""
    X, y = df[features], df[TARGET].to_numpy()
    categorical, numeric = split_types(df, features)
    oof = np.zeros(len(df))
    for train_idx, test_idx in folds.split(X, y, groups):
        model = analyst_pipeline(categorical, numeric)
        model.fit(X.iloc[train_idx], y[train_idx])
        oof[test_idx] = model.predict_proba(X.iloc[test_idx])[:, 1]
    return roc_auc_score(y, oof)


def fit_once(fit: pd.DataFrame, features: list[str]):
    """Fit the analyst's pipeline once on `fit` and return it."""
    categorical, numeric = split_types(fit, features)
    model = analyst_pipeline(categorical, numeric)
    model.fit(fit[features], fit[TARGET].to_numpy())
    return model


def odds_ratios(model, fit: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    """Coefficients of the fitted logistic regression as odds ratios.

    Numeric columns were standardised inside the pipeline, so their
    coefficient is per one standard deviation of the building data; the
    per-unit version divides by that standard deviation.  One-hot columns
    are relative to the dropped first category of each categorical.
    """
    prep = model.named_steps["prep"]
    names = prep.get_feature_names_out()
    coef = model.named_steps["est"].coef_[0]
    scale = dict(zip(prep.named_transformers_["num"].feature_names_in_,
                     prep.named_transformers_["num"].scale_))
    rows = []
    for name, b in zip(names, coef):
        kind, col = name.split("__", 1)
        if kind == "num":
            rows.append({"feature": col, "type": "numeric (per 1 SD)",
                         "sd_in_building_data": round(scale[col], 4),
                         "coef": round(b, 4), "odds_ratio_per_sd": round(np.exp(b), 4),
                         "odds_ratio_per_unit": round(np.exp(b / scale[col]), 4)})
        else:
            rows.append({"feature": col, "type": "one-hot vs dropped first category",
                         "sd_in_building_data": np.nan,
                         "coef": round(b, 4), "odds_ratio_per_sd": round(np.exp(b), 4),
                         "odds_ratio_per_unit": np.nan})
    dropped = {c: cats[0] for c, cats in
               zip(prep.named_transformers_["cat"].feature_names_in_,
                   prep.named_transformers_["cat"].categories_)}
    out = pd.DataFrame(rows)
    out["baseline_category"] = out["feature"].map(
        lambda f: next((f"{c}={v}" for c, v in dropped.items() if f.startswith(c + "_")), ""))
    out["abs_coef"] = out["coef"].abs()
    return out.sort_values("abs_coef", ascending=False).drop(columns="abs_coef").reset_index(drop=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- harness check: the analyst's protocol on the raw file -------------
    raw = load_raw()
    raw_features = [c for c in raw.columns if c not in NOT_FEATURES]
    check = oof_auc(raw, raw_features, StratifiedKFold(N_SPLITS, shuffle=True, random_state=SEED))
    print(f"harness check: analyst's protocol on raw file, all months  AUC {check:.3f}  "
          f"(analyst_model.py prints 0.967; this is not an exhibit row)")
    print()

    # ---- data ----------------------------------------------------------------
    df, _ = load_clean()
    build = df[df["month"] <= TRAIN_END].reset_index(drop=True)
    test = df[df["month"] >= TEST_START].reset_index(drop=True)
    all_features = [c for c in df.columns if c not in NOT_FEATURES + ("month", "year")]
    assert len(all_features) == 14, all_features
    assert len(ADMISSIBLE) == 12, ADMISSIBLE
    assert set(ADMISSIBLE) <= set(all_features)

    pd.DataFrame(COLUMN_DECISIONS,
                 columns=["column", "decision", "timing_per_dictionary", "reason"]) \
      .to_csv(OUT / "a2_columns.csv", index=False)

    n_build, k_build = len(build), int(build[TARGET].sum())
    n_test, k_test = len(test), int(test[TARGET].sum())
    print(f"building window (<= {TRAIN_END}): {n_build:,} rows, {k_build:,} churners, "
          f"{build['member_id'].nunique():,} members")
    print(f"test window     (>= {TEST_START}): {n_test:,} rows, {k_test:,} churners, "
          f"{test['member_id'].nunique():,} members")
    print()

    rows = []

    def add(row, change, features, protocol, n_fit, n_scored, k_scored, auc, kind):
        rows.append({"row": row, "change": change, "n_features": len(features),
                     "protocol": protocol, "rows_fit": n_fit, "rows_scored": n_scored,
                     "churners_scored": k_scored, "auc": round(auc, 4), "kind": kind})
        print(f"row {row}  {change:<40s} AUC {auc:.4f}   [{kind}]")

    # ---- row 0: analyst's protocol, deduplicated, building window ------------
    skf = StratifiedKFold(N_SPLITS, shuffle=True, random_state=SEED)
    auc0 = oof_auc(build, all_features, skf)
    add(0, "analyst's protocol, deduplicated", all_features,
        "5-fold stratified CV, shuffled", n_build, n_build, k_build, auc0, "cross-validated")

    # ---- row 1: admissible columns only ---------------------------------------
    auc1 = oof_auc(build, ADMISSIBLE, skf)
    add(1, "+ admissible columns only", ADMISSIBLE,
        "5-fold stratified CV, shuffled", n_build, n_build, k_build, auc1, "cross-validated")

    # ---- row 2: one member, not many rows -------------------------------------
    # First, how much member overlap the analyst's split actually has, so the
    # size of change 2's effect can be read against the size of the problem.
    fold_of_row = np.zeros(n_build, dtype=int)
    for k, (_, held) in enumerate(skf.split(build[ADMISSIBLE], build[TARGET])):
        fold_of_row[held] = k
    folds_per_member = pd.Series(fold_of_row).groupby(build["member_id"].to_numpy()).nunique()
    overlap = pd.DataFrame([{
        "members_in_building_window": int(len(folds_per_member)),
        "members_with_rows_in_2_or_more_folds": int((folds_per_member > 1).sum()),
        "share": round(float((folds_per_member > 1).mean()), 4),
        "members_with_one_row": int((build.groupby("member_id").size() == 1).sum()),
    }])
    overlap.to_csv(OUT / "a2_fold_overlap.csv", index=False)
    print(f"member overlap under the analyst's random split: "
          f"{overlap.members_with_rows_in_2_or_more_folds[0]:,} of "
          f"{overlap.members_in_building_window[0]:,} members "
          f"({overlap.share[0]:.1%}) have rows in 2+ folds; change 2 removes all of it")

    sgkf = StratifiedGroupKFold(N_SPLITS, shuffle=True, random_state=SEED)
    auc2 = oof_auc(build, ADMISSIBLE, sgkf, groups=build["member_id"].to_numpy())
    add(2, "+ one member never in both folds", ADMISSIBLE,
        "5-fold stratified CV grouped by member_id", n_build, n_build, k_build, auc2,
        "cross-validated")

    # ---- row 3: past to future ------------------------------------------------
    model3 = fit_once(build, ADMISSIBLE)
    p_test = model3.predict_proba(test[ADMISSIBLE])[:, 1]
    auc3 = roc_auc_score(test[TARGET], p_test)
    add(3, "+ past to future", ADMISSIBLE,
        f"fit on months <= {TRAIN_END}, scored on months >= {TEST_START}",
        n_build, n_test, k_test, auc3, "test-window")

    # Save the test-window scores.  A3 reads these; nothing rescores the test set.
    scores = test[["member_id", "month", "acquisition_channel", TARGET]].copy()
    scores["segment"] = np.where(scores["acquisition_channel"].eq("corporate"),
                                 "corporate", "other")
    scores["p_churn"] = p_test
    scores.to_csv(OUT / "a2_test_scores.csv", index=False)

    # ---- row 4: by segment ----------------------------------------------------
    for seg in ("corporate", "other"):
        m = scores["segment"].eq(seg).to_numpy()
        k = int(scores.loc[m, TARGET].sum())
        auc4 = (roc_auc_score(scores.loc[m, TARGET], p_test[m])
                if 0 < k < m.sum() else float("nan"))
        add(4, f"+ by segment: {seg}", ADMISSIBLE,
            "row-3 scores, split by acquisition_channel", n_build, int(m.sum()), k, auc4,
            "test-window")

    table = pd.DataFrame(rows)
    table.to_csv(OUT / "a2_table.csv", index=False)

    # Diagnostic: what the row-3 model learned.  Building window only.
    ors = odds_ratios(model3, build, ADMISSIBLE)
    ors.to_csv(OUT / "a2_odds_ratios.csv", index=False)
    print()
    print("A2 exhibit")
    print(table.drop(columns=["protocol"]).to_string(index=False))
    print()
    print("test-window rows and churners by month and segment")
    print(scores.groupby(["month", "segment"])[TARGET]
                .agg(rows="size", churners="sum").to_string())
    print()
    print("row-3 model coefficients as odds ratios (diagnostic, building window only)")
    print(ors.to_string(index=False))
    print()
    print(f"wrote {OUT / 'a2_table.csv'}, a2_columns.csv, a2_test_scores.csv, "
          f"a2_fold_overlap.csv, a2_odds_ratios.csv")


if __name__ == "__main__":
    main()
