"""
Step 1 — Read database schema automatically for grounding SQL generation.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from utils.database import DB_PATH

# Sample rows help Llama3 understand column semantics
SAMPLE_ROW_LIMIT = 2


def read_schema(db_path: Path | None = None) -> str:
    """
    Return a human-readable schema string with columns, types, FKs, and samples.

    Agent loop Step 1: Read database schema.
    """
    path = db_path or DB_PATH
    uri = f"file:{path.resolve()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )
    tables = [row[0] for row in cur.fetchall()]

    sections: list[str] = []
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = cur.fetchall()
        col_lines = []
        for col in columns:
            cid, name, col_type, notnull, default, pk = col
            flags = []
            if pk:
                flags.append("PRIMARY KEY")
            if notnull:
                flags.append("NOT NULL")
            flag_str = f" ({', '.join(flags)})" if flags else ""
            col_lines.append(f"  - {name} {col_type}{flag_str}")

        cur.execute(f"SELECT COUNT(*) FROM {table}")
        row_count = cur.fetchone()[0]

        cur.execute(f"SELECT * FROM {table} LIMIT {SAMPLE_ROW_LIMIT}")
        sample_rows = cur.fetchall()
        col_names = [c[1] for c in columns]
        samples = [dict(zip(col_names, row)) for row in sample_rows]

        sections.append(
            f"TABLE {table} ({row_count} rows)\n"
            f"Columns:\n" + "\n".join(col_lines) + "\n"
            f"Sample rows: {samples}"
        )

    conn.close()
    return "\n\n".join(sections)


def read_schema_compact(db_path: Path | None = None) -> str:
    """One-line-per-table schema for lightweight prompts."""
    full = read_schema(db_path)
    # Strip sample rows for compact mode
    lines = []
    for block in full.split("\n\n"):
        if "Sample rows:" in block:
            block = block.split("Sample rows:")[0].strip()
        lines.append(block)
    return "\n\n".join(lines)
