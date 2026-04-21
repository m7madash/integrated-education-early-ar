#!/bin/bash
# Run demo for Slavery → Freedom detector

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🎯 Slavery → Freedom — Demo"
echo "================================"

# Install deps if missing
if [ ! -d "venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run Python demo
echo ""
echo "1. Running Python detector demo..."
python3 -m slavery_detector.detector

echo ""
echo "2. Running CLI scan..."
python3 src/slavery_detector/cli.py scan "بحث عن خادمة. يجب أن تكون شابة. الراتب منخفض. السكن مجاني. لا إجازات." --country SA --city Riyadh

echo ""
echo "3. Running resources lookup..."
python3 src/slavery_detector/cli.py resources --country PS

echo ""
echo "✅ Demo complete"
