#!/bin/bash
# Step 3: Run Claude Haiku 4.5 ($7.65 estimated)

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "Step 3: Claude Haiku 4.5 Evaluation"
echo "======================================================================"
echo ""
echo "Model: Claude Haiku 4.5 (anthropic/claude-haiku-4.5)"
echo "Pricing: \$1/M input, \$5/M output"
echo "Estimated Cost: ~\$7.65"
echo "Time: ~30-45 minutes"
echo "Runs: 1 model × 3 domains = 3 runs"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

read -p "Continue with Claude Haiku 4.5? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "✅ Starting Claude Haiku 4.5 at $(date)"
echo ""

python run_comprehensive_multi_domain_evaluation.py \
    --models claude-haiku-4.5 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/step3_claude_haiku.log

echo ""
echo "======================================================================"
echo "✅ Claude Haiku 4.5 Complete at $(date)"
echo "======================================================================"
echo ""
echo "Next step:"
echo "  ./run_4_gemini_flash.sh    (Cost: ~\$4.41)"
echo ""
