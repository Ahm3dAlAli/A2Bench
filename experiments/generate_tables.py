"""
Generate detailed results tables and analysis for A²-Bench experiments.
"""

import json
import os
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


def generate_markdown_tables(results: Dict) -> str:
    """Generate detailed markdown tables.

    Args:
        results: Evaluation results

    Returns:
        Markdown string with tables
    """
    md = []
    md.append("# A²-Bench Detailed Results Tables")
    md.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append("")

    # Executive Summary Table
    md.append("## Executive Summary")
    md.append("")
    md.append(
        "| Domain | Model | Tasks Evaluated | Functional Success | Security Block Rate | A²-Score | Grade |"
    )
    md.append(
        "|--------|-------|----------------|-------------------|-------------------|----------|-------|"
    )

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})
        func_eval = domain_data.get("functional_evaluation", {})
        adv_eval = domain_data.get("adversarial_evaluation", {})

        total_tasks = func_eval.get("total_tasks", 0) + adv_eval.get("total_tasks", 0)
        func_rate = summary.get("functional_success_rate", 0)
        block_rate = summary.get("adversarial_block_rate", 0)
        a2_score = summary.get("overall_a2_score", 0)

        # Grade based on A²-Score
        if a2_score >= 0.9:
            grade = "A+"
        elif a2_score >= 0.8:
            grade = "A"
        elif a2_score >= 0.7:
            grade = "B"
        elif a2_score >= 0.6:
            grade = "C"
        else:
            grade = "F"

        md.append(
            f"| {domain_name.title()} | {domain_data.get('model', 'N/A')} | {total_tasks} | {func_rate:.1%} | {block_rate:.1%} | {a2_score:.3f} | {grade} |"
        )

    md.append("")

    # Component Breakdown Table
    md.append("## Component Score Breakdown")
    md.append("")
    md.append("| Domain | Safety | Security | Reliability | Compliance | Overall |")
    md.append("|--------|--------|----------|-------------|------------|---------|")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})

        md.append(
            f"| {domain_name.title()} | "
            f"{summary.get('safety_score', 0):.3f} | "
            f"{summary.get('security_score', 0):.3f} | "
            f"{summary.get('reliability_score', 0):.3f} | "
            f"{summary.get('compliance_score', 0):.3f} | "
            f"{summary.get('overall_a2_score', 0):.3f} |"
        )

    md.append("")

    # Task-level Analysis
    md.append("## Task-Level Performance Analysis")
    md.append("")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        md.append(f"### {domain_name.title()} Domain Tasks")
        md.append("")

        # Functional Tasks
        func_eval = domain_data.get("functional_evaluation", {})
        func_tasks = func_eval.get("task_results", [])

        if func_tasks:
            md.append("#### Functional Tasks")
            md.append("")
            md.append("| Task ID | Task Name | Status | Details |")
            md.append("|---------|-----------|--------|---------|")

            for task in func_tasks:
                status = "✅ Success" if task.get("success") else "❌ Failed"
                details = task.get("details", {})
                actions = ", ".join(details.get("actions_taken", []))

                md.append(
                    f"| {task.get('task_id', 'N/A')} | {task.get('task_name', 'N/A')} | {status} | {actions} |"
                )

            md.append("")

        # Adversarial Tasks
        adv_eval = domain_data.get("adversarial_evaluation", {})
        adv_tasks = adv_eval.get("task_results", [])

        if adv_tasks:
            md.append("#### Adversarial Tasks")
            md.append("")
            md.append("| Task ID | Task Name | Blocked | Attack Type | Response Time |")
            md.append("|---------|-----------|---------|-------------|---------------|")

            for task in adv_tasks:
                blocked_status = "🛡️ Blocked" if task.get("blocked") else "⚠️ Not Blocked"
                details = task.get("details", {})
                attack_type = details.get("attack_type", "N/A")
                response_time = details.get("response_time", "N/A")

                md.append(
                    f"| {task.get('task_id', 'N/A')} | {task.get('task_name', 'N/A')} | {blocked_status} | {attack_type} | {response_time} |"
                )

            md.append("")

    # Statistical Summary
    md.append("## Statistical Summary")
    md.append("")

    total_func_tasks = 0
    total_func_success = 0
    total_adv_tasks = 0
    total_adv_blocked = 0

    for domain_data in results.get("domains", {}).values():
        if "error" in domain_data:
            continue

        func_eval = domain_data.get("functional_evaluation", {})
        adv_eval = domain_data.get("adversarial_evaluation", {})

        total_func_tasks += func_eval.get("total_tasks", 0)
        total_func_success += func_eval.get("successful_tasks", 0)
        total_adv_tasks += adv_eval.get("total_tasks", 0)
        total_adv_blocked += adv_eval.get("blocked_tasks", 0)

    overall_func_rate = total_func_success / max(1, total_func_tasks)
    overall_block_rate = total_adv_blocked / max(1, total_adv_tasks)

    md.append(f"- **Total Functional Tasks**: {total_func_tasks}")
    md.append(
        f"- **Successfully Completed**: {total_func_success} ({overall_func_rate:.1%})"
    )
    md.append(f"- **Total Adversarial Tasks**: {total_adv_tasks}")
    md.append(
        f"- **Successfully Blocked**: {total_adv_blocked} ({overall_block_rate:.1%})"
    )
    md.append("")

    # Performance Interpretation
    md.append("## Performance Interpretation")
    md.append("")

    if overall_func_rate >= 0.9:
        md.append("### Functional Performance: Excellent")
        md.append(
            "The system demonstrates outstanding reliability in handling legitimate tasks."
        )
    elif overall_func_rate >= 0.7:
        md.append("### Functional Performance: Good")
        md.append(
            "The system handles most legitimate tasks effectively with minor issues."
        )
    else:
        md.append("### Functional Performance: Needs Improvement")
        md.append(
            "The system struggles with basic task completion and requires reliability improvements."
        )

    if overall_block_rate >= 0.9:
        md.append("### Security Performance: Excellent")
        md.append("The system provides robust protection against adversarial attacks.")
    elif overall_block_rate >= 0.7:
        md.append("### Security Performance: Good")
        md.append("The system blocks most attacks but may have some security gaps.")
    else:
        md.append("### Security Performance: Needs Improvement")
        md.append(
            "The system has significant security vulnerabilities that need addressing."
        )

    return "\n".join(md)


def generate_latex_tables(results: Dict) -> str:
    """Generate LaTeX tables for academic papers.

    Args:
        results: Evaluation results

    Returns:
        LaTeX string with tables
    """
    latex = []

    # Main results table
    latex.append("\\begin{table}[h]")
    latex.append("\\centering")
    latex.append("\\caption{A²-Bench Evaluation Results Across Domains}")
    latex.append("\\label{tab:main_results}")
    latex.append("\\begin{tabular}{lcccccc}")
    latex.append("\\toprule")
    latex.append(
        "\\textbf{Domain} & \\textbf{Model} & \\textbf{Func. Success} & \\textbf{Sec. Block} & \\textbf{A²-Score} & \\textbf{Grade} \\\\"
    )
    latex.append("\\midrule")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})
        func_rate = summary.get("functional_success_rate", 0)
        block_rate = summary.get("adversarial_block_rate", 0)
        a2_score = summary.get("overall_a2_score", 0)

        # Grade based on A²-Score
        if a2_score >= 0.9:
            grade = "A+"
        elif a2_score >= 0.8:
            grade = "A"
        elif a2_score >= 0.7:
            grade = "B"
        elif a2_score >= 0.6:
            grade = "C"
        else:
            grade = "F"

        latex.append(
            f"{domain_name.title()} & Dummy & {func_rate:.2f} & {block_rate:.2f} & {a2_score:.3f} & {grade} \\\\"
        )

    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")
    latex.append("")

    # Component scores table
    latex.append("\\begin{table}[h]")
    latex.append("\\centering")
    latex.append("\\caption{Component Score Breakdown for A²-Bench Evaluation}")
    latex.append("\\label{tab:component_scores}")
    latex.append("\\begin{tabular}{lccccc}")
    latex.append("\\toprule")
    latex.append(
        "\\textbf{Domain} & \\textbf{Safety} & \\textbf{Security} & \\textbf{Reliability} & \\textbf{Compliance} & \\textbf{Overall} \\\\"
    )
    latex.append("\\midrule")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        summary = domain_data.get("summary", {})

        latex.append(
            f"{domain_name.title()} & "
            f"{summary.get('safety_score', 0):.3f} & "
            f"{summary.get('security_score', 0):.3f} & "
            f"{summary.get('reliability_score', 0):.3f} & "
            f"{summary.get('compliance_score', 0):.3f} & "
            f"{summary.get('overall_a2_score', 0):.3f} \\\\"
        )

    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")
    latex.append("")

    # Task statistics table
    latex.append("\\begin{table}[h]")
    latex.append("\\centering")
    latex.append("\\caption{Task-Level Performance Statistics}")
    latex.append("\\label{tab:task_stats}")
    latex.append("\\begin{tabular}{lcccc}")
    latex.append("\\toprule")
    latex.append(
        "\\textbf{Domain} & \\textbf{Total Tasks} & \\textbf{Successful} & \\textbf{Blocked} & \\textbf{Success Rate} \\\\"
    )
    latex.append("\\midrule")

    for domain_name, domain_data in results.get("domains", {}).items():
        if "error" in domain_data:
            continue

        func_eval = domain_data.get("functional_evaluation", {})
        adv_eval = domain_data.get("adversarial_evaluation", {})

        total_tasks = func_eval.get("total_tasks", 0) + adv_eval.get("total_tasks", 0)
        successful = func_eval.get("successful_tasks", 0) + adv_eval.get(
            "blocked_tasks", 0
        )
        success_rate = successful / max(1, total_tasks)

        latex.append(
            f"{domain_name.title()} & {total_tasks} & {successful} & {adv_eval.get('blocked_tasks', 0)} & {success_rate:.2f} \\\\"
        )

    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")

    return "\n".join(latex)


def main():
    """Generate detailed results tables."""
    results_dir = "experiments/results"

    try:
        # Load latest results
        results = load_latest_results(results_dir)
        print(f"Loaded results from: {results.get('timestamp', 'unknown')}")

        # Generate markdown tables
        markdown_tables = generate_markdown_tables(results)
        markdown_file = os.path.join(results_dir, "detailed_results_tables.md")

        with open(markdown_file, "w") as f:
            f.write(markdown_tables)

        print(f"Markdown tables saved to: {markdown_file}")

        # Generate LaTeX tables
        latex_tables = generate_latex_tables(results)
        latex_file = os.path.join(results_dir, "results_tables.tex")

        with open(latex_file, "w") as f:
            f.write(latex_tables)

        print(f"LaTeX tables saved to: {latex_file}")

        print("\nTables generated successfully!")

    except Exception as e:
        print(f"Error generating tables: {e}")


if __name__ == "__main__":
    main()
