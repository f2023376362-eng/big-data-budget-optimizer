"""
Marketing Budget Recommendation Engine.
Calculates mathematically derived, constraint-bounded budget distributions
across Facebook, Instagram, Google, TikTok, and YouTube.
Supports:
- Strategy 1: ROAS Maximization
- Strategy 2: Conversion Maximization
- Strategy 3: Balanced Optimization
Includes customizable constraints (Min/Max platform share, Risk tolerance),
exact budget rounding to match total PKR, and estimated performance projections.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from src.advertising_metrics import calculate_ctr, calculate_cpc, calculate_cpa, calculate_cvr, calculate_roas
import config


class BudgetOptimizer:
    """
    Mathematical optimization and budget reallocation engine.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy() if df is not None and not df.empty else pd.DataFrame()
        self.platforms = config.PLATFORMS

    def _extract_platform_metrics(self) -> pd.DataFrame:
        """
        Extracts historical baseline performance metrics for all 5 platforms.
        Uses fallback platform priors if a platform is absent in the dataset.
        """
        if self.df.empty:
            # Fallback priors based on configuration benchmarks
            records = []
            for plat in self.platforms:
                prof = config.PLATFORM_PROFILES.get(plat, {"roas_mean": 2.5, "cpc_mean": 10.0, "cvr_mean": 3.0, "ctr_mean": 2.0})
                records.append({
                    "platform": plat,
                    "impressions": 100_000,
                    "clicks": int(100_000 * prof["ctr_mean"] / 100.0),
                    "spend": 200_000.0,
                    "conversions": int(100_000 * (prof["ctr_mean"] / 100.0) * (prof["cvr_mean"] / 100.0)),
                    "revenue": 200_000.0 * prof["roas_mean"],
                    "roas_volatility": 0.35,
                })
            base_df = pd.DataFrame(records)
        else:
            # Group from actual dataset
            grouped = self.df.groupby("platform").agg(
                impressions=("impressions", "sum"),
                clicks=("clicks", "sum"),
                spend=("spend", "sum"),
                conversions=("conversions", "sum"),
                revenue=("revenue", "sum"),
            ).reset_index()

            # Calculate daily ROAS volatility (risk metric)
            if "date" in self.df.columns:
                daily = self.df.groupby(["platform", "date"]).agg(
                    d_spend=("spend", "sum"),
                    d_rev=("revenue", "sum")
                ).reset_index()
                daily["d_roas"] = np.where(daily["d_spend"] > 0, daily["d_rev"] / daily["d_spend"], 0.0)
                volatility = daily.groupby("platform")["d_roas"].std().fillna(0.2).reset_index()
                volatility.columns = ["platform", "roas_volatility"]
                grouped = pd.merge(grouped, volatility, on="platform", how="left")
            else:
                grouped["roas_volatility"] = 0.25

            # Ensure all 5 platforms exist
            existing_platforms = set(grouped["platform"].unique())
            missing_records = []
            for plat in self.platforms:
                if plat not in existing_platforms:
                    prof = config.PLATFORM_PROFILES.get(plat, {"roas_mean": 2.0, "cpc_mean": 10.0, "cvr_mean": 2.5, "ctr_mean": 2.0})
                    missing_records.append({
                        "platform": plat,
                        "impressions": 10_000,
                        "clicks": 200,
                        "spend": 50_000.0,
                        "conversions": 10,
                        "revenue": 50_000.0 * prof["roas_mean"],
                        "roas_volatility": 0.4,
                    })

            if missing_records:
                grouped = pd.concat([grouped, pd.DataFrame(missing_records)], ignore_index=True)

            base_df = grouped

        # Calculate unit economics
        base_df["ctr"] = calculate_ctr(base_df["clicks"], base_df["impressions"])
        base_df["cpc"] = calculate_cpc(base_df["spend"], base_df["clicks"])
        base_df["cpa"] = calculate_cpa(base_df["spend"], base_df["conversions"])
        base_df["cvr"] = calculate_cvr(base_df["conversions"], base_df["clicks"])
        base_df["roas"] = calculate_roas(base_df["revenue"], base_df["spend"])

        total_historical_spend = base_df["spend"].sum()
        base_df["current_budget_share"] = np.where(
            total_historical_spend > 0,
            (base_df["spend"] / total_historical_spend * 100.0),
            20.0
        )

        return base_df

    def _apply_constraints(
        self,
        raw_weights: np.ndarray,
        min_pct: float,
        max_pct: float,
        max_iterations: int = 50,
    ) -> np.ndarray:
        """
        Projects raw weights onto the simplex sum(w) = 1.0 subject to min_pct <= w_i <= max_pct.
        """
        n = len(raw_weights)
        if min_pct * n > 1.0 or max_pct * n < 1.0:
            # Fallback to uniform if constraints are infeasible
            return np.ones(n) / n

        weights = np.copy(raw_weights)
        weights = np.maximum(weights, 1e-6)
        weights = weights / weights.sum()

        for _ in range(max_iterations):
            clipped = np.clip(weights, min_pct, max_pct)
            excess = 1.0 - clipped.sum()
            if abs(excess) < 1e-5:
                weights = clipped
                break

            # Distribute excess to unclipped elements
            unclipped_mask = (clipped > min_pct + 1e-5) & (clipped < max_pct - 1e-5)
            if not unclipped_mask.any():
                # All clipped or at boundary
                weights = clipped
                break
            weights[unclipped_mask] += excess / unclipped_mask.sum()
            weights = np.clip(weights, min_pct, max_pct)

        # Final normalization
        weights = weights / weights.sum()
        return weights

    def optimize_budget(
        self,
        total_budget: float = config.DEFAULT_BUDGET,
        strategy: str = "Balanced Optimization",
        min_allocation_pct: float = 0.05,
        max_allocation_pct: float = 0.45,
        risk_tolerance: float = 0.5,  # 0.0 = Very Conservative, 1.0 = Aggressive
    ) -> Dict[str, Any]:
        """
        Executes budget optimization and generates actionable allocations.
        """
        df_metrics = self._extract_platform_metrics()
        platforms = df_metrics["platform"].tolist()
        n = len(platforms)

        roas_vals = df_metrics["roas"].values
        cpa_vals = np.maximum(df_metrics["cpa"].values, 1.0)
        cvr_vals = df_metrics["cvr"].values
        ctr_vals = df_metrics["ctr"].values
        volatility_vals = df_metrics["roas_volatility"].fillna(0.2).values

        # Normalize components [0, 1]
        def min_max(arr):
            rng = arr.max() - arr.min()
            return (arr - arr.min()) / rng if rng > 0 else np.ones_like(arr) * 0.5

        norm_roas = min_max(roas_vals)
        norm_cpa_inv = min_max(1.0 / cpa_vals)
        norm_cvr = min_max(cvr_vals)
        norm_ctr = min_max(ctr_vals)
        norm_vol = min_max(volatility_vals)

        # Compute raw scores based on Strategy
        if strategy == "ROAS Maximization":
            # Prioritize historical ROAS with small stability check
            raw_scores = (roas_vals ** 1.8) * (1.0 + 0.3 * norm_cvr)
            if risk_tolerance < 0.5:
                raw_scores /= (1.0 + (1.0 - risk_tolerance) * norm_vol)

        elif strategy == "Conversion Maximization":
            # Prioritize low CPA and high conversion rate
            raw_scores = (norm_cpa_inv * 1.5) + (norm_cvr * 1.2) + (norm_ctr * 0.3)
            raw_scores = np.maximum(raw_scores, 0.05)

        else:  # "Balanced Optimization"
            # Blend ROAS, CPA, CVR, CTR, and penalize volatility according to risk preference
            w_roas = 0.40 + 0.15 * risk_tolerance
            w_cpa = 0.25
            w_cvr = 0.20
            w_risk = (1.0 - risk_tolerance) * 0.20

            raw_scores = (
                w_roas * norm_roas +
                w_cpa * norm_cpa_inv +
                w_cvr * norm_cvr +
                0.05 * norm_ctr -
                w_risk * norm_vol
            )
            raw_scores = np.maximum(raw_scores, 0.05)

        # Apply boundary constraints (min_allocation_pct, max_allocation_pct)
        allocated_pcts = self._apply_constraints(raw_scores, min_allocation_pct, max_allocation_pct)

        # Compute exact amounts in PKR
        raw_amounts = total_budget * allocated_pcts
        # Exact integer/cent rounding ensuring sum == total_budget
        rounded_amounts = np.round(raw_amounts, 2)
        diff = total_budget - rounded_amounts.sum()
        # Adjust biggest platform with difference
        max_idx = np.argmax(rounded_amounts)
        rounded_amounts[max_idx] += round(diff, 2)

        # Recalculate exact percentages
        exact_pcts = np.round(rounded_amounts / total_budget * 100.0, 2)
        # Ensure exact 100% display
        diff_pct = 100.0 - exact_pcts.sum()
        exact_pcts[max_idx] += round(diff_pct, 2)

        # Projections & Strategic Rationale
        allocations = []
        tot_proj_impressions = 0
        tot_proj_clicks = 0
        tot_proj_conversions = 0
        tot_proj_revenue = 0.0

        for i, plat in enumerate(platforms):
            amt = float(rounded_amounts[i])
            pct = float(exact_pcts[i])
            curr_pct = float(round(df_metrics.loc[i, "current_budget_share"], 2))
            hist_roas = float(round(df_metrics.loc[i, "roas"], 2))
            hist_cpa = float(round(df_metrics.loc[i, "cpa"], 2))
            hist_cpc = float(round(df_metrics.loc[i, "cpc"], 2))
            hist_cvr = float(round(df_metrics.loc[i, "cvr"], 2))
            hist_ctr = float(round(df_metrics.loc[i, "ctr"], 2))

            # Expected estimates based on unit economics
            expected_clicks = int(amt / hist_cpc) if hist_cpc > 0 else 0
            expected_impressions = int(expected_clicks / (hist_ctr / 100.0)) if hist_ctr > 0 else expected_clicks * 30
            expected_conversions = int(amt / hist_cpa) if hist_cpa > 0 else int(expected_clicks * (hist_cvr / 100.0))
            expected_revenue = round(amt * hist_roas, 2)

            tot_proj_impressions += expected_impressions
            tot_proj_clicks += expected_clicks
            tot_proj_conversions += expected_conversions
            tot_proj_revenue += expected_revenue

            # Shift direction
            delta_pct = round(pct - curr_pct, 2)
            if delta_pct > 2.0:
                action = "INCREASE"
            elif delta_pct < -2.0:
                action = "DECREASE"
            else:
                action = "MAINTAIN"

            # Formulate strategic reasoning
            if hist_roas >= 3.0:
                rationale = f"Strong return efficiency ({hist_roas}x ROAS). Warranted high capital share."
            elif hist_cpa < 250.0:
                rationale = f"Highly efficient customer acquisition (Rs. {hist_cpa} CPA). Cost-effective volume driver."
            elif delta_pct < -2.0:
                rationale = f"Lower relative ROAS ({hist_roas}x) or higher CPA. Capital pruned to fund higher-yield channels."
            else:
                rationale = f"Balanced channel offering dependable reach ({hist_ctr}% CTR) and steady conversions."

            allocations.append({
                "platform": plat,
                "allocated_percentage": pct,
                "allocated_amount": amt,
                "current_percentage": curr_pct,
                "budget_shift": delta_pct,
                "action": action,
                "historical_roas": hist_roas,
                "historical_cpa": hist_cpa,
                "expected_impressions": expected_impressions,
                "expected_clicks": expected_clicks,
                "expected_conversions": expected_conversions,
                "expected_revenue": expected_revenue,
                "expected_roas": hist_roas,
                "rationale": rationale,
            })

        allocations.sort(key=lambda x: x["allocated_amount"], reverse=True)

        overall_expected_roas = round(tot_proj_revenue / total_budget, 2) if total_budget > 0 else 0.0

        return {
            "total_budget": total_budget,
            "strategy": strategy,
            "min_allocation_pct": min_allocation_pct * 100.0,
            "max_allocation_pct": max_allocation_pct * 100.0,
            "risk_tolerance": risk_tolerance,
            "allocations": allocations,
            "projections": {
                "expected_impressions": tot_proj_impressions,
                "expected_clicks": tot_proj_clicks,
                "expected_conversions": tot_proj_conversions,
                "expected_revenue": round(tot_proj_revenue, 2),
                "expected_net_profit": round(tot_proj_revenue - total_budget, 2),
                "expected_roas": overall_expected_roas,
                "disclaimer": "Projections are mathematical estimates derived from historical cost-per-click, conversion rates, and ROAS. Actual outcomes depend on ad creative fatigue and bidding dynamics.",
            },
        }

    def compare_all_strategies(self, total_budget: float = config.DEFAULT_BUDGET) -> pd.DataFrame:
        """
        Computes allocations and projected KPIs across all 3 strategies side-by-side.
        """
        strategies = ["ROAS Maximization", "Conversion Maximization", "Balanced Optimization"]
        rows = []

        for strat in strategies:
            res = self.optimize_budget(total_budget=total_budget, strategy=strat)
            for alloc in res["allocations"]:
                rows.append({
                    "Strategy": strat,
                    "Platform": alloc["platform"],
                    "Allocation (%)": alloc["allocated_percentage"],
                    "Allocated Budget (PKR)": alloc["allocated_amount"],
                    "Expected Conversions": alloc["expected_conversions"],
                    "Expected Revenue (PKR)": alloc["expected_revenue"],
                    "Expected ROAS": alloc["expected_roas"],
                })

        return pd.DataFrame(rows)

