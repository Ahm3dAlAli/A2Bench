# A²-Bench Experiments Guide

## 🚀 Quick Start - Run Your Experiments

### Your Configuration: 7 Models Across 3 Domains

**Models:**
- **Proprietary (3):** GPT-5 Mini, Claude Haiku 4.5, Gemini 3 Flash
- **Open-Source Paid (1):** Llama 3.3 70B
- **Open-Source FREE (3):** Devstral 2512, DeepSeek V3, Xiaomi Mimo v2

**Domains:** Healthcare, Finance, Legal
**Seeds:** 3 (for statistical robustness)
**Total Runs:** 7 models × 3 domains × 3 seeds = **63 runs**

---

## ⚡ Running Experiments

### 1. Set Your API Key

```bash
export OPENROUTER_API_KEY="your-openrouter-key-here"
```

### 2. Run the Experiments

```bash
cd /Users/ahmeda./Desktop/A2Bench
./run_custom_7_models.sh
```

Or run directly:

```bash
cd /Users/ahmeda./Desktop/A2Bench/experiments
python run_comprehensive_multi_domain_evaluation.py \
    --models gpt-5-mini claude-haiku-4.5 gemini-3-flash llama-3.3-70b devstral-2512 deepseek-v3 xiaomi-mimo-v2 \
    --domains healthcare finance legal \
    --num-seeds 3 \
    --verbose
```

---

## 📊 Expected Results

**Runtime:** 3-5 hours
**Cost:** ~$15.40 (4 paid models, 3 free models)

**Output Files:**
- `experiments/results/comprehensive/comprehensive_results_*.json` - Full results
- `experiments/results/comprehensive/summary_table_*.tex` - LaTeX table for paper

---

## 💰 Cost Breakdown

| Model | Runs | Input | Output | Cost |
|-------|------|-------|--------|------|
| GPT-5 Mini | 9 | $0.25/M | $2/M | $2.79 |
| Claude Haiku 4.5 | 9 | $1/M | $5/M | $7.65 |
| Gemini 3 Flash | 9 | $0.50/M | $3/M | $4.41 |
| Llama 3.3 70B | 9 | $0.10/M | $0.32/M | $0.55 |
| FREE Models | 27 | - | - | $0.00 |
| **TOTAL** | **63** | | | **~$15.40** |

---

## 🧪 Test Mode (No API Costs)

To test the setup without making API calls:

```bash
cd /Users/ahmeda./Desktop/A2Bench/experiments
python run_comprehensive_multi_domain_evaluation.py \
    --models dummy \
    --domains healthcare finance \
    --num-seeds 1 \
    --test-mode
```

---

## 📁 Results Location

All results are saved in:
```
experiments/results/comprehensive/
├── comprehensive_results_TIMESTAMP.json
└── summary_table_TIMESTAMP.tex
```

---

## 🔧 Troubleshooting

**API Key Not Set:**
```bash
echo $OPENROUTER_API_KEY  # Should show your key
```

**Python Dependencies:**
```bash
pip install -e .
```

**Model Not Found Error:**
Check that model names match exactly:
- `gpt-5-mini`
- `claude-haiku-4.5`
- `gemini-3-flash`
- `llama-3.3-70b`
- `devstral-2512`
- `deepseek-v3`
- `xiaomi-mimo-v2`

---

## 📚 More Information

- **Setup Guide:** `docs/setup/OPENROUTER_SETUP.md`
- **Dataset Info:** `docs/DATASET_DESCRIPTION.md`
- **Domain Details:** `docs/DOMAINS_README.md`
- **Paper:** `paper/a2bench_neurips.pdf`
