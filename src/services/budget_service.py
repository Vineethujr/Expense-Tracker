"""
Budget Service Module.
Handles monthly and category-level budget allocations, utilization calculations,
and tiered alert triggers (80% Warning, 100% Critical).
"""

import pandas as pd
from typing import Optional, Dict, Any, Union
from pathlib import Path
from src.database.connection import get_connection
from src.database.schema import init_db
from src.config import BUDGET_WARNING_THRESHOLD, BUDGET_CRITICAL_THRESHOLD, ALL_CATEGORIES


def set_budget(
    month: str,
    category: str,
    allocated_amount: float,
    db_path: Optional[Union[str, Path]] = None
) -> bool:
    """
    Sets or updates a monthly or category budget.
    'category' can be 'OVERALL' or any valid category from ALL_CATEGORIES.
    """
    init_db(db_path)
    clean_month = str(month).strip()[:7]
    clean_cat = str(category).strip()

    if clean_cat != "OVERALL" and clean_cat not in ALL_CATEGORIES:
        raise ValueError(f"Invalid budget category: '{clean_cat}'. Must be 'OVERALL' or an approved category.")

    try:
        amt = float(allocated_amount)
    except (ValueError, TypeError):
        raise ValueError("Allocated amount must be a valid number.")

    if amt <= 0:
        raise ValueError("Allocated budget must be strictly greater than zero.")

    query = """
    INSERT INTO budgets (month, category, allocated_amount)
    VALUES (?, ?, ?)
    ON CONFLICT(month, category) DO UPDATE SET
        allocated_amount = excluded.allocated_amount,
        created_at = CURRENT_TIMESTAMP;
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (clean_month, clean_cat, amt))
        return cursor.rowcount > 0


def get_budgets_for_month(month: str, db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieves all budget allocations for a specific YYYY-MM month."""
    init_db(db_path)
    clean_month = str(month).strip()[:7]
    query = "SELECT id, month, category, allocated_amount, created_at FROM budgets WHERE month = ? ORDER BY category;"
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn, params=[clean_month])


def get_all_budgets(db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieves all budget allocations across all months."""
    init_db(db_path)
    query = "SELECT id, month, category, allocated_amount, created_at FROM budgets ORDER BY month DESC, category;"
    with get_connection(db_path) as conn:
        return pd.read_sql_query(query, conn)


def delete_budget(budget_id: int, db_path: Optional[Union[str, Path]] = None) -> bool:
    """Deletes a budget target by its ID."""
    init_db(db_path)
    query = "DELETE FROM budgets WHERE id = ?;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (int(budget_id),))
        return cursor.rowcount > 0


def calculate_budget_status(
    month: str,
    expenses_df: Optional[pd.DataFrame] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Calculates detailed budget utilization and alert statuses for a given month.
    """
    clean_month = str(month).strip()[:7]
    budgets_df = get_budgets_for_month(clean_month, db_path)

    # Filter expenses for target month if dataframe provided, else query DB
    if expenses_df is None:
        from src.services.expense_service import get_filtered_expenses
        start_date = f"{clean_month}-01"
        # End date approximate
        end_date = f"{clean_month}-31"
        expenses_df = get_filtered_expenses(start_date=start_date, end_date=end_date, db_path=db_path)
    else:
        # Filter in memory
        expenses_df = expenses_df[expenses_df["date"].astype(str).str.startswith(clean_month)].copy()

    total_spent = float(expenses_df["amount"].sum()) if not expenses_df.empty else 0.0

    category_spend_map = {}
    if not expenses_df.empty:
        cat_grouped = expenses_df.groupby("category")["amount"].sum()
        category_spend_map = cat_grouped.to_dict()

    overall_budget_row = budgets_df[budgets_df["category"] == "OVERALL"] if not budgets_df.empty else pd.DataFrame()
    overall_allocated = float(overall_budget_row["allocated_amount"].iloc[0]) if not overall_budget_row.empty else 0.0

    # Overall calculation
    if overall_allocated > 0:
        overall_utilization = round((total_spent / overall_allocated) * 100.0, 2)
        overall_remaining = round(overall_allocated - total_spent, 2)
        if overall_utilization >= (BUDGET_CRITICAL_THRESHOLD * 100.0):
            overall_status = "exceeded"
        elif overall_utilization >= (BUDGET_WARNING_THRESHOLD * 100.0):
            overall_status = "warning"
        else:
            overall_status = "normal"
    else:
        overall_utilization = 0.0
        overall_remaining = 0.0
        overall_status = "not_set"

    # Category-level calculations
    category_budgets = []
    category_budget_rows = budgets_df[budgets_df["category"] != "OVERALL"] if not budgets_df.empty else pd.DataFrame()

    for _, row in category_budget_rows.iterrows():
        cat = row["category"]
        allocated = float(row["allocated_amount"])
        spent = float(category_spend_map.get(cat, 0.0))
        utilization = round((spent / allocated) * 100.0, 2) if allocated > 0 else 0.0
        remaining = round(allocated - spent, 2)

        if utilization >= (BUDGET_CRITICAL_THRESHOLD * 100.0):
            status = "exceeded"
        elif utilization >= (BUDGET_WARNING_THRESHOLD * 100.0):
            status = "warning"
        else:
            status = "normal"

        category_budgets.append({
            "id": row["id"],
            "category": cat,
            "allocated": allocated,
            "spent": spent,
            "remaining": remaining,
            "utilization_pct": utilization,
            "status": status
        })

    return {
        "month": clean_month,
        "overall_allocated": overall_allocated,
        "total_spent": total_spent,
        "overall_remaining": overall_remaining,
        "overall_utilization_pct": overall_utilization,
        "overall_status": overall_status,
        "category_budgets": category_budgets,
        "has_budgets": not budgets_df.empty
    }
