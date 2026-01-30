#!/usr/bin/env python3
"""
A²-Bench CLI - Command-line interface for running agent evaluations.
"""

import argparse
import json
import sys
from pathlib import Path

from a2_bench import A2Benchmark
from a2_bench.agents import LLMAgent, DummyAgent
from a2_bench.domains.healthcare import HealthcareDomain
from a2_bench.domains.finance import FinanceDomain
from a2_bench.domains.legal import LegalDomain


DOMAINS = {
    "healthcare": HealthcareDomain,
    "finance": FinanceDomain,
    "legal": LegalDomain,
}


def get_agent(model: str, provider: str = "openrouter"):
    """Create an agent from model name and provider."""
    if model == "dummy":
        return DummyAgent()
    return LLMAgent(model=model, provider=provider, config={"temperature": 0.0})


def cmd_evaluate(args):
    """Run evaluation on a single domain."""
    domain_cls = DOMAINS.get(args.domain)
    if domain_cls is None:
        print(f"Unknown domain: {args.domain}. Available: {list(DOMAINS.keys())}")
        sys.exit(1)

    domain = domain_cls()
    agent = get_agent(args.model, args.provider)
    benchmark = A2Benchmark(domain=domain, num_trials=args.trials)

    print(f"Evaluating {args.model} on {args.domain} ({args.trials} trials)")
    results = benchmark.evaluate(agent, verbose=args.verbose)

    print(f"\nResults for {args.model} on {args.domain}:")
    print(f"  A²-Score:    {results.mean_a2:.3f}")
    print(f"  Safety:      {results.mean_safety:.3f}")
    print(f"  Security:    {results.mean_security:.3f}")
    print(f"  Reliability: {results.mean_reliability:.3f}")
    print(f"  Compliance:  {results.mean_compliance:.3f}")

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results.to_dict() if hasattr(results, "to_dict") else str(results), f, indent=2)
        print(f"\nResults saved to {output_path}")


def cmd_adversarial(args):
    """Run adversarial evaluation."""
    from a2_bench.adversary import AdversarySimulator
    from a2_bench.adversary.strategies import AdversarialStrategy

    domain_cls = DOMAINS.get(args.domain)
    if domain_cls is None:
        print(f"Unknown domain: {args.domain}. Available: {list(DOMAINS.keys())}")
        sys.exit(1)

    domain = domain_cls()
    agent = get_agent(args.model, args.provider)
    benchmark = A2Benchmark(domain=domain, adversarial=True)

    strategy_map = {
        "social_engineering": AdversarialStrategy.SOCIAL_ENGINEERING,
        "prompt_injection": AdversarialStrategy.PROMPT_INJECTION,
        "constraint_exploitation": AdversarialStrategy.CONSTRAINT_EXPLOITATION,
        "state_corruption": AdversarialStrategy.STATE_CORRUPTION,
        "multi_vector": AdversarialStrategy.MULTI_VECTOR,
    }

    strategy = strategy_map.get(args.strategy)
    if strategy is None:
        print(f"Unknown strategy: {args.strategy}. Available: {list(strategy_map.keys())}")
        sys.exit(1)

    adversary = AdversarySimulator(strategy=strategy, sophistication=args.sophistication)

    print(f"Adversarial evaluation: {args.model} on {args.domain}")
    print(f"  Strategy: {args.strategy}, Sophistication: {args.sophistication}")

    results = benchmark.evaluate_adversarial(agent, adversary, num_episodes=args.episodes, verbose=args.verbose)

    print(f"\nDefense rate: {results.get('defense_rate', 'N/A')}")


def cmd_list_domains(args):
    """List available domains."""
    for name, cls in DOMAINS.items():
        domain = cls()
        tasks = domain.get_tasks()
        adv = domain.get_adversarial_scenarios()
        print(f"  {name}: {len(tasks)} tasks, {len(adv)} adversarial scenarios")


def main():
    parser = argparse.ArgumentParser(
        prog="a2-bench",
        description="A²-Bench: Agent Assessment Benchmark CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # evaluate
    eval_parser = subparsers.add_parser("evaluate", help="Run baseline evaluation")
    eval_parser.add_argument("--model", required=True, help="Model name (e.g., gpt-4o, claude-3-5-sonnet, dummy)")
    eval_parser.add_argument("--domain", required=True, choices=list(DOMAINS.keys()), help="Evaluation domain")
    eval_parser.add_argument("--provider", default="openrouter", help="API provider (openai, anthropic, openrouter)")
    eval_parser.add_argument("--trials", type=int, default=1, help="Number of trials")
    eval_parser.add_argument("--output", help="Output JSON file path")
    eval_parser.add_argument("--verbose", action="store_true")
    eval_parser.set_defaults(func=cmd_evaluate)

    # adversarial
    adv_parser = subparsers.add_parser("adversarial", help="Run adversarial evaluation")
    adv_parser.add_argument("--model", required=True, help="Model name")
    adv_parser.add_argument("--domain", required=True, choices=list(DOMAINS.keys()))
    adv_parser.add_argument("--provider", default="openrouter")
    adv_parser.add_argument("--strategy", default="social_engineering",
                            choices=["social_engineering", "prompt_injection", "constraint_exploitation",
                                     "state_corruption", "multi_vector"])
    adv_parser.add_argument("--sophistication", type=float, default=0.7, help="Attack sophistication 0.0-1.0")
    adv_parser.add_argument("--episodes", type=int, default=10, help="Number of episodes")
    adv_parser.add_argument("--verbose", action="store_true")
    adv_parser.set_defaults(func=cmd_adversarial)

    # list
    list_parser = subparsers.add_parser("list", help="List available domains and tasks")
    list_parser.set_defaults(func=cmd_list_domains)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
