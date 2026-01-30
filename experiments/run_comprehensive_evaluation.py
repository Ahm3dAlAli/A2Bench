"""
Comprehensive experiment runner for A²-Bench evaluation across multiple domains.
This script runs experiments for both healthcare and finance domains.
"""

import os
import json
import argparse
from typing import Dict, List
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from a2_bench import A2Benchmark
from a2_bench.agents import LLMAgent
from a2_bench.domains.healthcare import HealthcareDomain
from a2_bench.domains.finance import FinanceDomain
from a2_bench.adversary import AdversarySimulator
from a2_bench.adversary.strategies import AdversarialStrategy
from a2_bench.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


class MultiDomainExperimentRunner:
    """Runs A²-Bench experiments across multiple domains."""

    def __init__(self, output_dir: str = "experiments/results"):
        """Initialize experiment runner.

        Args:
            output_dir: Directory for results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

        # Initialize domains
        self.healthcare_domain = HealthcareDomain()
        self.finance_domain = FinanceDomain()

    def run_domain_evaluation(
        self,
        domain_name: str,
        domain,
        model_name: str,
        model_config: Dict,
        evaluation_type: str = "full",
    ) -> Dict:
        """Run evaluation for a specific domain.

        Args:
            domain_name: Name of domain (healthcare/finance)
            domain: Domain instance
            model_name: Name of model to evaluate
            model_config: Model configuration
            evaluation_type: Type of evaluation (baseline/adversarial/full)

        Returns:
            Results dictionary
        """
        logger.info(
            f"Running {evaluation_type} evaluation for {domain_name} domain with {model_name}"
        )

        results = {
            "domain": domain_name,
            "model": model_name,
            "evaluation_type": evaluation_type,
            "timestamp": self.timestamp,
        }

        if evaluation_type in ["baseline", "full"]:
            # Run baseline evaluation
            baseline_results = self._run_baseline(domain, model_name, model_config)
            results["baseline"] = baseline_results

        if evaluation_type in ["adversarial", "full"]:
            # Run adversarial evaluation
            adversarial_results = self._run_adversarial(
                domain, model_name, model_config
            )
            results["adversarial"] = adversarial_results

        # Save domain-specific results
        output_file = os.path.join(
            self.output_dir,
            f"{domain_name}_{model_name}_{evaluation_type}_{self.timestamp}.json",
        )

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        results["output_file"] = output_file
        return results

    def _run_baseline(self, domain, model_name: str, model_config: Dict) -> Dict:
        """Run baseline evaluation."""
        benchmark = A2Benchmark(
            domain=domain, adversarial=False, num_trials=4, config={"max_turns": 10}
        )

        # Create agent
        agent = LLMAgent(
            model=model_config["model_id"],
            temperature=model_config.get("temperature", 0.0),
            provider=model_config["provider"],
            config={"model": model_name},
        )

        # Get functional tasks
        tasks = domain.get_tasks()
        functional_tasks = [t for t in tasks if not t.get("adversarial", False)]

        logger.info(f"Evaluating {len(functional_tasks)} functional tasks")
        results = benchmark.evaluate(agent, tasks=functional_tasks, verbose=False)

        return results.to_dict()

    def _run_adversarial(self, domain, model_name: str, model_config: Dict) -> Dict:
        """Run adversarial evaluation."""
        strategies = [
            AdversarialStrategy.SOCIAL_ENGINEERING,
            AdversarialStrategy.PROMPT_INJECTION,
            AdversarialStrategy.CONSTRAINT_EXPLOITATION,
            AdversarialStrategy.MULTI_VECTOR,
        ]
        sophistication_levels = [0.3, 0.5, 0.7, 0.9]

        benchmark = A2Benchmark(
            domain=domain, adversarial=True, num_trials=4, config={"max_turns": 10}
        )

        # Create agent
        agent = LLMAgent(
            model=model_config["model_id"],
            temperature=model_config.get("temperature", 0.0),
            provider=model_config["provider"],
            config={"model": model_name},
        )

        all_results = []

        # Test each strategy at each sophistication level
        for strategy in strategies:
            for sophistication in sophistication_levels:
                logger.info(
                    f"  Strategy: {strategy.value}, Sophistication: {sophistication}"
                )

                # Create adversary
                domain_name = domain.name.lower()
                adversary = AdversarySimulator(
                    strategy=strategy,
                    sophistication=sophistication,
                    config={"domain": domain_name},
                )

                # Run adversarial evaluation
                results = benchmark.evaluate_adversarial(
                    agent=agent, adversary=adversary, num_episodes=20, verbose=False
                )

                all_results.append(
                    {
                        "strategy": strategy.value,
                        "sophistication": sophistication,
                        "results": results,
                    }
                )

        return all_results

    def run_comprehensive_evaluation(
        self, models: Dict[str, Dict], domains: List[str] = None
    ) -> Dict:
        """Run comprehensive evaluation across specified domains.

        Args:
            models: Dictionary of model configurations
            domains: List of domains to evaluate (default: all)

        Returns:
            All results
        """
        domains = domains or ["healthcare", "finance"]
        all_results = {
            "domains": {},
            "timestamp": self.timestamp,
            "models_evaluated": list(models.keys()),
            "domains_evaluated": domains,
        }

        for domain_name in domains:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"EVALUATING DOMAIN: {domain_name.upper()}")
            logger.info(f"{'=' * 60}\n")

            domain_results = {}
            domain = getattr(self, f"{domain_name}_domain")

            for model_name, model_config in models.items():
                logger.info(f"\n{'-' * 40}")
                logger.info(f"Evaluating model: {model_name}")
                logger.info(f"{'-' * 40}\n")

                try:
                    # Run full evaluation for this model and domain
                    model_results = self.run_domain_evaluation(
                        domain_name, domain, model_name, model_config, "full"
                    )
                    domain_results[model_name] = model_results

                except Exception as e:
                    logger.error(f"Error evaluating {model_name} on {domain_name}: {e}")
                    domain_results[model_name] = {"error": str(e)}

            all_results["domains"][domain_name] = domain_results

        # Save combined results
        output_file = os.path.join(
            self.output_dir, f"comprehensive_results_{self.timestamp}.json"
        )

        with open(output_file, "w") as f:
            json.dump(all_results, f, indent=2, default=str)

        logger.info(f"\nAll comprehensive results saved to: {output_file}")
        return all_results

    def generate_comparison_tables(self, results: Dict) -> str:
        """Generate comparison tables across domains and models.

        Args:
            results: Comprehensive evaluation results

        Returns:
            Markdown table string
        """
        tables = []

        # Generate summary table
        tables.append("# A²-Bench Comprehensive Results Summary\n")
        tables.append("## Domain Performance Comparison\n")

        # Create comparison table
        tables.append(
            "| Model | Domain | Safety | Security | Reliability | Compliance | A²-Score |"
        )
        tables.append(
            "|-------|--------|--------|----------|-------------|------------|----------|"
        )

        for domain_name, domain_data in results.get("domains", {}).items():
            for model_name, model_data in domain_data.items():
                if "error" in model_data:
                    continue

                baseline = model_data.get("baseline", {})
                tables.append(
                    f"| {model_name} | {domain_name.title()} | "
                    f"{baseline.get('mean_safety', 0):.3f} | "
                    f"{baseline.get('mean_security', 0):.3f} | "
                    f"{baseline.get('mean_reliability', 0):.3f} | "
                    f"{baseline.get('mean_compliance', 0):.3f} | "
                    f"{baseline.get('mean_a2', 0):.3f} |"
                )

        # Adversarial resilience table
        tables.append("\n## Adversarial Resilience Comparison\n")
        tables.append(
            "| Model | Domain | Social Engineering | Prompt Injection | Constraint Exploitation | Multi-Vector |"
        )
        tables.append(
            "|-------|--------|-------------------|------------------|------------------------|--------------|"
        )

        for domain_name, domain_data in results.get("domains", {}).items():
            for model_name, model_data in domain_data.items():
                if "error" in model_data or "adversarial" not in model_data:
                    continue

                adv_results = model_data["adversarial"]
                strategy_scores = {}

                for result in adv_results:
                    strategy = result["strategy"]
                    strategy_results = result["results"]

                    # Calculate average success rate for this strategy
                    episodes = strategy_results.get("episodes", [])
                    if episodes:
                        blocked_count = sum(
                            1 for ep in episodes if ep.get("blocked", False)
                        )
                        success_rate = blocked_count / len(episodes)
                        strategy_scores[strategy] = success_rate

                tables.append(
                    f"| {model_name} | {domain_name.title()} | "
                    f"{strategy_scores.get('social_engineering', 0):.3f} | "
                    f"{strategy_scores.get('prompt_injection', 0):.3f} | "
                    f"{strategy_scores.get('constraint_exploitation', 0):.3f} | "
                    f"{strategy_scores.get('multi_vector', 0):.3f} |"
                )

        return "\n".join(tables)

    def generate_latex_tables(self, results: Dict) -> str:
        """Generate LaTeX tables for paper inclusion.

        Args:
            results: Comprehensive evaluation results

        Returns:
            LaTeX table string
        """
        latex = []

        # Main results table
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{A²-Bench scores across domains and models.}")
        latex.append("\\begin{tabular}{lccccc}")
        latex.append("\\toprule")
        latex.append(
            "\\textbf{Model} & \\textbf{Domain} & \\textbf{Safety} & \\textbf{Security} & \\textbf{Reliability} & \\textbf{A²-Score} \\\\"
        )
        latex.append("\\midrule")

        for domain_name, domain_data in results.get("domains", {}).items():
            for model_name, model_data in domain_data.items():
                if "error" in model_data:
                    continue

                baseline = model_data.get("baseline", {})
                domain_display = domain_name.title()

                latex.append(
                    f"{model_name} & {domain_display} & "
                    f"{baseline.get('mean_safety', 0):.2f} & "
                    f"{baseline.get('mean_security', 0):.2f} & "
                    f"{baseline.get('mean_reliability', 0):.2f} & "
                    f"{baseline.get('mean_a2', 0):.2f} \\\\"
                )

        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        # Adversarial resilience table
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{Adversarial attack resilience across domains.}")
        latex.append("\\begin{tabular}{lccc}")
        latex.append("\\toprule")
        latex.append(
            "\\textbf{Domain} & \\textbf{Social Eng.} & \\textbf{Prompt Inj.} & \\textbf{Constraint Exp.} \\\\"
        )
        latex.append("\\midrule")

        for domain_name, domain_data in results.get("domains", {}).items():
            # Calculate average resilience for this domain across all models
            strategy_scores = {
                "social_engineering": [],
                "prompt_injection": [],
                "constraint_exploitation": [],
            }

            for model_name, model_data in domain_data.items():
                if "adversarial" not in model_data:
                    continue

                adv_results = model_data["adversarial"]
                for result in adv_results:
                    strategy = result["strategy"]
                    if strategy in strategy_scores:
                        strategy_results = result["results"]
                        episodes = strategy_results.get("episodes", [])
                        if episodes:
                            blocked_count = sum(
                                1 for ep in episodes if ep.get("blocked", False)
                            )
                            success_rate = blocked_count / len(episodes)
                            strategy_scores[strategy].append(success_rate)

            # Calculate averages
            avg_scores = {
                k: sum(v) / len(v) if v else 0 for k, v in strategy_scores.items()
            }

            latex.append(
                f"{domain_name.title()} & "
                f"{avg_scores['social_engineering']:.2f} & "
                f"{avg_scores['prompt_injection']:.2f} & "
                f"{avg_scores['constraint_exploitation']:.2f} \\\\"
            )

        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        return "\n\n".join(latex)


def main():
    """Main experiment runner."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive A²-Bench experiments"
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=["dummy"],
        help="Models to evaluate (dummy, gpt4, claude, o4mini)",
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        default=["healthcare", "finance"],
        help="Domains to evaluate (healthcare, finance)",
    )
    parser.add_argument(
        "--baseline-only", action="store_true", help="Run only baseline evaluation"
    )
    parser.add_argument(
        "--adversarial-only",
        action="store_true",
        help="Run only adversarial evaluation",
    )
    parser.add_argument(
        "--output-dir", default="experiments/results", help="Output directory"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)

    # Define model configurations
    model_configs = {
        "dummy": {
            "provider": "dummy",
            "model_id": "dummy",
        },
        "gpt4": {
            "provider": "openai",
            "model_id": "gpt-4-0125-preview",
            "temperature": 0.0,
        },
        "claude": {
            "provider": "anthropic",
            "model_id": "claude-3-sonnet-20240229",
            "temperature": 0.0,
        },
        "o4mini": {
            "provider": "openai",
            "model_id": "o4-mini-2024-04-15",
            "temperature": 0.0,
        },
    }

    # Select models
    selected_models = {
        name: config for name, config in model_configs.items() if name in args.models
    }

    if not selected_models:
        logger.error(f"No valid models selected from: {args.models}")
        return

    # Create runner
    runner = MultiDomainExperimentRunner(output_dir=args.output_dir)

    # Run experiments
    evaluation_type = (
        "baseline"
        if args.baseline_only
        else ("adversarial" if args.adversarial_only else "full")
    )

    if len(args.domains) == 1:
        # Single domain evaluation
        domain_name = args.domains[0]
        domain = getattr(runner, f"{domain_name}_domain")

        for model_name, model_config in selected_models.items():
            runner.run_domain_evaluation(
                domain_name, domain, model_name, model_config, evaluation_type
            )
    else:
        # Multi-domain comprehensive evaluation
        if evaluation_type == "full":
            results = runner.run_comprehensive_evaluation(selected_models, args.domains)

            # Generate comparison tables
            logger.info("\n" + "=" * 60)
            logger.info("COMPREHENSIVE EVALUATION COMPLETE")
            logger.info("=" * 60)

            # Print markdown tables
            markdown_tables = runner.generate_comparison_tables(results)
            logger.info("\nMarkdown Tables:")
            logger.info(markdown_tables)

            # Print LaTeX tables
            latex_tables = runner.generate_latex_tables(results)
            logger.info("\nLaTeX Tables:")
            logger.info(latex_tables)
        else:
            # Run single evaluation type for all domains
            for domain_name in args.domains:
                domain = getattr(runner, f"{domain_name}_domain")
                for model_name, model_config in selected_models.items():
                    runner.run_domain_evaluation(
                        domain_name, domain, model_name, model_config, evaluation_type
                    )


if __name__ == "__main__":
    main()
