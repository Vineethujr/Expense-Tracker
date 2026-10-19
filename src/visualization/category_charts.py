"""
Category Visualizations using Plotly.
Generates interactive Donut charts and comparative Bar charts for category breakdowns.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from src.config import CATEGORY_COLORS, CURRENCY_SYMBOL


def create_category_donut_chart(category_summary_df: pd.DataFrame) -> go.Figure:
    """
    Renders an interactive Donut chart showing category percentage and absolute spend.
    """
    if category_summary_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No expense data available to display chart",
            showarrow=False,
            font=dict(size=14, color="#6c757d")
        )
        fig.update_layout(height=350, margin=dict(t=20, b=20, l=20, r=20))
        return fig

    colors = [CATEGORY_COLORS.get(cat, "#8d99ae") for cat in category_summary_df["category"]]

    fig = go.Figure(data=[
        go.Pie(
            labels=category_summary_df["category"],
            values=category_summary_df["total_spend"],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Spend: " + CURRENCY_SYMBOL + " %{value:,.2f}<br>Share: %{percent}<extra></extra>",
            textposition="inside",
        )
    ])

    total_amount = category_summary_df["total_spend"].sum()
    fig.update_layout(
        title=dict(text="<b>Expense Distribution by Category</b>", font=dict(size=16)),
        annotations=[
            dict(
                text=f"<b>Total</b><br>{CURRENCY_SYMBOL} {total_amount:,.0f}",
                x=0.5, y=0.5,
                font=dict(size=14, color="#1d3557"),
                showarrow=False
            )
        ],
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=420,
        margin=dict(t=50, b=60, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_category_bar_chart(category_summary_df: pd.DataFrame) -> go.Figure:
    """
    Renders a horizontal bar chart ranking categories by expenditure.
    """
    if category_summary_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig

    # Sort ascending for horizontal bar chart (highest at top)
    sorted_df = category_summary_df.sort_values("total_spend", ascending=True)
    colors = [CATEGORY_COLORS.get(cat, "#457b9d") for cat in sorted_df["category"]]

    fig = go.Figure(data=[
        go.Bar(
            y=sorted_df["category"],
            x=sorted_df["total_spend"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"{CURRENCY_SYMBOL} {v:,.0f}" for v in sorted_df["total_spend"]],
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Spend: " + CURRENCY_SYMBOL + " %{x:,.2f}<extra></extra>"
        )
    ])

    fig.update_layout(
        title=dict(text="<b>Category Ranking by Total Outflow</b>", font=dict(size=16)),
        xaxis=dict(title="Total Amount (₹)", showgrid=True, gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(title=""),
        height=420,
        margin=dict(t=50, b=40, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
