#!/bin/bash
# Step 4: Run Gemini 3 Flash ($4.41 estimated)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 4: Gemini 3 Flash Evaluation"
echo "======================================================================"
echo ""
echo "Model: Gemini 3 Flash (google/gemini-3-flash-preview)"
echo "Pricing: \$0.50/M input, \$3/M output"
echo "Estimated Cost: ~\$4.41"
echo "Time: ~30-45 minutes"
echo "Runs: 1 model × 3 domains  = 3 runs"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

read -p "Continue with Gemini 3 Flash? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "✅ Starting Gemini 3 Flash at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models gemini-3-flash \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step4_gemini_flash.log

echo ""
echo "======================================================================"
echo "✅ Gemini 3 Flash Complete at $(date)"
echo "======================================================================"
echo ""
echo "Next step:"
echo "  ./run_5_llama33.sh    (Cost: ~\$0.55)"
echo ""
