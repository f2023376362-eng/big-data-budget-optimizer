"""
Big Data Benchmarking Engine.
Orchestrates fair, reproducible comparative performance benchmarks
across Pandas, MapReduce, and Apache Spark.
Logs metrics, execution time, throughput (RPS), and memory footprint.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import pandas as pd

from src.pandas_processor import PandasProcessor
from src.mapreduce_processor import MapReduceProcessor
from src.spark_processor import SparkProcessor
import config


class BenchmarkEngine:
    """
    Executes and records benchmarks across analytical engines.
    """

    def __init__(self, db_manager: Optional[Any] = None):
        self.db = db_manager
        self.pandas_proc = PandasProcessor()
        self.mr_proc = MapReduceProcessor()
        self.spark_proc = SparkProcessor()

    def run_engine_benchmark(
        self,
        engine_name: str,
        source: Union[str, Path, pd.DataFrame],
        dataset_size: int,
    ) -> Dict[str, Any]:
        """
        Executes a benchmark for a single designated engine.
        """
        norm_name = engine_name.lower().strip()
        result = None

        if "pandas" in norm_name:
            result = self.pandas_proc.process(source)
        elif "mapreduce" in norm_name or "map_reduce" in norm_name or "mr" in norm_name:
            result = self.mr_proc.process(source)
        elif "spark" in norm_name:
            result = self.spark_proc.process(source)
        else:
            raise ValueError(f"Unknown engine: {engine_name}. Choose Pandas, MapReduce, or Spark.")

        # Save to benchmark history
        self._record_result(result, dataset_size)
        return result

    def run_all_comparisons(
        self,
        source: Union[str, Path, pd.DataFrame],
        dataset_size: int,
        include_spark: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Runs Pandas, MapReduce, and Spark on the EXACT same dataset for fair comparison.
        """
        results = []

        # 1. Run Pandas
        try:
            p_res = self.pandas_proc.process(source)
            self._record_result(p_res, dataset_size)
            results.append(p_res)
        except Exception as e:
            results.append({
                "engine": "Pandas (Vectorized In-Memory)",
                "status": "ERROR",
                "dataset_size": dataset_size,
                "execution_time_sec": 0.0,
                "throughput_rps": 0.0,
                "memory_mb": 0.0,
                "notes": f"Pandas failed: {str(e)}",
            })

        # 2. Run MapReduce
        try:
            mr_res = self.mr_proc.process(source)
            self._record_result(mr_res, dataset_size)
            results.append(mr_res)
        except Exception as e:
            results.append({
                "engine": "MapReduce (Streaming / Partitioned Simulation)",
                "status": "ERROR",
                "dataset_size": dataset_size,
                "execution_time_sec": 0.0,
                "throughput_rps": 0.0,
                "memory_mb": 0.0,
                "notes": f"MapReduce failed: {str(e)}",
            })

        # 3. Run Spark
        if include_spark:
            try:
                s_res = self.spark_proc.process(source)
                self._record_result(s_res, dataset_size)
                results.append(s_res)
            except Exception as e:
                results.append({
                    "engine": "Apache Spark (PySpark Local)",
                    "status": "ERROR",
                    "dataset_size": dataset_size,
                    "execution_time_sec": 0.0,
                    "throughput_rps": 0.0,
                    "memory_mb": 0.0,
                    "notes": f"Spark failed: {str(e)}",
                })

        return results

    def _record_result(self, result: Dict[str, Any], dataset_size: int):
        """
        Persists benchmark run result to JSON log and SQLite database.
        """
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dataset_size": dataset_size,
            "engine": result.get("engine", "Unknown"),
            "execution_time_sec": result.get("execution_time_sec", 0.0),
            "throughput_rps": result.get("throughput_rps", 0.0),
            "memory_mb": result.get("memory_mb", 0.0),
            "status": result.get("status", "UNKNOWN"),
            "notes": result.get("notes", ""),
        }

        # Append to JSON benchmark log
        log_file = config.BENCHMARKS_DIR / "benchmark_history.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        # Save to DB if connection provided
        if self.db:
            try:
                self.db.insert_benchmark(
                    dataset_size=record["dataset_size"],
                    engine=record["engine"],
                    execution_time_sec=record["execution_time_sec"],
                    throughput_rps=record["throughput_rps"],
                    memory_mb=record["memory_mb"],
                    status=record["status"],
                    notes=record["notes"],
                )
            except Exception:
                pass

    def get_benchmark_history(self) -> pd.DataFrame:
        """
        Loads all past benchmark history as a DataFrame.
        """
        log_file = config.BENCHMARKS_DIR / "benchmark_history.jsonl"
        if not log_file.exists():
            return pd.DataFrame(columns=[
                "timestamp", "dataset_size", "engine", "execution_time_sec", "throughput_rps", "memory_mb", "status", "notes"
            ])

        records = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue

        return pd.DataFrame(records)

