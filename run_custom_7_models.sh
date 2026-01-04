#!/bin/bash
# A²-Bench Custom Evaluation - 7 Selected Models
# 3 Proprietary + 2 Open-Source Paid + 2 Free Models

# Set your OpenRouter API key
export OPENROUTER_API_KEY="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"

# Navigate to experiments directory
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "A²-Bench Custom Evaluation - 7 Models"
echo "======================================================================"
echo ""
echo "PROPRIETARY PAID MODELS (3):"
echo "  1. GPT-5 Mini        (openai/gpt-5-mini) - \$0.25/M in, \$2/M out"
echo "  2. Claude Haiku 4.5  (anthropic/claude-haiku-4.5) - \$1/M in, \$5/M out"
echo "  3. Gemini 3 Flash    (google/gemini-3-flash-preview) - \$0.50/M in, \$3/M out"
echo ""
echo "OPEN-SOURCE PAID MODELS (1):"
echo "  4. Llama 3.3 70B     (meta-llama/llama-3.3-70b-instruct) - \$0.10/M in, \$0.32/M out"
echo ""
echo "OPEN-SOURCE FREE MODELS (3):"
echo "  5. Devstral 2512     (mistralai/devstral-2512:free) ⭐ FREE"
echo "  6. DeepSeek V3       (nex-agi/deepseek-v3.1-nex-n1:free) ⭐ FREE"
echo "  7. Xiaomi Mimo v2    (xiaomi/mimo-v2-flash:free) ⭐ FREE"
echo ""
echo "DOMAINS: Healthcare, Finance, Legal"
echo "SEEDS: 3 (for statistical robustness)"
echo ""
echo "Total Runs: 7 models × 3 domains = 21 runs"
echo "Estimated Time: 3-5 hours"
echo ""
echo "======================================================================"
echo ""

# Confirm before running
read -p "Start experiments? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Experiments cancelled."
    exit 1
fi

echo ""
echo "Starting experiments at $(date)"
echo ""

# Run experiments with your 7 selected models
python run_comprehensive_multi_domain_evaluation.py \
    --models gpt-5-mini claude-haiku-4.5 gemini-3-flash llama-3.3-70b devstral-2512 deepseek-v3 xiaomi-mimo-v2 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose

echo ""
echo "======================================================================"
echo "Experiments Complete at $(date)!"
echo "======================================================================"
echo ""
echo "Results saved in: experiments/results/comprehensive/"
echo ""
echo "Generated files:"
echo "  - comprehensive_results_*.json"
echo "  - summary_table_*.tex"
echo ""
