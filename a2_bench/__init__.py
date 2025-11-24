"""
A²-Bench: Agent Assessment Benchmark

A comprehensive evaluation framework for AI agent safety, security, and reliability.
"""

from a2_bench.core.environment import A2Environment
from a2_bench.core.safety_spec import SafetySpec
from a2_bench.core.evaluation import A2Evaluator
from a2_bench.benchmark import A2Benchmark

__version__ = "0.1.0"
__all__ = [
    "A2Environment",
    "SafetySpec",
    "A2Evaluator",
    "A2Benchmark",
]
