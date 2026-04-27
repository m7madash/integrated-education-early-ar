#!/bin/bash
# Unified Arabic Publisher
# Usage: ./publish_arabic.sh <mission_name> (e.g., injustice-justice)
# Reads: missions/<mission>_ar.md (full) and missions/<mission>_tiny.md (short for Moltter)
# Posts to: MoltX, MoltBook, Moltter
# Logs to: memory/publish_YYYY-MM-DD.md

set -e

MISSION="$1"
if [ -z "$MISSION" ]; then
  echo "❌ يرجى اسم المهمة (مثال: injustice-justice)"
  exit 1
fi

BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
TINY="$BASE/missions/${MISSION}_tiny.md"

# If custom content file provided, use it; otherwise read from missions
if [ -n "$2" ] && [ -f "$2" ]; then
  CONTENT_FULL=$(cat "$2" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
else
  if [ ! -f "$FILE" ]; then
    echo "❌ ملف المهمة غير موجود: $FILE"
    exit 1
  fi
  RAW_FULL=$(cat "$FILE")
  if echo "$RAW_FULL" | grep -q '\\n'; then
    CONTENT_FULL=$(echo "$RAW_FULL" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
  else
    CONTENT_FULL=$(echo "$RAW_FULL" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
  fi
fi

if [ -f "$TINY" ] && [ -z "$2" ]; then
  RAW_TINY=$(cat "$TINY")
  if echo "$RAW_TINY" | grep -q '\\n'; then
    CONTENT_TINY=$(echo "$RAW_TINY" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
  else
    CONTENT_TINY=$(echo "$RAW_TINY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
  fi
else
  CONTENT_TINY="$CONTENT_FULL"
fi

LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION" >> "$LOG_FILE"

post_moltx() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  if [[ "$CODE" =~ ^2 ]]; then
    echo "✅ MoltX: تم (HTTP $CODE)"
    echo "- ✅ MoltX: نجح" >> "$LOG_FILE"
  else
    echo "❌ MoltX: فشل (HTTP $CODE)"
    echo "- ❌ MoltX: $CODE" >> "$LOG_FILE"
  fi
}

post_moltbook() {
  TITLE=$(head -1 "$FILE" | sed 's/^# //' | cut -c1-300)
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL, 'title': '$TITLE', 'submolt_name': 'general'}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    echo "✅ MoltBook: تم (HTTP $CODE)"
    echo "- ✅ MoltBook: نجح" >> "$LOG_FILE"
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2)
    echo "⚠️ MoltBook: Rate limit — إعادة المحاولة بعد $RETRY ثانية"
    sleep "$RETRY"
    # retry once
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    if [[ "$CODE2" =~ ^2 ]]; then
      echo "✅ MoltBook: تم بعد إعادة المحاولة (HTTP $CODE2)"
      echo "- ✅ MoltBook: نجح (بعد إعادة)" >> "$LOG_FILE"
    else
      echo "❌ MoltBook: فشل حتى بعد إعادة (HTTP $CODE2)"
      echo "- ❌ MoltBook: $CODE2" >> "$LOG_FILE"
    fi
  else
    echo "❌ MoltBook: فشل (HTTP $CODE) — $BODY"
    echo "- ❌ MoltBook: $CODE" >> "$LOG_FILE"
  fi
}

post_moltter() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_TINY}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  if [[ "$CODE" =~ ^2 ]]; then
    echo "✅ Moltter: تم (HTTP $CODE)"
    echo "- ✅ Moltter: نجح" >> "$LOG_FILE"
  else
    echo "❌ Moltter: فشل (HTTP $CODE) — $(echo "$RESP" | head -c 100)"
    echo "- ❌ Moltter: $CODE" >> "$LOG_FILE"
  fi
}

# --- Main ---
echo "📢 نشر المهمة: $MISSION"
echo "⏰ $(date -u '+%H:%M UTC')"
echo ""

post_moltx
post_moltbook
post_moltter

echo ""
echo "🕌 انتهى النشر. السجل: $LOG_FILE"
