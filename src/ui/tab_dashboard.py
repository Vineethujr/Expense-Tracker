"""
Dashboard Overview View.
Renders summary KPI cards, category distribution donut, monthly trend charts,
budget utilization meters, and high-priority rule-based insights.
"""

import streamlit as st
import pandas as pd
from datetime import date
from src.services.expense_service import get_all_expenses
from src.services.budget_service import calculate_budget_status
from src.analytics.aggregations import calculate_kpis, calculate_category_summary
from src.analytics.trend_analysis import calculate_monthly_trends
from src.analytics.financial_insights import generate_rule_based_insights
from src.visualization.category_charts import create_category_donut_chart
from src.visualization.trend_charts import create_monthly_trend_chart
from src.visualization.budget_charts import create_budget_utilization_chart
from src.ui.components import render_kpi_card, render_insight_card
from src.utils.formatters import format_currency, format_month


def render_dashboard_tab():
    """Renders the primary Dashboard Overview tab."""
    st.markdown("### 📊 Financial Dashboard Overview")

    df = get_all_expenses()

    if df.empty:
        st.info(
            "👋 **Welcome to your Personal Expense Tracker & Financial Analytics App!**\n\n"
            "Your database is currently empty. You can:\n"
            "1. Navigate to **Manage Expenses** to record your first transaction.\n"
            "2. Go to **Sample Data Management** to load realistic synthetic data for an instant demonstration."
        )
        return

    current_month = date.today().strftime("%Y-%m")

    # Dynamic KPI derivations
    kpis = calculate_kpis(df, current_month=current_month)
    budget_status = calculate_budget_status(current_month, expenses_df=df)

    # 1. KPI Cards Row (6 dynamic metrics)
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        render_kpi_card("Total Outflows", format_currency(kpis["total_expenses"]), "All-time logged spend", icon="💳")
    with c2:
        render_kpi_card(f"Spend ({format_month(current_month)[:3]})", format_currency(kpis["current_month_spending"]), "Current month total", icon="📅")
    with c3:
        render_kpi_card("Avg Ticket Size", format_currency(kpis["avg_transaction_amount"]), "Per transaction average", icon="🏷️")
    with c4:
        render_kpi_card("Transactions", f"{kpis['transaction_count']:,}", "Total records count", icon="🧾")
    with c5:
        render_kpi_card("Top Category", kpis["highest_category"], format_currency(kpis["highest_category_amount"]), icon="👑")
    with c6:
        if budget_status["overall_allocated"] > 0:
            rem_label = format_currency(budget_status["overall_remaining"])
            sub_text = f"{budget_status['overall_utilization_pct']:.1f}% used"
            icon_status = "🟢" if budget_status["overall_status"] == "normal" else ("🟡" if budget_status["overall_status"] == "warning" else "🔴")
        else:
            rem_label = "Not Set"
            sub_text = "Configure in Budgets tab"
            icon_status = "⚪"
        render_kpi_card("Budget Balance", rem_label, sub_text, icon=icon_status)

    st.markdown("---")

    # 2. Main Interactive Visualizations (Donut + Monthly Trend)
    col_chart_1, col_chart_2 = st.columns([1, 1])

    cat_summary_df = calculate_category_summary(df)
    monthly_trends_df = calculate_monthly_trends(df)

    with col_chart_1:
        st.plotly_chart(create_category_donut_chart(cat_summary_df), use_container_width=True, key="dashboard_category_donut")

    with col_chart_2:
        st.plotly_chart(create_monthly_trend_chart(monthly_trends_df), use_container_width=True, key="dashboard_monthly_trend")

    # 3. Budget Status & Financial Intelligence Section
    b_col, i_col = st.columns([1, 1])

    with b_col:
        st.markdown(f"#### 🎯 Budget Progress ({format_month(current_month)})")
        st.plotly_chart(create_budget_utilization_chart(budget_status), use_container_width=True, key="dashboard_budget_progress")

    with i_col:
        st.markdown("#### 💡 Rule-Based Financial Insights")
        insights = generate_rule_based_insights(df, budget_status=budget_status, current_month=current_month)
        for ins in insights[:3]:  # Top 3 insights on main dashboard
            render_insight_card(ins)
