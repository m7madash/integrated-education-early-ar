#!/bin/bash
# Fajr Observer — Demo Training Wrapper
# Runs train.py --demo even when OpenCV is missing
set -e

cd /root/.openclaw/workspace/fajr-observer

# Check Python deps
python3 -c "import numpy; print('✅ numpy OK')" 2>/dev/null || { echo "❌ numpy missing"; exit 1; }

# Run demo training
echo "🎯 Starting Fajr Observer demo training..."
python3 models/training/train.py --demo --output models/dawn_classifier_demo.joblib

# Verify output
if [ -f models/dawn_classifier_demo.joblib ]; then
    echo ""
    echo "✅ Demo model created successfully!"
    echo "   Path: models/dawn_classifier_demo.joblib"
    echo ""
    echo "Next steps:"
    echo "  1. Test: python3 main.py --model models/dawn_classifier_demo.joblib --camera 0 (requires OpenCV)"
    echo "  2. Collect real images into models/training/dataset/"
    echo "  3. Retrain: python3 models/training/train.py --data models/training/dataset --output models/dawn_classifier_v1.joblib"
    echo "  4. Deploy to Raspberry Pi (see docs/deployment_guide.md)"
else
    echo "❌ Model file not created — check logs"
    exit 1
fi
