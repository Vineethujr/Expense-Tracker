"""
Unit Tests for Rule-Based Financial Insights Engine.
"""

import pytest
import pandas as pd
from src.analytics.financial_insights import generate_rule_based_insights


def test_insights_insufficient_data():
    """An empty or 1-row DataFrame should yield an informative onboarding insight."""
    insights_empty = generate_rule_based_insights(pd.DataFrame())
    assert len(insights_empty) == 1
    assert insights_empty[0]["severity"] == "info"
    assert "Insufficient Data" in insights_empty[0]["title"]


def test_insights_budget_exceeded():
    """When budget is exceeded, a critical alert insight must be generated."""
    df = pd.DataFrame([
        {"date": "2026-10-05", "category": "Housing & Rent", "amount": 25000.0},
        {"date": "2026-10-10", "category": "Food & Groceries", "amount": 10000.0},
    ])
    budget_status = {
        "has_budgets": True,
        "overall_status": "exceeded",
        "overall_allocated": 30000.0,
        "total_spent": 35000.0,
        "overall_utilization_pct": 116.7,
        "category_budgets": []
    }
    insights = generate_rule_based_insights(df, budget_status=budget_status, current_month="2026-10")
    severities = [i["severity"] for i in insights]
    assert "critical" in severities
    assert any("Budget Exceeded" in i["title"] for i in insights)


def test_insights_high_discretionary():
    """If discretionary spending exceeds 40%, a warning insight must be triggered."""
    df = pd.DataFrame([
        {"date": "2026-10-05", "category": "Housing & Rent", "amount": 10000.0},   # Essential
        {"date": "2026-10-10", "category": "Shopping & Retail", "amount": 15000.0}, # Discretionary (60% of total)
    ])
    insights = generate_rule_based_insights(df, current_month="2026-10")
    assert any("Elevated Discretionary" in i["title"] for i in insights)
