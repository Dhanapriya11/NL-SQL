"""
SQLite database utilities: seed from CSV, read-only execution, KPI helpers.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "company.db"
CSV_DIR = PROJECT_ROOT / "database" / "csv"

# Table load order respects foreign keys
CSV_TABLES = [
    ("departments", "departments.csv"),
    ("employees", "employees.csv"),
    ("products", "products.csv"),
    ("sales", "sales.csv"),
]


def _writable_connection() -> sqlite3.Connection:
    """Connection for setup/migrations (read-write)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def _read_only_connection() -> sqlite3.Connection:
    """Read-only URI connection for query execution."""
    uri = f"file:{DB_PATH.resolve()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def init_database(force: bool = False) -> None:
    """
    Build company.db from CSV files if missing or when force=True.
    Drops and recreates tables from CSV on force rebuild.
    """
    if DB_PATH.exists() and not force:
        return

    conn = _writable_connection()
    cur = conn.cursor()

    if force:
        for table, _ in reversed(CSV_TABLES):
            cur.execute(f"DROP TABLE IF EXISTS {table}")

    # Schema with foreign keys
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT
        );
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            hire_date TEXT,
            salary REAL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            unit_price REAL
        );
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            employee_id INTEGER,
            sale_date TEXT,
            quantity INTEGER,
            amount REAL,
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
        """
    )

    for table, csv_name in CSV_TABLES:
        csv_path = CSV_DIR / csv_name
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing seed CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        df.to_sql(table, conn, if_exists="append", index=False)

    conn.commit()
    conn.close()


def execute_query(sql: str, limit: int = 500) -> tuple[pd.DataFrame, str | None]:
    """
    Run a validated read-only query. Appends LIMIT if not present.
    Returns (dataframe, error_message).
    """
    stripped = sql.strip().rstrip(";")
    if "LIMIT" not in stripped.upper():
        stripped = f"{stripped} LIMIT {limit}"

    try:
        conn = _read_only_connection()
        df = pd.read_sql_query(stripped, conn)
        conn.close()
        return df, None
    except Exception as exc:
        return pd.DataFrame(), str(exc)


def get_table_info() -> dict[str, dict]:
    """Row counts and column metadata for the Streamlit schema explorer."""
    conn = _read_only_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    info: dict[str, dict] = {}
    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        cols = cur.fetchall()
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        info[table] = {"columns": cols, "count": count}
    conn.close()
    return info


def kpi_metrics() -> dict[str, float | int]:
    """Dashboard headline metrics."""
    conn = _read_only_connection()
    total_sales = pd.read_sql("SELECT ROUND(SUM(amount), 2) AS v FROM sales", conn).iloc[0, 0]
    employees = pd.read_sql("SELECT COUNT(*) AS v FROM employees", conn).iloc[0, 0]
    products = pd.read_sql("SELECT COUNT(*) AS v FROM products", conn).iloc[0, 0]
    departments = pd.read_sql("SELECT COUNT(*) AS v FROM departments", conn).iloc[0, 0]
    conn.close()
    return {
        "total_sales": float(total_sales or 0),
        "employees": int(employees),
        "products": int(products),
        "departments": int(departments),
    }
