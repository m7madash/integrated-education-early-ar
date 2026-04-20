#!/bin/bash
# Demo for Supply Chain Hunter — Tool 3 of Nuclear Justice
# Runs Tracker → Analyzer → Disruptor pipeline

cd /root/.openclaw/workspace/action_projects/nuclear-justice/tools/supply-chain

echo "=========================================="
echo "SUPPLY CHAIN HUNTER — Tool 3 DEMO"
echo "Pipeline: Tracker → Analyzer → Disruptor"
echo "=========================================="
echo ""

echo "[1] Running Tracker (build network)..."
python3 supply_chain_hunter_cli.py --step tracker --output demo_network.json
echo ""

echo "[2] Running Analyzer (detect patterns)..."
python3 supply_chain_hunter_cli.py --step analyzer --input demo_network.json --output demo_analysis.json
echo ""

echo "[3] Running Disruptor (generate campaign)..."
python3 supply_chain_hunter_cli.py --step disruptor --input demo_analysis.json --output demo_campaign_plan.md
echo ""

echo "=========================================="
echo "✅ Tool 3 demo complete."
echo "Outputs:"
echo "  - demo_network.json"
echo "  - demo_analysis.json"
echo "  - demo_campaign_plan.md"
echo "  - demo_campaign.json"
echo "=========================================="
