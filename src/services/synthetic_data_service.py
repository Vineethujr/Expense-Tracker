"""
Synthetic Data Generation Service.
Generates realistic, reproducible sample transactions spanning several months
for financial demonstration and testing.
"""

import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from src.config import ALL_CATEGORIES, PAYMENT_METHODS
from src.services.expense_service import bulk_add_expenses, get_expenses_stats_count


def generate_synthetic_expenses(
    months_back: int = 5,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates a reproducible dataset of realistic personal expenses.
    Uses realistic Indian spending patterns and assigns is_synthetic = 1.
    """
    rng = np.random.default_rng(seed)
    end_date = date.today()
    start_date = end_date - timedelta(days=months_back * 30)

    # Calculate month periods
    current = start_date
    all_dates = []
    while current <= end_date:
        all_dates.append(current)
        current += timedelta(days=1)

    records: List[Dict[str, Any]] = []

    # Monthly recurring templates (Housing & Rent, Utilities, Subscriptions)
    year_months = sorted(list({d.strftime("%Y-%m") for d in all_dates}))
    for ym in year_months:
        y, m = map(int, ym.split("-"))
        # 1. Rent on 2nd-4th of each month
        rent_day = min(int(rng.integers(2, 5)), 28)
        rent_date = date(y, m, rent_day)
        if start_date <= rent_date <= end_date:
            rent_amt = float(rng.choice([18000.0, 22500.0, 25000.0, 28000.0]))
            records.append({
                "date": rent_date.strftime("%Y-%m-%d"),
                "category": "Housing & Rent",
                "amount": rent_amt,
                "payment_method": "Net Banking",
                "description": "Monthly House Rent [Sample]",
                "is_synthetic": 1
            })

        # 2. Electricity & WiFi bills on 10th-14th
        util_day = min(int(rng.integers(10, 15)), 28)
        util_date = date(y, m, util_day)
        if start_date <= util_date <= end_date:
            util_amt = float(rng.uniform(1800.0, 3600.0))
            records.append({
                "date": util_date.strftime("%Y-%m-%d"),
                "category": "Utilities & Bills",
                "amount": round(util_amt, 2),
                "payment_method": "UPI",
                "description": "Electricity & Broadband Bill [Sample]",
                "is_synthetic": 1
            })

        # 3. Mobile Recharge & Streaming Subscription
        sub_day = min(int(rng.integers(5, 12)), 28)
        sub_date = date(y, m, sub_day)
        if start_date <= sub_date <= end_date:
            sub_amt = float(rng.choice([499.0, 699.0, 999.0, 1199.0]))
            records.append({
                "date": sub_date.strftime("%Y-%m-%d"),
                "category": "Subscriptions & Memberships",
                "amount": sub_amt,
                "payment_method": "Credit Card",
                "description": "OTT & Mobile Plan [Sample]",
                "is_synthetic": 1
            })

    # Variable daily and weekly expenses
    for day in all_dates:
        is_weekend = day.weekday() >= 5
        day_str = day.strftime("%Y-%m-%d")

        # Groceries: 2 to 3 times a week
        if rng.random() < 0.35:
            records.append({
                "date": day_str,
                "category": "Food & Groceries",
                "amount": round(float(rng.uniform(350.0, 2800.0)), 2),
                "payment_method": str(rng.choice(["UPI", "UPI", "Credit Card", "Cash"])),
                "description": str(rng.choice(["Supermarket Provisions", "Fresh Vegetables & Fruits", "Dairy & Essentials", "Local Kirana Store"])) + " [Sample]",
                "is_synthetic": 1
            })

        # Transportation: commute on weekdays, cabs on weekends
        if rng.random() < 0.40:
            amt = float(rng.uniform(60.0, 450.0)) if not is_weekend else float(rng.uniform(150.0, 850.0))
            records.append({
                "date": day_str,
                "category": "Transportation",
                "amount": round(amt, 2),
                "payment_method": str(rng.choice(["UPI", "Metro Card / UPI", "Cash", "Debit Card"])),
                "description": str(rng.choice(["Metro Commute", "Auto Rickshaw Fare", "Cab Ride", "Fuel Refill"])) + " [Sample]",
                "is_synthetic": 1
            })

        # Dining & Food Delivery: more likely on weekends and Fridays
        dining_prob = 0.50 if is_weekend else 0.25
        if rng.random() < dining_prob:
            dining_amt = float(rng.uniform(250.0, 1850.0))
            records.append({
                "date": day_str,
                "category": "Dining & Takeout",
                "amount": round(dining_amt, 2),
                "payment_method": str(rng.choice(["UPI", "UPI", "Credit Card"])),
                "description": str(rng.choice(["Swiggy / Zomato Order", "Dinner with Friends", "Café Coffee & Snacks", "Weekend Brunch"])) + " [Sample]",
                "is_synthetic": 1
            })

        # Occasional Shopping: ~3-5 times a month
        if rng.random() < 0.12:
            records.append({
                "date": day_str,
                "category": "Shopping & Retail",
                "amount": round(float(rng.uniform(650.0, 4900.0)), 2),
                "payment_method": str(rng.choice(["Credit Card", "UPI", "Debit Card"])),
                "description": str(rng.choice(["Clothing & Apparel", "Electronics Accessories", "Home Essentials", "Online E-commerce Order"])) + " [Sample]",
                "is_synthetic": 1
            })

        # Entertainment: movies, events on weekends
        if is_weekend and rng.random() < 0.25:
            records.append({
                "date": day_str,
                "category": "Entertainment & Leisure",
                "amount": round(float(rng.uniform(400.0, 2200.0)), 2),
                "payment_method": str(rng.choice(["Credit Card", "UPI"])),
                "description": str(rng.choice(["Movie Tickets & Popcorn", "Weekend Game / Outing", "Concert / Event Pass"])) + " [Sample]",
                "is_synthetic": 1
            })

        # Healthcare / Pharmacy: occasional
        if rng.random() < 0.06:
            records.append({
                "date": day_str,
                "category": "Health & Medical",
                "amount": round(float(rng.uniform(200.0, 2500.0)), 2),
                "payment_method": str(rng.choice(["UPI", "Cash", "Credit Card"])),
                "description": str(rng.choice(["Pharmacy Medicines", "Doctor Consultation", "Lab Diagnostic Test", "Dental Checkup"])) + " [Sample]",
                "is_synthetic": 1
            })

    df = pd.DataFrame(records)
    # Sort chronologically
    df["date_dt"] = pd.to_datetime(df["date"])
    df = df.sort_values("date_dt").drop(columns=["date_dt"]).reset_index(drop=True)
    return df


def seed_synthetic_data_into_db(
    months_back: int = 5,
    seed: int = 42,
    db_path: Optional[Union[str, Path]] = None
) -> int:
    """
    Generates reproducible synthetic expenses and inserts them into the database.
    Prevents duplicate insertion if synthetic records are already present.
    Returns the count of newly inserted records.
    """
    stats = get_expenses_stats_count(db_path)
    if stats["synthetic"] > 0:
        # Avoid duplicate sample records if already loaded
        return 0

    df = generate_synthetic_expenses(months_back=months_back, seed=seed)
    return bulk_add_expenses(df, db_path=db_path)
