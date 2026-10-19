"""
CSV Data Validation and Ingestion Cleaner.
Inspects uploaded CSV files, cleans rows, standardizes dates and categories,
and flags structural errors and duplicate records.
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Tuple, Dict, Any, Optional
from src.config import ALL_CATEGORIES, PAYMENT_METHODS


COLUMN_ALIASES = {
    "date": ["date", "transaction_date", "trans_date", "timestamp", "expense_date"],
    "category": ["category", "expense_category", "cat", "type"],
    "amount": ["amount", "cost", "spend", "expense_amount", "price", "value", "inr"],
    "payment_method": ["payment_method", "payment_mode", "method", "mode", "payment_type", "paid_via"],
    "description": ["description", "desc", "note", "notes", "details", "remarks", "narrative"],
}


def _match_column(col_name: str, aliases: list) -> bool:
    cleaned = str(col_name).strip().lower().replace(" ", "_").replace("-", "_")
    return cleaned in aliases


def parse_date_safely(val: Any) -> Optional[str]:
    """Attempts to parse varied date representations into YYYY-MM-DD."""
    if pd.isna(val) or val is None or str(val).strip() == "":
        return None
    val_str = str(val).strip()
    # If already YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(val_str[:10], fmt).strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    # Try pandas to_datetime fallback
    try:
        dt = pd.to_datetime(val_str, errors="coerce")
        if pd.notna(dt):
            return dt.strftime("%Y-%m-%d")
    except Exception:
        pass
    return None


def parse_amount_safely(val: Any) -> Optional[float]:
    """Cleans currency strings (e.g. '₹ 1,500.50' or '$1500') to positive float."""
    if pd.isna(val) or val is None:
        return None
    val_str = str(val).replace("₹", "").replace("$", "").replace(",", "").strip()
    try:
        amount = float(val_str)
        return amount if amount > 0 else None
    except (ValueError, TypeError):
        return None


def validate_and_clean_csv(
    df: pd.DataFrame,
    existing_df: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Validates and cleans an uploaded CSV DataFrame.
    Returns:
        (cleaned_df, report)
    """
    report = {
        "total_rows": len(df),
        "valid_rows": 0,
        "dropped_rows": 0,
        "duplicate_rows": 0,
        "errors": [],
        "warnings": [],
    }

    if df.empty:
        report["errors"].append("The uploaded CSV file is empty.")
        return pd.DataFrame(), report

    # 1. Map columns using aliases
    mapped_cols = {}
    for target, aliases in COLUMN_ALIASES.items():
        matched = None
        for col in df.columns:
            if _match_column(col, aliases):
                matched = col
                break
        if matched:
            mapped_cols[target] = matched

    # Mandatory columns check
    mandatory = ["date", "category", "amount"]
    missing_mandatory = [col for col in mandatory if col not in mapped_cols]
    if missing_mandatory:
        report["errors"].append(
            f"Missing required columns in CSV: {', '.join(missing_mandatory)}. "
            f"Found columns: {list(df.columns)}"
        )
        return pd.DataFrame(), report

    # Construct standardized dataframe
    clean_records = []
    dropped_count = 0

    for idx, row in df.iterrows():
        raw_date = row[mapped_cols["date"]]
        raw_cat = row[mapped_cols["category"]]
        raw_amt = row[mapped_cols["amount"]]

        raw_method = row[mapped_cols["payment_method"]] if "payment_method" in mapped_cols else "UPI"
        raw_desc = row[mapped_cols["description"]] if "description" in mapped_cols else ""

        # Validate date
        clean_date = parse_date_safely(raw_date)
        if not clean_date:
            dropped_count += 1
            continue

        # Validate amount
        clean_amt = parse_amount_safely(raw_amt)
        if clean_amt is None or clean_amt <= 0:
            dropped_count += 1
            continue

        # Standardize category
        clean_cat = str(raw_cat).strip()
        matched_cat = None
        for approved_cat in ALL_CATEGORIES:
            if clean_cat.lower() == approved_cat.lower():
                matched_cat = approved_cat
                break
        if not matched_cat:
            matched_cat = "Miscellaneous"

        # Standardize payment method
        clean_method = str(raw_method).strip()
        matched_method = None
        for approved_method in PAYMENT_METHODS:
            if clean_method.lower() == approved_method.lower():
                matched_method = approved_method
                break
        if not matched_method:
            matched_method = "UPI"

        clean_records.append({
            "date": clean_date,
            "category": matched_cat,
            "amount": clean_amt,
            "payment_method": matched_method,
            "description": str(raw_desc).strip()[:255] if pd.notna(raw_desc) else "",
            "is_synthetic": 0
        })

    if not clean_records:
        report["errors"].append("No valid expense records could be parsed from the file.")
        report["dropped_rows"] = dropped_count
        return pd.DataFrame(), report

    cleaned_df = pd.DataFrame(clean_records)

    # 2. Duplicate Detection (within CSV)
    initial_valid = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates(subset=["date", "category", "amount", "description"])
    internal_duplicates = initial_valid - len(cleaned_df)

    # 3. Duplicate Detection (against existing database records if provided)
    db_duplicates = 0
    if existing_df is not None and not existing_df.empty:
        existing_signatures = set(
            zip(
                existing_df["date"].astype(str),
                existing_df["category"].astype(str),
                existing_df["amount"].astype(float).round(2),
                existing_df["description"].fillna("").astype(str)
            )
        )
        is_duplicate = cleaned_df.apply(
            lambda r: (str(r["date"]), str(r["category"]), round(float(r["amount"]), 2), str(r["description"])) in existing_signatures,
            axis=1
        )
        db_duplicates = int(is_duplicate.sum())
        cleaned_df["is_existing_duplicate"] = is_duplicate
    else:
        cleaned_df["is_existing_duplicate"] = False

    report["total_rows"] = len(df)
    report["valid_rows"] = len(cleaned_df)
    report["dropped_rows"] = dropped_count + internal_duplicates
    report["duplicate_rows"] = internal_duplicates + db_duplicates

    if internal_duplicates > 0:
        report["warnings"].append(f"Ignored {internal_duplicates} internal duplicate rows within the uploaded file.")
    if db_duplicates > 0:
        report["warnings"].append(f"Detected {db_duplicates} rows that appear to already exist in your database.")

    return cleaned_df, report
