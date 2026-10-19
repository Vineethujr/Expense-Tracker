"""
Expense Input Validation Module.
Validates fields for single expense creation and editing.
"""

from datetime import datetime, date, timedelta
from typing import Tuple, Any
from src.config import ALL_CATEGORIES, PAYMENT_METHODS


def validate_expense(
    date_val: Any,
    category: Any,
    amount: Any,
    payment_method: Any,
    description: Any = ""
) -> Tuple[bool, str]:
    """
    Validates expense attributes.
    Returns (True, "") if valid, or (False, "error message") if invalid.
    """
    # 1. Amount Validation
    if amount is None or amount == "":
        return False, "Amount is required."
    try:
        amount_float = float(amount)
    except (ValueError, TypeError):
        return False, "Amount must be a valid numeric value."

    if amount_float <= 0:
        return False, "Amount must be strictly greater than zero."
    if amount_float > 100_000_000:
        return False, "Amount exceeds the maximum permissible limit (₹ 10 Crore)."

    # 2. Date Validation
    if not date_val:
        return False, "Date is required."

    if isinstance(date_val, (datetime, date)):
        date_obj = date_val if isinstance(date_val, date) else date_val.date()
    else:
        try:
            date_obj = datetime.strptime(str(date_val).strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format."

    # Prevent future dates beyond tomorrow (allowing minor timezone variances)
    tomorrow = date.today() + timedelta(days=1)
    if date_obj > tomorrow:
        return False, f"Date cannot be in the future (maximum allowed: {tomorrow.strftime('%Y-%m-%d')})."

    # Reasonable historical floor
    if date_obj < date(2000, 1, 1):
        return False, "Date cannot be earlier than 01 Jan 2000."

    # 3. Category Validation
    if not category or not str(category).strip():
        return False, "Category is required."
    clean_category = str(category).strip()
    if clean_category not in ALL_CATEGORIES:
        return False, f"Invalid category '{clean_category}'. Please select an approved category."

    # 4. Payment Method Validation
    if not payment_method or not str(payment_method).strip():
        return False, "Payment method is required."
    clean_method = str(payment_method).strip()
    if clean_method not in PAYMENT_METHODS:
        return False, f"Invalid payment method '{clean_method}'. Please select an approved method."

    # 5. Description Validation
    if description and len(str(description)) > 255:
        return False, "Description cannot exceed 255 characters."

    return True, ""
