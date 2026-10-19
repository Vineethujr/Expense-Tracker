"""
Configuration Module for Expense Tracker App.
Defines constants, category taxonomies, payment methods, budget thresholds,
and path defaults.
"""

from pathlib import Path

# Application Metadata
APP_TITLE = "Expense Tracker & Financial Analytics"
APP_SUBTITLE = "Personal Finance Intelligence with Rule-Based Insights"
APP_ICON = "💰"

# Currency & Localization
CURRENCY_SYMBOL = "₹"
CURRENCY_CODE = "INR"

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
SCREENSHOTS_DIR = BASE_DIR / "Screenshots"
DEFAULT_DB_PATH = DATA_DIR / "expenses.db"

# Ensure runtime directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

# Category Taxonomy (Mapped to Essential vs Discretionary for financial analytics)
ESSENTIAL_CATEGORIES = [
    "Housing & Rent",
    "Food & Groceries",
    "Utilities & Bills",
    "Transportation",
    "Health & Medical",
    "Education & Tuition",
]

DISCRETIONARY_CATEGORIES = [
    "Dining & Takeout",
    "Shopping & Retail",
    "Entertainment & Leisure",
    "Travel & Vacation",
    "Personal Care",
    "Subscriptions & Memberships",
    "Miscellaneous",
]

ALL_CATEGORIES = ESSENTIAL_CATEGORIES + DISCRETIONARY_CATEGORIES

# Category Palette for Consistent Plotly Visualizations
CATEGORY_COLORS = {
    "Housing & Rent": "#264653",
    "Food & Groceries": "#2a9d8f",
    "Utilities & Bills": "#457b9d",
    "Transportation": "#e76f51",
    "Health & Medical": "#e63946",
    "Education & Tuition": "#1d3557",
    "Dining & Takeout": "#f4a261",
    "Shopping & Retail": "#d4a373",
    "Entertainment & Leisure": "#b5838d",
    "Travel & Vacation": "#6d6875",
    "Personal Care": "#84a59d",
    "Subscriptions & Memberships": "#f28482",
    "Miscellaneous": "#8d99ae",
}

# Payment Methods
PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Cash",
]

# Budget Alert Thresholds
BUDGET_WARNING_THRESHOLD = 0.80   # 80% used -> Warning
BUDGET_CRITICAL_THRESHOLD = 1.00  # 100% used -> Over budget

# Date Formats
DATE_STORAGE_FORMAT = "%Y-%m-%d"
DATE_DISPLAY_FORMAT = "%d %b %Y"
MONTH_STORAGE_FORMAT = "%Y-%m"
