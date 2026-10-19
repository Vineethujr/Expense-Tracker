"""
Unit Tests for Expense Service CRUD and Filter Operations.
"""

import pytest
import pandas as pd
from src.services.expense_service import (
    add_expense, update_expense, delete_expense, get_expense_by_id,
    get_all_expenses, get_filtered_expenses, bulk_add_expenses,
    purge_synthetic_expenses, get_expenses_stats_count
)


def test_add_and_retrieve_expense(temp_db):
    """Test inserting a single expense and fetching it."""
    exp_id = add_expense(
        date="2026-10-15",
        category="Food & Groceries",
        amount=1450.50,
        payment_method="UPI",
        description="Supermarket trip",
        is_synthetic=0,
        db_path=temp_db
    )
    assert exp_id > 0

    record = get_expense_by_id(exp_id, db_path=temp_db)
    assert record is not None
    assert record["id"] == exp_id
    assert record["amount"] == 1450.50
    assert record["category"] == "Food & Groceries"
    assert record["payment_method"] == "UPI"
    assert record["description"] == "Supermarket trip"
    assert record["is_synthetic"] == 0


def test_update_expense(temp_db):
    """Test updating an existing expense."""
    exp_id = add_expense(
        date="2026-10-15",
        category="Food & Groceries",
        amount=1000.0,
        payment_method="Cash",
        db_path=temp_db
    )
    success = update_expense(
        expense_id=exp_id,
        date="2026-10-16",
        category="Dining & Takeout",
        amount=1200.0,
        payment_method="Credit Card",
        description="Dinner updated",
        db_path=temp_db
    )
    assert success is True

    record = get_expense_by_id(exp_id, db_path=temp_db)
    assert record["amount"] == 1200.0
    assert record["category"] == "Dining & Takeout"
    assert record["payment_method"] == "Credit Card"
    assert record["date"] == "2026-10-16"


def test_delete_expense(temp_db):
    """Test deleting an expense."""
    exp_id = add_expense(
        date="2026-10-15",
        category="Transportation",
        amount=350.0,
        payment_method="UPI",
        db_path=temp_db
    )
    assert delete_expense(exp_id, db_path=temp_db) is True
    assert get_expense_by_id(exp_id, db_path=temp_db) is None
    # Deleting non-existent ID returns False
    assert delete_expense(99999, db_path=temp_db) is False


def test_get_filtered_expenses(populated_temp_db):
    """Test filtering expenses by category, date range, and search."""
    # Filter by category
    groceries = get_filtered_expenses(categories=["Food & Groceries"], db_path=populated_temp_db)
    assert len(groceries) == 2

    # Filter by date range
    sep_expenses = get_filtered_expenses(start_date="2026-09-01", end_date="2026-09-30", db_path=populated_temp_db)
    assert len(sep_expenses) == 5

    # Filter by keyword
    rent_expenses = get_filtered_expenses(search_keyword="Rent", db_path=populated_temp_db)
    assert len(rent_expenses) == 2


def test_purge_synthetic_expenses(temp_db):
    """Test that purging synthetic expenses does not delete genuine user data."""
    # Add 1 user expense and 2 synthetic expenses
    add_expense("2026-10-10", "Utilities & Bills", 1500.0, "UPI", "User bill", is_synthetic=0, db_path=temp_db)
    add_expense("2026-10-11", "Food & Groceries", 500.0, "UPI", "Sample food 1", is_synthetic=1, db_path=temp_db)
    add_expense("2026-10-12", "Dining & Takeout", 800.0, "Credit Card", "Sample food 2", is_synthetic=1, db_path=temp_db)

    stats = get_expenses_stats_count(db_path=temp_db)
    assert stats["total"] == 3
    assert stats["user"] == 1
    assert stats["synthetic"] == 2

    deleted = purge_synthetic_expenses(db_path=temp_db)
    assert deleted == 2

    stats_after = get_expenses_stats_count(db_path=temp_db)
    assert stats_after["total"] == 1
    assert stats_after["user"] == 1
    assert stats_after["synthetic"] == 0


def test_persistence_after_connection_close(temp_db):
    """Verify data remains stored across independent connection cycles."""
    add_expense("2026-10-14", "Health & Medical", 450.0, "UPI", "Pharmacy", db_path=temp_db)
    all_df = get_all_expenses(db_path=temp_db)
    assert len(all_df) == 1
    assert all_df.iloc[0]["amount"] == 450.0
