"""
Formatting Utilities for Currency and Dates.
Implements Indian Rupee numbering format (Lakhs, Crores) and user-friendly date representations.
"""

from datetime import datetime
from typing import Union
from src.config import CURRENCY_SYMBOL


def format_currency(amount: Union[int, float], include_symbol: bool = True) -> str:
    """
    Format a number into the Indian currency system (e.g., ₹ 12,34,567.89).
    Negative amounts are formatted as -₹ 12,345.67.
    """
    if amount is None:
        return f"{CURRENCY_SYMBOL} 0.00" if include_symbol else "0.00"

    is_negative = amount < 0
    abs_amount = abs(amount)

    # Format with two decimal places
    formatted_float = f"{abs_amount:.2f}"
    int_part, dec_part = formatted_float.split(".")

    if len(int_part) <= 3:
        formatted_int = int_part
    else:
        # Last 3 digits
        last_three = int_part[-3:]
        remaining = int_part[:-3]
        # Group in pairs of 2 digits from right to left
        pairs = []
        while len(remaining) > 2:
            pairs.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            pairs.append(remaining)
        pairs.reverse()
        formatted_int = ",".join(pairs) + "," + last_three

    result = f"{formatted_int}.{dec_part}"
    prefix = f"-{CURRENCY_SYMBOL} " if is_negative else (f"{CURRENCY_SYMBOL} " if include_symbol else "")
    return f"{prefix}{result}"


def format_date(date_str: str, output_format: str = "%d %b %Y") -> str:
    """
    Convert an ISO date string (YYYY-MM-DD) into a human-readable display string.
    """
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(str(date_str).strip()[:10], "%Y-%m-%d")
        return dt.strftime(output_format)
    except (ValueError, TypeError):
        return str(date_str)


def format_month(month_str: str) -> str:
    """
    Convert 'YYYY-MM' to 'Month YYYY' (e.g., '2026-10' -> 'October 2026').
    """
    if not month_str:
        return "N/A"
    try:
        dt = datetime.strptime(str(month_str).strip()[:7], "%Y-%m")
        return dt.strftime("%B %Y")
    except (ValueError, TypeError):
        return str(month_str)


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a float as a percentage string (e.g., 78.4%).
    """
    if value is None:
        return "0.0%"
    return f"{value:.{decimal_places}f}%"
