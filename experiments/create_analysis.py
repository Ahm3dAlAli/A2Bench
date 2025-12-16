"""
Generate visualizations and comprehensive analysis for A²-Bench experiments.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import Dict, List


def load_latest_results(results_dir: str = "experiments/results") -> Dict:
    """Load the latest comprehensive results.

    Args:
        results_dir: Directory containing results

    Returns:
        Latest results dictionary
    """
    # Look for comprehensive results files
    files = [
        f
        for f in os.listdir(results_dir)
        if f.startswith("comprehensive_") and f.endswith(".json")
    ]

    if not files:
        raise FileNotFoundError("No comprehensive results found")

    # Get the latest file
    latest_file = sorted(files)[-1]
    latest_path = os.path.join(results_dir, latest_file)

    with open(latest_path, "r") as f:
        return json.load(f)


def create_performance_comparison_chart(results: Dict, output_dir: str):
    """Create performance comparison chart.

    Args:
        results: Evaluation results
        output_dir: Output directory
    """
    # Set up the figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(
        "A²-Bench Performance Analysis Across Domains", fontsize=16, fontweight="bold"
    )

    domains = []
    func_success = []
    sec_block = []
    a2_scores = []

    # Extract data
    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})
        domains.append(domain_name.title())
        func_success.append(summary.get("functional_success_rate", 0))
        sec_block.append(summary.get("adversarial_block_rate", 0))
        a2_scores.append(summary.get("overall_a2_score", 0))

    # 1. Success Rates Comparison
    x = np.arange(len(domains))
    width = 0.35

    ax1.bar(
        x - width / 2,
        func_success,
        width,
        label="Functional Success",
        color="skyblue",
        alpha=0.8,
    )
    ax1.bar(
        x + width / 2,
        sec_block,
        width,
        label="Security Block Rate",
        color="lightcoral",
        alpha=0.8,
    )

    ax1.set_xlabel("Domain")
    ax1.set_ylabel("Success Rate")
    ax1.set_title("Functional vs Security Performance")
    ax1.set_xticks(x)
    ax1.set_xticklabels(domains)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Add value labels on bars
    for i, (f, s) in enumerate(zip(func_success, sec_block)):
        ax1.text(
            i - width / 2,
            f + 0.01,
            f"{f:.1%}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
        ax1.text(
            i + width / 2,
            s + 0.01,
            f"{s:.1%}",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # 2. A²-Score Comparison
    colors = [
        "gold" if score >= 0.9 else "lightgreen" if score >= 0.7 else "lightcoral"
        for score in a2_scores
    ]
    bars = ax2.bar(domains, a2_scores, color=colors, alpha=0.8)

    ax2.set_xlabel("Domain")
    ax2.set_ylabel("A²-Score")
    ax2.set_title("Overall A²-Score by Domain")
    ax2.set_ylim(0, 1.1)
    ax2.grid(True, alpha=0.3)

    # Add value labels and grade
    for i, (bar, score) in enumerate(zip(bars, a2_scores)):
        height = bar.get_height()
        grade = (
            "A+"
            if score >= 0.9
            else "A"
            if score >= 0.8
            else "B"
            if score >= 0.7
            else "C"
            if score >= 0.6
            else "F"
        )
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.02,
            f"{score:.3f}\n({grade})",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    # 3. Component Scores Radar Chart
    categories = ["Safety", "Security", "Reliability", "Compliance"]

    # Create subplot for radar chart (using polar coordinates)
    ax3.remove()
    ax3 = fig.add_subplot(2, 2, 3, projection="polar")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})
        values = [
            summary.get("safety_score", 0),
            summary.get("security_score", 0),
            summary.get("reliability_score", 0),
            summary.get("compliance_score", 0),
        ]

        # Complete the circle
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        ax3.plot(angles, values, "o-", linewidth=2, label=domain_name.title())
        ax3.fill(angles, values, alpha=0.25)

    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(categories)
    ax3.set_ylim(0, 1)
    ax3.set_title("Component Scores Comparison")
    ax3.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
    ax3.grid(True)

    # 4. Task Completion Summary
    task_types = [
        "Functional\nSuccess",
        "Functional\nFailure",
        "Adversarial\nBlocked",
        "Adversarial\nMissed",
    ]
    colors = ["lightgreen", "lightcoral", "lightblue", "orange"]

    total_stats = [0, 0, 0, 0]

    for domain_data in results.get("domains", {}).values():
        if "error" in domain_data:
            continue

        func_eval = domain_data.get("functional_evaluation", {})
        adv_eval = domain_data.get("adversarial_evaluation", {})

        total_stats[0] += func_eval.get("successful_tasks", 0)
        total_stats[1] += func_eval.get("failed_tasks", 0)
        total_stats[2] += adv_eval.get("blocked_tasks", 0)
        total_stats[3] += adv_eval.get("unblocked_tasks", 0)

    # Create pie chart
    wedges, texts, autotexts = ax4.pie(
        total_stats,
        labels=task_types,
        colors=colors,
        autopct="%1.0f",
        startangle=90,
        textprops={"fontsize": 10},
    )

    # Enhance text
    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    ax4.set_title("Task Completion Summary")

    plt.tight_layout()

    # Save the figure
    output_file = os.path.join(output_dir, "performance_analysis.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Performance comparison chart saved to: {output_file}")


def create_detailed_analysis_report(results: Dict, output_dir: str):
    """Create a comprehensive analysis report.

    Args:
        results: Evaluation results
        output_dir: Output directory
    """
    report = []
    report.append("# A²-Bench Comprehensive Analysis Report")
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Executive Summary
    report.append("## Executive Summary")
    report.append("")

    total_domains = len(
        [d for d in results.get("domains", {}).values() if "error" not in d]
    )
    total_tasks = 0
    total_successful = 0

    for domain_data in results.get("domains", {}).values():
        if "error" in domain_data:
            continue

        func_eval = domain_data.get("functional_evaluation", {})
        adv_eval = domain_data.get("adversarial_evaluation", {})

        total_tasks += func_eval.get("total_tasks", 0) + adv_eval.get("total_tasks", 0)
        total_successful += func_eval.get("successful_tasks", 0) + adv_eval.get(
            "blocked_tasks", 0
        )

    overall_success_rate = total_successful / max(1, total_tasks)

    report.append(
        f"This report presents a comprehensive analysis of the A²-Bench evaluation conducted on {total_domains} domains."
    )
    report.append(
        f"The evaluation assessed a total of {total_tasks} tasks across functional and adversarial scenarios."
    )
    report.append(
        f"Overall system achieved a {overall_success_rate:.1%} success rate across all evaluated scenarios."
    )
    report.append("")

    # Domain-Specific Analysis
    report.append("## Domain-Specific Analysis")
    report.append("")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        report.append(f"### {domain_name.title()} Domain")
        report.append("")

        summary = domain_data.get("summary", {})
        func_eval = domain_data.get("functional_evaluation", {})
        adv_eval = domain_data.get("adversarial_evaluation", {})

        # Performance metrics
        report.append("#### Performance Metrics")
        report.append(
            f"- **Functional Success Rate**: {summary.get('functional_success_rate', 0):.1%}"
        )
        report.append(
            f"- **Security Block Rate**: {summary.get('adversarial_block_rate', 0):.1%}"
        )
        report.append(
            f"- **Overall A²-Score**: {summary.get('overall_a2_score', 0):.3f}"
        )
        report.append("")

        # Component analysis
        report.append("#### Component Analysis")
        report.append(f"- **Safety Score**: {summary.get('safety_score', 0):.3f}")
        report.append(f"- **Security Score**: {summary.get('security_score', 0):.3f}")
        report.append(
            f"- **Reliability Score**: {summary.get('reliability_score', 0):.3f}"
        )
        report.append(
            f"- **Compliance Score**: {summary.get('compliance_score', 0):.3f}"
        )
        report.append("")

        # Task breakdown
        report.append("#### Task Breakdown")
        report.append(
            f"- **Functional Tasks**: {func_eval.get('successful_tasks', 0)}/{func_eval.get('total_tasks', 0)} successful"
        )
        report.append(
            f"- **Adversarial Tasks**: {adv_eval.get('blocked_tasks', 0)}/{adv_eval.get('total_tasks', 0)} blocked"
        )
        report.append("")

        # Strengths and weaknesses
        a2_score = summary.get("overall_a2_score", 0)
        if a2_score >= 0.9:
            report.append("#### Assessment: Excellent Performance")
            report.append(
                "The domain demonstrates exceptional performance across all evaluated metrics."
            )
        elif a2_score >= 0.7:
            report.append("#### Assessment: Good Performance")
            report.append(
                "The domain shows strong performance with minor areas for improvement."
            )
        else:
            report.append("#### Assessment: Needs Improvement")
            report.append(
                "The domain requires significant improvements to meet expected standards."
            )

        report.append("")

    # Comparative Analysis
    report.append("## Comparative Analysis")
    report.append("")

    # Compare domains
    domain_scores = {}
    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" not in domain_data:
            summary = domain_data.get("summary", {})
            domain_scores[domain_name] = summary.get("overall_a2_score", 0)

    if domain_scores:
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

        report.append("### Domain Performance Ranking")
        report.append("")
        for i, (domain, score) in enumerate(sorted_domains, 1):
            report.append(f"{i}. **{domain.title()}**: A²-Score of {score:.3f}")

        report.append("")

        best_domain = sorted_domains[0][0]
        worst_domain = sorted_domains[-1][0]

        report.append(
            f"The **{best_domain.title()}** domain achieved the highest performance with an A²-Score of {domain_scores[best_domain]:.3f}."
        )
        if len(sorted_domains) > 1:
            report.append(
                f"The **{worst_domain.title()}** domain showed the lowest performance with an A²-Score of {domain_scores[worst_domain]:.3f}."
            )

        report.append("")

    # Security Analysis
    report.append("## Security Analysis")
    report.append("")

    total_adv_tasks = 0
    total_blocked = 0

    for domain_data in results.get("domains", {}).values():
        if "error" in domain_data:
            continue

        adv_eval = domain_data.get("adversarial_evaluation", {})
        total_adv_tasks += adv_eval.get("total_tasks", 0)
        total_blocked += adv_eval.get("blocked_tasks", 0)

    security_rate = total_blocked / max(1, total_adv_tasks)

    report.append(
        f"The system demonstrated strong security capabilities, successfully blocking {total_blocked} out of {total_adv_tasks} adversarial attempts ({security_rate:.1%} block rate)."
    )
    report.append("")

    if security_rate >= 0.9:
        report.append("### Security Assessment: Excellent")
        report.append(
            "The system provides robust protection against a wide range of adversarial attacks."
        )
    elif security_rate >= 0.7:
        report.append("### Security Assessment: Good")
        report.append(
            "The system effectively blocks most attacks but may have some security gaps."
        )
    else:
        report.append("### Security Assessment: Needs Improvement")
        report.append(
            "The system has significant security vulnerabilities that require attention."
        )

    report.append("")

    # Recommendations
    report.append("## Recommendations")
    report.append("")

    # Analyze overall performance and provide recommendations
    overall_func = np.mean(
        [
            d.get("summary", {}).get("functional_success_rate", 0)
            for d in results.get("domains", {}).values()
            if "error" not in d
        ]
    )
    overall_sec = np.mean(
        [
            d.get("summary", {}).get("adversarial_block_rate", 0)
            for d in results.get("domains", {}).values()
            if "error" not in d
        ]
    )

    recommendations = []

    if overall_func >= 0.9:
        recommendations.append(
            "Maintain high functional performance through regular testing and validation."
        )
    elif overall_func >= 0.7:
        recommendations.append(
            "Focus on improving task completion reliability, particularly for edge cases."
        )
    else:
        recommendations.append(
            "Priority: Address fundamental functionality issues before focusing on advanced features."
        )

    if overall_sec >= 0.9:
        recommendations.append(
            "Continue maintaining strong security measures and regular security audits."
        )
    elif overall_sec >= 0.7:
        recommendations.append(
            "Enhance security protocols to address the remaining attack vectors."
        )
    else:
        recommendations.append(
            "Critical: Implement comprehensive security overhaul to address significant vulnerabilities."
        )

    # Add domain-specific recommendations
    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})
        a2_score = summary.get("overall_a2_score", 0)

        if a2_score < 0.8:
            recommendations.append(
                f"For {domain_name.title()} domain: Investigate specific challenges and implement targeted improvements."
            )

    for i, rec in enumerate(recommendations, 1):
        report.append(f"{i}. {rec}")

    report.append("")

    # Conclusion
    report.append("## Conclusion")
    report.append("")
    report.append(
        "The A²-Bench evaluation provides valuable insights into the system's performance across critical dimensions of functionality and security."
    )
    report.append(
        f"With an overall success rate of {overall_success_rate:.1%}, the system demonstrates {'strong' if overall_success_rate >= 0.8 else 'moderate' if overall_success_rate >= 0.6 else 'limited'} capability to handle both legitimate tasks and adversarial attacks."
    )
    report.append("")
    report.append(
        "Continuous monitoring, regular evaluation, and iterative improvement are essential to maintain and enhance system performance in real-world deployment scenarios."
    )
    report.append("")

    # Appendices
    report.append("## Appendices")
    report.append("")
    report.append("### Evaluation Methodology")
    report.append(
        "- **Functional Tasks**: Evaluate system's ability to handle legitimate user requests"
    )
    report.append(
        "- **Adversarial Tasks**: Assess system's resilience against various attack vectors"
    )
    report.append(
        "- **Scoring**: A²-Score combines functional success and security block rates with domain-specific weights"
    )
    report.append("")

    # Save the report
    report_content = "\n".join(report)
    report_file = os.path.join(output_dir, "comprehensive_analysis_report.md")

    with open(report_file, "w") as f:
        f.write(report_content)

    print(f"Comprehensive analysis report saved to: {report_file}")
    return report_content


def main():
    """Generate visualizations and analysis reports."""
    results_dir = "experiments/results"

    try:
        # Load latest results
        results = load_latest_results(results_dir)
        print(f"Loaded results from: {results.get('timestamp', 'unknown')}")

        # Create performance comparison chart
        create_performance_comparison_chart(results, results_dir)

        # Create comprehensive analysis report
        create_detailed_analysis_report(results, results_dir)

        print("\nVisualization and analysis generation completed successfully!")
        print(f"Generated files in: {results_dir}")

    except Exception as e:
        print(f"Error generating visualizations: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
