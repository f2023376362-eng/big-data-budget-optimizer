"""
Data cleaning and preprocessing pipeline for digital advertising datasets.
Normalizes columns, repairs physical bound anomalies, imputes missing values,
and removes duplicate entries.
"""

from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np
from src.data_validation import DatasetValidator


# Map common platform name variations to official platform names
PLATFORM_SYNONYMS = {
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "facebook": "Facebook",
    "google": "Google",
    "instagram": "Instagram",
    "fb": "Facebook",
    "meta": "Facebook",
    "facebook ads": "Facebook",
    "ig": "Instagram",
    "insta": "Instagram",
    "instagram ads": "Instagram",
    "google ads": "Google",
    "adwords": "Google",
    "google search": "Google",
    "yt": "YouTube",
    "youtube ads": "YouTube",
    "tiktok ads": "TikTok",
}


class DataCleaner:
    """
    Cleans raw advertising datasets for consistent analytical processing.
    """

    def __init__(self):
        self.validator = DatasetValidator()

    def clean(self, df: pd.DataFrame, drop_duplicates: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Runs the full data cleaning pipeline.
        Returns (cleaned_df, cleaning_summary_dict).
        """
        summary = {
            "initial_rows": len(df),
            "duplicates_removed": 0,
            "nulls_imputed": 0,
            "clicks_clamped": 0,
            "conversions_clamped": 0,
            "negative_metrics_rectified": 0,
            "final_rows": 0,
        }

        # 1. Standardize columns
        mapping, _ = self.validator.detect_column_mapping(df.columns.tolist())
        cleaned = df.rename(columns={v: k for k, v in mapping.items()}).copy()

        # 2. Handle duplicates
        if drop_duplicates:
            dup_count = int(cleaned.duplicated().sum())
            if dup_count > 0:
                cleaned = cleaned.drop_duplicates().reset_index(drop=True)
                summary["duplicates_removed"] = dup_count

        # 3. Clean and normalize platform names
        if "platform" in cleaned.columns:
            cleaned["platform"] = cleaned["platform"].astype(str).str.strip()
            cleaned["platform"] = cleaned["platform"].apply(
                lambda p: PLATFORM_SYNONYMS.get(p.lower(), p.title())
            )

        # 4. Standardize dates
        if "date" in cleaned.columns:
            cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce").dt.strftime("%Y-%m-%d")
            # Fill missing dates with today or default
            cleaned["date"] = cleaned["date"].fillna("2026-01-01")

        # 5. Numeric types and non-negative boundaries
        numeric_int_cols = ["impressions", "clicks", "conversions"]
        numeric_float_cols = ["spend", "revenue"]

        for col in numeric_int_cols:
            if col in cleaned.columns:
                null_mask = cleaned[col].isna()
                summary["nulls_imputed"] += int(null_mask.sum())
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).astype(int)
                # Rectify negative
                neg_mask = cleaned[col] < 0
                summary["negative_metrics_rectified"] += int(neg_mask.sum())
                cleaned[col] = np.maximum(cleaned[col], 0)

        for col in numeric_float_cols:
            if col in cleaned.columns:
                null_mask = cleaned[col].isna()
                summary["nulls_imputed"] += int(null_mask.sum())
                cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0.0).astype(float)
                # Rectify negative
                neg_mask = cleaned[col] < 0.0
                summary["negative_metrics_rectified"] += int(neg_mask.sum())
                cleaned[col] = np.maximum(cleaned[col], 0.0)

        # 6. Physical Advertising Constraints
        # Clicks cannot exceed impressions
        if "clicks" in cleaned.columns and "impressions" in cleaned.columns:
            invalid_clicks = cleaned["clicks"] > cleaned["impressions"]
            summary["clicks_clamped"] = int(invalid_clicks.sum())
            cleaned["clicks"] = np.minimum(cleaned["clicks"], cleaned["impressions"])

        # Conversions cannot exceed clicks
        if "conversions" in cleaned.columns and "clicks" in cleaned.columns:
            invalid_conv = cleaned["conversions"] > cleaned["clicks"]
            summary["conversions_clamped"] = int(invalid_conv.sum())
            cleaned["conversions"] = np.minimum(cleaned["conversions"], cleaned["clicks"])

        # 7. Categorical columns normalization
        categorical_cols = ["campaign", "age", "gender", "city", "device"]
        for col in categorical_cols:
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].fillna("Unknown").astype(str).str.strip()
            else:
                cleaned[col] = "Unknown"

        summary["final_rows"] = len(cleaned)
        return cleaned, summary

