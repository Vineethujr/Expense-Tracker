"""
Unit Tests for Budget Service and Threshold Alert Calculations.
"""

import pytest
import pandas as pd
from src.services.budget_service import (
    set_budget, get_budgets_for_month, delete_budget, calculate_budget_status
)


def test_set_and_get_budget(temp_db):
    """Test allocating a monthly and category budget target."""
    assert set_budget("2026-10", "OVERALL", 45000.0, db_path=temp_db) is True
    assert set_budget("2026-10", "Food & Groceries", 8000.0, db_path=temp_db) is True

    b_df = get_budgets_for_month("2026-10", db_path=temp_db)
    assert len(b_df) == 2
    cats = list(b_df["category"])
    assert "OVERALL" in cats
    assert "Food & Groceries" in cats


def test_set_budget_invalid_category(temp_db):
    """Setting budget on unknown category raises ValueError."""
    with pytest.raises(ValueError):
        set_budget("2026-10", "Unapproved Category", 5000.0, db_path=temp_db)


def test_set_budget_invalid_amount(temp_db):
    """Setting budget <= 0 raises ValueError."""
    with pytest.raises(ValueError):
        set_budget("2026-10", "OVERALL", -100.0, db_path=temp_db)


def test_budget_utilization_thresholds(temp_db):
    """
    Test 3 tiered threshold states:
      1. Normal (< 80%)
      2. Warning (80% - 99.9%)
      3. Exceeded (>= 100%)
    """
    set_budget("2026-10", "OVERALL", 10000.0, db_path=temp_db)

    # Case 1: Spend 5000 (50% -> normal)
    df_normal = pd.DataFrame([{"date": "2026-10-05", "category": "Food & Groceries", "amount": 5000.0}])
    status_normal = calculate_budget_status("2026-10", expenses_df=df_normal, db_path=temp_db)
    assert status_normal["overall_status"] == "normal"
    assert status_normal["overall_utilization_pct"] == 50.0
    assert status_normal["overall_remaining"] == 5000.0

    # Case 2: Spend 8500 (85% -> warning)
    df_warning = pd.DataFrame([{"date": "2026-10-15", "category": "Food & Groceries", "amount": 8500.0}])
    status_warning = calculate_budget_status("2026-10", expenses_df=df_warning, db_path=temp_db)
    assert status_warning["overall_status"] == "warning"
    assert status_warning["overall_utilization_pct"] == 85.0
    assert status_warning["overall_remaining"] == 1500.0

    # Case 3: Spend 11500 (115% -> exceeded)
    df_exceeded = pd.DataFrame([{"date": "2026-10-25", "category": "Food & Groceries", "amount": 11500.0}])
    status_exceeded = calculate_budget_status("2026-10", expenses_df=df_exceeded, db_path=temp_db)
    assert status_exceeded["overall_status"] == "exceeded"
    assert status_exceeded["overall_utilization_pct"] == 115.0
    assert status_exceeded["overall_remaining"] == -1500.0


def test_delete_budget(temp_db):
    """Test removing a budget allocation."""
    set_budget("2026-10", "OVERALL", 25000.0, db_path=temp_db)
    b_df = get_budgets_for_month("2026-10", db_path=temp_db)
    b_id = int(b_df.iloc[0]["id"])

    assert delete_budget(b_id, db_path=temp_db) is True
    b_df_after = get_budgets_for_month("2026-10", db_path=temp_db)
    assert b_df_after.empty
