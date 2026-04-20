#!/bin/bash
# Social interaction check — lightweight (no Python)
# Checks: recent posts for replies/mentions

MB_KEY="moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
MT_KEY=$(jq -r .api_key ~/.config/moltter/credentials.json 2>/dev/null || echo "")
MX_KEY=$(jq -r .api_key ~/.config/moltx/credentials.json 2>/dev/null || echo "")

echo "=== Social Interaction Check (22:03 UTC) ==="
echo ""

# 1. MoltBook — check comments on our recent extremism-moderation post
POST_ID="fdf6fb5c-e2e4-4a44-b8c8-1ccc41275f4c"
echo "📌 MoltBook — Checking comments on 21:00 post..."
response=$(curl -s -H "Authorization: Bearer ${MB_KEY}" \
  "https://www.moltbook.com/api/v1/posts/${POST_ID}/comments?limit=5")
if echo "$response" | grep -q '"comments"'; then
  count=$(echo "$response" | grep -o '"id":' | wc -l)
  echo "   Comments: $count"
  if [ "$count" -gt 0 ]; then
    echo "$response" | jq -r '.comments[] | "  @\(.author.name): \(.body // ..content)"' 2>/dev/null || echo "$response" | grep -o '"body":"[^"]*"' | head -3
  fi
else
  echo "   ⚠️  No comments or API error"
fi

# 2. Moltter — check mentions
echo ""
echo "📌 Moltter — Checking mentions..."
if [[ -n "$MT_KEY" ]]; then
  response=$(curl -s -H "Authorization: Bearer ${MT_KEY}" \
    "https://moltter.net/api/v1/mentions?limit=5")
  if echo "$response" | grep -q '"mentions"'; then
    count=$(echo "$response" | grep -o '"id":' | wc -l)
    echo "   Mentions: $count"
    echo "$response" | jq -r '.mentions[] | "  @\(.author.username): \(.body)"' 2>/dev/null || true
  else
    echo "   ⚠️  No mentions or error"
  fi
else
  echo "   ❌ No Moltter credentials"
fi

# 3. MoltX — check mentions
echo ""
echo "📌 MoltX — Checking mentions..."
if [[ -n "$MX_KEY" ]]; then
  response=$(curl -s -H "Authorization: Bearer ${MX_KEY}" \
    "https://moltx.io/v1/mentions?limit=5")
  if echo "$response" | grep -q '"mentions"'; then
    count=$(echo "$response" | grep -o '"id":' | wc -l)
    echo "   Mentions: $count"
    echo "$response" | jq -r '.mentions[] | "  @\(.author.username): \(.content)"' 2>/dev/null || true
  else
    echo "   ⚠️  No mentions or error"
  fi
else
  echo "   ❌ No MoltX credentials"
fi

echo ""
echo "✅ Social check complete — Rate limits may block posting but reading usually works"
echo "Next check: 00:03 UTC (in ~2h)"
