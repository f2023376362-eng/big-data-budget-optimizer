"""
Unit tests for data validation, schema boundary checks, and data cleaner.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_validation import DatasetValidator
from src.data_cleaning import DataCleaner


def test_column_mapping_and_synonyms():
    validator = DatasetValidator()
    # Test column synonyms typical of Google / Meta / TikTok ads
    test_cols = ["Day", "Media_Source", "Ad_Campaign", "Impr", "Link_Clicks", "Amount_Spent", "Purchases", "Sales"]
    mapping, missing = validator.detect_column_mapping(test_cols)

    assert "date" in mapping
    assert "platform" in mapping
    assert "campaign" in mapping
    assert "impressions" in mapping
    assert "clicks" in mapping
    assert "spend" in mapping
    assert "conversions" in mapping
    assert "revenue" in mapping


def test_missing_critical_columns():
    validator = DatasetValidator()
    bad_df = pd.DataFrame({"some_metric": [1, 2, 3]})
    report = validator.validate(bad_df)

    assert report["is_valid"] is False
    assert len(report["errors"]) > 0
    assert "Missing critical advertising columns" in report["errors"][0]


def test_negative_metric_rejection():
    validator = DatasetValidator()
    invalid_df = pd.DataFrame({
        "date": ["2026-01-01"],
        "campaign": ["Camp A"],
        "platform": ["Google"],
        "impressions": [1000],
        "clicks": [50],
        "spend": [-500.0],  # Negative spend
        "conversions": [5],
        "revenue": [1500.0],
        "age": ["25-34"],
        "gender": ["Male"],
        "city": ["Lahore"],
        "device": ["Mobile"],
    })
    report = validator.validate(invalid_df)
    assert report["is_valid"] is False
    assert any("negative spend" in err for err in report["errors"])


def test_data_cleaner_clamps_anomalies():
    cleaner = DataCleaner()
    dirty_df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-01"],  # Duplicate row
        "campaign": ["Camp A", "Camp A"],
        "platform": ["fb", "fb"],  # Needs normalization
        "impressions": [100, 100],
        "clicks": [150, 150],  # Clicks > impressions (impossible)
        "spend": [500.0, 500.0],
        "conversions": [200, 200],  # Conversions > clicks (impossible)
        "revenue": [2000.0, 2000.0],
        "age": ["25-34", "25-34"],
        "gender": ["Male", "Male"],
        "city": ["Karachi", "Karachi"],
        "device": ["Mobile", "Mobile"],
    })

    cleaned_df, summary = cleaner.clean(dirty_df, drop_duplicates=True)

    # 1 duplicate removed -> 1 row remains
    assert len(cleaned_df) == 1
    assert summary["duplicates_removed"] == 1
    # Platform normalized
    assert cleaned_df["platform"].iloc[0] == "Facebook"
    # Clicks clamped to impressions (100)
    assert cleaned_df["clicks"].iloc[0] == 100
    # Conversions clamped to clicks (100)
    assert cleaned_df["conversions"].iloc[0] == 100

