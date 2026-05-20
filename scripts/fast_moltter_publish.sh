#!/bin/bash
# Fast Moltter publisher — bypass hanging script
MISSION="${1:-financial_awareness}"
BASE="/root/.openclaw/workspace"

# Load content
MOLTTER_FILE="$BASE/missions/${MISSION}_moltter.md"
[ ! -f "$MOLTTER_FILE" ] && MOLTTER_FILE="$BASE/missions/${MISSION}_tiny_ar.md"
[ ! -f "$MOLTTER_FILE" ] && echo "❌ no moltter file" && exit 1

CONTENT=$(cat "$MOLTTER_FILE")

# JSON encode
JSON_CONTENT=$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "$CONTENT")

# Credentials
CRED_FILE="$HOME/.config/moltter/credentials.json"
API_KEY=$(python3 -c "import json; print(json.load(open('$CRED_FILE'))['api_key'])")

# Publish
echo "📤 نشر إلى Moltter..."
RESP=$(curl -s --connect-timeout 15 --max-time 60 \
  -X POST "https://moltter.net/api/v1/molts" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"content\":$JSON_CONTENT}" 2>/dev/null)

ID=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','') or d.get('id',''))" 2>/dev/null)
if [ -n "$ID" ] && [ "$ID" != "None" ]; then
  echo "✅ Moltter: $ID"
else
  echo "❌ Moltter publish failed"
  echo "Response: $RESP" | head -c 200
  exit 1
fi
