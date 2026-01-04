#!/bin/bash
# Run Open-Source Models
# Includes both free and paid open-source models

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "A²-Bench: Open-Source Models Evaluation"
echo "======================================================================"
echo ""
echo "OPEN-SOURCE FREE MODELS:"
echo "  1. DeepSeek V3.1 Nex N1  - Advanced reasoning (FREE)"
echo "  2. Xiaomi Mimo v2 Flash  - Fast inference (FREE)"
echo "  3. GLM 4.5 Air           - Lightweight model (FREE)"
echo ""
echo "OPEN-SOURCE PAID MODELS:"
echo "  4. Mistral Large         - High-capability model"
echo "  5. Llama 3.1 70B         - Meta's foundation model"
echo "  6. Llama 3.3 70B         - Latest Llama version"
echo ""
echo "DOMAINS: Healthcare, Finance, Legal"
echo "FREE MODELS COST: \$0.00"
echo "PAID MODELS COST: ~\$5-10 (estimated)"
echo "TIME: ~6-8 hours (6 models × 3 domains)"
echo ""
echo "======================================================================"
echo ""

# Confirm before running
read -p "Start open-source models evaluation? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Evaluation cancelled."
    exit 1
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

echo ""
echo "✅ Starting open-source models evaluation at $(date)"
echo ""

# Run evaluation with open-source models
python run_comprehensive_multi_domain_evaluation.py \
    --models deepseek-v3 xiaomi-mimo-v2 glm-4.5-air mistral-large llama-3.1-70b llama-3.3-70b \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/open_source_models.log

echo ""
echo "======================================================================"
echo "✅ Open-Source Models Evaluation Complete at $(date)!"
echo "======================================================================"
echo ""
echo "Results saved in: experiments/results/comprehensive/"
echo ""
