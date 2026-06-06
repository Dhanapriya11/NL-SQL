"""
Plotly chart helpers — auto-select visualization from agent recommendation.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px


def create_chart(
    df: pd.DataFrame,
    chart_type: str | None,
    x_col: str | None,
    y_col: str | None,
    title: str | None,
):
    """
    Build a Plotly figure when chart_type and columns are valid.
    Returns None if a chart is not appropriate.
    """
    if not chart_type or chart_type == "none" or df.empty:
        return None
    if not x_col or not y_col:
        return None
    if x_col not in df.columns or y_col not in df.columns:
        return None

    palette = ["#6366f1", "#8b5cf6", "#14b8a6", "#f59e0b", "#ec4899"]
    title = title or "Query visualization"

    builders = {
        "bar": lambda: px.bar(df, x=x_col, y=y_col, title=title, color_discrete_sequence=palette),
        "line": lambda: px.line(
            df, x=x_col, y=y_col, title=title, markers=True, color_discrete_sequence=["#6366f1"]
        ),
        "pie": lambda: px.pie(df, names=x_col, values=y_col, title=title, color_discrete_sequence=palette),
        "scatter": lambda: px.scatter(
            df, x=x_col, y=y_col, title=title, color_discrete_sequence=["#14b8a6"]
        ),
    }
    builder = builders.get(chart_type.lower())
    if not builder:
        return None

    fig = builder()
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f8fafc",
        font_color="#334155",
        title_font_color="#4f46e5",
        title_font_size=15,
        xaxis=dict(gridcolor="#e2e8f0"),
        yaxis=dict(gridcolor="#e2e8f0"),
        margin=dict(l=48, r=24, t=56, b=48),
        height=400,
    )
    return fig


def infer_chart_from_dataframe(df: pd.DataFrame) -> dict:
    """
    Rule-based fallback when the LLM does not return chart metadata.
    """
    if df.empty or len(df.columns) < 2:
        return {"chart_type": "none", "chart_x": None, "chart_y": None, "chart_title": None}

    cols = list(df.columns)
    numeric = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
    non_numeric = [c for c in cols if c not in numeric]

    if not numeric:
        return {"chart_type": "none", "chart_x": None, "chart_y": None, "chart_title": None}

    x_col = non_numeric[0] if non_numeric else cols[0]
    y_col = numeric[0]

    # Heuristic: month/year strings → line chart
    sample = str(df[x_col].iloc[0]) if len(df) else ""
    if non_numeric and ("-" in sample and len(sample) >= 7):
        return {
            "chart_type": "line",
            "chart_x": x_col,
            "chart_y": y_col,
            "chart_title": f"{y_col} over {x_col}",
        }

    if len(df) <= 8 and non_numeric:
        return {
            "chart_type": "bar",
            "chart_x": x_col,
            "chart_y": y_col,
            "chart_title": f"{y_col} by {x_col}",
        }

    return {
        "chart_type": "bar",
        "chart_x": x_col,
        "chart_y": y_col,
        "chart_title": f"{y_col} by {x_col}",
    }
