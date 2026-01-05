#!/bin/bash
# Step 1a: Run Devstral-2512 (FREE)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 1a: Devstral-2512 Evaluation (FREE)"
echo "======================================================================"
echo ""
echo "Model: Devstral-2512 (mistralai/devstral-2512:free)"
echo "Cost: \$0.00 (FREE!)"
echo "Time: ~20-30 minutes"
echo "Runs: 1 model × 3 domains = 3 runs"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

echo "✅ Starting Devstral-2512 at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models devstral-2512 \
    --domains healthcare finance legal \
    --num-seeds 3 \
    --verbose 2>&1 | tee logs/step1a_devstral.log

echo ""
echo "======================================================================"
echo "✅ Devstral-2512 Complete at $(date)"
echo "======================================================================"
echo ""
echo "Results saved to:"
echo "  experiments/results/comprehensive/comprehensive_results_*.json"
echo ""
echo "Next step:"
echo "  ./run_1b_deepseek.sh    (Cost: \$0.00 - FREE)"
echo ""
