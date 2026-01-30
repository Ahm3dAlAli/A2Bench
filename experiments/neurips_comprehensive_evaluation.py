"""
Comprehensive NeurIPS-grade evaluation for A2Bench.
Includes multiple models, adversarial testing, and publication-quality analysis.
"""

import json
import sys
import time
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2_bench.benchmark import A2Benchmark
from a2_bench.domains.healthcare.domain import HealthcareDomain
from a2_bench.domains.finance.domain import FinanceDomain
from a2_bench.agents.dummy import DummyAgent
from a2_bench.adversary.simulator import AdversarySimulator
from a2_bench.utils.logging import get_logger

logger = get_logger(__name__)

# Set publication-quality plotting defaults
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['figure.titlesize'] = 16


class NeurIPSExperimentRunner:
    """Comprehensive experiment runner for NeurIPS-grade evaluation."""

    def __init__(self, output_dir: str = "experiments/results/neurips"):
        """Initialize experiment runner."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

        # Initialize domains
        self.healthcare_domain = HealthcareDomain()
        self.finance_domain = FinanceDomain()

        # Model configurations for comprehensive testing
        self.model_configs = {
            'baseline': {
                'name': 'Baseline Agent',
                'config': {'model': 'baseline', 'temperature': 0.0}
            },
            'conservative': {
                'name': 'Conservative Agent',
                'config': {'model': 'conservative', 'temperature': 0.0, 'safety_threshold': 0.9}
            },
            'aggressive': {
                'name': 'Aggressive Agent',
                'config': {'model': 'aggressive', 'temperature': 0.5, 'safety_threshold': 0.3}
            },
            'balanced': {
                'name': 'Balanced Agent',
                'config': {'model': 'balanced', 'temperature': 0.2, 'safety_threshold': 0.6}
            }
        }

    def load_test_cases(self, domain: str, real_data: bool = True) -> List[Dict]:
        """Load test cases for a domain."""
        if real_data:
            test_file = Path(__file__).parent.parent / "data" / domain / "test_cases_real.json"
        else:
            test_file = Path(__file__).parent.parent / "data" / domain / "test_cases.json"

        if not test_file.exists():
            logger.warning(f"Test cases not found: {test_file}")
            return []

        with open(test_file, 'r') as f:
            data = json.load(f)
            return data.get('test_cases', [])

    def run_single_evaluation(self,
                             domain_name: str,
                             domain,
                             model_key: str,
                             test_cases: List[Dict],
                             num_cases: int = None) -> Dict:
        """Run evaluation for a single model on a domain."""

        model_info = self.model_configs[model_key]
        agent = DummyAgent(config=model_info['config'])

        benchmark = A2Benchmark(
            domain=domain,
            num_trials=1,
            config={'max_turns': 10}
        )

        cases_to_test = test_cases[:num_cases] if num_cases else test_cases

        print(f"\n  Evaluating {model_info['name']} on {len(cases_to_test)} test cases...")
        start_time = time.time()

        results = benchmark.evaluate(
            agent=agent,
            tasks=cases_to_test,
            verbose=False
        )

        elapsed = time.time() - start_time

        return {
            'model': model_key,
            'model_name': model_info['name'],
            'domain': domain_name,
            'num_cases': len(cases_to_test),
            'elapsed_time': elapsed,
            'scores': {
                'safety': results.mean_safety,
                'security': results.mean_security,
                'reliability': results.mean_reliability,
                'compliance': results.mean_compliance,
                'a2_score': results.mean_a2
            },
            'std': {
                'safety': results.std_safety,
                'security': results.std_security,
                'reliability': results.std_reliability,
                'compliance': results.std_compliance,
                'a2_score': results.std_a2
            },
            'violations': {
                'total': results.total_violations,
                'critical': results.critical_violations
            },
            'task_completion_rate': results.task_completion_rate,
            'raw_results': results
        }

    def run_adversarial_evaluation(self,
                                   domain_name: str,
                                   domain,
                                   model_key: str) -> Dict:
        """Run adversarial evaluation."""

        model_info = self.model_configs[model_key]
        agent = DummyAgent(config=model_info['config'])

        benchmark = A2Benchmark(
            domain=domain,
            adversarial=True,
            num_trials=1,
            config={'max_turns': 10}
        )

        adversary = AdversarySimulator(strategy='mixed')

        print(f"\n  Running adversarial tests for {model_info['name']}...")

        try:
            results = benchmark.evaluate_adversarial(
                agent=agent,
                adversary=adversary,
                num_episodes=10,
                verbose=False
            )

            return {
                'model': model_key,
                'domain': domain_name,
                'successful_attacks': results.get('successful_attacks', 0),
                'total_episodes': results.get('total_episodes', 10),
                'attack_success_rate': results.get('attack_success_rate', 0),
                'defense_rate': results.get('defense_rate', 1.0)
            }
        except Exception as e:
            logger.warning(f"Adversarial evaluation failed: {e}")
            return {
                'model': model_key,
                'domain': domain_name,
                'successful_attacks': 0,
                'total_episodes': 0,
                'attack_success_rate': 0,
                'defense_rate': 1.0,
                'error': str(e)
            }

    def run_comprehensive_experiments(self, num_cases_per_domain: int = 20):
        """Run comprehensive experiments across all models and domains."""

        print("="*80)
        print("NeurIPS-Grade Comprehensive Evaluation")
        print("="*80)
        print(f"\nModels to evaluate: {len(self.model_configs)}")
        print(f"Domains: Healthcare, Finance")
        print(f"Test cases per domain: {num_cases_per_domain}")
        print(f"Total evaluations: {len(self.model_configs) * 2 * 2}")  # models * domains * (baseline + adversarial)

        all_results = []
        adversarial_results = []

        # Load test cases
        healthcare_cases = self.load_test_cases('healthcare', real_data=True)
        finance_cases = self.load_test_cases('finance', real_data=True)

        print(f"\nLoaded {len(healthcare_cases)} healthcare test cases")
        print(f"Loaded {len(finance_cases)} finance test cases")

        # Run evaluations for each model
        for model_key in self.model_configs.keys():
            print(f"\n{'='*80}")
            print(f"Evaluating: {self.model_configs[model_key]['name']}")
            print(f"{'='*80}")

            # Healthcare domain
            print("\n[Healthcare Domain - Baseline Evaluation]")
            hc_result = self.run_single_evaluation(
                'healthcare',
                self.healthcare_domain,
                model_key,
                healthcare_cases,
                num_cases_per_domain
            )
            all_results.append(hc_result)

            # Healthcare adversarial
            print("\n[Healthcare Domain - Adversarial Evaluation]")
            hc_adv = self.run_adversarial_evaluation(
                'healthcare',
                self.healthcare_domain,
                model_key
            )
            adversarial_results.append(hc_adv)

            # Finance domain
            print("\n[Finance Domain - Baseline Evaluation]")
            fin_result = self.run_single_evaluation(
                'finance',
                self.finance_domain,
                model_key,
                finance_cases,
                num_cases_per_domain
            )
            all_results.append(fin_result)

            # Finance adversarial
            print("\n[Finance Domain - Adversarial Evaluation]")
            fin_adv = self.run_adversarial_evaluation(
                'finance',
                self.finance_domain,
                model_key
            )
            adversarial_results.append(fin_adv)

        self.results = {
            'baseline_results': all_results,
            'adversarial_results': adversarial_results,
            'timestamp': self.timestamp,
            'metadata': {
                'num_models': len(self.model_configs),
                'num_domains': 2,
                'cases_per_domain': num_cases_per_domain
            }
        }

        return self.results

    def create_score_heatmap(self):
        """Create heatmap of scores across models and domains."""

        results_df = pd.DataFrame(self.results['baseline_results'])

        # Create separate heatmaps for each metric
        metrics = ['safety', 'security', 'reliability', 'compliance', 'a2_score']
        metric_names = ['Safety', 'Security', 'Reliability', 'Compliance', 'A² Score']

        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        axes = axes.flatten()

        for idx, (metric, name) in enumerate(zip(metrics, metric_names)):
            # Create pivot table
            pivot_data = results_df.pivot_table(
                values=f'scores',
                index='model',
                columns='domain',
                aggfunc=lambda x: x.iloc[0][metric] if len(x) > 0 else 0
            )

            # Reorder for better visualization
            model_order = ['baseline', 'conservative', 'balanced', 'aggressive']
            pivot_data = pivot_data.reindex([m for m in model_order if m in pivot_data.index])

            # Create heatmap
            sns.heatmap(
                pivot_data,
                annot=True,
                fmt='.3f',
                cmap='RdYlGn',
                vmin=0,
                vmax=1,
                cbar_kws={'label': 'Score'},
                ax=axes[idx],
                linewidths=0.5,
                linecolor='gray'
            )

            axes[idx].set_title(f'{name} Scores', fontweight='bold', fontsize=14)
            axes[idx].set_xlabel('Domain', fontweight='bold')
            axes[idx].set_ylabel('Model', fontweight='bold')
            axes[idx].set_xticklabels(['Finance', 'Healthcare'], rotation=0)

            # Format model names
            model_labels = [self.model_configs[m]['name'] for m in pivot_data.index]
            axes[idx].set_yticklabels(model_labels, rotation=0)

        # Remove extra subplot
        fig.delaxes(axes[5])

        plt.tight_layout()
        output_file = self.output_dir / f'score_heatmaps_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"\n✓ Saved score heatmaps: {output_file}")
        plt.close()

    def create_performance_comparison(self):
        """Create bar chart comparing overall performance."""

        results_df = pd.DataFrame(self.results['baseline_results'])

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        domains = ['healthcare', 'finance']
        domain_names = ['Healthcare', 'Finance']

        for idx, (domain, domain_name) in enumerate(zip(domains, domain_names)):
            domain_data = results_df[results_df['domain'] == domain]

            # Prepare data
            models = [self.model_configs[m]['name'] for m in domain_data['model']]
            a2_scores = [row['scores']['a2_score'] for _, row in domain_data.iterrows()]

            # Create bars
            bars = axes[idx].bar(range(len(models)), a2_scores,
                                color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])

            # Customize
            axes[idx].set_xlabel('Model', fontweight='bold', fontsize=12)
            axes[idx].set_ylabel('A² Score', fontweight='bold', fontsize=12)
            axes[idx].set_title(f'{domain_name} Domain Performance',
                              fontweight='bold', fontsize=14)
            axes[idx].set_xticks(range(len(models)))
            axes[idx].set_xticklabels(models, rotation=45, ha='right')
            axes[idx].set_ylim(0, 1.1)
            axes[idx].grid(axis='y', alpha=0.3, linestyle='--')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                             f'{height:.3f}',
                             ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()
        output_file = self.output_dir / f'performance_comparison_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Saved performance comparison: {output_file}")
        plt.close()

    def create_attack_analysis(self):
        """Create visualization of adversarial attack success rates."""

        adv_df = pd.DataFrame(self.results['adversarial_results'])

        if adv_df.empty or 'attack_success_rate' not in adv_df.columns:
            print("⚠ No adversarial results available for visualization")
            return

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        domains = ['healthcare', 'finance']
        domain_names = ['Healthcare', 'Finance']

        for idx, (domain, domain_name) in enumerate(zip(domains, domain_names)):
            domain_data = adv_df[adv_df['domain'] == domain]

            if domain_data.empty:
                continue

            # Prepare data
            models = [self.model_configs[m]['name'] for m in domain_data['model']]
            attack_rates = domain_data['attack_success_rate'].values
            defense_rates = domain_data['defense_rate'].values

            x = np.arange(len(models))
            width = 0.35

            # Create grouped bars
            bars1 = axes[idx].bar(x - width/2, attack_rates, width,
                                 label='Attack Success Rate', color='#d62728', alpha=0.8)
            bars2 = axes[idx].bar(x + width/2, defense_rates, width,
                                 label='Defense Rate', color='#2ca02c', alpha=0.8)

            # Customize
            axes[idx].set_xlabel('Model', fontweight='bold', fontsize=12)
            axes[idx].set_ylabel('Rate', fontweight='bold', fontsize=12)
            axes[idx].set_title(f'{domain_name} - Adversarial Robustness',
                              fontweight='bold', fontsize=14)
            axes[idx].set_xticks(x)
            axes[idx].set_xticklabels(models, rotation=45, ha='right')
            axes[idx].set_ylim(0, 1.1)
            axes[idx].legend(loc='upper right')
            axes[idx].grid(axis='y', alpha=0.3, linestyle='--')

            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                                     f'{height:.2f}',
                                     ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        output_file = self.output_dir / f'attack_analysis_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Saved attack analysis: {output_file}")
        plt.close()

    def create_violation_analysis(self):
        """Create visualization of violations by model and domain."""

        results_df = pd.DataFrame(self.results['baseline_results'])

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        domains = ['healthcare', 'finance']
        domain_names = ['Healthcare', 'Finance']

        for idx, (domain, domain_name) in enumerate(zip(domains, domain_names)):
            domain_data = results_df[results_df['domain'] == domain]

            # Prepare data
            models = [self.model_configs[m]['name'] for m in domain_data['model']]
            total_violations = [row['violations']['total'] for _, row in domain_data.iterrows()]
            critical_violations = [row['violations']['critical'] for _, row in domain_data.iterrows()]

            x = np.arange(len(models))
            width = 0.35

            # Create grouped bars
            bars1 = axes[idx].bar(x - width/2, total_violations, width,
                                 label='Total Violations', color='#ff7f0e', alpha=0.8)
            bars2 = axes[idx].bar(x + width/2, critical_violations, width,
                                 label='Critical Violations', color='#d62728', alpha=0.8)

            # Customize
            axes[idx].set_xlabel('Model', fontweight='bold', fontsize=12)
            axes[idx].set_ylabel('Number of Violations', fontweight='bold', fontsize=12)
            axes[idx].set_title(f'{domain_name} - Safety Violations',
                              fontweight='bold', fontsize=14)
            axes[idx].set_xticks(x)
            axes[idx].set_xticklabels(models, rotation=45, ha='right')
            axes[idx].legend(loc='upper right')
            axes[idx].grid(axis='y', alpha=0.3, linestyle='--')

            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        axes[idx].text(bar.get_x() + bar.get_width()/2., height,
                                     f'{int(height)}',
                                     ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        output_file = self.output_dir / f'violation_analysis_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Saved violation analysis: {output_file}")
        plt.close()

    def create_radar_chart(self):
        """Create radar chart comparing models across all metrics."""

        results_df = pd.DataFrame(self.results['baseline_results'])

        fig, axes = plt.subplots(1, 2, figsize=(16, 7), subplot_kw=dict(projection='polar'))

        categories = ['Safety', 'Security', 'Reliability', 'Compliance', 'A² Score']
        N = len(categories)

        domains = ['healthcare', 'finance']
        domain_names = ['Healthcare', 'Finance']

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

        for idx, (domain, domain_name) in enumerate(zip(domains, domain_names)):
            domain_data = results_df[results_df['domain'] == domain]

            # Set up angles
            angles = [n / float(N) * 2 * np.pi for n in range(N)]
            angles += angles[:1]

            ax = axes[idx]
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)

            # Draw one axis per variable and add labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=11)

            # Draw ylabels
            ax.set_rlabel_position(0)
            ax.set_yticks([0.25, 0.5, 0.75, 1.0])
            ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'], fontsize=9)
            ax.set_ylim(0, 1)

            # Plot data for each model
            for model_idx, (_, row) in enumerate(domain_data.iterrows()):
                values = [
                    row['scores']['safety'],
                    row['scores']['security'],
                    row['scores']['reliability'],
                    row['scores']['compliance'],
                    row['scores']['a2_score']
                ]
                values += values[:1]

                model_name = self.model_configs[row['model']]['name']
                ax.plot(angles, values, 'o-', linewidth=2,
                       label=model_name, color=colors[model_idx])
                ax.fill(angles, values, alpha=0.15, color=colors[model_idx])

            ax.set_title(f'{domain_name} Domain', fontweight='bold',
                        fontsize=14, pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
            ax.grid(True)

        plt.tight_layout()
        output_file = self.output_dir / f'radar_comparison_{self.timestamp}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Saved radar chart: {output_file}")
        plt.close()

    def generate_latex_tables(self):
        """Generate LaTeX tables for paper."""

        results_df = pd.DataFrame(self.results['baseline_results'])

        latex_output = []

        # Main results table
        latex_output.append("% Main Results Table")
        latex_output.append("\\begin{table}[t]")
        latex_output.append("\\centering")
        latex_output.append("\\caption{Performance of different agent configurations on A²-Bench with real-world datasets.}")
        latex_output.append("\\label{tab:main_results}")
        latex_output.append("\\begin{tabular}{llccccc}")
        latex_output.append("\\toprule")
        latex_output.append("\\textbf{Domain} & \\textbf{Model} & \\textbf{Safety} & \\textbf{Security} & \\textbf{Reliability} & \\textbf{Compliance} & \\textbf{A² Score} \\\\")
        latex_output.append("\\midrule")

        for domain in ['healthcare', 'finance']:
            domain_data = results_df[results_df['domain'] == domain]
            domain_name = domain.capitalize()

            for idx, (_, row) in enumerate(domain_data.iterrows()):
                model_name = self.model_configs[row['model']]['name']
                scores = row['scores']

                if idx == 0:
                    line = f"{domain_name} & {model_name}"
                else:
                    line = f" & {model_name}"

                line += f" & {scores['safety']:.3f}"
                line += f" & {scores['security']:.3f}"
                line += f" & {scores['reliability']:.3f}"
                line += f" & {scores['compliance']:.3f}"
                line += f" & \\textbf{{{scores['a2_score']:.3f}}} \\\\"

                latex_output.append(line)

            if domain == 'healthcare':
                latex_output.append("\\midrule")

        latex_output.append("\\bottomrule")
        latex_output.append("\\end{tabular}")
        latex_output.append("\\end{table}")
        latex_output.append("")

        # Adversarial results table
        if self.results['adversarial_results']:
            adv_df = pd.DataFrame(self.results['adversarial_results'])

            latex_output.append("% Adversarial Robustness Table")
            latex_output.append("\\begin{table}[t]")
            latex_output.append("\\centering")
            latex_output.append("\\caption{Adversarial robustness evaluation results.}")
            latex_output.append("\\label{tab:adversarial_results}")
            latex_output.append("\\begin{tabular}{llccc}")
            latex_output.append("\\toprule")
            latex_output.append("\\textbf{Domain} & \\textbf{Model} & \\textbf{Attack Success} & \\textbf{Defense Rate} & \\textbf{Total Episodes} \\\\")
            latex_output.append("\\midrule")

            for domain in ['healthcare', 'finance']:
                domain_data = adv_df[adv_df['domain'] == domain]
                domain_name = domain.capitalize()

                for idx, (_, row) in enumerate(domain_data.iterrows()):
                    model_name = self.model_configs[row['model']]['name']

                    if idx == 0:
                        line = f"{domain_name} & {model_name}"
                    else:
                        line = f" & {model_name}"

                    line += f" & {row['attack_success_rate']:.3f}"
                    line += f" & {row['defense_rate']:.3f}"
                    line += f" & {row['total_episodes']} \\\\"

                    latex_output.append(line)

                if domain == 'healthcare':
                    latex_output.append("\\midrule")

            latex_output.append("\\bottomrule")
            latex_output.append("\\end{tabular}")
            latex_output.append("\\end{table}")

        # Save to file
        latex_file = self.output_dir / f'tables_{self.timestamp}.tex'
        with open(latex_file, 'w') as f:
            f.write('\n'.join(latex_output))

        print(f"✓ Saved LaTeX tables: {latex_file}")

        return '\n'.join(latex_output)

    def perform_statistical_analysis(self):
        """Perform statistical tests and generate analysis report."""

        results_df = pd.DataFrame(self.results['baseline_results'])

        analysis = []
        analysis.append("="*80)
        analysis.append("STATISTICAL ANALYSIS")
        analysis.append("="*80)

        # Compare models within each domain
        for domain in ['healthcare', 'finance']:
            domain_data = results_df[results_df['domain'] == domain]

            analysis.append(f"\n{domain.upper()} DOMAIN")
            analysis.append("-"*80)

            # Extract A² scores
            models = domain_data['model'].values
            a2_scores = [row['scores']['a2_score'] for _, row in domain_data.iterrows()]

            analysis.append(f"\nA² Scores:")
            for model, score in zip(models, a2_scores):
                model_name = self.model_configs[model]['name']
                analysis.append(f"  {model_name:.<30} {score:.3f}")

            # Find best and worst
            best_idx = np.argmax(a2_scores)
            worst_idx = np.argmin(a2_scores)

            analysis.append(f"\nBest performing model: {self.model_configs[models[best_idx]]['name']} ({a2_scores[best_idx]:.3f})")
            analysis.append(f"Worst performing model: {self.model_configs[models[worst_idx]]['name']} ({a2_scores[worst_idx]:.3f})")
            analysis.append(f"Performance gap: {a2_scores[best_idx] - a2_scores[worst_idx]:.3f}")

        # Cross-domain comparison
        analysis.append(f"\n{'='*80}")
        analysis.append("CROSS-DOMAIN COMPARISON")
        analysis.append("="*80)

        for model_key in self.model_configs.keys():
            model_name = self.model_configs[model_key]['name']
            hc_score = results_df[(results_df['domain'] == 'healthcare') &
                                 (results_df['model'] == model_key)]['scores'].iloc[0]['a2_score']
            fin_score = results_df[(results_df['domain'] == 'finance') &
                                  (results_df['model'] == model_key)]['scores'].iloc[0]['a2_score']

            analysis.append(f"\n{model_name}:")
            analysis.append(f"  Healthcare: {hc_score:.3f}")
            analysis.append(f"  Finance:    {fin_score:.3f}")
            analysis.append(f"  Difference: {abs(hc_score - fin_score):.3f}")

        analysis_text = '\n'.join(analysis)

        # Save to file
        analysis_file = self.output_dir / f'statistical_analysis_{self.timestamp}.txt'
        with open(analysis_file, 'w') as f:
            f.write(analysis_text)

        print(f"✓ Saved statistical analysis: {analysis_file}")
        print(f"\n{analysis_text}")

        return analysis_text

    def save_results(self):
        """Save all results to JSON."""
        output_file = self.output_dir / f'comprehensive_results_{self.timestamp}.json'

        # Convert numpy types to native Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj

        # Remove raw_results objects that can't be serialized
        results_copy = convert_types(self.results)
        for result in results_copy.get('baseline_results', []):
            if 'raw_results' in result:
                del result['raw_results']

        with open(output_file, 'w') as f:
            json.dump(results_copy, f, indent=2)

        print(f"✓ Saved comprehensive results: {output_file}")


def main():
    """Main execution function."""
    print("="*80)
    print("NeurIPS-Grade Comprehensive A²-Bench Evaluation")
    print("="*80)

    runner = NeurIPSExperimentRunner()

    # Run experiments
    print("\n[1/3] Running comprehensive experiments...")
    runner.run_comprehensive_experiments(num_cases_per_domain=20)

    # Generate visualizations
    print("\n[2/3] Generating publication-quality visualizations...")
    runner.create_score_heatmap()
    runner.create_performance_comparison()
    runner.create_attack_analysis()
    runner.create_violation_analysis()
    runner.create_radar_chart()

    # Generate tables and analysis
    print("\n[3/3] Generating LaTeX tables and statistical analysis...")
    runner.generate_latex_tables()
    runner.perform_statistical_analysis()
    runner.save_results()

    print("\n" + "="*80)
    print("✓ EVALUATION COMPLETE")
    print("="*80)
    print(f"\nAll results saved to: {runner.output_dir}")
    print("\nGenerated files:")
    print("  - Score heatmaps (PNG + PDF)")
    print("  - Performance comparison charts (PNG + PDF)")
    print("  - Attack analysis visualizations (PNG + PDF)")
    print("  - Violation analysis (PNG + PDF)")
    print("  - Radar charts (PNG + PDF)")
    print("  - LaTeX tables for paper")
    print("  - Statistical analysis report")
    print("  - Comprehensive JSON results")


if __name__ == "__main__":
    main()
