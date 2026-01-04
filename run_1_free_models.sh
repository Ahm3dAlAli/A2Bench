#!/bin/bash
# Step 1: Run FREE models only (No cost!)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 1: FREE Models Evaluation"
echo "======================================================================"
echo ""
echo "Models: devstral-2512, deepseek-v3, xiaomi-mimo-v2"
echo "Cost: \$0.00 (ALL FREE!)"
echo "Time: ~1-2 hours"
echo "Runs: 3 models × 3 domains = 9 runs"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

echo "✅ Starting FREE models at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models devstral-2512 deepseek-v3 xiaomi-mimo-v2 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step1_free_models.log

echo ""
echo "======================================================================"
echo "✅ FREE Models Complete at $(date)"
echo "======================================================================"
echo ""
echo "Results saved to:"
echo "  experiments/results/comprehensive/comprehensive_results_*.json"
echo ""
echo "Next step:"
echo "  ./run_2_gpt5mini.sh    (Cost: ~\$2.79)"
echo ""
