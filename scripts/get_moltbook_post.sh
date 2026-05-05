#!/bin/bash
# Get details of specific MoltBook posts

MB_KEY=$(jq -r .api_key ~/.config/moltbook/credentials.json 2>/dev/null || echo "")
POST_ID="$1"

if [[ -z "$POST_ID" ]]; then
  echo "Usage: $0 POST_ID"
  exit 1
fi

response=$(curl -s -H "Authorization: Bearer ${MB_KEY}" \
  "https://www.moltbook.com/api/v1/posts/${POST_ID}" 2>/dev/null || echo "{}")

echo "$response" | jq '.' 2>/dev/null || echo "$response"
