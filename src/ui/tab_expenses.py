"""
Expense Management View.
Provides full CRUD capabilities: Add new expense, edit existing entries,
delete with confirmation, and filter transaction history.
"""

import streamlit as st
import pandas as pd
from datetime import date
from src.config import ALL_CATEGORIES, PAYMENT_METHODS
from src.services.expense_service import (
    add_expense, update_expense, delete_expense, get_all_expenses,
    get_filtered_expenses, get_expense_by_id
)
from src.utils.formatters import format_currency, format_date


def render_expenses_tab():
    """Renders the Expense Management tab."""
    st.markdown("### 📝 Expense Management & Ledger")

    add_tab, edit_tab, delete_tab = st.tabs(["➕ Add Expense", "✏️ Edit Expense", "🗑️ Delete Expense"])

    # --- 1. ADD EXPENSE ---
    with add_tab:
        st.markdown("##### Record a New Transaction")
        with st.form("add_expense_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                exp_date = st.date_input("Transaction Date", value=date.today())
            with col2:
                category = st.selectbox("Category", options=ALL_CATEGORIES)
            with col3:
                amount = st.number_input("Amount (₹)", min_value=1.0, max_value=10000000.0, value=250.0, step=50.0)

            col4, col5 = st.columns([1, 2])
            with col4:
                payment_method = st.selectbox("Payment Method", options=PAYMENT_METHODS)
            with col5:
                description = st.text_input("Description / Notes (Optional)", placeholder="e.g. Swiggy lunch order, groceries, fuel")

            submitted = st.form_submit_button("💾 Save Expense", use_container_width=True)
            if submitted:
                try:
                    new_id = add_expense(
                        date=str(exp_date),
                        category=category,
                        amount=float(amount),
                        payment_method=payment_method,
                        description=description,
                        is_synthetic=0
                    )
                    st.success(f"✅ Expense #{new_id} of {format_currency(amount)} recorded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to save expense: {str(e)}")

    # --- 2. EDIT EXPENSE ---
    with edit_tab:
        st.markdown("##### Modify an Existing Transaction")
        all_df = get_all_expenses()
        if all_df.empty:
            st.info("No expense records available to edit.")
        else:
            options_dict = {
                f"#{row['id']} | {row['date']} | {row['category']} | {format_currency(row['amount'])}": row['id']
                for _, row in all_df.head(100).iterrows()
            }
            selected_label = st.selectbox("Select Transaction to Edit", options=list(options_dict.keys()))
            selected_id = options_dict[selected_label]
            record = get_expense_by_id(selected_id)

            if record:
                with st.form("edit_expense_form"):
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        e_date = st.date_input("Transaction Date", value=date.fromisoformat(record["date"]))
                    with ec2:
                        e_cat_idx = ALL_CATEGORIES.index(record["category"]) if record["category"] in ALL_CATEGORIES else 0
                        e_cat = st.selectbox("Category", options=ALL_CATEGORIES, index=e_cat_idx)
                    with ec3:
                        e_amt = st.number_input("Amount (₹)", min_value=1.0, value=float(record["amount"]), step=50.0)

                    ec4, ec5 = st.columns([1, 2])
                    with ec4:
                        e_meth_idx = PAYMENT_METHODS.index(record["payment_method"]) if record["payment_method"] in PAYMENT_METHODS else 0
                        e_meth = st.selectbox("Payment Method", options=PAYMENT_METHODS, index=e_meth_idx)
                    with ec5:
                        e_desc = st.text_input("Description", value=record["description"] or "")

                    e_submitted = st.form_submit_button("🔄 Update Record", use_container_width=True)
                    if e_submitted:
                        try:
                            update_expense(selected_id, str(e_date), e_cat, float(e_amt), e_meth, e_desc)
                            st.success(f"✅ Transaction #{selected_id} updated successfully!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"❌ Update failed: {str(ex)}")

    # --- 3. DELETE EXPENSE ---
    with delete_tab:
        st.markdown("##### Delete a Transaction")
        all_df = get_all_expenses()
        if all_df.empty:
            st.info("No expense records available to delete.")
        else:
            del_dict = {
                f"#{row['id']} | {row['date']} | {row['category']} | {format_currency(row['amount'])}": row['id']
                for _, row in all_df.head(100).iterrows()
            }
            del_label = st.selectbox("Select Transaction to Delete", options=list(del_dict.keys()), key="del_select")
            del_id = del_dict[del_label]

            col_del_warn, col_del_btn = st.columns([2, 1])
            with col_del_warn:
                confirm_check = st.checkbox("I confirm I want to permanently delete this transaction.", key="del_confirm")
            with col_del_btn:
                if st.button("🗑️ Delete Now", type="secondary", disabled=not confirm_check, use_container_width=True):
                    delete_expense(del_id)
                    st.success(f"✅ Transaction #{del_id} deleted.")
                    st.rerun()

    st.markdown("---")

    # --- FILTERABLE TRANSACTION LEDGER ---
    st.markdown("#### 📜 Transaction History Ledger")

    f1, f2, f3, f4 = st.columns([1, 1, 1, 1])
    with f1:
        date_filter = st.date_input("Date Range", value=(date(date.today().year, 1, 1), date.today()), key="ledger_date")
    with f2:
        cat_filter = st.multiselect("Filter Category", options=ALL_CATEGORIES, default=[])
    with f3:
        method_filter = st.multiselect("Filter Payment Mode", options=PAYMENT_METHODS, default=[])
    with f4:
        keyword = st.text_input("Search Keyword", placeholder="Search description...")

    include_synthetic = st.checkbox("Include Sample / Synthetic Data", value=True)

    start_d = str(date_filter[0]) if isinstance(date_filter, (tuple, list)) and len(date_filter) > 0 else None
    end_d = str(date_filter[1]) if isinstance(date_filter, (tuple, list)) and len(date_filter) > 1 else None

    filtered_df = get_filtered_expenses(
        start_date=start_d,
        end_date=end_d,
        categories=cat_filter if cat_filter else None,
        payment_methods=method_filter if method_filter else None,
        include_synthetic=include_synthetic,
        search_keyword=keyword
    )

    st.caption(f"Showing {len(filtered_df):,} matching transactions | Total: {format_currency(filtered_df['amount'].sum() if not filtered_df.empty else 0)}")

    if filtered_df.empty:
        st.warning("No transactions match the selected criteria.")
    else:
        # Display formatted table
        display_df = filtered_df.copy()
        display_df["Formatted Amount"] = display_df["amount"].apply(lambda x: format_currency(x))
        display_df["Display Date"] = display_df["date"].apply(lambda x: format_date(x))
        display_df["Type"] = display_df["is_synthetic"].apply(lambda s: "🧪 Sample" if s == 1 else "👤 User")

        display_cols = ["id", "Display Date", "category", "Formatted Amount", "payment_method", "description", "Type"]
        st.dataframe(
            display_df[display_cols].rename(columns={
                "id": "ID",
                "Display Date": "Date",
                "category": "Category",
                "Formatted Amount": "Amount (₹)",
                "payment_method": "Payment Mode",
                "description": "Description",
                "Type": "Data Source"
            }),
            use_container_width=True,
            hide_index=True
        )
