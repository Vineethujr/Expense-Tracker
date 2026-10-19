"""
Unit Tests for Analytics, KPIs, and Trend Calculations.
"""

import pytest
import pandas as pd
from src.analytics.aggregations import calculate_kpis, calculate_category_summary
from src.analytics.trend_analysis import calculate_monthly_trends, calculate_daily_trends
from src.analytics.spending_patterns import analyze_spending_patterns


def test_calculate_kpis_empty():
    """Empty DataFrame should return safe zeroed KPIs without throwing errors."""
    empty_df = pd.DataFrame()
    kpis = calculate_kpis(empty_df)
    assert kpis["total_expenses"] == 0.0
    assert kpis["transaction_count"] == 0
    assert kpis["avg_transaction_amount"] == 0.0
    assert kpis["highest_category"] == "N/A"


def test_calculate_kpis_exact_values(sample_test_data):
    """Verify KPIs against known mathematical ground truth."""
    df = pd.DataFrame(sample_test_data)
    kpis = calculate_kpis(df, current_month="2026-10")

    assert kpis["total_expenses"] == 53700.0
    assert kpis["transaction_count"] == 9
    assert round(kpis["avg_transaction_amount"], 2) == round(53700.0 / 9, 2)
    assert kpis["highest_category"] == "Housing & Rent"
    assert kpis["highest_category_amount"] == 40000.0

    # Essential: Rent (40000) + Groceries (3500) + Utilities (5000) = 48500
    assert kpis["essential_spend"] == 48500.0
    # Discretionary: Dining (2200) + Shopping (3000) = 5200
    assert kpis["discretionary_spend"] == 5200.0

    assert round(kpis["essential_pct"] + kpis["discretionary_pct"], 1) == 100.0


def test_calculate_category_summary(sample_test_data):
    """Test category breakdown aggregations."""
    df = pd.DataFrame(sample_test_data)
    cat_df = calculate_category_summary(df)

    assert len(cat_df) == 5
    # Category totals check
    cat_map = cat_df.set_index("category")["total_spend"].to_dict()
    assert cat_map["Housing & Rent"] == 40000.0
    assert cat_map["Utilities & Bills"] == 5000.0
    assert cat_map["Food & Groceries"] == 3500.0
    assert cat_map["Shopping & Retail"] == 3000.0
    assert cat_map["Dining & Takeout"] == 2200.0

    # Percentages must sum to 100%
    assert round(cat_df["percentage"].sum(), 1) == 100.0


def test_calculate_monthly_trends(sample_test_data):
    """
    Test Month-over-Month calculation.
    Sep: 20000 + 2000 + 2500 + 1000 + 3000 = 28,500
    Oct: 20000 + 1500 + 2500 + 1200 = 25,200
    Diff: -3,300
    Growth: -3300 / 28500 = -11.58%
    """
    df = pd.DataFrame(sample_test_data)
    monthly_df = calculate_monthly_trends(df)

    assert len(monthly_df) == 2
    assert monthly_df.iloc[0]["month"] == "2026-09"
    assert monthly_df.iloc[0]["total_spend"] == 28500.0
    assert pd.isna(monthly_df.iloc[0]["mom_growth_pct"])  # First month has no previous month

    assert monthly_df.iloc[1]["month"] == "2026-10"
    assert monthly_df.iloc[1]["total_spend"] == 25200.0
    assert monthly_df.iloc[1]["mom_change_amt"] == -3300.0
    assert round(monthly_df.iloc[1]["mom_growth_pct"], 2) == -11.58


def test_calculate_daily_trends(sample_test_data):
    """Test daily rolling average calculation."""
    df = pd.DataFrame(sample_test_data)
    daily_df = calculate_daily_trends(df)

    assert not daily_df.empty
    assert "rolling_7d_avg" in daily_df.columns
    assert daily_df["rolling_7d_avg"].notna().all()


def test_analyze_spending_patterns(sample_test_data):
    """Test behavioral spending pattern extraction."""
    df = pd.DataFrame(sample_test_data)
    patterns = analyze_spending_patterns(df)

    assert patterns["essential_total"] == 48500.0
    assert patterns["discretionary_total"] == 5200.0
    assert len(patterns["top_transactions"]) == 5
    # Largest transaction is Rent (20,000)
    assert patterns["top_transactions"][0]["amount"] == 20000.0
