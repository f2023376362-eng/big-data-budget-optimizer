"""
Unit tests for Marketing Budget Recommendation Engine.
Tests exact budget sum constraints, min/max allocations, and strategy behaviors.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.budget_optimizer import BudgetOptimizer
from src.data_generator import AdvertisingDataGenerator


@pytest.fixture
def sample_dataset():
    gen = AdvertisingDataGenerator(seed=42)
    return gen.generate_batch(5_000)


def test_budget_exact_sum_rule(sample_dataset):
    optimizer = BudgetOptimizer(sample_dataset)
    target_budget = 1_000_000.0

    for strategy in ["ROAS Maximization", "Conversion Maximization", "Balanced Optimization"]:
        result = optimizer.optimize_budget(total_budget=target_budget, strategy=strategy)
        allocations = result["allocations"]

        # Ensure all 5 platforms present
        assert len(allocations) == 5
        # Ensure exact budget sum
        total_allocated = sum(a["allocated_amount"] for a in allocations)
        assert abs(total_allocated - target_budget) < 0.05, f"Sum {total_allocated} != {target_budget} for {strategy}"

        # Ensure percentages sum to 100%
        total_pct = sum(a["allocated_percentage"] for a in allocations)
        assert abs(total_pct - 100.0) < 0.1, f"Total % {total_pct} != 100% for {strategy}"


def test_min_max_constraints(sample_dataset):
    optimizer = BudgetOptimizer(sample_dataset)
    target_budget = 1_000_000.0
    min_pct = 0.08  # 8%
    max_pct = 0.40  # 40%

    result = optimizer.optimize_budget(
        total_budget=target_budget,
        strategy="Balanced Optimization",
        min_allocation_pct=min_pct,
        max_allocation_pct=max_pct,
    )

    for a in result["allocations"]:
        pct = a["allocated_percentage"] / 100.0
        assert pct >= (min_pct - 0.01), f"{a['platform']} allocation {pct} < min {min_pct}"
        assert pct <= (max_pct + 0.01), f"{a['platform']} allocation {pct} > max {max_pct}"


def test_custom_budget_amount(sample_dataset):
    optimizer = BudgetOptimizer(sample_dataset)
    # Test unusual custom budget
    target_budget = 2_750_430.50
    result = optimizer.optimize_budget(total_budget=target_budget, strategy="ROAS Maximization")

    total_allocated = sum(a["allocated_amount"] for a in result["allocations"])
    assert abs(total_allocated - target_budget) < 0.05


def test_fallback_with_empty_dataframe():
    optimizer = BudgetOptimizer(pd.DataFrame())
    target_budget = 1_000_000.0
    result = optimizer.optimize_budget(total_budget=target_budget)

    assert len(result["allocations"]) == 5
    total_allocated = sum(a["allocated_amount"] for a in result["allocations"])
    assert abs(total_allocated - target_budget) < 0.05

