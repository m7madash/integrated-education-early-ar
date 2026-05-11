#!/bin/bash
# Unified Arabic Publisher v3 — With Content Shield Integration
# Reads: missions/<mission>_analytical_ar.md (+ tiny)
# Posts: MoltX, MoltBook, Moltter
# Filters: Content Shield v3 (context-aware) before publishing

set -e

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_analytical_ar.md"
TINY="$BASE/missions/${MISSION}_tiny_ar.md"

[ -z "$MISSION" ] && { echo "❌ يرجى اسم المهمة (مثال: injustice-justice)"; exit 1; }

# Fallbacks
[ -f "$FILE" ] || FILE="$BASE/missions/${MISSION}_ar.md"
[ -f "$TINY" ] || TINY="$BASE/missions/${MISSION}_tiny.md"

[ -f "$FILE" ] || { echo "❌ ملف المهمة غير موجود: $FILE"; exit 1; }

# Load content (with JSON decoding)
RAW_FULL=$(cat "$FILE")
if echo "$RAW_FULL" | grep -q '\\n'; then
  CONTENT_FULL=$(echo "$RAW_FULL" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
else
  CONTENT_FULL=$(echo "$RAW_FULL" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
fi

if [ -f "$TINY" ]; then
  RAW_TINY=$(cat "$TINY")
  if echo "$RAW_TINY" | grep -q '\\n'; then
    CONTENT_TINY=$(echo "$RAW_TINY" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
  else
    CONTENT_TINY=$(echo "$RAW_TINY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
  fi
else
  CONTENT_TINY="$CONTENT_FULL"
fi

# ========== 🕌 VERIFICATION GATE ==========
if ! node "$BASE/scripts/verify_full_arabic.js" "$MISSION" "$FILE" 2>/dev/null; then
  echo "❌ فشل التحقق: المحتوى يحتوي على非-Arabic characters"
  echo "🛑 نشر [$MISSION] abort — verification failure" >> "$BASE/memory/verification_errors.log"
  exit 1
fi

if ! "$BASE/scripts/verify_mission_religious.sh" "$MISSION" "$FILE" 2>/dev/null; then
  echo "❌ فشل التحقق: مرجعية شرعية غير صحيحة"
  echo "🛑 نشر [$MISSION] abort — religious verification failed" >> "$BASE/memory/verification_errors.log"
  exit 1
fi

# ========== 🛡️ CONTENT SHIELD FILTER ==========
# Context-aware filter (v3): Allows mission-specific + positive-context exceptions
if ! node "$BASE/scripts/content_shield/shield_check.js" "$CONTENT_FULL" "multi" "$MISSION" 2>/dev/null; then
  echo "❌ فشل فحص المحتوى (Content Shield) — تم الرفض"
  echo "🛑 نشر [$MISSION] abort — shield reject" >> "$BASE/memory/verification_errors.log"
  exit 1
fi
# If shield_check exits 0 but queued → still continue (no block)
# ========== END SHIELD ==========

POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"
LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
LEDGER_FILE="$BASE/memory/ledger.jsonl"

mkdir -p "$BASE/posts" "$BASE/reports"
[ -f "$POST_IDS_FILE" ] || echo '{}' > "$POST_IDS_FILE"

append_ledger() {
  local type="$1"; shift
  local payload="$*"
  local ts
  ts=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
  node -e "const fs=require('fs');const p=JSON.parse(process.argv[2]);const e={ts:process.argv[1],type:'$type',payload:p};fs.appendFileSync('$LEDGER_FILE', JSON.stringify(e)+'\n');" "$ts" "$payload" 2>/dev/null || true
}

echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') - نشر: $MISSION" >> "$LOG_FILE"

# Load previous IDs & delete old posts
PREV_IDS=$(cat "$POST_IDS_FILE")
MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx','') or json.load(sys.stdin).get('MOLTX',''))" 2>/dev/null || echo "")
MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook','') or json.load(sys.stdin).get('MOLTBOOK',''))" 2>/dev/null || echo "")
MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter','') or json.load(sys.stdin).get('MOLTTER',''))" 2>/dev/null || echo "")

delete_previous() {
  local platform="$1" post_id="$2" token_var="$3"
  [ -n "$post_id" ] && [ "$post_id" != "null" ] && [ "$post_id" != "undefined" ] || return 0
  echo "🗑️ حذف المنشور القديم من $platform (ID: $post_id)..."
  local CODE
  case "$platform" in
    moltx)
      CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
        "https://moltx.io/v1/posts/$post_id" \
        -H "Authorization: Bearer ${!token_var}")
      ;;
    moltbook)
      CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
        "https://moltbook.com/api/v1/posts/$post_id" \
        -H "Authorization: Bearer ${!token_var}")
      ;;
    moltter)
      CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
        "https://api.molt.tw/v1/statuses/$post_id" \
        -H "Authorization: Bearer ${!token_var}")
      ;;
  esac
  if [ "$CODE" = "200" ] || [ "$CODE" = "204" ]; then
    echo "✅ حُذف بنجاح"
  else
    echo "⚠️ حذف فشل (HTTP $CODE) — قد يكون المنشور محذوف مسبقاً"
  fi
}

delete_previous moltx "$MOLTX_ID" moltx_sk
delete_previous moltbook "$MOLTBOOK_ID" moltbook_sk
delete_previous moltter "$MOLTTER_ID" moltter_sk

# Publish functions
publish_moltx() {
  local content="$1"
  echo "📤 نشر إلى MoltX..."
  local resp
  resp=$(curl -s --connect-timeout 15 --max-time 60 -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer ${moltx_sk:-moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a}" \
    -H "Content-Type: application/json" \
    -d "{\"content\":$content,\"visibility\":\"public\"}")
  local id
  id=$(echo "$resp" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
  if [ -n "$id" ] && [ "$id" != "None" ]; then
    echo "✅ MoltX: $id"
    MOLTX_ID="$id"
    return 0
  else
    echo "❌ MoltX publish failed: $resp"
    return 1
  fi
}

publish_moltbook() {
  local content="$1"
  echo "📤 نشر إلى MoltBook..."
  local resp
  resp=$(curl -s --connect-timeout 15 --max-time 60 -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer ${moltbook_sk:-moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW}" \
    -H "Content-Type: application/json" \
    -d "{\"content\":$content,\"visibility\":\"public\"}")
  local id
  id=$(echo "$resp" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
  if [ -n "$id" ] && [ "$id" != "None" ]; then
    echo "✅ MoltBook: $id"
    MOLTBOOK_ID="$id"
    return 0
  else
    echo "❌ MoltBook publish failed (HTTP 403 = rate limit, safe to ignore)"
    return 1
  fi
}

publish_moltter() {
  local content="$1"
  echo "📤 نشر إلى Moltter..."
  local resp
  resp=$(curl -s --connect-timeout 15 --max-time 60 -X POST "https://api.molt.tw/v2/statuses" \
    -H "Authorization: Bearer ${moltter_sk:-moltter_sk_d8162b89d8204a5f94b5c6f8b2e1a7d9}" \
    -H "Content-Type: application/json" \
    -d "{\"status\":$content}")
  local id
  id=$(echo "$resp" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null || echo "")
  if [ -n "$id" ] && [ "$id" != "None" ]; then
    echo "✅ Moltter: $id"
    MOLTTER_ID="$id"
    return 0
  else
    echo "❌ Moltter publish failed"
    return 1
  fi
}

# ========== PUBLISH (with retry) ==========
MOLTX_OK=0; MOLTBOOK_OK=0; MOLTTER_OK=0

publish_moltx "$CONTENT_FULL" || true
sleep 1
publish_moltbook "$CONTENT_FULL" || true
sleep 1
publish_moltter "$CONTENT_FULL" || true

# Save IDs
jq -n \
  --arg moltx "$MOLTX_ID" --arg moltbook "$MOLTBOOK_ID" --arg moltter "$MOLTTER_ID" \
  '{moltx:$moltx, moltbook:$moltbook, moltter:$moltter}' > "$POST_IDS_FILE"

# Log to ledger
append_ledger "publish" "{\"mission\":\"$MISSION\",\"moltx\":\"$MOLTX_ID\",\"moltbook\":\"$MOLTBOOK_ID\",\"moltter\":\"$MOLTTER_ID\"}"

echo "" >> "$LOG_FILE"
echo "✅ **النشر اكتمل** — $MISSION" >> "$LOG_FILE"
echo " - MoltX: ${MOLTX_ID:-failed}" >> "$LOG_FILE"
echo " - MoltBook: ${MOLTBOOK_ID:-failed}" >> "$LOG_FILE"
echo " - Moltter: ${MOLTTER_ID:-failed}" >> "$LOG_FILE"

echo "🎉 بفضل الله — Mission [$MISSION] publish done"
exit 0
