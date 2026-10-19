"""
Trend Analysis Engine.
Calculates monthly spending progressions, Month-over-Month (MoM) variances,
daily trends with 7-day rolling averages, and category-level monthly breakdowns.
"""

import pandas as pd
import numpy as np


def calculate_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups expenses by month (YYYY-MM) and computes Month-over-Month (MoM)
    changes in absolute terms (₹) and percentage.
    Correctly handles edge cases (first month, zero spending).
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "month", "total_spend", "transaction_count", "avg_spend", "mom_change_amt", "mom_growth_pct"
        ])

    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)
    working_df["month"] = working_df["date"].astype(str).str[:7]

    monthly = working_df.groupby("month").agg(
        total_spend=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_spend=("amount", "mean")
    ).reset_index().sort_values("month").reset_index(drop=True)

    # Calculate Month-over-Month (MoM) differences
    monthly["mom_change_amt"] = monthly["total_spend"].diff()

    # Percentage change
    prev_spend = monthly["total_spend"].shift(1)
    mom_pct = []
    for curr, prev in zip(monthly["total_spend"], prev_spend):
        if pd.isna(prev) or prev == 0:
            mom_pct.append(None)
        else:
            pct = ((curr - prev) / prev) * 100.0
            mom_pct.append(round(pct, 2))

    monthly["mom_growth_pct"] = mom_pct
    return monthly


def calculate_daily_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups expenses by calendar day and computes a 7-day rolling average
    to smooth out spending volatility.
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "daily_spend", "transaction_count", "rolling_7d_avg"])

    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)
    working_df["date_str"] = working_df["date"].astype(str).str[:10]

    daily = working_df.groupby("date_str").agg(
        daily_spend=("amount", "sum"),
        transaction_count=("amount", "count")
    ).reset_index().rename(columns={"date_str": "date"}).sort_values("date").reset_index(drop=True)

    # 7-day rolling average
    daily["rolling_7d_avg"] = daily["daily_spend"].rolling(window=7, min_periods=1).mean().round(2)
    return daily


def calculate_category_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constructs a pivot table of Category vs Month for comparative spending matrix.
    """
    if df.empty:
        return pd.DataFrame()

    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)
    working_df["month"] = working_df["date"].astype(str).str[:7]

    pivot = working_df.pivot_table(
        index="category",
        columns="month",
        values="amount",
        aggfunc="sum",
        fill_value=0.0
    ).reset_index()

    return pivot
