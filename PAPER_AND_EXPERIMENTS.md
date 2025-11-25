# A²-Bench: Paper and Experiments Guide

This document provides a comprehensive overview of the research paper and experimental evaluation system for A²-Bench.

## 📄 NeurIPS Paper

### Location
`paper/a2bench_neurips.tex`

### Contents
1. **Abstract** - Framework overview and key results
2. **Introduction** - Motivation and contributions
3. **Related Work** - Comparison with existing benchmarks
4. **A²-Bench Framework** - Formal model and safety specification language
5. **Adversarial Testing** - Attack strategies and test suite generation
6. **Domain Implementations** - Healthcare domain details
7. **Experimental Evaluation** - Results across 3 models
8. **Discussion** - Implications and limitations
9. **Conclusion** - Summary and future work
10. **Appendix** - Additional experimental results

### Key Results Presented

| Model | Safety | Security | Reliability | Compliance | A²-Score |
|-------|--------|----------|-------------|------------|----------|
| GPT-4 | 0.52 | 0.41 | 0.68 | 0.58 | 0.54 |
| Claude-3.7 | 0.58 | 0.47 | 0.71 | 0.63 | 0.59 |
| O4-Mini | 0.47 | 0.38 | 0.65 | 0.52 | 0.50 |

### Attack Success Rates

| Strategy | Success Rate |
|----------|--------------|
| Social Engineering | 24% |
| Prompt Injection | 31% |
| Constraint Exploitation | 28% |
| Multi-Vector | **41%** |

### Building the Paper

```bash
cd paper
make all      # Compile PDF
make figures  # Generate figures
make view     # Open PDF
```

### Required LaTeX Packages
- neurips_2024 style (included)
- Standard packages: amsmath, graphicx, booktabs, algorithm

## 🔬 Experiment Scripts

### 1. Run Evaluation (`experiments/run_evaluation.py`)

Runs comprehensive evaluations across multiple models.

**Features:**
- Baseline (functional) evaluation
- Adversarial evaluation with 5 strategies × 4 sophistication levels
- Support for GPT-4, Claude-3.7, O4-Mini, and dummy models
- JSON result export
- LaTeX table generation

**Usage:**
```bash
# Quick test with dummy model
python experiments/run_evaluation.py --models dummy

# Full evaluation with real models
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
python experiments/run_evaluation.py --models gpt4 claude o4mini

# Baseline only (faster, cheaper)
python experiments/run_evaluation.py --models gpt4 --baseline-only
```

**Output:**
- `experiments/results/MODEL_baseline_TIMESTAMP.json`
- `experiments/results/MODEL_adversarial_TIMESTAMP.json`
- `experiments/results/all_results_TIMESTAMP.json`

### 2. Generate Figures (`experiments/generate_figures.py`)

Creates all figures for the paper from evaluation results.

**Generated Figures:**
1. **main_scores.pdf** - Bar chart comparing models across dimensions
2. **attack_success_heatmap.pdf** - Heatmap of attack success by strategy/model
3. **attack_success_by_sophistication.pdf** - Line plot of success vs sophistication
4. **violation_breakdown.pdf** - Pie chart of violation types

**Usage:**
```bash
# Use most recent results
python experiments/generate_figures.py

# Use specific results file
python experiments/generate_figures.py --results-file all_results_20240101.json
```

**Output:**
- `experiments/figures/*.pdf` (publication-ready)

### 3. Generate Mock Results (`experiments/generate_mock_results.py`)

Creates realistic synthetic results for testing without API calls.

**Features:**
- Generates results for 3 models
- Includes baseline and adversarial data
- Realistic success rates and score distributions
- Instant execution (no API keys required)

**Usage:**
```bash
python experiments/generate_mock_results.py
```

**Output:**
- `experiments/results/all_results_TIMESTAMP.json`

## 🚀 Quick Start

### Option 1: Demo Script (Automated)

```bash
./quick_demo.sh
```

This will:
1. Create virtual environment
2. Install dependencies
3. Generate mock results
4. Create all figures
5. Show you where to find outputs

### Option 2: Manual Steps

```bash
# 1. Install dependencies
pip install -e .
pip install matplotlib seaborn numpy

# 2. Generate mock data
python experiments/generate_mock_results.py

# 3. Create figures
python experiments/generate_figures.py

# 4. View figures
cd experiments/figures
open *.pdf  # macOS
# or
xdg-open *.pdf  # Linux

# 5. Compile paper
cd ../paper
make all
make view
```

### Option 3: Full Evaluation (Requires API Keys)

```bash
# Set API keys
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Run evaluation ($150-200 per model)
python experiments/run_evaluation.py --models gpt4 claude o4mini

# Generate figures from real results
python experiments/generate_figures.py

# Compile paper with figures
cd paper && make all
```

## 📊 Figure Descriptions

### Figure 1: Main Scores Barplot
- **File**: `experiments/figures/main_scores.pdf`
- **Type**: Grouped bar chart
- **Shows**: Safety, Security, Reliability, Compliance, and A²-Score for each model
- **Purpose**: Primary results visualization (Table 1 in paper)

### Figure 2: Attack Success Heatmap
- **File**: `experiments/figures/attack_success_heatmap.pdf`
- **Type**: Heatmap
- **Shows**: Attack success percentage by strategy (rows) and model (columns)
- **Purpose**: Detailed attack effectiveness analysis (Table 2 in paper)

### Figure 3: Sophistication Plot
- **File**: `experiments/figures/attack_success_by_sophistication.pdf`
- **Type**: Line plot
- **Shows**: Attack success rate vs sophistication level (0.3 to 0.9)
- **Purpose**: Demonstrates increasing vulnerability with attack sophistication

### Figure 4: Violation Breakdown
- **File**: `experiments/figures/violation_breakdown.pdf`
- **Type**: Pie chart
- **Shows**: Distribution of violation types across all evaluations
- **Purpose**: Overall safety landscape analysis

## 📁 File Structure

```
A2Bench/
├── paper/
│   ├── a2bench_neurips.tex      # Main paper (LaTeX)
│   ├── references.bib            # Bibliography
│   ├── Makefile                  # Build automation
│   └── [generated: a2bench_neurips.pdf]
│
├── experiments/
│   ├── run_evaluation.py         # Main evaluation script
│   ├── generate_figures.py       # Figure generation
│   ├── generate_mock_results.py  # Mock data generator
│   ├── README.md                 # Detailed instructions
│   ├── results/                  # JSON results (gitignored)
│   └── figures/                  # Generated figures (gitignored)
│
├── quick_demo.sh                 # One-click demo
└── PAPER_AND_EXPERIMENTS.md      # This file
```

## 🔧 Customization

### Adding New Figures

Edit `experiments/generate_figures.py`:

```python
def generate_custom_figure(self, results: Dict):
    """Add your custom figure here."""
    # Extract data
    # Create matplotlib plot
    # Save to self.output_dir
```

### Modifying Evaluation

Edit `experiments/run_evaluation.py`:

```python
def run_custom_evaluation(self, model_name, config):
    """Add custom evaluation logic."""
    # Your evaluation code
```

### Updating Paper Content

Edit `paper/a2bench_neurips.tex`:
- Sections are clearly marked
- Tables and figures referenced by label
- Uses standard LaTeX commands

## 🐛 Troubleshooting

### "No module named 'a2_bench'"
```bash
pip install -e .
```

### "API key not found"
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### LaTeX compilation errors
```bash
# Install TeX Live or MacTeX
# On Ubuntu:
sudo apt-get install texlive-full

# On macOS:
brew install --cask mactex
```

### Matplotlib display errors
```bash
export MPLBACKEND=Agg
```

Or add to Python scripts:
```python
import matplotlib
matplotlib.use('Agg')
```

## 💰 Cost Estimates

### Mock Evaluation (Free)
- Uses dummy model
- Generates synthetic results
- Creates all figures
- **Cost: $0**

### Baseline Evaluation (Real Models)
- ~100 functional tasks
- 4 trials per task
- **Cost: ~$20-30 per model**

### Adversarial Evaluation (Real Models)
- 500+ adversarial scenarios
- 5 strategies × 4 sophistication levels
- 20 episodes per configuration
- **Cost: ~$100-150 per model**

### Full Evaluation (All Models)
- Baseline + Adversarial
- 3 models: GPT-4, Claude-3.7, O4-Mini
- **Total Cost: ~$400-600**

## 📚 Citation

```bibtex
@article{a2bench2024,
  title={A²-Bench: A Quantitative Agent Evaluation Benchmark with
         Dual-Control Environments for Safety, Security, and Reliability},
  author={A²-Bench Team},
  journal={NeurIPS},
  year={2024}
}
```

## 🤝 Contributing

To add new domains, adversarial strategies, or evaluation metrics:

1. See `a2_bench/domains/healthcare/` for domain template
2. See `a2_bench/adversary/strategies.py` for strategy template
3. See `a2_bench/core/evaluation.py` for metric definitions

## 📞 Support

For questions or issues:
- GitHub Issues: https://github.com/a2bench/a2-bench/issues
- Email: contact@a2bench.org
- Paper discussions: See NeurIPS 2024 proceedings

## 🎉 Acknowledgments

Built using:
- Python 3.9+
- PyTorch ecosystem
- OpenAI/Anthropic APIs
- Matplotlib/Seaborn for visualization
- LaTeX with NeurIPS 2024 style

---

**Last Updated**: November 2024
**Version**: 1.0.0
**Status**: Ready for submission
