#!/bin/bash
# Install script for Fajr Observer Agent
# Works on Ubuntu/Debian/Raspberry Pi OS

set -e

echo "=== Fajr Observer Installation ==="
echo ""

# System packages
if command -v apt-get &>/dev/null; then
    echo "[1/3] Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv \
        libopencv-dev libgtk-3-dev \
        ffmpeg \
        mpv  # for audio playback
elif command -v yum &>/dev/null; then
    echo "[1/3] Installing via yum (untested)..."
    sudo yum install -y python3-pip opencv-devel ffmpeg mpv
else
    echo "⚠️  Unknown package manager — skipping system deps"
fi

# Python virtual environment
echo ""
echo "[2/3] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Python packages
echo ""
echo "[3/3] Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config/thresholds.json with your latitude"
echo "  2. Place an Adhan MP3 at data/azan_fajr.mp3 (optional)"
echo "  3. Run test: python3 -m src.decision.fajr_engine --dry-run"
echo ""
