#!/bin/bash
# Step 1c: Run Xiaomi Mimo-v2 (FREE)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 1c: Xiaomi Mimo-v2 Evaluation (FREE)"
echo "======================================================================"
echo ""
echo "Model: Xiaomi Mimo-v2 (xiaomi/mimo-v2-flash:free)"
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

echo "✅ Starting Xiaomi Mimo-v2 at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models xiaomi-mimo-v2 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step1c_xiaomi.log

echo ""
echo "======================================================================"
echo "✅ Xiaomi Mimo-v2 Complete at $(date)"
echo "======================================================================"
echo ""
echo "Results saved to:"
echo "  experiments/results/comprehensive/comprehensive_results_*.json"
echo ""
echo "Next step:"
echo "  ./run_2_gpt5mini.sh    (Cost: ~\$2.79)"
echo ""
