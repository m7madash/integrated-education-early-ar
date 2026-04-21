#!/bin/bash
# Run Fajr Observer in Emulation Mode (no dependencies, no hardware)
# This script runs the pure-Python emulator to test the logic without camera or pip packages.

set -e

cd "$(dirname "$0")"

echo "🔍 Fajr Observer — Emulation Mode"
echo "================================"
echo ""
echo "This runs the full pipeline using only Python standard library."
echo "No numpy, no PIL, no sklearn required."
echo ""

if ! command -v python3 &>/dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

python3 emulate.py

echo ""
echo "✅ Emulation complete!"
echo ""
echo "Notes:"
echo "- This uses synthetic features, not real images"
echo "- For real deployment, use deploy.sh on Raspberry Pi"
echo "- Emulated model saved to models/emulated_model.json"
