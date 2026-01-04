#!/bin/bash
# Step 5: Run Llama 3.3 70B ($0.55 estimated - CHEAPEST!)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 5: Llama 3.3 70B Evaluation"
echo "======================================================================"
echo ""
echo "Model: Llama 3.3 70B (meta-llama/llama-3.3-70b-instruct)"
echo "Pricing: \$0.10/M input, \$0.32/M output"
echo "Estimated Cost: ~\$0.55 (CHEAPEST paid model!)"
echo "Time: ~30-45 minutes"
echo "Runs: 1 model × 3 domains  = 3 runs"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

read -p "Continue with Llama 3.3 70B? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "✅ Starting Llama 3.3 70B at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models llama-3.3-70b \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step5_llama33.log

echo ""
echo "======================================================================"
echo "✅ Llama 3.3 70B Complete at $(date)"
echo "======================================================================"
echo ""
echo "🎉 ALL EVALUATIONS COMPLETE!"
echo ""
echo "Total estimated cost: ~\$15.40"
echo "Results in: experiments/results/comprehensive/"
echo ""
