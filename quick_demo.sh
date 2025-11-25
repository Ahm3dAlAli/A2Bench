#!/bin/bash
# Quick demo script for A²-Bench

set -e

echo "======================================"
echo "A²-Bench Quick Demo"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -q -e . matplotlib seaborn numpy 2>/dev/null || true

echo ""
echo "1. Generating mock results..."
python experiments/generate_mock_results.py

echo ""
echo "2. Generating figures..."
python experiments/generate_figures.py

echo ""
echo "======================================"
echo "Demo Complete!"
echo "======================================"
echo ""
echo "Generated files:"
echo "  - experiments/results/all_results_*.json"
echo "  - experiments/figures/*.pdf"
echo ""
echo "View figures:"
echo "  cd experiments/figures && open *.pdf"
echo ""
echo "Or compile the paper:"
echo "  cd paper && make all"
echo ""
