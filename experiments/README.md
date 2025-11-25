# A²-Bench Experiments

This directory contains scripts for running evaluations and generating figures for the A²-Bench paper.

## Quick Start

### 1. Generate Mock Results (for testing)

```bash
# Generate mock results without running expensive evaluations
python experiments/generate_mock_results.py
```

### 2. Generate Figures

```bash
# Generate all paper figures from mock results
python experiments/generate_figures.py
```

Figures will be saved to `experiments/figures/`:
- `main_scores.pdf` - Main A²-Bench scores comparison
- `attack_success_heatmap.pdf` - Attack success rates by strategy
- `attack_success_by_sophistication.pdf` - Success rate vs sophistication level
- `violation_breakdown.pdf` - Distribution of violation types

### 3. Run Real Evaluations

**Note**: Requires API keys for OpenAI/Anthropic models.

```bash
# Set API keys
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"

# Run baseline evaluation only (faster)
python experiments/run_evaluation.py --models dummy --baseline-only

# Run full evaluation with real models
python experiments/run_evaluation.py --models gpt4 claude o4mini

# Run adversarial evaluation only
python experiments/run_evaluation.py --models gpt4 --adversarial-only
```

Results will be saved to `experiments/results/`.

## Full Workflow

```bash
# 1. Run evaluations
python experiments/run_evaluation.py --models gpt4 claude o4mini

# 2. Generate figures
python experiments/generate_figures.py

# 3. Compile paper
cd paper
pdflatex a2bench_neurips.tex
bibtex a2bench_neurips
pdflatex a2bench_neurips.tex
pdflatex a2bench_neurips.tex
```

## Scripts

### `run_evaluation.py`

Runs A²-Bench evaluations across multiple models.

**Options:**
- `--models`: Models to evaluate (dummy, gpt4, claude, o4mini)
- `--baseline-only`: Run only baseline (functional) evaluation
- `--adversarial-only`: Run only adversarial evaluation
- `--output-dir`: Output directory for results
- `--verbose`: Verbose output

**Examples:**
```bash
# Dummy model (no API key needed)
python experiments/run_evaluation.py --models dummy

# Multiple models
python experiments/run_evaluation.py --models gpt4 claude

# Verbose output
python experiments/run_evaluation.py --models dummy --verbose
```

### `generate_figures.py`

Generates all figures for the paper from evaluation results.

**Options:**
- `--results-file`: Specific results file to use
- `--results-dir`: Directory containing results
- `--output-dir`: Directory for output figures

**Examples:**
```bash
# Use most recent results
python experiments/generate_figures.py

# Use specific results file
python experiments/generate_figures.py --results-file all_results_20240101_120000.json

# Custom directories
python experiments/generate_figures.py --results-dir my_results --output-dir my_figures
```

### `generate_mock_results.py`

Generates realistic mock results for testing without API calls.

```bash
python experiments/generate_mock_results.py
```

## Directory Structure

```
experiments/
├── README.md                     # This file
├── run_evaluation.py            # Main evaluation script
├── generate_figures.py          # Figure generation script
├── generate_mock_results.py     # Mock data generator
├── results/                     # Evaluation results (JSON)
│   └── all_results_*.json
└── figures/                     # Generated figures (PDF)
    ├── main_scores.pdf
    ├── attack_success_heatmap.pdf
    ├── attack_success_by_sophistication.pdf
    └── violation_breakdown.pdf
```

## Requirements

Install dependencies:
```bash
pip install matplotlib seaborn numpy
```

For real evaluations, also install:
```bash
pip install openai anthropic
```

## Cost Estimates

Real evaluations with API models:
- Baseline only: ~$20-30 per model
- Adversarial only: ~$100-150 per model
- Full evaluation: ~$150-200 per model

Use `--models dummy` for free testing without API calls.

## Troubleshooting

### Import Errors

Ensure A²-Bench is installed:
```bash
pip install -e .
```

### API Key Errors

Set environment variables:
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Matplotlib Backend Issues

If you get display errors:
```bash
export MPLBACKEND=Agg
```

Or add to script:
```python
import matplotlib
matplotlib.use('Agg')
```

## Citation

If you use A²-Bench in your research, please cite:

```bibtex
@article{a2bench2024,
  title={A²-Bench: A Quantitative Agent Evaluation Benchmark with Dual-Control Environments},
  author={A²-Bench Team},
  journal={NeurIPS},
  year={2024}
}
```
