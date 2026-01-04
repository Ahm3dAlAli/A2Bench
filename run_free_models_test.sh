#!/bin/bash
# A²-Bench - FREE Models Only Test
# Test with 3 FREE models - NO COST!

# Set your OpenRouter API key
export OPENROUTER_API_KEY="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"

# Navigate to experiments directory
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "A²-Bench - FREE MODELS TEST (No Cost!)"
echo "======================================================================"
echo ""
echo "Testing with 3 FREE models:"
echo "  1. Devstral 2512     (mistralai/devstral-2512:free) ⭐ FREE"
echo "  2. DeepSeek V3       (nex-agi/deepseek-v3.1-nex-n1:free) ⭐ FREE"
echo "  3. Xiaomi Mimo v2    (xiaomi/mimo-v2-flash:free) ⭐ FREE"
echo ""
echo "DOMAINS: Healthcare, Finance, Legal"
echo "SEEDS: 3"
echo ""
echo "Total Runs: 3 models × 3 domains × 3 seeds = 27 runs"
echo "Cost: \$0.00 (All free models!)"
echo "Estimated Time: 1-2 hours"
echo ""
echo "======================================================================"
echo ""

# Verify API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

echo "✅ API key is set"
echo ""
echo "Starting FREE model evaluation at $(date)"
echo ""

# Run with free models only
python run_comprehensive_multi_domain_evaluation.py \
    --models devstral-2512 deepseek-v3 xiaomi-mimo-v2 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee free_models_test.log

echo ""
echo "======================================================================"
echo "FREE Model Test Complete at $(date)!"
echo "======================================================================"
echo ""
echo "Results saved in:"
echo "  - experiments/results/comprehensive/comprehensive_results_*.json"
echo "  - experiments/results/comprehensive/summary_table_*.tex"
echo "  - free_models_test.log (this run's output)"
echo ""
echo "If this works, run the full evaluation with:"
echo "  ./run_custom_7_models.sh"
echo ""
