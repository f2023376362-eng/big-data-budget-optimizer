"""
Database Management Module for SQLite storage and analytical querying.
Implements normalized relational schema creation, batch inserts, analytical views,
and execution of predefined and custom SQL queries.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import config


class DatabaseManager:
    """
    Manages SQLite database connections, schema migrations, and SQL queries.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else config.DATABASE_PATH
        self.schema_path = config.SCHEMA_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection with foreign keys enabled."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables and views from schema.sql."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.schema_path.exists():
            with open(self.schema_path, "r", encoding="utf-8") as f:
                ddl = f.read()
            with self.get_connection() as conn:
                conn.executescript(ddl)

    def populate_dimensions(self, df: pd.DataFrame, conn: sqlite3.Connection):
        """Ensures all unique platforms, campaigns, cities, and devices are registered."""
        # 1. Platforms
        platforms = df["platform"].dropna().unique().tolist()
        for p in platforms:
            conn.execute("INSERT OR IGNORE INTO platforms (platform_name) VALUES (?)", (str(p),))

        # 2. Campaigns
        campaigns = df["campaign"].dropna().unique().tolist()
        for c in campaigns:
            conn.execute("INSERT OR IGNORE INTO campaigns (campaign_name) VALUES (?)", (str(c),))

        # 3. Cities
        cities = df["city"].dropna().unique().tolist()
        for ci in cities:
            conn.execute("INSERT OR IGNORE INTO cities (city_name) VALUES (?)", (str(ci),))

        # 4. Devices
        devices = df["device"].dropna().unique().tolist()
        for d in devices:
            conn.execute("INSERT OR IGNORE INTO devices (device_name) VALUES (?)", (str(d),))

    def insert_advertising_records(self, df: pd.DataFrame, chunk_size: int = 25_000) -> int:
        """
        Inserts advertising DataFrame records into normalized tables.
        Maps natural keys to surrogate foreign keys.
        """
        if df.empty:
            return 0

        with self.get_connection() as conn:
            self.populate_dimensions(df, conn)

            # Retrieve mapping dictionaries
            plat_map = dict(conn.execute("SELECT platform_name, platform_id FROM platforms").fetchall())
            camp_map = dict(conn.execute("SELECT campaign_name, campaign_id FROM campaigns").fetchall())
            city_map = dict(conn.execute("SELECT city_name, city_id FROM cities").fetchall())
            dev_map = dict(conn.execute("SELECT device_name, device_id FROM devices").fetchall())

            # Prepare records tuple
            records_to_insert = []
            for _, row in df.iterrows():
                plat_id = plat_map.get(str(row["platform"]))
                camp_id = camp_map.get(str(row["campaign"]))
                city_id = city_map.get(str(row["city"]))
                dev_id = dev_map.get(str(row["device"]))

                if plat_id and camp_id and city_id and dev_id:
                    records_to_insert.append((
                        str(row["date"]),
                        camp_id,
                        plat_id,
                        city_id,
                        dev_id,
                        str(row.get("age", "Unknown")),
                        str(row.get("gender", "Unknown")),
                        int(row["impressions"]),
                        int(row["clicks"]),
                        float(row["spend"]),
                        int(row["conversions"]),
                        float(row["revenue"]),
                    ))

            # Batch insert
            insert_sql = """
                INSERT INTO advertising_records (
                    record_date, campaign_id, platform_id, city_id, device_id,
                    age_group, gender, impressions, clicks, spend, conversions, revenue
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            for i in range(0, len(records_to_insert), chunk_size):
                batch = records_to_insert[i : i + chunk_size]
                conn.executemany(insert_sql, batch)

            conn.commit()

        return len(records_to_insert)

    def insert_benchmark(
        self,
        dataset_size: int,
        engine: str,
        execution_time_sec: float,
        throughput_rps: float,
        memory_mb: Optional[float],
        status: str,
        notes: str = "",
    ):
        """Logs engine benchmark performance."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO benchmark_results (
                    dataset_size, engine, execution_time_sec, throughput_rps, memory_mb, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (dataset_size, engine, execution_time_sec, throughput_rps, memory_mb, status, notes),
            )
            conn.commit()

    def insert_budget_recommendations(self, recommendation_result: Dict[str, Any]):
        """Saves recommended budget allocations to database."""
        budget = recommendation_result["total_budget"]
        strat = recommendation_result["strategy"]
        with self.get_connection() as conn:
            for alloc in recommendation_result["allocations"]:
                conn.execute(
                    """
                    INSERT INTO budget_recommendations (
                        total_budget, strategy, platform, allocated_percentage, allocated_amount,
                        expected_conversions, expected_revenue, expected_roas, rationale
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        budget,
                        strat,
                        alloc["platform"],
                        alloc["allocated_percentage"],
                        alloc["allocated_amount"],
                        alloc.get("expected_conversions"),
                        alloc.get("expected_revenue"),
                        alloc.get("expected_roas"),
                        alloc.get("rationale"),
                    ),
                )
            conn.commit()

    def execute_query(self, sql: str, params: Tuple = ()) -> pd.DataFrame:
        """Executes a SQL query and returns results as a Pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(sql, conn, params=params)

    def get_table_names(self) -> List[str]:
        """Returns list of user tables in the database."""
        sql = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
        df = self.execute_query(sql)
        return df["name"].tolist() if not df.empty else []

    def get_table_stats(self) -> pd.DataFrame:
        """Returns row count and disk estimate for each table."""
        tables = self.get_table_names()
        stats = []
        with self.get_connection() as conn:
            for t in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                stats.append({"Table Name": t, "Row Count": count})
        return pd.DataFrame(stats)

    def get_predefined_queries(self) -> Dict[str, str]:
        """Returns a catalog of analytical SQL queries for the Explorer."""
        return {
            "Platform Performance Overview (View)": "SELECT * FROM v_platform_summary ORDER BY total_revenue DESC;",
            "Top 5 Campaigns by ROAS": """
                SELECT 
                    c.campaign_name,
                    p.platform_name,
                    SUM(a.spend) AS total_spend,
                    SUM(a.revenue) AS total_revenue,
                    ROUND(SUM(a.revenue) / SUM(a.spend), 2) AS roas,
                    SUM(a.conversions) AS conversions
                FROM advertising_records a
                JOIN campaigns c ON a.campaign_id = c.campaign_id
                JOIN platforms p ON a.platform_id = p.platform_id
                GROUP BY c.campaign_name, p.platform_name
                HAVING total_spend > 50000
                ORDER BY roas DESC
                LIMIT 5;
            """,
            "Revenue & Spend by City": """
                SELECT 
                    ci.city_name,
                    SUM(a.impressions) AS total_impressions,
                    SUM(a.clicks) AS total_clicks,
                    ROUND(SUM(a.spend), 2) AS total_spend,
                    ROUND(SUM(a.revenue), 2) AS total_revenue,
                    ROUND(SUM(a.revenue) / SUM(a.spend), 2) AS city_roas
                FROM advertising_records a
                JOIN cities ci ON a.city_id = ci.city_id
                GROUP BY ci.city_name
                ORDER BY total_revenue DESC;
            """,
            "Device Type Breakdown": """
                SELECT 
                    d.device_name,
                    SUM(a.impressions) AS impressions,
                    SUM(a.clicks) AS clicks,
                    ROUND(SUM(a.clicks) * 100.0 / SUM(a.impressions), 2) AS ctr,
                    ROUND(SUM(a.spend), 2) AS spend,
                    ROUND(SUM(a.revenue), 2) AS revenue,
                    ROUND(SUM(a.revenue) / SUM(a.spend), 2) AS roas
                FROM advertising_records a
                JOIN devices d ON a.device_id = d.device_id
                GROUP BY d.device_name
                ORDER BY revenue DESC;
            """,
            "Recent Benchmark Results": """
                SELECT executed_at, dataset_size, engine, execution_time_sec, throughput_rps, memory_mb, status
                FROM benchmark_results
                ORDER BY executed_at DESC
                LIMIT 10;
            """,
            "Latest Budget Allocation Recommendations": """
                SELECT created_at, strategy, platform, allocated_percentage, allocated_amount, expected_roas, rationale
                FROM budget_recommendations
                ORDER BY created_at DESC
                LIMIT 10;
            """,
        }

