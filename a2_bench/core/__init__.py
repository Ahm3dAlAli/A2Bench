"""Core components for A²-Bench."""

from a2_bench.core.environment import A2Environment, ViolationType, Violation
from a2_bench.core.safety_spec import (
    SafetySpec,
    SafetyProperty,
    Invariant,
    TemporalProperty,
    SecurityPolicy,
    ComplianceRule,
)
from a2_bench.core.safety_monitor import SafetyMonitor
from a2_bench.core.evaluation import A2Evaluator, EvaluationResult
from a2_bench.core.decorators import (
    requires_role,
    requires_authentication,
    audit_log,
    safety_check,
)

__all__ = [
    "A2Environment",
    "ViolationType",
    "Violation",
    "SafetySpec",
    "SafetyProperty",
    "Invariant",
    "TemporalProperty",
    "SecurityPolicy",
    "ComplianceRule",
    "SafetyMonitor",
    "A2Evaluator",
    "EvaluationResult",
    "requires_role",
    "requires_authentication",
    "audit_log",
    "safety_check",
]
