#!/usr/bin/env python3
"""
Create advanced publication-quality visualizations for A2Bench results.
Includes heatmaps, radar charts, violin plots, and correlation matrices.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Circle
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, str(Path(__file__).parent.parent))

# Publication settings
plt.rcParams.update({
    'figure.figsize': (12, 8),
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


def load_latest_results():
    """Load the most recent evaluation results."""
    results_dir = Path("experiments/results/icml")
    result_files = sorted(results_dir.glob("full_results_*.json"))

    if not result_files:
        raise FileNotFoundError("No result files found")

    latest_file = result_files[-1]
    print(f"Loading results from: {latest_file.name}")

    with open(latest_file, 'r') as f:
        return json.load(f)


def create_performance_heatmap(results, output_dir):
    """Create performance heatmap across models and metrics."""

    print("\n[1/8] Creating performance heatmap...")

    agg_results = results['aggregate_results']

    # Prepare data for heatmap
    metrics = ['safety', 'security', 'reliability', 'compliance', 'a2_score']
    models = sorted(set([r['model_name'] for r in agg_results]))
    domains = sorted(set([r['domain'] for r in agg_results]))

    # Create combined model-domain labels
    labels = []
    data = []

    for domain in domains:
        for model in models:
            label = f"{model}\n({domain.capitalize()})"
            labels.append(label)

            # Find matching result
            result = next((r for r in agg_results
                          if r['model_name'] == model and r['domain'] == domain), None)

            if result:
                scores = [result['scores'][m] for m in metrics]
                data.append(scores)
            else:
                data.append([0] * len(metrics))

    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 10))

    heatmap_data = np.array(data)
    im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    # Set ticks
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(['Safety', 'Security', 'Reliability', 'Compliance', 'A²-Score'])
    ax.set_yticklabels(labels)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add values
    for i in range(len(labels)):
        for j in range(len(metrics)):
            text = ax.text(j, i, f'{heatmap_data[i, j]:.3f}',
                          ha="center", va="center", color="black" if heatmap_data[i, j] > 0.5 else "white",
                          fontsize=11, weight='bold')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Score', rotation=270, labelpad=20)

    ax.set_title('A²-Bench Performance Heatmap: Models × Domains × Metrics',
                 fontsize=18, weight='bold', pad=20)

    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"heatmap_performance_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_radar_charts(results, output_dir):
    """Create radar charts for model comparison."""

    print("\n[2/8] Creating radar charts...")

    agg_results = results['aggregate_results']
    metrics = ['Safety', 'Security', 'Reliability', 'Compliance']
    metric_keys = ['safety', 'security', 'reliability', 'compliance']

    models = sorted(set([r['model_name'] for r in agg_results]))

    # Create subplot for each domain
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(projection='polar'))

    domains = ['healthcare', 'finance']
    domain_names = ['Healthcare', 'Finance']

    for idx, (domain, domain_name) in enumerate(zip(domains, domain_names)):
        ax = axes[idx]

        # Number of metrics
        num_vars = len(metrics)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        # Plot each model
        colors = plt.cm.Set2(np.linspace(0, 1, len(models)))

        for model_idx, model in enumerate(models):
            result = next((r for r in agg_results
                          if r['model_name'] == model and r['domain'] == domain), None)

            if result:
                values = [result['scores'][m] for m in metric_keys]
                values += values[:1]  # Complete the circle

                ax.plot(angles, values, 'o-', linewidth=2.5, label=model,
                       color=colors[model_idx], markersize=8)
                ax.fill(angles, values, alpha=0.15, color=colors[model_idx])

        # Customize
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics, fontsize=13)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=11)
        ax.set_title(f'{domain_name} Domain', fontsize=16, weight='bold', pad=20)
        ax.grid(True, linewidth=0.8, alpha=0.3)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)

    fig.suptitle('Model Comparison Radar Charts', fontsize=20, weight='bold', y=1.02)
    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"radar_comparison_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_violation_analysis(results, output_dir):
    """Create violation analysis visualization."""

    print("\n[3/8] Creating violation analysis...")

    agg_results = results['aggregate_results']

    # Prepare data
    data = []
    for result in agg_results:
        data.append({
            'Model': result['model_name'],
            'Domain': result['domain'].capitalize(),
            'Total Violations': result['violations']['total'],
            'Critical Violations': result['violations']['critical'],
            'A²-Score': result['scores']['a2_score']
        })

    df = pd.DataFrame(data)

    # Create figure with subplots
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Subplot 1: Bar chart of violations
    ax1 = axes[0]
    x = np.arange(len(df))
    width = 0.35

    ax1.bar(x - width/2, df['Total Violations'], width, label='Total', color='#e74c3c', alpha=0.8)
    ax1.bar(x + width/2, df['Critical Violations'], width, label='Critical', color='#c0392b', alpha=0.8)

    ax1.set_xlabel('Model × Domain', fontsize=14, weight='bold')
    ax1.set_ylabel('Number of Violations', fontsize=14, weight='bold')
    ax1.set_title('Violation Counts by Model and Domain', fontsize=16, weight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{row['Model']}\n({row['Domain']})" for _, row in df.iterrows()],
                        rotation=45, ha='right', fontsize=11)
    ax1.legend(fontsize=12)
    ax1.grid(axis='y', alpha=0.3)

    # Subplot 2: Scatter plot - A² Score vs Violations
    ax2 = axes[1]

    healthcare_data = df[df['Domain'] == 'Healthcare']
    finance_data = df[df['Domain'] == 'Finance']

    ax2.scatter(healthcare_data['Critical Violations'], healthcare_data['A²-Score'],
               s=200, alpha=0.7, c='#3498db', label='Healthcare', edgecolors='black', linewidth=1.5)
    ax2.scatter(finance_data['Critical Violations'], finance_data['A²-Score'],
               s=200, alpha=0.7, c='#e74c3c', label='Finance', edgecolors='black', linewidth=1.5)

    # Add labels
    for _, row in df.iterrows():
        ax2.annotate(row['Model'],
                    (row['Critical Violations'], row['A²-Score']),
                    xytext=(5, 5), textcoords='offset points', fontsize=10)

    ax2.set_xlabel('Critical Violations', fontsize=14, weight='bold')
    ax2.set_ylabel('A²-Score', fontsize=14, weight='bold')
    ax2.set_title('A²-Score vs Critical Violations', fontsize=16, weight='bold')
    ax2.legend(fontsize=12)
    ax2.grid(alpha=0.3)

    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"violation_analysis_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_metric_correlation_matrix(results, output_dir):
    """Create correlation matrix for metrics."""

    print("\n[4/8] Creating metric correlation matrix...")

    per_case = results['per_case_results']

    # Extract metrics
    data = []
    for case in per_case:
        data.append({
            'Safety': case['safety'],
            'Security': case['security'],
            'Reliability': case['reliability'],
            'Compliance': case['compliance'],
            'A²-Score': case['a2_score']
        })

    df = pd.DataFrame(data)

    # Calculate correlation
    corr = df.corr()

    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))

    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    cmap = sns.diverging_palette(250, 10, as_cmap=True)

    sns.heatmap(corr, mask=mask, cmap=cmap, center=0,
                square=True, linewidths=2, cbar_kws={"shrink": 0.8},
                annot=True, fmt='.3f', annot_kws={'fontsize': 13, 'weight': 'bold'})

    ax.set_title('Metric Correlation Matrix', fontsize=18, weight='bold', pad=20)

    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"correlation_matrix_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_score_distribution(results, output_dir):
    """Create score distribution plots."""

    print("\n[5/8] Creating score distributions...")

    per_case = results['per_case_results']

    # Prepare data
    metrics = ['safety', 'security', 'reliability', 'compliance', 'a2_score']
    metric_labels = ['Safety', 'Security', 'Reliability', 'Compliance', 'A²-Score']

    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()

    for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
        ax = axes[idx]

        # Collect data by domain
        healthcare_scores = [c[metric] for c in per_case if c['domain'] == 'healthcare']
        finance_scores = [c[metric] for c in per_case if c['domain'] == 'finance']

        # Create violin plots
        parts = ax.violinplot([healthcare_scores, finance_scores],
                              positions=[1, 2],
                              showmeans=True, showextrema=True, showmedians=True)

        # Customize colors
        colors = ['#3498db', '#e74c3c']
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.7)

        ax.set_xticks([1, 2])
        ax.set_xticklabels(['Healthcare', 'Finance'])
        ax.set_ylabel('Score', fontsize=12, weight='bold')
        ax.set_title(label, fontsize=14, weight='bold')
        ax.set_ylim(-0.05, 1.05)
        ax.grid(axis='y', alpha=0.3)

    # Remove extra subplot
    fig.delaxes(axes[5])

    fig.suptitle('Score Distributions by Domain', fontsize=20, weight='bold')
    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"score_distributions_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_domain_comparison_scatter(results, output_dir):
    """Create scatter plot comparing domains."""

    print("\n[6/8] Creating domain comparison scatter...")

    agg_results = results['aggregate_results']

    # Get healthcare vs finance scores for each model
    models = sorted(set([r['model_name'] for r in agg_results]))

    healthcare_scores = []
    finance_scores = []
    model_labels = []

    for model in models:
        hc_result = next((r for r in agg_results
                         if r['model_name'] == model and r['domain'] == 'healthcare'), None)
        fin_result = next((r for r in agg_results
                          if r['model_name'] == model and r['domain'] == 'finance'), None)

        if hc_result and fin_result:
            healthcare_scores.append(hc_result['scores']['a2_score'])
            finance_scores.append(fin_result['scores']['a2_score'])
            model_labels.append(model)

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(12, 10))

    colors = plt.cm.Set2(np.linspace(0, 1, len(model_labels)))

    for i, (hc, fin, label) in enumerate(zip(healthcare_scores, finance_scores, model_labels)):
        ax.scatter(hc, fin, s=400, alpha=0.7, c=[colors[i]],
                  edgecolors='black', linewidth=2, label=label)
        ax.annotate(label, (hc, fin), xytext=(10, 10),
                   textcoords='offset points', fontsize=12, weight='bold')

    # Add diagonal line (perfect correlation)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, linewidth=2, label='Perfect Correlation')

    ax.set_xlabel('Healthcare Domain A²-Score', fontsize=14, weight='bold')
    ax.set_ylabel('Finance Domain A²-Score', fontsize=14, weight='bold')
    ax.set_title('Cross-Domain Performance Comparison', fontsize=18, weight='bold', pad=20)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=12, loc='lower right')

    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"domain_comparison_scatter_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_comprehensive_dashboard(results, output_dir):
    """Create comprehensive dashboard."""

    print("\n[7/8] Creating comprehensive dashboard...")

    agg_results = results['aggregate_results']

    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. Overall A² Scores (top-left)
    ax1 = fig.add_subplot(gs[0, :2])
    models = [r['model_name'] for r in agg_results]
    domains = [r['domain'].capitalize() for r in agg_results]
    a2_scores = [r['scores']['a2_score'] for r in agg_results]

    x = np.arange(len(models))
    colors = ['#3498db' if d == 'Healthcare' else '#e74c3c' for d in domains]

    bars = ax1.bar(x, a2_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('A²-Score', fontsize=12, weight='bold')
    ax1.set_title('Overall A²-Scores by Model and Domain', fontsize=14, weight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{m}\n({d})" for m, d in zip(models, domains)], rotation=45, ha='right')
    ax1.set_ylim(0, 1.1)
    ax1.grid(axis='y', alpha=0.3)

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}', ha='center', va='bottom', fontsize=10, weight='bold')

    # 2. Metric breakdown (top-right)
    ax2 = fig.add_subplot(gs[0, 2])
    metrics = ['Safety', 'Security', 'Reliability', 'Compliance']
    avg_scores = []
    for metric in ['safety', 'security', 'reliability', 'compliance']:
        avg_scores.append(np.mean([r['scores'][metric] for r in agg_results]))

    ax2.barh(metrics, avg_scores, color='#2ecc71', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.set_xlabel('Average Score', fontsize=12, weight='bold')
    ax2.set_title('Metric Averages', fontsize=14, weight='bold')
    ax2.set_xlim(0, 1.1)
    ax2.grid(axis='x', alpha=0.3)

    for i, v in enumerate(avg_scores):
        ax2.text(v, i, f' {v:.3f}', va='center', fontsize=10, weight='bold')

    # 3. Violations (middle-left)
    ax3 = fig.add_subplot(gs[1, :])
    total_viol = [r['violations']['total'] for r in agg_results]
    crit_viol = [r['violations']['critical'] for r in agg_results]

    x = np.arange(len(models))
    width = 0.35

    ax3.bar(x - width/2, total_viol, width, label='Total', color='#e74c3c', alpha=0.8)
    ax3.bar(x + width/2, crit_viol, width, label='Critical', color='#c0392b', alpha=0.8)

    ax3.set_ylabel('Violations', fontsize=12, weight='bold')
    ax3.set_title('Violation Analysis', fontsize=14, weight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{m}\n({d})" for m, d in zip(models, domains)], rotation=45, ha='right')
    ax3.legend(fontsize=11)
    ax3.grid(axis='y', alpha=0.3)

    # 4. Task completion (bottom-left)
    ax4 = fig.add_subplot(gs[2, 0])
    completion_rates = [r['task_completion_rate'] for r in agg_results]

    ax4.bar(x, completion_rates, color='#9b59b6', alpha=0.8, edgecolor='black', linewidth=1.5)
    ax4.set_ylabel('Completion Rate', fontsize=12, weight='bold')
    ax4.set_title('Task Completion Rates', fontsize=14, weight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels([f"{m}\n({d})" for m, d in zip(models, domains)], rotation=45, ha='right', fontsize=9)
    ax4.set_ylim(0, 1.1)
    ax4.grid(axis='y', alpha=0.3)

    # 5. Domain comparison pie (bottom-middle)
    ax5 = fig.add_subplot(gs[2, 1])
    healthcare_avg = np.mean([r['scores']['a2_score'] for r in agg_results if r['domain'] == 'healthcare'])
    finance_avg = np.mean([r['scores']['a2_score'] for r in agg_results if r['domain'] == 'finance'])

    wedges, texts, autotexts = ax5.pie([healthcare_avg, finance_avg],
                                        labels=['Healthcare', 'Finance'],
                                        autopct='%1.1f%%',
                                        colors=['#3498db', '#e74c3c'],
                                        startangle=90,
                                        textprops={'fontsize': 12, 'weight': 'bold'})
    ax5.set_title('Domain A²-Score Distribution', fontsize=14, weight='bold')

    # 6. Summary stats (bottom-right)
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')

    # Count unique test cases
    unique_cases = len(set([c.get('case_id', c.get('task_id', f"{c['model']}_{c['domain']}_{i}"))
                           for i, c in enumerate(results['per_case_results'])]))

    summary_text = f"""
    EVALUATION SUMMARY
    ==================

    Total Test Cases: {unique_cases}
    Models Evaluated: {len(set([r['model'] for r in agg_results]))}
    Domains: {len(set([r['domain'] for r in agg_results]))}

    Average A²-Score: {np.mean([r['scores']['a2_score'] for r in agg_results]):.3f}
    Best Score: {np.max([r['scores']['a2_score'] for r in agg_results]):.3f}
    Worst Score: {np.min([r['scores']['a2_score'] for r in agg_results]):.3f}

    Total Violations: {sum([r['violations']['total'] for r in agg_results])}
    Critical: {sum([r['violations']['critical'] for r in agg_results])}
    """

    ax6.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    fig.suptitle('A²-Bench Comprehensive Evaluation Dashboard',
                fontsize=22, weight='bold', y=0.98)

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dashboard_comprehensive_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def create_test_case_analysis(results, output_dir):
    """Create test case-level analysis."""

    print("\n[8/8] Creating test case analysis...")

    per_case = results['per_case_results']

    # Group by test case (use case_id or task_id or generate one)
    test_cases = {}
    for i, case in enumerate(per_case):
        task_id = case.get('case_id', case.get('task_id', f"{case['domain']}_{i}"))
        if task_id not in test_cases:
            test_cases[task_id] = []
        test_cases[task_id].append(case)

    # Calculate variance across models for each test case
    variances = []
    for task_id, cases in test_cases.items():
        a2_scores = [c['a2_score'] for c in cases]
        variances.append({
            'task_id': task_id,
            'mean': np.mean(a2_scores),
            'variance': np.var(a2_scores),
            'domain': cases[0]['domain']
        })

    df = pd.DataFrame(variances).sort_values('variance', ascending=False)

    # Plot top 20 most variable test cases
    fig, ax = plt.subplots(figsize=(16, 10))

    top_20 = df.head(20)
    colors = ['#3498db' if d == 'healthcare' else '#e74c3c' for d in top_20['domain']]

    bars = ax.barh(range(len(top_20)), top_20['variance'], color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels(top_20['task_id'], fontsize=10)
    ax.set_xlabel('Score Variance Across Models', fontsize=14, weight='bold')
    ax.set_title('Top 20 Most Discriminative Test Cases', fontsize=18, weight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3)

    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#3498db', label='Healthcare'),
                      Patch(facecolor='#e74c3c', label='Finance')]
    ax.legend(handles=legend_elements, fontsize=12)

    plt.tight_layout()

    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_case_analysis_{timestamp}"
    plt.savefig(output_dir / f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.savefig(output_dir / f"{filename}.pdf", bbox_inches='tight')
    plt.close()

    print(f"  ✓ Saved: {filename}.png/pdf")


def main():
    """Generate all advanced visualizations."""

    print("="*80)
    print("ADVANCED PUBLICATION-QUALITY VISUALIZATIONS")
    print("="*80)

    # Load results
    results = load_latest_results()

    # Output directory
    output_dir = Path("experiments/results/icml")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate visualizations
    create_performance_heatmap(results, output_dir)
    create_radar_charts(results, output_dir)
    create_violation_analysis(results, output_dir)
    create_metric_correlation_matrix(results, output_dir)
    create_score_distribution(results, output_dir)
    create_domain_comparison_scatter(results, output_dir)
    create_comprehensive_dashboard(results, output_dir)
    create_test_case_analysis(results, output_dir)

    print("\n" + "="*80)
    print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
    print("="*80)
    print(f"\nAll visualizations saved to: {output_dir}")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
