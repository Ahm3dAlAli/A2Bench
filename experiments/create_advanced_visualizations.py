"""
Create advanced NeurIPS-grade visualizations and analysis.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches

# Set publication-quality defaults
plt.rcParams.update({
    'figure.figsize': (10, 6),
    'font.size': 11,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'text.usetex': False,
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': False
})


class AdvancedVisualizationCreator:
    """Create advanced visualizations for NeurIPS paper."""

    def __init__(self, results_dir: str = "experiments/results/neurips"):
        self.results_dir = Path(results_dir)

        # Find the most recent results file
        result_files = list(self.results_dir.glob("comprehensive_results_*.json"))
        if not result_files:
            raise FileNotFoundError("No results file found")

        self.results_file = sorted(result_files)[-1]

        with open(self.results_file, 'r') as f:
            self.results = json.load(f)

        self.baseline_df = pd.DataFrame(self.results['baseline_results'])
        self.adv_df = pd.DataFrame(self.results['adversarial_results'])

    def create_metric_breakdown_chart(self):
        """Create detailed breakdown of all metrics by domain and model."""

        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        metrics = [
            ('safety', 'Safety', '#2ecc71'),
            ('security', 'Security', '#3498db'),
            ('reliability', 'Reliability', '#9b59b6'),
            ('compliance', 'Compliance', '#e74c3c')
        ]

        domains = ['healthcare', 'finance']
        domain_names = {'healthcare': 'Healthcare', 'finance': 'Finance'}

        for idx, (metric_key, metric_name, color) in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]

            # Prepare data for grouped bar chart
            models_hc = []
            models_fin = []
            scores_hc = []
            scores_fin = []

            for domain in domains:
                domain_data = self.baseline_df[self.baseline_df['domain'] == domain]
                for _, row in domain_data.iterrows():
                    score = row['scores'][metric_key]
                    model_name = row['model_name']

                    if domain == 'healthcare':
                        models_hc.append(model_name)
                        scores_hc.append(score)
                    else:
                        models_fin.append(model_name)
                        scores_fin.append(score)

            x = np.arange(len(models_hc))
            width = 0.35

            bars1 = ax.bar(x - width/2, scores_hc, width, label='Healthcare',
                          color=color, alpha=0.8, edgecolor='black', linewidth=1)
            bars2 = ax.bar(x + width/2, scores_fin, width, label='Finance',
                          color=color, alpha=0.5, edgecolor='black', linewidth=1)

            ax.set_ylabel(f'{metric_name} Score', fontweight='bold')
            ax.set_title(f'{metric_name} Performance Across Domains',
                        fontweight='bold', fontsize=13)
            ax.set_xticks(x)
            ax.set_xticklabels(models_hc, rotation=45, ha='right')
            ax.set_ylim(0, 1.15)
            ax.legend(loc='upper right', framealpha=0.9)
            ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)

            # Add value labels
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                           f'{height:.2f}',
                           ha='center', va='bottom', fontsize=8, fontweight='bold')

        plt.tight_layout()
        output_file = self.results_dir / 'metric_breakdown_detailed.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created metric breakdown: {output_file}")
        plt.close()

    def create_score_distribution_plot(self):
        """Create box plots showing score distributions."""

        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        metrics_to_plot = ['safety', 'security', 'reliability', 'compliance', 'a2_score']
        metric_labels = ['Safety', 'Security', 'Reliability', 'Compliance', 'A² Score']

        for idx, domain in enumerate(['healthcare', 'finance']):
            domain_data = self.baseline_df[self.baseline_df['domain'] == domain]

            # Prepare data for box plot
            data_to_plot = []
            for metric in metrics_to_plot:
                scores = [row['scores'][metric] for _, row in domain_data.iterrows()]
                data_to_plot.append(scores)

            # Create box plot
            bp = axes[idx].boxplot(data_to_plot, labels=metric_labels,
                                  patch_artist=True, widths=0.6,
                                  boxprops=dict(facecolor='lightblue', alpha=0.7),
                                  medianprops=dict(color='red', linewidth=2),
                                  whiskerprops=dict(linewidth=1.5),
                                  capprops=dict(linewidth=1.5))

            # Color the boxes
            colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12']
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)

            domain_name = domain.capitalize()
            axes[idx].set_title(f'{domain_name} Domain - Score Distribution',
                              fontweight='bold', fontsize=14)
            axes[idx].set_ylabel('Score', fontweight='bold')
            axes[idx].set_ylim(-0.1, 1.2)
            axes[idx].grid(axis='y', alpha=0.3, linestyle='--')
            axes[idx].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        output_file = self.results_dir / 'score_distributions.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created score distributions: {output_file}")
        plt.close()

    def create_comparative_analysis_chart(self):
        """Create comprehensive comparative analysis chart."""

        fig = plt.figure(figsize=(18, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Main heatmap (top-left, spanning 2x2)
        ax_main = fig.add_subplot(gs[0:2, 0:2])

        # Create comprehensive score matrix
        models = self.baseline_df['model_name'].unique()
        domains = ['healthcare', 'finance']

        # Prepare data: rows are models, columns are domain+metric combinations
        columns = []
        for domain in domains:
            for metric in ['Safety', 'Security', 'Reliability', 'Compliance']:
                columns.append(f'{domain.capitalize()}\n{metric}')

        data_matrix = []
        model_labels = []

        for model in models:
            row_data = []
            for domain in ['healthcare', 'finance']:
                model_data = self.baseline_df[
                    (self.baseline_df['model_name'] == model) &
                    (self.baseline_df['domain'] == domain)
                ]
                if not model_data.empty:
                    scores = model_data.iloc[0]['scores']
                    row_data.extend([
                        scores['safety'],
                        scores['security'],
                        scores['reliability'],
                        scores['compliance']
                    ])
                else:
                    row_data.extend([0, 0, 0, 0])

            data_matrix.append(row_data)
            model_labels.append(model)

        # Create heatmap
        im = ax_main.imshow(data_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

        # Set ticks and labels
        ax_main.set_xticks(np.arange(len(columns)))
        ax_main.set_yticks(np.arange(len(model_labels)))
        ax_main.set_xticklabels(columns, fontsize=9)
        ax_main.set_yticklabels(model_labels, fontsize=10)

        # Rotate x labels
        plt.setp(ax_main.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Add values to cells
        for i in range(len(model_labels)):
            for j in range(len(columns)):
                text = ax_main.text(j, i, f'{data_matrix[i][j]:.2f}',
                                   ha="center", va="center", color="black",
                                   fontsize=8, fontweight='bold')

        ax_main.set_title('Comprehensive Performance Matrix', fontweight='bold', fontsize=14, pad=10)

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax_main, fraction=0.046, pad=0.04)
        cbar.set_label('Score', rotation=270, labelpad=15, fontweight='bold')

        # Top-right: Overall A² scores comparison
        ax_top_right = fig.add_subplot(gs[0, 2])

        hc_scores = []
        fin_scores = []
        for model in models:
            hc_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'healthcare')
            ]
            fin_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'finance')
            ]

            if not hc_data.empty:
                hc_scores.append(hc_data.iloc[0]['scores']['a2_score'])
            if not fin_data.empty:
                fin_scores.append(fin_data.iloc[0]['scores']['a2_score'])

        x = np.arange(len(models))
        width = 0.35

        ax_top_right.bar(x - width/2, hc_scores, width, label='Healthcare', color='#2ecc71', alpha=0.8)
        ax_top_right.bar(x + width/2, fin_scores, width, label='Finance', color='#e74c3c', alpha=0.8)

        ax_top_right.set_ylabel('A² Score', fontweight='bold', fontsize=10)
        ax_top_right.set_title('Overall A² Scores', fontweight='bold', fontsize=11)
        ax_top_right.set_xticks(x)
        ax_top_right.set_xticklabels([m.split()[0] for m in models], fontsize=8)
        ax_top_right.legend(fontsize=8)
        ax_top_right.set_ylim(0, 1.2)
        ax_top_right.grid(axis='y', alpha=0.3, linestyle='--')

        # Middle-right: Violations comparison
        ax_mid_right = fig.add_subplot(gs[1, 2])

        total_viol = []
        critical_viol = []
        for model in models:
            model_data = self.baseline_df[self.baseline_df['model_name'] == model]
            total_viol.append(model_data['violations'].apply(lambda x: x['total']).sum())
            critical_viol.append(model_data['violations'].apply(lambda x: x['critical']).sum())

        x = np.arange(len(models))
        width = 0.35

        ax_mid_right.bar(x - width/2, total_viol, width, label='Total', color='#ff7f0e', alpha=0.8)
        ax_mid_right.bar(x + width/2, critical_viol, width, label='Critical', color='#d62728', alpha=0.8)

        ax_mid_right.set_ylabel('Violations', fontweight='bold', fontsize=10)
        ax_mid_right.set_title('Safety Violations', fontweight='bold', fontsize=11)
        ax_mid_right.set_xticks(x)
        ax_mid_right.set_xticklabels([m.split()[0] for m in models], fontsize=8)
        ax_mid_right.legend(fontsize=8)
        ax_mid_right.grid(axis='y', alpha=0.3, linestyle='--')

        # Bottom: Task completion rates
        ax_bottom = fig.add_subplot(gs[2, :])

        completion_data = []
        labels = []
        colors_list = []

        for model in models:
            for domain in ['healthcare', 'finance']:
                model_data = self.baseline_df[
                    (self.baseline_df['model_name'] == model) &
                    (self.baseline_df['domain'] == domain)
                ]
                if not model_data.empty:
                    completion_rate = model_data.iloc[0]['task_completion_rate']
                    completion_data.append(completion_rate * 100)
                    labels.append(f"{model.split()[0]}\n{domain.capitalize()}")
                    colors_list.append('#2ecc71' if domain == 'healthcare' else '#e74c3c')

        bars = ax_bottom.bar(range(len(completion_data)), completion_data, color=colors_list, alpha=0.7, edgecolor='black')

        ax_bottom.set_ylabel('Completion Rate (%)', fontweight='bold', fontsize=11)
        ax_bottom.set_title('Task Completion Rates by Model and Domain', fontweight='bold', fontsize=12)
        ax_bottom.set_xticks(range(len(labels)))
        ax_bottom.set_xticklabels(labels, fontsize=8, rotation=45, ha='right')
        ax_bottom.set_ylim(0, 110)
        ax_bottom.grid(axis='y', alpha=0.3, linestyle='--')
        ax_bottom.axhline(y=100, color='green', linestyle='--', linewidth=1, alpha=0.5)

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax_bottom.text(bar.get_x() + bar.get_width()/2., height + 2,
                         f'{height:.0f}%',
                         ha='center', va='bottom', fontsize=7, fontweight='bold')

        output_file = self.results_dir / 'comprehensive_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created comprehensive analysis: {output_file}")
        plt.close()

    def create_domain_comparison_scatter(self):
        """Create scatter plot comparing healthcare vs finance performance."""

        fig, ax = plt.subplots(figsize=(10, 10))

        models = self.baseline_df['model_name'].unique()
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        markers = ['o', 's', '^', 'D']

        for idx, model in enumerate(models):
            hc_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'healthcare')
            ]
            fin_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'finance')
            ]

            if not hc_data.empty and not fin_data.empty:
                hc_score = hc_data.iloc[0]['scores']['a2_score']
                fin_score = fin_data.iloc[0]['scores']['a2_score']

                ax.scatter(hc_score, fin_score, s=300, c=[colors[idx]],
                          marker=markers[idx], alpha=0.7, edgecolors='black',
                          linewidths=2, label=model, zorder=3)

                # Add model name annotation
                ax.annotate(model.split()[0], (hc_score, fin_score),
                          xytext=(10, 10), textcoords='offset points',
                          fontsize=10, fontweight='bold',
                          bbox=dict(boxstyle='round,pad=0.3', facecolor=colors[idx], alpha=0.3))

        # Add diagonal line (perfect correlation)
        ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, linewidth=2, label='Perfect Correlation', zorder=1)

        # Add grid
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

        ax.set_xlabel('Healthcare Domain A² Score', fontweight='bold', fontsize=13)
        ax.set_ylabel('Finance Domain A² Score', fontweight='bold', fontsize=13)
        ax.set_title('Cross-Domain Performance Comparison', fontweight='bold', fontsize=15, pad=15)
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.legend(loc='lower right', fontsize=11, framealpha=0.9)
        ax.set_aspect('equal')

        # Add performance quadrants
        ax.axhline(y=0.75, color='gray', linestyle=':', alpha=0.3, linewidth=1)
        ax.axvline(x=0.75, color='gray', linestyle=':', alpha=0.3, linewidth=1)

        # Add quadrant labels
        ax.text(0.87, 0.87, 'High-High', fontsize=9, alpha=0.5, ha='center')
        ax.text(0.87, 0.13, 'High HC\nLow Fin', fontsize=9, alpha=0.5, ha='center')
        ax.text(0.13, 0.87, 'Low HC\nHigh Fin', fontsize=9, alpha=0.5, ha='center')
        ax.text(0.13, 0.13, 'Low-Low', fontsize=9, alpha=0.5, ha='center')

        output_file = self.results_dir / 'domain_comparison_scatter.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created domain comparison scatter: {output_file}")
        plt.close()

    def create_summary_dashboard(self):
        """Create a single summary dashboard with key metrics."""

        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 4, hspace=0.35, wspace=0.3)

        # Title
        fig.suptitle('A²-Bench Comprehensive Evaluation Dashboard',
                    fontsize=20, fontweight='bold', y=0.98)

        models = self.baseline_df['model_name'].unique()

        # 1. Overall Performance (top-left, spanning 2 columns)
        ax1 = fig.add_subplot(gs[0, 0:2])

        x = np.arange(len(models))
        width = 0.25

        hc_safety = []
        hc_a2 = []
        fin_safety = []
        fin_a2 = []

        for model in models:
            hc_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'healthcare')
            ]
            fin_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'finance')
            ]

            if not hc_data.empty:
                hc_safety.append(hc_data.iloc[0]['scores']['safety'])
                hc_a2.append(hc_data.iloc[0]['scores']['a2_score'])
            if not fin_data.empty:
                fin_safety.append(fin_data.iloc[0]['scores']['safety'])
                fin_a2.append(fin_data.iloc[0]['scores']['a2_score'])

        ax1.bar(x - 1.5*width, hc_safety, width, label='HC Safety', color='#2ecc71', alpha=0.8)
        ax1.bar(x - 0.5*width, hc_a2, width, label='HC A²', color='#27ae60', alpha=0.8)
        ax1.bar(x + 0.5*width, fin_safety, width, label='Fin Safety', color='#e74c3c', alpha=0.8)
        ax1.bar(x + 1.5*width, fin_a2, width, label='Fin A²', color='#c0392b', alpha=0.8)

        ax1.set_ylabel('Score', fontweight='bold')
        ax1.set_title('Overall Performance Summary', fontweight='bold', fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels([m.split()[0] for m in models])
        ax1.legend(loc='lower right', ncol=2, fontsize=9)
        ax1.set_ylim(0, 1.2)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')

        # 2. Metric Breakdown Healthcare (top-right)
        ax2 = fig.add_subplot(gs[0, 2:])

        hc_data = self.baseline_df[self.baseline_df['domain'] == 'healthcare']
        metrics = ['safety', 'security', 'reliability', 'compliance']
        metric_labels = ['Safety', 'Security', 'Reliability', 'Compliance']

        bottom = np.zeros(len(models))
        colors_stack = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']

        for metric, label, color in zip(metrics, metric_labels, colors_stack):
            values = [hc_data[hc_data['model_name'] == model].iloc[0]['scores'][metric]
                     for model in models]
            ax2.bar([m.split()[0] for m in models], values, 0.6, label=label,
                   bottom=bottom, color=color, alpha=0.8)
            bottom += values

        ax2.set_ylabel('Cumulative Score', fontweight='bold')
        ax2.set_title('Healthcare Metrics Breakdown', fontweight='bold', fontsize=13)
        ax2.legend(loc='upper right', fontsize=9)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')

        # 3. Metric Breakdown Finance (middle-left)
        ax3 = fig.add_subplot(gs[1, 0:2])

        fin_data = self.baseline_df[self.baseline_df['domain'] == 'finance']

        bottom = np.zeros(len(models))
        for metric, label, color in zip(metrics, metric_labels, colors_stack):
            values = [fin_data[fin_data['model_name'] == model].iloc[0]['scores'][metric]
                     for model in models]
            ax3.bar([m.split()[0] for m in models], values, 0.6, label=label,
                   bottom=bottom, color=color, alpha=0.8)
            bottom += values

        ax3.set_ylabel('Cumulative Score', fontweight='bold')
        ax3.set_title('Finance Metrics Breakdown', fontweight='bold', fontsize=13)
        ax3.legend(loc='upper right', fontsize=9)
        ax3.grid(axis='y', alpha=0.3, linestyle='--')

        # 4. Violations Heatmap (middle-right)
        ax4 = fig.add_subplot(gs[1, 2:])

        viol_matrix = []
        for model in models:
            row = []
            for domain in ['healthcare', 'finance']:
                data = self.baseline_df[
                    (self.baseline_df['model_name'] == model) &
                    (self.baseline_df['domain'] == domain)
                ]
                if not data.empty:
                    row.append(data.iloc[0]['violations']['total'])
                else:
                    row.append(0)
            viol_matrix.append(row)

        im = ax4.imshow(viol_matrix, cmap='Reds', aspect='auto')
        ax4.set_xticks([0, 1])
        ax4.set_xticklabels(['Healthcare', 'Finance'])
        ax4.set_yticks(range(len(models)))
        ax4.set_yticklabels([m.split()[0] for m in models])
        ax4.set_title('Total Violations', fontweight='bold', fontsize=13)

        for i in range(len(models)):
            for j in range(2):
                text = ax4.text(j, i, int(viol_matrix[i][j]),
                               ha="center", va="center", color="black", fontweight='bold')

        plt.colorbar(im, ax=ax4, fraction=0.046, pad=0.04)

        # 5-6-7-8. Individual model radar charts (bottom row)
        categories = ['Safety', 'Security', 'Reliability', 'Compliance']
        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]

        for idx, model in enumerate(models[:4]):  # Max 4 models
            ax = fig.add_subplot(gs[2, idx], projection='polar')

            # Healthcare data
            hc_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'healthcare')
            ]
            if not hc_data.empty:
                hc_values = [
                    hc_data.iloc[0]['scores']['safety'],
                    hc_data.iloc[0]['scores']['security'],
                    hc_data.iloc[0]['scores']['reliability'],
                    hc_data.iloc[0]['scores']['compliance']
                ]
                hc_values += hc_values[:1]
                ax.plot(angles, hc_values, 'o-', linewidth=2, label='Healthcare', color='#2ecc71')
                ax.fill(angles, hc_values, alpha=0.2, color='#2ecc71')

            # Finance data
            fin_data = self.baseline_df[
                (self.baseline_df['model_name'] == model) &
                (self.baseline_df['domain'] == 'finance')
            ]
            if not fin_data.empty:
                fin_values = [
                    fin_data.iloc[0]['scores']['safety'],
                    fin_data.iloc[0]['scores']['security'],
                    fin_data.iloc[0]['scores']['reliability'],
                    fin_data.iloc[0]['scores']['compliance']
                ]
                fin_values += fin_values[:1]
                ax.plot(angles, fin_values, 'o-', linewidth=2, label='Finance', color='#e74c3c')
                ax.fill(angles, fin_values, alpha=0.2, color='#e74c3c')

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=8)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.25, 0.5, 0.75, 1.0])
            ax.set_yticklabels(['0.25', '0.5', '0.75', '1.0'], fontsize=7)
            ax.set_title(model.split()[0], fontweight='bold', fontsize=11, pad=10)
            ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1), fontsize=7)
            ax.grid(True, linewidth=0.5)

        output_file = self.results_dir / 'summary_dashboard.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.savefig(output_file.with_suffix('.pdf'), bbox_inches='tight')
        print(f"✓ Created summary dashboard: {output_file}")
        plt.close()

    def generate_all_visualizations(self):
        """Generate all advanced visualizations."""
        print("\n" + "="*80)
        print("Creating Advanced NeurIPS-Grade Visualizations")
        print("="*80)

        self.create_metric_breakdown_chart()
        self.create_score_distribution_plot()
        self.create_comparative_analysis_chart()
        self.create_domain_comparison_scatter()
        self.create_summary_dashboard()

        print("\n" + "="*80)
        print("✓ All Advanced Visualizations Created")
        print("="*80)


if __name__ == "__main__":
    creator = AdvancedVisualizationCreator()
    creator.generate_all_visualizations()
