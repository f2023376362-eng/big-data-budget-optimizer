"""
Data validation module for external and internal digital advertising datasets.
Validates schemas, types, logical boundaries (e.g., clicks <= impressions),
and maps equivalent column names from third-party exports.
"""

from typing import Dict, List, Tuple, Any, Optional
import pandas as pd
import numpy as np


# Common synonyms for column mapping from external ad tools (Meta Ads, Google Ads, TikTok Ads)
COLUMN_ALIASES: Dict[str, List[str]] = {
    "date": ["date", "day", "record_date", "timestamp", "ad_date"],
    "campaign": ["campaign", "campaign_name", "ad_campaign", "utm_campaign", "campaignname"],
    "platform": ["platform", "ad_platform", "channel", "network", "media_source", "source"],
    "impressions": ["impressions", "impr", "views", "ad_impressions", "total_impressions"],
    "clicks": ["clicks", "link_clicks", "ad_clicks", "total_clicks"],
    "spend": ["spend", "cost", "ad_spend", "amount_spent", "budget_spent", "investment"],
    "conversions": ["conversions", "purchases", "acquisitions", "leads", "orders", "conv"],
    "revenue": ["revenue", "sales", "order_value", "total_revenue", "conv_value"],
    "age": ["age", "age_group", "audience_age", "demographic_age"],
    "gender": ["gender", "audience_gender", "sex"],
    "city": ["city", "location", "region", "geo", "audience_city"],
    "device": ["device", "device_type", "platform_device", "device_category"],
}


class DatasetValidator:
    """
    Validates uploaded and synthetic datasets for digital advertising analytics.
    """

    def __init__(self, required_columns: Optional[List[str]] = None):
        self.required_columns = required_columns or list(COLUMN_ALIASES.keys())

    def detect_column_mapping(self, df_columns: List[str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Attempts to map arbitrary user column names to standardized system names.
        Returns (mapping_dict: standard_col -> input_col, missing_standard_cols: list)
        """
        lower_cols = {str(c).strip().lower(): c for c in df_columns}
        mapping: Dict[str, str] = {}
        missing: List[str] = []

        for standard_col, aliases in COLUMN_ALIASES.items():
            found = False
            for alias in aliases:
                if alias.lower() in lower_cols:
                    mapping[standard_col] = lower_cols[alias.lower()]
                    found = True
                    break
            if not found and standard_col in self.required_columns:
                missing.append(standard_col)

        return mapping, missing

    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Performs thorough structural and semantic data validation.
        """
        report: Dict[str, Any] = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "null_cells": int(df.isna().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "invalid_metric_rows": 0,
            },
            "column_status": {},
        }

        # Check required columns
        mapping, missing = self.detect_column_mapping(df.columns.tolist())
        if missing:
            report["is_valid"] = False
            report["errors"].append(
                f"Missing critical advertising columns: {', '.join(missing)}. "
                f"Cannot conduct optimization without these core metrics."
            )
            return report

        # Test metrics boundaries if columns present
        # Normalize mapped view for validation
        mapped_df = df.rename(columns={v: k for k, v in mapping.items()})

        # Check numeric conversions
        numeric_cols = ["impressions", "clicks", "spend", "conversions", "revenue"]
        for col in numeric_cols:
            if col in mapped_df.columns:
                non_num_count = pd.to_numeric(mapped_df[col], errors="coerce").isna().sum()
                if non_num_count > 0:
                    report["warnings"].append(
                        f"Column '{col}' contains {non_num_count} non-numeric or missing entries."
                    )

        # Ensure non-negative and logical bounds
        try:
            work_df = mapped_df.copy()
            for col in numeric_cols:
                work_df[col] = pd.to_numeric(work_df[col], errors="coerce").fillna(0)

            # Check spend & revenue >= 0
            negative_spend = (work_df["spend"] < 0).sum()
            if negative_spend > 0:
                report["errors"].append(f"Found {negative_spend} records with negative spend.")
                report["is_valid"] = False

            negative_rev = (work_df["revenue"] < 0).sum()
            if negative_rev > 0:
                report["errors"].append(f"Found {negative_rev} records with negative revenue.")
                report["is_valid"] = False

            # Clicks cannot exceed impressions
            clicks_exceed = (work_df["clicks"] > work_df["impressions"]).sum()
            if clicks_exceed > 0:
                report["warnings"].append(
                    f"Found {clicks_exceed} records where clicks exceed impressions (logical impossibility)."
                )
                report["summary"]["invalid_metric_rows"] += int(clicks_exceed)

            # Conversions cannot exceed clicks
            conv_exceed = (work_df["conversions"] > work_df["clicks"]).sum()
            if conv_exceed > 0:
                report["warnings"].append(
                    f"Found {conv_exceed} records where conversions exceed clicks (logical anomaly)."
                )
                report["summary"]["invalid_metric_rows"] += int(conv_exceed)

        except Exception as e:
            report["warnings"].append(f"Semantic bound checking encountered error: {str(e)}")

        if report["summary"]["invalid_metric_rows"] > 0 and len(report["errors"]) == 0:
            report["warnings"].append(
                "Data cleaning is recommended to rectify logical violations before budget optimization."
            )

        return report

