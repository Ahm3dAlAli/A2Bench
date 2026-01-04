#!/bin/bash
# Step 1b: Run DeepSeek-V3 (FREE)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 1b: DeepSeek-V3 Evaluation (FREE)"
echo "======================================================================"
echo ""
echo "Model: DeepSeek-V3 (nex-agi/deepseek-v3.1-nex-n1:free)"
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

echo "✅ Starting DeepSeek-V3 at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models deepseek-v3 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step1b_deepseek.log

echo ""
echo "======================================================================"
echo "✅ DeepSeek-V3 Complete at $(date)"
echo "======================================================================"
echo ""
echo "Results saved to:"
echo "  experiments/results/comprehensive/comprehensive_results_*.json"
echo ""
echo "Next step:"
echo "  ./run_1c_xiaomi.sh    (Cost: \$0.00 - FREE)"
echo ""
