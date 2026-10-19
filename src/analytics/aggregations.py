"""
Analytics Aggregation Engine.
Derives dynamic KPIs, category summaries, and high-level financial metrics using Pandas.
"""

import pandas as pd
import numpy as np
from datetime import date
from typing import Dict, Any
from src.config import ESSENTIAL_CATEGORIES, DISCRETIONARY_CATEGORIES


def calculate_kpis(df: pd.DataFrame, current_month: str = None) -> Dict[str, Any]:
    """
    Computes summary KPIs from an expenses DataFrame.
    Never hardcodes metrics. Handles empty DataFrames gracefully.
    """
    if df.empty:
        return {
            "total_expenses": 0.0,
            "current_month_spending": 0.0,
            "avg_transaction_amount": 0.0,
            "transaction_count": 0,
            "avg_daily_spending": 0.0,
            "highest_category": "N/A",
            "highest_category_amount": 0.0,
            "lowest_category": "N/A",
            "lowest_category_amount": 0.0,
            "essential_spend": 0.0,
            "discretionary_spend": 0.0,
            "essential_pct": 0.0,
            "discretionary_pct": 0.0,
        }

    # Ensure clean numeric amounts and dates
    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)
    working_df["date_str"] = working_df["date"].astype(str).str[:10]

    total_expenses = float(working_df["amount"].sum())
    transaction_count = int(len(working_df))
    avg_transaction = float(working_df["amount"].mean()) if transaction_count > 0 else 0.0

    # Current month spending
    target_month = current_month or date.today().strftime("%Y-%m")
    current_month_df = working_df[working_df["date_str"].str.startswith(target_month)]
    current_month_spending = float(current_month_df["amount"].sum()) if not current_month_df.empty else 0.0

    # Daily average spend across active days in the dataset
    unique_days = working_df["date_str"].nunique()
    avg_daily_spending = float(total_expenses / unique_days) if unique_days > 0 else 0.0

    # Category summaries
    cat_grouped = working_df.groupby("category")["amount"].sum().sort_values(ascending=False)
    if not cat_grouped.empty:
        highest_category = str(cat_grouped.index[0])
        highest_category_amount = float(cat_grouped.iloc[0])
        lowest_category = str(cat_grouped.index[-1]) if len(cat_grouped) > 1 else highest_category
        lowest_category_amount = float(cat_grouped.iloc[-1]) if len(cat_grouped) > 1 else highest_category_amount
    else:
        highest_category = "N/A"
        highest_category_amount = 0.0
        lowest_category = "N/A"
        lowest_category_amount = 0.0

    # Essential vs Discretionary
    essential_mask = working_df["category"].isin(ESSENTIAL_CATEGORIES)
    essential_spend = float(working_df[essential_mask]["amount"].sum())
    discretionary_spend = float(working_df[~essential_mask]["amount"].sum())

    essential_pct = (essential_spend / total_expenses * 100.0) if total_expenses > 0 else 0.0
    discretionary_pct = (discretionary_spend / total_expenses * 100.0) if total_expenses > 0 else 0.0

    return {
        "total_expenses": total_expenses,
        "current_month_spending": current_month_spending,
        "avg_transaction_amount": avg_transaction,
        "transaction_count": transaction_count,
        "avg_daily_spending": avg_daily_spending,
        "highest_category": highest_category,
        "highest_category_amount": highest_category_amount,
        "lowest_category": lowest_category,
        "lowest_category_amount": lowest_category_amount,
        "essential_spend": essential_spend,
        "discretionary_spend": discretionary_spend,
        "essential_pct": essential_pct,
        "discretionary_pct": discretionary_pct,
    }


def calculate_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes total spend, percentage share, transaction count,
    and average ticket size for each category.
    """
    if df.empty:
        return pd.DataFrame(columns=[
            "category", "total_spend", "percentage", "transaction_count", "avg_spend", "max_spend"
        ])

    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)

    total_overall = working_df["amount"].sum()

    grouped = working_df.groupby("category").agg(
        total_spend=("amount", "sum"),
        transaction_count=("amount", "count"),
        avg_spend=("amount", "mean"),
        max_spend=("amount", "max")
    ).reset_index()

    if total_overall > 0:
        grouped["percentage"] = (grouped["total_spend"] / total_overall) * 100.0
    else:
        grouped["percentage"] = 0.0

    grouped = grouped.sort_values(by="total_spend", ascending=False).reset_index(drop=True)
    return grouped
