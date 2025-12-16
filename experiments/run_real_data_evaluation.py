"""Run A2Bench evaluation with real-world datasets."""

import json
import sys
from pathlib import Path
from datetime import datetime
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from a2_bench.benchmark import A2Benchmark
from a2_bench.domains.healthcare.domain import HealthcareDomain
from a2_bench.domains.finance.domain import FinanceDomain
from a2_bench.agents.dummy import DummyAgent
from a2_bench.utils.logging import get_logger

logger = get_logger(__name__)


def load_real_test_cases(domain: str) -> list:
    """Load real-data test cases for a domain."""
    test_file = Path(__file__).parent.parent / "data" / domain / "test_cases_real.json"

    if not test_file.exists():
        logger.warning(f"Real test cases not found: {test_file}")
        return []

    with open(test_file, 'r') as f:
        data = json.load(f)
        return data.get('test_cases', [])


def run_healthcare_evaluation():
    """Run healthcare domain evaluation with real MIMIC-III data."""
    print("\n" + "="*80)
    print("HEALTHCARE DOMAIN - Real Data Evaluation (MIMIC-III)")
    print("="*80)

    # Load real test cases
    test_cases = load_real_test_cases("healthcare")
    print(f"Loaded {len(test_cases)} real-data test cases")

    # Initialize domain
    domain = HealthcareDomain()

    # Initialize benchmark
    benchmark = A2Benchmark(
        domain=domain,
        num_trials=1,
        config={'max_turns': 10}
    )

    # Create dummy agent for baseline evaluation
    agent = DummyAgent(config={'model': 'baseline'})

    # Run evaluation
    print("\nRunning evaluation...")
    start_time = time.time()

    results = benchmark.evaluate(
        agent=agent,
        tasks=test_cases[:10],  # Start with first 10 for testing
        verbose=True
    )

    elapsed = time.time() - start_time

    # Print results
    print("\n" + "-"*80)
    print("RESULTS - Healthcare (Real MIMIC-III Data)")
    print("-"*80)
    print(f"Total test cases: {len(test_cases[:10])}")
    print(f"Evaluation time: {elapsed:.2f}s")
    print(f"\nSafety Score: {results.mean_safety:.3f} (±{results.std_safety:.3f})")
    print(f"Security Score: {results.mean_security:.3f} (±{results.std_security:.3f})")
    print(f"Reliability Score: {results.mean_reliability:.3f} (±{results.std_reliability:.3f})")
    print(f"Compliance Score: {results.mean_compliance:.3f} (±{results.std_compliance:.3f})")
    print(f"Overall A² Score: {results.mean_a2:.3f} (±{results.std_a2:.3f})")
    print(f"\nTotal Violations: {results.total_violations}")
    print(f"Critical Violations: {results.critical_violations}")
    print(f"Task Completion Rate: {results.task_completion_rate:.1%}")

    return {
        'domain': 'healthcare',
        'data_source': 'MIMIC-III Real Clinical Data',
        'test_cases_evaluated': len(test_cases[:10]),
        'results': results.to_dict(),
        'elapsed_time': elapsed
    }


def run_finance_evaluation():
    """Run finance domain evaluation with real credit card fraud data."""
    print("\n" + "="*80)
    print("FINANCE DOMAIN - Real Data Evaluation (Credit Card Fraud 2023)")
    print("="*80)

    # Load real test cases
    test_cases = load_real_test_cases("finance")
    print(f"Loaded {len(test_cases)} real-data test cases")

    # Initialize domain
    domain = FinanceDomain()

    # Initialize benchmark
    benchmark = A2Benchmark(
        domain=domain,
        num_trials=1,
        config={'max_turns': 10}
    )

    # Create dummy agent for baseline evaluation
    agent = DummyAgent(config={'model': 'baseline'})

    # Run evaluation
    print("\nRunning evaluation...")
    start_time = time.time()

    results = benchmark.evaluate(
        agent=agent,
        tasks=test_cases[:10],  # Start with first 10 for testing
        verbose=True
    )

    elapsed = time.time() - start_time

    # Print results
    print("\n" + "-"*80)
    print("RESULTS - Finance (Real Credit Card Data)")
    print("-"*80)
    print(f"Total test cases: {len(test_cases[:10])}")
    print(f"Evaluation time: {elapsed:.2f}s")
    print(f"\nSafety Score: {results.mean_safety:.3f} (±{results.std_safety:.3f})")
    print(f"Security Score: {results.mean_security:.3f} (±{results.std_security:.3f})")
    print(f"Reliability Score: {results.mean_reliability:.3f} (±{results.std_reliability:.3f})")
    print(f"Compliance Score: {results.mean_compliance:.3f} (±{results.std_compliance:.3f})")
    print(f"Overall A² Score: {results.mean_a2:.3f} (±{results.std_a2:.3f})")
    print(f"\nTotal Violations: {results.total_violations}")
    print(f"Critical Violations: {results.critical_violations}")
    print(f"Task Completion Rate: {results.task_completion_rate:.1%}")

    return {
        'domain': 'finance',
        'data_source': 'Kaggle Credit Card Fraud 2023',
        'test_cases_evaluated': len(test_cases[:10]),
        'results': results.to_dict(),
        'elapsed_time': elapsed
    }


def save_results(healthcare_results, finance_results):
    """Save evaluation results to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    results = {
        'evaluation_type': 'real_data',
        'timestamp': timestamp,
        'data_sources': {
            'healthcare': 'MIMIC-III Clinical Database Demo',
            'finance': 'Kaggle Credit Card Fraud Detection 2023'
        },
        'healthcare': healthcare_results,
        'finance': finance_results,
        'summary': {
            'total_test_cases': (
                healthcare_results['test_cases_evaluated'] +
                finance_results['test_cases_evaluated']
            ),
            'total_time': (
                healthcare_results['elapsed_time'] +
                finance_results['elapsed_time']
            ),
            'healthcare_a2_score': healthcare_results['results']['scores']['a2']['mean'],
            'finance_a2_score': finance_results['results']['scores']['a2']['mean'],
            'average_a2_score': (
                healthcare_results['results']['scores']['a2']['mean'] +
                finance_results['results']['scores']['a2']['mean']
            ) / 2
        }
    }

    # Save to file
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / f"real_data_evaluation_{timestamp}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

    return results


def print_summary(results):
    """Print evaluation summary."""
    print("\n" + "="*80)
    print("EVALUATION SUMMARY - Real Open-Source Datasets")
    print("="*80)

    print("\nData Sources:")
    print(f"  Healthcare: {results['data_sources']['healthcare']}")
    print(f"  Finance:    {results['data_sources']['finance']}")

    print(f"\nTotal Test Cases: {results['summary']['total_test_cases']}")
    print(f"Total Evaluation Time: {results['summary']['total_time']:.2f}s")

    print("\nDomain A² Scores:")
    print(f"  Healthcare A² Score: {results['summary']['healthcare_a2_score']:.3f}")
    print(f"  Finance A² Score:    {results['summary']['finance_a2_score']:.3f}")
    print(f"  Average A² Score:    {results['summary']['average_a2_score']:.3f}")

    print("\n" + "="*80)


def main():
    """Main evaluation function."""
    print("="*80)
    print("A2Bench Evaluation with Real Open-Source Datasets")
    print("="*80)
    print("\nThis evaluation uses:")
    print("  - MIMIC-III Clinical Database Demo (real de-identified patient data)")
    print("  - Kaggle Credit Card Fraud Detection 2023 (real anonymized transactions)")
    print("="*80)

    try:
        # Run healthcare evaluation
        healthcare_results = run_healthcare_evaluation()

        # Run finance evaluation
        finance_results = run_finance_evaluation()

        # Save and summarize results
        results = save_results(healthcare_results, finance_results)
        print_summary(results)

        print("\n✓ Evaluation completed successfully!")

        return results

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()
