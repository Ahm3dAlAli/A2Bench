"""
Full dataset evaluation with ICML/NeurIPS-grade visualizations.
Uses ALL test cases and creates publication-quality bar and line graphs.
"""

import json
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))

from a2_bench.benchmark import A2Benchmark
from a2_bench.domains.healthcare.domain import HealthcareDomain
from a2_bench.domains.finance.domain import FinanceDomain
from a2_bench.agents.dummy import DummyAgent
from a2_bench.utils.logging import get_logger

logger = get_logger(__name__)

# ICML/NeurIPS publication settings
plt.rcParams.update({
    'figure.figsize': (12, 7),
    'font.size': 14,
    'font.family': 'serif',
    'font.serif': ['Computer Modern Roman', 'Times New Roman'],
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 13,
    'figure.titlesize': 20,
    'axes.linewidth': 1.5,
    'grid.linewidth': 0.8,
    'lines.linewidth': 2.5,
    'lines.markersize': 8,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})


class FullDatasetEvaluator:
    """Evaluate on ALL test cases with ICML-grade visualizations."""

    def __init__(self, output_dir: str = "experiments/results/icml"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

    def load_all_test_cases(self, domain: str) -> List[Dict]:
        """Load ALL test cases for a domain."""
        test_file = Path(__file__).parent.parent / "data" / domain / "test_cases_real.json"

        if not test_file.exists():
            logger.warning(f"Test cases not found: {test_file}")
            return []

        with open(test_file, 'r') as f:
            data = json.load(f)
            cases = data.get('test_cases', [])
            print(f"  Loaded {len(cases)} test cases from {test_file.name}")
            return cases

    def run_full_evaluation(self):
        """Run evaluation on ALL test cases."""

        print("="*80)
        print("FULL DATASET EVALUATION - ALL TEST CASES")
        print("="*80)

        # Initialize domains
        healthcare_domain = HealthcareDomain()
        finance_domain = FinanceDomain()

        # Load ALL test cases
        healthcare_cases = self.load_all_test_cases('healthcare')
        finance_cases = self.load_all_test_cases('finance')

        print(f"\nTotal test cases: {len(healthcare_cases) + len(finance_cases)}")
        print(f"  Healthcare: {len(healthcare_cases)}")
        print(f"  Finance: {len(finance_cases)}")

        # Model configurations
        models = {
            'baseline': {'name': 'Baseline', 'config': {'model': 'baseline'}},
            'conservative': {'name': 'Conservative', 'config': {'model': 'conservative', 'safety_threshold': 0.9}},
            'aggressive': {'name': 'Aggressive', 'config': {'model': 'aggressive', 'safety_threshold': 0.3}},
            'balanced': {'name': 'Balanced', 'config': {'model': 'balanced', 'safety_threshold': 0.6}}
        }

        all_results = []
        per_case_results = []

        # Evaluate each model on ALL test cases
        for model_key, model_info in models.items():
            print(f"\n{'='*80}")
            print(f"Evaluating: {model_info['name']}")
            print(f"{'='*80}")

            # Healthcare - ALL cases
            print(f"\n[Healthcare Domain - {len(healthcare_cases)} test cases]")
            agent = DummyAgent(config=model_info['config'])
            benchmark = A2Benchmark(domain=healthcare_domain, num_trials=1, config={'max_turns': 10})

            start_time = time.time()
            hc_results = benchmark.evaluate(agent=agent, tasks=healthcare_cases, verbose=True)
            hc_elapsed = time.time() - start_time

            # Store results
            all_results.append({
                'model': model_key,
                'model_name': model_info['name'],
                'domain': 'healthcare',
                'num_cases': len(healthcare_cases),
                'elapsed_time': hc_elapsed,
                'scores': {
                    'safety': hc_results.mean_safety,
                    'security': hc_results.mean_security,
                    'reliability': hc_results.mean_reliability,
                    'compliance': hc_results.mean_compliance,
                    'a2_score': hc_results.mean_a2
                },
                'std': {
                    'safety': hc_results.std_safety,
                    'security': hc_results.std_security,
                    'reliability': hc_results.std_reliability,
                    'compliance': hc_results.std_compliance,
                    'a2_score': hc_results.std_a2
                },
                'violations': {
                    'total': hc_results.total_violations,
                    'critical': hc_results.critical_violations
                },
                'task_completion_rate': hc_results.task_completion_rate
            })

            # Store per-case results for healthcare
            for i, task_result in enumerate(hc_results.task_results):
                per_case_results.append({
                    'model': model_key,
                    'model_name': model_info['name'],
                    'domain': 'healthcare',
                    'case_id': healthcare_cases[i].get('id', f'hc_{i}'),
                    'case_name': healthcare_cases[i].get('name', f'case_{i}'),
                    'case_type': healthcare_cases[i].get('type', 'unknown'),
                    'safety': task_result.safety_score,
                    'security': task_result.security_score,
                    'reliability': task_result.reliability_score,
                    'compliance': task_result.compliance_score,
                    'a2_score': task_result.a2_score,
                    'violations': task_result.total_violations,
                    'completed': task_result.task_completed
                })

            # Finance - ALL cases
            print(f"\n[Finance Domain - {len(finance_cases)} test cases]")
            agent = DummyAgent(config=model_info['config'])
            benchmark = A2Benchmark(domain=finance_domain, num_trials=1, config={'max_turns': 10})

            start_time = time.time()
            fin_results = benchmark.evaluate(agent=agent, tasks=finance_cases, verbose=True)
            fin_elapsed = time.time() - start_time

            # Store results
            all_results.append({
                'model': model_key,
                'model_name': model_info['name'],
                'domain': 'finance',
                'num_cases': len(finance_cases),
                'elapsed_time': fin_elapsed,
                'scores': {
                    'safety': fin_results.mean_safety,
                    'security': fin_results.mean_security,
                    'reliability': fin_results.mean_reliability,
                    'compliance': fin_results.mean_compliance,
                    'a2_score': fin_results.mean_a2
                },
                'std': {
                    'safety': fin_results.std_safety,
                    'security': fin_results.std_security,
                    'reliability': fin_results.std_reliability,
                    'compliance': fin_results.std_compliance,
                    'a2_score': fin_results.std_a2
                },
                'violations': {
                    'total': fin_results.total_violations,
                    'critical': fin_results.critical_violations
                },
                'task_completion_rate': fin_results.task_completion_rate
            })

            # Store per-case results for finance
            for i, task_result in enumerate(fin_results.task_results):
                per_case_results.append({
                    'model': model_key,
                    'model_name': model_info['name'],
                    'domain': 'finance',
                    'case_id': finance_cases[i].get('id', f'fin_{i}'),
                    'case_name': finance_cases[i].get('name', f'case_{i}'),
                    'case_type': finance_cases[i].get('type', 'unknown'),
                    'safety': task_result.safety_score,
                    'security': task_result.security_score,
                    'reliability': task_result.reliability_score,
                    'compliance': task_result.compliance_score,
                    'a2_score': task_result.a2_score,
                    'violations': task_result.total_violations,
                    'completed': task_result.task_completed
                })

        self.results = {
            'aggregate_results': all_results,
            'per_case_results': per_case_results,
            'metadata': {
                'total_cases': len(healthcare_cases) + len(finance_cases),
                'healthcare_cases': len(healthcare_cases),
                'finance_cases': len(finance_cases),
                'models': len(models),
                'timestamp': self.timestamp
            }
        }

        # Save results
        output_file = self.output_dir / f'full_results_{self.timestamp}.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Saved results to: {output_file}")

        return self.results

    def create_bar_graphs(self):
        """Create ICML-grade bar graph visualizations."""

        print("\n" + "="*80)
        print("Creating Bar Graph Visualizations")
        print("="*80)

        results_df = pd.DataFrame(self.results['aggregate_results'])

        # 1. Overall Performance Bar Chart
        fig, ax = plt.subplots(figsize=(14, 8))

        models = results_df['model_name'].unique()
        x = np.arange(len(models))
        width = 0.35

        hc_scores = []
        fin_scores = []

        for model in models:
            hc_data = results_df[(results_df['model_name'] == model) &
                                (results_df['domain'] == 'healthcare')]
            fin_data = results_df[(results_df['model_name'] == model) &
                                 (results_df['domain'] == 'finance')]

            hc_scores.append(hc_data.iloc[0]['scores']['a2_score'] if not hc_data.empty else 0)
            fin_scores.append(fin_data.iloc[0]['scores']['a2_score'] if not fin_data.empty else 0)

        bars1 = ax.bar(x - width/2, hc_scores, width, label='Healthcare',
                      color='#2E86AB', alpha=0.9, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, fin_scores, width, label='Finance',
                      color='#A23B72', alpha=0.9, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('Model Configuration', fontweight='bold', fontsize=18)
        ax.set_ylabel('A² Score', fontweight='bold', fontsize=18)
        ax.set_title('Overall Performance: A² Score by Model and Domain\n(Full Dataset Evaluation)',
                    fontweight='bold', fontsize=20, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(models, fontsize=16)
        ax.set_ylim(0, 1.15)
        ax.legend(loc='upper right', fontsize=15, framealpha=0.95, edgecolor='black', fancybox=False)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1)
        ax.axhline(y=1.0, color='green', linestyle=':', linewidth=2, alpha=0.4, label='Perfect Score')

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                       f'{height:.3f}',
                       ha='center', va='bottom', fontsize=13, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_dir / f'bar_overall_performance_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

        # 2. Metric-wise Bar Chart
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        axes = axes.flatten()

        metrics = ['safety', 'security', 'reliability', 'compliance']
        metric_names = ['Safety Score', 'Security Score', 'Reliability Score', 'Compliance Score']
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

        for idx, (metric, metric_name, color) in enumerate(zip(metrics, metric_names, colors)):
            ax = axes[idx]

            hc_scores = []
            fin_scores = []

            for model in models:
                hc_data = results_df[(results_df['model_name'] == model) &
                                    (results_df['domain'] == 'healthcare')]
                fin_data = results_df[(results_df['model_name'] == model) &
                                     (results_df['domain'] == 'finance')]

                hc_scores.append(hc_data.iloc[0]['scores'][metric] if not hc_data.empty else 0)
                fin_scores.append(fin_data.iloc[0]['scores'][metric] if not fin_data.empty else 0)

            x = np.arange(len(models))
            width = 0.35

            ax.bar(x - width/2, hc_scores, width, label='Healthcare',
                  color=color, alpha=0.7, edgecolor='black', linewidth=1.5)
            ax.bar(x + width/2, fin_scores, width, label='Finance',
                  color=color, alpha=0.4, edgecolor='black', linewidth=1.5)

            ax.set_ylabel(metric_name, fontweight='bold', fontsize=16)
            ax.set_title(f'{metric_name} Comparison', fontweight='bold', fontsize=17, pad=10)
            ax.set_xticks(x)
            ax.set_xticklabels(models, fontsize=13, rotation=20, ha='right')
            ax.set_ylim(0, 1.15)
            ax.legend(loc='upper right', fontsize=12)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.axhline(y=1.0, color='green', linestyle=':', linewidth=1.5, alpha=0.3)

            # Add value labels
            for i, (hc, fin) in enumerate(zip(hc_scores, fin_scores)):
                ax.text(i - width/2, hc + 0.02, f'{hc:.2f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
                ax.text(i + width/2, fin + 0.02, f'{fin:.2f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.suptitle('Detailed Metric Analysis Across All Models and Domains',
                    fontsize=22, fontweight='bold', y=0.995)
        plt.tight_layout()

        output_file = self.output_dir / f'bar_metric_breakdown_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

        # 3. Violations Bar Chart
        fig, ax = plt.subplots(figsize=(14, 8))

        hc_violations = []
        fin_violations = []

        for model in models:
            hc_data = results_df[(results_df['model_name'] == model) &
                                (results_df['domain'] == 'healthcare')]
            fin_data = results_df[(results_df['model_name'] == model) &
                                 (results_df['domain'] == 'finance')]

            hc_violations.append(hc_data.iloc[0]['violations']['total'] if not hc_data.empty else 0)
            fin_violations.append(fin_data.iloc[0]['violations']['total'] if not fin_data.empty else 0)

        x = np.arange(len(models))
        width = 0.35

        bars1 = ax.bar(x - width/2, hc_violations, width, label='Healthcare',
                      color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, fin_violations, width, label='Finance',
                      color='#D62828', alpha=0.8, edgecolor='black', linewidth=1.5)

        ax.set_xlabel('Model Configuration', fontweight='bold', fontsize=18)
        ax.set_ylabel('Total Violations', fontweight='bold', fontsize=18)
        ax.set_title('Safety Violations by Model and Domain\n(Full Dataset)',
                    fontweight='bold', fontsize=20, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(models, fontsize=16)
        ax.legend(loc='upper right', fontsize=15, framealpha=0.95, edgecolor='black')
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1)

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=13, fontweight='bold')

        plt.tight_layout()
        output_file = self.output_dir / f'bar_violations_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

    def create_line_graphs(self):
        """Create ICML-grade line graph visualizations."""

        print("\n" + "="*80)
        print("Creating Line Graph Visualizations")
        print("="*80)

        per_case_df = pd.DataFrame(self.results['per_case_results'])

        # 1. Performance Trends Across Test Cases
        fig, axes = plt.subplots(1, 2, figsize=(18, 7))

        for idx, domain in enumerate(['healthcare', 'finance']):
            ax = axes[idx]
            domain_data = per_case_df[per_case_df['domain'] == domain]

            models = domain_data['model_name'].unique()
            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
            markers = ['o', 's', '^', 'D']

            for model_idx, model in enumerate(models):
                model_data = domain_data[domain_data['model_name'] == model].sort_values('case_id')

                x = np.arange(len(model_data))
                y = model_data['a2_score'].values

                ax.plot(x, y, marker=markers[model_idx], label=model,
                       color=colors[model_idx], linewidth=2.5, markersize=7,
                       alpha=0.85, markeredgecolor='black', markeredgewidth=1)

            ax.set_xlabel('Test Case Index', fontweight='bold', fontsize=16)
            ax.set_ylabel('A² Score', fontweight='bold', fontsize=16)
            ax.set_title(f'{domain.capitalize()} Domain: Per-Case Performance',
                        fontweight='bold', fontsize=18, pad=15)
            ax.legend(loc='best', fontsize=13, framealpha=0.95, edgecolor='black')
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_ylim(-0.05, 1.15)
            ax.axhline(y=1.0, color='green', linestyle=':', linewidth=2, alpha=0.4)
            ax.axhline(y=0.5, color='orange', linestyle=':', linewidth=2, alpha=0.4)

        plt.suptitle('A² Score Progression Across All Test Cases',
                    fontsize=22, fontweight='bold', y=1.00)
        plt.tight_layout()

        output_file = self.output_dir / f'line_per_case_performance_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

        # 2. Metric Evolution Line Graphs
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))
        axes = axes.flatten()

        metrics = ['safety', 'security', 'reliability', 'compliance']
        metric_names = ['Safety', 'Security', 'Reliability', 'Compliance']

        for metric_idx, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
            ax = axes[metric_idx]

            # Healthcare line
            hc_data = per_case_df[per_case_df['domain'] == 'healthcare']
            hc_grouped = hc_data.groupby('model_name')[metric].apply(list).to_dict()

            # Finance line
            fin_data = per_case_df[per_case_df['domain'] == 'finance']
            fin_grouped = fin_data.groupby('model_name')[metric].apply(list).to_dict()

            colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']

            for idx, model in enumerate(hc_grouped.keys()):
                # Healthcare
                if model in hc_grouped:
                    x_hc = np.arange(len(hc_grouped[model]))
                    ax.plot(x_hc, hc_grouped[model], marker='o', label=f'{model} (HC)',
                           color=colors[idx], linewidth=2, markersize=5, alpha=0.7,
                           linestyle='-')

                # Finance
                if model in fin_grouped:
                    x_fin = np.arange(len(fin_grouped[model]))
                    ax.plot(x_fin, fin_grouped[model], marker='s', label=f'{model} (Fin)',
                           color=colors[idx], linewidth=2, markersize=5, alpha=0.7,
                           linestyle='--')

            ax.set_xlabel('Test Case Index', fontweight='bold', fontsize=14)
            ax.set_ylabel(f'{metric_name} Score', fontweight='bold', fontsize=14)
            ax.set_title(f'{metric_name} Metric Evolution', fontweight='bold', fontsize=16)
            ax.legend(loc='best', fontsize=10, ncol=2)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_ylim(-0.05, 1.15)

        plt.suptitle('Metric-wise Performance Evolution Across Test Cases',
                    fontsize=22, fontweight='bold', y=0.995)
        plt.tight_layout()

        output_file = self.output_dir / f'line_metric_evolution_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

        # 3. Cumulative Performance Line Graph
        fig, ax = plt.subplots(figsize=(14, 8))

        models = per_case_df['model_name'].unique()
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        markers = ['o', 's', '^', 'D']

        for idx, model in enumerate(models):
            model_data = per_case_df[per_case_df['model_name'] == model].sort_values('case_id')

            # Calculate cumulative average A² score
            cumulative_avg = np.cumsum(model_data['a2_score'].values) / np.arange(1, len(model_data) + 1)
            x = np.arange(len(cumulative_avg))

            ax.plot(x, cumulative_avg, marker=markers[idx], label=model,
                   color=colors[idx], linewidth=3, markersize=6,
                   alpha=0.85, markeredgecolor='black', markeredgewidth=1,
                   markevery=max(1, len(x)//20))

        ax.set_xlabel('Number of Test Cases Evaluated', fontweight='bold', fontsize=18)
        ax.set_ylabel('Cumulative Average A² Score', fontweight='bold', fontsize=18)
        ax.set_title('Cumulative Performance: Running Average A² Score\n(All Test Cases Combined)',
                    fontweight='bold', fontsize=20, pad=20)
        ax.legend(loc='best', fontsize=15, framealpha=0.95, edgecolor='black')
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
        ax.set_ylim(0, 1.15)
        ax.axhline(y=1.0, color='green', linestyle=':', linewidth=2, alpha=0.4)
        ax.axhline(y=0.75, color='orange', linestyle=':', linewidth=2, alpha=0.4)
        ax.axhline(y=0.5, color='red', linestyle=':', linewidth=2, alpha=0.4)

        plt.tight_layout()
        output_file = self.output_dir / f'line_cumulative_performance_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()


def main():
    """Main execution."""
    print("="*80)
    print("FULL DATASET EVALUATION WITH ICML/NEURIPS VISUALIZATIONS")
    print("="*80)

    evaluator = FullDatasetEvaluator()

    # Run full evaluation
    print("\n[1/3] Running evaluation on ALL test cases...")
    evaluator.run_full_evaluation()

    # Create visualizations
    print("\n[2/3] Creating bar graph visualizations...")
    evaluator.create_bar_graphs()

    print("\n[3/3] Creating line graph visualizations...")
    evaluator.create_line_graphs()

    print("\n" + "="*80)
    print("✓ FULL EVALUATION COMPLETE")
    print("="*80)
    print(f"\nAll results saved to: {evaluator.output_dir}")
    print("\nGenerated visualizations:")
    print("  - Overall performance bar chart")
    print("  - Metric breakdown bar charts")
    print("  - Violations bar chart")
    print("  - Per-case performance line graphs")
    print("  - Metric evolution line graphs")
    print("  - Cumulative performance line graph")


if __name__ == "__main__":
    main()
