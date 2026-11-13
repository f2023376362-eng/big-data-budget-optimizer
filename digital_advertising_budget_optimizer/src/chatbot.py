"""
Analytics Assistant / Chatbot Module.
Answers natural language analytical questions about active campaign datasets,
metrics (CTR, CPC, CPA, ROAS, Revenue), platform comparisons, audience performance,
and budget recommendations with zero fabricated numbers.
"""

import re
from typing import Dict, Any, Optional, List
import pandas as pd
from src.campaign_analytics import CampaignAnalyticsEngine
from src.audience_analytics import AudienceAnalyticsEngine
from src.budget_optimizer import BudgetOptimizer
from src.advertising_metrics import compute_aggregate_metrics
import config


class AdvertisingAnalyticsAssistant:
    """
    Intelligent rule-based analytical assistant for digital advertising data.
    """

    def __init__(self, df: Optional[pd.DataFrame] = None):
        self.df = df
        self.update_data(df)

    def update_data(self, df: Optional[pd.DataFrame]):
        """Refreshes active dataset reference and precomputes key metrics."""
        self.df = df
        if df is not None and not df.empty:
            self.camp_engine = CampaignAnalyticsEngine(df)
            self.aud_engine = AudienceAnalyticsEngine(df)
            self.optimizer = BudgetOptimizer(df)
            self.overall = compute_aggregate_metrics(df)
            self.insights = self.camp_engine.identify_key_insights()
            self.platform_df = self.camp_engine.get_platform_performance()
        else:
            self.camp_engine = None
            self.aud_engine = None
            self.optimizer = None
            self.overall = {}
            self.insights = {}
            self.platform_df = pd.DataFrame()

    def answer_query(self, query: str) -> str:
        """
        Processes natural language user questions and returns data-grounded responses.
        """
        if self.df is None or self.df.empty:
            return (
                "⚠️ **No dataset is currently loaded.** Please generate or upload an advertising dataset "
                "in the **Dataset Management** tab so I can compute real metrics for you."
            )

        q = query.lower().strip()

        # 1. Highest Revenue Platform
        if any(w in q for w in ["highest revenue", "most revenue", "max revenue", "top revenue", "best revenue"]):
            top = self.insights.get("highest_revenue_platform", {})
            return (
                f"📊 **Highest Revenue Platform:**\n\n"
                f"**{top.get('platform', 'N/A')}** leads all channels, generating "
                f"**Rs. {top.get('revenue', 0):,.2f}** in gross revenue with an average **{top.get('roas', 0):.2f}x ROAS**."
            )

        # 2. Highest ROAS Platform
        if any(w in q for w in ["best roas", "highest roas", "top roas", "max roas", "most profitable"]):
            top = self.insights.get("highest_roas_platform", {})
            return (
                f"📈 **Highest ROAS Platform:**\n\n"
                f"**{top.get('platform', 'N/A')}** delivers the highest capital efficiency at "
                f"**{top.get('roas', 0):.2f}x ROAS** (Total Revenue: Rs. {top.get('revenue', 0):,.2f}). "
                f"For every 1 rupee spent, it produces Rs. {top.get('roas', 0):.2f} in return."
            )

        # 3. Lowest CPA / Cost Per Acquisition
        if any(w in q for w in ["lowest cpa", "cheapest acquisition", "best cpa", "min cpa", "cost per acquisition"]):
            top = self.insights.get("lowest_cpa_platform", {})
            return (
                f"🎯 **Lowest CPA Platform:**\n\n"
                f"**{top.get('platform', 'N/A')}** achieves the most cost-effective acquisitions at "
                f"**Rs. {top.get('cpa', 0):,.2f} per conversion**, securing **{top.get('conversions', 0):,} total conversions**."
            )

        # 4. Average CPC / Cost Per Click
        if any(w in q for w in ["cpc", "cost per click", "average cpc", "cheapest click"]):
            overall_cpc = self.overall.get("cpc", 0.0)
            lowest_cpc_plat = self.platform_df.loc[self.platform_df["cpc"].idxmin()]
            highest_cpc_plat = self.platform_df.loc[self.platform_df["cpc"].idxmax()]
            return (
                f"🖱️ **Cost Per Click (CPC) Analysis:**\n\n"
                f"- **Overall Portfolio Average CPC:** Rs. {overall_cpc:,.2f}\n"
                f"- **Cheapest Clicks:** **{lowest_cpc_plat['platform']}** at Rs. {lowest_cpc_plat['cpc']:,.2f} / click\n"
                f"- **Most Expensive Clicks:** **{highest_cpc_plat['platform']}** at Rs. {highest_cpc_plat['cpc']:,.2f} / click"
            )

        # 5. Best Performing Campaign
        if any(w in q for w in ["best campaign", "top campaign", "most efficient campaign", "winning campaign"]):
            bc = self.insights.get("best_campaign", {})
            return (
                f"🏆 **Top Performing Campaign:**\n\n"
                f"**\"{bc.get('name', 'N/A')}\"** on **{bc.get('platform', 'N/A')}**\n"
                f"- **ROAS:** {bc.get('roas', 0):.2f}x\n"
                f"- **Revenue:** Rs. {bc.get('revenue', 0):,.2f}\n"
                f"- **Ad Spend:** Rs. {bc.get('spend', 0):,.2f}\n"
                f"- **Net Profit:** Rs. {(bc.get('revenue', 0) - bc.get('spend', 0)):,.2f}"
            )

        # 6. Poor performing campaigns / budget sinks
        if any(w in q for w in ["poor", "worst", "underperforming", "losing", "waste", "sink"]):
            under = self.insights.get("underperforming_campaigns", [])
            if not under:
                return "✅ No severely underperforming campaigns were detected with ROAS below 1.5."
            resp = ["⚠️ **Underperforming Campaigns Identified (High Spend / Low Return):**\n"]
            for idx, c in enumerate(under[:3], 1):
                resp.append(
                    f"{idx}. **{c['campaign']}** ({c['platform']}): Spent Rs. {c['spend']:,.2f} "
                    f"yielding only {c['roas']:.2f}x ROAS (CPA: Rs. {c['cpa']:,.2f}). Recommendation: pause or revise creative."
                )
            return "\n".join(resp)

        # 7. How to spend Rs. 1 million / Budget distribution
        if any(w in q for w in ["1 million", "1,000,000", "distribute", "allocate", "spend the next", "budget"]):
            rec = self.optimizer.optimize_budget(total_budget=1_000_000.0, strategy="Balanced Optimization")
            resp = [
                "💡 **Recommended Distribution for Rs. 1,000,000 (Balanced Strategy):**\n\n"
                "Management should allocate the next Rs. 1M as follows:\n"
            ]
            for a in rec["allocations"]:
                resp.append(
                    f"- **{a['platform']}:** {a['allocated_percentage']:.1f}% (Rs. {a['allocated_amount']:,.2f}) — *{a['action']}* ({a['rationale']})"
                )
            proj = rec["projections"]
            resp.append(
                f"\n**Projected Outcomes:** Expected Revenue: **Rs. {proj['expected_revenue']:,.2f}** "
                f"({proj['expected_roas']:.2f}x overall ROAS), yielding **{proj['expected_conversions']:,} conversions**."
            )
            return "\n".join(resp)

        # 8. Audience Demographics / Gender / Age / City
        if any(w in q for w in ["audience", "demographic", "age", "gender", "city"]):
            age_df = self.aud_engine.get_age_performance()
            city_df = self.aud_engine.get_city_performance()
            top_age = age_df.loc[age_df["conversions"].idxmax()]
            top_city = city_df.loc[city_df["revenue"].idxmax()]
            return (
                f"👥 **Audience & Demographic Highlights:**\n\n"
                f"- **Top Age Group for Conversions:** **{top_age['age']}** with {top_age['conversions']:,} conversions "
                f"and {top_age['roas']:.2f}x ROAS.\n"
                f"- **Top City by Revenue:** **{top_city['city']}** generating Rs. {top_city['revenue']:,.2f} in revenue "
                f"with {top_city['roas']:.2f}x ROAS."
            )

        # 9. Overall Summary
        if any(w in q for w in ["summary", "overview", "total", "overall", "performance"]):
            return (
                f"📋 **Overall Portfolio Summary:**\n\n"
                f"- **Total Ad Spend:** Rs. {self.overall.get('total_spend', 0):,.2f}\n"
                f"- **Total Revenue:** Rs. {self.overall.get('total_revenue', 0):,.2f}\n"
                f"- **Net Profit:** Rs. {self.overall.get('net_profit', 0):,.2f}\n"
                f"- **Overall ROAS:** {self.overall.get('roas', 0):.2f}x\n"
                f"- **Total Impressions:** {self.overall.get('total_impressions', 0):,}\n"
                f"- **Total Clicks:** {self.overall.get('total_clicks', 0):,} (CTR: {self.overall.get('ctr', 0):.2f}%)\n"
                f"- **Total Conversions:** {self.overall.get('total_conversions', 0):,} (CVR: {self.overall.get('cvr', 0):.2f}%)\n"
                f"- **Average CPC:** Rs. {self.overall.get('cpc', 0):.2f} | **Average CPA:** Rs. {self.overall.get('cpa', 0):.2f}"
            )

        # Default fallback
        return (
            "🤖 **Analytics Assistant Guidance:**\n\n"
            "I could not match your exact question to an analytical category. Here are suggested questions I can answer accurately from your data:\n\n"
            "1. *Which platform generated the most revenue?*\n"
            "2. *Which platform has the best ROAS?*\n"
            "3. *What is the average CPC and CPA across platforms?*\n"
            "4. *Which campaign performed best?*\n"
            "5. *Which campaigns have poor or underperforming results?*\n"
            "6. *How should we distribute Rs. 1 million?*\n"
            "7. *Which audience group and city generated the most conversions?*\n"
            "8. *Give me an overall performance summary.*"
        )

