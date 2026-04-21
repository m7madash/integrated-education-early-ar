#!/bin/bash
# Fajr Observer — One-Command Raspberry Pi Deployment
# Usage: bash deploy.sh

set -e

cd "$(dirname "$0")"

echo "🚀 Fajr Observer — Automated Deployment"
echo "======================================"
echo ""
echo "This script will:"
echo "1. Install system dependencies (Python3, pip)"
echo "2. Create Python virtual environment"
echo "3. Install Python packages (numpy, scikit-learn, pillow, opencv-python)"
echo "4. Generate synthetic training data (1000 samples)"
echo "5. Train SVM model"
echo "6. Run dry-run test"
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Run full pipeline
bash scripts/auto_pipeline.sh

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📖 Next steps:"
echo "  - Connect Raspberry Pi camera"
echo "  - Run: python3 main.py --camera"
echo "  - See PI_DEPLOYMENT_GUIDE.md for full docs"
