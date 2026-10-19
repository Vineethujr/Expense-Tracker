"""
Unit Tests for Expense and CSV Input Validation.
"""

import pytest
import pandas as pd
from datetime import date, timedelta
from src.validation.expense_validator import validate_expense
from src.validation.csv_validator import validate_and_clean_csv, parse_amount_safely, parse_date_safely


def test_validate_expense_success():
    """Valid expense inputs should pass with empty error string."""
    is_valid, err = validate_expense(
        date_val="2026-10-15",
        category="Food & Groceries",
        amount=550.0,
        payment_method="UPI",
        description="Weekly vegetables"
    )
    assert is_valid is True
    assert err == ""


@pytest.mark.parametrize("invalid_amount, expected_substr", [
    (0, "strictly greater than zero"),
    (-100.0, "strictly greater than zero"),
    ("not_a_number", "valid numeric"),
    (None, "required"),
    ("", "required"),
    (150_000_000, "maximum permissible limit"),
])
def test_validate_expense_invalid_amounts(invalid_amount, expected_substr):
    """Test rejection of non-positive or malformed amounts."""
    is_valid, err = validate_expense("2026-10-15", "Food & Groceries", invalid_amount, "UPI")
    assert is_valid is False
    assert expected_substr in err


def test_validate_expense_future_date():
    """Future dates (> tomorrow) should be rejected."""
    future_date = (date.today() + timedelta(days=5)).strftime("%Y-%m-%d")
    is_valid, err = validate_expense(future_date, "Food & Groceries", 100.0, "UPI")
    assert is_valid is False
    assert "future" in err.lower()


def test_validate_expense_invalid_category():
    """Unapproved categories should be rejected."""
    is_valid, err = validate_expense("2026-10-15", "Cryptocurrency Investment", 500.0, "UPI")
    assert is_valid is False
    assert "invalid category" in err.lower()


def test_validate_expense_invalid_payment_method():
    """Unapproved payment methods should be rejected."""
    is_valid, err = validate_expense("2026-10-15", "Food & Groceries", 500.0, "Bitcoin")
    assert is_valid is False
    assert "invalid payment method" in err.lower()


def test_validate_expense_long_description():
    """Descriptions longer than 255 characters should be rejected."""
    long_desc = "a" * 256
    is_valid, err = validate_expense("2026-10-15", "Food & Groceries", 500.0, "UPI", description=long_desc)
    assert is_valid is False
    assert "255 characters" in err


# --- CSV Validation Tests ---

def test_parse_amount_safely():
    """Test cleaning varied currency strings."""
    assert parse_amount_safely("₹ 1,500.50") == 1500.50
    assert parse_amount_safely("$250") == 250.0
    assert parse_amount_safely("  3,450  ") == 3450.0
    assert parse_amount_safely("-50") is None
    assert parse_amount_safely("abc") is None


def test_parse_date_safely():
    """Test parsing varied date representations."""
    assert parse_date_safely("2026-10-19") == "2026-10-19"
    assert parse_date_safely("19/10/2026") == "2026-10-19"
    assert parse_date_safely("19-10-2026") == "2026-10-19"
    assert parse_date_safely("invalid") is None


def test_csv_validation_missing_columns():
    """CSV missing required columns should return an error in report."""
    bad_df = pd.DataFrame({"random_col": [1, 2, 3]})
    clean_df, report = validate_and_clean_csv(bad_df)
    assert clean_df.empty
    assert len(report["errors"]) > 0
    assert "Missing required columns" in report["errors"][0]


def test_csv_validation_clean_data_and_duplicates():
    """Test parsing a valid CSV with an internal duplicate row."""
    raw_csv_data = pd.DataFrame({
        "Date": ["2026-10-10", "11/10/2026", "2026-10-10"],  # row 3 is duplicate of row 1
        "Category": ["Food & Groceries", "utilities & bills", "Food & Groceries"],
        "Amount": ["₹ 1,500.00", "2200.50", "1500.00"],
        "Payment Mode": ["UPI", "Net Banking", "UPI"],
        "Description": ["Grocery shopping", "Electricity bill", "Grocery shopping"]
    })

    clean_df, report = validate_and_clean_csv(raw_csv_data)
    assert report["total_rows"] == 3
    assert report["valid_rows"] == 2
    assert report["duplicate_rows"] == 1
    assert len(clean_df) == 2
    assert clean_df.iloc[0]["category"] == "Food & Groceries"
    assert clean_df.iloc[1]["category"] == "Utilities & Bills"
