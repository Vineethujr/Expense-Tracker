"""
Expense Tracker App Using Data Science.
Main Streamlit application entry point.
Initializes the SQLite database, injects responsive styling,
and routes navigation across the 6 core functional tabs.
"""

import streamlit as st
from datetime import date
from src.config import APP_TITLE, APP_SUBTITLE, APP_ICON
from src.database.schema import init_db
from src.services.expense_service import get_expenses_stats_count
from src.ui.styles import apply_custom_css
from src.ui.tab_dashboard import render_dashboard_tab
from src.ui.tab_expenses import render_expenses_tab
from src.ui.tab_budgets import render_budgets_tab
from src.ui.tab_analytics import render_analytics_tab
from src.ui.tab_data_tools import render_data_tools_tab
from src.ui.tab_sample_data import render_sample_data_tab


def main():
    # 1. Configure Streamlit Page
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Custom CSS
    apply_custom_css()

    # 3. Ensure SQLite Database is Initialized
    init_db()

    # 4. Render Sidebar Branding & Fast Status
    with st.sidebar:
        st.markdown(f"## {APP_ICON} **ExpenseTracker**")
        st.caption(APP_SUBTITLE)
        st.markdown("---")

        stats = get_expenses_stats_count()
        st.markdown("##### 📌 System Status")
        st.write(f"• **Database:** SQLite (`data/expenses.db`)")
        st.write(f"• **Total Records:** `{stats['total']:,}`")
        st.write(f"• **User Records:** `{stats['user']:,}`")
        st.write(f"• **Sample Data:** `{stats['synthetic']:,}`")
        st.write(f"• **Currency:** `Indian Rupee (₹)`")
        st.write(f"• **Date:** `{date.today().strftime('%d %b %Y')}`")

        st.markdown("---")
        st.markdown("##### 💡 Quick Guide")
        st.markdown(
            "1. **Dashboard:** High-level KPIs & trends.\n"
            "2. **Expenses:** Add, edit, or delete transactions.\n"
            "3. **Budgets:** Set limits & monitor thresholds.\n"
            "4. **Analytics:** Behavioral spending patterns.\n"
            "5. **Data Tools:** CSV upload & download.\n"
            "6. **Sample Data:** Seed demo transactions."
        )

        st.markdown("---")
        st.caption("Developed with Python, Pandas, Streamlit & Plotly.")

    # 5. Header Title
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.caption(APP_SUBTITLE)

    # 6. Primary Tabs Navigation
    t1, t2, t3, t4, t5, t6 = st.tabs([
        "📊 Dashboard Overview",
        "📝 Manage Expenses",
        "🎯 Budget Management",
        "📈 Spending Analytics",
        "💾 Data Import & Export",
        "🧪 Sample Data Management"
    ])

    with t1:
        render_dashboard_tab()

    with t2:
        render_expenses_tab()

    with t3:
        render_budgets_tab()

    with t4:
        render_analytics_tab()

    with t5:
        render_data_tools_tab()

    with t6:
        render_sample_data_tab()


if __name__ == "__main__":
    main()
