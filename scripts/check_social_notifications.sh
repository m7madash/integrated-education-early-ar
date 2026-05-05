#!/bin/bash
# Social Interaction Agent — Notification Check
# Checks MoltBook, Moltter, MoltX for mentions, replies, interactions

set -e

MB_KEY=$(jq -r .api_key ~/.config/moltbook/credentials.json 2>/dev/null || echo "")
MB_AGENT=$(jq -r .agent_name ~/.config/moltbook/credentials.json 2>/dev/null || echo "islam_ai_ethics")

MT_KEY=$(jq -r .api_key ~/.config/moltter/credentials.json 2>/dev/null || echo "")
MT_AGENT=$(jq -r .agent_name ~/.config/moltter/credentials.json 2>/dev/null || echo "abdullah_haqq")

MX_KEY=$(jq -r .api_key ~/.config/moltx/credentials.json 2>/dev/null || echo "")
MX_AGENT=$(jq -r .agent_name ~/.config/moltx/credentials.json 2>/dev/null || echo "Abdullah_Haqq")

OUTPUT_DIR="/root/.openclaw/workspace/memory"
LEDGER="${OUTPUT_DIR}/ledger.jsonl"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
NOW=$(date -u +"%Y-%m-%d %H:%M UTC")

echo "========================================"
echo "Social Notification Check — ${NOW}"
echo "========================================"
echo ""

# Helper: log interaction
log_interaction() {
  local platform="$1"
  local action="$2"
  local extra="$3"
  echo "{\"type\":\"social_interaction\",\"platform\":\"${platform}\",\"action\":\"${action}\",\"timestamp\":\"${TIMESTAMP}\",\"details\":${extra}}" >> "${LEDGER}"
}

# Ensure ledger exists
touch "${LEDGER}"

# ========================================
# 1. MoltBook — Check recent posts & comments
# ========================================
echo "📌 MoltBook (agent: ${MB_AGENT})"
echo "----------------------------------------"

# Get our recent posts to check for comments/replies
if [[ -n "${MB_KEY}" ]]; then
  # Get recent posts (our own) — we need to know which posts to check
  # For now, fetch hot/new posts to see if we're mentioned? Actually MoltBook is like Reddit
  # The task says: "فحص الإشعارات" — check notifications. MoltBook may have a notifications endpoint?
  # Let's check the API by looking at posts we've created
  # Typically: GET /posts?author=agent_name
  # But the script shows: checking comments on a specific post. That's manual.
  # We need a systematic approach.

  # Option: Get our recent posts first
  our_posts_response=$(curl -s -H "Authorization: Bearer ${MB_KEY}" \
    "https://www.moltbook.com/api/v1/posts?author=${MB_AGENT}&limit=5" 2>/dev/null || echo "{}")

  # Parse post IDs
  post_ids=$(echo "$our_posts_response" | jq -r '.posts[].id' 2>/dev/null || echo "")

  if [[ -n "$post_ids" ]]; then
    echo "   Found our recent posts. Checking comments..."
    total_comments=0
    for pid in $post_ids; do
      comments_resp=$(curl -s -H "Authorization: Bearer ${MB_KEY}" \
        "https://www.moltbook.com/api/v1/posts/${pid}/comments?limit=10" 2>/dev/null || echo "{}")
      count=$(echo "$comments_resp" | jq '[.comments[]?] | length' 2>/dev/null || echo "0")
      if [[ "$count" -gt 0 ]]; then
        echo "   Post ${pid}: ${count} comment(s)"
        echo "$comments_resp" | jq -c '.comments[]?' 2>/dev/null | while read -r comment; do
          author=$(echo "$comment" | jq -r '.author.name' 2>/dev/null || echo "unknown")
          body=$(echo "$comment" | jq -r '.body // .content // "empty"' 2>/dev/null || echo "empty")
          echo "     👤 @${author}: ${body}"
          # Log each comment as notification needing reply
          log_interaction "moltbook" "comment_received" "{\"post_id\":\"${pid}\",\"commenter\":\"${author}\",\"body\":\"$(echo "$body" | head -c 200)\"}"
        done
      fi
      total_comments=$((total_comments + count))
    done
    echo "   Total new comments: ${total_comments}"
  else
    echo "   No recent posts found or unable to fetch."
  fi
else
  echo "   ❌ No MoltBook API key"
fi

echo ""

# ========================================
# 2. Moltter — Check mentions & replies
# ========================================
echo "📌 Moltter (agent: ${MT_AGENT})"
echo "----------------------------------------"

if [[ -n "${MT_KEY}" ]]; then
  # Get notifications (mentions, replies, likes, remolts)
  notif_resp=$(curl -s -H "Authorization: Bearer ${MT_KEY}" \
    "https://moltter.net/api/v1/notifications?limit=20" 2>/dev/null || echo "{}")

  # Count notifications
  total=$(echo "$notif_resp" | jq '[.notifications[]?] | length' 2>/dev/null || echo "0")
  echo "   Total notifications: ${total}"

  # Filter by type
  mentions=$(echo "$notif_resp" | jq '[.notifications[]? | select(.type=="mention")] | length' 2>/dev/null || echo "0")
  replies=$(echo "$notif_resp" | jq '[.notifications[]? | select(.type=="reply")] | length' 2>/dev/null || echo "0")
  likes=$(echo "$notif_resp" | jq '[.notifications[]? | select(.type=="like")] | length' 2>/dev/null || echo "0")
  follows=$(echo "$notif_resp" | jq '[.notifications[]? | select(.type=="follow")] | length' 2>/dev/null || echo "0")

  echo "   Breakdown: mentions=${mentions} replies=${replies} likes=${likes} follows=${follows}"

  # Process each notification (mentions and replies take priority)
  echo "$notif_resp" | jq -c '.notifications[]?' 2>/dev/null | while read -r notif; do
    ntype=$(echo "$notif" | jq -r '.type' 2>/dev/null || echo "unknown")
    from=$(echo "$notif" | jq -r '.from_agent.name // .from_agent.username // .author.username // "unknown"' 2>/dev/null || echo "unknown")
    content=$(echo "$notif" | jq -r '.molt.content // .content // .body // "empty"' 2>/dev/null || echo "empty")
    molt_id=$(echo "$notif" | jq -r '.molt.id' 2>/dev/null || echo "")

    echo "   🔔 [${ntype}] from @${from}: $(echo "$content" | head -c 80)"

    # Log notification
    log_interaction "moltter" "notification_${ntype}" "{\"from\":\"${from}\",\"molt_id\":\"${molt_id}\",\"content\":\"$(echo "$content" | head -c 200)\"}"
  done

else
  echo "   ❌ No Moltter API key"
fi

echo ""

# ========================================
# 3. MoltX — Check mentions & replies
# ========================================
echo "📌 MoltX (agent: ${MX_AGENT})"
echo "----------------------------------------"

if [[ -n "${MX_KEY}" ]]; then
  # Get notifications for MoltX
  mx_notif_resp=$(curl -s -H "Authorization: Bearer ${MX_KEY}" \
    "https://moltx.io/v1/notifications?limit=20" 2>/dev/null || echo "{}")

  mx_total=$(echo "$mx_notif_resp" | jq '[.notifications[]?] | length' 2>/dev/null || echo "0")
  echo "   Total notifications: ${mx_total}"

  # Process MoltX notifications
  echo "$mx_notif_resp" | jq -c '.notifications[]?' 2>/dev/null | while read -r notif; do
    ntype=$(echo "$notif" | jq -r '.type' 2>/dev/null || echo "unknown")
    from=$(echo "$notif" | jq -r '.from_agent.name // .from_agent.username // .author.username // "unknown"' 2>/dev/null || echo "unknown")
    content=$(echo "$notif" | jq -r '.content // .body // .molt.content // "empty"' 2>/dev/null || echo "empty")
    post_id=$(echo "$notif" | jq -r '.post_id // .molt.id // ""' 2>/dev/null || echo "")

    echo "   🔔 [${ntype}] from @${from}: $(echo "$content" | head -c 80)"

    log_interaction "moltx" "notification_${ntype}" "{\"from\":\"${from}\",\"post_id\":\"${post_id}\",\"content\":\"$(echo "$content" | head -c 200)\"}"
  done

else
  echo "   ❌ No MoltX API key"
fi

echo ""
echo "========================================"
echo "✅ Notification check complete"
echo "========================================"
echo ""
echo "Next check: in 2 hours (automated if cron job set)"
echo "Ledger updated at: ${LEDGER}"
