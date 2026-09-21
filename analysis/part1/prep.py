"""
Shared cleaning for Part A.  Every Part A script loads the data through
load_clean() so A1, A2 and A3 all see the same rows.

What load_clean() does, and nothing more:

    1. month = month_key(snapshot_month)   the supplied normaliser (NLF-2198)
    2. drop exact duplicate rows            the re-run March 2025 load (NLF-2231)
    3. check one row per (member_id, month) remains, and raise if not
    4. sort by member_id, month

No column is dropped and no value is changed.  Which columns are admissible
is an A2 decision and lives in the A2 script, not here.

The supplied data file is read in place and never written.
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "part1_northline" / "starter"))
from load import (TARGET, TRAIN_END, VALID_MONTH, TEST_START,  # noqa: E402,F401
                  OFFER_COST, MEMBER_LTV, OFFER_CONVERSION,
                  load_raw, month_key, offer_value)


def load_clean() -> tuple[pd.DataFrame, list[str]]:
    """Cleaned member-months and a log of what the cleaning did."""
    df = load_raw().copy()
    notes = []
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


if __name__ == "__main__":
    _, notes = load_clean()
    print("\n".join(notes))
