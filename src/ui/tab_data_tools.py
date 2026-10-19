"""
Data Import and Export View.
Provides CSV validation, duplicate detection, batch ingestion,
filtered CSV downloads, and starter template generation.
"""

import streamlit as st
import pandas as pd
from datetime import date
from src.config import ALL_CATEGORIES, PAYMENT_METHODS
from src.validation.csv_validator import validate_and_clean_csv
from src.services.expense_service import bulk_add_expenses, get_all_expenses, get_filtered_expenses
from src.services.data_io_service import export_expenses_to_csv, generate_csv_template
from src.utils.formatters import format_currency


def render_data_tools_tab():
    """Renders the Data Import & Export tab."""
    st.markdown("### 💾 Data Import & Export Tools")

    import_tab, export_tab, template_tab = st.tabs(["📥 Import from CSV", "📤 Export to CSV", "📄 Download Template"])

    # --- 1. IMPORT CSV ---
    with import_tab:
        st.markdown("##### Upload Expenses via CSV")
        st.caption("Upload your bank or personal spending CSV. Supported columns: Date, Category, Amount, Payment Method, Description.")

        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                raw_df = pd.read_csv(uploaded_file)
                st.write(f"📁 **File Uploaded:** `{uploaded_file.name}` ({len(raw_df)} total rows)")

                existing_df = get_all_expenses()
                cleaned_df, report = validate_and_clean_csv(raw_df, existing_df=existing_df)

                # Summary Metrics
                v1, v2, v3, v4 = st.columns(4)
                v1.metric("Total Rows in File", report["total_rows"])
                v2.metric("Valid Rows Parsed", report["valid_rows"])
                v3.metric("Invalid / Dropped Rows", report["dropped_rows"])
                v4.metric("Potential Duplicates", report["duplicate_rows"])

                if report["warnings"]:
                    for w in report["warnings"]:
                        st.warning(f"⚠️ {w}")

                if report["errors"]:
                    for e in report["errors"]:
                        st.error(f"❌ {e}")

                if not cleaned_df.empty:
                    st.markdown("##### Preview of Validated Rows Ready for Import")
                    st.dataframe(cleaned_df.head(10), use_container_width=True)

                    skip_existing = st.checkbox("Skip rows that already exist in your database", value=True)

                    if st.button("🚀 Commit Validated Rows to Database", type="primary", use_container_width=True):
                        final_to_insert = cleaned_df.copy()
                        if skip_existing and "is_existing_duplicate" in final_to_insert.columns:
                            final_to_insert = final_to_insert[~final_to_insert["is_existing_duplicate"]]

                        if final_to_insert.empty:
                            st.warning("All records were filtered out as duplicates. Nothing to insert.")
                        else:
                            inserted_count = bulk_add_expenses(final_to_insert)
                            st.success(f"🎉 Successfully imported {inserted_count:,} expenses into SQLite!")
                            st.rerun()

            except Exception as ex:
                st.error(f"Failed to read CSV: {str(ex)}")

    # --- 2. EXPORT CSV ---
    with export_tab:
        st.markdown("##### Export Expense Records to CSV")
        st.caption("Filter transactions and download a clean CSV for external analysis or backup.")

        e_col1, e_col2 = st.columns(2)
        with e_col1:
            export_date_range = st.date_input(
                "Select Export Date Range",
                value=(date(date.today().year, 1, 1), date.today()),
                key="exp_export_range"
            )
        with e_col2:
            export_cats = st.multiselect("Filter Export Categories (Optional)", options=ALL_CATEGORIES, default=[])

        inc_sample = st.checkbox("Include Synthetic Sample Data in Export", value=True, key="exp_inc_sample")

        start_d = str(export_date_range[0]) if isinstance(export_date_range, (tuple, list)) and len(export_date_range) > 0 else None
        end_d = str(export_date_range[1]) if isinstance(export_date_range, (tuple, list)) and len(export_date_range) > 1 else None

        export_df = get_filtered_expenses(
            start_date=start_d,
            end_date=end_d,
            categories=export_cats if export_cats else None,
            include_synthetic=inc_sample
        )

        st.info(f"Filtered {len(export_df):,} records for export (Total Value: {format_currency(export_df['amount'].sum() if not export_df.empty else 0)}).")

        csv_data = export_expenses_to_csv(export_df)
        today_slug = date.today().strftime("%Y%m%d")

        st.download_button(
            label="📥 Download Export CSV",
            data=csv_data,
            file_name=f"expenses_export_{today_slug}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # --- 3. CSV TEMPLATE ---
    with template_tab:
        st.markdown("##### Download Starter CSV Template")
        st.caption("Use this sample CSV format to populate and import your personal records smoothly.")

        template_csv = generate_csv_template()
        st.download_button(
            label="📄 Download Sample CSV Template",
            data=template_csv,
            file_name="expense_import_template.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.code("""
date,category,amount,payment_method,description
2026-10-15,Food & Groceries,1450.00,UPI,Weekly supermarket grocery shopping
2026-10-14,Utilities & Bills,2200.00,Net Banking,Monthly electricity bill payment
2026-10-12,Transportation,350.00,UPI,Fuel refill for two-wheeler
2026-10-10,Dining & Takeout,650.00,Credit Card,Dinner with colleagues
        """, language="csv")
