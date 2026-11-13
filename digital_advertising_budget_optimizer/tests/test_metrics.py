"""
Unit tests for advertising metric formulas and division-by-zero resilience.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.advertising_metrics import (
    calculate_ctr,
    calculate_cpc,
    calculate_cpa,
    calculate_cvr,
    calculate_roas,
    compute_aggregate_metrics,
)


def test_ctr_calculation():
    # 50 clicks out of 1,000 impressions = 5.0%
    assert calculate_ctr(50, 1000) == 5.0
    # Zero impressions should safely return 0.0
    assert calculate_ctr(50, 0) == 0.0
    assert calculate_ctr(0, 0) == 0.0


def test_cpc_calculation():
    # Rs. 1,000 spend for 50 clicks = Rs. 20.0 per click
    assert calculate_cpc(1000.0, 50) == 20.0
    # Zero clicks should safely return 0.0
    assert calculate_cpc(1000.0, 0) == 0.0


def test_cpa_calculation():
    # Rs. 10,000 spend for 20 conversions = Rs. 500.0 CPA
    assert calculate_cpa(10000.0, 20) == 500.0
    # Zero conversions should safely return 0.0
    assert calculate_cpa(10000.0, 0) == 0.0


def test_cvr_calculation():
    # 25 conversions from 500 clicks = 5.0%
    assert calculate_cvr(25, 500) == 5.0
    # Zero clicks should safely return 0.0
    assert calculate_cvr(25, 0) == 0.0


def test_roas_calculation():
    # Rs. 350,000 revenue from Rs. 100,000 spend = 3.5x ROAS
    assert calculate_roas(350000.0, 100000.0) == 3.5
    # Zero spend should safely return 0.0
    assert calculate_roas(350000.0, 0.0) == 0.0


def test_vectorized_metrics():
    impressions = pd.Series([1000, 2000, 0])
    clicks = pd.Series([50, 0, 10])
    spend = pd.Series([1000.0, 500.0, 0.0])
    conversions = pd.Series([5, 0, 0])
    revenue = pd.Series([3000.0, 0.0, 0.0])

    ctr_series = calculate_ctr(clicks, impressions)
    assert ctr_series[0] == 5.0
    assert ctr_series[1] == 0.0
    assert ctr_series[2] == 0.0

    roas_series = calculate_roas(revenue, spend)
    assert roas_series[0] == 3.0
    assert roas_series[1] == 0.0
    assert roas_series[2] == 0.0


def test_compute_aggregate_metrics():
    df = pd.DataFrame({
        "impressions": [1000, 2000],
        "clicks": [50, 100],
        "spend": [500.0, 1000.0],
        "conversions": [5, 10],
        "revenue": [2000.0, 4000.0],
    })

    agg = compute_aggregate_metrics(df)
    assert agg["total_records"] == 2
    assert agg["total_impressions"] == 3000
    assert agg["total_clicks"] == 150
    assert agg["total_spend"] == 1500.0
    assert agg["total_conversions"] == 15
    assert agg["total_revenue"] == 6000.0
    assert agg["roas"] == 4.0
    assert agg["ctr"] == 5.0
    assert agg["cpc"] == 10.0
    assert agg["cpa"] == 100.0

