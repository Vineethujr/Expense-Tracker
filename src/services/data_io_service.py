"""
Data Import and Export Service.
Handles CSV conversions, template downloads, and serialization.
"""

import pandas as pd
from datetime import date
from io import StringIO


def export_expenses_to_csv(df: pd.DataFrame) -> str:
    """
    Serializes an expenses DataFrame into a clean CSV string.
    Omits internal columns like 'is_synthetic' if desired, or preserves for clarity.
    """
    if df.empty:
        return "id,date,category,amount,payment_method,description\n"

    export_cols = ["id", "date", "category", "amount", "payment_method", "description"]
    cols_to_use = [c for c in export_cols if c in df.columns]
    return df[cols_to_use].to_csv(index=False)


def generate_csv_template() -> str:
    """
    Generates a sample CSV template string that users can download, fill, and import.
    """
    today_str = date.today().strftime("%Y-%m-%d")
    template_data = [
        {"date": today_str, "category": "Food & Groceries", "amount": 1450.00, "payment_method": "UPI", "description": "Weekly supermarket grocery shopping"},
        {"date": today_str, "category": "Utilities & Bills", "amount": 2200.00, "payment_method": "Net Banking", "description": "Monthly electricity bill payment"},
        {"date": today_str, "category": "Transportation", "amount": 350.00, "payment_method": "UPI", "description": "Fuel refill for two-wheeler"},
        {"date": today_str, "category": "Dining & Takeout", "amount": 650.00, "payment_method": "Credit Card", "description": "Dinner with colleagues"},
    ]
    df = pd.DataFrame(template_data)
    return df.to_csv(index=False)
