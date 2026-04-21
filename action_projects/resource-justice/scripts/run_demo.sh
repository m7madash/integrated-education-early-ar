#!/bin/bash
# Resource Justice — Demo Impact Scenarios
# Shows impact of reallocating military budgets to food/health/education

set -e

cd "$(dirname "$0")/.."

echo "🚀 Resource Justice — Impact Demo"
echo "=================================="
echo ""

# Demo scenarios: country, percent
scenarios=(
    "Saudi Arabia:5"
    "Egypt:3"
    "Palestine:10"
    "UAE:2"
    "Jordan:4"
)

for scenario in "${scenarios[@]}"; do
    IFS=':' read -r country percent <<< "$scenario"
    echo "📌 ${country} — reallocating ${percent}% of military budget:"
    python3 -m resource_justice.calculator --country "$country" --percent "$percent" 2>/dev/null || true
    echo ""
done

echo "✅ Demo complete."
echo ""
echo "💡 Try yourself:"
echo "   python3 -m resource_justice.calculator --country \"Saudi Arabia\" --percent 1"
echo "   python3 -m resource_justice.cli serve --port 5000"
