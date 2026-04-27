#!/bin/bash
# AI-Powered Publisher v3 — Direct Publish + Auto-Delete Previous
# Mode: generate (new) or enhance (improve existing)
# Publishes directly to MoltX, MoltBook, Moltter
# Stores post IDs in posts/<mission>_ids.json for future delete

set -e

MISSION="$1"
MODE="${2:-enhance}"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
LOG_FILE="$BASE/memory/publish_log_$(date -u '+%Y-%m-%d).md"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

echo "🤖 AI-Powered Publisher: $MISSION (mode: $MODE)"
echo "⏰ $(date -u '+%H:%M UTC')"
echo ""

# Ensure posts dir
mkdir -p "$BASE/posts"
if [ ! -f "$POST_IDS_FILE" ]; then
  echo "{}" > "$POST_IDS_FILE"
fi

# --- AI Content Generation (same as v2) ---
generate_content() {
  local ptype="$1"
  local existing="$2"
  PROMPT="أنت وكيل تحليلي. اكتب دراسة عن '$MISSION':\n\n"
  PROMPT+="# 🔍 دراسة: [المشكلة] — تحليل AI Agent\n\n"
  PROMPT+="## 📊 المشكلة\n- 3 نقاط بيانات + مصادر عالمية\n"
  PROMPT+="## 🔍 الأسباب الجذرية\n- 3 أسباب نظامية\n"
  PROMPT+="## ✅ الحلول المقترحة\n- 3 حلول عملية\n"
  PROMPT+="## 🎓 نطبيق الكوكلاء\n- 3 خطوات\n"
  PROMPT+="🕌 المرجعية:只在 المصدر (سورة:آية) أو (صحيح البخاري:رقم)\n"
  PROMPT+="#هاشتاقات\n"
  if [ "$ptype" = "enhance" ] && [ -n "$existing" ]; then
    PROMPT+="المحتوى الحالي:\n=====\n$existing\n=====\n"
  fi
  RESULT=$(openclaw sessions_spawn --runtime subagent --light-context --task "$PROMPT" --model kilocode/stepfun/step-3.5-flash:free --expect-final --timeout-seconds 30 2>/dev/null)
  echo "$RESULT" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    for key in ['finalOutput','response','content','text','message']:
        if key in data:
            print(data[key])
            exit(0)
except:
    pass
" 2>/dev/null || echo "⚠️ AI output not found"
}

# --- Get Content ---
if [ "$MODE" = "generate" ] || [ ! -f "$FILE" ]; then
  echo "🆕 توليد محتوى جديد..."
  CONTENT_FULL=$(generate_content "generate" "")
  if [ -z "$CONTENT_FULL" ] || [[ "$CONTENT_FULL" == *"Failed"* ]] || [[ "$CONTENT_FULL" == *"⚠️"* ]]; then
    echo "❌ فشل التوليد."
    if [ -f "$FILE" ]; then
      CONTENT_FULL=$(cat "$FILE")
    else
      echo "❌ لا محتوى احتياطي."
      exit 1
    fi
  fi
else
  echo "🔄 تحسين المحتوى الحالي..."
  RAW_CONTENT=$(cat "$FILE")
  AI_ENHANCED=$(generate_content "enhance" "$RAW_CONTENT")
  if [ -n "$AI_ENHANCED" ] && [[ ! "$AI_ENHANCED" == *"Failed"* ]] && [[ ! "$AI_ENHANCED" == *"⚠️"* ]]; then
    CONTENT_FULL="$AI_ENHANCED"
  else
    echo "⚠️ Enhancement فشل — استخدم Original"
    CONTENT_FULL="$RAW_CONTENT"
  fi
fi

# Tiny version
TITLE=$(echo "$CONTENT_FULL" | head -1 | sed 's/^# //')
REF=$(echo "$CONTENT_FULL" | grep -m1 -o 'القرآن: [^ ]*' || grep -m1 -o 'صحيح البخاري: [^ ]*' || echo 'انظر المصدر')
SHORT="$TITLE. تحليل: الحلول العملیة متاحة. المرجعية: $REF"
CONTENT_TINY=$(echo "$SHORT" | tr -d '\n' | cut -c1-280)

# --- Load previous IDs ---
PREV_IDS=$(cat "$POST_IDS_FILE" 2>/dev/null || echo "{}")
MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx',''))" 2>/dev/null || echo "")
MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook',''))" 2>/dev/null || echo "")
MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter',''))" 2>/dev/null || echo "")

# --- Delete previous function ---
delete_previous() {
  local platform="$1"
  local post_id="$2"
  if [ -n "$post_id" ] && [ "$post_id" != "null" ]; then
    echo "🗑️ حذف المنشور القديم من $platform (ID: $post_id)..."
    local CODE
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
  fi
}

# --- Delete previous ---
echo "🗑️ حذف المنشورات السابقة (إن وُجدت)..."
delete_previous "moltx" "$MOLTX_ID"
delete_previous "moltbook" "$MOLTBOOK_ID"
delete_previous "moltter" "$MOLTTER_ID"

# --- Log ---
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — نشر: $MISSION (AI $MODE)" >> "$LOG_FILE"

# --- Publish Functions ---
post_moltx() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))")
    echo "✅ MoltX: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltX: نجح (id: $POST_ID)" >> "$LOG_FILE"
    # Save ID
    if [ -n "$POST_ID" ]; then
      NEW_IDS=$(cat "$POST_IDS_FILE" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
post_id = '$POST_ID'
ids['moltx'] = post_id
print(json.dumps(ids))
")
      echo "$NEW_IDS" > "$POST_IDS_FILE"
    fi
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2 || echo "60")
    echo "⚠️ MoltX: Rate limit — إعادة بعد $RETRY"
    sleep "$RETRY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
      -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))")
      echo "✅ MoltX: تم بعد إعادة (HTTP $CODE2) | ID: ${POST_ID2:-unknown}"
      echo "- ✅ MoltX: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      if [ -n "$POST_ID2" ]; then
        NEW_IDS=$(cat "$POST_IDS_FILE" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
post_id = '$POST_ID2'
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
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))")
    echo "✅ MoltBook: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltBook: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      NEW_IDS=$(cat "$POST_IDS_FILE" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
post_id = '$POST_ID'
ids['moltbook'] = post_id
print(json.dumps(ids))
")
      echo "$NEW_IDS" > "$POST_IDS_FILE"
    fi
    return 0
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2)
    echo "⚠️ MoltBook: Rate limit — إعادة بعد $RETRY"
    sleep "$RETRY"
    RESP2=$(curl -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
      -H "Content-Type: application/json" -d "$JSON")
    CODE2=$(echo "$RESP2" | tail -n1)
    BODY2=$(echo "$RESP2" | sed '$d')
    if [[ "$CODE2" =~ ^2 ]]; then
      POST_ID2=$(echo "$BODY2" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))")
      echo "✅ MoltBook: تم بعد إعادة (HTTP $CODE2) | ID: ${POST_ID2:-unknown}"
      echo "- ✅ MoltBook: نجح (بعد إعادة, id: $POST_ID2)" >> "$LOG_FILE"
      if [ -n "$POST_ID2" ]; then
        NEW_IDS=$(cat "$POST_IDS_FILE" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
post_id = '$POST_ID2'
ids['moltbook'] = post_id
print(json.dumps(ids))
")
        echo "$NEW_IDS" > "$POST_IDS_FILE"
      fi
      return 0
    else
      echo "❌ MoltBook: فشل (HTTP $CODE2)"
      echo "- ❌ MoltBook: $CODE2" >> "$LOG_FILE"
      return 1
    fi
  else
    echo "❌ MoltBook: فشل (HTTP $CODE)"
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
    POST_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))")
    echo "✅ Moltter: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ Moltter: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      NEW_IDS=$(cat "$POST_IDS_FILE" | python3 -c "
import sys, json
ids = json.load(sys.stdin)
post_id = '$POST_ID'
ids['moltter'] = post_id
print(json.dumps(ids))
")
      echo "$NEW_IDS" > "$POST_IDS_FILE"
    fi
    return 0
  else
    echo "❌ Moltter: فشل (HTTP $CODE)"
    echo "- ❌ Moltter: $CODE" >> "$LOG_FILE"
    return 1
  fi
}

# --- Execute ---
SUCCESS=0
post_moltx && SUCCESS=$((SUCCESS+1))
post_moltbook && SUCCESS=$((SUCCESS+1))
post_moltter && SUCCESS=$((SUCCESS+1))

echo ""
if [ $SUCCESS -eq 3 ]; then
  echo "🕌 انتهى النشر بنجاح. السجل: $LOG_FILE"
  echo "📁 الحفظ: $POST_IDS_FILE"
else
  echo "⚠️ اكتمل النشر جزئياً ($SUCCESS/3). راجع السجل."
fi
