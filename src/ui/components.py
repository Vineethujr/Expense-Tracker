"""
Reusable Streamlit UI Components.
Implements modular cards, insight widgets, and empty state containers.
"""

import streamlit as st
from typing import Dict, Any


def render_kpi_card(title: str, value: str, subtitle: str = "", icon: str = "💰"):
    """Renders a styled KPI metric card."""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{icon} {title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-subtitle">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


def render_insight_card(insight: Dict[str, Any]):
    """Renders a color-coded financial insight card."""
    severity = insight.get("severity", "info")
    title = insight.get("title", "Financial Insight")
    msg = insight.get("message", "")
    tip = insight.get("actionable_tip", "")

    st.markdown(f"""
    <div class="insight-box insight-{severity}">
        <div class="insight-title">{title}</div>
        <div class="insight-msg">{msg}</div>
        <div class="insight-tip">💡 {tip}</div>
    </div>
    """, unsafe_allow_html=True)


def render_empty_state(title: str, message: str, help_text: str = None):
    """Renders a friendly onboarding empty state banner."""
    st.info(f"### {title}\n{message}")
    if help_text:
        st.caption(help_text)
