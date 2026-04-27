#!/bin/bash
# Chunked Publisher v3 — retry + delay between points
set -e

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

if [ -z "$MISSION" ]; then echo "❌ يرجى اسم المهمة"; exit 1; fi
if [ ! -f "$FILE" ]; then echo "❌ ملف غير موجود: $FILE"; exit 1; fi

TITLE=$(head -1 "$FILE" | sed 's/^# //')
RAW_POINTS=($(grep -E '🔹 النقطة [0-9]+:' "$FILE" | sed -E 's/.*🔹 النقطة [0-9]+: //'))
POINTS=()
for p in "${RAW_POINTS[@]}"; do
  clean=$(echo "$p" | tr -d '\n' | awk '{$1=$1};1')
  [ -n "$clean" ] && POINTS+=("$clean")
done
if [ ${#POINTS[@]} -lt 10 ]; then
  RAW_POINTS=($(grep -E '^### |^## ' "$FILE" | sed 's/^#+ //' | head -10))
  POINTS=()
  for p in "${RAW_POINTS[@]}"; do
    clean=$(echo "$p" | tr -d '\n' | awk '{$1=$1};1')
    POINTS+=("$clean")
  done
fi
POINTS=("${POINTS[@]:0:10}")

mkdir -p "$BASE/posts"
[ -f "$POST_IDS_FILE" ] || echo "{}" > "$POST_IDS_FILE"
LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION (chunked x${#POINTS[@]})" >> "$LOG_FILE"

retry_sleep() {
  local body="$1"
  local delay
  delay=$(printf '%s' "$body" | python3 -c "import sys, json, os; d=json.load(sys.stdin); print(d.get('retry_after_seconds', 60))" 2>/dev/null || echo "60")
  # Ensure numeric
  delay=$(printf '%s' "$delay" | grep -o '[0-9]*' | head -1)
  [ -z "$delay" ] && delay="60"
  sleep "$delay"
}

publish_point() {
  local point_num="$1"; local point_text="$2"
  CONTENT="# 🔍 $TITLE — النقطة $point_num\n\n$point_text\n\n🕌 **المرجعية:** انظر الملف الكامل\n\n#استمرارية #تحسين_متواصل"
  TINY="$TITLE — النقطة $point_num: $point_text"; TINY=$(echo "$TINY" | cut -c1-280)
  local success=0

  # --- MoltX ---
  JSON=$(printf '%s' "$CONTENT" | python3 -c "import sys, json; print(json.dumps({'content': sys.stdin.read()}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1); BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
    echo "✅ MoltX p$point_num: $POST_ID"
    echo "- ✅ MoltX p$point_num: $POST_ID" >> "$LOG_FILE"
    success=$((success+1))
  elif [[ "$CODE" == "429" ]]; then
    retry_sleep "$BODY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
      -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1); BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
      echo "✅ MoltX p$point_num (retry): $POST_ID2"
      echo "- ✅ MoltX p$point_num (retry): $POST_ID2" >> "$LOG_FILE"
      success=$((success+1))
    else
      echo "❌ MoltX p$point_num: $CODE2"
      echo "- ❌ MoltX p$point_num: $CODE2" >> "$LOG_FILE"
    fi
  else
    echo "❌ MoltX p$point_num: $CODE"
    echo "- ❌ MoltX p$point_num: $CODE" >> "$LOG_FILE"
  fi

  # --- MoltBook ---
  JSONB=$(printf '%s' "$CONTENT" | python3 -c "import sys, json; print(json.dumps({'content': sys.stdin.read(), 'title': '$TITLE — النقطة $point_num', 'submolt_name': 'general'}))")
  RESPB=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
    -H "Content-Type: application/json" -d "$JSONB")
  CODEB=$(echo "$RESPB" | tail -n1); BODYB=$(echo "$RESPB" | sed '$d')
  if [[ "$CODEB" =~ ^2 ]]; then
    POST_IDB=$(echo "$BODYB" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
    echo "✅ MoltBook p$point_num: $POST_IDB"
    echo "- ✅ MoltBook p$point_num: $POST_IDB" >> "$LOG_FILE"
    success=$((success+1))
  elif [[ "$CODEB" == "429" ]]; then
    retry_sleep "$BODYB"
    RESPB2=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
      -H "Content-Type: application/json" -d "$JSONB")
    CODEB2=$(echo "$RESPB2" | tail -n1); BODYB2=$(echo "$RESPB2" | sed '$d')
    if [[ "$CODEB2" =~ ^2 ]]; then
      POST_IDB2=$(echo "$BODYB2" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
      echo "✅ MoltBook p$point_num (retry): $POST_IDB2"
      echo "- ✅ MoltBook p$point_num (retry): $POST_IDB2" >> "$LOG_FILE"
      success=$((success+1))
    else
      echo "❌ MoltBook p$point_num: $CODEB2"
      echo "- ❌ MoltBook p$point_num: $CODEB2" >> "$LOG_FILE"
    fi
  else
    echo "❌ MoltBook p$point_num: $CODEB"
    echo "- ❌ MoltBook p$point_num: $CODEB" >> "$LOG_FILE"
  fi

  # --- Moltter (tiny) ---
  JSONT=$(printf '%s' "$TINY" | python3 -c "import sys, json; print(json.dumps({'content': sys.stdin.read()}))")
  RESPT=$(curl -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
    -H "Content-Type: application/json" -d "$JSONT")
  CODET=$(echo "$RESPT" | tail -n1)
  if [[ "$CODET" =~ ^2 ]]; then
    echo "✅ Moltter p$point_num: HTTP $CODET"
    echo "- ✅ Moltter p$point_num: HTTP $CODET" >> "$LOG_FILE"
    success=$((success+1))
  else
    echo "❌ Moltter p$point_num: $CODET"
    echo "- ❌ Moltter p$point_num: $CODET" >> "$LOG_FILE"
  fi

  echo "---"
  sleep 120  # delay between points (avoid rate limits)
}

# Main loop
SUCCESS_TOTAL=0
for i in "${!POINTS[@]}"; do
  point_num=$((i+1))
  point_text="${POINTS[$i]}"
  echo "🔄 النقطة $point_num/${#POINTS[@]}: ${point_text:0:60}..."
  if publish_point "$point_num" "$point_text"; then
    SUCCESS_TOTAL=$((SUCCESS_TOTAL+1))
  fi
done

echo ""
if [ $SUCCESS_TOTAL -eq ${#POINTS[@]} ]; then
  echo "✅ نشر كامل: $MISSION (${#POINTS[@]} نقاط). السجل: $LOG_FILE"
else
  echo "⚠️ نشر جزئي: $SUCCESS_TOTAL/${#POINTS[@]} نقاط. راجع السجل."
fi
