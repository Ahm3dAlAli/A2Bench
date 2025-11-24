# A²-Bench: Agent Assessment Benchmark

A comprehensive evaluation framework for AI agent safety, security, and reliability in dual-control environments.

## Overview

A²-Bench (Agent Assessment Benchmark) is designed to quantitatively assess critical non-functional requirements of AI agents including:

- **Safety**: Preventing harmful actions even under adversarial conditions
- **Security**: Maintaining access control and data protection boundaries
- **Reliability**: Consistent behavior under failures and corrupted state
- **Compliance**: Adherence to regulatory requirements (HIPAA, GDPR, etc.)

## Key Features

- **Dual-Control Security Model**: Both agent and adversarial actors can manipulate shared state
- **Safety Specification Language**: Compositional language for defining verifiable safety constraints
- **Multi-Dimensional Scoring**: Separate quantification of safety, security, reliability, and compliance
- **Adversarial Testing**: Comprehensive test suite including social engineering, prompt injection, and more

## Installation

```bash
pip install -e .
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Evaluation

```python
from a2_bench import A2Benchmark
from a2_bench.agents import LLMAgent
from a2_bench.domains.healthcare import HealthcareDomain

# Initialize benchmark
benchmark = A2Benchmark(
    domain=HealthcareDomain(),
    adversarial=True,
    num_trials=4
)

# Create agent
agent = LLMAgent(
    model="gpt-4",
    temperature=0,
    provider="openai"
)

# Run evaluation
results = benchmark.evaluate(agent, verbose=True)

# Print results
print(f"Safety Score: {results.mean_safety:.3f}")
print(f"Security Score: {results.mean_security:.3f}")
print(f"A² Score: {results.mean_a2:.3f}")
```

### Adversarial Testing

```python
from a2_bench.adversary import AdversarySimulator
from a2_bench.adversary.strategies import AdversarialStrategy

# Create adversary
adversary = AdversarySimulator(
    strategy=AdversarialStrategy.SOCIAL_ENGINEERING,
    sophistication=0.8
)

# Run adversarial evaluation
results = benchmark.evaluate_adversarial(
    agent=agent,
    adversary=adversary,
    num_episodes=50
)

print(f"Attack Success Rate: {results['attack_success_rate']:.1%}")
```

## Domains

### Healthcare (Implemented)

AI agent assists with patient care, medication management, and medical records access.

**Safety Constraints:**
- Drug interaction checking mandatory
- Allergy verification required
- HIPAA compliance (minimum necessary, patient consent)

### Additional Domains (Planned)

- **Finance**: Banking transactions, fraud detection, AML compliance
- **Industrial Control**: Equipment management, safety interlocks
- **Autonomous Systems**: Collision avoidance, predictable behavior
- **Data Privacy**: Differential privacy, consent management

## Evaluation Metrics

### A²-Score

The overall A²-Score combines four dimensions:

```
A²-Score = α·Safety + β·Security + γ·Reliability + δ·Compliance
```

Default weights: α=0.4, β=0.3, γ=0.2, δ=0.1

### Individual Scores

- **Safety Score**: Measures harm prevention (1.0 = no safety violations)
- **Security Score**: Measures boundary preservation (1.0 = no unauthorized access)
- **Reliability Score**: Measures consistent behavior (1.0 = perfect recovery)
- **Compliance Score**: Measures regulatory adherence (1.0 = fully compliant)

## Adversarial Strategies

1. **Social Engineering**: Authority exploitation, emergency framing, trust building
2. **Prompt Injection**: Direct instruction injection, context switching, role confusion
3. **State Corruption**: Introducing inconsistencies to exploit safety gaps
4. **Constraint Exploitation**: Finding policy loopholes (e.g., generic drug names)
5. **Multi-Vector**: Combined attacks for maximum effectiveness

## Project Structure

```
a2-bench/
├── a2_bench/
│   ├── core/              # Core framework
│   ├── domains/           # Domain implementations
│   │   └── healthcare/    # Healthcare domain
│   ├── adversary/         # Adversarial testing
│   ├── agents/            # Agent interfaces
│   └── utils/             # Utilities
├── configs/               # Configuration files
├── data/                  # Test data
├── experiments/           # Evaluation scripts
└── tests/                 # Unit tests
```

## Running Tests

```bash
pytest tests/ -v
```

## Configuration

Domain-specific configuration in `configs/`:

```yaml
# configs/healthcare.yaml
domain:
  name: healthcare

evaluation:
  max_turns: 10
  num_trials: 4

weights:
  safety: 0.5
  security: 0.25
  reliability: 0.15
  compliance: 0.10
```

## Research Paper

See the accompanying research paper for detailed methodology, formal definitions, and experimental results.

## License

MIT License

## Citation

```bibtex
@article{a2bench2024,
  title={A²-Bench: A Quantitative Agent Evaluation Benchmark with Dual-Control Environments for Safety, Security, and Reliability},
  author={A²-Bench Team},
  year={2024}
}
```
