"""
Create additional advanced analysis and visualizations.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Publication settings
plt.rcParams.update({
    'figure.figsize': (14, 8),
    'font.size': 14,
    'font.family': 'serif',
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 12,
    'lines.linewidth': 2.5,
    'savefig.dpi': 300
})


class AdvancedAnalyzer:
    """Create advanced analysis visualizations."""

    def __init__(self, results_dir="experiments/results/icml"):
        self.results_dir = Path(results_dir)

        # Load results
        result_files = list(self.results_dir.glob("full_results_*.json"))
        if not result_files:
            raise FileNotFoundError("No results file found")

        with open(result_files[-1], 'r') as f:
            self.results = json.load(f)

        self.per_case_df = pd.DataFrame(self.results['per_case_results'])
        self.aggregate_df = pd.DataFrame(self.results['aggregate_results'])

    def create_test_case_type_analysis(self):
        """Analyze performance by test case type."""

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))

        for idx, domain in enumerate(['healthcare', 'finance']):
            ax = axes[idx]
            domain_data = self.per_case_df[self.per_case_df['domain'] == domain]

            # Group by case type
            type_performance = domain_data.groupby('case_type').agg({
                'a2_score': ['mean', 'std', 'count'],
                'violations': 'sum',
                'completed': 'sum'
            }).reset_index()

            if len(type_performance) > 0:
                case_types = type_performance['case_type'].values
                mean_scores = type_performance['a2_score']['mean'].values
                std_scores = type_performance['a2_score']['std'].values
                counts = type_performance['a2_score']['count'].values

                x = np.arange(len(case_types))

                bars = ax.bar(x, mean_scores, yerr=std_scores,
                             color=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'][:len(x)],
                             alpha=0.8, capsize=5, edgecolor='black', linewidth=1.5)

                ax.set_xlabel('Test Case Type', fontweight='bold', fontsize=16)
                ax.set_ylabel('Mean A² Score', fontweight='bold', fontsize=16)
                ax.set_title(f'{domain.capitalize()}: Performance by Test Type',
                           fontweight='bold', fontsize=18, pad=15)
                ax.set_xticks(x)
                ax.set_xticklabels(case_types, rotation=45, ha='right')
                ax.set_ylim(0, 1.15)
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                ax.axhline(y=1.0, color='green', linestyle=':', linewidth=2, alpha=0.4)

                # Add count labels
                for i, (bar, count) in enumerate(zip(bars, counts)):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.03,
                           f'{height:.3f}\n(n={int(count)})',
                           ha='center', va='bottom', fontsize=10, fontweight='bold')

        plt.suptitle('Performance Analysis by Test Case Category',
                    fontsize=20, fontweight='bold', y=0.98)
        plt.tight_layout()

        output_file = self.results_dir / 'analysis_by_test_type.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

    def create_model_comparison_matrix(self):
        """Create detailed model comparison matrix."""

        fig, axes = plt.subplots(2, 2, figsize=(16, 14))

        models = self.aggregate_df['model_name'].unique()
        metrics = ['safety', 'security', 'reliability', 'compliance']
        metric_names = ['Safety', 'Security', 'Reliability', 'Compliance']

        for idx, (metric, metric_name) in enumerate(zip(metrics, metric_names)):
            ax = axes[idx // 2, idx % 2]

            # Create comparison matrix
            hc_scores = []
            fin_scores = []

            for model in models:
                hc_data = self.aggregate_df[
                    (self.aggregate_df['model_name'] == model) &
                    (self.aggregate_df['domain'] == 'healthcare')
                ]
                fin_data = self.aggregate_df[
                    (self.aggregate_df['model_name'] == model) &
                    (self.aggregate_df['domain'] == 'finance')
                ]

                hc_scores.append(hc_data.iloc[0]['scores'][metric] if not hc_data.empty else 0)
                fin_scores.append(fin_data.iloc[0]['scores'][metric] if not fin_data.empty else 0)

            # Create matrix
            data_matrix = np.array([hc_scores, fin_scores])

            # Plot heatmap
            im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

            ax.set_xticks(np.arange(len(models)))
            ax.set_yticks(np.arange(2))
            ax.set_xticklabels(models, rotation=45, ha='right')
            ax.set_yticklabels(['Healthcare', 'Finance'])

            ax.set_title(f'{metric_name} Score Matrix', fontweight='bold', fontsize=16, pad=10)

            # Add values
            for i in range(2):
                for j in range(len(models)):
                    text = ax.text(j, i, f'{data_matrix[i, j]:.3f}',
                                 ha="center", va="center", color="black",
                                 fontsize=13, fontweight='bold')

            # Colorbar
            cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Score', rotation=270, labelpad=15, fontweight='bold')

        plt.suptitle('Model-Domain Performance Matrix (All Metrics)',
                    fontsize=20, fontweight='bold', y=0.995)
        plt.tight_layout()

        output_file = self.results_dir / 'model_comparison_matrix.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

    def create_statistical_comparison(self):
        """Create statistical comparison plots."""

        fig, axes = plt.subplots(2, 2, figsize=(16, 14))

        # 1. Score distributions
        ax = axes[0, 0]

        hc_scores = self.per_case_df[self.per_case_df['domain'] == 'healthcare']['a2_score']
        fin_scores = self.per_case_df[self.per_case_df['domain'] == 'finance']['a2_score']

        positions = [1, 2]
        bp = ax.boxplot([hc_scores, fin_scores], positions=positions,
                        widths=0.6, patch_artist=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7),
                        medianprops=dict(color='red', linewidth=3))

        colors = ['#2E86AB', '#A23B72']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_xticklabels(['Healthcare', 'Finance'], fontweight='bold')
        ax.set_ylabel('A² Score Distribution', fontweight='bold', fontsize=14)
        ax.set_title('Score Distribution Comparison', fontweight='bold', fontsize=16, pad=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(-0.1, 1.2)

        # Add statistics
        ax.text(1, 1.05, f'μ={hc_scores.mean():.3f}\nσ={hc_scores.std():.3f}',
               ha='center', fontsize=11, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax.text(2, 0.6, f'μ={fin_scores.mean():.3f}\nσ={fin_scores.std():.3f}',
               ha='center', fontsize=11, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # 2. Violation distribution
        ax = axes[0, 1]

        hc_violations = self.per_case_df[self.per_case_df['domain'] == 'healthcare'].groupby('model_name')['violations'].sum()
        fin_violations = self.per_case_df[self.per_case_df['domain'] == 'finance'].groupby('model_name')['violations'].sum()

        models = hc_violations.index
        x = np.arange(len(models))
        width = 0.35

        ax.bar(x - width/2, hc_violations.values, width, label='Healthcare',
              color='#2E86AB', alpha=0.8, edgecolor='black')
        ax.bar(x + width/2, fin_violations.values, width, label='Finance',
              color='#A23B72', alpha=0.8, edgecolor='black')

        ax.set_xlabel('Model', fontweight='bold')
        ax.set_ylabel('Total Violations', fontweight='bold', fontsize=14)
        ax.set_title('Violation Count by Model', fontweight='bold', fontsize=16, pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # 3. Completion rate analysis
        ax = axes[1, 0]

        completion_by_model = self.per_case_df.groupby(['domain', 'model_name'])['completed'].mean() * 100

        hc_completion = completion_by_model['healthcare']
        fin_completion = completion_by_model['finance']

        x = np.arange(len(hc_completion))
        width = 0.35

        ax.bar(x - width/2, hc_completion.values, width, label='Healthcare',
              color='#2E86AB', alpha=0.8, edgecolor='black')
        ax.bar(x + width/2, fin_completion.values, width, label='Finance',
              color='#A23B72', alpha=0.8, edgecolor='black')

        ax.set_xlabel('Model', fontweight='bold')
        ax.set_ylabel('Task Completion Rate (%)', fontweight='bold', fontsize=14)
        ax.set_title('Task Completion Comparison', fontweight='bold', fontsize=16, pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(hc_completion.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, 110)
        ax.axhline(y=100, color='green', linestyle=':', linewidth=2, alpha=0.4)

        # 4. Metric correlation
        ax = axes[1, 1]

        metrics = ['safety', 'security', 'reliability', 'compliance', 'a2_score']
        metric_data = self.per_case_df[metrics].corr()

        im = ax.imshow(metric_data, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)

        ax.set_xticks(np.arange(len(metrics)))
        ax.set_yticks(np.arange(len(metrics)))
        ax.set_xticklabels([m.capitalize() for m in metrics], rotation=45, ha='right')
        ax.set_yticklabels([m.capitalize() for m in metrics])

        ax.set_title('Metric Correlation Matrix', fontweight='bold', fontsize=16, pad=10)

        # Add correlation values
        for i in range(len(metrics)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{metric_data.iloc[i, j]:.2f}',
                             ha="center", va="center",
                             color="white" if abs(metric_data.iloc[i, j]) > 0.5 else "black",
                             fontsize=11, fontweight='bold')

        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Correlation', rotation=270, labelpad=15, fontweight='bold')

        plt.suptitle('Statistical Analysis Dashboard',
                    fontsize=20, fontweight='bold', y=0.995)
        plt.tight_layout()

        output_file = self.results_dir / 'statistical_comparison.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

    def create_error_rate_analysis(self):
        """Analyze error rates and failure modes."""

        fig, axes = plt.subplots(1, 2, figsize=(16, 7))

        # Calculate error rates (1 - success rate)
        for idx, domain in enumerate(['healthcare', 'finance']):
            ax = axes[idx]
            domain_data = self.per_case_df[self.per_case_df['domain'] == domain]

            models = domain_data['model_name'].unique()

            # Calculate failure rates per metric
            metrics = ['safety', 'security', 'reliability', 'compliance']
            metric_labels = ['Safety\nFailures', 'Security\nFailures',
                           'Reliability\nFailures', 'Compliance\nFailures']

            failure_rates = []
            for model in models:
                model_data = domain_data[domain_data['model_name'] == model]
                model_failures = []
                for metric in metrics:
                    # Failure rate = proportion of cases with score < 1.0
                    failures = (model_data[metric] < 1.0).sum() / len(model_data) * 100
                    model_failures.append(failures)
                failure_rates.append(model_failures)

            # Plot stacked bar chart
            x = np.arange(len(models))
            width = 0.6

            bottom = np.zeros(len(models))
            colors = ['#D62828', '#F77F00', '#FCBF49', '#90BE6D']

            for i, (metric_label, color) in enumerate(zip(metric_labels, colors)):
                values = [fr[i] for fr in failure_rates]
                ax.bar(x, values, width, label=metric_label, bottom=bottom,
                      color=color, alpha=0.8, edgecolor='black', linewidth=1)
                bottom += values

            ax.set_xlabel('Model', fontweight='bold', fontsize=16)
            ax.set_ylabel('Failure Rate (%)', fontweight='bold', fontsize=16)
            ax.set_title(f'{domain.capitalize()}: Failure Analysis',
                        fontweight='bold', fontsize=18, pad=15)
            ax.set_xticks(x)
            ax.set_xticklabels(models, rotation=45, ha='right')
            ax.legend(loc='upper right', fontsize=11)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            ax.set_ylim(0, max(bottom) * 1.15 if max(bottom) > 0 else 10)

        plt.suptitle('Failure Mode Analysis Across Metrics',
                    fontsize=20, fontweight='bold', y=0.98)
        plt.tight_layout()

        output_file = self.results_dir / 'error_rate_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

    def create_performance_heatmap(self):
        """Create comprehensive performance heatmap."""

        fig, ax = plt.subplots(figsize=(16, 10))

        # Prepare data: rows are test cases, columns are models
        # Color by A² score

        models = self.per_case_df['model_name'].unique()

        # Get unique case IDs and sort
        healthcare_cases = self.per_case_df[
            self.per_case_df['domain'] == 'healthcare'
        ]['case_id'].unique()
        finance_cases = self.per_case_df[
            self.per_case_df['domain'] == 'finance'
        ]['case_id'].unique()

        all_cases = list(healthcare_cases) + list(finance_cases)

        # Create matrix
        data_matrix = np.zeros((len(all_cases), len(models)))

        for i, case_id in enumerate(all_cases):
            for j, model in enumerate(models):
                case_data = self.per_case_df[
                    (self.per_case_df['case_id'] == case_id) &
                    (self.per_case_df['model_name'] == model)
                ]
                if not case_data.empty:
                    data_matrix[i, j] = case_data.iloc[0]['a2_score']

        # Plot heatmap
        im = ax.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

        ax.set_xticks(np.arange(len(models)))
        ax.set_xticklabels(models, rotation=45, ha='right', fontsize=12)

        # Add domain separators
        ax.axhline(y=len(healthcare_cases) - 0.5, color='black', linewidth=3)

        # Labels
        ax.set_xlabel('Model Configuration', fontweight='bold', fontsize=16)
        ax.set_ylabel('Test Case ID', fontweight='bold', fontsize=16)
        ax.set_title('Complete Performance Heatmap: All 67 Test Cases × 4 Models',
                    fontweight='bold', fontsize=18, pad=20)

        # Add domain annotations
        ax.text(-0.5, len(healthcare_cases)/2, 'Healthcare\n(31 cases)',
               rotation=90, va='center', ha='right', fontsize=13,
               fontweight='bold', bbox=dict(boxstyle='round', facecolor='#2E86AB', alpha=0.3))
        ax.text(-0.5, len(healthcare_cases) + len(finance_cases)/2, 'Finance\n(36 cases)',
               rotation=90, va='center', ha='right', fontsize=13,
               fontweight='bold', bbox=dict(boxstyle='round', facecolor='#A23B72', alpha=0.3))

        # Colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
        cbar.set_label('A² Score', rotation=270, labelpad=25, fontweight='bold', fontsize=14)

        plt.tight_layout()

        output_file = self.results_dir / 'complete_performance_heatmap.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created: {output_file.name}")
        plt.close()

    def generate_summary_statistics(self):
        """Generate detailed summary statistics."""

        output = []
        output.append("="*80)
        output.append("DETAILED STATISTICAL SUMMARY - ALL 67 TEST CASES")
        output.append("="*80)

        # Overall statistics
        output.append("\n1. OVERALL PERFORMANCE")
        output.append("-"*80)

        for domain in ['healthcare', 'finance']:
            domain_data = self.per_case_df[self.per_case_df['domain'] == domain]

            output.append(f"\n{domain.upper()}:")
            output.append(f"  Test Cases: {len(domain_data['case_id'].unique())}")
            output.append(f"  Mean A² Score: {domain_data['a2_score'].mean():.3f} ± {domain_data['a2_score'].std():.3f}")
            output.append(f"  Min A² Score: {domain_data['a2_score'].min():.3f}")
            output.append(f"  Max A² Score: {domain_data['a2_score'].max():.3f}")
            output.append(f"  Total Violations: {domain_data['violations'].sum()}")
            output.append(f"  Completion Rate: {domain_data['completed'].mean()*100:.1f}%")

        # Per-model statistics
        output.append("\n2. PER-MODEL PERFORMANCE")
        output.append("-"*80)

        for model in self.per_case_df['model_name'].unique():
            model_data = self.per_case_df[self.per_case_df['model_name'] == model]
            output.append(f"\n{model}:")
            output.append(f"  Overall A² Score: {model_data['a2_score'].mean():.3f}")
            output.append(f"  Healthcare: {model_data[model_data['domain']=='healthcare']['a2_score'].mean():.3f}")
            output.append(f"  Finance: {model_data[model_data['domain']=='finance']['a2_score'].mean():.3f}")

        # Statistical tests
        output.append("\n3. STATISTICAL TESTS")
        output.append("-"*80)

        hc_scores = self.per_case_df[self.per_case_df['domain'] == 'healthcare']['a2_score']
        fin_scores = self.per_case_df[self.per_case_df['domain'] == 'finance']['a2_score']

        # T-test
        t_stat, p_value = stats.ttest_ind(hc_scores, fin_scores)
        output.append(f"\nT-test (Healthcare vs Finance):")
        output.append(f"  t-statistic: {t_stat:.3f}")
        output.append(f"  p-value: {p_value:.6f}")
        output.append(f"  Significant: {'Yes' if p_value < 0.05 else 'No'} (α=0.05)")

        # Effect size (Cohen's d)
        pooled_std = np.sqrt(((len(hc_scores)-1)*hc_scores.std()**2 +
                             (len(fin_scores)-1)*fin_scores.std()**2) /
                            (len(hc_scores) + len(fin_scores) - 2))
        cohens_d = (hc_scores.mean() - fin_scores.mean()) / pooled_std if pooled_std > 0 else 0
        output.append(f"\nEffect Size (Cohen's d): {cohens_d:.3f}")
        output.append(f"  Interpretation: {'Large' if abs(cohens_d) > 0.8 else 'Medium' if abs(cohens_d) > 0.5 else 'Small'}")

        # Save to file
        summary_text = '\n'.join(output)
        summary_file = self.results_dir / 'detailed_statistics.txt'
        with open(summary_file, 'w') as f:
            f.write(summary_text)

        print(f"✓ Created: {summary_file.name}")
        print(summary_text)

    def run_all(self):
        """Run all additional analyses."""
        print("\n" + "="*80)
        print("Creating Additional Advanced Visualizations")
        print("="*80)

        self.create_test_case_type_analysis()
        self.create_model_comparison_matrix()
        self.create_statistical_comparison()
        self.create_error_rate_analysis()
        self.create_performance_heatmap()
        self.generate_summary_statistics()

        print("\n" + "="*80)
        print("✓ All Additional Visualizations Created")
        print("="*80)


if __name__ == "__main__":
    analyzer = AdvancedAnalyzer()
    analyzer.run_all()
