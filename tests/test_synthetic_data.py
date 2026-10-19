"""
Unit Tests for Synthetic Data Generation and Duplicate Prevention.
"""

import pytest
import pandas as pd
from src.services.synthetic_data_service import generate_synthetic_expenses, seed_synthetic_data_into_db
from src.services.expense_service import get_expenses_stats_count


def test_synthetic_data_reproducibility():
    """Generating with the same random seed must produce identical data."""
    df1 = generate_synthetic_expenses(months_back=3, seed=42)
    df2 = generate_synthetic_expenses(months_back=3, seed=42)

    pd.testing.assert_frame_equal(df1, df2)


def test_synthetic_data_attributes():
    """Verify generated synthetic records have valid structure and labels."""
    df = generate_synthetic_expenses(months_back=3, seed=42)

    assert not df.empty
    expected_cols = ["date", "category", "amount", "payment_method", "description", "is_synthetic"]
    for col in expected_cols:
        assert col in df.columns

    # All records must have is_synthetic = 1
    assert (df["is_synthetic"] == 1).all()

    # All amounts must be positive
    assert (df["amount"] > 0).all()

    # Descriptions should contain [Sample]
    assert df["description"].str.contains(r"\[Sample\]").all()


def test_seed_synthetic_data_prevents_duplicate_insertion(temp_db):
    """Calling seed_synthetic_data_into_db multiple times must not duplicate records."""
    inserted_1 = seed_synthetic_data_into_db(months_back=3, seed=42, db_path=temp_db)
    assert inserted_1 > 0

    stats_1 = get_expenses_stats_count(db_path=temp_db)
    assert stats_1["synthetic"] == inserted_1

    # Second call should recognize existing synthetic records and insert 0
    inserted_2 = seed_synthetic_data_into_db(months_back=3, seed=42, db_path=temp_db)
    assert inserted_2 == 0

    stats_2 = get_expenses_stats_count(db_path=temp_db)
    assert stats_2["synthetic"] == inserted_1
