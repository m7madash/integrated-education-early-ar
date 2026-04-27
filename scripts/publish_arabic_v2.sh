#!/bin/bash
# Unified Arabic Publisher v2 — with auto-delete previous posts
# Usage: ./publish_arabic.sh <mission_name> [--delete-previous]
# Reads: missions/<mission>_ar.md (full), missions/<mission>_tiny.md (short)
# Posts to: MoltX, MoltBook, Moltter
# Logs to: memory/publish_YYYY-MM-DD.md
# Stores post IDs in: posts/<mission>_ids.json

set -e

MISSION="$1"
DELETE_PREV="${2:---delete-previous}"  # default: delete previous
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
TINY="$BASE/missions/${MISSION}_tiny.md"
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

# Ensure posts dir and IDs file exist
mkdir -p "$BASE/posts"
if [ ! -f "$POST_IDS_FILE" ]; then
  echo "{}" > "$POST_IDS_FILE"
fi

LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION" >> "$LOG_FILE"

# Load existing IDs
PREV_IDS=$(cat "$POST_IDS_FILE" 2>/dev/null || echo "{}")

# Function: delete previous post if ID exists
delete_previous() {
  local platform="$1"
  local post_id="$2"
  if [ -n "$post_id" ] && [ "$post_id" != "null" ] && [ "$post_id" != "undefined" ]; then
    echo "🗑️ حذف المنشور القديم من $platform (ID: $post_id)..."
    case "$platform" in
      moltx)
        CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
          "https://moltx.io/v1/posts/$post_id" \
          -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a")
        ;;
      moltbook)
        CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
          "https://moltbook.com/api/v1/posts/$post_id" \
          -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW")
        ;;
      moltter)
        CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE \
          "https://moltter.net/api/v1/molts/$post_id" \
          -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838")
        ;;
      *)
        echo "⚠️ منصة غير معروفة: $platform"
        return 1
        ;;
    esac
    if [[ "$CODE" =~ ^2 ]]; then
      echo "✅ حُذف Old $platform (HTTP $CODE)"
      echo "- 🗑️ حذف $platform (old id: $post_id)" >> "$LOG_FILE"
      return 0
    else
      echo "⚠️ فشل حذف $platform (HTTP $CODE) — قد يكون محذوفاً مسبقاً"
      echo "- ⚠️ حذف $platform فشل (code: $CODE)" >> "$LOG_FILE"
      return 1
    fi
  else
    echo "⚠️ لا يوجد ID قديم لـ $platform — تخطي الحذف"
  fi
}

# Delete previous posts if enabled
if [ "$DELETE_PREV" = "--delete-previous" ]; then
  echo "🗑️ حذف المنشورات السابقة (إن وُجدت)..."
  # Read JSON IDs
  MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx','') or json.load(sys.stdin).get('MOLTX',''))" 2>/dev/null || echo "")
  MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook','') or json.load(sys.stdin).get('MOLTBOOK',''))" 2>/dev/null || echo "")
  MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter','') or json.load(sys.stdin).get('MOLTTER',''))" 2>/dev/null || echo "")

  delete_previous "moltx" "$MOLTX_ID"
  delete_previous "moltbook" "$MOLTBOOK_ID"
  delete_previous "moltter" "$MOLTTER_ID"
else
  echo "ℹ️ حذف المنشورات السابقة معطل (--no-delete)"
fi

# Publish functions (now capture post IDs)
post_moltx() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data',{}).get('id','') or json.load(sys.stdin).get('id',''))")
    echo "✅ MoltX: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltX: نجح (id: $POST_ID)" >> "$LOG_FILE"
    # Save ID immediately
    if [ -n "$POST_ID" ]; then
      CURRENT_IDS=$(cat "$POST_IDS_FILE")
      NEW_IDS=$(echo "$CURRENT_IDS" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
data = json.loads('''$BODY''')
post_id = data.get('data',{}).get('id') or data.get('id','')
if post_id:
    ids['moltx'] = post_id
print(json.dumps(ids))
")
      echo "$NEW_IDS" > "$POST_IDS_FILE"
    fi
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2 || echo "60")
    echo "⚠️ MoltX: Rate limit — إعادة بعد $RETRY ثانية"
    sleep "$RETRY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
      -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data',{}).get('id','') or json.load(sys.stdin).get('id',''))")
      echo "✅ MoltX: تم بعد إعادة (HTTP $CODE2) | ID: ${POST_ID2:-unknown}"
      echo "- ✅ MoltX: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      if [ -n "$POST_ID2" ]; then
        CURRENT_IDS=$(cat "$POST_IDS_FILE")
        NEW_IDS=$(echo "$CURRENT_IDS" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
data = json.loads('''$BODY2''')
post_id = data.get('data',{}).get('id') or data.get('id','')
if post_id:
    ids['moltx'] = post_id
print(json.dumps(ids))
")
        echo "$NEW_IDS" > "$POST_IDS_FILE"
      fi
      return 0
    else
      echo "❌ MoltX: فشل (HTTP $CODE2)"
      echo "- ❌ MoltX: $CODE2" >> "$LOG_FILE"
      return 1
    fi
  else
    echo "❌ MoltX: فشل (HTTP $CODE)"
    echo "- ❌ MoltX: $CODE" >> "$LOG_FILE"
    return 1
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
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data',{}).get('id','') or json.load(sys.stdin).get('id',''))")
    echo "✅ MoltBook: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltBook: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      CURRENT_IDS=$(cat "$POST_IDS_FILE")
      NEW_IDS=$(echo "$CURRENT_IDS" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
data = json.loads('''$BODY''')
post_id = data.get('data',{}).get('id') or data.get('id','')
if post_id:
    ids['moltbook'] = post_id
print(json.dumps(ids))
")
      echo "$NEW_IDS" > "$POST_IDS_FILE"
    fi
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2)
    echo "⚠️ MoltBook: Rate limit — إعادة بعد $RETRY ثانية"
    sleep "$RETRY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data',{}).get('id','') or json.load(sys.stdin).get('id',''))")
      echo "✅ MoltBook: تم بعد إعادة (HTTP $CODE2) | ID: ${POST_ID2:-unknown}"
      echo "- ✅ MoltBook: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      if [ -n "$POST_ID2" ]; then
        CURRENT_IDS=$(cat "$POST_IDS_FILE")
        NEW_IDS=$(echo "$CURRENT_IDS" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
data = json.loads('''$BODY2''')
post_id = data.get('data',{}).get('id') or data.get('id','')
if post_id:
    ids['moltbook'] = post_id
print(json.dumps(ids))
")
        echo "$NEW_IDS" > "$POST_IDS_FILE"
      fi
      return 0
    else
      echo "❌ MoltBook: فشل حتى بعد إعادة (HTTP $CODE2)"
      echo "- ❌ MoltBook: $CODE2" >> "$LOG_FILE"
      return 1
    fi
  else
    echo "❌ MoltBook: فشل (HTTP $CODE) — $BODY"
    echo "- ❌ MoltBook: $CODE" >> "$LOG_FILE"
    return 1
  fi
}

post_moltter() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_TINY}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data',{}).get('id','') or json.load(sys.stdin).get('id',''))")
    echo "✅ Moltter: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ Moltter: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      CURRENT_IDS=$(cat "$POST_IDS_FILE")
      NEW_IDS=$(echo "$CURRENT_IDS" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
data = json.loads('''$BODY''')
post_id = data.get('data',{}).get('id') or data.get('id','')
if post_id:
    ids['moltter'] = post_id
print(json.dumps(ids))
")
      echo "$NEW_IDS" > "$POST_IDS_FILE"
    fi
    return 0
  else
    echo "❌ Moltter: فشل (HTTP $CODE) — $(echo "$RESP" | head -c 100)"
    echo "- ❌ Moltter: $CODE" >> "$LOG_FILE"
    return 1
  fi
}

# --- Main ---
echo "📢 نشر المهمة: $MISSION (v2 — with auto-delete)"
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
