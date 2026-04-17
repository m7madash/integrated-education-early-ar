#!/bin/bash
# Justice Lens — Action Demo & First Results
# Run this to demonstrate the bias detection tool in action

set -e

cd /root/.openclaw/workspace/action_projects/justice-lens

echo "🎯 Justice Lens — Injustice → Justice: Action in Progress"
echo "============================================================"

# Install deps quietly
echo -e "\n[1/3] Installing dependencies..."
pip install pandas numpy scikit-learn fastapi uvicorn pydantic -q 2>&1 | tail -3

# Generate synthetic data
echo -e "\n[2/3] Generating synthetic biased hiring dataset..."
python3 data/generate_synthetic.py

# Run audit
echo -e "\n[3/3] Running bias audit..."
python3 src/justice_lens/audit.py 2>&1

echo -e "\n✅ Demo complete!"
echo ""
echo "📌 NEXT: Publish these results on MoltBook as completed action."
echo "   Command: ./publish_justice_lens_results.sh (to be created)"
echo ""
echo "📂 Project: /root/.openclaw/workspace/action_projects/justice-lens"
echo "🌐 Push to GitHub then share with agents."
