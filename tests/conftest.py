"""
Pytest Fixtures and Test Setup.
Provides isolated temporary SQLite database fixtures and sample test data.
"""

import pytest
import tempfile
import os
import pandas as pd
from pathlib import Path
from src.database.schema import init_db
from src.services.expense_service import bulk_add_expenses


@pytest.fixture
def temp_db(tmp_path):
    """
    Creates an isolated temporary SQLite database for test execution.
    Guarantees user database is never touched.
    """
    db_file = tmp_path / "test_expenses.db"
    init_db(db_file)
    return str(db_file)


@pytest.fixture
def sample_test_data():
    """
    Returns a ground-truth dataset spanning two distinct months
    with known exact totals for mathematical verification.
    Total Spend:
      Food & Groceries: 2000 + 1500 = 3500
      Housing & Rent: 20000 + 20000 = 40000
      Utilities & Bills: 2500 + 2500 = 5000
      Dining & Takeout: 1000 + 1200 = 2200
      Shopping & Retail: 3000 + 0 = 3000
      Total: 53,700
    """
    return [
        # September 2026
        {"date": "2026-09-02", "category": "Housing & Rent", "amount": 20000.0, "payment_method": "Net Banking", "description": "Rent Sep", "is_synthetic": 0},
        {"date": "2026-09-05", "category": "Food & Groceries", "amount": 2000.0, "payment_method": "UPI", "description": "Groceries 1", "is_synthetic": 0},
        {"date": "2026-09-12", "category": "Utilities & Bills", "amount": 2500.0, "payment_method": "UPI", "description": "Electricity Sep", "is_synthetic": 0},
        {"date": "2026-09-15", "category": "Dining & Takeout", "amount": 1000.0, "payment_method": "Credit Card", "description": "Dinner Sep", "is_synthetic": 0},
        {"date": "2026-09-20", "category": "Shopping & Retail", "amount": 3000.0, "payment_method": "Credit Card", "description": "Clothes", "is_synthetic": 0},

        # October 2026
        {"date": "2026-10-02", "category": "Housing & Rent", "amount": 20000.0, "payment_method": "Net Banking", "description": "Rent Oct", "is_synthetic": 0},
        {"date": "2026-10-06", "category": "Food & Groceries", "amount": 1500.0, "payment_method": "UPI", "description": "Groceries Oct", "is_synthetic": 0},
        {"date": "2026-10-12", "category": "Utilities & Bills", "amount": 2500.0, "payment_method": "UPI", "description": "Electricity Oct", "is_synthetic": 0},
        {"date": "2026-10-18", "category": "Dining & Takeout", "amount": 1200.0, "payment_method": "Credit Card", "description": "Dinner Oct", "is_synthetic": 0},
    ]


@pytest.fixture
def populated_temp_db(temp_db, sample_test_data):
    """Yields an isolated temp DB pre-loaded with the sample test data."""
    df = pd.DataFrame(sample_test_data)
    bulk_add_expenses(df, db_path=temp_db)
    return temp_db
