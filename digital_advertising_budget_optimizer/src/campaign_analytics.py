"""
Campaign and Platform Analytics Engine.
Performs multi-dimensional aggregations, KPI calculations,
efficiency frontier analysis, and identifies high-performing vs underperforming campaigns.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np
from src.advertising_metrics import (
    calculate_ctr,
    calculate_cpc,
    calculate_cpa,
    calculate_cvr,
    calculate_roas,
    compute_aggregate_metrics,
)


class CampaignAnalyticsEngine:
    """
    Computes analytical breakdowns across platforms, campaigns, and time series.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_platform_performance(self) -> pd.DataFrame:
        """
        Aggregates metrics for each advertising platform.
        Calculates CTR, CPC, CPA, CVR, ROAS, and net profit.
        """
        if self.df.empty:
            return pd.DataFrame()

        grouped = self.df.groupby("platform").agg(
            total_records=("date", "count"),
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        grouped["ctr"] = calculate_ctr(grouped["clicks"], grouped["impressions"]).round(2)
        grouped["cpc"] = calculate_cpc(grouped["spend"], grouped["clicks"]).round(2)
        grouped["cpa"] = calculate_cpa(grouped["spend"], grouped["conversions"]).round(2)
        grouped["conversion_rate"] = calculate_cvr(grouped["conversions"], grouped["clicks"]).round(2)
        grouped["roas"] = calculate_roas(grouped["revenue"], grouped["spend"]).round(2)
        grouped["net_profit"] = (grouped["revenue"] - grouped["spend"]).round(2)

        # Budget share
        total_spend = grouped["spend"].sum()
        grouped["spend_share"] = ((grouped["spend"] / total_spend * 100.0) if total_spend > 0 else 0.0).round(2)

        return grouped.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    def get_campaign_performance(self) -> pd.DataFrame:
        """
        Aggregates metrics across individual marketing campaigns.
        """
        if self.df.empty:
            return pd.DataFrame()

        grouped = self.df.groupby(["campaign", "platform"]).agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        grouped["ctr"] = calculate_ctr(grouped["clicks"], grouped["impressions"]).round(2)
        grouped["cpc"] = calculate_cpc(grouped["spend"], grouped["clicks"]).round(2)
        grouped["cpa"] = calculate_cpa(grouped["spend"], grouped["conversions"]).round(2)
        grouped["conversion_rate"] = calculate_cvr(grouped["conversions"], grouped["clicks"]).round(2)
        grouped["roas"] = calculate_roas(grouped["revenue"], grouped["spend"]).round(2)
        grouped["net_profit"] = (grouped["revenue"] - grouped["spend"]).round(2)

        return grouped.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    def get_daily_trends(self) -> pd.DataFrame:
        """
        Daily time-series aggregations for trend analysis.
        """
        if self.df.empty:
            return pd.DataFrame()

        daily = self.df.groupby("date").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily.sort_values("date").reset_index(drop=True)
        daily["ctr"] = calculate_ctr(daily["clicks"], daily["impressions"]).round(2)
        daily["cpc"] = calculate_cpc(daily["spend"], daily["clicks"]).round(2)
        daily["cpa"] = calculate_cpa(daily["spend"], daily["conversions"]).round(2)
        daily["roas"] = calculate_roas(daily["revenue"], daily["spend"]).round(2)
        daily["net_profit"] = (daily["revenue"] - daily["spend"]).round(2)

        return daily

    def get_monthly_trends(self) -> pd.DataFrame:
        """
        Monthly aggregated performance trends.
        """
        if self.df.empty:
            return pd.DataFrame()

        work_df = self.df.copy()
        work_df["month"] = pd.to_datetime(work_df["date"]).dt.to_period("M").astype(str)

        monthly = work_df.groupby("month").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        monthly["ctr"] = calculate_ctr(monthly["clicks"], monthly["impressions"]).round(2)
        monthly["cpc"] = calculate_cpc(monthly["spend"], monthly["clicks"]).round(2)
        monthly["cpa"] = calculate_cpa(monthly["spend"], monthly["conversions"]).round(2)
        monthly["roas"] = calculate_roas(monthly["revenue"], monthly["spend"]).round(2)
        monthly["net_profit"] = (monthly["revenue"] - monthly["spend"]).round(2)

        return monthly.sort_values("month").reset_index(drop=True)

    def identify_key_insights(self) -> Dict[str, Any]:
        """
        Identifies top performers, worst performers, and key business trade-offs.
        """
        platform_df = self.get_platform_performance()
        campaign_df = self.get_campaign_performance()

        if platform_df.empty:
            return {}

        highest_rev_platform = platform_df.loc[platform_df["revenue"].idxmax()]
        lowest_cpa_platform = platform_df.loc[platform_df["cpa"].idxmin()]
        highest_roas_platform = platform_df.loc[platform_df["roas"].idxmax()]
        highest_ctr_platform = platform_df.loc[platform_df["ctr"].idxmax()]
        best_cvr_platform = platform_df.loc[platform_df["conversion_rate"].idxmax()]

        # Find best campaign by ROAS (with meaningful spend > median spend)
        median_spend = campaign_df["spend"].median()
        qualified_campaigns = campaign_df[campaign_df["spend"] >= median_spend]
        if qualified_campaigns.empty:
            qualified_campaigns = campaign_df

        best_campaign = qualified_campaigns.loc[qualified_campaigns["roas"].idxmax()]

        # Identify poor performing campaigns: spend above median but ROAS below 1.5 or CPA > 75th percentile
        cpa_threshold = campaign_df["cpa"].quantile(0.75)
        underperforming = campaign_df[
            (campaign_df["spend"] >= median_spend) &
            ((campaign_df["roas"] < 1.8) | (campaign_df["cpa"] >= cpa_threshold))
        ].sort_values(by="spend", ascending=False)

        return {
            "highest_revenue_platform": {
                "platform": highest_rev_platform["platform"],
                "revenue": highest_rev_platform["revenue"],
                "roas": highest_rev_platform["roas"],
            },
            "lowest_cpa_platform": {
                "platform": lowest_cpa_platform["platform"],
                "cpa": lowest_cpa_platform["cpa"],
                "conversions": lowest_cpa_platform["conversions"],
            },
            "highest_roas_platform": {
                "platform": highest_roas_platform["platform"],
                "roas": highest_roas_platform["roas"],
                "revenue": highest_roas_platform["revenue"],
            },
            "highest_ctr_platform": {
                "platform": highest_ctr_platform["platform"],
                "ctr": highest_ctr_platform["ctr"],
            },
            "best_cvr_platform": {
                "platform": best_cvr_platform["platform"],
                "conversion_rate": best_cvr_platform["conversion_rate"],
            },
            "best_campaign": {
                "name": best_campaign["campaign"],
                "platform": best_campaign["platform"],
                "roas": best_campaign["roas"],
                "revenue": best_campaign["revenue"],
                "spend": best_campaign["spend"],
            },
            "underperforming_campaigns": underperforming[["campaign", "platform", "spend", "revenue", "roas", "cpa"]].head(5).to_dict(orient="records"),
        }

