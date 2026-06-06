"""
Orchestrates the 7-step NL-to-SQL agent loop with structured error handling.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from agents.insight_generator import generate_insights
from agents.llm_client import LLMConfig
from agents.schema_reader import read_schema
from agents.sql_generator import generate_sql
from agents.sql_validator import SQLValidationError, validate_sql
from utils.database import execute_query


@dataclass
class AgentStep:
    number: int
    name: str
    status: str  # pending | running | done | error
    detail: str = ""


@dataclass
class AgentResult:
    question: str
    schema: str
    sql: str | None = None
    dataframe: pd.DataFrame = field(default_factory=pd.DataFrame)
    insight: str = ""
    chart_type: str | None = None
    chart_x: str | None = None
    chart_y: str | None = None
    chart_title: str | None = None
    steps: list[AgentStep] = field(default_factory=list)
    error: str | None = None


def _mark_error(steps: list[AgentStep], exc: Exception) -> None:
    for s in steps:
        if s.status in ("pending", "running"):
            s.status = "error"
            s.detail = str(exc)[:200]
            break


def _friendly_error(exc: Exception) -> str:
    msg = str(exc)
    lower = msg.lower()
    if "api key" in lower:
        return "OpenRouter API key missing. Add it in the sidebar."
    if "timeout" in lower:
        return "AI request timed out. Switch to OpenRouter or try a simpler question."
    if "connection" in lower and "ollama" in lower:
        return "Cannot connect to Ollama. Run: ollama serve"
    if isinstance(exc, SQLValidationError):
        return f"SQL blocked for security: {msg}"
    if "execution failed" in lower:
        return f"SQL ran but failed: {msg}"
    return msg


def run_agent_loop(
    question: str,
    llm: LLMConfig | None = None,
    use_llm_insights: bool = True,
) -> AgentResult:
    config = llm or LLMConfig()
    provider_label = "OpenRouter" if config.provider == "openrouter" else "Ollama"

    steps = [
        AgentStep(1, "Read database schema", "pending"),
        AgentStep(2, "Understand user question", "pending"),
        AgentStep(3, "Generate SQL", "pending"),
        AgentStep(4, "Validate SQL", "pending"),
        AgentStep(5, "Execute SQL", "pending"),
        AgentStep(6, "Analyze result", "pending"),
        AgentStep(7, "Recommend visualization", "pending"),
    ]
    result = AgentResult(question=question, schema="", steps=steps)

    try:
        steps[0].status = "running"
        schema = read_schema()
        result.schema = schema
        steps[0].status = "done"
        steps[0].detail = f"{schema.count('TABLE')} tables (departments, employees, products, sales)"

        steps[1].status = "done"
        steps[1].detail = question[:100] + ("…" if len(question) > 100 else "")

        steps[2].status = "running"
        sql_raw = generate_sql(question, schema, llm=config)
        steps[2].status = "done"
        steps[2].detail = f"Generated via {provider_label} ({config.model})"

        steps[3].status = "running"
        sql = validate_sql(sql_raw)
        result.sql = sql
        steps[3].status = "done"
        steps[3].detail = "Read-only SELECT validated"

        steps[4].status = "running"
        df, exec_err = execute_query(sql)
        if exec_err:
            raise RuntimeError(exec_err)
        result.dataframe = df
        steps[4].status = "done"
        steps[4].detail = f"{len(df)} row(s) · amounts in Rs"

        steps[5].status = "running"
        steps[6].status = "running"
        insights = generate_insights(
            question, sql, df, llm=config, use_llm=use_llm_insights
        )
        result.insight = insights.get("insight", "")
        result.chart_type = insights.get("chart_type")
        result.chart_x = insights.get("chart_x")
        result.chart_y = insights.get("chart_y")
        result.chart_title = insights.get("chart_title")
        steps[5].status = "done"
        steps[5].detail = "Insight ready"
        steps[6].status = "done"
        steps[6].detail = f"Chart: {result.chart_type or 'none'}"

    except SQLValidationError as exc:
        _mark_error(steps, exc)
        result.error = _friendly_error(exc)
    except Exception as exc:
        _mark_error(steps, exc)
        result.error = _friendly_error(exc)

    return result
