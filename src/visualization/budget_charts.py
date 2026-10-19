"""
Budget and Lifestyle Allocation Visualizations using Plotly.
Generates budget progress bars with tiered color alerts and 50-30-20 lifestyle distribution charts.
"""

import plotly.graph_objects as go
from src.config import CURRENCY_SYMBOL
from src.utils.formatters import format_currency


def create_budget_utilization_chart(budget_status: dict) -> go.Figure:
    """
    Renders horizontal progress meters for monthly and category budgets.
    Color codes:
      - Green: < 80% (On track)
      - Amber / Orange: 80% - 99.9% (Warning threshold)
      - Red: >= 100% (Over budget alert)
    """
    category_budgets = budget_status.get("category_budgets", [])
    overall_allocated = budget_status.get("overall_allocated", 0.0)

    if overall_allocated == 0 and not category_budgets:
        fig = go.Figure()
        fig.add_annotation(
            text="No budgets configured for this month. Set budget targets in the Budget Management tab.",
            showarrow=False,
            font=dict(size=13, color="#6c757d")
        )
        fig.update_layout(height=280)
        return fig

    labels = []
    utilizations = []
    colors = []
    text_labels = []

    # Include overall if set
    if overall_allocated > 0:
        overall_spent = budget_status.get("total_spent", 0.0)
        overall_util = budget_status.get("overall_utilization_pct", 0.0)
        labels.append("<b>OVERALL MONTHLY</b>")
        utilizations.append(min(overall_util, 130.0))  # Cap bar at 130% for visual sanity
        text_labels.append(f"{overall_util:.1f}% ({format_currency(overall_spent)} / {format_currency(overall_allocated)})")

        if overall_util >= 100.0:
            colors.append("#e63946")  # Red
        elif overall_util >= 80.0:
            colors.append("#f4a261")  # Orange
        else:
            colors.append("#2a9d8f")  # Green

    # Category budgets
    for cb in category_budgets:
        labels.append(cb["category"])
        utilizations.append(min(cb["utilization_pct"], 130.0))
        text_labels.append(f"{cb['utilization_pct']:.1f}% ({format_currency(cb['spent'])} / {format_currency(cb['allocated'])})")

        if cb["status"] == "exceeded":
            colors.append("#e63946")
        elif cb["status"] == "warning":
            colors.append("#f4a261")
        else:
            colors.append("#2a9d8f")

    # Reverse to have overall at the top
    labels.reverse()
    utilizations.reverse()
    colors.reverse()
    text_labels.reverse()

    fig = go.Figure(data=[
        go.Bar(
            y=labels,
            x=utilizations,
            orientation="h",
            marker=dict(color=colors),
            text=text_labels,
            textposition="auto",
            hovertemplate="<b>%{y}</b><br>Utilization: %{x:.1f}%<extra></extra>"
        )
    ])

    # Reference lines for 80% warning and 100% budget limit
    fig.add_vline(x=80, line_width=1.5, line_dash="dash", line_color="#f4a261", annotation_text="80% Warning", annotation_position="top")
    fig.add_vline(x=100, line_width=2, line_dash="solid", line_color="#e63946", annotation_text="100% Limit", annotation_position="top")

    fig.update_layout(
        title=dict(text="<b>Budget Utilization & Threshold Status</b>", font=dict(size=16)),
        xaxis=dict(title="Utilization Percentage (%)", range=[0, max(max(utilizations, default=100) + 15, 115)]),
        yaxis=dict(title=""),
        height=max(320, len(labels) * 50 + 100),
        margin=dict(t=60, b=40, l=120, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def create_essential_vs_discretionary_chart(patterns: dict) -> go.Figure:
    """
    Renders an interactive Donut chart comparing Essential Needs vs Discretionary Wants.
    """
    essential = patterns.get("essential_total", 0.0)
    discretionary = patterns.get("discretionary_total", 0.0)

    if essential == 0 and discretionary == 0:
        fig = go.Figure()
        fig.add_annotation(text="No spending records available", showarrow=False)
        fig.update_layout(height=300)
        return fig

    labels = ["Essential Needs (Housing, Food, Bills, Health)", "Discretionary Wants (Shopping, Dining, Leisure)"]
    values = [essential, discretionary]
    colors = ["#2a9d8f", "#e76f51"]

    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.55,
            marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>Amount: " + CURRENCY_SYMBOL + " %{value:,.2f}<br>Share: %{percent}<extra></extra>",
            textposition="inside",
        )
    ])

    fig.update_layout(
        title=dict(text="<b>Essential Needs vs Discretionary Wants</b>", font=dict(size=15)),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=360,
        margin=dict(t=50, b=50, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
