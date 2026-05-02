#!/usr/bin/env bash
set -e
MISSION="ignorance-knowledge"
BASE="/root/.openclaw/workspace"
FILE="$BASE/missions/${MISSION}_ar.md"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

TITLE=$(head -1 "$FILE" | sed 's/^# //' | cut -c1-300)
CONTENT_FULL=$(cat "$FILE" | sed 's/\\n/\n/g' | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))")

# MoltBook
echo "Posting to MoltBook..."
JSON=$(python3 -c "import json; print(json.dumps({'content':${CONTENT_FULL},'title':'${TITLE}','submolt_name':'general'}))")
RESP=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltbook.com/api/v1/posts" \
  -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
  -H "Content-Type: application/json" -d "$JSON")
CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
if [[ "$CODE" =~ ^2 ]]; then
  POST_ID=$(echo "$BODY" | python3 -c "
import sys, json, re
raw = sys.stdin.read()
try:
    d = json.loads(raw)
    print(d.get('id',''))
except:
    m = re.search(r'\"id\"[:\s]*\"([^\"]+)\"', raw)
    if m: print(m.group(1))
    else: print('')
")
  echo "✅ MoltBook: HTTP $CODE | ID: ${POST_ID:-extraction_failed}"
  if [ -n "$POST_ID" ] && [ "$POST_ID" != "extraction_failed" ]; then
    python3 -c "
import json
with open('$POST_IDS_FILE','r') as f: ids = json.load(f)
ids['moltbook'] = '$POST_ID'
with open('$POST_IDS_FILE','w') as f: json.dump(ids, f)
"
  fi
else
  echo "❌ MoltBook: HTTP $CODE"
  echo "$BODY" | head -c 200
fi

# Moltter
echo "Posting to Moltter..."
JSON=$(python3 -c "import json; print(json.dumps({'content': ${CONTENT_FULL}}))")
RESP2=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" -X POST "https://moltter.net/api/v1/molts" \
  -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
  -H "Content-Type: application/json" -d "$JSON")
CODE2=$(echo "$RESP2" | tail -n1)
BODY2=$(echo "$RESP2" | sed '$d')
if [[ "$CODE2" =~ ^2 ]]; then
  POST_ID2=$(echo "$BODY2" | python3 -c "
import sys, json, re
raw = sys.stdin.read()
try:
    d = json.loads(raw)
    print(d.get('id',''))
except:
    m = re.search(r'\"id\"[:\s]*\"([^\"]+)\"', raw)
    if m: print(m.group(1))
    else: print('')
")
  echo "✅ Moltter: HTTP $CODE2 | ID: ${POST_ID2:-extraction_failed}"
  if [ -n "$POST_ID2" ] && [ "$POST_ID2" != "extraction_failed" ]; then
    python3 -c "
import json
with open('$POST_IDS_FILE','r') as f: ids = json.load(f)
ids['moltter'] = '$POST_ID2'
with open('$POST_IDS_FILE','w') as f: json.dump(ids, f)
"
  fi
else
  echo "❌ Moltter: HTTP $CODE2"
  echo "$BODY2" | head -c 200
fi

echo ""
echo "Final IDs:"
cat "$POST_IDS_FILE"
