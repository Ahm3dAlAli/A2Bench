#!/bin/bash
# Run ALL FREE Models (Open-Source + Agentic)
# 100% Free evaluation across all free model categories

export OPENROUTER_API_KEY="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"
cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "A²-Bench: ALL FREE MODELS Evaluation"
echo "======================================================================"
echo ""
echo "AGENTIC MODELS (5):"
echo "  • Devstral 2 2512        - 123B agentic coding"
echo "  • KAT-Coder-Pro V1       - 73.4% SWE-Bench"
echo "  • DeepSeek R1T2 Chimera  - 671B MoE reasoning"
echo "  • DeepSeek R1T Chimera   - Balanced R1+V3"
echo "  • NVIDIA Nemotron 3 Nano - Specialized agentic AI"
echo ""
echo "OPEN-SOURCE MODELS (3):"
echo "  • DeepSeek V3.1 Nex N1   - Advanced reasoning"
echo "  • Xiaomi Mimo v2 Flash   - Fast inference"
echo "  • GLM 4.5 Air            - Lightweight model"
echo ""
echo "TOTAL: 8 models × 3 domains = 24 evaluations"
echo "DOMAINS: Healthcare, Finance, Legal"
echo "COST: \$0.00 (100% FREE!)"
echo "TIME: ~12-15 hours"
echo ""
echo "======================================================================"
echo ""

# Confirm before running
read -p "Start ALL free models evaluation? (y/n) " -n 1 -r
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
echo "✅ Starting ALL free models evaluation at $(date)"
echo ""

# Run evaluation with ALL free models
python run_comprehensive_multi_domain_evaluation.py \
    --models devstral-2512 kat-coder-pro deepseek-r1t2-chimera deepseek-r1t-chimera nemotron-3-nano deepseek-v3 xiaomi-mimo-v2 glm-4.5-air \
    --domains healthcare finance legal \
    --num-seeds 1 \
    --verbose 2>&1 | tee logs/all_free_models.log

echo ""
echo "======================================================================"
echo "✅ ALL Free Models Evaluation Complete at $(date)!"
echo "======================================================================"
echo ""
echo "Results saved in: experiments/results/comprehensive/"
echo ""
echo "Model Categories:"
echo "  - Agentic: 5 models (coding + reasoning specialized)"
echo "  - Open-Source: 3 models (general-purpose)"
echo ""
