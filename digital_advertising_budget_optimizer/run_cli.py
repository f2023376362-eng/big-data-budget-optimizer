"""
Standalone Demonstration Runner & CLI Pipeline
Executes the full Big Data Analytics workflow:
1. Data generation & cleaning
2. Database insertion & analytical querying
3. Big Data benchmark (Pandas vs MapReduce vs Spark)
4. Budget optimization for Rs. 1,000,000
5. Report generation
"""

import sys
import time
from pathlib import Path
import pandas as pd

# Set paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from src.data_generator import ensure_dataset
from src.data_cleaning import DataCleaner
from src.advertising_metrics import compute_aggregate_metrics
from src.campaign_analytics import CampaignAnalyticsEngine
from src.budget_optimizer import BudgetOptimizer
from src.benchmark_engine import BenchmarkEngine
from src.database import DatabaseManager
from src.report_generator import ReportGenerator


def run_pipeline(dataset_size: int = 10_000, budget: float = 1_000_000.0):
    print("=" * 80)
    print("  DIGITAL ADVERTISING BUDGET OPTIMIZER — BIG DATA ANALYTICS SYSTEM")
    print("  Student: Hurrain Mustafa | Roll No: F202333011 | Course: Big Data Analytics")
    print("=" * 80)

    # 1. Dataset Generation
    print(f"\n[1/5] Ensuring {dataset_size:,} record dataset on disk...")
    csv_path = ensure_dataset(dataset_size)
    print(f"      Source file: {csv_path.name} ({csv_path.stat().st_size / (1024*1024):.2f} MB)")

    df_raw = pd.read_csv(csv_path)
    cleaner = DataCleaner()
    df, clean_stats = cleaner.clean(df_raw)
    print(f"      Cleaned dataset: {len(df):,} valid rows ({clean_stats['duplicates_removed']} duplicates removed)")

    # 2. Database Sync
    print("\n[2/5] Initializing SQLite database and syncing records...")
    db = DatabaseManager()
    inserted = db.insert_advertising_records(df.head(10_000))
    print(f"      Inserted {inserted:,} records into normalized tables.")
    view_df = db.execute_query("SELECT * FROM v_platform_summary ORDER BY total_revenue DESC;")
    print("      Active Platforms in Database:")
    for _, r in view_df.iterrows():
        print(f"        - {r['platform_name']:<12}: Revenue = Rs. {r['total_revenue']:>12,.2f} | ROAS = {r['roas']:.2f}x | CPA = Rs. {r['cpa']:.2f}")

    # 3. Big Data Benchmarking
    print(f"\n[3/5] Running Big Data Benchmarks across Engines ({dataset_size:,} records)...")
    bench_engine = BenchmarkEngine(db_manager=db)
    bench_runs = bench_engine.run_all_comparisons(csv_path, dataset_size, include_spark=True)
    print("      Benchmark Results Table:")
    print(f"      {'Engine':<35} | {'Latency (s)':<12} | {'Throughput (rps)':<18} | {'Status'}")
    print("      " + "-" * 75)
    for b in bench_runs:
        print(f"      {b.get('engine'):<35} | {b.get('execution_time_sec', 0.0):>10.4f}s | {b.get('throughput_rps', 0.0):>16,.0f} | {b.get('status')}")

    # 4. Marketing Budget Recommendation Engine (Rs. 1,000,000)
    print(f"\n[4/5] Solving Marketing Budget Allocation for Rs. {budget:,.2f}...")
    optimizer = BudgetOptimizer(df)
    rec = optimizer.optimize_budget(total_budget=budget, strategy="Balanced Optimization")

    print(f"      Strategy: {rec['strategy']}")
    print(f"      {'Platform':<12} | {'Allocation %':<14} | {'Allocated PKR':<18} | {'Direction':<10} | {'Expected ROAS'}")
    print("      " + "-" * 72)
    for a in rec["allocations"]:
        print(f"      {a['platform']:<12} | {a['allocated_percentage']:>12.1f}% | Rs. {a['allocated_amount']:>14,.2f} | {a['action']:<10} | {a['expected_roas']:.2f}x")

    total_allocated = sum(a['allocated_amount'] for a in rec["allocations"])
    print("      " + "-" * 72)
    print(f"      {'TOTAL':<12} | {100.0:>12.1f}% | Rs. {total_allocated:>14,.2f} | (Exact match: {abs(total_allocated - budget) < 0.01})")

    proj = rec["projections"]
    print(f"\n      Projected Return: Rs. {proj['expected_revenue']:,.2f} gross revenue ({proj['expected_roas']:.2f}x blended ROAS)")
    print(f"      Projected Net Contribution: Rs. {proj['expected_net_profit']:,.2f}")
    print(f"      Projected Conversions: {proj['expected_conversions']:,} customer orders")

    # 5. Report Generation
    print("\n[5/5] Generating Executive Summary & Exporting Reports...")
    rep_gen = ReportGenerator()
    overall = compute_aggregate_metrics(df)
    camp_engine = CampaignAnalyticsEngine(df)
    platform_df = camp_engine.get_platform_performance()
    md_report = rep_gen.generate_executive_summary_text(overall, platform_df, rec)

    report_path = config.REPORTS_DIR / "Executive_Summary_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"      Executive Report saved to: {report_path.resolve()}")

    print("\n" + "=" * 80)
    print("  ALL DEMONSTRATION WORKFLOWS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    run_pipeline(dataset_size=10_000, budget=1_000_000.0)

