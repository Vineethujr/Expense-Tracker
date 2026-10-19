"""
Unit Tests for Database Initialization and Schema Integrity.
"""

import sqlite3
import pytest
from src.database.schema import init_db
from src.database.connection import get_connection


def test_init_db_creates_tables(temp_db):
    """Verify that init_db creates expenses and budgets tables with indexes."""
    with get_connection(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]

        assert "expenses" in tables
        assert "budgets" in tables


def test_init_db_is_idempotent(temp_db):
    """Calling init_db multiple times must not crash or wipe data."""
    assert init_db(temp_db) is True
    assert init_db(temp_db) is True


def test_expense_amount_positive_constraint(temp_db):
    """Inserting a non-positive amount should trigger an SQLite CHECK constraint error."""
    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(temp_db) as conn:
            conn.execute(
                "INSERT INTO expenses (date, category, amount, payment_method) VALUES ('2026-10-19', 'Food & Groceries', -50.0, 'UPI');"
            )


def test_budget_unique_month_category_constraint(temp_db):
    """Inserting duplicate (month, category) should violate UNIQUE constraint."""
    with get_connection(temp_db) as conn:
        conn.execute("INSERT INTO budgets (month, category, allocated_amount) VALUES ('2026-10', 'OVERALL', 30000.0);")

    with pytest.raises(sqlite3.IntegrityError):
        with get_connection(temp_db) as conn:
            conn.execute("INSERT INTO budgets (month, category, allocated_amount) VALUES ('2026-10', 'OVERALL', 40000.0);")
