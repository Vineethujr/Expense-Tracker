"""
Unit Tests for CSV Export and Template Generation.
"""

import io
import pandas as pd
from src.services.data_io_service import export_expenses_to_csv, generate_csv_template


def test_export_expenses_to_csv():
    """Verify DataFrame converts to valid CSV string."""
    df = pd.DataFrame([
        {"id": 1, "date": "2026-10-10", "category": "Food & Groceries", "amount": 1200.0, "payment_method": "UPI", "description": "Vegetables"},
        {"id": 2, "date": "2026-10-11", "category": "Transportation", "amount": 350.0, "payment_method": "Cash", "description": "Auto fare"}
    ])

    csv_str = export_expenses_to_csv(df)
    assert "id,date,category,amount,payment_method,description" in csv_str
    assert "Food & Groceries" in csv_str
    assert "1200.0" in csv_str

    # Test roundtrip parseability
    parsed_df = pd.read_csv(io.StringIO(csv_str))
    assert len(parsed_df) == 2


def test_generate_csv_template():
    """Verify that generated CSV template is valid and parseable."""
    template_str = generate_csv_template()
    assert "date,category,amount,payment_method,description" in template_str

    parsed_df = pd.read_csv(io.StringIO(template_str))
    assert not parsed_df.empty
    assert "category" in parsed_df.columns
    assert "amount" in parsed_df.columns
