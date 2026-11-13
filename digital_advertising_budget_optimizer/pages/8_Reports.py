"""
Page 8: Reports
Generates downloadable executive summaries, CSV analytical exports,
and PDF reports for management and academic review.
"""

import streamlit as st
import pandas as pd
from src.campaign_analytics import CampaignAnalyticsEngine
from src.budget_optimizer import BudgetOptimizer
from src.report_generator import ReportGenerator
from src.advertising_metrics import compute_aggregate_metrics
from src.benchmark_engine import BenchmarkEngine

st.title("📑 Analytical Reports & Document Generation")
st.markdown("Generate executive summaries, platform audits, and export raw data for stakeholder presentation.")

df = st.session_state.get("active_df")
if df is None or df.empty:
    st.warning("No active dataset loaded. Please go to 'Dataset Management' first.")
    st.stop()

engine = CampaignAnalyticsEngine(df)
metrics = compute_aggregate_metrics(df)
platform_df = engine.get_platform_performance()
campaign_df = engine.get_campaign_performance()

optimizer = BudgetOptimizer(df)
recommendation = optimizer.optimize_budget(total_budget=1_000_000.0)

rep_gen = ReportGenerator()
bench_engine = BenchmarkEngine()
bench_df = bench_engine.get_benchmark_history()

# Generate Report text
markdown_report = rep_gen.generate_executive_summary_text(metrics, platform_df, recommendation)

tab_view, tab_exports = st.tabs(["📄 Executive Summary Preview", "📥 Export Center (CSV / PDF)"])

# ----------------- TAB 1: PREVIEW -----------------
with tab_view:
    st.markdown("### Executive Report Preview")
    st.markdown(markdown_report)

# ----------------- TAB 2: EXPORTS -----------------
with tab_exports:
    st.markdown("### Download Analytical Reports & Datasets")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("#### 📑 Executive Summary Reports")
        st.download_button(
            label="⬇️ Download Executive Report (Markdown)",
            data=markdown_report,
            file_name="Executive_Advertising_Budget_Report.md",
            mime="text/markdown",
            use_container_width=True,
        )

        pdf_path = rep_gen.export_pdf(markdown_report, "Executive_Advertising_Budget_Report.pdf")
        if pdf_path and pdf_path.exists():
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="⬇️ Download Executive Report (PDF / Formatted)",
                data=pdf_bytes,
                file_name=pdf_path.name,
                mime="application/pdf" if pdf_path.suffix == ".pdf" else "text/markdown",
                use_container_width=True,
            )

    with col_e2:
        st.markdown("#### 📊 CSV Data Exports")
        # 1. Platform Performance CSV
        plat_csv = platform_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Platform Performance (CSV)",
            data=plat_csv,
            file_name="platform_performance_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # 2. Campaign Performance CSV
        camp_csv = campaign_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Campaign Performance (CSV)",
            data=camp_csv,
            file_name="campaign_performance_summary.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # 3. Budget Recommendation CSV
        alloc_csv = pd.DataFrame(recommendation["allocations"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Rs. 1M Budget Recommendation (CSV)",
            data=alloc_csv,
            file_name="budget_recommendation_1M.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # 4. Benchmark History CSV
        if not bench_df.empty:
            bench_csv = bench_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Benchmark Performance History (CSV)",
                data=bench_csv,
                file_name="big_data_benchmark_history.csv",
                mime="text/csv",
                use_container_width=True,
            )

