"""
Big Data Processing Module — Approach A: Pandas.
Performs vectorized in-memory or chunk-based processing on advertising datasets.
Records actual execution time, memory utilization, and throughput.
"""

import time
import os
import gc
from pathlib import Path
from typing import Dict, Any, Union
import pandas as pd
import numpy as np


class PandasProcessor:
    """
    Executes benchmark aggregations using Pandas vectorized operations.
    """

    def __init__(self, chunk_size: int = 100_000):
        self.chunk_size = chunk_size

    def process(self, source: Union[str, Path, pd.DataFrame]) -> Dict[str, Any]:
        """
        Executes standard analytical aggregations:
        - Total impressions, clicks, spend, conversions, revenue
        - Platform-level revenue, spend, ROAS
        - Campaign-level revenue, spend, ROAS
        """
        start_time = time.perf_counter()
        
        # Read or accept DataFrame
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Source file does not exist: {path}")
            
            # Read CSV
            df = pd.read_csv(path)
        else:
            df = source.copy()

        num_records = len(df)

        # 1. Overall Aggregations
        tot_impressions = int(df["impressions"].sum())
        tot_clicks = int(df["clicks"].sum())
        tot_spend = round(float(df["spend"].sum()), 2)
        tot_conversions = int(df["conversions"].sum())
        tot_revenue = round(float(df["revenue"].sum()), 2)

        # 2. Platform Aggregations
        platform_grp = df.groupby("platform").agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        platform_grp["roas"] = np.where(
            platform_grp["spend"] > 0,
            (platform_grp["revenue"] / platform_grp["spend"]).round(2),
            0.0
        )
        platform_results = platform_grp.to_dict(orient="records")

        # 3. Campaign Aggregations
        campaign_grp = df.groupby(["campaign", "platform"]).agg(
            impressions=("impressions", "sum"),
            clicks=("clicks", "sum"),
            spend=("spend", "sum"),
            conversions=("conversions", "sum"),
            revenue=("revenue", "sum"),
        ).reset_index()

        campaign_grp["roas"] = np.where(
            campaign_grp["spend"] > 0,
            (campaign_grp["revenue"] / campaign_grp["spend"]).round(2),
            0.0
        )
        campaign_results = campaign_grp.to_dict(orient="records")

        elapsed_time = time.perf_counter() - start_time
        throughput = round(num_records / elapsed_time, 2) if elapsed_time > 0 else 0.0

        # Memory estimation (DataFrame memory footprint)
        memory_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)

        return {
            "engine": "Pandas (Vectorized In-Memory)",
            "status": "SUCCESS",
            "dataset_size": num_records,
            "execution_time_sec": round(elapsed_time, 4),
            "throughput_rps": throughput,
            "memory_mb": memory_mb,
            "summary": {
                "impressions": tot_impressions,
                "clicks": tot_clicks,
                "spend": tot_spend,
                "conversions": tot_conversions,
                "revenue": tot_revenue,
                "overall_roas": round(tot_revenue / tot_spend, 2) if tot_spend > 0 else 0.0,
            },
            "platform_breakdown": platform_results,
            "campaign_breakdown": campaign_results[:10],  # sample top
            "notes": "Pandas loads the complete dataset into RAM and applies C-optimized vectorized operations.",
        }

