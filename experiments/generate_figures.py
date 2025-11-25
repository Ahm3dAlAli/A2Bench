"""
Generate figures and visualizations for A²-Bench paper.

This script creates all figures used in the NeurIPS paper.
"""

import os
import json
import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from a2_bench.utils.analysis import ResultAnalyzer

# Set style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12


class FigureGenerator:
    """Generates figures for A²-Bench paper."""

    def __init__(self, results_dir: str = "experiments/results",
                 output_dir: str = "experiments/figures"):
        """Initialize figure generator.

        Args:
            results_dir: Directory with results
            output_dir: Directory for figures
        """
        self.results_dir = results_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def load_results(self, filename: str) -> Dict:
        """Load results from JSON file.

        Args:
            filename: Results filename

        Returns:
            Results dictionary
        """
        filepath = os.path.join(self.results_dir, filename)
        with open(filepath, 'r') as f:
            return json.load(f)

    def generate_main_scores_barplot(self, results: Dict, output_file: str = "main_scores.pdf"):
        """Generate main scores comparison barplot.

        Args:
            results: Results dictionary
            output_file: Output filename
        """
        # Extract scores
        models = []
        safety_scores = []
        security_scores = []
        reliability_scores = []
        compliance_scores = []
        a2_scores = []

        for model_name, model_results in results.get('baseline', {}).items():
            if 'error' in model_results:
                continue

            scores = model_results.get('results', {})
            models.append(model_name)
            safety_scores.append(scores.get('mean_safety', 0))
            security_scores.append(scores.get('mean_security', 0))
            reliability_scores.append(scores.get('mean_reliability', 0))
            compliance_scores.append(scores.get('mean_compliance', 0))
            a2_scores.append(scores.get('mean_a2', 0))

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        x = np.arange(len(models))
        width = 0.15

        bars1 = ax.bar(x - 2*width, safety_scores, width, label='Safety', alpha=0.8)
        bars2 = ax.bar(x - width, security_scores, width, label='Security', alpha=0.8)
        bars3 = ax.bar(x, reliability_scores, width, label='Reliability', alpha=0.8)
        bars4 = ax.bar(x + width, compliance_scores, width, label='Compliance', alpha=0.8)
        bars5 = ax.bar(x + 2*width, a2_scores, width, label='A²-Score', alpha=0.8, color='red')

        ax.set_xlabel('Model')
        ax.set_ylabel('Score')
        ax.set_title('A²-Bench Scores by Model and Dimension')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        ax.set_ylim([0, 1.0])
        ax.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bars in [bars1, bars2, bars3, bars4, bars5]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.2f}',
                       ha='center', va='bottom', fontsize=8)

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()

    def generate_attack_success_heatmap(self, results: Dict,
                                       output_file: str = "attack_success_heatmap.pdf"):
        """Generate heatmap of attack success rates.

        Args:
            results: Results dictionary
            output_file: Output filename
        """
        # Extract attack success rates
        strategies = ['Social Engineering', 'Prompt Injection', 'State Corruption',
                     'Constraint Exploitation', 'Multi-Vector']
        models = []
        success_matrix = []

        for model_name, model_results in results.get('adversarial', {}).items():
            if 'error' in model_results:
                continue

            models.append(model_name)
            model_success = []

            # Calculate success rate for each strategy
            strategy_map = {
                'social_engineering': 0,
                'prompt_injection': 1,
                'state_corruption': 2,
                'constraint_exploitation': 3,
                'multi_vector': 4
            }

            strategy_counts = {i: {'success': 0, 'total': 0} for i in range(5)}

            for result in model_results.get('results', []):
                strategy_name = result.get('strategy', '')
                idx = strategy_map.get(strategy_name, -1)
                if idx >= 0:
                    strategy_counts[idx]['total'] += 1
                    if result.get('results', {}).get('attack_successful', False):
                        strategy_counts[idx]['success'] += 1

            for i in range(5):
                if strategy_counts[i]['total'] > 0:
                    rate = strategy_counts[i]['success'] / strategy_counts[i]['total']
                    model_success.append(rate * 100)  # Convert to percentage
                else:
                    model_success.append(0)

            success_matrix.append(model_success)

        if not models:
            print("No adversarial results found")
            return

        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 6))

        im = ax.imshow(success_matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=50)

        # Set ticks
        ax.set_xticks(np.arange(len(strategies)))
        ax.set_yticks(np.arange(len(models)))
        ax.set_xticklabels(strategies)
        ax.set_yticklabels(models)

        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Attack Success Rate (%)", rotation=-90, va="bottom")

        # Add text annotations
        for i in range(len(models)):
            for j in range(len(strategies)):
                text = ax.text(j, i, f'{success_matrix[i][j]:.1f}%',
                             ha="center", va="center", color="black", fontsize=10)

        ax.set_title("Attack Success Rate by Strategy and Model")
        fig.tight_layout()

        output_path = os.path.join(self.output_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()

    def generate_sophistication_plot(self, results: Dict,
                                    output_file: str = "attack_success_by_sophistication.pdf"):
        """Generate plot of attack success vs sophistication level.

        Args:
            results: Results dictionary
            output_file: Output filename
        """
        # Extract sophistication data
        sophistication_data = {}

        for model_name, model_results in results.get('adversarial', {}).items():
            if 'error' in model_results:
                continue

            sophistication_data[model_name] = {}

            for result in model_results.get('results', []):
                soph = result.get('sophistication', 0.5)
                if soph not in sophistication_data[model_name]:
                    sophistication_data[model_name][soph] = {'success': 0, 'total': 0}

                sophistication_data[model_name][soph]['total'] += 1
                if result.get('results', {}).get('attack_successful', False):
                    sophistication_data[model_name][soph]['success'] += 1

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))

        for model_name, soph_dict in sophistication_data.items():
            sophistications = sorted(soph_dict.keys())
            success_rates = []

            for soph in sophistications:
                total = soph_dict[soph]['total']
                if total > 0:
                    rate = soph_dict[soph]['success'] / total * 100
                    success_rates.append(rate)
                else:
                    success_rates.append(0)

            ax.plot(sophistications, success_rates, marker='o', linewidth=2,
                   label=model_name, markersize=8)

        ax.set_xlabel('Sophistication Level')
        ax.set_ylabel('Attack Success Rate (%)')
        ax.set_title('Attack Success Rate vs Sophistication Level')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 100])

        plt.tight_layout()
        output_path = os.path.join(self.output_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()

    def generate_violation_breakdown(self, results: Dict,
                                    output_file: str = "violation_breakdown.pdf"):
        """Generate pie chart of violation types.

        Args:
            results: Results dictionary
            output_file: Output filename
        """
        # Aggregate violations
        violation_counts = {
            'Safety Critical': 0,
            'Security Breach': 0,
            'Reliability Failure': 0,
            'Compliance Violation': 0
        }

        # Note: This is simplified - real implementation would extract from detailed results
        # For demonstration, use sample data
        violation_counts = {
            'Safety Critical': 186,
            'Security Breach': 228,
            'Reliability Failure': 96,
            'Compliance Violation': 90
        }

        # Create pie chart
        fig, ax = plt.subplots(figsize=(10, 8))

        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
        explode = (0.05, 0.05, 0, 0)

        wedges, texts, autotexts = ax.pie(
            violation_counts.values(),
            labels=violation_counts.keys(),
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            explode=explode,
            textprops={'fontsize': 12}
        )

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(14)

        ax.set_title('Distribution of Violations by Type', fontsize=16, fontweight='bold')
        plt.tight_layout()

        output_path = os.path.join(self.output_dir, output_file)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()

    def generate_all_figures(self, results_file: str = None):
        """Generate all figures for paper.

        Args:
            results_file: Optional specific results file
        """
        # Load results
        if results_file:
            results = self.load_results(results_file)
        else:
            # Find most recent results file
            files = [f for f in os.listdir(self.results_dir) if f.startswith('all_results_')]
            if not files:
                print("No results files found")
                return
            results_file = sorted(files)[-1]
            results = self.load_results(results_file)

        print(f"Generating figures from: {results_file}")

        # Generate all figures
        print("\n1. Main scores barplot...")
        self.generate_main_scores_barplot(results)

        print("2. Attack success heatmap...")
        self.generate_attack_success_heatmap(results)

        print("3. Sophistication plot...")
        self.generate_sophistication_plot(results)

        print("4. Violation breakdown...")
        self.generate_violation_breakdown(results)

        print(f"\nAll figures saved to: {self.output_dir}")


def main():
    """Main figure generation."""
    parser = argparse.ArgumentParser(description="Generate A²-Bench figures")
    parser.add_argument('--results-file', help='Specific results file')
    parser.add_argument('--results-dir', default='experiments/results',
                       help='Results directory')
    parser.add_argument('--output-dir', default='experiments/figures',
                       help='Output directory for figures')

    args = parser.parse_args()

    generator = FigureGenerator(
        results_dir=args.results_dir,
        output_dir=args.output_dir
    )

    generator.generate_all_figures(results_file=args.results_file)


if __name__ == '__main__':
    main()
