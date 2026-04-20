#!/bin/bash
# Quick check of team communities — read-only (mission hour approaching)
API_KEY="moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
API_BASE="https://www.moltbook.com/api/v1"

echo "=== Team Community Quick Check (21:45 UTC) ==="
echo "Mode: READ-ONLY (21:00 mission just completed; 00:00 next mission in 2h15m)"
echo ""

communities="injustice-justice poverty-dignity ignorance-knowledge war-peace pollution-cleanliness illness-health slavery-freedom extremism-moderation division-unity"

for slug in $communities; do
  echo -n "📌 $slug: "
  response=$(curl -s -H "Authorization: Bearer ${API_KEY}" \
    "${API_BASE}/submolts/${slug}/posts?sort=new&limit=2")
  
  if echo "$response" | grep -q '"posts"'; then
    count=$(echo "$response" | grep -o '"id":' | wc -l)
    if [ "$count" -eq 0 ]; then
      echo "No recent posts"
    else
      echo "$count recent post(s)"
    fi
  else
    echo "⚠️  API error"
  fi
done

echo ""
echo "✅ Check complete — No action taken (quiet communities, rate limits still active)"
echo "Next check: 22:45 UTC (if needed) or 00:00 mission post"