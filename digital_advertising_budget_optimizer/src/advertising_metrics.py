"""
Core mathematical formulas and analytical metrics for digital advertising.
Handles division by zero gracefully and provides typed, reusable calculations.
"""

from typing import Union, Dict, Any, Optional

try:
    import numpy as np
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    np = None
    pd = None


def calculate_ctr(clicks: Any, impressions: Any) -> Any:
    """
    Click-Through Rate (CTR) = (Clicks / Impressions) * 100
    Returns percentage (e.g. 2.5 means 2.5%).
    """
    if HAS_PANDAS and isinstance(impressions, pd.Series):
        return np.where(impressions > 0, (clicks / impressions) * 100.0, 0.0)
    return (float(clicks) / float(impressions) * 100.0) if impressions and float(impressions) > 0 else 0.0


def calculate_cpc(spend: Any, clicks: Any) -> Any:
    """
    Cost Per Click (CPC) = Spend / Clicks
    Returns cost in PKR per click.
    """
    if HAS_PANDAS and isinstance(clicks, pd.Series):
        return np.where(clicks > 0, spend / clicks, 0.0)
    return (float(spend) / float(clicks)) if clicks and float(clicks) > 0 else 0.0


def calculate_cpa(spend: Any, conversions: Any) -> Any:
    """
    Cost Per Acquisition / Action (CPA) = Spend / Conversions
    Returns cost in PKR per acquired customer/conversion.
    """
    if HAS_PANDAS and isinstance(conversions, pd.Series):
        return np.where(conversions > 0, spend / conversions, 0.0)
    return (float(spend) / float(conversions)) if conversions and float(conversions) > 0 else 0.0


def calculate_cvr(conversions: Any, clicks: Any) -> Any:
    """
    Conversion Rate (CVR) = (Conversions / Clicks) * 100
    Returns percentage (e.g. 3.0 means 3.0%).
    """
    if HAS_PANDAS and isinstance(clicks, pd.Series):
        return np.where(clicks > 0, (conversions / clicks) * 100.0, 0.0)
    return (float(conversions) / float(clicks) * 100.0) if clicks and float(clicks) > 0 else 0.0


def calculate_roas(revenue: Any, spend: Any) -> Any:
    """
    Return on Ad Spend (ROAS) = Revenue / Spend
    Ratio of gross revenue earned per rupee spent (e.g., 3.5x).
    """
    if HAS_PANDAS and isinstance(spend, pd.Series):
        return np.where(spend > 0, revenue / spend, 0.0)
    return (float(revenue) / float(spend)) if spend and float(spend) > 0 else 0.0


def compute_aggregate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes business KPI scorecard across the entire DataFrame.
    """
    if df is None or df.empty:
        return {
            "total_records": 0,
            "total_impressions": 0,
            "total_clicks": 0,
            "total_spend": 0.0,
            "total_conversions": 0,
            "total_revenue": 0.0,
            "net_profit": 0.0,
            "ctr": 0.0,
            "cpc": 0.0,
            "cpa": 0.0,
            "cvr": 0.0,
            "roas": 0.0,
        }

    impressions = float(df["impressions"].sum())
    clicks = float(df["clicks"].sum())
    spend = float(df["spend"].sum())
    conversions = float(df["conversions"].sum())
    revenue = float(df["revenue"].sum())

    ctr = calculate_ctr(clicks, impressions)
    cpc = calculate_cpc(spend, clicks)
    cpa = calculate_cpa(spend, conversions)
    cvr = calculate_cvr(conversions, clicks)
    roas = calculate_roas(revenue, spend)
    net_profit = revenue - spend

    return {
        "total_records": len(df),
        "total_impressions": int(impressions),
        "total_clicks": int(clicks),
        "total_spend": round(spend, 2),
        "total_conversions": int(conversions),
        "total_revenue": round(revenue, 2),
        "net_profit": round(net_profit, 2),
        "ctr": round(ctr, 2),
        "cpc": round(cpc, 2),
        "cpa": round(cpa, 2),
        "cvr": round(cvr, 2),
        "roas": round(roas, 2),
    }

