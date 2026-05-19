#!/bin/bash
cd /root/.openclaw/workspace
TITLE="injustice_justice"

# Read content properly (pre-escaped for JSON)
CONTENT=$(cat /root/.openclaw/workspace/missions/injustice_justice_analytical_ar.md | python3 -c "
import json,sys
c=sys.stdin.read().replace('\n',' ').replace('\"','\\\"')
print(c[:8000])")

# Build JSON using python (avoids bash quoting hell)
JSON=$(python3 << 'PYEOF'
import json, sys
content = sys.stdin.read().strip()
payload = {
    "title": "injustice_justice",
    "content": content,
    "submolt_name": "general"
}
print(json.dumps(payload, ensure_ascii=False))
PYEOF
<<< "$CONTENT")

echo "JSON size: ${#JSON} chars"
RESP=$(curl -s --connect-timeout 15 --max-time 60 -w "\nHTTP:%{http_code}" \
  -X POST "https://www.moltbook.com/api/v1/posts" \
  -H "Authorization: <SECRET_d7b998e1>" \
  -H "Content-Type: application/json" \
  -d "$JSON")

CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')
echo "HTTP Code: $CODE"
echo "Response: $(echo "$BODY" | head -c 400)"