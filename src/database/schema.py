"""
SQLite Database Schema and Initialization.
Defines tables, constraints, and indexes for persistent expense and budget storage.
"""

from pathlib import Path
from typing import Optional, Union
from src.database.connection import get_connection


CREATE_EXPENSES_TABLE = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    payment_method TEXT NOT NULL,
    description TEXT DEFAULT '',
    is_synthetic INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_BUDGETS_TABLE = """
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL,
    category TEXT NOT NULL,
    allocated_amount REAL NOT NULL CHECK(allocated_amount > 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(month, category)
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_synthetic ON expenses(is_synthetic);",
    "CREATE INDEX IF NOT EXISTS idx_budgets_month ON budgets(month);",
    "CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category);",
]


def init_db(db_path: Optional[Union[str, Path]] = None) -> bool:
    """
    Initializes the SQLite database with required tables and indexes.
    Idempotent: Safe to call repeatedly on app startup.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_EXPENSES_TABLE)
        cursor.execute(CREATE_BUDGETS_TABLE)
        for index_sql in CREATE_INDEXES:
            cursor.execute(index_sql)
    return True
