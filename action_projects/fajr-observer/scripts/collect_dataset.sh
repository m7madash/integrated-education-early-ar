#!/bin/bash
# Collect dawn images for training the classifier
# Usage: ./scripts/collect_dataset.sh [output_dir]

# This script guides manual collection; automatic YouTube download requires youtube-dl
# which may violate ToS — use only public domain or self-captured images.

set -e

OUTPUT_DIR="${1:-models/training/dataset}"
mkdir -p "$OUTPUT_DIR"/{night,false_dawn,true_dawn}

echo "=== Fajr Observer Dataset Collection ==="
echo ""
echo "This script helps organize your training dataset."
echo "You need to supply images manually (recommended) or via youtube-dl (caution)."
echo ""
echo "Directory structure created:"
echo "  $OUTPUT_DIR/night/      — images of night sky (before false dawn)"
echo "  $OUTPUT_DIR/false_dawn/ — images of false dawn (vertical streak)"
echo "  $OUTPUT_DIR/true_dawn/  — images of true dawn (horizontal spread)"
echo ""
echo "How to collect:"
echo "  1. Capture images using your camera during 3–6 AM (save as JPG)"
echo "  2. Label each image manually: does it show night/false/true dawn?"
echo "  3. Place into corresponding folder"
echo ""
echo "Minimum recommended: 500 images per class (1500 total) for decent accuracy."
echo ""
echo "Alternatively, use time-lapse videos:"
echo "  youtube-dl -f best \"<DAWN_TIMELAPSE_URL>\" -o temp.mp4"
echo "  ffmpeg -i temp.mp4 -vf \"select='gte(t,3*60)*lt(t,6*60)'\" -vsync vfr frame_%04d.jpg"
echo "  (then manually label frames)"
echo ""
echo "After collection, run training:"
echo "  python3 models/training/train.py --data $OUTPUT_DIR --epochs 20"
echo ""

# Create dummy README inside dataset
cat > "$OUTPUT_DIR/README.txt" << EOF
Fajr Observer — Training Dataset

Place your labeled images here:

  night/      — before any dawn light appears (complete darkness)
  false_dawn/ — vertical streak only (no horizontal spread)
  true_dawn/  — horizontal glow across horizon

Filename format: <location>_<date>_<time>.jpg
Example: gaza_20260420_0425.jpg

Recommended: at least 500 images per class for baseline model.
EOF

echo "✅ Dataset folder structure ready. Start collecting images!"
