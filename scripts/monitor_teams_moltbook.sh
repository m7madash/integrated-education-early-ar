#!/bin/bash
# Monitor 9 mission communities on MoltBook — check for new posts/replies

API_KEY="moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
API_BASE="https://www.moltbook.com/api/v1"

communities="
injustice-justice
poverty-dignity
ignorance-knowledge
war-peace
pollution-cleanliness
disease-health
slavery-freedom
extremism-moderation
division-unity
"

echo "=== Mission Communities Check ==="
for slug in $communities; do
  echo -n "📌 $slug: "
  response=$(curl -s -H "Authorization: Bearer ${API_KEY}" \
    "${API_BASE}/posts?submolt_name=${slug}&limit=3")
  
  if echo "$response" | grep -q '"posts"'; then
    count=$(echo "$response" | grep -o '"id":' | wc -l)
    if [ "$count" -eq 0 ]; then
      echo "No recent posts"
    else
      echo "$count recent post(s)"
      # Extract first title
      title=$(echo "$response" | grep -o '"title":"[^"]*"' | head -1 | cut -d'"' -f4)
      if [ -n "$title" ]; then
        echo "   Latest: $title"
      fi
    fi
  else
    echo "⚠️  Error or no activity"
  fi
done

echo ""
echo "✅ Check complete at $(date -u +%H:%M) UTC"
