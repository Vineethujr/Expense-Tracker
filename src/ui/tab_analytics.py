"""
Spending Analytics View.
Provides deep-dive category breakdowns, daily/monthly trend progressions,
Month-over-Month comparisons, essential vs discretionary distributions, and complete rule-based insights.
"""

import streamlit as st
import pandas as pd
from datetime import date
from src.services.expense_service import get_all_expenses
from src.services.budget_service import calculate_budget_status
from src.analytics.aggregations import calculate_category_summary
from src.analytics.trend_analysis import (
    calculate_monthly_trends, calculate_daily_trends, calculate_category_monthly_trends
)
from src.analytics.spending_patterns import analyze_spending_patterns
from src.analytics.financial_insights import generate_rule_based_insights
from src.visualization.category_charts import create_category_bar_chart, create_category_donut_chart
from src.visualization.trend_charts import (
    create_monthly_trend_chart, create_daily_trend_chart, create_mom_comparison_chart
)
from src.visualization.budget_charts import create_essential_vs_discretionary_chart
from src.ui.components import render_insight_card
from src.utils.formatters import format_currency, format_month, format_percentage


def render_analytics_tab():
    """Renders the comprehensive Spending Analytics tab."""
    st.markdown("### 📈 Comprehensive Spending Analytics")

    df = get_all_expenses()

    if df.empty:
        st.info("No expense data available to analyze. Please add expenses or generate sample demonstration data.")
        return

    # Section 1: Category Analytics & Ranking
    st.markdown("#### 1. Category Breakdown & Ranking")
    cat_summary = calculate_category_summary(df)

    c_col1, c_col2 = st.columns([1, 1])
    with c_col1:
        st.plotly_chart(create_category_bar_chart(cat_summary), use_container_width=True, key="analytics_category_bar")
    with c_col2:
        # Category Data Table
        table_df = cat_summary.copy()
        table_df["Total Spend (₹)"] = table_df["total_spend"].apply(format_currency)
        table_df["Share (%)"] = table_df["percentage"].apply(lambda p: f"{p:.1f}%")
        table_df["Avg / Txn (₹)"] = table_df["avg_spend"].apply(format_currency)
        table_df["Max (₹)"] = table_df["max_spend"].apply(format_currency)

        st.dataframe(
            table_df[["category", "Total Spend (₹)", "Share (%)", "transaction_count", "Avg / Txn (₹)", "Max (₹)"]].rename(columns={
                "category": "Category",
                "transaction_count": "Transactions"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # Section 2: Monthly Trends & Month-over-Month (MoM) Comparison
    st.markdown("#### 2. Monthly Trends & MoM Growth")
    monthly_trends = calculate_monthly_trends(df)

    m_col1, m_col2 = st.columns([1.2, 1])
    with m_col1:
        st.plotly_chart(create_monthly_trend_chart(monthly_trends), use_container_width=True, key="analytics_monthly_trend")

    with m_col2:
        st.markdown("##### Month-over-Month Performance")
        m_display = monthly_trends.copy()
        m_display["Month"] = m_display["month"].apply(format_month)
        m_display["Total Spend (₹)"] = m_display["total_spend"].apply(format_currency)
        m_display["MoM Change (₹)"] = m_display["mom_change_amt"].apply(
            lambda v: format_currency(v) if pd.notna(v) else "—"
        )
        m_display["Growth (%)"] = m_display["mom_growth_pct"].apply(
            lambda v: f"{v:+.1f}%" if pd.notna(v) else "—"
        )
        st.dataframe(
            m_display[["Month", "Total Spend (₹)", "transaction_count", "MoM Change (₹)", "Growth (%)"]].rename(columns={
                "transaction_count": "Txns"
            }),
            use_container_width=True,
            hide_index=True
        )

    # Side-by-side MoM Comparison Selector
    pivot_df = calculate_category_monthly_trends(df)
    months_available = [c for c in pivot_df.columns if c != "category"] if not pivot_df.empty else []

    if len(months_available) >= 2:
        st.markdown("##### Compare Category Spending Between Two Months")
        sel_c1, sel_c2 = st.columns(2)
        with sel_c1:
            m1 = st.selectbox("Base Month", options=months_available, index=len(months_available)-2)
        with sel_c2:
            m2 = st.selectbox("Comparison Month", options=months_available, index=len(months_available)-1)

        st.plotly_chart(create_mom_comparison_chart(pivot_df, m1, m2), use_container_width=True, key="analytics_mom_comparison")

    st.markdown("---")

    # Section 3: Daily Timeline & 7-Day Rolling Average
    st.markdown("#### 3. Daily Spending Timeline & 7-Day Moving Average")
    daily_trends = calculate_daily_trends(df)
    st.plotly_chart(create_daily_trend_chart(daily_trends), use_container_width=True, key="analytics_daily_trend")

    st.markdown("---")

    # Section 4: Spending Habits (Essential vs Discretionary, Day of Week, Top Transactions)
    st.markdown("#### 4. Behavioral Spending Patterns")
    patterns = analyze_spending_patterns(df)

    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        st.plotly_chart(create_essential_vs_discretionary_chart(patterns), use_container_width=True, key="analytics_essential_vs_discretionary")

    with p_col2:
        st.markdown("##### 💳 Payment Mode Distribution")
        pm_df = patterns["payment_methods_summary"]
        if not pm_df.empty:
            pm_display = pm_df.copy()
            pm_display["Spend (₹)"] = pm_display["total_spend"].apply(format_currency)
            pm_display["Share (%)"] = pm_display["percentage"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(
                pm_display[["payment_method", "Spend (₹)", "Share (%)", "transaction_count"]].rename(columns={
                    "payment_method": "Payment Method",
                    "transaction_count": "Transactions"
                }),
                use_container_width=True,
                hide_index=True
            )

    # Top 5 Largest Transactions Table
    st.markdown("##### 🏆 Top 5 Largest Outflows")
    top_txns = patterns["top_transactions"]
    if top_txns:
        top_df = pd.DataFrame(top_txns)
        top_df["Amount (₹)"] = top_df["amount"].apply(format_currency)
        st.dataframe(
            top_df[["date", "category", "Amount (₹)", "payment_method", "description"]].rename(columns={
                "date": "Date",
                "category": "Category",
                "payment_method": "Payment Mode",
                "description": "Description"
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # Section 5: All Rule-Based Financial Insights
    st.markdown("#### 5. Financial Advisory & Heuristic Insights")
    current_month = date.today().strftime("%Y-%m")
    budget_status = calculate_budget_status(current_month, expenses_df=df)
    all_insights = generate_rule_based_insights(df, budget_status=budget_status, current_month=current_month)

    for ins in all_insights:
        render_insight_card(ins)
