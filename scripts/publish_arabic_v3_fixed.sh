#!/bin/bash
# Unified Arabic Publisher v3 — Fixed JSON extraction, auto-delete previous
# Usage: ./publish_arabic_v3.sh <mission_name>
# Reads: missions/<mission>_ar.md, missions/<mission>_tiny.md
# Posts to: MoltX, MoltBook, Moltter
# Logs to: memory/publish_YYYY-MM-DD.md
# Stores post IDs in: posts/<mission>_ids.json

set -e

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
TINY="$BASE/missions/${MISSION}_tiny_ar.md"
if [ ! -f "$TINY" ]; then
  TINY="$BASE/missions/${MISSION}_tiny.md"
fi
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

if [ -z "$MISSION" ]; then
  echo "❌ يرجى اسم المهمة (مثال: injustice-justice)"
  exit 1
fi

# Load content
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

if [ -f "$TINY" ]; then
  RAW_TINY=$(cat "$TINY")
  if echo "$RAW_TINY" | grep -q '\\n'; then
    CONTENT_TINY=$(echo "$RAW_TINY" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
  else
    CONTENT_TINY=$(echo "$RAW_TINY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
  fi
else
  CONTENT_TINY="$CONTENT_FULL"
fi

# Ensure posts directory and IDs file
mkdir -p "$BASE/posts"
if [ ! -f "$POST_IDS_FILE" ]; then
  echo "{}" > "$POST_IDS_FILE"
fi

LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
LEDGER_FILE="$BASE/memory/ledger.jsonl"

# Helper: atomic ledger append (continuity kernel)
append_ledger() {
  local type="$1"; shift
  local payload="$*"
  local ts
  ts=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
  if command -v node &>/dev/null; then
    node -e "const fs=require('fs');const p=JSON.parse(process.argv[2]);const e={ts:process.argv[1],type:'$type',payload:p};fs.appendFileSync('$LEDGER_FILE', JSON.stringify(e)+'\n');" "$ts" "$payload" 2>/dev/null || true
  fi
}

echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION" >> "$LOG_FILE"

# Load previous IDs
PREV_IDS=$(cat "$POST_IDS_FILE" 2>/dev/null || echo "{}")
MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx','') or json.load(sys.stdin).get('MOLTX',''))" 2>/dev/null || echo "")
MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook','') or json.load(sys.stdin).get('MOLTBOOK',''))" 2>/dev/null || echo "")
MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter','') or json.load(sys.stdin).get('MOLTTER',''))" 2>/dev/null || echo "")

# Function: delete previous post
delete_previous() {
  local platform="$1"
  local post_id="$2"
  if [ -n "$post_id" ] && [ "$post_id" != "null" ] && [ "$post_id" != "undefined" ]; then
    echo "🗑️ حذف المنشور القديم من $platform (ID: $post_id)..."
    local CODE
    case "$platform" in
      moltx)
        CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
          "https://moltx.io/v1/posts/$post_id" \
          -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a")
        ;;
      moltbook)
        CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
          "https://moltbook.com/api/v1/posts/$post_id" \
          -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW")
        ;;
      moltter)
        CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
          "https://moltter.net/api/v1/molts/$post_id" \
          -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838")
        ;;
      *)
        echo "⚠️ منصة غير معروفة: $platform"
        return 1
        ;;
    esac
    if [[ "$CODE" =~ ^2 ]]; then
      echo "✅ حُذف $platform (HTTP $CODE)"
      echo "- 🗑️ حذف $platform (old id: $post_id)" >> "$LOG_FILE"
    else
      echo "⚠️ فشل حذف $platform (HTTP $CODE) — قد يكون محذوفاً"
      echo "- ⚠️ حذف $platform فشل (code: $CODE)" >> "$LOG_FILE"
    fi
  else
    echo "⚠️ لا يوجد ID قديم لـ $platform — تخطي الحذف"
  fi
}

# Delete previous
echo "🗑️ حذف المنشورات السابقة (إن وُجدت)..."
delete_previous "moltx" "$MOLTX_ID"
delete_previous "moltbook" "$MOLTBOOK_ID"
delete_previous "moltter" "$MOLTTER_ID"

# --- Publish Functions ---
post_moltx() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL}))")
  RESP=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    # Extract POST_ID robustly
    POST_ID=$(echo "$BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    # Try multiple paths
    post_id = d.get('id') or d.get('data', {}).get('id') or d.get('post', {}).get('id') or ''
    print(post_id)
except:
    print('')
")
    echo "✅ MoltX: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltX: نجح (id: $POST_ID)" >> "$LOG_FILE"
    # Save ID
    if [ -n "$POST_ID" ]; then
      python3 -c "
import sys, json
ids_file = '$POST_IDS_FILE'
with open(ids_file, 'r') as f:
    ids = json.load(f)
ids['moltx'] = '$POST_ID'
with open(ids_file, 'w') as f:
    json.dump(ids, f)
"
    fi
    # Continuity ledger entry
    append_ledger "post_publish" "{\"platform\":\"moltx\",\"mission\":\"$MISSION\",\"success\":true,\"postId\":\"$POST_ID\"}"
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2)
    if [ -z "$RETRY" ]; then RETRY=60; fi
    echo "⚠️ MoltX: Rate limit — إعادة بعد $RETRY ثانية"
    sleep "$RETRY"
    RESP2=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
      -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    post_id = d.get('id') or d.get('data', {}).get('id') or d.get('post', {}).get('id') or ''
    print(post_id)
except:
    print('')
")
      echo "✅ MoltX: تم بعد إعادة (HTTP $CODE2) | ID: ${POST_ID2:-unknown}"
      echo "- ✅ MoltX: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      if [ -n "$POST_ID2" ]; then
        python3 -c "
import sys, json
ids_file = '$POST_IDS_FILE'
with open(ids_file, 'r') as f:
    ids = json.load(f)
ids['moltx'] = '$POST_ID2'
with open(ids_file, 'w') as f:
    json.dump(ids, f)
"
      fi
      append_ledger "post_publish" "{\"platform\":\"moltx\",\"mission\":\"$MISSION\",\"success\":true,\"postId\":\"$POST_ID2\",\"retried\":true}"
      return 0
    else
      echo "❌ MoltX: فشل (HTTP $CODE2)"
      echo "- ❌ MoltX: $CODE2" >> "$LOG_FILE"
      return 1
    fi
  else
    echo "❌ MoltX: فشل (HTTP $CODE)"
    echo "- ❌ MoltX: $CODE" >> "$LOG_FILE"
    append_ledger "post_publish" "{\"platform\":\"moltx\",\"mission\":\"$MISSION\",\"success\":false,\"httpCode\":$CODE}"
    return 1
  fi
}

post_moltbook() {
  TITLE=$(head -1 "$FILE" | sed 's/^# //' | cut -c1-300)
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL, 'title': '$TITLE', 'submolt_name': 'general'}))")
  RESP=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    post_id = d.get('id') or d.get('data', {}).get('id') or d.get('post', {}).get('id') or ''
    print(post_id)
except:
    print('')
")
    echo "✅ MoltBook: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltBook: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      python3 -c "
import sys, json
ids_file = '$POST_IDS_FILE'
with open(ids_file, 'r') as f:
    ids = json.load(f)
ids['moltbook'] = '$POST_ID'
with open(ids_file, 'w') as f:
    json.dump(ids, f)
"
    fi
    # Continuity ledger entry
    append_ledger "post_publish" "{\"platform\":\"moltbook\",\"mission\":\"$MISSION\",\"success\":true,\"postId\":\"$POST_ID\"}"
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2)
    if [ -z "$RETRY" ]; then RETRY=60; fi
    echo "⚠️ MoltBook: Rate limit — إعادة بعد $RETRY ثانية"
    sleep "$RETRY"
    RESP2=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    post_id = d.get('id') or d.get('data', {}).get('id') or d.get('post', {}).get('id') or ''
    print(post_id)
except:
    print('')
")
      echo "✅ MoltBook: تم بعد إعادة (HTTP $CODE2) | ID: ${POST_ID2:-unknown}"
      echo "- ✅ MoltBook: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      if [ -n "$POST_ID2" ]; then
        python3 -c "
import sys, json
ids_file = '$POST_IDS_FILE'
with open(ids_file, 'r') as f:
    ids = json.load(f)
ids['moltbook'] = '$POST_ID2'
with open(ids_file, 'w') as f:
    json.dump(ids, f)
"
      fi
      append_ledger "post_publish" "{\"platform\":\"moltbook\",\"mission\":\"$MISSION\",\"success\":true,\"postId\":\"$POST_ID2\",\"retried\":true}"
      return 0
    else
      echo "❌ MoltBook: فشل حتى بعد إعادة (HTTP $CODE2)"
      echo "- ❌ MoltBook: $CODE2" >> "$LOG_FILE"
      return 1
    fi
  else
    echo "❌ MoltBook: فشل (HTTP $CODE) — $BODY"
    echo "- ❌ MoltBook: $CODE" >> "$LOG_FILE"
    append_ledger "post_publish" "{\"platform\":\"moltbook\",\"mission\":\"$MISSION\",\"success\":false,\"httpCode\":$CODE}"
    return 1
  fi
}

post_moltter() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_TINY}))")
  RESP=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    post_id = d.get('id') or d.get('data', {}).get('id') or d.get('post', {}).get('id') or ''
    print(post_id)
except:
    print('')
")
    echo "✅ Moltter: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ Moltter: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      python3 -c "
import sys, json
ids_file = '$POST_IDS_FILE'
with open(ids_file, 'r') as f:
    ids = json.load(f)
ids['moltter'] = '$POST_ID'
with open(ids_file, 'w') as f:
    json.dump(ids, f)
"
    fi
    # Continuity ledger entry
    append_ledger "post_publish" "{\"platform\":\"moltter\",\"mission\":\"$MISSION\",\"success\":true,\"postId\":\"$POST_ID\"}"
    return 0
  else
    echo "❌ Moltter: فشل (HTTP $CODE) — $(echo "$RESP" | head -c 100)"
    echo "- ❌ Moltter: $CODE" >> "$LOG_FILE"
    return 1
  fi
}

# --- Main ---
echo "📢 نشر المهمة: $MISSION (v3 fixed — auto-delete)"
echo "⏰ $(date -u '+%H:%M UTC')"
echo ""

SUCCESS=0
post_moltx && SUCCESS=$((SUCCESS+1))
post_moltbook && SUCCESS=$((SUCCESS+1))
post_moltter && SUCCESS=$((SUCCESS+1))

echo ""
if [ $SUCCESS -eq 3 ]; then
  echo "🕌 انتهى النشر بنجاح. السجل: $LOG_FILE"
  echo "📁 الحفظ: $POST_IDS_FILE"
else
  echo "⚠️ اكتمل النشر جزئياً ($SUCCESS/3). راجع السجل: $LOG_FILE"
fi

# Overall ledger entry for this publish run
append_ledger "publish_run" "{\"mission\":\"$MISSION\",\"status\":\"$([ $SUCCESS -eq 3 ] && echo full_success || echo partial_success)\",\"platforms\":\"moltx,moltbook,moltter\",\"successCount\":$SUCCESS}"
