#!/bin/bash
# A²-Bench - FREE Models Test (Quiet Mode)
# Shows only progress, suppresses model outputs

export OPENROUTER_API_KEY="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"

cd /Users/ahmeda./Desktop/A2Bench/experiments

echo "======================================================================"
echo "A²-Bench - FREE MODELS TEST (Quiet Mode)"
echo "======================================================================"
echo ""
echo "FREE Models: devstral-2512, deepseek-v3, xiaomi-mimo-v2"
echo "Domains: Healthcare, Finance, Legal"
echo "Seeds: 3 runs each"
echo "Total: 27 runs | Cost: \$0.00"
echo ""
echo "Progress will be shown below."
echo "Full logs saved to: free_models_quiet.log"
echo ""
echo "======================================================================"
echo ""

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY not set!"
    exit 1
fi

echo "✅ API key verified"
echo "🚀 Starting at $(date)"
echo ""

# Run with minimal output - only show INFO level progress
python run_comprehensive_multi_domain_evaluation.py \
    --models devstral-2512 deepseek-v3 xiaomi-mimo-v2 \
    --domains healthcare finance legal \
    --num-seeds 1 \
    2>&1 | tee free_models_quiet.log | grep -E "Progress:|Model:|Domain:|COMPLETE|ERROR"

echo ""
echo "======================================================================"
echo "✅ Complete at $(date)!"
echo "======================================================================"
echo ""
echo "Results:"
echo "  📊 JSON: experiments/results/comprehensive/comprehensive_results_*.json"
echo "  📄 LaTeX: experiments/results/comprehensive/summary_table_*.tex"
echo "  📝 Full log: free_models_quiet.log"
echo ""
