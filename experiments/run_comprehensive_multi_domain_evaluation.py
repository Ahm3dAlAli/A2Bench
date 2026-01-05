#!/usr/bin/env python3
"""
Comprehensive Multi-Domain, Multi-Seed Evaluation for A²-Bench
Evaluates Claude 4.5 Sonnet and GPT-4o across Healthcare, Finance, and Legal domains
Runs 3 seeds for statistical robustness
Generates publication-ready results and visualizations
"""

import os
import json
import argparse
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from a2_bench import A2Benchmark
from a2_bench.agents import LLMAgent, DummyAgent
from a2_bench.domains.healthcare import HealthcareDomain
from a2_bench.domains.finance import FinanceDomain
from a2_bench.domains.legal import LegalDomain
from a2_bench.adversary import AdversarySimulator
from a2_bench.adversary.strategies import AdversarialStrategy
from a2_bench.utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


class ComprehensiveEvaluationRunner:
    """Runs comprehensive multi-domain, multi-seed evaluation."""

    def __init__(self, output_dir: str = "experiments/results/comprehensive", num_seeds: int = 3):
        """Initialize evaluation runner.

        Args:
            output_dir: Directory for results
            num_seeds: Number of random seeds to run
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.num_seeds = num_seeds
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}

    def get_model_configs(self) -> Dict[str, Dict]:
        """Get model configurations for latest models via OpenRouter.

        Returns:
            Dictionary of model configurations
        """
        return {
            # ===== PROPRIETARY MODELS =====
            'gpt-5-mini': {
                'provider': 'openrouter',
                'model_id': 'openai/gpt-5-mini',
                'temperature': 0.0,
                'description': 'GPT-5 Mini (Proprietary)',
                'category': 'proprietary'
            },
            'gpt-5.2': {
                'provider': 'openrouter',
                'model_id': 'openai/gpt-5.2-chat',
                'temperature': 0.0,
                'description': 'GPT-5.2 Chat (Proprietary)',
                'category': 'proprietary'
            },
            'claude-sonnet-4.5': {
                'provider': 'openrouter',
                'model_id': 'anthropic/claude-sonnet-4.5',
                'temperature': 0.0,
                'description': 'Claude Sonnet 4.5 (Proprietary)',
                'category': 'proprietary'
            },
            'claude-haiku-4.5': {
                'provider': 'openrouter',
                'model_id': 'anthropic/claude-haiku-4.5',
                'temperature': 0.0,
                'description': 'Claude Haiku 4.5 (Proprietary)',
                'category': 'proprietary'
            },
            'gemini-3-flash': {
                'provider': 'openrouter',
                'model_id': 'google/gemini-3-flash-preview',
                'temperature': 0.0,
                'description': 'Gemini 3 Flash Preview (Proprietary)',
                'category': 'proprietary'
            },

            # ===== OPEN-SOURCE MODELS =====
            'mistral-large': {
                'provider': 'openrouter',
                'model_id': 'mistralai/mistral-large',
                'temperature': 0.0,
                'description': 'Mistral Large (Open-Source)',
                'category': 'open-source'
            },
            'llama-3.1-70b': {
                'provider': 'openrouter',
                'model_id': 'meta-llama/llama-3.1-70b-instruct',
                'temperature': 0.0,
                'description': 'Llama 3.1 70B (Open-Source)',
                'category': 'open-source'
            },
            'llama-3.3-70b': {
                'provider': 'openrouter',
                'model_id': 'meta-llama/llama-3.3-70b-instruct',
                'temperature': 0.0,
                'description': 'Llama 3.3 70B (Open-Source)',
                'category': 'open-source'
            },
            'deepseek-v3': {
                'provider': 'openrouter',
                'model_id': 'nex-agi/deepseek-v3.1-nex-n1:free',
                'temperature': 0.0,
                'description': 'DeepSeek V3.1 Nex N1 (Open-Source, Free)',
                'category': 'open-source'
            },
            'xiaomi-mimo-v2': {
                'provider': 'openrouter',
                'model_id': 'xiaomi/mimo-v2-flash:free',
                'temperature': 0.0,
                'description': 'Xiaomi Mimo v2 Flash (Open-Source, Free)',
                'category': 'open-source'
            },
            'glm-4.5-air': {
                'provider': 'openrouter',
                'model_id': 'z-ai/glm-4.5-air:free',
                'temperature': 0.0,
                'description': 'GLM 4.5 Air (Open-Source, Free)',
                'category': 'open-source'
            },

            # ===== AGENTIC MODELS (Specialized for Agent Tasks) =====
            'devstral-2512': {
                'provider': 'openrouter',
                'model_id': 'mistralai/devstral-2512:free',
                'temperature': 0.0,
                'description': 'Devstral 2 2512 - 123B agentic coding model (Free)',
                'category': 'agentic',
                'context': '256K',
                'specs': '123B params, dense transformer, 256K context'
            },
            'kat-coder-pro': {
                'provider': 'openrouter',
                'model_id': 'kwaipilot/kat-coder-pro-v1:free',
                'temperature': 0.0,
                'description': 'KAT-Coder-Pro V1 - Agentic coding (73.4% SWE-Bench) (Free)',
                'category': 'agentic',
                'context': '256K',
                'specs': 'Optimized for tool-use, multi-turn interaction'
            },
            'deepseek-r1t2-chimera': {
                'provider': 'openrouter',
                'model_id': 'tngtech/deepseek-r1t2-chimera:free',
                'temperature': 0.0,
                'description': 'DeepSeek R1T2 Chimera - 671B MoE reasoning (Free)',
                'category': 'agentic',
                'context': '164K',
                'specs': '671B MoE, tri-parent merge, 2× faster than R1'
            },
            'deepseek-r1t-chimera': {
                'provider': 'openrouter',
                'model_id': 'tngtech/deepseek-r1t-chimera:free',
                'temperature': 0.0,
                'description': 'DeepSeek R1T Chimera - MoE reasoning (Free)',
                'category': 'agentic',
                'context': '164K',
                'specs': 'R1 + V3 merge, balanced reasoning & efficiency'
            },
            'nemotron-3-nano': {
                'provider': 'openrouter',
                'model_id': 'nvidia/nemotron-3-nano-30b-a3b:free',
                'temperature': 0.0,
                'description': 'NVIDIA Nemotron 3 Nano 30B - Specialized agentic AI (Free)',
                'category': 'agentic',
                'context': '256K',
                'specs': '30B MoE, optimized for agentic systems'
            },

            # ===== ADDITIONAL MODELS (for reference) =====
            'gpt-4': {
                'provider': 'openrouter',
                'model_id': 'openai/gpt-4',
                'temperature': 0.0,
                'description': 'GPT-4 (Proprietary)',
                'category': 'proprietary'
            },
            'claude-4.5-sonnet': {
                'provider': 'openrouter',
                'model_id': 'anthropic/claude-sonnet-4-5',
                'temperature': 0.0,
                'description': 'Claude 4.5 Sonnet (Latest)',
                'category': 'proprietary'
            },
            'gpt-4o': {
                'provider': 'openrouter',
                'model_id': 'openai/gpt-4o',
                'temperature': 0.0,
                'description': 'GPT-4o (Latest)',
                'category': 'proprietary'
            },
            'gpt-4o-mini': {
                'provider': 'openrouter',
                'model_id': 'openai/gpt-4o-mini',
                'temperature': 0.0,
                'description': 'GPT-4o Mini',
                'category': 'proprietary'
            },

            # Test Model
            'dummy': {
                'provider': 'dummy',
                'model_id': 'dummy',
                'description': 'Dummy baseline (for testing)',
                'category': 'test'
            }
        }

    def get_domains(self) -> Dict[str, Any]:
        """Get all domain instances.

        Returns:
            Dictionary of domain instances
        """
        return {
            'healthcare': HealthcareDomain(),
            'finance': FinanceDomain(),
            'legal': LegalDomain()
        }

    def run_domain_evaluation(self,
                             domain_name: str,
                             domain: Any,
                             model_name: str,
                             model_config: Dict,
                             seed: int) -> Dict:
        """Run evaluation for a single domain, model, and seed.

        Args:
            domain_name: Name of domain
            domain: Domain instance
            model_name: Name of model
            model_config: Model configuration
            seed: Random seed

        Returns:
            Results dictionary
        """
        logger.info(f"  Seed {seed}: Evaluating {model_name} on {domain_name}")

        # Set random seed for reproducibility
        np.random.seed(seed)

        # Create benchmark
        benchmark = A2Benchmark(
            domain=domain,
            adversarial=False,
            num_trials=4,
            config={'max_turns': 10, 'seed': seed}
        )

        # Create agent
        if model_config.get('provider') == 'dummy':
            agent = DummyAgent(config={'model': model_name, 'seed': seed})
        else:
            agent = LLMAgent(
                model=model_config['model_id'],
                temperature=model_config.get('temperature', 0.0),
                provider=model_config['provider'],
                config={'model': model_name, 'seed': seed}
            )

        # Get functional tasks
        tasks = domain.get_tasks()
        functional_tasks = [t for t in tasks if not t.get('adversarial', False)]

        try:
            # Run baseline evaluation
            logger.info(f"    Running baseline evaluation ({len(functional_tasks)} tasks)")
            baseline_results = benchmark.evaluate(agent, tasks=functional_tasks, verbose=False)

            # Convert baseline to dict IMMEDIATELY to freeze the values
            baseline_dict = baseline_results.to_dict() if hasattr(baseline_results, 'to_dict') else baseline_results
            logger.info(f"    Baseline complete: {baseline_dict['num_tasks']} tasks, {baseline_dict['overall']['total_violations']} violations")

            # Run adversarial evaluation
            logger.info(f"    Running adversarial evaluation")
            adversarial_results = self.run_adversarial_evaluation(
                domain=domain,
                agent=agent,
                model_name=model_name,
                seed=seed
            )

            return {
                'domain': domain_name,
                'model': model_name,
                'seed': seed,
                'baseline': baseline_dict,
                'adversarial': adversarial_results,
                'success': True
            }

        except Exception as e:
            logger.error(f"    Error in evaluation: {e}")
            return {
                'domain': domain_name,
                'model': model_name,
                'seed': seed,
                'error': str(e),
                'success': False
            }

    def run_adversarial_evaluation(self,
                                  domain: Any,
                                  agent: Any,
                                  model_name: str,
                                  seed: int) -> Dict:
        """Run adversarial evaluation.

        Args:
            domain: Domain instance
            agent: Agent to evaluate
            model_name: Name of model
            seed: Random seed

        Returns:
            Adversarial results
        """
        strategies = [
            AdversarialStrategy.SOCIAL_ENGINEERING,
            AdversarialStrategy.PROMPT_INJECTION,
            AdversarialStrategy.CONSTRAINT_EXPLOITATION,
            AdversarialStrategy.MULTI_VECTOR,
        ]
        sophistication_levels = [0.5, 0.7, 0.9]

        benchmark = A2Benchmark(
            domain=domain,
            adversarial=True,
            num_trials=4,
            config={'max_turns': 10, 'seed': seed}
        )

        all_results = []

        for strategy in strategies:
            for sophistication in sophistication_levels:
                # Create adversary
                adversary = AdversarySimulator(
                    strategy=strategy,
                    sophistication=sophistication,
                    config={'domain': domain.name, 'seed': seed}
                )

                try:
                    # Run adversarial evaluation (reduced episodes for faster testing)
                    results = benchmark.evaluate_adversarial(
                        agent=agent,
                        adversary=adversary,
                        num_episodes=10,
                        verbose=False
                    )

                    all_results.append({
                        'strategy': strategy.value,
                        'sophistication': sophistication,
                        'results': results
                    })

                except Exception as e:
                    logger.error(f"      Error in adversarial eval ({strategy.value}, {sophistication}): {e}")
                    all_results.append({
                        'strategy': strategy.value,
                        'sophistication': sophistication,
                        'error': str(e)
                    })

        return all_results

    def run_full_evaluation(self, models: List[str] = None, domains: List[str] = None) -> Dict:
        """Run full evaluation across all models, domains, and seeds.

        Args:
            models: List of model names to evaluate (None = all)
            domains: List of domain names to evaluate (None = all)

        Returns:
            Complete results dictionary
        """
        all_model_configs = self.get_model_configs()
        all_domains = self.get_domains()

        # Filter models and domains if specified
        if models:
            model_configs = {k: v for k, v in all_model_configs.items() if k in models}
        else:
            model_configs = all_model_configs

        if domains:
            domain_instances = {k: v for k, v in all_domains.items() if k in domains}
        else:
            domain_instances = all_domains

        if not model_configs:
            logger.error(f"No valid models selected")
            return {}

        if not domain_instances:
            logger.error(f"No valid domains selected")
            return {}

        # Initialize results structure
        results = {
            'metadata': {
                'timestamp': self.timestamp,
                'num_seeds': self.num_seeds,
                'models': list(model_configs.keys()),
                'domains': list(domain_instances.keys())
            },
            'results': {}
        }

        # Run evaluation for each combination
        total_runs = len(model_configs) * len(domain_instances) * self.num_seeds
        current_run = 0

        for model_name, model_config in model_configs.items():
            logger.info(f"\n{'='*80}")
            logger.info(f"Model: {model_name} ({model_config['description']})")
            logger.info(f"{'='*80}")

            results['results'][model_name] = {}

            for domain_name, domain in domain_instances.items():
                logger.info(f"\nDomain: {domain_name.upper()}")

                results['results'][model_name][domain_name] = {
                    'seeds': []
                }

                for seed in range(self.num_seeds):
                    current_run += 1
                    logger.info(f"Progress: {current_run}/{total_runs}")

                    seed_results = self.run_domain_evaluation(
                        domain_name=domain_name,
                        domain=domain,
                        model_name=model_name,
                        model_config=model_config,
                        seed=seed
                    )

                    results['results'][model_name][domain_name]['seeds'].append(seed_results)

                # Compute aggregated statistics across seeds
                results['results'][model_name][domain_name]['aggregated'] = \
                    self.aggregate_seed_results(
                        results['results'][model_name][domain_name]['seeds']
                    )

            # Save incremental results after each model completes
            output_file = self.output_dir / f"comprehensive_results_{self.timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"💾 Saved progress: {model_name} complete → {output_file.name}")

        # Save final results
        output_file = self.output_dir / f"comprehensive_results_{self.timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"\n{'='*80}")
        logger.info(f"EVALUATION COMPLETE")
        logger.info(f"Results saved to: {output_file}")
        logger.info(f"{'='*80}")

        return results

    def aggregate_seed_results(self, seed_results: List[Dict]) -> Dict:
        """Aggregate results across multiple seeds.

        Args:
            seed_results: List of results for each seed

        Returns:
            Aggregated statistics
        """
        successful_results = [r for r in seed_results if r.get('success', False)]

        if not successful_results:
            return {'error': 'No successful runs'}

        # Extract baseline scores
        baseline_scores = {
            'safety': [],
            'security': [],
            'reliability': [],
            'compliance': [],
            'a2_score': []
        }

        for result in successful_results:
            baseline = result.get('baseline', {})
            scores = baseline.get('scores', {})
            baseline_scores['safety'].append(scores.get('safety', {}).get('mean', 0))
            baseline_scores['security'].append(scores.get('security', {}).get('mean', 0))
            baseline_scores['reliability'].append(scores.get('reliability', {}).get('mean', 0))
            baseline_scores['compliance'].append(scores.get('compliance', {}).get('mean', 0))
            baseline_scores['a2_score'].append(scores.get('a2', {}).get('mean', 0))

        # Compute mean and std
        aggregated = {}
        for metric, values in baseline_scores.items():
            if values:
                aggregated[f'{metric}_mean'] = float(np.mean(values))
                aggregated[f'{metric}_std'] = float(np.std(values))
                aggregated[f'{metric}_min'] = float(np.min(values))
                aggregated[f'{metric}_max'] = float(np.max(values))

        aggregated['num_seeds'] = len(successful_results)

        return aggregated

    def generate_summary_table(self, results: Dict) -> str:
        """Generate LaTeX summary table.

        Args:
            results: Evaluation results

        Returns:
            LaTeX table string
        """
        latex = []
        latex.append("\\begin{table*}[t]")
        latex.append("\\centering")
        latex.append("\\caption{A²-Bench Evaluation Results Across Domains and Models (Mean ± Std over 3 seeds)}")
        latex.append("\\label{tab:comprehensive_results}")
        latex.append("\\begin{tabular}{llcccccc}")
        latex.append("\\toprule")
        latex.append("\\textbf{Domain} & \\textbf{Model} & \\textbf{Safety} & \\textbf{Security} & \\textbf{Reliability} & \\textbf{Compliance} & \\textbf{A²-Score} & \\textbf{Seeds} \\\\")
        latex.append("\\midrule")

        model_results = results.get('results', {})

        for model_name in sorted(model_results.keys()):
            for domain_name in sorted(model_results[model_name].keys()):
                agg = model_results[model_name][domain_name].get('aggregated', {})

                if 'error' not in agg:
                    safety_mean = agg.get('safety_mean', 0)
                    safety_std = agg.get('safety_std', 0)
                    security_mean = agg.get('security_mean', 0)
                    security_std = agg.get('security_std', 0)
                    reliability_mean = agg.get('reliability_mean', 0)
                    reliability_std = agg.get('reliability_std', 0)
                    compliance_mean = agg.get('compliance_mean', 0)
                    compliance_std = agg.get('compliance_std', 0)
                    a2_mean = agg.get('a2_score_mean', 0)
                    a2_std = agg.get('a2_score_std', 0)
                    num_seeds = agg.get('num_seeds', 0)

                    latex.append(
                        f"{domain_name.capitalize()} & {model_name} & "
                        f"{safety_mean:.2f}±{safety_std:.2f} & "
                        f"{security_mean:.2f}±{security_std:.2f} & "
                        f"{reliability_mean:.2f}±{reliability_std:.2f} & "
                        f"{compliance_mean:.2f}±{compliance_std:.2f} & "
                        f"{a2_mean:.2f}±{a2_std:.2f} & "
                        f"{num_seeds} \\\\"
                    )

        latex.append("\\bottomrule")
        latex.append("\\end{tabular}")
        latex.append("\\end{table*}")

        return "\n".join(latex)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive multi-domain, multi-seed A²-Bench evaluation"
    )
    parser.add_argument(
        '--models',
        nargs='+',
        default=['claude-4.5-sonnet', 'gpt-4o'],
        help='Models to evaluate (default: claude-4.5-sonnet gpt-4o)'
    )
    parser.add_argument(
        '--domains',
        nargs='+',
        default=['healthcare', 'finance', 'legal'],
        help='Domains to evaluate (default: all)'
    )
    parser.add_argument(
        '--num-seeds',
        type=int,
        default=3,
        help='Number of random seeds (default: 3)'
    )
    parser.add_argument(
        '--output-dir',
        default='experiments/results/comprehensive',
        help='Output directory for results'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Test mode: use dummy model only'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(level=log_level)

    # Override models in test mode
    if args.test_mode:
        args.models = ['dummy']
        logger.info("Test mode: using dummy model only")

    # Create runner
    runner = ComprehensiveEvaluationRunner(
        output_dir=args.output_dir,
        num_seeds=args.num_seeds
    )

    # Run evaluation
    logger.info(f"\n{'='*80}")
    logger.info("A²-Bench Comprehensive Evaluation")
    logger.info(f"Models: {', '.join(args.models)}")
    logger.info(f"Domains: {', '.join(args.domains)}")
    logger.info(f"Seeds: {args.num_seeds}")
    logger.info(f"{'='*80}\n")

    results = runner.run_full_evaluation(
        models=args.models,
        domains=args.domains
    )

    # Generate and print summary table
    latex_table = runner.generate_summary_table(results)
    logger.info("\n" + "="*80)
    logger.info("LaTeX Summary Table:")
    logger.info("="*80)
    logger.info(latex_table)

    # Save table to file
    table_file = runner.output_dir / f"summary_table_{runner.timestamp}.tex"
    with open(table_file, 'w') as f:
        f.write(latex_table)
    logger.info(f"\nTable saved to: {table_file}")


if __name__ == '__main__':
    main()
