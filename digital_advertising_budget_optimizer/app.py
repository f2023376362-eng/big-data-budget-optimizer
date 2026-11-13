"""
Digital Advertising Budget Optimizer — Big Data Analytics System
Main Streamlit Application Entry Point.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from src.data_generator import ensure_dataset
from src.data_cleaning import DataCleaner
from src.database import DatabaseManager
from src.advertising_metrics import compute_aggregate_metrics

# Page configuration
st.set_page_config(
    page_title="Digital Advertising Budget Optimizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for university-grade UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #10B981;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_db():
    return DatabaseManager()


@st.cache_data
def load_initial_data():
    """Loads or generates the default 10k baseline dataset for instant exploration."""
    default_csv = ensure_dataset(10_000)
    df = pd.read_csv(default_csv)
    cleaner = DataCleaner()
    cleaned_df, _ = cleaner.clean(df)
    return cleaned_df


# Global session state initialization
if "active_df" not in st.session_state:
    st.session_state["active_df"] = load_initial_data()

if "dataset_name" not in st.session_state:
    st.session_state["dataset_name"] = "Default Synthetic Dataset (10,000 records)"

# Sidebar Controls & Navigation Info
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400&auto=format&fit=crop&q=60",
        caption="Ad Tech Analytics Hub",
        use_container_width=True,
    )
    st.markdown("### 💼 Decision Support System")
    st.info(
        "**Core Business Problem:**\n\n"
        "*'Where should we spend the next Rs. 1,000,000 across Facebook, Instagram, Google, TikTok, "
        "and YouTube to maximize advertising ROI?'*"
    )

    st.markdown("---")
    st.markdown("#### 📂 Active Dataset")
    st.caption(f"**Loaded:** {st.session_state.get('dataset_name', 'None')}")
    if st.session_state.get("active_df") is not None:
        st.caption(f"**Records:** {len(st.session_state['active_df']):,} rows")

    st.markdown("---")
    st.markdown("#### 🎓 Project Details")
    st.caption("**Student:** Hurrain Mustafa")
    st.caption("**Roll No:** F202333011")
    st.caption("**Course:** Big Data Analytics (Project 2)")


# Main Page Landing View
st.markdown('<div class="main-header">🎯 Digital Advertising Budget Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Big Data Analytics System comparing Pandas, MapReduce & Spark to optimize Rs. 1,000,000 media spend.</div>',
    unsafe_allow_html=True,
)

# Overview KPIs
df = st.session_state["active_df"]
metrics = compute_aggregate_metrics(df)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Spend", value=f"Rs. {metrics['total_spend']:,.0f}")
with col2:
    st.metric(label="Total Revenue", value=f"Rs. {metrics['total_revenue']:,.0f}")
with col3:
    st.metric(label="Overall ROAS", value=f"{metrics['roas']:.2f}x")
with col4:
    st.metric(label="Total Conversions", value=f"{metrics['total_conversions']:,}")

col5, col6, col7, col8 = st.columns(4)
with col5:
    st.metric(label="Impressions", value=f"{metrics['total_impressions']:,}")
with col6:
    st.metric(label="Clicks", value=f"{metrics['total_clicks']:,}")
with col7:
    st.metric(label="CTR", value=f"{metrics['ctr']:.2f}%")
with col8:
    st.metric(label="Avg CPC", value=f"Rs. {metrics['cpc']:.2f}")

st.markdown("---")

st.markdown("### 🧭 System Navigation & Capabilities")
st.markdown(
    """
    Use the sidebar pages to navigate the complete analytical suite:
    
    1. **📊 Executive Overview:** Executive scorecard, business challenge, and top platform breakdown.
    2. **💾 Dataset Management:** Generate 10K to 10M datasets, upload external CSV/Excel, validate schemas, clean data.
    3. **📈 Advertising Analytics:** Platform comparisons, campaign efficiency frontiers, CTR/CPC/CPA/ROAS trends.
    4. **👥 Audience Insights:** Age groups, gender, geographic cities (Karachi, Lahore, etc.), and device splits.
    5. **⚡ Big Data Lab:** Benchmark **Pandas vs MapReduce vs Apache Spark** with actual latency and throughput measurements.
    6. **💰 Budget Optimizer:** Mathematical allocation engine distributing **Rs. 1,000,000** across 3 strategies with expected ROI projections.
    7. **🗄️ Database Explorer:** SQLite normalized tables, record counts, and analytical SQL console.
    8. **📑 Reports:** Downloadable executive summaries, CSV exports, and printable PDF reports.
    9. **🤖 Analytics Assistant:** Deterministic chatbot providing verifiable, dataset-grounded answers.
    """
)

