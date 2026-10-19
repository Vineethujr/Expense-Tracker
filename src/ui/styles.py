"""
Streamlit Custom CSS Styling Module.
Provides sleek, modern UI aesthetics, custom KPI cards, and responsive alert styling.
"""

CUSTOM_CSS = """
<style>
/* Modern typography and general aesthetics */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Custom KPI Metric Cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    margin-bottom: 12px;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08);
}
.kpi-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 4px;
}
.kpi-subtitle {
    font-size: 0.8rem;
    color: #9ca3af;
}

/* Financial Insight Cards */
.insight-box {
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 14px;
    border-left: 5px solid;
    background-color: #ffffff;
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
}
.insight-critical {
    border-left-color: #ef4444;
    background-color: #fef2f2;
}
.insight-warning {
    border-left-color: #f59e0b;
    background-color: #fffbeb;
}
.insight-info {
    border-left-color: #3b82f6;
    background-color: #eff6ff;
}
.insight-success {
    border-left-color: #10b981;
    background-color: #f0fdf4;
}
.insight-title {
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 6px;
    color: #1f2937;
}
.insight-msg {
    font-size: 0.88rem;
    color: #374151;
    line-height: 1.45;
    margin-bottom: 8px;
}
.insight-tip {
    font-size: 0.82rem;
    font-weight: 500;
    color: #4b5563;
    font-style: italic;
    background: rgba(255, 255, 255, 0.6);
    padding: 6px 10px;
    border-radius: 6px;
    display: inline-block;
}

/* Sample data tag */
.synthetic-tag {
    background-color: #fef3c7;
    color: #92400e;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid #fde68a;
}
</style>
"""


def apply_custom_css():
    """Injects custom CSS styles into the Streamlit session."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
