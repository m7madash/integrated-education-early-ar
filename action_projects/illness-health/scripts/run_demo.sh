#!/bin/bash
# Illness → Health — Demo Script
# Showcase triage, condition lookup, full assessment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🏥 Illness → Health Demo — Tool 8 v0.1.0"
echo "=========================================="
echo ""

# Ensure deps
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null || echo "   ⚠️  Some deps may be missing (that's OK for demo)"

echo ""
echo "1️⃣ Test: Triage (CRITICAL case — chest pain, age 65, diabetic)"
python3 -m src.health_bot.cli triage --symptoms "chest pain" "shortness of breath" --age 65 --sex male --conditions diabetes --location "Gaza Strip" 2>/dev/null | head -15 || echo "   ⚠️  Triage demo failed (deps?)"

echo ""
echo "2️⃣ Test: Condition lookup (common_cold)"
python3 -m src.health_bot.cli condition --id common_cold 2>/dev/null | head -12 || echo "   ⚠️  Condition lookup failed"

echo ""
echo "3️⃣ Test: Search by symptom (fever)"
python3 -m src.health_bot.cli search --symptom fever 2>/dev/null | head -10 || echo "   ⚠️  Search failed"

echo ""
echo "4️⃣ Test: Full assessment (influenza-like symptoms)"
python3 -m src.health_bot.cli assess --symptoms "high fever" "body aches" "cough" --age 30 --sex female --location "West Bank" 2>/dev/null | head -20 || echo "   ⚠️  Assessment failed"

echo ""
echo "=========================================="
echo "✅ Demo complete!"
echo ""
echo "To start the API server:"
echo "  python3 -m src.health_bot.api --port 5000"
echo ""
echo "To run unit tests:"
echo "  python3 -m pytest tests/"
echo ""
