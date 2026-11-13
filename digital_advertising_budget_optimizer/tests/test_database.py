"""
Unit tests for SQLite database schema, operations, foreign keys, and queries.
"""

import pytest
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import DatabaseManager
from src.data_generator import AdvertisingDataGenerator


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_advertising.db"
    return DatabaseManager(db_path=db_file)


def test_schema_initialization(temp_db):
    tables = temp_db.get_table_names()
    assert "platforms" in tables
    assert "campaigns" in tables
    assert "cities" in tables
    assert "devices" in tables
    assert "advertising_records" in tables
    assert "benchmark_results" in tables
    assert "budget_recommendations" in tables


def test_insert_and_query_records(temp_db):
    gen = AdvertisingDataGenerator(seed=123)
    sample_df = gen.generate_batch(500)

    inserted = temp_db.insert_advertising_records(sample_df)
    assert inserted == 500

    # Query view
    view_df = temp_db.execute_query("SELECT * FROM v_platform_summary;")
    assert not view_df.empty
    assert len(view_df) <= 5
    assert "roas" in view_df.columns
    assert "total_revenue" in view_df.columns


def test_predefined_queries_execution(temp_db):
    gen = AdvertisingDataGenerator(seed=123)
    sample_df = gen.generate_batch(500)
    temp_db.insert_advertising_records(sample_df)

    queries = temp_db.get_predefined_queries()
    for name, sql in queries.items():
        res = temp_db.execute_query(sql)
        assert isinstance(res, pd.DataFrame), f"Query '{name}' failed to return DataFrame"

