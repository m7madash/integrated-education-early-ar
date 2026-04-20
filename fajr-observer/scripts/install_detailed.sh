#!/bin/bash
# Fajr Observer — Installation Script (Ubuntu/Debian/Raspberry Pi OS)

set -e

echo "=== Fajr Observer Agent — Dependency Installer ==="
echo ""

# Check if running as root (needed for apt)
if [ "$EUID" -ne 0 ]; then
  echo "⚠️  Some steps require sudo. Will prompt when needed."
  SUDO="sudo"
else
  SUDO=""
fi

# 1. System packages
echo "[1/3] Installing system dependencies..."
$SUDO apt-get update
$SUDO apt-get install -y \
  python3-pip \
  python3-venv \
  libopencv-dev \
  libgtk-3-dev \
  ffmpeg \
  mpv \
  curl \
  wget \
  git

# 2. Create virtual environment
echo ""
echo "[2/3] Creating Python virtual environment..."
python3 -m venv venv || { echo "❌ Failed to create venv. Install python3-venv first."; exit 1; }
source venv/bin/activate

# 3. Upgrade pip and install Python packages
echo ""
echo "[3/3] Installing Python packages..."
pip install --upgrade pip
pip install \
  opencv-python>=4.8.0 \
  numpy>=1.24.0 \
  pillow>=10.0.0 \
  astral>=3.2 \
  scikit-learn>=1.3.0 \
  pyyaml \
  schedule>=1.2.0 \
  python-telegram-bot>=20.0 \
  requests

# Optional: TensorFlow (heavy, for CNN) — skip by default
# pip install tensorflow  # uncomment if you have GPU/RPi 4+

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Configure: nano config/thresholds.json  (set your latitude)"
echo "  2. Camera: connect and mount facing east (no obstructions)"
echo "  3. Test dry-run: ./scripts/run_observer.sh --dry-run --lat 21.5 --lon 39.0"
echo "  4. If test OK, run live: ./scripts/run_observer.sh --live"
echo ""
echo "For Raspberry Pi specific issues, see docs/deployment_guide.md"
echo ""
