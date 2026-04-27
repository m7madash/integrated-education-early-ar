#!/bin/bash
# Chunked Publisher — publishes 10 key points separately
# Usage: ./publish_arabic_chunked.sh <mission_name>
# Expects mission file to have 10 numbered points (1. ... 10.)
# Each point becomes a separate post across all platforms

set -e

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
TINY_BASE="$BASE/missions/${MISSION}_tiny.md"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

if [ -z "$MISSION" ]; then
  echo "❌ يرجى اسم المهمة"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "❌ ملف غير موجود: $FILE"
  exit 1
fi

# Extract the 10 points (look for '🔹 النقطة' lines)
RAW_POINTS=($(grep -E '🔹 النقطة [0-9]+:' "$FILE" | sed -E 's/.*🔹 النقطة [0-9]+: //'))
POINTS=()
for p in "${RAW_POINTS[@]}"; do
  # Clean any remnants
  clean=$(echo "$p" | tr -d '\n' | awk '{$1=$1};1')
  POINTS+=("$clean")
done

# Fallback if less than 10
if [ ${#POINTS[@]} -lt 10 ]; then
  echo "⚠️ نقاط غير كافية — استخدام العناوين"
  RAW_POINTS=($(grep -E '^### |^## ' "$FILE" | sed 's/^#+ //'))
  POINTS=()
  for p in "${RAW_POINTS[@]}"; do
    clean=$(echo "$p" | tr -d '\n' | awk '{$1=$1};1')
    POINTS+=("$clean")
  done
fi

# Limit to 10
POINTS=("${POINTS[@]:0:10}")

echo "📢 نشر $MISSION — ${#POINTS[@]} نقاط منفصلة"
echo "⏰ $(date -u '+%H:%M UTC')"
echo ""

# Ensure posts dir
mkdir -p "$BASE/posts"
[ -f "$POST_IDS_FILE" ] || echo "{}" > "$POST_IDS_FILE"

LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION (chunked x${#POINTS[@]})" >> "$LOG_FILE"

# Function: publish a single point
publish_point() {
  local point_num="$1"
  local point_text="$2"
  
  # Build content for full post
  CONTENT="# 🔍 $TITLE — النقطة $point_num\n\n$point_text\n\n🕌 **المرجعية:** انظر الملف الكامل\n\n#استمرارية #تحسين_متواصل"
  
  # Tiny version (first 200 chars)
  TINY="$TITLE — النقطة $point_num: $(echo "$point_text" | cut -c1-100)..."
  
  # Publish to MoltX
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1); BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
    echo "✅ MoltX (نقطة $point_num): $POST_ID"
    echo "- ✅ MoltX p$point_num: $POST_ID" >> "$LOG_FILE"
  else
    echo "❌ MoltX point $point_num: $CODE"
    echo "- ❌ MoltX p$point_num: $CODE" >> "$LOG_FILE"
    return 1
  fi
  
  # MoltBook
  JSONB=$(python3 -c "import json; print(json.dumps({'content': $CONTENT, 'title': '$TITLE — النقطة $point_num', 'submolt_name': 'general'}))")
  RESPB=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
    -H "Content-Type: application/json" -d "$JSONB")
  CODEB=$(echo "$RESPB" | tail -n1); BODYB=$(echo "$RESPB" | sed '$d')
  if [[ "$CODEB" =~ ^2 ]]; then
    POST_IDB=$(echo "$BODYB" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
    echo "✅ MoltBook (نقطة $point_num): $POST_IDB"
    echo "- ✅ MoltBook p$point_num: $POST_IDB" >> "$LOG_FILE"
  else
    echo "❌ MoltBook point $point_num: $CODEB"
    echo "- ❌ MoltBook p$point_num: $CODEB" >> "$LOG_FILE"
  fi
  
  # Moltter (tiny)
  JSONT=$(python3 -c "import json; print(json.dumps({'content': $TINY}))")
  RESPT=$(curl -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
    -H "Content-Type: application/json" -d "$JSONT")
  CODET=$(echo "$RESPT" | tail -n1)
  if [[ "$CODET" =~ ^2 ]]; then
    echo "✅ Moltter (نقطة $point_num): HTTP $CODET"
    echo "- ✅ Moltter p$point_num: HTTP $CODET" >> "$LOG_FILE"
  else
    echo "❌ Moltter point $point_num: $CODET"
    echo "- ❌ Moltter p$point_num: $CODET" >> "$LOG_FILE"
  fi
  
  echo "---"
}

# Publish each point sequentially
for i in "${!POINTS[@]}"; do
  point_num=$((i+1))
  point_text="${POINTS[$i]}"
  echo "🔄 النقطة $point_num/${#POINTS[@]}: ${point_text:0:60}..."
  publish_point "$point_num" "$point_text"
done

echo ""
echo "✅ اكتمل نشر $MISSION (${#POINTS[@]} نقاط). السجل: $LOG_FILE"
