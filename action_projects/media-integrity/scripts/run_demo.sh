#!/bin/bash
# Media Integrity — Demo Script
# Run quick demonstration of all modules

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "🔍 Media Integrity Demo — Tool 7 v0.1.0"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 required"
    exit 1
fi

# Install deps if missing
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt 2>/dev/null || true

# Create test data
echo "1️⃣ Creating test data..."
python3 -c "from src.media_integrity.image import ImageForensics; from PIL import Image; img=Image.new('RGB',(100,100),(255,0,0)); img.save('tests/test_data/demo.jpg','JPEG'); print('   ✅ Test image created')" 2>/dev/null || echo "   ⚠️  Pillow not available, skipping image test"

# 2. Image test
echo ""
echo "2️⃣ Image Forensics Test..."
python3 -m src.media_integrity.image tests/test_data/demo.jpg --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   Score: {d[\"manipulation_score\"]}, Manipulated: {d[\"likely_manipulated\"]}')" || echo "   ⚠️  Requires Pillow"

# 3. Text test
echo ""
echo "3️⃣ Fake News Detection Test..."
python3 -m src.media_integrity.text "Shocking! 5G causes coronavirus! Secret government plot!" --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   Score: {d[\"manipulation_score\"]}, Fake: {d[\"is_likely_fake\"]}')" || echo "   ⚠️  Requires scikit-learn"

# 4. Source test
echo ""
echo "4️⃣ Source Reputation Test..."
python3 -m src.media_integrity.source https://reuters.com/article --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   Score: {d[\"reputation_score\"]}, Assessment: {d[\"overall_assessment\"][:40]}...')" || echo "   ⚠️  Requires requests"

# 5. Bot test
echo ""
echo "5️⃣ Bot Detection Test..."
cat > /tmp/bot_test.json <<EOF
{
  "id": "test_bot_123",
  "username": "user328415",
  "join_date": "2026-04-10T00:00:00Z",
  "followers": 5,
  "following": 500,
  "posts": 300,
  "content_samples": ["Check out this link!", "Check out this link!", "Amazing news!"]
}
EOF
python3 -m src.media_integrity.social --account /tmp/bot_test.json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   Bot score: {d[\"bot_score\"]}, Likely bot: {d[\"is_likely_bot\"]}')" || echo "   ⚠️  Requires scikit-learn"

# 6. Orchestrator test
echo ""
echo "6️⃣ Orchestrator Test..."
python3 -m src.media_integrity.detector "Breaking: AI will destroy all jobs tomorrow!" --type text 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'   Verdict: {d[\"verdict\"]}, Score: {d[\"overall_integrity_score\"]}')" || echo "   ⚠️ "

echo ""
echo "=========================================="
echo "✅ Demo complete!"
echo ""
echo "To start the API server:"
echo "  python3 -m src.media_integrity.api --port 5000"
echo ""
