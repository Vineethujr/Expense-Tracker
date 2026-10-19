"""
Budget Management View.
Allows users to define overall monthly and category-level budgets,
track utilization percentages in real time, and receive 80% warning and 100% overspend alerts.
"""

import streamlit as st
import pandas as pd
from datetime import date
from src.config import ALL_CATEGORIES
from src.services.budget_service import set_budget, get_budgets_for_month, delete_budget, calculate_budget_status
from src.services.expense_service import get_all_expenses
from src.visualization.budget_charts import create_budget_utilization_chart
from src.utils.formatters import format_currency, format_month, format_percentage


def render_budgets_tab():
    """Renders the Budget Management & Threshold Alerts tab."""
    st.markdown("### 🎯 Budget Targets & Threshold Monitoring")

    # Select target month (default current)
    curr_date = date.today()
    default_month_str = curr_date.strftime("%Y-%m")

    # Generate recent 12 months for dropdown
    month_options = []
    for i in range(-2, 10):
        # Rough month offset
        yr = curr_date.year + ((curr_date.month - 1 + i) // 12)
        m = ((curr_date.month - 1 + i) % 12) + 1
        month_options.append(f"{yr:04d}-{m:02d}")
    month_options = sorted(list(set(month_options)), reverse=True)

    c_m1, c_m2 = st.columns([1, 2])
    with c_m1:
        selected_month = st.selectbox("Select Target Budget Month", options=month_options, index=month_options.index(default_month_str) if default_month_str in month_options else 0)

    st.markdown("---")

    # Set Budget Form
    with st.expander("➕ Set or Update Budget Targets", expanded=True):
        st.caption(f"Allocating budget targets for **{format_month(selected_month)}**")
        with st.form("budget_form"):
            b_col1, b_col2, b_col3 = st.columns([1.5, 1.5, 1])
            with b_col1:
                budget_scope = st.selectbox("Budget Scope", options=["OVERALL (Entire Month)", "Specific Category"])
            with b_col2:
                if budget_scope == "Specific Category":
                    budget_cat = st.selectbox("Target Category", options=ALL_CATEGORIES)
                else:
                    budget_cat = "OVERALL"
            with b_col3:
                allocated_amt = st.number_input("Budget Limit (₹)", min_value=100.0, max_value=50000000.0, value=30000.0, step=1000.0)

            submitted = st.form_submit_button("💾 Save Budget Allocation", use_container_width=True)
            if submitted:
                try:
                    set_budget(selected_month, budget_cat, float(allocated_amt))
                    st.success(f"✅ Budget of {format_currency(allocated_amt)} set for {budget_cat} in {format_month(selected_month)}.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"❌ Error: {str(ex)}")

    # Current Budget Status
    expenses_df = get_all_expenses()
    budget_status = calculate_budget_status(selected_month, expenses_df=expenses_df)

    st.markdown(f"#### 📊 Utilization Status for {format_month(selected_month)}")

    # Overall Summary Metrics
    if budget_status["overall_allocated"] > 0:
        overall_util = budget_status["overall_utilization_pct"]
        overall_status = budget_status["overall_status"]

        if overall_status == "exceeded":
            st.error(
                f"🚨 **CRITICAL OVERSPEND ALERT!** You have exceeded your monthly budget of "
                f"{format_currency(budget_status['overall_allocated'])} by "
                f"{format_currency(abs(budget_status['overall_remaining']))} ({overall_util:.1f}% utilized)."
            )
        elif overall_status == "warning":
            st.warning(
                f"⚠️ **BUDGET WARNING!** You have reached {overall_util:.1f}% of your monthly budget. "
                f"Remaining: {format_currency(budget_status['overall_remaining'])}."
            )
        else:
            st.success(
                f"✅ **ON TRACK:** You have utilized {overall_util:.1f}% of your monthly budget. "
                f"Remaining: {format_currency(budget_status['overall_remaining'])}."
            )

    # Plotly Utilization Chart
    st.plotly_chart(create_budget_utilization_chart(budget_status), use_container_width=True, key="budgets_tab_utilization_chart")

    # Table of Configured Budgets for the month with delete option
    budgets_df = get_budgets_for_month(selected_month)
    if not budgets_df.empty:
        st.markdown("##### Configured Budget Targets")
        for idx, row in budgets_df.iterrows():
            del_c1, del_c2, del_c3 = st.columns([3, 2, 1])
            with del_c1:
                st.write(f"**{row['category']}**")
            with del_c2:
                st.write(format_currency(row["allocated_amount"]))
            with del_c3:
                if st.button("🗑️ Delete", key=f"del_b_{row['id']}"):
                    delete_budget(row["id"])
                    st.rerun()
