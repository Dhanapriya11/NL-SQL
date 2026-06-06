"""
Step 6 & 7 — Analyze results and recommend visualization.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from agents.llm_client import LLMConfig, chat
from utils.charts import infer_chart_from_dataframe

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "insight_prompt.txt"


def _load_prompt_template() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _parse_insight_json(text: str) -> dict:
    cleaned = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse insight JSON:\n{text[:500]}")


def _rule_based_insight(question: str, df: pd.DataFrame) -> dict:
    chart = infer_chart_from_dataframe(df)
    if df.empty:
        insight = "The query returned no rows. Try broadening filters or check table names."
    elif len(df) == 1 and len(df.columns) == 1:
        val = df.iloc[0, 0]
        insight = f"Answer for '{question}': {val}."
    else:
        insight = (
            f"Found {len(df)} row(s) across {len(df.columns)} column(s) "
            f"relevant to: {question}."
        )
    return {"insight": insight, **chart}


def generate_insights(
    question: str,
    sql: str,
    df: pd.DataFrame,
    llm: LLMConfig | None = None,
    use_llm: bool = True,
) -> dict:
    """Agent loop Steps 6–7: Analyze result + recommend chart."""
    if not use_llm:
        return _rule_based_insight(question, df)

    config = llm or LLMConfig()
    sample = df.head(10).to_dict(orient="records")
    template = _load_prompt_template()
    prompt = template.format(
        question=question,
        sql=sql,
        columns=list(df.columns),
        row_count=len(df),
        sample_rows=json.dumps(sample, default=str),
    )

    try:
        raw = chat(prompt, config, temperature=0.3, timeout=60)
        result = _parse_insight_json(raw)
        if result.get("chart_type") in (None, "null", ""):
            result["chart_type"] = "none"
        return result
    except Exception:
        return _rule_based_insight(question, df)
