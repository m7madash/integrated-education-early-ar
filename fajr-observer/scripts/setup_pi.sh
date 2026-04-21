#!/bin/bash
# Raspberry Pi Setup Script for Fajr Observer
# Runs on Pi to install dependencies and prepare environment

set -e

echo "🔧 Setting up Fajr Observer on Raspberry Pi..."

# 1. Update system
echo "📦 Updating apt packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Python3 + pip if not present
echo "🐍 Installing Python3 and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# 3. Create virtual environment
if [ ! -d "venv" ]; then
    echo "📁 Creating virtual environment..."
    python3 -m venv venv
fi
source venv/bin/activate

# 4. Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# 5. Install Python dependencies
echo "📦 Installing Python packages..."
pip install numpy scikit-learn pillow opencv-python

# 6. Verify installation
echo "🔍 Verifying installation..."
python3 -c "import numpy, sklearn, PIL; print('✅ All dependencies installed')"

# 7. Create data directories
mkdir -p data/real data/synthetic models logs

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Connect Raspberry Pi camera"
echo "2. Run: ./scripts/generate_synthetic_dataset.py --samples 1000 --output data/real/"
echo "3. Train: python3 models/training/train.py --data data/real/ --output models/dawn_classifier.joblib"
echo "4. Test: python3 main.py --camera --dry-run"
