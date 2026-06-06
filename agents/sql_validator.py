"""
Step 4 — Validate generated SQL (read-only, safe execution).
"""

from __future__ import annotations

import re

# Blocked SQL verbs (case-insensitive word boundaries)
_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|REPLACE|TRUNCATE|ATTACH|DETACH|PRAGMA|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

# Multiple statements (; separated) are not allowed
_MULTI_STATEMENT = re.compile(r";\s*\S")


class SQLValidationError(Exception):
    """Raised when generated SQL fails security or syntax checks."""


def validate_sql(sql: str) -> str:
    """
    Validate and normalize SQL for read-only execution.

    Agent loop Step 4: Validate SQL.

    Security:
    - Only SELECT / WITH queries
    - Blocks DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, etc.
    - Rejects multiple statements

    Returns cleaned SQL string on success.
    Raises SQLValidationError on failure.
    """
    if not sql or not sql.strip():
        raise SQLValidationError("SQL query is empty.")

    cleaned = sql.strip()

    # Remove markdown code fences if model added them
    cleaned = re.sub(r"^```(?:sql)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip().rstrip(";")

    if _MULTI_STATEMENT.search(cleaned):
        raise SQLValidationError("Multiple SQL statements are not allowed.")

    if _FORBIDDEN.search(cleaned):
        raise SQLValidationError(
            "Only read-only SELECT queries are allowed. "
            "Blocked: DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE."
        )

    upper = cleaned.upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        raise SQLValidationError("Query must start with SELECT or WITH.")

    return cleaned


def is_safe_sql(sql: str) -> bool:
    """Non-throwing check for tests and UI hints."""
    try:
        validate_sql(sql)
        return True
    except SQLValidationError:
        return False
