"""Reusable Streamlit UI components."""

from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st

from config.constants import APP_NAME, APP_TAGLINE, CURRENCY_LABEL
from utils.formatting import format_inr
from utils.history import dataframe_to_csv_bytes


def render_hero() -> None:
    st.markdown(
        f"""
<div class="brand-header">
  <div class="brand-badge">Hackathon Demo · NL-to-SQL Agent</div>
  <h1>{html.escape(APP_NAME)}</h1>
  <p>{html.escape(APP_TAGLINE)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_kpis(kpis: dict[str, float | int]) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"Total sales ({CURRENCY_LABEL})", format_inr(kpis["total_sales"]))
    c2.metric("Employees", f"{kpis['employees']:,}")
    c3.metric("Products", f"{kpis['products']:,}")
    c4.metric("Departments", f"{kpis['departments']:,}")


def render_agent_timeline(steps: list[dict]) -> None:
    with st.expander("Agent pipeline — 7 steps", expanded=False):
        st.markdown('<div class="step-timeline">', unsafe_allow_html=True)
        for step in steps:
            status = step.get("status", "pending")
            dot_class = (
                "dot-done" if status == "done"
                else "dot-error" if status == "error"
                else "dot-pending"
            )
            detail = html.escape(step.get("detail") or "")
            st.markdown(
                f'<div class="step-item">'
                f'<div class="step-dot {dot_class}">{step["number"]}</div>'
                f'<div><strong>{html.escape(step["name"])}</strong> '
                f'<span style="color:#64748b">— {status}</span>'
                f'{"<br><small>" + detail + "</small>" if detail else ""}'
                f"</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def render_assistant_block(item: dict) -> None:
    if item.get("steps"):
        render_agent_timeline(item["steps"])

    if item.get("error"):
        st.error(item["error"])
        _render_error_tips(item["error"])
        return

    if item.get("insight"):
        safe = html.escape(item["insight"])
        st.markdown(
            f'<div class="insight-card"><strong>Business insight</strong><br>{safe}</div>',
            unsafe_allow_html=True,
        )

    if item.get("sql"):
        st.markdown("**Generated SQL**")
        st.markdown(
            f'<div class="sql-block">{html.escape(item["sql"])}</div>',
            unsafe_allow_html=True,
        )
        st.code(item["sql"], language="sql")

    df = item.get("df")
    if df is not None and not df.empty:
        st.markdown("**Query results**")
        st.dataframe(df, use_container_width=True, hide_index=True)
        _render_download_button(df, item.get("query_id", "results"))

    if item.get("chart") is not None:
        st.plotly_chart(item["chart"], use_container_width=True)


def _render_download_button(df: pd.DataFrame, file_id: str) -> None:
    st.download_button(
        label="Download results as CSV",
        data=dataframe_to_csv_bytes(df),
        file_name=f"insightsql_{file_id}.csv",
        mime="text/csv",
        key=f"dl_{file_id}",
        use_container_width=True,
    )


def _render_error_tips(error: str) -> None:
    err = error.lower()
    with st.expander("Troubleshooting tips"):
        if "api key" in err or "openrouter" in err:
            st.markdown("- Add your **OpenRouter API key** in the sidebar")
            st.markdown("- Get a key at [openrouter.ai/keys](https://openrouter.ai/keys)")
        elif "ollama" in err or "timeout" in err:
            st.markdown("- Switch to **OpenRouter** in the sidebar (faster)")
            st.markdown("- Or run `ollama serve` and `ollama pull llama3`")
        elif "validation" in err or "select" in err:
            st.markdown("- Rephrase your question more specifically")
            st.markdown("- Check table names in the schema explorer")
        else:
            st.markdown("- Try a sample question from the sidebar")
            st.markdown("- Rebuild the database if data looks stale")


def render_user_bubble(content: str) -> None:
    safe = html.escape(content)
    st.markdown(
        f'<div class="user-bubble"><div class="bubble-label">You asked</div>{safe}</div>',
        unsafe_allow_html=True,
    )


def render_query_history_sidebar(log_df: pd.DataFrame) -> None:
    st.markdown("### Query history")
    if log_df.empty:
        st.caption("No queries yet. Ask a question to build history.")
        return
    for i, row in log_df.iloc[::-1].head(10).iterrows():
        icon = "✓" if row["status"] == "success" else "✗"
        q = row["question"][:50] + ("…" if len(row["question"]) > 50 else "")
        st.markdown(
            f'<div class="history-item">{icon} <strong>{html.escape(q)}</strong>'
            f'<br><small>{row["timestamp"]} · {row["rows"]} rows</small></div>',
            unsafe_allow_html=True,
        )
    st.download_button(
        "Export full history (CSV)",
        data=dataframe_to_csv_bytes(log_df),
        file_name="insightsql_query_history.csv",
        mime="text/csv",
        use_container_width=True,
        key="dl_history",
    )


def run_with_loading(message: str, func, *args, **kwargs) -> Any:
    """Wrap agent call with Streamlit status animation."""
    with st.status(message, expanded=True) as status:
        st.markdown('<span class="loading-pulse">Running agent pipeline…</span>', unsafe_allow_html=True)
        result = func(*args, **kwargs)
        if getattr(result, "error", None):
            status.update(label="Request failed", state="error")
        else:
            status.update(label="Analysis complete", state="complete")
        return result
