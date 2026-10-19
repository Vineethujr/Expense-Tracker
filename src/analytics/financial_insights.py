"""
Rule-Based Financial Insights Engine.
Evaluates deterministic financial heuristics and rules to generate actionable,
student-friendly guidance on budget compliance, spending anomalies, and savings opportunities.
"""

import pandas as pd
import numpy as np
from datetime import date
from typing import List, Dict, Any, Optional
from src.utils.formatters import format_currency, format_percentage
from src.config import ESSENTIAL_CATEGORIES, DISCRETIONARY_CATEGORIES


def generate_rule_based_insights(
    df: pd.DataFrame,
    budget_status: Optional[Dict[str, Any]] = None,
    current_month: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Evaluates spending data against rule-based heuristic criteria.
    Returns a list of structured insight cards:
    [
        {
            "severity": "critical" | "warning" | "info" | "success",
            "title": str,
            "message": str,
            "actionable_tip": str
        }
    ]
    """
    insights: List[Dict[str, Any]] = []

    if df.empty or len(df) < 2:
        insights.append({
            "severity": "info",
            "title": "Insufficient Data for In-Depth Analytics",
            "message": "Only a limited number of transactions have been recorded. Add more expenses or load the sample synthetic dataset to unlock trend predictions and pattern insights.",
            "actionable_tip": "Tip: Log at least 15 to 20 transactions across 2 different months to enable full Month-over-Month comparisons."
        })
        return insights

    working_df = df.copy()
    working_df["amount"] = pd.to_numeric(working_df["amount"], errors="coerce").fillna(0.0)
    working_df["date_str"] = working_df["date"].astype(str).str[:10]
    total_spend = working_df["amount"].sum()

    target_month = current_month or date.today().strftime("%Y-%m")

    # RULE 1: Overall Budget Compliance
    if budget_status and budget_status.get("has_budgets", False):
        overall_status = budget_status.get("overall_status")
        overall_allocated = budget_status.get("overall_allocated", 0.0)
        overall_spent = budget_status.get("total_spent", 0.0)
        util_pct = budget_status.get("overall_utilization_pct", 0.0)

        if overall_status == "exceeded":
            overspend_amt = overall_spent - overall_allocated
            insights.append({
                "severity": "critical",
                "title": f"🚨 Monthly Budget Exceeded ({format_percentage(util_pct)})",
                "message": f"You have spent {format_currency(overall_spent)} against an allocated budget of {format_currency(overall_allocated)}. You are over budget by {format_currency(overspend_amt)}.",
                "actionable_tip": "Review your discretionary expenses (shopping, dining, entertainment) to halt non-essential outflows for the remainder of this month."
            })
        elif overall_status == "warning":
            remaining_amt = overall_allocated - overall_spent
            insights.append({
                "severity": "warning",
                "title": f"⚠️ Budget Alert: 80% Threshold Reached ({format_percentage(util_pct)})",
                "message": f"You have utilized {format_percentage(util_pct)} of your total monthly budget. Only {format_currency(remaining_amt)} remains.",
                "actionable_tip": "Slow down optional spending to ensure you do not breach your monthly limit before month-end."
            })
        elif overall_status == "normal" and overall_allocated > 0:
            remaining_amt = overall_allocated - overall_spent
            insights.append({
                "severity": "success",
                "title": f"✅ Healthy Budget Utilization ({format_percentage(util_pct)})",
                "message": f"Great financial discipline! You have spent {format_currency(overall_spent)} of {format_currency(overall_allocated)} with {format_currency(remaining_amt)} remaining.",
                "actionable_tip": "Keep up this run rate. The remaining surplus can be redirected into your emergency fund or investments."
            })

        # Category Budget Alerts
        category_budgets = budget_status.get("category_budgets", [])
        for cb in category_budgets:
            if cb["status"] == "exceeded":
                insights.append({
                    "severity": "critical",
                    "title": f"🚨 Category Overspend: {cb['category']}",
                    "message": f"Spending on '{cb['category']}' ({format_currency(cb['spent'])}) has exceeded its allocated limit of {format_currency(cb['allocated'])} by {format_currency(cb['spent'] - cb['allocated'])}.",
                    "actionable_tip": f"Audit recent transactions under '{cb['category']}' to identify unusually high charges."
                })

    # RULE 2: Category Dominance (Single category > 45% of total spend)
    cat_totals = working_df.groupby("category")["amount"].sum()
    if not cat_totals.empty:
        top_cat = cat_totals.idxmax()
        top_amt = cat_totals.max()
        top_share = (top_amt / total_spend) * 100.0

        if top_share >= 45.0 and top_cat not in ["Housing & Rent"]:
            insights.append({
                "severity": "warning",
                "title": f"📊 High Concentration in {top_cat} ({format_percentage(top_share)})",
                "message": f"'{top_cat}' accounts for {format_percentage(top_share)} of your total logged expenditures ({format_currency(top_amt)}).",
                "actionable_tip": f"Explore whether recurring costs in {top_cat} can be optimized or reduced."
            })
        else:
            insights.append({
                "severity": "info",
                "title": f"🏷️ Top Spending Category: {top_cat}",
                "message": f"Your largest outflow category is '{top_cat}', representing {format_currency(top_amt)} ({format_percentage(top_share)} of total spend).",
                "actionable_tip": "Tracking your largest expense category is the most effective lever for improving monthly savings."
            })

    # RULE 3: Essential vs Discretionary Ratio (50-30-20 Rule Check)
    essential_mask = working_df["category"].isin(ESSENTIAL_CATEGORIES)
    discretionary_spend = working_df[~essential_mask]["amount"].sum()
    discretionary_pct = (discretionary_spend / total_spend * 100.0) if total_spend > 0 else 0.0

    if discretionary_pct > 40.0:
        insights.append({
            "severity": "warning",
            "title": f"🛍️ Elevated Discretionary Spending ({format_percentage(discretionary_pct)})",
            "message": f"Lifestyle and non-essential expenses (Shopping, Dining, Leisure) account for {format_percentage(discretionary_pct)} of your total outflow. The standard 50/30/20 benchmark recommends capping wants at 30%.",
            "actionable_tip": "Try enforcing a '48-hour delay rule' on non-essential online shopping and restaurant orders."
        })

    # RULE 4: Spending Anomaly / Spike Detection (Daily spend > Mean + 2*StdDev)
    daily_spend = working_df.groupby("date_str")["amount"].sum()
    if len(daily_spend) >= 7:
        mean_daily = daily_spend.mean()
        std_daily = daily_spend.std()
        spike_threshold = mean_daily + (2.0 * std_daily)
        spikes = daily_spend[daily_spend > spike_threshold]

        if not spikes.empty:
            spike_date = spikes.index[-1]
            spike_amt = spikes.iloc[-1]
            insights.append({
                "severity": "warning",
                "title": f"⚡ Spending Spike Detected on {spike_date}",
                "message": f"Spending on {spike_date} reached {format_currency(spike_amt)}, which is more than 2 standard deviations above your daily average of {format_currency(mean_daily)}.",
                "actionable_tip": "Check if this spike was a planned one-off expense (e.g. annual insurance or appliance purchase) or an avoidable outflow."
            })

    # RULE 5: Month-over-Month (MoM) Growth or Savings
    working_df["month"] = working_df["date_str"].str[:7]
    monthly_series = working_df.groupby("month")["amount"].sum().sort_index()
    if len(monthly_series) >= 2:
        curr_m = monthly_series.index[-1]
        prev_m = monthly_series.index[-2]
        curr_amt = monthly_series.iloc[-1]
        prev_amt = monthly_series.iloc[-2]

        if prev_amt > 0:
            diff_amt = curr_amt - prev_amt
            pct_change = (diff_amt / prev_amt) * 100.0

            if pct_change >= 15.0:
                insights.append({
                    "severity": "warning",
                    "title": f"📈 Monthly Spending Increased by {format_percentage(pct_change)}",
                    "message": f"Your spending in {curr_m} ({format_currency(curr_amt)}) is higher than in {prev_m} ({format_currency(prev_amt)}) by {format_currency(diff_amt)}.",
                    "actionable_tip": "Compare category spending between these two months in the Spending Analytics tab to identify which category surged."
                })
            elif pct_change <= -10.0:
                insights.append({
                    "severity": "success",
                    "title": f"📉 Spending Reduced by {format_percentage(abs(pct_change))}",
                    "message": f"Congratulations! Your spending in {curr_m} ({format_currency(curr_amt)}) decreased by {format_currency(abs(diff_amt))} compared to {prev_m} ({format_currency(prev_amt)}).",
                    "actionable_tip": "Excellent budget control! Consider automating a transfer of the saved surplus directly into an investment fund."
                })

    return insights
