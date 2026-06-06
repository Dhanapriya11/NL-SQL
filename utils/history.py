"""
Query history — session persistence and export helpers.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st


def init_session() -> None:
    """Initialize session state keys for chat + query log."""
    defaults: dict[str, Any] = {
        "chat_history": [],
        "query_log": [],  # structured log for hackathon demo / CSV export
        "db_ready": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val if key != "db_ready" else False


def add_user_message(question: str) -> None:
    st.session_state.chat_history.append({"role": "user", "content": question})


def add_assistant_message(payload: dict) -> None:
    st.session_state.chat_history.append({"role": "assistant", **payload})
    # Structured query log (one row per Q&A)
    if payload.get("sql") or payload.get("error"):
        st.session_state.query_log.append(
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "question": _last_user_question(),
                "sql": payload.get("sql") or "",
                "rows": len(payload["df"]) if payload.get("df") is not None else 0,
                "insight": payload.get("insight") or "",
                "status": "error" if payload.get("error") else "success",
                "error": payload.get("error") or "",
            }
        )


def _last_user_question() -> str:
    for item in reversed(st.session_state.chat_history):
        if item.get("role") == "user":
            return item.get("content", "")
    return ""


def clear_history() -> None:
    st.session_state.chat_history = []
    st.session_state.query_log = []


def get_query_log_df() -> pd.DataFrame:
    if not st.session_state.query_log:
        return pd.DataFrame(
            columns=["timestamp", "question", "sql", "rows", "insight", "status", "error"]
        )
    return pd.DataFrame(st.session_state.query_log)


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")
