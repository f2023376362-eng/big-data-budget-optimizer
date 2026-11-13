"""
Page 3: Advertising Analytics
Platform comparison, campaign efficiency frontier, metric deep dives (CTR, CPC, CPA, ROAS),
and daily/monthly trend tracking.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.campaign_analytics import CampaignAnalyticsEngine

st.title("📈 Advertising Analytics & Campaign Performance")

df = st.session_state.get("active_df")
if df is None or df.empty:
    st.warning("No active dataset loaded. Please go to 'Dataset Management' first.")
    st.stop()

engine = CampaignAnalyticsEngine(df)
platform_df = engine.get_platform_performance()
campaign_df = engine.get_campaign_performance()
daily_df = engine.get_daily_trends()
monthly_df = engine.get_monthly_trends()
insights = engine.identify_key_insights()

tab_plat, tab_camp, tab_trends = st.tabs([
    "🏢 Platform Comparison",
    "🎯 Campaign Efficiency Frontier",
    "📅 Time-Series Trends (Daily & Monthly)",
])

# ----------------- TAB 1: PLATFORM COMPARISON -----------------
with tab_plat:
    st.markdown("### Cross-Platform Efficiency Metrics")
    metric_choice = st.selectbox(
        "Select Performance Metric to Compare:",
        options=["roas", "revenue", "spend", "cpa", "cpc", "conversion_rate", "ctr"],
        format_func=lambda x: {
            "roas": "Return on Ad Spend (ROAS)",
            "revenue": "Gross Revenue (PKR)",
            "spend": "Advertising Expenditure (PKR)",
            "cpa": "Cost Per Acquisition (CPA in PKR)",
            "cpc": "Cost Per Click (CPC in PKR)",
            "conversion_rate": "Conversion Rate (%)",
            "ctr": "Click-Through Rate (CTR %)",
        }[x],
        index=0,
    )

    col_chart, col_data = st.columns([3, 2])
    with col_chart:
        fig_metric = px.bar(
            platform_df.sort_values(by=metric_choice, ascending=False),
            x="platform",
            y=metric_choice,
            color="platform",
            text=metric_choice,
            title=f"Platform Comparison: {metric_choice.upper()}",
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        if metric_choice in ["revenue", "spend", "cpa", "cpc"]:
            fig_metric.update_traces(texttemplate="Rs. %{text:,.2f}", textposition="outside")
        elif metric_choice in ["ctr", "conversion_rate"]:
            fig_metric.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        else:
            fig_metric.update_traces(texttemplate="%{text:.2f}x", textposition="outside")

        fig_metric.update_layout(height=400, showlegend=False, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_metric, use_container_width=True)

    with col_data:
        st.markdown(f"#### Ranked by {metric_choice.upper()}")
        table_sub = platform_df[["platform", metric_choice, "spend", "revenue"]].copy()
        table_sub.columns = ["Platform", metric_choice.upper(), "Spend (PKR)", "Revenue (PKR)"]
        st.dataframe(table_sub, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### ⚖️ Efficiency Matrix: CPA vs ROAS by Platform")
    fig_bubble = px.scatter(
        platform_df,
        x="cpa",
        y="roas",
        size="conversions",
        color="platform",
        hover_name="platform",
        text="platform",
        labels={"cpa": "Cost Per Acquisition (PKR) — Lower is Better", "roas": "ROAS (Ratio) — Higher is Better"},
    )
    fig_bubble.update_traces(textposition="top center")
    fig_bubble.update_layout(height=420)
    st.plotly_chart(fig_bubble, use_container_width=True)

# ----------------- TAB 2: CAMPAIGN FRONTIER -----------------
with tab_camp:
    st.markdown("### Campaign Performance & Budget Sinks")
    st.caption("Identify winning campaigns driving high ROAS vs underperformers burning capital.")

    # Scatter of spend vs revenue
    fig_camp = px.scatter(
        campaign_df,
        x="spend",
        y="revenue",
        size="conversions",
        color="roas",
        hover_data=["campaign", "platform", "cpa", "conversion_rate"],
        color_continuous_scale="Viridis",
        title="Campaign Frontier: Spend vs Revenue (Bubble size = Conversions, Color = ROAS)",
    )
    fig_camp.update_layout(height=450)
    st.plotly_chart(fig_camp, use_container_width=True)

    # Top vs Underperforming
    col_best, col_under = st.columns(2)
    with col_best:
        st.markdown("#### 🌟 Top Campaigns by ROAS")
        best_df = campaign_df[campaign_df["spend"] > campaign_df["spend"].median()].sort_values(by="roas", ascending=False).head(5)
        st.dataframe(
            best_df[["campaign", "platform", "spend", "revenue", "roas", "conversions"]].style.format({
                "spend": "Rs. {:,.0f}",
                "revenue": "Rs. {:,.0f}",
                "roas": "{:.2f}x",
                "conversions": "{:,}",
            }),
            use_container_width=True,
            hide_index=True,
        )

    with col_under:
        st.markdown("#### ⚠️ Underperforming / High-Spend Sinks")
        under_df = campaign_df[
            (campaign_df["spend"] >= campaign_df["spend"].median()) &
            (campaign_df["roas"] < 1.8)
        ].sort_values(by="spend", ascending=False).head(5)
        if not under_df.empty:
            st.dataframe(
                under_df[["campaign", "platform", "spend", "revenue", "roas", "cpa"]].style.format({
                    "spend": "Rs. {:,.0f}",
                    "revenue": "Rs. {:,.0f}",
                    "roas": "{:.2f}x",
                    "cpa": "Rs. {:.2f}",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No high-spend campaigns have ROAS below 1.8.")

# ----------------- TAB 3: TRENDS -----------------
with tab_trends:
    st.markdown("### Daily Performance Dynamics")
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["spend"], mode="lines", name="Spend (PKR)", line=dict(color="#EF4444", width=2)))
    fig_daily.add_trace(go.Scatter(x=daily_df["date"], y=daily_df["revenue"], mode="lines", name="Revenue (PKR)", line=dict(color="#10B981", width=2)))
    fig_daily.update_layout(height=380, title="Daily Spend vs Gross Revenue", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_daily, use_container_width=True)

    st.markdown("### Monthly Financial Aggregations")
    fig_monthly = px.bar(
        monthly_df,
        x="month",
        y=["spend", "revenue", "net_profit"],
        barmode="group",
        title="Monthly Financial Overview (Spend, Revenue & Profit)",
        color_discrete_map={"spend": "#F87171", "revenue": "#60A5FA", "net_profit": "#34D399"},
    )
    fig_monthly.update_layout(height=380)
    st.plotly_chart(fig_monthly, use_container_width=True)

