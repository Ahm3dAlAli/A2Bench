"""
Generate mock results for testing visualizations.

This creates realistic-looking results without running expensive evaluations.
"""

import json
import os
import numpy as np
from datetime import datetime


def generate_mock_results():
    """Generate mock evaluation results."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Mock baseline results
    baseline_results = {
        'GPT-4': {
            'model': 'GPT-4',
            'type': 'baseline',
            'results': {
                'mean_safety': 0.52,
                'mean_security': 0.41,
                'mean_reliability': 0.68,
                'mean_compliance': 0.58,
                'mean_a2': 0.54,
                'std_safety': 0.12,
                'std_security': 0.15,
                'std_reliability': 0.09,
                'std_compliance': 0.11,
                'num_tasks': 100
            }
        },
        'Claude-3.7': {
            'model': 'Claude-3.7',
            'type': 'baseline',
            'results': {
                'mean_safety': 0.58,
                'mean_security': 0.47,
                'mean_reliability': 0.71,
                'mean_compliance': 0.63,
                'mean_a2': 0.59,
                'std_safety': 0.10,
                'std_security': 0.14,
                'std_reliability': 0.08,
                'std_compliance': 0.10,
                'num_tasks': 100
            }
        },
        'O4-Mini': {
            'model': 'O4-Mini',
            'type': 'baseline',
            'results': {
                'mean_safety': 0.47,
                'mean_security': 0.38,
                'mean_reliability': 0.65,
                'mean_compliance': 0.52,
                'mean_a2': 0.50,
                'std_safety': 0.13,
                'std_security': 0.16,
                'std_reliability': 0.10,
                'std_compliance': 0.12,
                'num_tasks': 100
            }
        }
    }

    # Mock adversarial results
    adversarial_results = {}

    strategies = ['social_engineering', 'prompt_injection', 'state_corruption',
                 'constraint_exploitation', 'multi_vector']
    sophistication_levels = [0.3, 0.5, 0.7, 0.9]

    for model_name in ['GPT-4', 'Claude-3.7', 'O4-Mini']:
        model_results = []

        # Base success rates by model and strategy
        base_rates = {
            'GPT-4': {
                'social_engineering': 0.26,
                'prompt_injection': 0.33,
                'state_corruption': 0.19,
                'constraint_exploitation': 0.30,
                'multi_vector': 0.43
            },
            'Claude-3.7': {
                'social_engineering': 0.21,
                'prompt_injection': 0.28,
                'state_corruption': 0.16,
                'constraint_exploitation': 0.25,
                'multi_vector': 0.38
            },
            'O4-Mini': {
                'social_engineering': 0.27,
                'prompt_injection': 0.32,
                'state_corruption': 0.21,
                'constraint_exploitation': 0.29,
                'multi_vector': 0.42
            }
        }

        for strategy in strategies:
            for sophistication in sophistication_levels:
                # Calculate success rate (increases with sophistication)
                base_rate = base_rates[model_name][strategy]
                sophistication_factor = 0.5 + (sophistication * 1.0)  # Scale from 0.5 to 1.5
                success_rate = min(0.95, base_rate * sophistication_factor)

                # Generate 20 episodes per configuration
                num_episodes = 20
                num_successes = int(num_episodes * success_rate)

                model_results.append({
                    'strategy': strategy,
                    'sophistication': sophistication,
                    'results': {
                        'total_episodes': num_episodes,
                        'successful_attacks': num_successes,
                        'attack_success_rate': success_rate,
                        'attack_successful': num_successes > 0,
                        'aggregated_scores': {
                            'safety_score': 1.0 - success_rate * 0.8,
                            'security_score': 1.0 - success_rate,
                            'reliability_score': 0.75,
                            'compliance_score': 0.85,
                            'a2_score': 1.0 - success_rate * 0.7
                        }
                    }
                })

        adversarial_results[model_name] = {
            'model': model_name,
            'type': 'adversarial',
            'results': model_results
        }

    # Combine results
    all_results = {
        'baseline': baseline_results,
        'adversarial': adversarial_results,
        'timestamp': timestamp
    }

    return all_results


def main():
    """Generate and save mock results."""
    os.makedirs('experiments/results', exist_ok=True)

    results = generate_mock_results()

    output_file = os.path.join(
        'experiments/results',
        f"all_results_{results['timestamp']}.json"
    )

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Mock results generated: {output_file}")
    print(f"\nBaseline results for {len(results['baseline'])} models")
    print(f"Adversarial results for {len(results['adversarial'])} models")
    print(f"\nYou can now run: python experiments/generate_figures.py --results-file {os.path.basename(output_file)}")


if __name__ == '__main__':
    main()
