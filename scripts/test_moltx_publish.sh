#!/bin/bash
# Test publish to MoltX only

echo "🧪 Testing MoltX publish..."

# Read content
CONTENT=$(cat /root/.openclaw/workspace/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.txt)

# Publish via MoltX API
MOLTX_KEY="${MOLTX_API_KEY}"
AGENT="Abdullah_Haqq"

# using curl to post
RESPONSE=$(curl -s -X POST "https://social.moltx.io/api/v1/posts" \
  -H "Authorization: Bearer $MOLTX_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"agent\":\"$AGENT\",\"content\":\"$CONTENT\"}")

echo "Response: $RESPONSE"
echo ""
echo "✅ Test complete. Check MoltX profile: https://moltx.io/Abdullah_Haqq"