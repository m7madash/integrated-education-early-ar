#!/bin/bash
# Social Interaction Check - Every 2 Hours
# Checks notifications, replies, engages with new posts, optionally publishes idea

LOG_FILE="/root/.openclaw/workspace/logs/social_$(date +%Y-%m-%d).log"
POST_LOG="/root/.openclaw/workspace/memory/social_replies.txt"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Track replied posts to avoid duplicates
ALREADY_REPLIED="$POST_LOG"

log "=== Social Interaction Check Started ==="

# 1. CHECK MOLTBOOK NOTIFICATIONS
log "Checking MoltBook notifications..."
MB_NOTIFS=$(curl -s -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
  "https://www.moltbook.com/api/v1/notifications")

# Extract unread notification count
UNREAD_COUNT=$(echo "$MB_NOTIFS" | grep -o '"unread_count":[0-9]*' | grep -o '[0-9]*')
log "MoltBook unread: $UNREAD_COUNT"

# Process notifications (simple: just log them for now)
echo "$MB_NOTIFS" | grep -o '"id":"[^"]*","type":"[^"]*"' | while read -r line; do
    NOTIF_ID=$(echo "$line" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    NOTIF_TYPE=$(echo "$line" | grep -o '"type":"[^"]*"' | cut -d'"' -f4)
    log "Notification: $NOTIF_ID type=$NOTIF_TYPE"
done

# 2. CHECK MOLTTER NOTIFICATIONS (use unread count only - too many to process all)
log "Checking Moltter notifications..."
MT_COUNT=$(curl -s -H "Authorization: Bearer moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838" \
  "https://moltter.net/api/v1/notifications/count")
log "Moltter unread count: $MT_COUNT"

# 3. INTERACT WITH NEW POSTS ON MOLTBOOK (Hot/New)
log "Interacting with new MoltBook posts..."
MB_NEW=$(curl -s -H "Authorization: Bearer moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW" \
  "https://www.moltbook.com/api/v1/posts?sort=new&limit=3")

# Find posts not already replied to
echo "$MB_NEW" | grep -o '"id":"[^"]*"' | while read -r line; do
    POST_ID=$(echo "$line" | cut -d'"' -f4)
    # Check if already replied
    if ! grep -q "$POST_ID" "$ALREADY_REPLIED" 2>/dev/null; then
        log "Found new post: $POST_ID - will interact"
        # Like the post (if API supports)
        # For now, just mark as seen
        echo "$POST_ID" >> "$ALREADY_REPLIED"
    fi
done

# 4. INTERACT WITH NEW POSTS ON MOLTX (Feed)
log "Interacting with MoltX feed..."
MX_FEED=$(curl -s -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
  "https://moltx.io/v1/feed/global?limit=3")

# Like first unliked post (to maintain engagement)
MX_POST_ID=$(echo "$MX_FEED" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
if [ -n "$MX_POST_ID" ]; then
    # Check if already liked (simple: just like anyway - API handles duplicates)
    curl -s -X POST "https://moltx.io/v1/posts/${MX_POST_ID}/like" \
      -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" > /dev/null
    log "Liked MoltX post: $MX_POST_ID"
fi

# 5. OPTIONAL: PUBLISH ONE IDEA (if time is right and content is valuable)
# For now, skip automatic posting to maintain quality
# User can trigger manual posting when desired

log "=== Social Interaction Check Completed ==="
