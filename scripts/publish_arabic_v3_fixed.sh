#!/bin/bash
# Unified Arabic Publisher v3 — With Content Shield Integration
# Reads: missions/<mission>_analytical_ar.md (+ tiny)
# Posts: MoltX, MoltBook, Moltter
# Filters: Content Shield v3 (context-aware) before publishing

set -e

# Load .env if present (auto-export all vars)
if [ -f "$BASE/.env" ]; then
  set -a
  . "$BASE/.env"
  set +a
fi

# Load platform credentials (priority: ~/.config/{platform}/credentials.json > .env)
for platform in moltter moltx moltbook; do
  ENV_VAR="${platform^^}_API_KEY"
  CRED_FILE="${HOME}/.config/${platform}/credentials.json"
  if [ -z "${!ENV_VAR}" ] && [ -f "$CRED_FILE" ]; then
    if command -v jq &> /dev/null; then
      VAL=$(jq -r '.api_key // empty' "$CRED_FILE" 2>/dev/null)
    else
      VAL=$(grep '"api_key"' "$CRED_FILE" | sed 's/.*"api_key"[[:space:]]*:[[:space:]]*"\\([^"]*\\)".*/\\1/')
    fi
    if [ -n "$VAL" ]; then
      export "${ENV_VAR}=${VAL}"
    fi
  fi
done

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_analytical_ar.md"
TINY="$BASE/missions/${MISSION}_tiny_ar.md"

[ -z "$MISSION" ] && { echo "❌ يرجى اسم المهمة (مثال: injustice-justice)"; exit 1; }

# Fallbacks
[ -f "$FILE" ] || FILE="$BASE/missions/${MISSION}_ar.md"
[ -f "$TINY" ] || TINY="$BASE/missions/${MISSION}_tiny.md"

[ -f "$FILE" ] || { echo "❌ ملف المهمة غير موجود: $FILE"; exit 1; }

# Moltter: pre-written short form (≤275 chars) preferred
MOLTTER_FILE="$BASE/missions/${MISSION}_moltter.md"
[ -f "$MOLTTER_FILE" ] || MOLTTER_FILE="$TINY"

# Load content (with JSON decoding)
RAW_FULL=$(cat "$FILE")
if echo "$RAW_FULL" | grep -q '\\n'; then
  CONTENT_FULL=$(echo "$RAW_FULL" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
else
  CONTENT_FULL=$(echo "$RAW_FULL" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
fi

# Load Moltter-specific short content
if [ -f "$MOLTTER_FILE" ]; then
  RAW_MOLTTER=$(cat "$MOLTTER_FILE")
  if echo "$RAW_MOLTTER" | grep -q '\\n'; then
    CONTENT_MOLTTER=$(echo "$RAW_MOLTTER" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
  else
    CONTENT_MOLTTER=$(echo "$RAW_MOLTTER" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read(), ensure_ascii=False))")
  fi
elif [ -f "$TINY" ]; then
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

# Load previous IDs (store old IDs for deletion after successful new publish)
PREV_IDS=$(cat "$POST_IDS_FILE")
OLD_MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx','') or json.load(sys.stdin).get('MOLTX',''))" 2>/dev/null || echo "")
OLD_MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook','') or json.load(sys.stdin).get('MOLTBOOK',''))" 2>/dev/null || echo "")
OLD_MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter','') or json.load(sys.stdin).get('MOLTTER',''))" 2>/dev/null || echo "")

# Initialize new IDs as empty
MOLTX_ID=""
MOLTBOOK_ID=""
MOLTTER_ID=""

delete_previous() {
  local platform="$1" post_id="$2" token_var="$3"
  [ -n "$post_id" ] && [ "$post_id" != "null" ] && [ "$post_id" != "undefined" ] || return 0
  echo "🗑️ حذف المنشور القديم من $platform (ID: $post_id)..."
  local CODE="000"
  case "$platform" in
    moltx)
      CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
        "https://moltx.io/v1/posts/$post_id" \
        -H "Authorization: Bearer ${!token_var}" 2>/dev/null) || true
      ;;
    moltbook)
      CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
        "https://moltbook.com/api/v1/posts/$post_id" \
        -H "Authorization: Bearer ${!token_var}" 2>/dev/null) || true
      ;;
    moltter)
      CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
        "${MOLTTER_BASE_URL:-https://moltter.net}/api/v1/molts/$post_id" \
        -H "Authorization: Bearer ${!token_var}" 2>/dev/null) || true
      ;;
  esac
  if [ "$CODE" = "200" ] || [ "$CODE" = "204" ]; then
    echo "✅ حُذف بنجاح"
  else
    echo "⚠️ حذف فشل (HTTP $CODE) — قد يكون المنشور محذوف مسبقاً"
  fi
}



# Publish functions
publish_moltx() {
  local content="$1"
  echo "📤 نشر إلى MoltX..."
  local resp=""
  resp=$(curl -s --connect-timeout 15 --max-time 60 -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer ${moltx_sk:-moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a}" \
    -H "Content-Type: application/json" \
    -d "{\"content\":$content,\"visibility\":\"public\"}" 2>/dev/null) || true
  local id
  id=$(echo "$resp" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id','') or data.get('data',{}).get('id',''))" 2>/dev/null || echo "")
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

  # ⏳ MoltBook Rate Limiter — enforce ≥2h gap between posts
  local MIN_GAP=$(( 2 * 60 * 60 ))   # 2 hours in seconds
  local LAST_MB_FILE="$BASE/memory/.last_moltbook_at"
  if [ -f "$LAST_MB_FILE" ]; then
    local last_ts
    last_ts=$(cat "$LAST_MB_FILE" | tr -d '\n')
    if [ -n "$last_ts" ]; then
      local now_epoch last_epoch gap_seconds
      now_epoch=$(date -u '+%s')
      last_epoch=$(date -u -d "$last_ts" '+%s' 2>/dev/null || date -u -j -f '%Y-%m-%dT%H:%M:%SZ' "$last_ts" '+%s' 2>/dev/null || echo 0)
      gap_seconds=$(( now_epoch - last_epoch ))
      if [ "$gap_seconds" -lt "$MIN_GAP" ] && [ "$last_epoch" -gt 0 ]; then
        local gap_min=$(( gap_seconds / 60 ))
        echo "⏳ MoltBook rate-limit guard: last post was ${gap_min}min ago (< 2h). Skipping to avoid rate limit."
        echo "   Next MoltBook attempt allowed at: $(date -u -d "$last_ts + 2 hours" '+%H:%M UTC')"
        return 0  # treated as ok — caller records partial_success
      fi
    fi
  fi

  echo "📤 نشر إلى MoltBook..."
  local resp=""
  local mb_title
  mb_title=$(echo "$content" | head -c 200 | cut -c1-200 | python3 -c "import sys; c=sys.stdin.read().strip(); print(c[:50])" 2>/dev/null || echo "مهمة جديدة")
  resp=$(curl -s --connect-timeout 15 --max-time 60 -X POST "${MOLTBOOK_BASE_URL:-https://www.moltbook.com}/api/v1/posts" \
    -H "Authorization: Bearer ${MOLTBOOK_API_KEY:-${moltbook_sk:-}}" \
    -H "Content-Type: application/json" \
    -d "{\"submolt\":\"introductions\",\"submolt_name\":\"introductions\",\"title\":$(python3 -c "import json,sys; t=sys.argv[1]; print(json.dumps(t[:200]))" "$content" 2>/dev/null || echo 'null'),\"content\":$content}" 2>/dev/null) || true
  local id
  id=$(echo "$resp" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id','') or data.get('data',{}).get('id',''))" 2>/dev/null || echo "")
  if [ -n "$id" ] && [ "$id" != "None" ]; then
    echo "✅ MoltBook: $id"
    MOLTBOOK_ID="$id"
    # ✅ Update rate-limit state: record this successful post timestamp
    date -u '+%Y-%m-%dT%H:%M:%SZ' > "$LAST_MB_FILE"
    return 0
  else
    echo "❌ MoltBook publish failed"
    return 1
  fi
}

# --- Moltter-safe truncation (≤275 display chars) ---
moltter_truncate() {
  local text="$1"
  python3 -c "
import sys, re
text = sys.stdin.read()
text = re.sub(r'^[#\s]+', '', text, flags=re.MULTILINE)
text = re.sub(r'[🤖📚📊🔍📱💡🌱✅❌🕌🛡️🔗\n]', ' ', text)
text = re.sub(r'#[^\s]+', ' ', text)
text = re.sub(r'—.+', '', text)
lines = [l.strip() for l in re.split(r'[。.,؟!]', text)
         if l.strip() and len(l.strip()) > 5 and not re.match(r'^[*\-•·]', l.strip())]
para = ' '.join(lines[:3])
if len(para) > 260:
    para = re.split(r'[\s,،]', para[:260])[0]
print(para.strip())
" <<< "$text"
}

publish_moltter() {
  local content="$1"
  echo "📤 نشر إلى Moltter..."
  local resp=""
  resp=$(curl -s --connect-timeout 15 --max-time 60 -X POST "${MOLTTER_BASE_URL:-https://moltter.net}/api/v1/molts" \
    -H "Authorization: Bearer ${MOLTTER_API_KEY:-${moltter_sk:-}}" \
    -H "Content-Type: application/json" \
    -d "{\"content\":$content}" 2>/dev/null) || true
  local id
  id=$(echo "$resp" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id','') or data.get('data',{}).get('id',''))" 2>/dev/null || echo "")
  if [ -n "$id" ] && [ "$id" != "None" ]; then
    echo "✅ Moltter: $id"
    MOLTTER_ID="$id"
    return 0
  else
    echo "❌ Moltter publish failed"
    return 1
  fi
}

# ========== PUBLISH (with retry + safe delete) ==========
MAX_ATTEMPTS=3
BASE_DELAY=60   # seconds

# --- Circuit Breaker: Parse enabled platforms from environment ---
# ENABLED_PLATFORMS is a comma-separated list (e.g., "moltx,moltbook,moltter")
# If not set, default to all platforms for backward compatibility
CIRCUIT_ENABLED=${CIRCUIT_BREAKER_ACTIVE:-0}
if [ "$CIRCUIT_ENABLED" = "1" ] && [ -n "$ENABLED_PLATFORMS" ]; then
  echo "🛡️  Circuit breaker active: publishing only to: $ENABLED_PLATFORMS"
  ENABLED_LIST="$ENABLED_PLATFORMS"
else
  echo "⚠️  Circuit breaker bypassed or not configured — attempting all platforms"
  ENABLED_LIST="moltx,moltbook,moltter"
fi

is_platform_enabled() {
  local p="$1"
  case ",$ENABLED_LIST," in
    *",$p,"*) return 0 ;;
    *) return 1 ;;
  esac
}

# --- MoltX ---
if is_platform_enabled "moltx"; then
  attempt=1
  while [ $attempt -le $MAX_ATTEMPTS ]; do
    echo "📤 [MoltX] Attempt $attempt/$MAX_ATTEMPTS"
    if publish_moltx "$CONTENT_FULL"; then
      echo "✅ MoltX succeeded on attempt $attempt"
      # Delete old post only after successful new publish
      if [ -n "$OLD_MOLTX_ID" ] && [ "$OLD_MOLTX_ID" != "null" ] && [ "$OLD_MOLTX_ID" != "undefined" ]; then
        delete_previous moltx "$OLD_MOLTX_ID" moltx_sk
      fi
      break
    else
      echo "❌ MoltX failed on attempt $attempt"
      if [ $attempt -lt $MAX_ATTEMPTS ]; then
        delay=$(( BASE_DELAY * (2 ** (attempt - 1)) ))
        echo "⏳ Waiting ${delay}s before retrying MoltX..."
        sleep $delay
      fi
    fi
    attempt=$((attempt + 1))
  done
  sleep 1
else
  echo "⏭️  MoltX skipped (circuit breaker: disabled or unhealthy)"
fi

sleep 1

# --- MoltBook ---
if is_platform_enabled "moltbook"; then
  attempt=1
  while [ $attempt -le $MAX_ATTEMPTS ]; do
    echo "📤 [MoltBook] Attempt $attempt/$MAX_ATTEMPTS"
    if publish_moltbook "$CONTENT_FULL"; then
      echo "✅ MoltBook succeeded on attempt $attempt"
      if [ -n "$OLD_MOLTBOOK_ID" ] && [ "$OLD_MOLTBOOK_ID" != "null" ] && [ "$OLD_MOLTBOOK_ID" != "undefined" ]; then
        delete_previous moltbook "$OLD_MOLTBOOK_ID" moltbook_sk
      fi
      break
    else
      echo "❌ MoltBook failed on attempt $attempt"
      if [ $attempt -lt $MAX_ATTEMPTS ]; then
        delay=$(( BASE_DELAY * (2 ** (attempt - 1)) ))
        echo "⏳ Waiting ${delay}s before retrying MoltBook..."
        sleep $delay
      fi
    fi
    attempt=$((attempt + 1))
  done
  sleep 1
else
  echo "⏭️  MoltBook skipped (circuit breaker: disabled or unhealthy)"
fi

# --- Moltter ---
if is_platform_enabled "moltter"; then
  attempt=1
  while [ $attempt -le $MAX_ATTEMPTS ]; do
    echo "📤 [Moltter] Attempt $attempt/$MAX_ATTEMPTS"
    if publish_moltter "${CONTENT_MOLTTER:-"$(moltter_truncate "$CONTENT_TINY")"}"; then
      echo "✅ Moltter succeeded on attempt $attempt"
      if [ -n "$OLD_MOLTTER_ID" ] && [ "$OLD_MOLTTER_ID" != "null" ] && [ "$OLD_MOLTTER_ID" != "undefined" ]; then
        delete_previous moltter "$OLD_MOLTTER_ID" MOLTTER_API_KEY
      fi
      break
    else
      echo "❌ Moltter failed on attempt $attempt"
      if [ $attempt -lt $MAX_ATTEMPTS ]; then
        delay=$(( BASE_DELAY * (2 ** (attempt - 1)) ))
        echo "⏳ Waiting ${delay}s before retrying Moltter..."
        sleep $delay
      fi
    fi
    attempt=$((attempt + 1))
  done
else
  echo "⏭️  Moltter skipped (circuit breaker: disabled or unhealthy)"
fi

# Save IDs
jq -n \
  --arg moltx "$MOLTX_ID" --arg moltbook "$MOLTBOOK_ID" --arg moltter "$MOLTTER_ID" \
  '{moltx:$moltx, moltbook:$moltbook, moltter:$moltter}' > "$POST_IDS_FILE"

# Determine overall mission status from platform results
successCount=0
platforms=""
[ -n "$MOLTX_ID" ] && { successCount=$((successCount+1)); platforms="${platforms}moltx,"; }
[ -n "$MOLTBOOK_ID" ] && { successCount=$((successCount+1)); platforms="${platforms}moltbook,"; }
[ -n "$MOLTTER_ID" ] && { successCount=$((successCount+1)); platforms="${platforms}moltter,"; }
platforms=${platforms%,}  # trim trailing comma

if [ $successCount -eq 3 ]; then
  status="full_success"
elif [ $successCount -gt 0 ]; then
  status="partial_success"
else
  status="failed"
fi

# Write publish_run ledger entry (atomic append)
node -e "const fs=require('fs');const p='/root/.openclaw/workspace/memory/ledger.jsonl';const e={ts:new Date().toISOString(),type:'publish_run',payload:{mission:process.argv[1],status:process.argv[2],platforms:process.argv[3],successCount:parseInt(process.argv[4]),postIds:{moltx:process.argv[5]||null,moltbook:process.argv[6]||null,moltter:process.argv[7]||null}}};fs.appendFileSync(p,JSON.stringify(e)+'\n');" "$MISSION" "$status" "$platforms" "$successCount" "$MOLTX_ID" "$MOLTBOOK_ID" "$MOLTTER_ID"

echo "" >> "$LOG_FILE"
echo "✅ **النشر اكتمل** — $MISSION" >> "$LOG_FILE"
echo " - MoltX: ${MOLTX_ID:-failed}" >> "$LOG_FILE"
echo " - MoltBook: ${MOLTBOOK_ID:-failed}" >> "$LOG_FILE"
echo " - Moltter: ${MOLTTER_ID:-failed}" >> "$LOG_FILE"

echo "🎉 بفضل الله — Mission [$MISSION] publish done"
exit 0
