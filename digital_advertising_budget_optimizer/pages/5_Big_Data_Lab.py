"""
Page 5: Big Data Lab
Scientific benchmarking environment comparing:
Pandas (Vectorized In-Memory) vs MapReduce (Streaming Simulation) vs Apache Spark (PySpark Local).
Executes actual benchmarks across 10K, 100K, 1M, and 10M records.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.data_generator import ensure_dataset, get_default_dataset_path
from src.benchmark_engine import BenchmarkEngine
from src.database import DatabaseManager

st.title("⚡ Big Data Processing & Benchmark Lab")
st.markdown(
    "Rigorous comparative evaluation of **Pandas vs MapReduce vs Apache Spark** "
    "performing identical multi-metric aggregations across escalating dataset volumes."
)

# Connect DB for persisting results
db = DatabaseManager()
bench_engine = BenchmarkEngine(db_manager=db)

# Controls
st.markdown("### 🔬 Benchmark Configuration")
col_b1, col_b2 = st.columns(2)

with col_b1:
    dataset_size = st.selectbox(
        "Select Benchmark Dataset Volume:",
        options=[10_000, 100_000, 1_000_000, 10_000_000],
        format_func=lambda x: f"{x:,} records",
        index=1,
    )

with col_b2:
    engine_choice = st.selectbox(
        "Select Processing Engine:",
        options=["Run All Three Engines Comparatively (Recommended)", "Pandas Only", "MapReduce Only", "Apache Spark Only"],
    )

if dataset_size == 10_000_000:
    st.warning(
        "⚠️ **10 Million Scale Notice:** Executing all 3 engines on 10M records locally requires ~1-2 minutes. "
        "Engines use memory-bounded streaming to avoid system crashes."
    )

if st.button("🚀 Execute Real-Time Benchmark", type="primary", use_container_width=True):
    with st.spinner(f"Preparing {dataset_size:,} record dataset and executing benchmarks..."):
        # Ensure data file exists on disk
        data_path = ensure_dataset(dataset_size)

        benchmark_runs = []
        if "All Three" in engine_choice:
            benchmark_runs = bench_engine.run_all_comparisons(data_path, dataset_size)
        elif "Pandas" in engine_choice:
            benchmark_runs = [bench_engine.run_engine_benchmark("Pandas", data_path, dataset_size)]
        elif "MapReduce" in engine_choice:
            benchmark_runs = [bench_engine.run_engine_benchmark("MapReduce", data_path, dataset_size)]
        elif "Spark" in engine_choice:
            benchmark_runs = [bench_engine.run_engine_benchmark("Spark", data_path, dataset_size)]

        st.session_state["latest_benchmarks"] = benchmark_runs
        st.success(f"✅ Benchmark completed successfully across {len(benchmark_runs)} engine(s)!")

# Display Results
latest_results = st.session_state.get("latest_benchmarks")

if latest_results:
    st.markdown("---")
    st.markdown("### 📊 Measured Benchmark Results")

    # Summary table
    bench_table = []
    for r in latest_results:
        bench_table.append({
            "Engine": r.get("engine"),
            "Status": r.get("status"),
            "Dataset Size": f"{r.get('dataset_size', 0):,} records",
            "Execution Time (s)": r.get("execution_time_sec", 0.0),
            "Throughput (Records/Sec)": f"{r.get('throughput_rps', 0):,}",
            "Memory Footprint (MB)": r.get("memory_mb", 0.0),
            "Architecture Notes": r.get("notes", ""),
        })

    bench_df = pd.DataFrame(bench_table)
    st.dataframe(bench_df, use_container_width=True, hide_index=True)

    # Visualizations
    valid_runs = [r for r in latest_results if r.get("status") == "SUCCESS"]
    if valid_runs:
        v_df = pd.DataFrame(valid_runs)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_time = px.bar(
                v_df,
                x="engine",
                y="execution_time_sec",
                color="engine",
                text="execution_time_sec",
                title="Execution Latency (Seconds — Lower is Better)",
                color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
            )
            fig_time.update_traces(texttemplate="%{text:.3f}s", textposition="outside")
            fig_time.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig_time, use_container_width=True)

        with col_c2:
            fig_tps = px.bar(
                v_df,
                x="engine",
                y="throughput_rps",
                color="engine",
                text="throughput_rps",
                title="Throughput (Records / Sec — Higher is Better)",
                color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
            )
            fig_tps.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
            fig_tps.update_layout(height=360, showlegend=False)
            st.plotly_chart(fig_tps, use_container_width=True)

        # Scientific Consistency Audit
        st.markdown("#### 🔬 Aggregate Consistency Verification")
        st.caption("Verifies that different computing engines arrive at mathematically equivalent totals.")
        audit_rows = []
        for r in valid_runs:
            s = r.get("summary", {})
            audit_rows.append({
                "Engine": r.get("engine"),
                "Impressions": s.get("impressions", 0),
                "Clicks": s.get("clicks", 0),
                "Spend (PKR)": f"Rs. {s.get('spend', 0.0):,.2f}",
                "Conversions": s.get("conversions", 0),
                "Revenue (PKR)": f"Rs. {s.get('revenue', 0.0):,.2f}",
                "Overall ROAS": f"{s.get('overall_roas', 0.0):.2f}x",
            })
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True, hide_index=True)

st.markdown("---")
# Academic Deep Dive
st.markdown("### 🎓 Big Data Architecture Comparison & Engineering Analysis")

with st.expander("📖 1. How Pandas Processes Data", expanded=True):
    st.markdown(
        """
        - **Execution Model:** Loads the entire dataset into memory as contiguous NumPy C-arrays.
        - **Strengths:** Vectorized SIMD operations on single-node datasets that fit comfortably in RAM; near-zero serialization overhead.
        - **Limitations:** Monolithic single-node bottleneck. Requires 3–5x data size in free RAM during complex groupby transformations. Cannot scale horizontally.
        - **Ideal Scale:** Up to 1–5 million records on modern workstations.
        """
    )

with st.expander("📖 2. How MapReduce Works", expanded=True):
    st.markdown(
        """
        - **Execution Model:** Functional programming paradigm with 3 distinct stages:
          1. **Map:** Parses streaming records and emits intermediate `(key, values)` tuples.
          2. **Shuffle & Sort:** Partitions, hashes, and groups intermediate records by key across nodes/threads.
          3. **Reduce:** Aggregates values per key in parallel.
        - **Strengths:** Extremely memory-efficient streaming; node failure resilience; capable of scaling to petabytes on commodity clusters.
        - **Limitations:** High disk I/O and network serialization penalties between Map and Reduce phases. Higher latency on small/medium datasets.
        - **Ideal Scale:** Batch analytics on massive disk-bound datasets overflowing RAM.
        """
    )

with st.expander("📖 3. How Apache Spark Processes Data", expanded=True):
    st.markdown(
        """
        - **Execution Model:** Resilient Distributed Datasets (RDDs) and DataFrames with DAG (Directed Acyclic Graph) execution.
        - **Strengths:** In-memory caching and pipelined execution between transformations. Catalyst Query Optimizer and Tungsten code generation provide 10–100x speedups over traditional MapReduce.
        - **Limitations:** Higher initial JVM startup and cluster coordination overhead. Driver node memory constraints on local single-machine setups.
        - **Ideal Scale:** High-throughput streaming, iterative machine learning, and multi-terabyte distributed data pipelines.
        """
    )

