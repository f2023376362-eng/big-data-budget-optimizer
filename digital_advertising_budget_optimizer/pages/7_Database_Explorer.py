"""
Page 7: Database Explorer
Inspects normalized SQLite database tables, record counts, ERD schema mapping,
and executes predefined and custom analytical SQL queries.
"""

import time
import streamlit as st
import pandas as pd
from src.database import DatabaseManager

st.title("🗄️ Database Explorer & SQL Console")

db = DatabaseManager()

# Top Stats
st.markdown("### 📊 Database Statistics & Entities")
stats_df = db.get_table_stats()
if not stats_df.empty:
    cols = st.columns(len(stats_df))
    for idx, row in stats_df.iterrows():
        cols[idx].metric(row["Table Name"], f"{row['Row Count']:,} rows")
else:
    st.info("Database tables initialized. Synchronize active dataset in 'Dataset Management' to populate records.")

tab_queries, tab_custom, tab_erd = st.tabs([
    "🔍 Predefined Analytical SQL Queries",
    "💻 Custom SQL Console",
    "📐 Entity Relationship Diagram (ERD)",
])

# ----------------- TAB 1: PREDEFINED QUERIES -----------------
with tab_queries:
    st.markdown("### Predefined Business & Engineering Queries")
    predefined = db.get_predefined_queries()
    query_name = st.selectbox("Select Analytical Query:", options=list(predefined.keys()))

    selected_sql = predefined[query_name]
    st.code(selected_sql, language="sql")

    if st.button("▶️ Execute Query", key="run_predefined"):
        start = time.perf_counter()
        try:
            res_df = db.execute_query(selected_sql)
            elapsed = time.perf_counter() - start
            st.success(f"Query returned {len(res_df):,} rows in {elapsed*1000:.2f} ms")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Execution Error: {str(e)}")

# ----------------- TAB 2: CUSTOM CONSOLE -----------------
with tab_custom:
    st.markdown("### Interactive SQL Query Console")
    custom_sql = st.text_area(
        "Enter SQL Query (Read-only SELECT queries recommended):",
        value="SELECT p.platform_name, COUNT(a.record_id) AS records, SUM(a.revenue) AS revenue FROM advertising_records a JOIN platforms p ON a.platform_id = p.platform_id GROUP BY p.platform_name ORDER BY revenue DESC;",
        height=120,
    )

    if st.button("▶️ Run Custom SQL", type="primary"):
        start = time.perf_counter()
        try:
            res_df = db.execute_query(custom_sql)
            elapsed = time.perf_counter() - start
            st.success(f"Returned {len(res_df):,} rows in {elapsed*1000:.2f} ms")
            st.dataframe(res_df, use_container_width=True)
        except Exception as e:
            st.error(f"SQL Error: {str(e)}")

# ----------------- TAB 3: ERD -----------------
with tab_erd:
    st.markdown("### Database Architecture & Entity Relationships")
    st.markdown(
        """
        The database follows third normal form (3NF) principles:
        - **Dimensions:** `platforms`, `campaigns`, `cities`, `devices`
        - **Fact:** `advertising_records` with foreign key relationships
        - **Operational Logs:** `benchmark_results`, `budget_recommendations`
        - **Analytical Views:** `v_platform_summary`
        """
    )
    erd_file = db.schema_path.parent.parent / "diagrams" / "erd.mmd"
    if erd_file.exists():
        with open(erd_file, "r") as f:
            st.code(f.read(), language="mermaid")

