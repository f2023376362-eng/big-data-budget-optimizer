"""
Page 1: Executive Overview
High-level KPI scorecard, core business challenge, platform comparison, and strategic tradeoffs.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.advertising_metrics import compute_aggregate_metrics
from src.campaign_analytics import CampaignAnalyticsEngine

st.title("📊 Executive Overview & Business Problem")

df = st.session_state.get("active_df")
if df is None or df.empty:
    st.warning("No active dataset loaded. Please navigate to 'Dataset Management' to generate or upload data.")
    st.stop()

engine = CampaignAnalyticsEngine(df)
metrics = compute_aggregate_metrics(df)
platform_df = engine.get_platform_performance()
insights = engine.identify_key_insights()

# Strategic Business Challenge Banner
st.info(
    "🎯 **The Strategic Question for Management:**\n\n"
    "Our enterprise invests media budget across **Facebook, Instagram, Google, TikTok, and YouTube**. "
    "Management requires a data-driven recommendation for allocating the next **Rs. 1,000,000** "
    "to yield the strongest business impact, balancing immediate gross return (ROAS), acquisition cost (CPA), "
    "and audience reach."
)

st.markdown("### 📌 Executive KPI Scorecard")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="Total Spend", value=f"Rs. {metrics['total_spend']:,.0f}")
with kpi2:
    st.metric(label="Total Revenue", value=f"Rs. {metrics['total_revenue']:,.0f}")
with kpi3:
    net_p = metrics['net_profit']
    st.metric(label="Net Marketing Margin", value=f"Rs. {net_p:,.0f}", delta=f"{metrics['roas']:.2f}x ROAS")
with kpi4:
    st.metric(label="Total Conversions", value=f"{metrics['total_conversions']:,}")

kpi5, kpi6, kpi7, kpi8 = st.columns(4)
with kpi5:
    st.metric(label="Total Impressions", value=f"{metrics['total_impressions']:,}")
with kpi6:
    st.metric(label="Total Clicks", value=f"{metrics['total_clicks']:,}")
with kpi7:
    st.metric(label="Click-Through Rate (CTR)", value=f"{metrics['ctr']:.2f}%")
with kpi8:
    st.metric(label="Cost Per Acquisition (CPA)", value=f"Rs. {metrics['cpa']:.2f}")

st.markdown("---")

# Key Automated Strategic Highlights
st.markdown("### 🏆 Channel Performance Leaders")
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1:
    top_rev = insights.get("highest_revenue_platform", {})
    st.success(
        f"**Highest Revenue Generator:**\n\n"
        f"### {top_rev.get('platform', 'N/A')}\n"
        f"**Rs. {top_rev.get('revenue', 0):,.0f}** generated ({top_rev.get('roas', 0):.2f}x ROAS)"
    )
with h_col2:
    top_roas = insights.get("highest_roas_platform", {})
    st.success(
        f"**Highest Capital Return (ROAS):**\n\n"
        f"### {top_roas.get('platform', 'N/A')}\n"
        f"**{top_roas.get('roas', 0):.2f}x ROAS** (Rs. {top_roas.get('revenue', 0):,.0f} revenue)"
    )
with h_col3:
    low_cpa = insights.get("lowest_cpa_platform", {})
    st.success(
        f"**Most Efficient CPA:**\n\n"
        f"### {low_cpa.get('platform', 'N/A')}\n"
        f"**Rs. {low_cpa.get('cpa', 0):,.2f}** per acquired customer"
    )

st.markdown("---")

# Visual Comparison: Revenue vs Spend by Platform & ROAS Ranking
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 💰 Spend vs Revenue Distribution by Platform")
    fig_spend_rev = go.Figure()
    fig_spend_rev.add_trace(go.Bar(
        x=platform_df["platform"],
        y=platform_df["spend"],
        name="Spend (PKR)",
        marker_color="#94A3B8"
    ))
    fig_spend_rev.add_trace(go.Bar(
        x=platform_df["platform"],
        y=platform_df["revenue"],
        name="Revenue (PKR)",
        marker_color="#2563EB"
    ))
    fig_spend_rev.update_layout(
        barmode="group",
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_spend_rev, use_container_width=True)

with col_chart2:
    st.markdown("#### 📈 Return on Ad Spend (ROAS) Ranking")
    fig_roas = px.bar(
        platform_df.sort_values(by="roas", ascending=True),
        x="roas",
        y="platform",
        orientation="h",
        text="roas",
        color="roas",
        color_continuous_scale="Blues",
    )
    fig_roas.update_traces(texttemplate="%{text:.2f}x", textposition="outside")
    fig_roas.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_roas, use_container_width=True)

st.markdown("### 📋 Platform Scorecard Data Table")
styled_df = platform_df[[
    "platform", "spend", "revenue", "net_profit", "roas", "impressions", "clicks", "ctr", "cpc", "conversions", "cpa", "conversion_rate"
]].copy()
styled_df.columns = [
    "Platform", "Spend (PKR)", "Revenue (PKR)", "Net Profit (PKR)", "ROAS", "Impressions", "Clicks", "CTR (%)", "CPC (PKR)", "Conversions", "CPA (PKR)", "CVR (%)"
]
st.dataframe(
    styled_df.style.format({
        "Spend (PKR)": "Rs. {:,.2f}",
        "Revenue (PKR)": "Rs. {:,.2f}",
        "Net Profit (PKR)": "Rs. {:,.2f}",
        "ROAS": "{:.2f}x",
        "Impressions": "{:,}",
        "Clicks": "{:,}",
        "CTR (%)": "{:.2f}%",
        "CPC (PKR)": "Rs. {:.2f}",
        "Conversions": "{:,}",
        "CPA (PKR)": "Rs. {:.2f}",
        "CVR (%)": "{:.2f}%",
    }),
    use_container_width=True,
)

st.markdown("---")
st.markdown("### ⚖️ Strategic Trade-offs Analysis")
st.markdown(
    """
    > **Key Management Takeaway:** A platform should **never** be evaluated on a single metric in isolation:
    > - **Google** typically achieves high intent and top ROAS, but has higher CPC and saturation limits.
    > - **TikTok** delivers high volume, high CTR, and inexpensive clicks, but has lower average basket sizes and modest conversion rates.
    > - **Instagram & Facebook** provide reliable mid-funnel scaling with predictable acquisition costs.
    > - **YouTube** drives broad brand recall with high impressions, but requires higher attribution timeframes for direct sales.
    >
    > The **Budget Optimizer (Page 6)** uses mathematical weighting to balance these distinct strengths.
    """
)

