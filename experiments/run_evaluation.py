"""
Experiment runner for A²-Bench evaluation.

This script runs comprehensive evaluations across multiple models and generates
results, figures, and tables for the paper.
"""

import os
import json
import argparse
from typing import Dict, List
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from a2_bench import A2Benchmark
from a2_bench.agents import LLMAgent, DummyAgent
from a2_bench.domains.healthcare import HealthcareDomain
from a2_bench.adversary import AdversarySimulator
from a2_bench.adversary.strategies import AdversarialStrategy
from a2_bench.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


class ExperimentRunner:
    """Runs A²-Bench experiments and collects results."""

    def __init__(self, output_dir: str = "experiments/results"):
        """Initialize experiment runner.

        Args:
            output_dir: Directory for results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

    def run_baseline_evaluation(self, model_name: str, model_config: Dict) -> Dict:
        """Run baseline (non-adversarial) evaluation.

        Args:
            model_name: Name of model
            model_config: Model configuration

        Returns:
            Results dictionary
        """
        logger.info(f"Running baseline evaluation for {model_name}")

        # Create domain and benchmark
        domain = HealthcareDomain()
        benchmark = A2Benchmark(
            domain=domain,
            adversarial=False,
            num_trials=4,
            config={'max_turns': 10}
        )

        # Create agent
        if model_config.get('provider') == 'dummy':
            agent = DummyAgent(config={'model': model_name})
        else:
            agent = LLMAgent(
                model=model_config['model_id'],
                temperature=model_config.get('temperature', 0.0),
                provider=model_config['provider'],
                config={'model': model_name}
            )

        # Get tasks
        tasks = domain.get_tasks()
        functional_tasks = [t for t in tasks if not t.get('adversarial', False)]

        # Run evaluation
        logger.info(f"Evaluating {len(functional_tasks)} functional tasks")
        results = benchmark.evaluate(agent, tasks=functional_tasks, verbose=True)

        # Save results
        output_file = os.path.join(
            self.output_dir,
            f"{model_name}_baseline_{self.timestamp}.json"
        )
        benchmark.export_results(output_file)

        return {
            'model': model_name,
            'type': 'baseline',
            'results': results.to_dict(),
            'output_file': output_file
        }

    def run_adversarial_evaluation(self,
                                   model_name: str,
                                   model_config: Dict,
                                   strategies: List[AdversarialStrategy] = None,
                                   sophistication_levels: List[float] = None) -> Dict:
        """Run adversarial evaluation.

        Args:
            model_name: Name of model
            model_config: Model configuration
            strategies: List of adversarial strategies
            sophistication_levels: List of sophistication levels

        Returns:
            Results dictionary
        """
        logger.info(f"Running adversarial evaluation for {model_name}")

        strategies = strategies or [
            AdversarialStrategy.SOCIAL_ENGINEERING,
            AdversarialStrategy.PROMPT_INJECTION,
            AdversarialStrategy.CONSTRAINT_EXPLOITATION,
            AdversarialStrategy.MULTI_VECTOR,
        ]
        sophistication_levels = sophistication_levels or [0.3, 0.5, 0.7, 0.9]

        # Create domain and benchmark
        domain = HealthcareDomain()
        benchmark = A2Benchmark(
            domain=domain,
            adversarial=True,
            num_trials=4,
            config={'max_turns': 10}
        )

        # Create agent
        if model_config.get('provider') == 'dummy':
            agent = DummyAgent(config={'model': model_name})
        else:
            agent = LLMAgent(
                model=model_config['model_id'],
                temperature=model_config.get('temperature', 0.0),
                provider=model_config['provider'],
                config={'model': model_name}
            )

        all_results = []

        # Test each strategy at each sophistication level
        for strategy in strategies:
            for sophistication in sophistication_levels:
                logger.info(f"  Strategy: {strategy.value}, Sophistication: {sophistication}")

                # Create adversary
                adversary = AdversarySimulator(
                    strategy=strategy,
                    sophistication=sophistication,
                    config={'domain': 'healthcare'}
                )

                # Run adversarial evaluation
                results = benchmark.evaluate_adversarial(
                    agent=agent,
                    adversary=adversary,
                    num_episodes=20,
                    verbose=False
                )

                all_results.append({
                    'strategy': strategy.value,
                    'sophistication': sophistication,
                    'results': results
                })

        # Save results
        output_file = os.path.join(
            self.output_dir,
            f"{model_name}_adversarial_{self.timestamp}.json"
        )

        with open(output_file, 'w') as f:
            json.dump({
                'model': model_name,
                'timestamp': self.timestamp,
                'results': all_results
            }, f, indent=2, default=str)

        return {
            'model': model_name,
            'type': 'adversarial',
            'results': all_results,
            'output_file': output_file
        }

    def run_full_evaluation(self, models: Dict[str, Dict]) -> Dict:
        """Run full evaluation suite across all models.

        Args:
            models: Dictionary of model configurations

        Returns:
            All results
        """
        all_results = {
            'baseline': {},
            'adversarial': {},
            'timestamp': self.timestamp
        }

        for model_name, model_config in models.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Evaluating model: {model_name}")
            logger.info(f"{'='*60}\n")

            try:
                # Baseline evaluation
                baseline_results = self.run_baseline_evaluation(model_name, model_config)
                all_results['baseline'][model_name] = baseline_results

                # Adversarial evaluation
                adversarial_results = self.run_adversarial_evaluation(model_name, model_config)
                all_results['adversarial'][model_name] = adversarial_results

            except Exception as e:
                logger.error(f"Error evaluating {model_name}: {e}")
                all_results['baseline'][model_name] = {'error': str(e)}
                all_results['adversarial'][model_name] = {'error': str(e)}

        # Save combined results
        output_file = os.path.join(
            self.output_dir,
            f"all_results_{self.timestamp}.json"
        )

        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)

        logger.info(f"\nAll results saved to: {output_file}")
        return all_results

    def generate_summary_table(self, results: Dict) -> str:
        """Generate LaTeX summary table.

        Args:
            results: Evaluation results

        Returns:
            LaTeX table string
        """
        latex = []
        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{A²-Bench scores across models.}")
        latex.append("\\begin{tabular}{lcccccc}")
        latex.append("\\toprule")
        latex.append("\\textbf{Model} & \\textbf{Safety} & \\textbf{Security} & \\textbf{Reliability} & \\textbf{Compliance} & \\textbf{A²-Score} \\\\")
        latex.append("\\midrule")

        for model_name, model_results in results.get('baseline', {}).items():
            if 'error' in model_results:
                continue

            scores = model_results.get('results', {})
            latex.append(f"{model_name} & {scores.get('mean_safety', 0):.2f} & {scores.get('mean_security', 0):.2f} & {scores.get('mean_reliability', 0):.2f} & {scores.get('mean_compliance', 0):.2f} & {scores.get('mean_a2', 0):.2f} \\\\")

        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        latex.append("\\end{table}")

        return "\n".join(latex)


def main():
    """Main experiment runner."""
    parser = argparse.ArgumentParser(description="Run A²-Bench experiments")
    parser.add_argument('--models', nargs='+', default=['dummy'],
                       help='Models to evaluate (dummy, gpt4, claude, o4mini)')
    parser.add_argument('--baseline-only', action='store_true',
                       help='Run only baseline evaluation')
    parser.add_argument('--adversarial-only', action='store_true',
                       help='Run only adversarial evaluation')
    parser.add_argument('--output-dir', default='experiments/results',
                       help='Output directory')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(level=log_level)

    # Define model configurations
    model_configs = {
        'dummy': {
            'provider': 'dummy',
            'model_id': 'dummy',
        },
        'gpt4': {
            'provider': 'openai',
            'model_id': 'gpt-4-0125-preview',
            'temperature': 0.0,
        },
        'claude': {
            'provider': 'anthropic',
            'model_id': 'claude-3-sonnet-20240229',
            'temperature': 0.0,
        },
        'o4mini': {
            'provider': 'openai',
            'model_id': 'o4-mini-2024-04-15',
            'temperature': 0.0,
        }
    }

    # Select models
    selected_models = {
        name: config for name, config in model_configs.items()
        if name in args.models
    }

    if not selected_models:
        logger.error(f"No valid models selected from: {args.models}")
        return

    # Create runner
    runner = ExperimentRunner(output_dir=args.output_dir)

    # Run experiments
    if args.baseline_only:
        for model_name, model_config in selected_models.items():
            runner.run_baseline_evaluation(model_name, model_config)
    elif args.adversarial_only:
        for model_name, model_config in selected_models.items():
            runner.run_adversarial_evaluation(model_name, model_config)
    else:
        results = runner.run_full_evaluation(selected_models)

        # Generate summary
        logger.info("\n" + "="*60)
        logger.info("EVALUATION COMPLETE")
        logger.info("="*60)

        # Print LaTeX table
        latex_table = runner.generate_summary_table(results)
        logger.info("\nLaTeX Table:")
        logger.info(latex_table)


if __name__ == '__main__':
    main()
