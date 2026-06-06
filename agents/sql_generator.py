"""
Step 3 — Generate SQL using Ollama or OpenRouter.
"""

from __future__ import annotations

import re
from pathlib import Path

from agents.llm_client import (
    DEFAULT_OLLAMA_MODEL,
    LLMConfig,
    chat,
    check_provider,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPT_PATH = PROJECT_ROOT / "prompts" / "sql_prompt.txt"


def _load_prompt_template() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Missing prompt file: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_sql(raw: str) -> str:
    """Pull SQL from model output (strip fences and chatter)."""
    text = raw.strip()
    text = re.sub(r"^```(?:sql)?\s*", "", text, flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"\s*```$", "", text)
    match = re.search(r"((?:WITH\b[\s\S]*?)?SELECT\b[\s\S]*)", text, re.IGNORECASE)
    if match:
        text = match.group(1)
    return text.strip().rstrip(";")


def generate_sql(
    question: str,
    schema: str,
    llm: LLMConfig | None = None,
) -> str:
    """
    Agent loop Step 3: Generate SQL from natural language + schema.
    """
    config = llm or LLMConfig()
    template = _load_prompt_template()
    prompt = template.format(schema=schema, question=question.strip())
    raw = chat(prompt, config, temperature=0.1, timeout=90)
    sql = _extract_sql(raw)
    if not sql:
        raise ValueError(f"Model returned no SQL. Raw response:\n{raw[:400]}")
    return sql


def check_ollama_available(model: str | None = None) -> tuple[bool, str]:
    """Backward-compatible Ollama check."""
    return check_provider(
        LLMConfig(provider="ollama", model=model or DEFAULT_OLLAMA_MODEL)
    )
