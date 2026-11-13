"""
Audience Analytics Engine.
Analyzes demographic, geographic, and device breakdowns:
Age Groups, Gender, City, and Device performance.
"""

from typing import Dict, Any
import pandas as pd
from src.advertising_metrics import (
    calculate_ctr,
    calculate_cpc,
    calculate_cpa,
    calculate_cvr,
    calculate_roas,
)


class AudienceAnalyticsEngine:
    """
    Computes audience segmentation and behavioral insights.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def get_age_performance(self) -> pd.DataFrame:
        """Analyzes advertising efficiency across age brackets."""
        if self.df.empty:
            return pd.DataFrame()

        grouped = self.df.groupby("age").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        grouped["ctr"] = calculate_ctr(grouped["clicks"], grouped["impressions"]).round(2)
        grouped["cpa"] = calculate_cpa(grouped["spend"], grouped["conversions"]).round(2)
        grouped["conversion_rate"] = calculate_cvr(grouped["conversions"], grouped["clicks"]).round(2)
        grouped["roas"] = calculate_roas(grouped["revenue"], grouped["spend"]).round(2)

        return grouped.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    def get_gender_performance(self) -> pd.DataFrame:
        """Analyzes metrics by audience gender."""
        if self.df.empty:
            return pd.DataFrame()

        grouped = self.df.groupby("gender").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        grouped["ctr"] = calculate_ctr(grouped["clicks"], grouped["impressions"]).round(2)
        grouped["cpa"] = calculate_cpa(grouped["spend"], grouped["conversions"]).round(2)
        grouped["conversion_rate"] = calculate_cvr(grouped["conversions"], grouped["clicks"]).round(2)
        grouped["roas"] = calculate_roas(grouped["revenue"], grouped["spend"]).round(2)

        return grouped.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    def get_city_performance(self) -> pd.DataFrame:
        """Analyzes performance across major geographical locations."""
        if self.df.empty:
            return pd.DataFrame()

        grouped = self.df.groupby("city").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        grouped["ctr"] = calculate_ctr(grouped["clicks"], grouped["impressions"]).round(2)
        grouped["cpa"] = calculate_cpa(grouped["spend"], grouped["conversions"]).round(2)
        grouped["conversion_rate"] = calculate_cvr(grouped["conversions"], grouped["clicks"]).round(2)
        grouped["roas"] = calculate_roas(grouped["revenue"], grouped["spend"]).round(2)

        return grouped.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    def get_device_performance(self) -> pd.DataFrame:
        """Analyzes efficiency across device categories (Mobile, Desktop, Tablet)."""
        if self.df.empty:
            return pd.DataFrame()

        grouped = self.df.groupby("device").agg(
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

        return grouped.sort_values(by="revenue", ascending=False).reset_index(drop=True)

