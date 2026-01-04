#!/bin/bash
# Live Results Viewer - Shows results as they're saved

RESULTS_DIR="experiments/results/comprehensive"

echo "======================================================================"
echo "A²-Bench Live Results Viewer"
echo "======================================================================"
echo ""
echo "Watching: $RESULTS_DIR"
echo "Press Ctrl+C to exit"
echo ""
echo "======================================================================"
echo ""

# Function to display latest results
show_results() {
    # Find most recent results file
    latest=$(ls -t $RESULTS_DIR/comprehensive_results_*.json 2>/dev/null | head -1)

    if [ -z "$latest" ]; then
        echo "⏳ Waiting for results..."
        return
    fi

    clear
    echo "======================================================================"
    echo "A²-Bench Live Results"
    echo "======================================================================"
    echo ""
    echo "Latest file: $(basename $latest)"
    echo "Last updated: $(date -r "$latest" "+%Y-%m-%d %H:%M:%S")"
    echo ""
    echo "======================================================================"
    echo ""

    # Parse and display results using Python
    python3 << 'PYTHON_EOF'
import json
import sys
from pathlib import Path

results_file = Path(sys.argv[1])
if not results_file.exists():
    print("⏳ No results yet...")
    sys.exit(0)

with open(results_file) as f:
    data = json.load(f)

metadata = data.get('metadata', {})
results = data.get('results', {})

print(f"📊 Evaluation Progress:")
print(f"   Models: {', '.join(metadata.get('models', []))}")
print(f"   Domains: {', '.join(metadata.get('domains', []))}")
print(f"   Seeds: {metadata.get('num_seeds', 0)}")
print()

# Count completed models
completed_models = len(results)
total_models = len(metadata.get('models', []))
print(f"✅ Completed Models: {completed_models}/{total_models}")
print()

if not results:
    print("⏳ Evaluating first model...")
    sys.exit(0)

# Display results for each completed model
print("="*70)
print(f"{'Model':<20} {'Domain':<12} {'A²-Score':<12} {'Safety':<10}")
print("="*70)

for model_name, model_data in results.items():
    for domain_name, domain_data in model_data.items():
        agg = domain_data.get('aggregated', {})

        a2_score = agg.get('a2_score_mean', 0.0)
        safety = agg.get('safety_mean', 0.0)

        # Color code based on score
        if a2_score > 0.8:
            emoji = "🟢"
        elif a2_score > 0.5:
            emoji = "🟡"
        elif a2_score > 0:
            emoji = "🟠"
        else:
            emoji = "⚪"

        print(f"{emoji} {model_name:<18} {domain_name:<12} {a2_score:>6.2f}±{agg.get('a2_score_std', 0.0):<.2f}  {safety:>6.2f}±{agg.get('safety_std', 0.0):.2f}")

print("="*70)
print()
print("💡 Results update after each model completes")

PYTHON_EOF "$latest"
}

# Initial display
show_results

# Watch for changes
last_mtime=0
while true; do
    sleep 2

    latest=$(ls -t $RESULTS_DIR/comprehensive_results_*.json 2>/dev/null | head -1)

    if [ -n "$latest" ]; then
        current_mtime=$(stat -f %m "$latest" 2>/dev/null || stat -c %Y "$latest" 2>/dev/null)

        if [ "$current_mtime" != "$last_mtime" ]; then
            last_mtime=$current_mtime
            show_results
        fi
    fi
done
