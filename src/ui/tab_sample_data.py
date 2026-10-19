"""
Sample Data Management View.
Allows users to generate reproducible synthetic transactions for demonstrations,
inspect data origin distribution, and safely purge sample records without affecting user data.
"""

import streamlit as st
from src.services.synthetic_data_service import seed_synthetic_data_into_db
from src.services.expense_service import get_expenses_stats_count, purge_synthetic_expenses, get_filtered_expenses
from src.utils.formatters import format_currency


def render_sample_data_tab():
    """Renders the Synthetic Sample Data Management tab."""
    st.markdown("### 🧪 Synthetic Sample Data Management")
    st.caption("Generate realistic sample data spanning 5 months to demonstrate analytics, charts, and budget alerts.")

    stats = get_expenses_stats_count()

    # Data Source Metrics
    s1, s2, s3 = st.columns(3)
    s1.metric("Total Expenses in SQLite", f"{stats['total']:,}")
    s2.metric("👤 Genuine User Entries", f"{stats['user']:,}")
    s3.metric("🧪 Synthetic Sample Records", f"{stats['synthetic']:,}")

    st.markdown("---")

    col_gen, col_purge = st.columns(2)

    # 1. GENERATE
    with col_gen:
        st.markdown("##### 📥 Generate Realistic Demonstration Data")
        st.write(
            "Creates approximately 150–200 realistic Indian household transactions (Rent, UPI groceries, "
            "utility bills, metro fares, dining) with a fixed seed (`seed=42`)."
        )
        months_back = st.slider("Span of History (Months)", min_value=2, max_value=8, value=5)

        if st.button("✨ Generate & Load Sample Data", type="primary", use_container_width=True):
            if stats["synthetic"] > 0:
                st.warning("⚠️ Synthetic records already exist in your database. Purge existing sample data first if you wish to re-seed.")
            else:
                with st.spinner("Generating reproducible financial time-series data..."):
                    inserted = seed_synthetic_data_into_db(months_back=months_back, seed=42)
                    st.success(f"🎉 Successfully inserted {inserted:,} synthetic transactions!")
                    st.rerun()

    # 2. PURGE
    with col_purge:
        st.markdown("##### 🗑️ Purge Sample Data")
        st.write(
            "Permanently removes all records marked with `is_synthetic = 1`. "
            "**All genuine user-entered transactions are 100% preserved.**"
        )
        st.write("")  # Spacing
        st.write("")

        if stats["synthetic"] == 0:
            st.info("No synthetic records currently exist in the database.")
        else:
            confirm_purge = st.checkbox("Confirm deletion of all sample records", key="confirm_purge_synthetic")
            if st.button("🧹 Purge All Sample Data", type="secondary", disabled=not confirm_purge, use_container_width=True):
                deleted = purge_synthetic_expenses()
                st.success(f"🧹 Cleaned up {deleted:,} synthetic sample records.")
                st.rerun()

    st.markdown("---")

    # Preview of sample records
    st.markdown("##### 🔍 Recent Sample Records in Database")
    sample_df = get_filtered_expenses(include_synthetic=True)
    sample_only_df = sample_df[sample_df["is_synthetic"] == 1]

    if sample_only_df.empty:
        st.caption("No sample records currently loaded.")
    else:
        st.dataframe(
            sample_only_df[["id", "date", "category", "amount", "payment_method", "description"]].head(15),
            use_container_width=True,
            hide_index=True
        )
