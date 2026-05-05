#!/bin/bash
# MoltX-only re-publisher for a mission (fixes MoltX without touching MoltBook/Moltter)
# Usage: ./republish_moltx.sh <mission_name>

MISSION="$1"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

if [ -z "$MISSION" ]; then
  echo "❌ يرجى اسم المهمة"
  exit 1
fi

if [ ! -f "$FILE" ]; then
  echo "❌ ملف غير موجود: $FILE"
  exit 1
fi

RAW=$(cat "$FILE")
if echo "$RAW" | grep -q '\\n'; then
  CONTENT=$(echo "$RAW" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
else
  CONTENT=$(echo "$RAW" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")
fi

# Verify religious gate
if ! node "$BASE/scripts/verify_full_arabic.js" "$MISSION" "$FILE" 2>/dev/null; then
  echo "❌ فشل التحقق العقدي"
  exit 1
fi
if ! "$BASE/scripts/verify_mission_religious.sh" "$MISSION" "$FILE" 2>/dev/null; then
  echo "❌ فشل التحقق الشرعي"
  exit 1
fi

# Load existing IDs
if [ -f "$POST_IDS_FILE" ]; then
  PREV_IDS=$(cat "$POST_IDS_FILE")
  MOLTX_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltx','') or json.load(sys.stdin).get('MOLTX',''))" 2>/dev/null || echo "")
  MOLTBOOK_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltbook','') or json.load(sys.stdin).get('MOLTBOOK',''))" 2>/dev/null || echo "")
  MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter','') or json.load(sys.stdin).get('MOLTTER',''))" 2>/dev/null || echo "")
else
  MOLTX_ID=""; MOLTBOOK_ID=""; MOLTTER_ID=""
fi

echo "🎯 MoltX-only republish for: $MISSION"
echo "  Existing MoltX ID: ${MOLTX_ID:-none}"

# Delete old MoltX post if exists
if [ -n "$MOLTX_ID" ] && [ "$MOLTX_ID" != "null" ] && [ "$MOLTX_ID" != "undefined" ]; then
  echo "🗑️ حذف MoltX القديم (ID: $MOLTX_ID)..."
  CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
    "https://moltx.io/v1/posts/$MOLTX_ID" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a")
  echo "   HTTP $CODE"
fi

# Post fresh to MoltX
echo "📢 نشر MoltX جديد..."
JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT}))")
RESP=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
  -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
  -H "Content-Type: application/json" -d "$JSON")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')

if [[ "$CODE" =~ ^2 ]]; then
  NEW_ID=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data',{}).get('id',''))")
  echo "✅ MoltX نجح | ID: $NEW_ID"
  # Update IDs file (keep MoltBook/Moltter, replace MoltX)
  if [ -f "$POST_IDS_FILE" ]; then
    python3 -c "
import json, sys
path='$POST_IDS_FILE'
with open(path) as f: ids=json.load(f)
ids['moltx']='$NEW_ID'
with open(path,'w') as f: json.dump(ids, f, indent=2)
print('Updated ids file')
"
  else
    echo \"{\\\"moltx\\\": \\\"$NEW_ID\\\"}\" > "$POST_IDS_FILE"
  fi
else
  echo "❌ MoltX فشل (HTTP $CODE)"
  exit 1
fi

echo "✅ اكتمل إصلاح MoltX لـ $MISSION"
