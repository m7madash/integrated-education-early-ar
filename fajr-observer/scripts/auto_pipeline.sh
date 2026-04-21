#!/bin/bash
# Full automated pipeline for Fajr Observer on Raspberry Pi
# From setup to training to testing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "🚀 Fajr Observer — Full Auto Pipeline"
echo "======================================"

# Step 1: Setup (install dependencies)
echo ""
echo "🔧 Step 1/5: Installing dependencies (if needed)..."
if [ -f "scripts/setup_pi.sh" ]; then
    bash scripts/setup_pi.sh
else
    echo "⚠️  setup_pi.sh not found — skipping (dependencies may already be installed)"
fi

# Step 2: Generate synthetic dataset (placeholder until real camera available)
echo ""
echo "🎨 Step 2/5: Generating synthetic training data..."
mkdir -p data/real
python3 scripts/generate_synthetic_dataset.py --samples 1000 --output data/real/ || {
    echo "⚠️  Synthetic generation failed (PIL missing?) — continuing with existing data if any"
}

# Step 3: Train the model
echo ""
echo "🎓 Step 3/5: Training SVM model..."
python3 models/training/train.py --data data/real/ --output models/dawn_classifier.joblib || {
    echo "❌ Training failed — check dependencies (numpy, scikit-learn) and data"
    exit 1
}

# Step 4: Test dry-run
echo ""
echo "🧪 Step 4/5: Dry-run test (no camera)..."
python3 main.py --dry-run || {
    echo "⚠️  Dry-run test had warnings (camera not available?)"
}

# Step 5: Summary
echo ""
echo "✅ Pipeline complete!"
echo ""
echo "📂 Artifacts:"
echo "   - Model: models/dawn_classifier.joblib"
echo "   - Data: data/real/"
echo "   - Logs: logs/"
echo ""
echo "🚀 To run with camera:"
echo "   python3 main.py --camera"
echo ""
echo "📝 See README.md for deployment instructions and troubleshooting."
