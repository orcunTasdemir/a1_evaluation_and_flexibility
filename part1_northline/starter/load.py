"""
Assignment 1 starter.  Northline Fitness churn.

This file exists so you do not have to retype boilerplate.  It deliberately
does NOT clean the data, choose features, or drop any column.  Every one of
those is a decision you are being graded on.

The evaluation windows below are the ones the brief tells you to use.  They
are here so your A3 numbers are comparable to everyone else's -- you are
graded on explaining why this shape is right, not on inventing the boundaries.

Usage:
    from load import load_raw, month_key, TRAIN_END, VALID_MONTH, TEST_START
    df = load_raw()
    df["month"] = df["snapshot_month"].map(month_key)
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data" / "member_months.csv"

# The economics from the assignment brief.
OFFER_COST = 18.0        # cost of extending one retention offer, USD
MEMBER_LTV = 240.0       # value of a member who stays, USD
OFFER_CONVERSION = 0.35  # fraction of would-be churners retained by the offer

TARGET = "churn_next_60d"

# The evaluation windows from the brief, as 'YYYY-MM' strings.
# Training  : months <= TRAIN_END
# Not used  : 2025-07, 2025-08   (labels for the last training month mature at
#                                 the end of August 2025)
# Validation: month == VALID_MONTH
# Test      : months >= TEST_START   -- touch this once, at the end
TRAIN_END = "2025-06"
VALID_MONTH = "2025-09"
TEST_START = "2025-10"


def load_raw() -> pd.DataFrame:
    """Read the extract exactly as delivered.  No cleaning."""
    return pd.read_csv(DATA)


def month_key(value: str) -> str:
    """Normalise the three `snapshot_month` formats to 'YYYY-MM'.

    You still have to decide whether and how to use the month.  This just
    stops the three formats from silently becoming three different categories.
    """
    s = str(value).strip()
    if "/" in s:                      # 'MM/YYYY'
        month, year = s.split("/")
        return f"{year}-{int(month):02d}"
    return s[:7]                      # 'YYYY-MM' or 'YYYY-MM-DD'


def offer_value(churned: int, offered: int) -> float:
    """Realised dollar value of one targeting decision, per the brief."""
    if not offered:
        return 0.0
    return MEMBER_LTV * OFFER_CONVERSION - OFFER_COST if churned else -OFFER_COST


if __name__ == "__main__":
    df = load_raw()
    df["month"] = df["snapshot_month"].map(month_key)
    print(f"rows                {len(df):,}")
    print(f"unique member_id    {df['member_id'].nunique():,}")
    print(f"columns             {len(df.columns) - 1}")
    print(f"target base rate    {df[TARGET].mean():.4f}")
    print()
    print("months present:")
    print(sorted(df["month"].unique()))
    print()
    print(f"rows in training window (<= {TRAIN_END}) : "
          f"{(df['month'] <= TRAIN_END).sum():,}")
    print(f"rows in validation window ({VALID_MONTH})  : "
          f"{(df['month'] == VALID_MONTH).sum():,}")
    print(f"rows in test window (>= {TEST_START})     : "
          f"{(df['month'] >= TEST_START).sum():,}")
