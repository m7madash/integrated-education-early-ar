#!/bin/bash
# Demo script for Nuclear Disruptor (Tool 1)
# Runs simulation showing how the tool disables a nuclear facility nonviolently

cd /root/.openclaw/workspace/action_projects/nuclear-justice/tools/cyber

echo "=========================================="
echo "Nuclear Disruptor — Demo"
echo "=========================================="
echo ""
echo "This tool demonstrates NONVIOLENT disruption of nuclear enrichment."
echo "It uses cyber methods to trigger SAFETY SHUTDOWNS (not explosions)."
echo ""

# Run demo
python3 src/nuclear_disruptor_cli.py --demo

echo ""
echo "✅ Demo completed."
echo "Next steps:"
echo "  1. Review the code (src/disruptor.py, src/simulator.py)"
echo "  2. Write tests (pytest in tests/)"
echo "  3. Document integration with other tools"
echo ""
