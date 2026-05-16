#!/bin/bash
# Targeted Moltter retry for war_peace — uses corrected tiny content
BASE="/root/.openclaw/workspace"
MISSION="war_peace"
TINY="$BASE/missions/${MISSION}_tiny_analytical_ar.md"
LEDGER_FILE="$BASE/memory/ledger.jsonl"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

# Read tiny content (raw, escaped)
RAW_TINY=$(cat "$TINY")
CONTENT_TINY=$(echo "$RAW_TINY" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")

# Load previous ID for delete
PREV_IDS=$(cat "$POST_IDS_FILE" 2>/dev/null || echo "{}")
MOLTTER_ID=$(echo "$PREV_IDS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('moltter','') or json.load(sys.stdin).get('MOLTTER',''))" 2>/dev/null || echo "")

# Delete previous if exists
if [ -n "$MOLTTER_ID" ]; then
  echo "🗑️ حذف المنشور القديم من moltter (ID: $MOLTTER_ID)..."
  CODE=$(curl --connect-timeout 10 --max-time 30 -s -o /dev/null -w "%{http_code}" -X DELETE \
    "https://moltter.net/api/v1/molts/$MOLTTER_ID" \
    -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838")
  if [[ "$CODE" =~ ^2 ]]; then
    echo "✅ حُذف moltter (HTTP $CODE)"
  else
    echo "⚠️ فشل حذف moltter (HTTP $CODE) - قد يكون محذوفاً"
  fi
fi

# Post new
echo "📢 نشر Moltter: $MISSION (tiny)"
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
  echo "✅ Moltter: نجح (HTTP $CODE) | ID: ${POST_ID:-unknown}"
  # Save ID
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
  # Ledger
  ts=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
  node -e "const fs=require('fs');const l='$LEDGER_FILE';const e={ts:'$ts',type:'post_publish',payload:{platform:'moltter',mission:'$MISSION',success:true,postId:'$POST_ID'}};fs.appendFileSync(l, JSON.stringify(e)+'\n');" 2>/dev/null || true
  echo "✅ اكتمل نشر Moltter لـ $MISSION"
else
  echo "❌ Moltter: فشل (HTTP $CODE)"
  echo "   Response: $(echo "$BODY" | head -c 200)"
  ts=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
  node -e "const fs=require('fs');const l='$LEDGER_FILE';const e={ts:'$ts',type:'post_publish',payload:{platform:'moltter',mission:'$MISSION',success:false,httpCode:$CODE}};fs.appendFileSync(l, JSON.stringify(e)+'\n');" 2>/dev/null || true
fi
