"""
InsightSQL — NL-to-SQL Analytics Agent (Hackathon submission).

Stack: Python · Streamlit · SQLite · OpenRouter / Ollama · Pandas · Plotly
"""

from __future__ import annotations

import os
import sys
import uuid

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

if sys.platform == "win32":
    os.environ.setdefault("PYTHONUTF8", "1")

import streamlit as st

from agents.agent_loop import run_agent_loop
from agents.llm_client import (
    DEFAULT_OPENROUTER_MODEL,
    LLMConfig,
    OPENROUTER_MODELS,
    check_provider,
)
from config.constants import APP_NAME, SAMPLE_QUESTIONS
from ui.components import (
    render_assistant_block,
    render_hero,
    render_kpis,
    render_query_history_sidebar,
    render_user_bubble,
    run_with_loading,
)
from ui.styles import CUSTOM_CSS
from utils.charts import create_chart
from utils.database import get_table_info, init_database, kpi_metrics
from utils.history import (
    add_assistant_message,
    add_user_message,
    clear_history,
    get_query_log_df,
    init_session,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")

init_session()
if not st.session_state.db_ready:
    init_database(force=True)  # reload Tamil names + Rs data
    st.session_state.db_ready = True


def _build_llm_config() -> tuple[LLMConfig, bool]:
    """Read sidebar settings and return LLM config + is_openrouter flag."""
    provider = st.session_state.get("provider_choice", "OpenRouter (recommended)")
    use_openrouter = provider.startswith("OpenRouter")

    if use_openrouter:
        api_key = st.session_state.get("or_api_key", OPENROUTER_KEY)
        model = st.session_state.get("or_model", DEFAULT_OPENROUTER_MODEL)
        return LLMConfig(provider="openrouter", model=model, api_key=api_key), True

    model = st.session_state.get("ollama_model", OLLAMA_MODEL)
    return LLMConfig(provider="ollama", model=model), False


def _render_sidebar() -> tuple[LLMConfig, bool, bool, bool]:
    with st.sidebar:
        st.markdown("## InsightSQL")
        st.caption("NL → SQL Analytics Agent")

        provider = st.radio(
            "AI provider",
            ["OpenRouter (recommended)", "Ollama (local)"],
            key="provider_choice",
            help="OpenRouter is faster for hackathon demos",
        )
        use_openrouter = provider.startswith("OpenRouter")

        if use_openrouter:
            st.text_input(
                "OpenRouter API Key",
                type="password",
                value=OPENROUTER_KEY,
                placeholder="sk-or-v1-...",
                key="or_api_key",
                help="https://openrouter.ai/keys",
            )
            default_or = DEFAULT_OPENROUTER_MODEL
            idx = OPENROUTER_MODELS.index(default_or) if default_or in OPENROUTER_MODELS else 0
            st.selectbox("Model", OPENROUTER_MODELS, index=idx, key="or_model")
        else:
            st.text_input("Ollama model", value=OLLAMA_MODEL, key="ollama_model")
            st.caption("`ollama serve` then `ollama pull llama3`")

        llm_config, _ = _build_llm_config()
        ok, status_msg = check_provider(llm_config)
        if ok:
            st.success(status_msg)
        else:
            st.warning(status_msg)

        use_llm_insights = st.checkbox("AI business insights", value=True, key="llm_insights")

        st.markdown("---")
        render_query_history_sidebar(get_query_log_df())

        st.markdown("---")
        st.markdown("### Sample questions")
        for q in SAMPLE_QUESTIONS:
            if st.button(q, key=f"sug_{q}", use_container_width=True):
                st.session_state["prefill"] = q

        st.markdown("---")
        st.markdown("### Schema explorer")
        for tname, tdata in get_table_info().items():
            with st.expander(f"{tname} · {tdata['count']} rows"):
                for col in tdata["columns"]:
                    pk = " [PK]" if col[5] else ""
                    st.markdown(f"`{col[1]}` *{col[2]}*{pk}")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Clear", use_container_width=True):
                clear_history()
                st.rerun()
        with c2:
            if st.button("Rebuild DB", use_container_width=True):
                init_database(force=True)
                st.toast("Database rebuilt with Tamil names & Rs pricing")
                st.rerun()

    llm_config, use_or = _build_llm_config()
    ok, _ = check_provider(llm_config)
    return llm_config, use_or, ok, use_llm_insights


# ── Main layout ───────────────────────────────────────────────────────────────
llm_config, use_openrouter, provider_ok, use_llm_insights = _render_sidebar()

render_hero()
render_kpis(kpi_metrics())

st.markdown("### Conversation")

if not st.session_state.chat_history:
    st.info(
        "Try a sample question from the sidebar — e.g. "
        "**Show total sales by month** or **List employees named Priya or Dhana**"
    )

for idx, item in enumerate(st.session_state.chat_history):
    if item["role"] == "user":
        render_user_bubble(item["content"])
    else:
        with st.container():
            render_assistant_block(item)

st.markdown("---")
prefill = st.session_state.pop("prefill", "")
col_q, col_btn = st.columns([5, 1])
with col_q:
    question = st.text_input(
        "Ask a question",
        value=prefill,
        placeholder="e.g. Which product has the highest sales?",
        label_visibility="collapsed",
    )
with col_btn:
    submit = st.button("Analyze", type="primary", use_container_width=True)

if submit and question.strip():
    if not provider_ok:
        if use_openrouter:
            st.error("Add your OpenRouter API key in the sidebar to continue.")
        else:
            st.error("Start Ollama locally: ollama serve && ollama pull llama3")
    else:
        add_user_message(question.strip())
        query_id = uuid.uuid4().hex[:8]

        def _run():
            return run_agent_loop(
                question.strip(),
                llm=llm_config,
                use_llm_insights=use_llm_insights,
            )

        agent_result = run_with_loading(
            "InsightSQL agent is working on your question…",
            _run,
        )

        chart = None
        if not agent_result.error and not agent_result.dataframe.empty:
            chart = create_chart(
                agent_result.dataframe,
                agent_result.chart_type,
                agent_result.chart_x,
                agent_result.chart_y,
                agent_result.chart_title,
            )

        add_assistant_message(
            {
                "content": agent_result.insight or "Query completed.",
                "sql": agent_result.sql,
                "df": agent_result.dataframe,
                "insight": agent_result.insight,
                "chart": chart,
                "error": agent_result.error,
                "query_id": query_id,
                "steps": [
                    {
                        "number": s.number,
                        "name": s.name,
                        "status": s.status,
                        "detail": s.detail,
                    }
                    for s in agent_result.steps
                ],
            }
        )
        st.rerun()
