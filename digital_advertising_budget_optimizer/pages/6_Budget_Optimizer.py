"""
Page 6: Budget Optimizer
Main Business Feature: Allocates the next Rs. 1,000,000 across Facebook, Instagram,
Google, TikTok, and YouTube using historical data, mathematical optimization,
and customizable constraints.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.budget_optimizer import BudgetOptimizer
from src.database import DatabaseManager
import config

st.title("💰 Marketing Budget Recommendation Engine")
st.markdown(
    "### Management Decision: *'Where should we invest the next Rs. 1,000,000?'*"
)

df = st.session_state.get("active_df")
if df is None or df.empty:
    st.warning("No active dataset loaded. Please go to 'Dataset Management' first.")
    st.stop()

optimizer = BudgetOptimizer(df)
db = DatabaseManager()

# Controls
st.markdown("### ⚙️ Optimization Parameters & Constraints")
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    budget_input = st.number_input(
        "Total Marketing Budget (PKR):",
        min_value=50_000.0,
        max_value=50_000_000.0,
        value=config.DEFAULT_BUDGET,
        step=50_000.0,
        format="%.2f",
    )

with col_p2:
    strategy_choice = st.selectbox(
        "Optimization Strategy:",
        options=["Balanced Optimization", "ROAS Maximization", "Conversion Maximization"],
        help=(
            "ROAS Maximization: Heavily weights return on ad spend.\n"
            "Conversion Maximization: Prioritizes low CPA and high conversion rate.\n"
            "Balanced Optimization: Blends ROAS, CPA, volume, and penalizes volatility."
        ),
    )

with col_p3:
    risk_choice = st.select_slider(
        "Risk Preference:",
        options=[0.1, 0.3, 0.5, 0.7, 0.9],
        value=0.5,
        format_func=lambda x: {
            0.1: "Very Conservative",
            0.3: "Conservative",
            0.5: "Moderate",
            0.7: "Growth / Aggressive",
            0.9: "Highly Aggressive",
        }[x],
    )

with st.expander("🛠️ Advanced Simplex Boundary Constraints", expanded=False):
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        min_cap = st.slider("Minimum Platform Allocation (%):", 0.0, 15.0, 5.0, step=1.0) / 100.0
    with c_col2:
        max_cap = st.slider("Maximum Platform Allocation (%):", 25.0, 60.0, 45.0, step=1.0) / 100.0

tab_rec, tab_compare = st.tabs(["🎯 Optimal Allocation Breakdown", "📊 Strategy Comparison Matrix"])

# ----------------- TAB 1: OPTIMAL ALLOCATION -----------------
with tab_rec:
    result = optimizer.optimize_budget(
        total_budget=budget_input,
        strategy=strategy_choice,
        min_allocation_pct=min_cap,
        max_allocation_pct=max_cap,
        risk_tolerance=risk_choice,
    )

    allocations = result["allocations"]
    alloc_df = pd.DataFrame(allocations)
    proj = result["projections"]

    # Budget Projections Header Cards
    st.markdown("#### 📈 Projected Campaign Outcomes (Rs. 1,000,000 Allocation)")
    pr1, pr2, pr3, pr4 = st.columns(4)
    with pr1:
        st.metric("Expected Revenue", f"Rs. {proj['expected_revenue']:,.0f}")
    with pr2:
        st.metric("Expected Net Profit", f"Rs. {proj['expected_net_profit']:,.0f}")
    with pr3:
        st.metric("Expected ROAS", f"{proj['expected_roas']:.2f}x")
    with pr4:
        st.metric("Expected Conversions", f"{proj['expected_conversions']:,}")

    st.caption(f"ℹ️ *{proj['disclaimer']}*")

    st.markdown("---")

    # Visual Charts
    col_pie, col_bar = st.columns([2, 3])
    with col_pie:
        st.markdown("#### 🍰 Recommended Channel Mix")
        fig_pie = px.pie(
            alloc_df,
            names="platform",
            values="allocated_amount",
            hole=0.45,
            color="platform",
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_pie.update_traces(textinfo="label+percent", hovertemplate="<b>%{label}</b><br>Amount: Rs. %{value:,.2f}<br>Share: %{percent}")
        fig_pie.update_layout(height=380, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_bar:
        st.markdown("#### 🔄 Current vs Recommended Allocation Shift")
        fig_shift = go.Figure()
        fig_shift.add_trace(go.Bar(
            x=alloc_df["platform"],
            y=alloc_df["current_percentage"],
            name="Current Historical Share (%)",
            marker_color="#94A3B8",
        ))
        fig_shift.add_trace(go.Bar(
            x=alloc_df["platform"],
            y=alloc_df["allocated_percentage"],
            name="Recommended Share (%)",
            marker_color="#2563EB",
        ))
        fig_shift.update_layout(
            barmode="group",
            height=380,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_shift, use_container_width=True)

    st.markdown("### 📋 Recommended Allocation Table")
    # Exact sum check verification
    total_allocated = alloc_df["allocated_amount"].sum()
    sum_color = "green" if abs(total_allocated - budget_input) < 0.01 else "red"
    st.markdown(
        f"**Total Capital Distributed:** <span style='color:{sum_color}; font-weight:700;'>"
        f"Rs. {total_allocated:,.2f} / Rs. {budget_input:,.2f}</span>",
        unsafe_allow_html=True,
    )

    styled_alloc = alloc_df[[
        "platform", "allocated_percentage", "allocated_amount", "action", "budget_shift",
        "historical_roas", "historical_cpa", "expected_conversions", "expected_revenue", "rationale"
    ]].copy()
    styled_alloc.columns = [
        "Platform", "Allocation (%)", "Amount (PKR)", "Action", "Shift (% pts)",
        "Hist ROAS", "Hist CPA (PKR)", "Proj Conversions", "Proj Revenue (PKR)", "Strategic Rationale"
    ]

    st.dataframe(
        styled_alloc.style.format({
            "Allocation (%)": "{:.1f}%",
            "Amount (PKR)": "Rs. {:,.2f}",
            "Shift (% pts)": "{:+.1f}%",
            "Hist ROAS": "{:.2f}x",
            "Hist CPA (PKR)": "Rs. {:.2f}",
            "Proj Conversions": "{:,}",
            "Proj Revenue (PKR)": "Rs. {:,.2f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # Save to Database Button
    if st.button("💾 Persist Recommendations to Database", type="secondary"):
        db.insert_budget_recommendations(result)
        st.success("✅ Recommendations saved to SQLite `budget_recommendations` table!")

# ----------------- TAB 2: MULTI-STRATEGY COMPARISON -----------------
with tab_compare:
    st.markdown("### Multi-Strategy Allocation Comparison")
    st.caption("Compare how budget is allocated across the 3 distinct business strategies.")

    strat_comp_df = optimizer.compare_all_strategies(total_budget=budget_input)

    fig_strat_bar = px.bar(
        strat_comp_df,
        x="Platform",
        y="Allocation (%)",
        color="Strategy",
        barmode="group",
        title=f"Platform Allocation Comparison across Strategies (Budget: Rs. {budget_input:,.0f})",
        color_discrete_map={
            "ROAS Maximization": "#10B981",
            "Conversion Maximization": "#3B82F6",
            "Balanced Optimization": "#8B5CF6",
        },
    )
    fig_strat_bar.update_layout(height=420)
    st.plotly_chart(fig_strat_bar, use_container_width=True)

    st.dataframe(
        strat_comp_df.style.format({
            "Allocation (%)": "{:.1f}%",
            "Allocated Budget (PKR)": "Rs. {:,.2f}",
            "Expected Conversions": "{:,}",
            "Expected Revenue (PKR)": "Rs. {:,.2f}",
            "Expected ROAS": "{:.2f}x",
        }),
        use_container_width=True,
        hide_index=True,
    )

