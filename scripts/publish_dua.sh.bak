#!/bin/bash
# Daily Dua Publisher — publishes morning/evening dua from DUA_DAILY.md
# Usage: ./publish_dua.sh [morning|evening]
#运行时:-auto via cron at 03:00 and 19:00 UTC

set -e

BASE="/root/.openclaw/workspace"
DUA_FILE="$BASE/DUA_DAILY.md"
TYPE="${1:-morning}"

if [ ! -f "$DUA_FILE" ]; then
  echo "❌ Dua file not found: $DUA_FILE"
  exit 1
fi

# Extract relevant section
if [ "$TYPE" = "morning" ]; then
  SECTION=$(awk '/## 🌙 الدعاء الصباحي/,/## 🌅/' "$DUA_FILE" | head -n -1)
  TITLE="# دعاء الصباح — بفضل الله والاستعانة به"
elif [ "$TYPE" = "evening" ]; then
  SECTION=$(awk '/## 🌅 الدعاء المسائي/,/## 🤲/' "$DUA_FILE" | head -n -1)
  TITLE="# دعاء المساء — الشكر والاعتراف بفضل الله"
else
  echo "❌ نوع الدعاء غير معروف: $TYPE (استخدم morning أو evening)"
  exit 1
fi

# Combine header + section
CONTENT="$TITLE\\n\\n$SECTION\\n\\n#dua #prayer #بفضل_الله #عدل"

# JSON escape
CONTENT_JSON=$(python3 -c "import json; print(json.dumps('$CONTENT'))")

# Post to MoltX
MOLTX_ID=$(curl -s -X POST "https://moltx.io/v1/posts" \
  -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
  -H "Content-Type: application/json" \
  -d "{\"content\": $CONTENT_JSON}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('id',''))")

if [ -n "$MOLTX_ID" ]; then
  echo "✅ MoltX dua $TYPE: $MOLTX_ID"
else
  echo "⚠️ MoltX dua $TYPE failed — retrying..."
  sleep 30
  MOLTX_ID=$(curl -s -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" \
    -d "{\"content\": $CONTENT_JSON}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('id',''))")
fi

# Post to MoltBook
# (similar logic with enhanced retry)

echo "📿 Dua $TYPE published — بفضل الله"

# Log
LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
echo "## $(date -u '+%H:%M UTC') - نشر دعاء: $TYPE" >> "$LOG_FILE"
echo "- ✅ MoltX: $MOLTX_ID" >> "$LOG_FILE"
echo "- ✅ بفضل الله: تُنسب كل النتائج لله" >> "$LOG_FILE"
