"""
A1 -- baselines before any modelling.  Northline Fitness churn.

What this produces, all written to analysis/outputs/:

    a1_baselines.csv            the A1 exhibit: base rate, trivial-rule
                                accuracy, single-variable AUCs, analyst's AUC
    a1_base_rate_by_year.csv    diagnostic: does the base rate move over time?
    a1_base_rate_by_month.csv   same, monthly
    a1_cleaning.txt             what dedup removed, and the uniqueness check

Cleaning done here, and nothing else: normalise snapshot_month with the
supplied month_key(), then drop exact duplicate rows (ticket NLF-2231).  No
column is dropped -- that is A2 change 1, and A1 comes before it.

Single-variable rules need no fitting, so there is no cross-validation and
no randomness in this script.  The direction of each rule is fixed below
from what the column means, before the number is seen, and is not flipped
afterwards.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "analysis" / "outputs"

# Use the supplied loader rather than reimplementing it.
sys.path.insert(0, str(ROOT / "part1_northline" / "starter"))
from load import TARGET, load_raw, month_key  # noqa: E402

ANALYST_OUTPUT = OUT / "analyst_model_output.txt"
ANALYST_QUOTED_AUC = 0.967   # the figure in the brief, used only as a label

# Single-variable rules.  sign=+1 means "higher value -> more likely to
# churn"; sign=-1 means the opposite.  Chosen from the column definitions in
# the data dictionary, not from the data.
SINGLE_VARIABLE_RULES = {
    "days_since_last_login": (+1, "longer since last login -> more likely to churn"),
    "tenure_months":         (-1, "shorter tenure -> more likely to churn"),
    "app_opens_last_30d":    (-1, "fewer app opens -> more likely to churn"),
    "avg_session_minutes":   (-1, "shorter sessions -> more likely to churn"),
}

# Two columns the dictionary's timing notes say are recorded during or after
# the month being scored.  Diagnostic only: how do they sit against the label?
POST_SCORING_COLUMNS = ["exit_survey_started", "winback_offer_sent"]


def column_timing(df: pd.DataFrame) -> pd.DataFrame:
    """For each post-scoring column: how a 1 in it lines up with the label."""
    y = df[TARGET]
    is_last = df.index.isin(df.groupby("member_id").tail(1).index)
    rows = []
    for col in POST_SCORING_COLUMNS:
        one = df[col].eq(1)
        rows.append({
            "column": col,
            "rows_with_1": int(one.sum()),
            "share_of_rows_with_1": round(one.mean(), 4),
            "churners_among_1s": int(y[one].sum()),
            "non_churners_among_1s": int((1 - y[one]).sum()),
            "p_churn_given_1": round(y[one].mean(), 4),
            "p_churn_given_0": round(y[~one].mean(), 4),
            "share_of_churners_with_1": round(y[one].sum() / y.sum(), 4),
            "ones_on_members_last_row": int((one & is_last).sum()),
            "auc_alone": round(roc_auc_score(y, df[col]), 4),
        })
    return pd.DataFrame(rows)


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Normalise the month, drop exact duplicates, and record what happened."""
    notes = []
    df = df.copy()
    df["month"] = df["snapshot_month"].map(month_key)
    df["year"] = df["month"].str[:4]

    before = len(df)
    dup_mask = df.duplicated(keep="first")
    dup_months = df.loc[dup_mask, "month"].value_counts().sort_index()
    df = df.loc[~dup_mask].reset_index(drop=True)
    notes.append(f"rows as delivered           {before:,}")
    notes.append(f"exact duplicate rows removed {int(dup_mask.sum()):,}")
    notes.append(f"rows after dedup             {len(df):,}")
    notes.append("duplicates by month: " +
                 ", ".join(f"{m}={n:,}" for m, n in dup_months.items()))

    # After removing exact duplicates, one row per member per month is what
    # the dictionary promises.  Check it rather than assume it.
    remaining = df.duplicated(subset=["member_id", "month"]).sum()
    notes.append(f"(member_id, month) pairs still duplicated after dedup: {remaining:,}")
    if remaining:
        raise RuntimeError("non-identical duplicate member-months remain; inspect before continuing")

    notes.append(f"unique members               {df['member_id'].nunique():,}")
    notes.append(f"months covered               {df['month'].min()} -> {df['month'].max()} "
                 f"({df['month'].nunique()} months)")

    # How the label sits within a member's history.  The dictionary defines it
    # as a 60-day forward window, which could flag more than one row per
    # churner; record what the extract actually does.
    df = df.sort_values(["member_id", "month"]).reset_index(drop=True)
    flags_per_member = df.groupby("member_id")[TARGET].sum()
    last_rows = df.groupby("member_id").tail(1)
    notes.append(f"churners (members with >=1 flagged row)      {int((flags_per_member > 0).sum()):,}")
    notes.append(f"churners with more than one flagged row      {int((flags_per_member > 1).sum()):,}")
    notes.append(f"flagged rows that are the member's last row  {int(last_rows[TARGET].sum()):,} "
                 f"of {int(df[TARGET].sum()):,}")
    return df, notes


def analyst_auc() -> float | None:
    """Read the AUC the analyst's script printed, if run.sh has captured it."""
    if not ANALYST_OUTPUT.exists():
        return None
    m = re.search(r"cross-validated AUC\s+([0-9.]+)", ANALYST_OUTPUT.read_text())
    return float(m.group(1)) if m else None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df, notes = clean(load_raw())
    (OUT / "a1_cleaning.txt").write_text("\n".join(notes) + "\n")
    print("\n".join(notes))
    print()

    y = df[TARGET].to_numpy()
    n_rows, n_pos = len(y), int(y.sum())

    # 1. Base rate.  Row-level is the unit the analyst's model and the monthly
    #    programme use.  Member-level is context: a member who ever churns.
    base_rate_rows = y.mean()
    base_rate_members = df.groupby("member_id")[TARGET].max().mean()

    # 2. The trivial rule: predict "no churn" for everyone.
    trivial_acc = accuracy_score(y, np.zeros_like(y))

    # 3. Single-variable rules, scored on all deduped rows.  No fitting.
    rule_rows = []
    for col, (sign, meaning) in SINGLE_VARIABLE_RULES.items():
        auc = roc_auc_score(y, sign * df[col].to_numpy())
        rule_rows.append((col, sign, meaning, auc))

    # 4. The analyst's headline, as their script printed it.
    a_auc = analyst_auc()

    table = [
        {"quantity": "base rate of churn_next_60d (rows)",
         "value": round(base_rate_rows, 4),
         "n": n_rows, "positives": n_pos,
         "note": "deduped member-months; unit matches the analyst's model"},
        {"quantity": "base rate (members ever churning)",
         "value": round(base_rate_members, 4),
         "n": df["member_id"].nunique(),
         "positives": int(df.groupby("member_id")[TARGET].max().sum()),
         "note": "context only; different unit"},
        {"quantity": "accuracy of predicting 'no churn' for everyone",
         "value": round(trivial_acc, 4), "n": n_rows, "positives": n_pos,
         "note": "= 1 - base rate; no information used"},
    ]
    for col, sign, meaning, auc in rule_rows:
        table.append({"quantity": f"AUC, single-variable rule: {col}",
                      "value": round(auc, 4), "n": n_rows, "positives": n_pos,
                      "note": f"{meaning}; all deduped rows, no fitting"})
    table.append({"quantity": "analyst's 5-fold CV AUC (all columns, raw rows)",
                  "value": a_auc if a_auc is not None else "not run",
                  "n": "33,340 raw rows", "positives": "",
                  "note": f"as printed by starter/analyst_model.py; brief quotes {ANALYST_QUOTED_AUC}"})
    exhibit = pd.DataFrame(table)
    exhibit.to_csv(OUT / "a1_baselines.csv", index=False)

    # Diagnostic: base rate over time.  Not an A1 deliverable; evidence for the
    # paragraph on whether a pooled 2024-2025 number speaks to April 2026.
    df["corporate"] = df["acquisition_channel"].eq("corporate")
    agg = dict(rows=(TARGET, "size"), churners=(TARGET, "sum"),
               base_rate=(TARGET, "mean"), corporate_share=("corporate", "mean"))
    by_year = df.groupby("year").agg(**agg).reset_index()
    by_month = df.groupby("month").agg(**agg).reset_index()
    by_year.to_csv(OUT / "a1_base_rate_by_year.csv", index=False)
    by_month.to_csv(OUT / "a1_base_rate_by_month.csv", index=False)

    # Diagnostic: the two columns the dictionary dates after the scoring moment.
    timing = column_timing(df)
    timing.to_csv(OUT / "a1_column_timing.csv", index=False)

    print("A1 exhibit")
    print(exhibit.to_string(index=False))
    print()
    print("base rate by year (diagnostic)")
    print(by_year.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print()
    print("base rate by month, last six (diagnostic)")
    print(by_month.tail(6).to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print()
    print("post-scoring columns against the label (diagnostic)")
    print(timing.T.to_string(header=False))
    print()
    print(f"wrote {OUT / 'a1_baselines.csv'}, a1_base_rate_by_year.csv, "
          f"a1_base_rate_by_month.csv, a1_column_timing.csv, a1_cleaning.txt")


if __name__ == "__main__":
    main()
