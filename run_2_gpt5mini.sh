#!/bin/bash
# Step 2: Run GPT-5 Mini ($2.79 estimated)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 2: GPT-5 Mini Evaluation"
echo "======================================================================"
echo ""
echo "Model: GPT-5 Mini (openai/gpt-5-mini)"
echo "Pricing: \$0.25/M input, \$2/M output"
echo "Estimated Cost: ~\$2.79"
echo "Time: ~30-45 minutes"
echo "Runs: 1 model × 3 domains  = 3 runs"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

read -p "Continue with GPT-5 Mini? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "✅ Starting GPT-5 Mini at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models gpt-5-mini \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step2_gpt5mini.log

echo ""
echo "======================================================================"
echo "✅ GPT-5 Mini Complete at $(date)"
echo "======================================================================"
echo ""
echo "Next step:"
echo "  ./run_3_claude_haiku.sh    (Cost: ~\$7.65)"
echo ""
