"""
High-performance synthetic advertising dataset generator.
Generates realistic digital advertising records for:
Facebook, Instagram, Google, TikTok, YouTube.
Enforces physical and business constraints:
clicks <= impressions, conversions <= clicks, spend >= 0, revenue >= 0.
Supports chunked streaming for up to 10M records.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Generator, Optional, Callable, Union
import numpy as np
import pandas as pd

# Add parent to path for imports
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import config


class AdvertisingDataGenerator:
    """
    Synthesizes realistic advertising campaign data across the 5 target platforms.
    """

    def __init__(self, seed: Optional[int] = 42):
        self.rng = np.random.default_rng(seed)
        self.platforms = config.PLATFORMS
        self.campaigns = config.CAMPAIGNS
        self.cities = config.CITIES
        self.devices = config.DEVICES
        self.genders = config.GENDERS
        self.age_groups = config.AGE_GROUPS
        self.profiles = config.PLATFORM_PROFILES

        # Precompute platform probabilities
        self.platform_weights = np.array([0.25, 0.25, 0.22, 0.16, 0.12])
        self.platform_weights /= self.platform_weights.sum()

        # Precompute city weights
        self.city_weights = np.array([0.35, 0.25, 0.15, 0.10, 0.07, 0.04, 0.04])
        self.city_weights /= self.city_weights.sum()

        # Date range: past 180 days
        self.start_date = datetime(2026, 1, 1)

    def generate_batch(self, batch_size: int) -> pd.DataFrame:
        """
        Generates a vectorized batch of realistic advertising records.
        """
        # Sample dimensions
        selected_platforms = self.rng.choice(self.platforms, size=batch_size, p=self.platform_weights)
        selected_campaigns = self.rng.choice(self.campaigns, size=batch_size)
        selected_cities = self.rng.choice(self.cities, size=batch_size, p=self.city_weights)
        selected_devices = self.rng.choice(self.devices, size=batch_size, p=[0.70, 0.22, 0.08])
        selected_genders = self.rng.choice(self.genders, size=batch_size, p=[0.48, 0.48, 0.04])
        selected_ages = self.rng.choice(self.age_groups, size=batch_size, p=[0.28, 0.35, 0.20, 0.12, 0.05])

        # Sample dates (last 180 days)
        random_day_offsets = self.rng.integers(0, 180, size=batch_size)
        dates = [(self.start_date + timedelta(days=int(d))).strftime("%Y-%m-%d") for d in random_day_offsets]

        # Base impressions: log-normal distribution to represent small ad sets vs huge viral ads
        base_impressions = self.rng.lognormal(mean=7.5, sigma=0.85, size=batch_size)
        impressions = np.clip(base_impressions.astype(int), 50, 100_000)

        # Platform-specific metrics using vectorized parameters
        ctrs = np.zeros(batch_size, dtype=np.float64)
        cpcs = np.zeros(batch_size, dtype=np.float64)
        cvrs = np.zeros(batch_size, dtype=np.float64)
        roas_multipliers = np.zeros(batch_size, dtype=np.float64)

        for platform, profile in self.profiles.items():
            mask = selected_platforms == platform
            count = int(np.sum(mask))
            if count > 0:
                # CTR percentage (e.g. 2.5%)
                sampled_ctr = self.rng.normal(profile["ctr_mean"], profile["ctr_std"], size=count)
                ctrs[mask] = np.clip(sampled_ctr, 0.3, 12.0) / 100.0

                # CPC in PKR (Rs.)
                sampled_cpc = self.rng.normal(profile["cpc_mean"], profile["cpc_std"], size=count)
                cpcs[mask] = np.clip(sampled_cpc, 2.0, 50.0)

                # Conversion rate (e.g. 3.0%)
                sampled_cvr = self.rng.normal(profile["cvr_mean"], profile["cvr_std"], size=count)
                cvrs[mask] = np.clip(sampled_cvr, 0.2, 15.0) / 100.0

                # Expected ROAS
                sampled_roas = self.rng.normal(profile["roas_mean"], profile["roas_std"], size=count)
                roas_multipliers[mask] = np.clip(sampled_roas, 0.5, 8.0)

        # Calculate clicks with binomial/Poisson-like behavior
        expected_clicks = impressions * ctrs
        # Add random noise to click behavior
        noise_clicks = self.rng.uniform(0.85, 1.15, size=batch_size)
        clicks = np.clip((expected_clicks * noise_clicks).astype(int), 0, impressions)

        # Calculate spend in PKR (Spend = clicks * CPC, adjusted by impression base fee)
        # Even if clicks are 0, minimal impression delivery cost applies
        spend = clicks * cpcs + (impressions * 0.005)
        # Add budget variation
        spend = np.round(spend * self.rng.uniform(0.9, 1.1, size=batch_size), 2)
        spend = np.maximum(spend, 10.0)

        # Calculate conversions: must be <= clicks
        expected_conversions = clicks * cvrs
        noise_conv = self.rng.uniform(0.8, 1.2, size=batch_size)
        conversions = np.clip((expected_conversions * noise_conv).astype(int), 0, clicks)

        # Calculate revenue: driven by conversions and average order value (AOV ~ Rs. 800 - 3500)
        # Plus correlation with ROAS expectation
        base_revenue = spend * roas_multipliers * (0.5 + 0.5 * (conversions / np.maximum(conversions.mean(), 1.0)))
        revenue = np.round(np.clip(base_revenue * self.rng.uniform(0.85, 1.15, size=batch_size), 0.0, None), 2)

        # Guarantee consistency:
        # If conversions == 0, revenue is small or 0
        zero_conv_mask = conversions == 0
        revenue[zero_conv_mask] = np.round(self.rng.choice([0.0, 50.0, 100.0], size=int(np.sum(zero_conv_mask)), p=[0.85, 0.10, 0.05]), 2)

        df = pd.DataFrame({
            "date": dates,
            "campaign": selected_campaigns,
            "platform": selected_platforms,
            "impressions": impressions,
            "clicks": clicks,
            "spend": spend,
            "conversions": conversions,
            "revenue": revenue,
            "age": selected_ages,
            "gender": selected_genders,
            "city": selected_cities,
            "device": selected_devices,
        })

        return df

    def generate_dataset_to_file(
        self,
        total_records: int,
        output_filepath: Union[str, Path],
        chunk_size: int = 50_000,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Path:
        """
        Generates large datasets directly to a CSV file in chunks,
        ensuring bounded RAM usage even for 1M or 10M records.
        """
        path = Path(output_filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            path.unlink()

        records_generated = 0
        is_first = True

        while records_generated < total_records:
            current_batch_size = min(chunk_size, total_records - records_generated)
            chunk = self.generate_batch(current_batch_size)

            chunk.to_csv(path, mode="a", index=False, header=is_first)
            is_first = False

            records_generated += current_batch_size
            if progress_callback:
                progress_callback(records_generated, total_records)

        return path


def get_default_dataset_path(size: int) -> Path:
    """Returns canonical file path for benchmark datasets."""
    label = {
        10_000: "10k",
        100_000: "100k",
        1_000_000: "1m",
        10_000_000: "10m",
    }.get(size, f"{size}")
    return config.RAW_DATA_DIR / f"advertising_{label}.csv"


def ensure_dataset(size: int = 100_000, force_regenerate: bool = False) -> Path:
    """
    Ensures that a dataset of the specified size is generated on disk.
    """
    path = get_default_dataset_path(size)
    if not path.exists() or force_regenerate:
        generator = AdvertisingDataGenerator()
        generator.generate_dataset_to_file(size, path)
    return path
