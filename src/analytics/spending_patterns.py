"""
Spending Pattern Analysis Engine.
Analyzes frequent spending habits, essential vs discretionary ratios,
largest ticket items, payment method distribution, and day-of-week tendencies.
"""

import pandas as pd
from typing import Dict, Any, List
from src.config import ESSENTIAL_CATEGORIES, DISCRETIONARY_CATEGORIES


def analyze_spending_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Performs multidimensional spending pattern analysis.
    """
    if df.empty:
        return {
            "essential_total": 0.0,
            "discretionary_total": 0.0,
            "essential_pct": 0.0,
            "discretionary_pct": 0.0,
            "top_transactions": [],
            "payment_methods_summary": pd.DataFrame(),
            "day_of_week_summary": pd.DataFrame(),
            "frequent_categories": [],
            "avg_transaction": 0.0,
        }

    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)
    working_df["date_dt"] = pd.to_datetime(working_df["date"], errors="coerce")

    total_spend = working_df["amount"].sum()
    avg_transaction = float(working_df["amount"].mean())

    # 1. Essential vs Discretionary
    essential_mask = working_df["category"].isin(ESSENTIAL_CATEGORIES)
    essential_total = float(working_df[essential_mask]["amount"].sum())
    discretionary_total = float(working_df[~essential_mask]["amount"].sum())

    essential_pct = (essential_total / total_spend * 100.0) if total_spend > 0 else 0.0
    discretionary_pct = (discretionary_total / total_spend * 100.0) if total_spend > 0 else 0.0

    # 2. Top 5 Largest Transactions
    top_5_df = working_df.sort_values(by="amount", ascending=False).head(5)
    top_transactions: List[Dict[str, Any]] = []
    for _, r in top_5_df.iterrows():
        top_transactions.append({
            "id": r.get("id"),
            "date": str(r["date"])[:10],
            "category": str(r["category"]),
            "amount": float(r["amount"]),
            "payment_method": str(r["payment_method"]),
            "description": str(r.get("description", "")),
        })

    # 3. Payment Method Breakdown
    payment_methods_summary = working_df.groupby("payment_method").agg(
        total_spend=("amount", "sum"),
        transaction_count=("amount", "count")
    ).reset_index().sort_values("total_spend", ascending=False)
    if total_spend > 0:
        payment_methods_summary["percentage"] = (payment_methods_summary["total_spend"] / total_spend) * 100.0
    else:
        payment_methods_summary["percentage"] = 0.0

    # 4. Day of the Week Analysis (0=Monday, 6=Sunday)
    working_df["day_name"] = working_df["date_dt"].dt.day_name()
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_of_week_summary = working_df.groupby("day_name").agg(
        total_spend=("amount", "sum"),
        transaction_count=("amount", "count")
    ).reindex(day_order).fillna(0.0).reset_index()

    # 5. Frequent Categories (by transaction count)
    cat_counts = working_df["category"].value_counts().head(5).to_dict()
    frequent_categories = [{"category": k, "count": v} for k, v in cat_counts.items()]

    return {
        "essential_total": essential_total,
        "discretionary_total": discretionary_total,
        "essential_pct": essential_pct,
        "discretionary_pct": discretionary_pct,
        "top_transactions": top_transactions,
        "payment_methods_summary": payment_methods_summary,
        "day_of_week_summary": day_of_week_summary,
        "frequent_categories": frequent_categories,
        "avg_transaction": avg_transaction,
    }
