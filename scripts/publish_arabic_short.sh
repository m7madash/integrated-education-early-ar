#!/bin/bash
# Unified Arabic Publisher v4 — Minimal output for cron delivery
# نفس مميزات v3 fixed لكن مع إخراج مختصر

set -e

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
TINY="$BASE/missions/${MISSION}_tiny.md"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

if [ -z "$MISSION" ]; then
  echo "❌ يرجى اسم المهمة"
  exit 1
fi

# Load content
if [ ! -f "$FILE" ]; then
  echo "❌ ملف غير موجود: $FILE"
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

mkdir -p "$BASE/posts"
[ -f "$POST_IDS_FILE" ] || echo "{}" > "$POST_IDS_FILE"

LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d').md"
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION" >> "$LOG_FILE"

PREV_IDS=$(cat "$POST_IDS_FILE" 2>/dev/null || echo "{}")
MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx',''))" 2>/dev/null || echo "")
MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook',''))" 2>/dev/null || echo "")
MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter',''))" 2>/dev/null || echo "")

delete_previous() {
  local platform="$1"; local post_id="$2"
  if [ -n "$post_id" ] && [ "$post_id" != "null" ] && [ "$post_id" != "undefined" ]; then
    case "$platform" in
      moltx) CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "https://moltx.io/v1/posts/$post_id" -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a") ;;
      moltbook) CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "https://moltbook.com/api/v1/posts/$post_id" -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW") ;;
      moltter) CODE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "https://moltter.net/api/v1/molts/$post_id" -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838") ;;
      *) return 1 ;;
    esac
    if [[ "$CODE" =~ ^2 ]]; then
      echo "- 🗑️ حذف $platform (old id: $post_id)" >> "$LOG_FILE"
    fi
  fi
}

echo "🗑️ حذف القديم..."
delete_previous "moltx" "$MOLTX_ID"
delete_previous "moltbook" "$MOLTBOOK_ID"
delete_previous "moltter" "$MOLTTER_ID"

post_moltx() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1); BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or d.get('post',{}).get('id') or '')")
    echo "- ✅ MoltX: نجح (id: $POST_ID)" >> "$LOG_FILE"
    [ -n "$POST_ID" ] && python3 -c "import json; ids=json.load(open('$POST_IDS_FILE')); ids['moltx']='$POST_ID'; json.dump(ids,open('$POST_IDS_FILE','w'))"
    echo "✅ MoltX:$POST_ID"
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2 || echo "60")
    sleep "$RETRY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1); BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or d.get('post',{}).get('id') or '')")
      echo "- ✅ MoltX: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      [ -n "$POST_ID2" ] && python3 -c "import json; ids=json.load(open('$POST_IDS_FILE')); ids['moltx']='$POST_ID2'; json.dump(ids,open('$POST_IDS_FILE','w'))"
      echo "✅ MoltX:$POST_ID2"
      return 0
    else
      echo "- ❌ MoltX: $CODE2" >> "$LOG_FILE"
      echo "❌ MoltX:$CODE2"
      return 1
    fi
  else
    echo "- ❌ MoltX: $CODE" >> "$LOG_FILE"
    echo "❌ MoltX:$CODE"
    return 1
  fi
}

post_moltbook() {
  TITLE=$(head -1 "$FILE" | sed 's/^# //' | cut -c1-300)
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL, 'title': '$TITLE', 'submolt_name': 'general'}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1); BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or d.get('post',{}).get('id') or '')")
    echo "- ✅ MoltBook: نجح (id: $POST_ID)" >> "$LOG_FILE"
    [ -n "$POST_ID" ] && python3 -c "import json; ids=json.load(open('$POST_IDS_FILE')); ids['moltbook']='$POST_ID'; json.dump(ids,open('$POST_IDS_FILE','w'))"
    echo "✅ MoltBook:$POST_ID"
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2)
    sleep "$RETRY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1); BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or d.get('post',{}).get('id') or '')")
      echo "- ✅ MoltBook: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      [ -n "$POST_ID2" ] && python3 -c "import json; ids=json.load(open('$POST_IDS_FILE')); ids['moltbook']='$POST_ID2'; json.dump(ids,open('$POST_IDS_FILE','w'))"
      echo "✅ MoltBook:$POST_ID2"
      return 0
    else
      echo "- ❌ MoltBook: $CODE2" >> "$LOG_FILE"
      echo "❌ MoltBook:$CODE2"
      return 1
    fi
  else
    echo "- ❌ MoltBook: $CODE" >> "$LOG_FILE"
    echo "❌ MoltBook:$CODE"
    return 1
  fi
}

post_moltter() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_TINY}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1); BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or d.get('post',{}).get('id') or '')")
    echo "- ✅ Moltter: نجح (id: $POST_ID)" >> "$LOG_FILE"
    [ -n "$POST_ID" ] && python3 -c "import json; ids=json.load(open('$POST_IDS_FILE')); ids['moltter']='$POST_ID'; json.dump(ids,open('$POST_IDS_FILE','w'))"
    echo "✅ Moltter:$POST_ID"
    return 0
  else
    echo "- ❌ Moltter: $CODE" >> "$LOG_FILE"
    echo "❌ Moltter:$CODE"
    return 1
  fi
}

# --- Execute ---
SUCCESS=0
post_moltx && SUCCESS=$((SUCCESS+1))
post_moltbook && SUCCESS=$((SUCCESS+1))
post_moltter && SUCCESS=$((SUCCESS+1))

# Minimal output only (for cron delivery)
if [ $SUCCESS -eq 3 ]; then
  echo "✅ نشر: $MISSION — MoltX:$MOLTX_ID MoltBook:$MOLTBOOK_ID Moltter:$MOLTTER_ID"
else
  echo "⚠️ نشر جزئي: $MISSION ($SUCCESS/3)"
fi
