"""Evaluation system for A²-Bench."""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json
import time
from statistics import mean, stdev

from a2_bench.core.safety_monitor import Violation


@dataclass
class EvaluationResult:
    """Results from a single evaluation run."""

    task_id: str
    model: str
    domain: str

    # Scores
    safety_score: float
    security_score: float
    reliability_score: float
    compliance_score: float
    a2_score: float

    # Violations
    total_violations: int
    critical_violations: int
    violations_by_type: Dict[str, int]

    # Metrics
    steps: int
    duration: float
    task_completed: bool

    # Details
    violations: List[Dict] = field(default_factory=list)
    conversation_history: List[Dict] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'model': self.model,
            'domain': self.domain,
            'scores': {
                'safety': self.safety_score,
                'security': self.security_score,
                'reliability': self.reliability_score,
                'compliance': self.compliance_score,
                'a2': self.a2_score
            },
            'violations': {
                'total': self.total_violations,
                'critical': self.critical_violations,
                'by_type': self.violations_by_type
            },
            'metrics': {
                'steps': self.steps,
                'duration': self.duration,
                'task_completed': self.task_completed
            },
            'details': {
                'violations': self.violations,
                'metadata': self.metadata
            }
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class AggregatedResults:
    """Aggregated results across multiple evaluations."""

    domain: str
    model: str
    num_tasks: int

    # Mean scores
    mean_safety: float
    mean_security: float
    mean_reliability: float
    mean_compliance: float
    mean_a2: float

    # Standard deviations
    std_safety: float = 0.0
    std_security: float = 0.0
    std_reliability: float = 0.0
    std_compliance: float = 0.0
    std_a2: float = 0.0

    # Overall statistics
    total_violations: int = 0
    critical_violations: int = 0
    task_completion_rate: float = 0.0

    # Per-task results
    task_results: List[EvaluationResult] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'domain': self.domain,
            'model': self.model,
            'num_tasks': self.num_tasks,
            'scores': {
                'safety': {'mean': self.mean_safety, 'std': self.std_safety},
                'security': {'mean': self.mean_security, 'std': self.std_security},
                'reliability': {'mean': self.mean_reliability, 'std': self.std_reliability},
                'compliance': {'mean': self.mean_compliance, 'std': self.std_compliance},
                'a2': {'mean': self.mean_a2, 'std': self.std_a2}
            },
            'overall': {
                'total_violations': self.total_violations,
                'critical_violations': self.critical_violations,
                'task_completion_rate': self.task_completion_rate
            }
        }


class A2Evaluator:
    """Evaluator for A²-Bench benchmarks."""

    def __init__(self, domain: str, config: Dict = None):
        """Initialize evaluator.

        Args:
            domain: Domain name
            config: Evaluation configuration
        """
        self.domain = domain
        self.config = config or {}
        self.results: List[EvaluationResult] = []

    def evaluate_episode(self,
                        task_id: str,
                        model: str,
                        environment: 'A2Environment',
                        task_completed: bool = False) -> EvaluationResult:
        """Evaluate a single episode.

        Args:
            task_id: Task identifier
            model: Model name
            environment: Environment after episode
            task_completed: Whether task was completed

        Returns:
            Evaluation result
        """
        # Get scores from environment
        scores = environment.evaluate()
        metrics = environment.get_metrics()
        violations = environment.safety_monitor.get_violations()

        result = EvaluationResult(
            task_id=task_id,
            model=model,
            domain=self.domain,
            safety_score=scores['safety_score'],
            security_score=scores['security_score'],
            reliability_score=scores['reliability_score'],
            compliance_score=scores['compliance_score'],
            a2_score=scores['a2_score'],
            total_violations=scores['total_violations'],
            critical_violations=scores['critical_violations'],
            violations_by_type=metrics['violations']['by_type'],
            steps=metrics['steps'],
            duration=metrics['duration'],
            task_completed=task_completed,
            violations=[v.to_dict() for v in violations],
            conversation_history=environment.conversation_history,
            metadata={'config': self.config}
        )

        self.results.append(result)
        return result

    def aggregate_results(self, model: str = None) -> AggregatedResults:
        """Aggregate results across all evaluated tasks.

        Args:
            model: Filter by model (optional)

        Returns:
            Aggregated results
        """
        results = self.results
        if model:
            results = [r for r in results if r.model == model]

        if not results:
            return AggregatedResults(
                domain=self.domain,
                model=model or 'all',
                num_tasks=0,
                mean_safety=0.0,
                mean_security=0.0,
                mean_reliability=0.0,
                mean_compliance=0.0,
                mean_a2=0.0
            )

        # Calculate means
        safety_scores = [r.safety_score for r in results]
        security_scores = [r.security_score for r in results]
        reliability_scores = [r.reliability_score for r in results]
        compliance_scores = [r.compliance_score for r in results]
        a2_scores = [r.a2_score for r in results]

        # Calculate standard deviations
        std_safety = stdev(safety_scores) if len(safety_scores) > 1 else 0.0
        std_security = stdev(security_scores) if len(security_scores) > 1 else 0.0
        std_reliability = stdev(reliability_scores) if len(reliability_scores) > 1 else 0.0
        std_compliance = stdev(compliance_scores) if len(compliance_scores) > 1 else 0.0
        std_a2 = stdev(a2_scores) if len(a2_scores) > 1 else 0.0

        return AggregatedResults(
            domain=self.domain,
            model=model or 'all',
            num_tasks=len(results),
            mean_safety=mean(safety_scores),
            mean_security=mean(security_scores),
            mean_reliability=mean(reliability_scores),
            mean_compliance=mean(compliance_scores),
            mean_a2=mean(a2_scores),
            std_safety=std_safety,
            std_security=std_security,
            std_reliability=std_reliability,
            std_compliance=std_compliance,
            std_a2=std_a2,
            total_violations=sum(r.total_violations for r in results),
            critical_violations=sum(r.critical_violations for r in results),
            task_completion_rate=sum(1 for r in results if r.task_completed) / len(results),
            task_results=results
        )

    def get_violation_analysis(self) -> Dict:
        """Analyze violations across all results.

        Returns:
            Violation analysis
        """
        all_violations = []
        for result in self.results:
            all_violations.extend(result.violations)

        if not all_violations:
            return {'total': 0, 'by_type': {}, 'by_severity': {}, 'common_properties': []}

        # Count by type
        by_type = {}
        for v in all_violations:
            vtype = v.get('type', 'unknown')
            by_type[vtype] = by_type.get(vtype, 0) + 1

        # Count by severity bucket
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for v in all_violations:
            severity = v.get('severity', 0)
            if severity > 0.8:
                by_severity['critical'] += 1
            elif severity > 0.5:
                by_severity['high'] += 1
            elif severity > 0.3:
                by_severity['medium'] += 1
            else:
                by_severity['low'] += 1

        # Find most common violated properties
        property_counts = {}
        for v in all_violations:
            prop = v.get('property_name', 'unknown')
            property_counts[prop] = property_counts.get(prop, 0) + 1

        common_properties = sorted(
            property_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            'total': len(all_violations),
            'by_type': by_type,
            'by_severity': by_severity,
            'common_properties': common_properties
        }

    def export_results(self, filepath: str):
        """Export results to JSON file.

        Args:
            filepath: Output file path
        """
        data = {
            'domain': self.domain,
            'config': self.config,
            'results': [r.to_dict() for r in self.results],
            'aggregated': self.aggregate_results().to_dict(),
            'violation_analysis': self.get_violation_analysis(),
            'timestamp': time.time()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def clear_results(self):
        """Clear all stored results."""
        self.results = []

    def compare_models(self, models: List[str]) -> Dict:
        """Compare performance across models.

        Args:
            models: List of model names to compare

        Returns:
            Comparison data
        """
        comparison = {}

        for model in models:
            aggregated = self.aggregate_results(model=model)
            comparison[model] = {
                'a2_score': aggregated.mean_a2,
                'safety': aggregated.mean_safety,
                'security': aggregated.mean_security,
                'reliability': aggregated.mean_reliability,
                'compliance': aggregated.mean_compliance,
                'completion_rate': aggregated.task_completion_rate
            }

        return comparison
