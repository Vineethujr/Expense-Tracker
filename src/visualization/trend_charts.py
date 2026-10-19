"""
Trend Visualizations using Plotly.
Generates monthly trend charts with MoM flags, daily timeline with rolling average,
and side-by-side MoM category comparisons.
"""

import plotly.graph_objects as go
import pandas as pd
from src.config import CURRENCY_SYMBOL
from src.utils.formatters import format_month


def create_monthly_trend_chart(monthly_df: pd.DataFrame) -> go.Figure:
    """
    Renders a combined Bar and Line chart showing monthly spending progression
    and percentage change indicators.
    """
    if monthly_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No monthly trend data available", showarrow=False)
        fig.update_layout(height=350)
        return fig

    labels = [format_month(m) for m in monthly_df["month"]]

    fig = go.Figure()

    # Bar chart for monthly total
    fig.add_trace(go.Bar(
        x=labels,
        y=monthly_df["total_spend"],
        name="Monthly Spending",
        marker_color="#2a9d8f",
        text=[f"{CURRENCY_SYMBOL} {val:,.0f}" for val in monthly_df["total_spend"]],
        textposition="auto",
        hovertemplate="<b>%{x}</b><br>Spend: " + CURRENCY_SYMBOL + " %{y:,.2f}<extra></extra>"
    ))

    # Line chart overlay connecting months
    fig.add_trace(go.Scatter(
        x=labels,
        y=monthly_df["total_spend"],
        name="Trend Line",
        mode="lines+markers",
        line=dict(color="#e76f51", width=3),
        marker=dict(size=8, color="#e76f51"),
        hoverinfo="skip"
    ))

    fig.update_layout(
        title=dict(text="<b>Monthly Spending Progression</b>", font=dict(size=16)),
        xaxis=dict(title="Month"),
        yaxis=dict(title="Total Outflow (₹)", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(t=60, b=40, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_daily_trend_chart(daily_df: pd.DataFrame) -> go.Figure:
    """
    Renders daily spending timeline with a 7-day rolling average smoother.
    """
    if daily_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No daily trend data available", showarrow=False)
        fig.update_layout(height=350)
        return fig

    fig = go.Figure()

    # Daily bars
    fig.add_trace(go.Bar(
        x=daily_df["date"],
        y=daily_df["daily_spend"],
        name="Daily Spend",
        marker_color="rgba(69, 123, 157, 0.45)",
        hovertemplate="<b>%{x}</b><br>Daily: " + CURRENCY_SYMBOL + " %{y:,.2f}<extra></extra>"
    ))

    # 7-day rolling average line
    fig.add_trace(go.Scatter(
        x=daily_df["date"],
        y=daily_df["rolling_7d_avg"],
        name="7-Day Moving Average",
        mode="lines",
        line=dict(color="#e63946", width=2.5),
        hovertemplate="7-Day Avg: " + CURRENCY_SYMBOL + " %{y:,.2f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text="<b>Daily Spending Timeline with 7-Day Moving Average</b>", font=dict(size=16)),
        xaxis=dict(title="Date", showgrid=False),
        yaxis=dict(title="Amount (₹)", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(t=60, b=40, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_mom_comparison_chart(pivot_df: pd.DataFrame, m1: str, m2: str) -> go.Figure:
    """
    Renders a clustered bar chart comparing category spend between two selected months.
    """
    if pivot_df.empty or m1 not in pivot_df.columns or m2 not in pivot_df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Select two months with recorded expenses to compare", showarrow=False)
        fig.update_layout(height=350)
        return fig

    sub_df = pivot_df[["category", m1, m2]].copy()
    sub_df["max_val"] = sub_df[[m1, m2]].max(axis=1)
    sub_df = sub_df[sub_df["max_val"] > 0].sort_values("max_val", ascending=False).head(8)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sub_df["category"],
        y=sub_df[m1],
        name=format_month(m1),
        marker_color="#457b9d",
        hovertemplate=f"<b>%{{x}}</b><br>{format_month(m1)}: {CURRENCY_SYMBOL} %{{y:,.2f}}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=sub_df["category"],
        y=sub_df[m2],
        name=format_month(m2),
        marker_color="#f4a261",
        hovertemplate=f"<b>%{{x}}</b><br>{format_month(m2)}: {CURRENCY_SYMBOL} %{{y:,.2f}}<extra></extra>"
    ))

    fig.update_layout(
        barmode="group",
        title=dict(text=f"<b>Category Comparison: {format_month(m1)} vs {format_month(m2)}</b>", font=dict(size=16)),
        xaxis=dict(title="", tickangle=-30),
        yaxis=dict(title="Spend (₹)", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(t=60, b=80, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
