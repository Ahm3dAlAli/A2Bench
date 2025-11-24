"""Result analysis utilities for A²-Bench."""

from typing import Dict, List, Any
from statistics import mean, stdev
import json


class ResultAnalyzer:
    """Analyzer for benchmark results."""

    def __init__(self, results: List[Dict] = None):
        """Initialize analyzer.

        Args:
            results: List of evaluation results
        """
        self.results = results or []

    def load_results(self, filepath: str):
        """Load results from JSON file.

        Args:
            filepath: Path to results file
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.results = data.get('results', [])

    def get_score_statistics(self, score_type: str = 'a2') -> Dict:
        """Get statistics for a score type.

        Args:
            score_type: Type of score (safety, security, reliability, compliance, a2)

        Returns:
            Statistics dictionary
        """
        if not self.results:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}

        scores = []
        for r in self.results:
            score_dict = r.get('scores', {})
            score = score_dict.get(score_type, 0)
            scores.append(score)

        return {
            'mean': mean(scores),
            'std': stdev(scores) if len(scores) > 1 else 0,
            'min': min(scores),
            'max': max(scores),
            'count': len(scores)
        }

    def get_violation_breakdown(self) -> Dict:
        """Get breakdown of violations by type.

        Returns:
            Violation breakdown
        """
        breakdown = {
            'safety_critical': 0,
            'security_breach': 0,
            'reliability_failure': 0,
            'compliance_violation': 0
        }

        for r in self.results:
            violations = r.get('violations', {})
            by_type = violations.get('by_type', {})
            for vtype, count in by_type.items():
                breakdown[vtype] = breakdown.get(vtype, 0) + count

        return breakdown

    def compare_by_model(self) -> Dict:
        """Compare results by model.

        Returns:
            Model comparison
        """
        models = {}

        for r in self.results:
            model = r.get('model', 'unknown')
            if model not in models:
                models[model] = []
            models[model].append(r)

        comparison = {}
        for model, results in models.items():
            scores = [r.get('scores', {}).get('a2', 0) for r in results]
            comparison[model] = {
                'a2_mean': mean(scores) if scores else 0,
                'count': len(results)
            }

        return comparison

    def export_summary(self, filepath: str):
        """Export analysis summary to file.

        Args:
            filepath: Output file path
        """
        summary = {
            'total_results': len(self.results),
            'scores': {
                'safety': self.get_score_statistics('safety'),
                'security': self.get_score_statistics('security'),
                'reliability': self.get_score_statistics('reliability'),
                'compliance': self.get_score_statistics('compliance'),
                'a2': self.get_score_statistics('a2')
            },
            'violations': self.get_violation_breakdown(),
            'by_model': self.compare_by_model()
        }

        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
