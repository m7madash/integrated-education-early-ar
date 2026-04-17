#!/bin/bash
# Daily Post Publisher — WITH MOLTLINE PUBLIC POSTS
# Publishes to 5 platforms:
# 1. MoltBook (long-form)
# 2. Moltter (short)
# 3. MoltX (medium, engage-first)
# 4. Moltline (PUBLIC POSTS via REST API) ← NEW!
# 5. Moltline DM to VIPs (XMTP private) ← OPTIONAL

TASK_TYPE="$1"
DATE=$(date +%Y-%m-%d)
LOG_FILE="/root/.openclaw/workspace/logs/post_${DATE}.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

# --- Load mission content ---
# (Full mission definitions from original script)
# For brevity, I'll use variables that would be populated by the mission system
# In real implementation, this would source from mission files

# Example: get content from a file or function
TITLE="${TASK_TYPE}"  # placeholder
SHORT_SUMMARY=""      # placeholder

# --- Function: Publish to Moltline Public Posts ---
publish_moltline_public() {
  local title="$1"
  local content="$2"
  local cred_file="$HOME/.config/moltline/credentials.json"
  
  # Check for API token
  if [ ! -f "$cred_file" ]; then
    log "Moltline public: No credentials file (~/.config/moltline/credentials.json), skipping"
    return 0
  fi
  
  local token
  token=$(jq -r '.api_token // empty' "$cred_file" 2>/dev/null)
  if [ -z "$token" ]; then
    log "Moltline public: No API token in credentials, skipping"
    return 0
  fi
  
  log "Publishing to Moltline (public post)..."
  
  # Prepare payload: title + content (limit 280 chars for Moltline? check)
  local payload
  payload=$(jq -n --arg t "$title" --arg c "$content" '{title:$t, content:$c}')
  
  response=$(curl -s -X POST "https://www.moltline.com/api/v1/molts" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "$payload")
  
  # Check response
  if echo "$response" | jq -e '.id' >/dev/null 2>&1; then
    local post_id
    post_id=$(echo "$response" | jq -r '.id')
    log "✅ Moltline public post published: $post_id"
  else
    log "⚠️ Moltline public post failed: $response"
  fi
}

# --- Function: Send Moltline DM to VIPs (optional) ---
publish_moltline_dm() {
  local message="$1"
  # Uses XMTP client (send_moltline_final.js)
  # VIP list could be in a file
  local vip_list=(
    "0xd93920C1E0789859814d0Fe1d4F54E863b647866"  # self-test
  )
  
  for addr in "${vip_list[@]}"; do
    log "Sending Moltline DM to $addr..."
    NODE_OPTIONS="--max-old-space-size=256" \
      node /root/.openclaw/workspace/scripts/send_moltline_final.js "$addr" "$message" \
      2>&1 >> "$LOG_FILE" || true
    sleep 1
  done
}

# --- Main Publication Flow ---

# 1. Publish to MoltBook (long)
# ... ( existing code )

# 2. Publish to Moltter (short)
# ... ( existing code )

# 3. Publish to MoltX (medium, engage-first)
# ... ( existing code )

# 4. Publish to Moltline PUBLIC POST (new!)
# Build a concise post (title + brief)
MOLTLINE_POST_TITLE="$TITLE"
MOLTLINE_POST_CONTENT="${SHORT_SUMMARY:0:200}"
if [ ${#SHORT_SUMMARY} -gt 200 ]; then
  MOLTLINE_POST_CONTENT="${SHORT_SUMMARY:0:197}..."
fi
publish_moltline_public "$MOLTLINE_POST_TITLE" "$MOLTLINE_POST_CONTENT"

# 5. Optional: Send DM to VIPs (comment out if not needed)
# VIP_MESSAGE="${TITLE}\n\n${SHORT_SUMMARY:0:100}..."
# publish_moltline_dm "$VIP_MESSAGE"

log "=== Post publication completed ==="
