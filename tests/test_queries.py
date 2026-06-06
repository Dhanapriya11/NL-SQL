"""
Tests for SQL validation, schema, sample analytics, and Tamil employee data.
Run: python -m pytest tests/ -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agents.schema_reader import read_schema
from agents.sql_validator import SQLValidationError, is_safe_sql, validate_sql
from utils.database import execute_query, init_database


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_database(force=True)


class TestSQLValidator:
    def test_allows_select(self):
        assert validate_sql("SELECT * FROM sales LIMIT 10").upper().startswith("SELECT")

    def test_allows_with_cte(self):
        sql = validate_sql("WITH t AS (SELECT 1 AS x) SELECT x FROM t")
        assert "WITH" in sql.upper()

    def test_blocks_delete(self):
        with pytest.raises(SQLValidationError):
            validate_sql("DELETE FROM sales")

    def test_blocks_drop(self):
        with pytest.raises(SQLValidationError):
            validate_sql("DROP TABLE sales")

    def test_blocks_insert(self):
        with pytest.raises(SQLValidationError):
            validate_sql("INSERT INTO sales VALUES (1,1,1,'2024-01-01',1,10)")

    def test_blocks_update(self):
        with pytest.raises(SQLValidationError):
            validate_sql("UPDATE sales SET amount = 0")

    def test_blocks_truncate(self):
        with pytest.raises(SQLValidationError):
            validate_sql("TRUNCATE TABLE sales")

    def test_blocks_multiple_statements(self):
        with pytest.raises(SQLValidationError):
            validate_sql("SELECT 1; DROP TABLE sales")

    def test_strips_markdown_fences(self):
        sql = validate_sql("```sql\nSELECT * FROM products\n```")
        assert "products" in sql


class TestSchemaReader:
    def test_schema_contains_tables(self):
        schema = read_schema()
        for table in ("departments", "employees", "products", "sales"):
            assert f"TABLE {table}" in schema

    def test_schema_has_tamil_names(self):
        sql = "SELECT name FROM employees WHERE name IN ('Dhana','Priya','Dharshini','Koushi')"
        df, err = execute_query(validate_sql(sql))
        assert err is None
        assert len(df) == 4


class TestSampleQueries:
    def test_sales_by_month(self):
        sql = """
        SELECT strftime('%Y-%m', sale_date) AS month,
               ROUND(SUM(amount), 2) AS total_sales_rs
        FROM sales GROUP BY month ORDER BY month
        """
        df, err = execute_query(validate_sql(sql))
        assert err is None
        assert len(df) >= 1

    def test_top_product(self):
        sql = """
        SELECT p.name, ROUND(SUM(s.amount), 2) AS total_rs
        FROM sales s JOIN products p ON s.product_id = p.id
        GROUP BY p.name ORDER BY total_rs DESC LIMIT 1
        """
        df, err = execute_query(validate_sql(sql))
        assert err is None
        assert len(df) == 1

    def test_employees_by_department(self):
        sql = """
        SELECT d.name AS department, COUNT(e.id) AS employee_count
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id
        GROUP BY d.name
        """
        df, err = execute_query(validate_sql(sql))
        assert err is None
        assert df["employee_count"].sum() == 15

    def test_find_priya_and_dhana(self):
        sql = """
        SELECT name, salary FROM employees
        WHERE name IN ('Priya', 'Dhana')
        """
        df, err = execute_query(validate_sql(sql))
        assert err is None
        assert len(df) == 2
        assert set(df["name"]) == {"Priya", "Dhana"}

    def test_chennai_department_location(self):
        sql = "SELECT name FROM departments WHERE location = 'Chennai'"
        df, err = execute_query(validate_sql(sql))
        assert err is None
        assert "Engineering" in df["name"].values

    def test_is_safe_sql_helper(self):
        assert is_safe_sql("SELECT COUNT(*) FROM employees")
        assert not is_safe_sql("ALTER TABLE employees ADD col TEXT")
