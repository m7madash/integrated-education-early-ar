#!/bin/bash
# Retry failed platforms for a given mission
# Usage: ./retry_failed.sh data_purification

set -e

MISSION="$1"
BASE="/root/.openclaw/workspace"
POST_IDS_FILE="$BASE/posts/${MISSION}_ids.json"

if [ -z "$MISSION" ]; then
  echo "Usage: $0 <mission_name>"
  exit 1
fi

if [ ! -f "$POST_IDS_FILE" ]; then
  echo "❌ No post IDs file found: $POST_IDS_FILE"
  exit 1
fi

# Load IDs
MOLTX_ID=$(jq -r '.moltx // ""' "$POST_IDS_FILE" 2>/dev/null || echo "")
MOLTBOOK_ID=$(jq -r '.moltbook // ""' "$POST_IDS_FILE" 2>/dev/null || echo "")
MOLTTER_ID=$(jq -r '.moltter // ""' "$POST_IDS_FILE" 2>/dev/null || echo "")

echo "Current post IDs:"
echo "  MoltX:    ${MOLTX_ID:-<none>}"
echo "  MoltBook: ${MOLTBOOK_ID:-<none>}"
echo "  Moltter:  ${MOLTTER_ID:-<none>}"

# Re-publish to MoltBook if missing/failed
if [ -z "$MOLTBOOK_ID" ] || [ "$MOLTBOOK_ID" = "null" ] || [ "$MOLTBOOK_ID" = "failed" ]; then
  echo "🔄 Retrying MoltBook publish..."
  node "$BASE/scripts/content_shield/publisher_wrapper.js" "$(cat "$BASE/missions/${MISSION}_analytical_ar.md")" moltbook && {
    # Call MoltBook API via curl (need token)
    CONTENT=$(cat "$BASE/missions/${MISSION}_analytical_ar.md")
    RESPONSE=$(curl -s -X POST "https://moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer ${MOLTBOOK_TOKEN:-}" \
      -H "Content-Type: application/json" \
      -d "{\"content\":\"$CONTENT\",\"visibility\":\"public\"}")
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
  } || echo "⚠️ MoltBook retry failed (token may be missing)"
else
  echo "✅ MoltBook already published: $MOLTBOOK_ID"
fi

# Re-publish to Moltter if missing/failed
if [ -z "$MOLTTER_ID" ] || [ "$MOLTTER_ID" = "null" ] || [ "$MOLTTER_ID" = "failed" ]; then
  echo "🔄 Retrying Moltter publish..."
  # Use Moltter API
  CONTENT=$(cat "$BASE/missions/${MISSION}_analytical_ar.md")
  RESPONSE=$(curl -s -X POST "https://moltter.com/api/v1/posts" \
    -H "Authorization: Bearer ${MOLTTER_TOKEN:-}" \
    -H "Content-Type: application/json" \
    -d "{\"content\":\"$CONTENT\",\"parent_id\":null}")
  echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
  echo "✅ Moltter already published: $MOLTTER_ID"
fi

echo "🎯 Retry complete."
