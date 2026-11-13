# Digital Advertising Budget Optimizer — Big Data Analytics System
**University Project 2 Deliverable**  
**Student:** Hurrain Mustafa | **Roll No:** F202333011 | **Course:** Big Data Analytics

---

## 🎯 Project Overview
This enterprise-grade Big Data Analytics and Decision Support application answers the core strategic marketing question:
> **"Where should we spend the next Rs. 1,000,000 across Facebook, Instagram, Google, TikTok, and YouTube to maximize marketing ROI?"**

The system provides:
- **Big Data Simulation:** Side-by-side performance benchmarking of **Pandas vs MapReduce vs Apache Spark** across 10K, 100K, 1M, and 10M records.
- **Budget Optimization Engine:** Mathematically derives optimal capital allocations under 3 distinct strategies:
  1. *ROAS Maximization*
  2. *Conversion Maximization*
  3. *Balanced Optimization*
- **Exact Rupee Reconciliation:** Guarantees all platform splits sum to **exactly Rs. 1,000,000.00 PKR** (100.0%).
- **Interactive Multi-Page Streamlit Dashboard:** 9 dedicated pages with Plotly visualizations, dataset upload/cleaner, and an AI Analytics Assistant.
- **Normalized SQLite Database:** 3NF relational schema with dimensions, fact tables, analytical views, and SQL query console.
- **Automated Test Suite:** Comprehensive PyTest coverage for metric formulas, validation rules, budget optimization constraints, and database operations.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your machine.

### 2. Install Dependencies
```bash
cd digital_advertising_budget_optimizer
python -m pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m pytest tests/ -v
```

### 4. Launch the Streamlit Application
```bash
streamlit run app.py
```
*(Or specify the full path if invoking from root workspace)*:
```bash
python -m streamlit run digital_advertising_budget_optimizer/app.py
```

---

## 📁 Project Architecture & File Structure
```
digital_advertising_budget_optimizer/
│
├── app.py                     # Main application entry point & KPI scorecard
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive project documentation
├── config.py                  # Domain constants, paths & platform priors
│
├── data/
│   ├── raw/                   # Generated raw CSV datasets (10k, 100k, 1m, 10m)
│   ├── processed/             # Cleaned and normalized datasets
│   └── benchmarks/            # Benchmark history JSON logs
│
├── src/
│   ├── data_generator.py      # High-performance chunked data generator
│   ├── data_validation.py     # Schema & anomaly validator, column synonym mapper
│   ├── data_cleaning.py       # Bound clamper (clicks <= impressions), deduplicator
│   ├── advertising_metrics.py # CTR, CPC, CPA, CVR, ROAS zero-division-safe formulas
│   ├── campaign_analytics.py  # Platform & campaign efficiency frontier engine
│   ├── audience_analytics.py  # Age, gender, city (Karachi, Lahore), device analytics
│   ├── pandas_processor.py    # Vectorized in-memory Big Data processing engine
│   ├── mapreduce_processor.py # Streaming Mapper-Combiner-Reducer simulation
│   ├── spark_processor.py     # PySpark Local Cluster DataFrame processing engine
│   ├── benchmark_engine.py    # Fair benchmark orchestrator & logger
│   ├── budget_optimizer.py    # Simplex Rs. 1,000,000 budget recommendation engine
│   ├── database.py            # SQLite connection, DDL, views & query executor
│   ├── report_generator.py    # Markdown & PDF/CSV export engine
│   └── chatbot.py             # Deterministic data-grounded analytics assistant
│
├── pages/
│   ├── 1_Executive_Overview.py    # Scorecard KPIs & platform tradeoffs
│   ├── 2_Dataset_Management.py    # 10K-10M generator, CSV/Excel upload & cleaner
│   ├── 3_Advertising_Analytics.py # Platform comparisons & campaign frontiers
│   ├── 4_Audience_Insights.py     # Age, city, gender & device breakdowns
│   ├── 5_Big_Data_Lab.py          # Pandas vs MapReduce vs Spark benchmarks
│   ├── 6_Budget_Optimizer.py      # Interactive Rs. 1M budget optimizer
│   ├── 7_Database_Explorer.py     # Normalized tables & analytical SQL console
│   ├── 8_Reports.py               # Downloadable executive summaries & CSV exports
│   └── 9_Analytics_Assistant.py   # AI Assistant answering natural language queries
│
├── database/
│   ├── schema.sql             # Relational DDL (3NF dimensions, facts, views, indexes)
│   └── advertising.db         # Active SQLite database file
│
├── diagrams/
│   ├── erd.mmd                # Mermaid Entity Relationship Diagram
│   └── erd.png                # Visual architecture diagram
│
├── tests/
│   ├── test_metrics.py            # Unit tests for CTR, CPC, CPA, CVR, ROAS
│   ├── test_data_validation.py    # Unit tests for schema validation & cleaner
│   ├── test_budget_optimizer.py   # Unit tests for Rs. 1M sum & boundary constraints
│   └── test_database.py           # Unit tests for SQLite CRUD & analytical views
│
├── reports/                   # Exported CSV and PDF executive reports
│
└── docs/
    ├── project_documentation.md   # 27-section comprehensive university submission
    ├── methodology.md             # Mathematical formulas & simplex optimizer logic
    ├── big_data_comparison.md     # Engineering analysis: Pandas vs MR vs Spark
    ├── database_design.md         # Schema specification & index design
    └── limitations.md             # Boundary conditions & future enhancements
```

---

## 📊 Core Business & Metric Formulas
- **Click-Through Rate (CTR):** $(\text{Clicks} / \text{Impressions}) \times 100$
- **Cost Per Click (CPC):** $\text{Spend} / \text{Clicks}$
- **Cost Per Acquisition (CPA):** $\text{Spend} / \text{Conversions}$
- **Conversion Rate (CVR):** $(\text{Conversions} / \text{Clicks}) \times 100$
- **Return on Ad Spend (ROAS):** $\text{Revenue} / \text{Spend}$
- **Net Contribution:** $\text{Revenue} - \text{Spend}$

---

## ⚡ Big Data Benchmarks Overview (Typical Results)
| Dataset Volume | Pandas | MapReduce | Apache Spark |
|---|---|---|---|
| **10,000 Records** | ~0.03s (~330k rps) | ~0.12s (~83k rps) | ~1.8s (JVM startup) |
| **100,000 Records** | ~0.25s (~400k rps) | ~1.10s (~90k rps) | ~2.5s (~40k rps) |
| **1,000,000 Records** | ~2.80s (~357k rps) | ~11.5s (~87k rps) | ~5.2s (~192k rps) |

---

## 💰 Recommended Rs. 1,000,000 Allocation (Balanced Strategy)
- **Google:** ~35.0% (Rs. 350,000) — *Highest ROAS yield (~3.6x)*
- **Instagram:** ~28.0% (Rs. 280,000) — *High visual engagement (~3.1x ROAS)*
- **Facebook:** ~18.0% (Rs. 180,000) — *Broad demographic reach and predictable CPA*
- **TikTok:** ~12.0% (Rs. 120,000) — *Lowest CPC volume driver (Rs. 6.5/click)*
- **YouTube:** ~7.0% (Rs. 70,000) — *High-reach brand awareness*
- **Total:** **Exactly Rs. 1,000,000.00 (100.0%)**
- **Projected Return:** **~Rs. 3,180,000 Gross Revenue (~3.18x Blended ROAS)**

