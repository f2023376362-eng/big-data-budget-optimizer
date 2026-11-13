"""
Page 4: Audience Insights
Demographic, geographic, and device segmentation:
Age groups, Gender, City performance (Karachi, Lahore, etc.), and Device breakdowns.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.audience_analytics import AudienceAnalyticsEngine

st.title("👥 Audience & Demographic Intelligence")

df = st.session_state.get("active_df")
if df is None or df.empty:
    st.warning("No active dataset loaded. Please go to 'Dataset Management' first.")
    st.stop()

engine = AudienceAnalyticsEngine(df)
age_df = engine.get_age_performance()
gender_df = engine.get_gender_performance()
city_df = engine.get_city_performance()
dev_df = engine.get_device_performance()

tab_age, tab_city, tab_gender, tab_dev = st.tabs([
    "🎂 Age Groups",
    "🏙️ Geographical Cities",
    "🚻 Gender Breakdown",
    "📱 Device Category",
])

# ----------------- TAB 1: AGE GROUPS -----------------
with tab_age:
    st.markdown("### Advertising Performance by Age Bracket")
    col1, col2 = st.columns(2)
    with col1:
        fig_age_rev = px.bar(
            age_df,
            x="age",
            y="revenue",
            color="roas",
            text="roas",
            title="Revenue & ROAS by Age Bracket",
            color_continuous_scale="Purples",
        )
        fig_age_rev.update_traces(texttemplate="%{text:.2f}x", textposition="outside")
        fig_age_rev.update_layout(height=380)
        st.plotly_chart(fig_age_rev, use_container_width=True)

    with col2:
        fig_age_conv = px.bar(
            age_df,
            x="age",
            y="conversions",
            color="cpa",
            text="conversions",
            title="Conversions & CPA by Age Bracket",
            color_continuous_scale="Teal",
        )
        fig_age_conv.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_age_conv.update_layout(height=380)
        st.plotly_chart(fig_age_conv, use_container_width=True)

    st.dataframe(
        age_df.style.format({
            "spend": "Rs. {:,.2f}",
            "revenue": "Rs. {:,.2f}",
            "roas": "{:.2f}x",
            "impressions": "{:,}",
            "clicks": "{:,}",
            "ctr": "{:.2f}%",
            "conversions": "{:,}",
            "cpa": "Rs. {:.2f}",
            "conversion_rate": "{:.2f}%",
        }),
        use_container_width=True,
    )

# ----------------- TAB 2: GEOGRAPHICAL CITIES -----------------
with tab_city:
    st.markdown("### Regional City Performance (Pakistan Markets)")
    col_c1, col_c2 = st.columns([3, 2])
    with col_c1:
        fig_city = px.bar(
            city_df.sort_values(by="revenue", ascending=True),
            x="revenue",
            y="city",
            orientation="h",
            color="roas",
            text="revenue",
            title="Top Cities by Gross Advertising Revenue",
            color_continuous_scale="Blues",
        )
        fig_city.update_traces(texttemplate="Rs. %{text:,.0f}", textposition="outside")
        fig_city.update_layout(height=420)
        st.plotly_chart(fig_city, use_container_width=True)

    with col_c2:
        st.markdown("#### Regional Summary")
        st.dataframe(
            city_df[["city", "revenue", "spend", "roas", "conversions"]].style.format({
                "revenue": "Rs. {:,.0f}",
                "spend": "Rs. {:,.0f}",
                "roas": "{:.2f}x",
                "conversions": "{:,}",
            }),
            use_container_width=True,
            hide_index=True,
        )

# ----------------- TAB 3: GENDER -----------------
with tab_gender:
    st.markdown("### Performance Breakdown by Audience Gender")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_gender_pie = px.pie(
            gender_df,
            names="gender",
            values="revenue",
            title="Revenue Contribution by Gender",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_gender_pie.update_layout(height=380)
        st.plotly_chart(fig_gender_pie, use_container_width=True)

    with col_g2:
        fig_gender_bar = px.bar(
            gender_df,
            x="gender",
            y="conversions",
            color="cpa",
            text="cpa",
            title="Conversions & CPA by Gender",
            color_continuous_scale="Sunset",
        )
        fig_gender_bar.update_traces(texttemplate="Rs. %{text:.1f}", textposition="outside")
        fig_gender_bar.update_layout(height=380)
        st.plotly_chart(fig_gender_bar, use_container_width=True)

# ----------------- TAB 4: DEVICES -----------------
with tab_dev:
    st.markdown("### Device Distribution & Efficiency")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_dev_donut = px.pie(
            dev_df,
            names="device",
            values="spend",
            title="Ad Spend Share by Device",
            hole=0.45,
            color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
        )
        st.plotly_chart(fig_dev_donut, use_container_width=True)

    with col_d2:
        fig_dev_roas = px.bar(
            dev_df,
            x="device",
            y="roas",
            color="device",
            text="roas",
            title="ROAS by Device Category",
            color_discrete_sequence=["#3B82F6", "#10B981", "#F59E0B"],
        )
        fig_dev_roas.update_traces(texttemplate="%{text:.2f}x", textposition="outside")
        st.plotly_chart(fig_dev_roas, use_container_width=True)

