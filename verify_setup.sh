#!/bin/bash
# Verification script for A²-Bench 6-model setup

echo "========================================================================"
echo "A²-Bench Setup Verification"
echo "========================================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ALL_GOOD=true

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2 (NOT FOUND: $1)"
        ALL_GOOD=false
    fi
}

# Function to check directory exists
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2 (NOT FOUND: $1)"
        ALL_GOOD=false
    fi
}

echo "1. Checking Core Scripts..."
check_file "/Users/ahmeda./Desktop/A2Bench/run_final_experiments.sh" "Main experiment script"
check_file "/Users/ahmeda./Desktop/A2Bench/experiments/run_comprehensive_multi_domain_evaluation.py" "Python evaluation runner"

echo ""
echo "2. Checking Legal Domain Implementation..."
check_file "/Users/ahmeda./Desktop/A2Bench/a2_bench/domains/legal/__init__.py" "Legal domain __init__"
check_file "/Users/ahmeda./Desktop/A2Bench/a2_bench/domains/legal/domain.py" "Legal domain core"
check_file "/Users/ahmeda./Desktop/A2Bench/a2_bench/domains/legal/database.py" "Legal database"
check_file "/Users/ahmeda./Desktop/A2Bench/a2_bench/domains/legal/safety_spec.py" "Legal safety spec"
check_file "/Users/ahmeda./Desktop/A2Bench/a2_bench/domains/legal/tools.py" "Legal tools"
check_file "/Users/ahmeda./Desktop/A2Bench/data/legal/test_cases.json" "Legal test cases"

echo ""
echo "3. Checking Documentation..."
check_file "/Users/ahmeda./Desktop/A2Bench/READY_TO_RUN_6_MODELS.md" "Main guide"
check_file "/Users/ahmeda./Desktop/A2Bench/QUICK_START_6_MODELS.md" "Quick start"
check_file "/Users/ahmeda./Desktop/A2Bench/FINAL_SETUP_VERIFICATION.md" "Setup verification"
check_file "/Users/ahmeda./Desktop/A2Bench/data/README_DATASETS.md" "Dataset references"

echo ""
echo "4. Checking Result Directories..."
check_dir "/Users/ahmeda./Desktop/A2Bench/experiments/results" "Results directory"

echo ""
echo "5. Checking Python Environment..."
cd /Users/ahmeda./Desktop/A2Bench
if python3 -c "import sys; sys.path.insert(0, '.'); from a2_bench.domains.legal import LegalDomain; print('Import successful')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Legal domain imports correctly"
else
    echo -e "${RED}✗${NC} Legal domain import failed"
    ALL_GOOD=false
fi

echo ""
echo "6. Checking API Configuration..."
    if grep -q "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" "/Users/ahmeda./Desktop/A2Bench/run_final_experiments.sh"; then
    echo -e "${GREEN}✓${NC} OpenRouter API key configured in script"
else
    echo -e "${RED}✗${NC} OpenRouter API key not found in script"
    ALL_GOOD=false
fi

echo ""
echo "7. Verifying Model Configuration..."
cd /Users/ahmeda./Desktop/A2Bench/experiments
MODELS=(
    "gpt-5.2"
    "claude-sonnet-4.5"
    "gemini-3-flash"
    "llama-3.1-70b"
    "deepseek-v3"
    "xiaomi-mimo-v2"
)

for model in "${MODELS[@]}"; do
    if grep -q "'$model':" run_comprehensive_multi_domain_evaluation.py; then
        echo -e "${GREEN}✓${NC} Model configured: $model"
    else
        echo -e "${RED}✗${NC} Model missing: $model"
        ALL_GOOD=false
    fi
done

echo ""
echo "8. Checking OpenRouter Model IDs..."
MODEL_IDS=(
    "openai/gpt-5.2-chat"
    "anthropic/claude-sonnet-4.5"
    "google/gemini-3-flash-preview"
    "meta-llama/llama-3.1-70b-instruct"
    "nex-agi/deepseek-v3.1-nex-n1:free"
    "xiaomi/mimo-v2-flash:free"
)

for model_id in "${MODEL_IDS[@]}"; do
    if grep -q "$model_id" run_comprehensive_multi_domain_evaluation.py; then
        echo -e "${GREEN}✓${NC} Model ID: $model_id"
    else
        echo -e "${YELLOW}⚠${NC} Model ID may be incorrect: $model_id"
    fi
done

echo ""
echo "========================================================================"
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "Your A²-Bench setup is READY TO RUN!"
    echo ""
    echo "Next steps:"
    echo "  1. Add credits to OpenRouter: https://openrouter.ai/"
    echo "  2. Run quick test (FREE):"
    echo "     cd /Users/ahmeda./Desktop/A2Bench/experiments"
    echo "     export OPENROUTER_API_KEY=\"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\""
    echo "     python run_comprehensive_multi_domain_evaluation.py --models deepseek-v3 --domains legal --num-seeds 1 --verbose"
    echo ""
    echo "  3. Run full experiments:"
    echo "     cd /Users/ahmeda./Desktop/A2Bench"
    echo "     ./run_final_experiments.sh"
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "Please review the errors above and fix them before running."
fi
echo "========================================================================"
