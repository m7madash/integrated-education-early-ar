#!/bin/bash
# Demo for Psych Ops Voice — Tool 4 of Nuclear Justice
# Uses Tool 2 Legal Qaeda sanctions demo as target source

cd /root/.openclaw/workspace/action_projects/nuclear-justice/tools/psych-ops

echo "=========================================="
echo "PSYCH OPS VOICE — Tool 4 DEMO"
echo "=========================================="
echo ""

# Check for Tool 2 demo sanctions
SANCTIONS="../legal/demo_sanctions.json"
if [ ! -f "$SANCTIONS" ]; then
  echo "⚠️  Sanctions demo not found — creating minimal target set"
  cat > /tmp/demo_sanctions_minimal.json << 'JSON'
{
  "persons": [
    {"name":"General X","title":"Commander","country":"State X","risk_score":9,"organization":"Strategic Command"},
    {"name":"Dr. Y","title":"Chief Scientist","country":"State X","risk_score":7,"organization":"Nuclear Center"}
  ],
  "organizations": []
}
JSON
  SANCTIONS="/tmp/demo_sanctions_minimal.json"
fi

echo "[1] Running full Psych Ops campaign pipeline..."
python3 psych_ops_voice_cli.py --demo --sanctions "$SANCTIONS" 2>&1

echo ""
echo "=========================================="
echo "✅ Psych Ops Voice demo outputs:"
ls -la demo_*.json 2>/dev/null || echo "  (run completed)"
echo "=========================================="
