"""
Expense Service Module.
Executes business logic and parameterized SQL CRUD operations for expenses.
"""

import pandas as pd
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from src.database.connection import get_connection
from src.database.schema import init_db
from src.validation.expense_validator import validate_expense


def add_expense(
    date: str,
    category: str,
    amount: float,
    payment_method: str,
    description: str = "",
    is_synthetic: int = 0,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Validates and inserts a new expense record into the SQLite database.
    Returns the newly inserted record ID.
    Raises ValueError on validation failure.
    """
    init_db(db_path)
    is_valid, error = validate_expense(date, category, amount, payment_method, description)
    if not is_valid:
        raise ValueError(error)

    query = """
    INSERT INTO expenses (date, category, amount, payment_method, description, is_synthetic)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            query,
            (str(date)[:10], str(category).strip(), float(amount), str(payment_method).strip(), str(description).strip(), int(is_synthetic))
        )
        return cursor.lastrowid


def update_expense(
    expense_id: int,
    date: str,
    category: str,
    amount: float,
    payment_method: str,
    description: str = "",
    db_path: Optional[Union[str, Path]] = None
) -> bool:
    """
    Updates an existing expense record.
    Returns True if an entry was modified, False otherwise.
    """
    init_db(db_path)
    is_valid, error = validate_expense(date, category, amount, payment_method, description)
    if not is_valid:
        raise ValueError(error)

    query = """
    UPDATE expenses
    SET date = ?, category = ?, amount = ?, payment_method = ?, description = ?
    WHERE id = ?;
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            query,
            (str(date)[:10], str(category).strip(), float(amount), str(payment_method).strip(), str(description).strip(), int(expense_id))
        )
        return cursor.rowcount > 0


def delete_expense(expense_id: int, db_path: Optional[Union[str, Path]] = None) -> bool:
    """
    Deletes an expense record by its ID.
    Returns True if deleted, False if record not found.
    """
    init_db(db_path)
    query = "DELETE FROM expenses WHERE id = ?;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (int(expense_id),))
        return cursor.rowcount > 0


def get_expense_by_id(expense_id: int, db_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """Fetches a single expense as a dictionary, or None if not found."""
    init_db(db_path)
    query = "SELECT * FROM expenses WHERE id = ?;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (int(expense_id),))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_expenses(db_path: Optional[Union[str, Path]] = None) -> pd.DataFrame:
    """Retrieves all expenses ordered chronologically descending."""
    init_db(db_path)
    query = "SELECT id, date, category, amount, payment_method, description, is_synthetic, created_at FROM expenses ORDER BY date DESC, id DESC;"
    with get_connection(db_path) as conn:
        df = pd.read_sql_query(query, conn)
    return df


def get_filtered_expenses(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    categories: Optional[List[str]] = None,
    payment_methods: Optional[List[str]] = None,
    include_synthetic: bool = True,
    search_keyword: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None
) -> pd.DataFrame:
    """
    Retrieves filtered expenses based on user criteria.
    Uses parameterized SQL queries.
    """
    init_db(db_path)
    conditions = []
    params = []

    if start_date:
        conditions.append("date >= ?")
        params.append(str(start_date)[:10])

    if end_date:
        conditions.append("date <= ?")
        params.append(str(end_date)[:10])

    if categories:
        placeholders = ",".join("?" for _ in categories)
        conditions.append(f"category IN ({placeholders})")
        params.extend(categories)

    if payment_methods:
        placeholders = ",".join("?" for _ in payment_methods)
        conditions.append(f"payment_method IN ({placeholders})")
        params.extend(payment_methods)

    if not include_synthetic:
        conditions.append("is_synthetic = 0")

    if search_keyword and search_keyword.strip():
        conditions.append("(description LIKE ? OR category LIKE ?)")
        wildcard = f"%{search_keyword.strip()}%"
        params.extend([wildcard, wildcard])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"""
    SELECT id, date, category, amount, payment_method, description, is_synthetic, created_at
    FROM expenses
    {where_clause}
    ORDER BY date DESC, id DESC;
    """

    with get_connection(db_path) as conn:
        df = pd.read_sql_query(query, conn, params=params)
    return df


def bulk_add_expenses(df: pd.DataFrame, db_path: Optional[Union[str, Path]] = None) -> int:
    """
    Inserts a cleaned DataFrame of expenses in a single transaction.
    Returns the count of successfully inserted records.
    """
    if df.empty:
        return 0
    init_db(db_path)

    query = """
    INSERT INTO expenses (date, category, amount, payment_method, description, is_synthetic)
    VALUES (?, ?, ?, ?, ?, ?);
    """
    records = []
    for _, row in df.iterrows():
        records.append((
            str(row["date"])[:10],
            str(row["category"]).strip(),
            float(row["amount"]),
            str(row["payment_method"]).strip(),
            str(row.get("description", "")).strip(),
            int(row.get("is_synthetic", 0))
        ))

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(query, records)
        return cursor.rowcount


def purge_synthetic_expenses(db_path: Optional[Union[str, Path]] = None) -> int:
    """
    Deletes all synthetic sample transactions, preserving all genuine user entries.
    Returns count of deleted records.
    """
    init_db(db_path)
    query = "DELETE FROM expenses WHERE is_synthetic = 1;"
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.rowcount


def get_expenses_stats_count(db_path: Optional[Union[str, Path]] = None) -> Dict[str, int]:
    """Returns total, user-entered, and synthetic record counts."""
    init_db(db_path)
    query = """
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN is_synthetic = 1 THEN 1 ELSE 0 END) as synthetic,
        SUM(CASE WHEN is_synthetic = 0 THEN 1 ELSE 0 END) as user_count
    FROM expenses;
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        return {
            "total": row["total"] or 0,
            "synthetic": row["synthetic"] or 0,
            "user": row["user_count"] or 0
        }
