#!/usr/bin/env python3
"""
Generate comprehensive research-grade tables for A2Bench results.
Creates LaTeX tables suitable for ICML/NeurIPS publications.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


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


def create_main_results_table(results):
    """Create main results table (Table 1)."""

    print("\n" + "="*80)
    print("TABLE 1: Overall Performance Across Domains and Models")
    print("="*80)

    # Extract aggregate results
    agg_results = results['aggregate_results']

    # Create DataFrame
    rows = []
    for result in agg_results:
        rows.append({
            'Model': result['model_name'],
            'Domain': result['domain'].capitalize(),
            'Safety': result['scores']['safety'],
            'Security': result['scores']['security'],
            'Reliability': result['scores']['reliability'],
            'Compliance': result['scores']['compliance'],
            'A²-Score': result['scores']['a2_score'],
            'Violations': result['violations']['total'],
            'Critical': result['violations']['critical'],
            'Completion': result['task_completion_rate']
        })

    df = pd.DataFrame(rows)

    # Print markdown table
    print("\n" + df.to_markdown(index=False, floatfmt=".3f"))

    # Generate LaTeX table
    latex = r"""
\begin{table}[t]
\centering
\caption{Overall Performance Across Domains and Models. Scores range from 0 to 1, with 1 being perfect. The A²-Score is a weighted combination of Safety (40\%), Security (30\%), Reliability (20\%), and Compliance (10\%).}
\label{tab:main_results}
\begin{tabular}{llrrrrrrrr}
\toprule
\textbf{Model} & \textbf{Domain} & \textbf{Safety} & \textbf{Security} & \textbf{Reliability} & \textbf{Compliance} & \textbf{A²} & \textbf{Viol.} & \textbf{Crit.} & \textbf{Comp.} \\
\midrule
"""

    for _, row in df.iterrows():
        latex += f"{row['Model']} & {row['Domain']} & {row['Safety']:.3f} & {row['Security']:.3f} & {row['Reliability']:.3f} & {row['Compliance']:.3f} & {row['A²-Score']:.3f} & {int(row['Violations'])} & {int(row['Critical'])} & {row['Completion']:.2f} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""

    # Save LaTeX
    output_file = Path("experiments/results/icml/table1_main_results.tex")
    with open(output_file, 'w') as f:
        f.write(latex)

    print(f"\n✓ Saved LaTeX table to: {output_file}")

    return df


def create_domain_comparison_table(results):
    """Create domain-wise comparison table (Table 2)."""

    print("\n" + "="*80)
    print("TABLE 2: Domain-Specific Performance Analysis")
    print("="*80)

    agg_results = results['aggregate_results']

    # Calculate domain averages
    healthcare_results = [r for r in agg_results if r['domain'] == 'healthcare']
    finance_results = [r for r in agg_results if r['domain'] == 'finance']

    domains = []
    for domain_name, domain_results in [('Healthcare', healthcare_results), ('Finance', finance_results)]:
        avg_scores = {
            'safety': np.mean([r['scores']['safety'] for r in domain_results]),
            'security': np.mean([r['scores']['security'] for r in domain_results]),
            'reliability': np.mean([r['scores']['reliability'] for r in domain_results]),
            'compliance': np.mean([r['scores']['compliance'] for r in domain_results]),
            'a2_score': np.mean([r['scores']['a2_score'] for r in domain_results])
        }

        total_violations = sum([r['violations']['total'] for r in domain_results])
        critical_violations = sum([r['violations']['critical'] for r in domain_results])
        num_cases = domain_results[0]['num_cases']

        domains.append({
            'Domain': domain_name,
            'Test Cases': num_cases,
            'Avg Safety': avg_scores['safety'],
            'Avg Security': avg_scores['security'],
            'Avg Reliability': avg_scores['reliability'],
            'Avg Compliance': avg_scores['compliance'],
            'Avg A²-Score': avg_scores['a2_score'],
            'Total Violations': total_violations,
            'Critical Violations': critical_violations
        })

    df = pd.DataFrame(domains)
    print("\n" + df.to_markdown(index=False, floatfmt=".3f"))

    # LaTeX
    latex = r"""
\begin{table}[t]
\centering
\caption{Domain-Specific Performance Analysis. Averages computed across all models evaluated in each domain.}
\label{tab:domain_comparison}
\begin{tabular}{lrrrrrrrrr}
\toprule
\textbf{Domain} & \textbf{Cases} & \textbf{Safety} & \textbf{Security} & \textbf{Reliability} & \textbf{Compliance} & \textbf{A²} & \textbf{Tot. Viol.} & \textbf{Crit. Viol.} \\
\midrule
"""

    for _, row in df.iterrows():
        latex += f"{row['Domain']} & {int(row['Test Cases'])} & {row['Avg Safety']:.3f} & {row['Avg Security']:.3f} & {row['Avg Reliability']:.3f} & {row['Avg Compliance']:.3f} & {row['Avg A²-Score']:.3f} & {int(row['Total Violations'])} & {int(row['Critical Violations'])} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""

    output_file = Path("experiments/results/icml/table2_domain_comparison.tex")
    with open(output_file, 'w') as f:
        f.write(latex)

    print(f"\n✓ Saved LaTeX table to: {output_file}")

    return df


def create_model_ranking_table(results):
    """Create model ranking table (Table 3)."""

    print("\n" + "="*80)
    print("TABLE 3: Model Rankings by A²-Score")
    print("="*80)

    agg_results = results['aggregate_results']

    # Calculate average A² score per model
    models = {}
    for result in agg_results:
        model = result['model_name']
        if model not in models:
            models[model] = {
                'scores': [],
                'violations': [],
                'critical_violations': [],
                'completion_rates': []
            }

        models[model]['scores'].append(result['scores']['a2_score'])
        models[model]['violations'].append(result['violations']['total'])
        models[model]['critical_violations'].append(result['violations']['critical'])
        models[model]['completion_rates'].append(result['task_completion_rate'])

    # Create ranking
    rankings = []
    for model, data in models.items():
        rankings.append({
            'Model': model,
            'Avg A²-Score': np.mean(data['scores']),
            'Std Dev': np.std(data['scores']),
            'Total Violations': sum(data['violations']),
            'Critical Violations': sum(data['critical_violations']),
            'Avg Completion': np.mean(data['completion_rates'])
        })

    # Sort by A² score
    df = pd.DataFrame(rankings).sort_values('Avg A²-Score', ascending=False)
    df['Rank'] = range(1, len(df) + 1)
    df = df[['Rank', 'Model', 'Avg A²-Score', 'Std Dev', 'Total Violations', 'Critical Violations', 'Avg Completion']]

    print("\n" + df.to_markdown(index=False, floatfmt=".3f"))

    # LaTeX
    latex = r"""
\begin{table}[t]
\centering
\caption{Model Rankings by Average A²-Score. Models ranked by performance across both healthcare and finance domains.}
\label{tab:model_ranking}
\begin{tabular}{clrrrrrr}
\toprule
\textbf{Rank} & \textbf{Model} & \textbf{A²-Score} & \textbf{Std Dev} & \textbf{Tot. Viol.} & \textbf{Crit. Viol.} & \textbf{Completion} \\
\midrule
"""

    for _, row in df.iterrows():
        latex += f"{int(row['Rank'])} & {row['Model']} & {row['Avg A²-Score']:.3f} & {row['Std Dev']:.3f} & {int(row['Total Violations'])} & {int(row['Critical Violations'])} & {row['Avg Completion']:.2f} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""

    output_file = Path("experiments/results/icml/table3_model_ranking.tex")
    with open(output_file, 'w') as f:
        f.write(latex)

    print(f"\n✓ Saved LaTeX table to: {output_file}")

    return df


def create_detailed_metrics_table(results):
    """Create detailed per-metric breakdown table (Table 4)."""

    print("\n" + "="*80)
    print("TABLE 4: Detailed Metric Breakdown by Model and Domain")
    print("="*80)

    agg_results = results['aggregate_results']

    # Create detailed breakdown
    rows = []
    for result in agg_results:
        rows.append({
            'Model': result['model_name'],
            'Domain': result['domain'].capitalize(),
            'Safety': f"{result['scores']['safety']:.3f} ± {result['std']['safety']:.3f}",
            'Security': f"{result['scores']['security']:.3f} ± {result['std']['security']:.3f}",
            'Reliability': f"{result['scores']['reliability']:.3f} ± {result['std']['reliability']:.3f}",
            'Compliance': f"{result['scores']['compliance']:.3f} ± {result['std']['compliance']:.3f}",
            'A²-Score': f"{result['scores']['a2_score']:.3f} ± {result['std']['a2_score']:.3f}"
        })

    df = pd.DataFrame(rows)
    print("\n" + df.to_markdown(index=False))

    # LaTeX
    latex = r"""
\begin{table}[t]
\centering
\caption{Detailed Metric Breakdown. All values shown as mean ± standard deviation across test cases.}
\label{tab:detailed_metrics}
\small
\begin{tabular}{llccccc}
\toprule
\textbf{Model} & \textbf{Domain} & \textbf{Safety} & \textbf{Security} & \textbf{Reliability} & \textbf{Compliance} & \textbf{A²-Score} \\
\midrule
"""

    for result in agg_results:
        model = result['model_name']
        domain = result['domain'].capitalize()
        safety = f"{result['scores']['safety']:.3f} $\\pm$ {result['std']['safety']:.3f}"
        security = f"{result['scores']['security']:.3f} $\\pm$ {result['std']['security']:.3f}"
        reliability = f"{result['scores']['reliability']:.3f} $\\pm$ {result['std']['reliability']:.3f}"
        compliance = f"{result['scores']['compliance']:.3f} $\\pm$ {result['std']['compliance']:.3f}"
        a2 = f"{result['scores']['a2_score']:.3f} $\\pm$ {result['std']['a2_score']:.3f}"

        latex += f"{model} & {domain} & {safety} & {security} & {reliability} & {compliance} & {a2} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""

    output_file = Path("experiments/results/icml/table4_detailed_metrics.tex")
    with open(output_file, 'w') as f:
        f.write(latex)

    print(f"\n✓ Saved LaTeX table to: {output_file}")

    return df


def create_summary_statistics_table(results):
    """Create summary statistics table (Table 5)."""

    print("\n" + "="*80)
    print("TABLE 5: Summary Statistics")
    print("="*80)

    agg_results = results['aggregate_results']

    # Calculate summary statistics
    total_test_cases = sum(set([r['num_cases'] for r in agg_results]))
    num_models = len(set([r['model'] for r in agg_results]))
    total_evaluations = len(agg_results)
    avg_eval_time = np.mean([r['elapsed_time'] for r in agg_results])
    all_a2_scores = [r['scores']['a2_score'] for r in agg_results]
    avg_a2_score = np.mean(all_a2_scores)
    best_a2_score = np.max(all_a2_scores)
    worst_a2_score = np.min(all_a2_scores)

    stats = {
        'Metric': [
            'Total Test Cases',
            'Total Models Evaluated',
            'Total Evaluations',
            'Average Evaluation Time (s)',
            'Average A²-Score',
            'Best A²-Score',
            'Worst A²-Score'
        ],
        'Value': [
            total_test_cases,
            num_models,
            total_evaluations,
            f"{avg_eval_time:.3f}",
            f"{avg_a2_score:.3f}",
            f"{best_a2_score:.3f}",
            f"{worst_a2_score:.3f}"
        ]
    }

    df = pd.DataFrame(stats)
    print("\n" + df.to_markdown(index=False))

    # LaTeX
    latex = r"""
\begin{table}[t]
\centering
\caption{Summary Statistics for Full Dataset Evaluation.}
\label{tab:summary_stats}
\begin{tabular}{lr}
\toprule
\textbf{Metric} & \textbf{Value} \\
\midrule
"""

    for _, row in df.iterrows():
        latex += f"{row['Metric']} & {row['Value']} \\\\\n"

    latex += r"""\bottomrule
\end{tabular}
\end{table}
"""

    output_file = Path("experiments/results/icml/table5_summary_stats.tex")
    with open(output_file, 'w') as f:
        f.write(latex)

    print(f"\n✓ Saved LaTeX table to: {output_file}")

    return df


def main():
    """Generate all tables."""

    print("="*80)
    print("COMPREHENSIVE TABLE GENERATION FOR A2BENCH")
    print("="*80)

    # Load results
    results = load_latest_results()

    # Generate tables
    table1 = create_main_results_table(results)
    table2 = create_domain_comparison_table(results)
    table3 = create_model_ranking_table(results)
    table4 = create_detailed_metrics_table(results)
    table5 = create_summary_statistics_table(results)

    print("\n" + "="*80)
    print("✓ ALL TABLES GENERATED SUCCESSFULLY")
    print("="*80)
    print("\nLaTeX tables saved to experiments/results/icml/")
    print("  - table1_main_results.tex")
    print("  - table2_domain_comparison.tex")
    print("  - table3_model_ranking.tex")
    print("  - table4_detailed_metrics.tex")
    print("  - table5_summary_stats.tex")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
