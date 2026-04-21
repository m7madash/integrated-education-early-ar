#!/bin/bash
# Resource Justice — Collect Sample Data
# This script loads sample budgets from data/budgets.json (or fetches live if implemented)

set -e

cd "$(dirname "$0")/.."

echo "🔁 Collecting Resource Justice data..."

# For v0.1.0: we use sample data only
if [ -f "data/budgets.json" ]; then
    echo "✅ Sample budgets found:"
    python3 -m resource_justice.collector 2>/dev/null || echo "   (use CLI to view)"
else
    echo "❌ data/budgets.json missing"
    exit 1
fi

echo "✅ Data collection complete."
echo ""
echo "Next: Run './run_demo.sh' to see impact scenarios"
