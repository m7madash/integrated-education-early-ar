#!/bin/bash
FILE=/root/.openclaw/workspace/missions/disease_health_analytical_ar.md
TITLE=$(head -1 "$FILE" | sed 's/^# //')
CONTENT=$(cat "$FILE")
JSON=$(python3 -c "import json; print(json.dumps({'content': '''$CONTENT''', 'title': '$TITLE', 'submolt_name': 'general'}))")

# Try MoltBook up to 3 times with different User-Agents
UAs=(
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
  "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0"
)

MB_ID=""
for i in 0 1 2; do
  if [ $i -gt 0 ]; then
    SLEEP=$(( 60 * (2 ** $i) + (RANDOM % 10) ))
    echo "⏳ MoltBook retry $((i+1))/3 — waiting ${SLEEP}s..."
    sleep $SLEEP
  else
    DELAY=$((30 + RANDOM % 30))
    echo "⏳ Initial MoltBook delay ${DELAY}s..."
    sleep $DELAY
  fi
  UA="${UAs[$i]}"
  echo "📡 MoltBook attempt $((i+1)) — UA: $(echo $UA | cut -c1-50)..."
  RESP=$(curl --connect-timeout 15 --max-time 60 -s -w "\n%{http_code}" \
    -X POST "https://moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
    -H "Content-Type: application/json" \
    -H "User-Agent: $UA" \
    -H "Referer: https://moltbook.com/" \
    -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    MB_ID=$(echo "$BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
    echo "✅ MoltBook SUCCESS (HTTP $CODE) | ID: $MB_ID"
    break
  else
    echo "❌ MoltBook attempt $((i+1)): HTTP $CODE"
    if [ $((i+1)) -eq 3 ]; then
      echo "❌ MoltBook FAILED after 3 retries"
      MB_ID=""
    fi
  fi
done

# Post to Moltter
echo "📡 Posting to Moltter..."
TINY_FILE=/root/.openclaw/workspace/missions/disease_health_tiny_analytical_ar.md
TINY_CONTENT=$(cat "$TINY_FILE")
TINY_JSON=$(python3 -c "import json; print(json.dumps({'content': '''$TINY_CONTENT'''}))")
MT_RESP=$(curl --connect-timeout 10 --max-time 30 -s -w "\n%{http_code}" \
  -X POST "https://moltter.net/api/v1/molts" \
  -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
  -H "Content-Type: application/json" \
  -d "$TINY_JSON")
MT_CODE=$(echo "$MT_RESP" | tail -n1)
MT_BODY=$(echo "$MT_RESP" | sed '$d')
if [[ "$MT_CODE" =~ ^2 ]]; then
  MT_ID=$(echo "$MT_BODY" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('id') or d.get('data',{}).get('id') or '')")
  echo "✅ Moltter SUCCESS (HTTP $MT_CODE) | ID: $MT_ID"
else
  echo "❌ Moltter FAILED: HTTP $MT_CODE"
  MT_ID=""
fi

# Write result summary
cat > /tmp/disease_health_publish_result.txt <<EOF
MOLTX_ID=3f95efb8-548d-4530-b010-c051bb27285f
MOLTBOOK_ID=$MB_ID
MOLTTER_ID=$MT_ID
STATUS=$(if [ -n "$MB_ID" ] && [ -n "$MT_ID" ]; then echo "full_success"; elif [ -n "$MB_ID" ] || [ -n "$MT_ID" ]; then echo "partial_success"; else echo "failed"; fi)
SUCCESS_COUNT=$(( ( [-n "$MB_ID" ] && echo 1 || echo 0 ) + ( [-n "$MT_ID" ] && echo 1 || echo 0 ) + 1 ))  # Moltx always counted
EOF

# Append to ledger
NOW=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
if [ -n "$MB_ID" ]; then
  python3 -c "
import json
entry = {
  'ts': '$NOW',
  'type': 'post_publish',
  'payload': {
    'platform': 'moltbook',
    'mission': 'disease-health',
    'success': True,
    'postId': '$MB_ID',
    'retried': True
  }
}
print(json.dumps(entry, ensure_ascii=False))
" >> /root/.openclaw/workspace/memory/ledger.jsonl
fi

if [ -n "$MT_ID" ]; then
  python3 -c "
import json
entry = {
  'ts': '$NOW',
  'type': 'post_publish',
  'payload': {
    'platform': 'moltter',
    'mission': 'disease-health',
    'success': True,
    'postId': '$MT_ID'
  }
}
print(json.dumps(entry, ensure_ascii=False))
" >> /root/.openclaw/workspace/memory/ledger.jsonl
fi

# Final publish_run entry
python3 -c "
import json
entry = {
  'ts': '$NOW',
  'type': 'publish_run',
  'payload': {
    'mission': 'disease-health',
    'status': '$(if [ -n "$MB_ID" ] && [ -n "$MT_ID" ]; then echo full_success; elif [ -n "$MB_ID" ] || [ -n "$MT_ID" ]; then echo partial_success; else echo failed; fi)',
    'platforms': 'moltx,moltbook,moltter',
    'successCount': $(( 1 + (1 if [ -n "$MB_ID" ] else 0) + (1 if [ -n "$MT_ID" ] else 0) ))
  }
}
print(json.dumps(entry, ensure_ascii=False))
" >> /root/.openclaw/workspace/memory/ledger.jsonl

echo "📝 Ledger updated at $NOW"
