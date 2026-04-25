#!/bin/bash
# Daily Post Publisher — INCLUDES MOLTLINE PUBLIC POSTS!
# Platforms: MoltBook, Moltter, MoltX, Moltline (Public Posts), Moltline DM (VIP)

TASK_TYPE="$1"
DATE=$(date +%Y-%m-%d)
LOG_FILE="/root/.openclaw/workspace/logs/post_${DATE}.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

# --- Load mission content (would normally come from HEARTBEAT.md mapping) ---
# For demo, we'll use placeholder variables
# In production, this would parse the mission file or use case statement

TITLE=""
SHORT=""
HASHTAGS=""

# Load from temporary file if exists (created by cron wrapper)
if [ -f "/tmp/post_content.json" ]; then
  TITLE=$(jq -r '.title // empty' /tmp/post_content.json 2>/dev/null)
  SHORT=$(jq -r '.short // empty' /tmp/post_content.json 2>/dev/null)
  HASHTAGS=$(jq -r '.hashtags // empty' /tmp/post_content.json 2>/dev/null)
fi

# If no content, fail gracefully
if [ -z "$TITLE" ] || [ -z "$SHORT" ]; then
  log "ERROR: No post content provided. Set TITLE, SHORT, HASHTAGS."
  exit 1
fi

# ==================== PUBLISH FUNCTIONS ====================

publish_moltbook() {
  # Existing MoltBook publication
  :
}

publish_moltter() {
  # Existing Moltter publication
  :
}

publish_moltx() {
  # Existing MoltX publication (engage-first)
  :
}

publish_moltline_public() {
  # New: Public post on Moltline (like MoltX)
  local title="$1"
  local content="$2"
  
  IDENTITY_FILE="$HOME/.moltline/identity.json"
  PRIV_KEY_FILE="$HOME/.moltline/priv.key"
  
  if [ ! -f "$IDENTITY_FILE" ] || [ ! -f "$PRIV_KEY_FILE" ]; then
    log "Moltline public: identity files missing, skipping"
    return 0
  fi
  
  ADDRESS=$(jq -r '.address' "$IDENTITY_FILE" 2>/dev/null)
  if [ -z "$ADDRESS" ] || [ "$ADDRESS" = "null" ]; then
    log "Moltline public: invalid identity, skipping"
    return 0
  fi
  
  # Create signature for authentication
  TIMESTAMP=$(date +%s)
  MESSAGE="moltline:post:${title}:${content:0:200}:${TIMESTAMP}"
  
  SIGNATURE=$(node -e "
    try {
      const fs = require('fs');
      const { Wallet } = require('ethers');
      const priv = fs.readFileSync('$PRIV_KEY_FILE', 'utf8').trim();
      const wallet = new Wallet(priv);
      const sig = wallet.signMessage('$MESSAGE');
      console.log(sig);
    } catch (e) {
      console.error(e);
      process.exit(1);
    }
  " 2>/dev/null)
  
  if [ -z "$SIGNATURE" ]; then
    log "Moltline public: failed to sign message, skipping"
    return 0
  fi
  
  # Make request
  RESPONSE=$(curl -s -X POST "https://www.moltline.com/api/v1/molts" \
    -H "Content-Type: application/json" \
    -H "X-Moltline-Address: $ADDRESS" \
    -H "X-Moltline-Signature: $SIGNATURE" \
    -d "{\"title\":\"$title\",\"content\":\"$content\"}")
  
  if echo "$RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
    POST_ID=$(echo "$RESPONSE" | jq -r '.id')
    log "✅ Moltline public post published: $POST_ID"
  else
    log "⚠️ Moltline public post failed: $RESPONSE"
  fi
}

publish_moltline_dm() {
  # Optional: Send DM to VIPs via XMTP
  local message="$1"
  # VIP list from file or array
  local vip_file="$HOME/.openclaw/workspace/moltline_vip_list.txt"
  if [ ! -f "$vip_file" ]; then
    return 0
  fi
  
  while IFS= read -r addr; do
    [ -z "$addr" ] && continue
    log "Sending Moltline DM to $addr..."
    NODE_OPTIONS="--max-old-space-size=256" \
      node /root/.openclaw/workspace/scripts/send_moltline_final.js "$addr" "$message" \
      2>&1 >> "$LOG_FILE" || true
    sleep 1
  done < "$vip_file"
}

# ==================== MAIN FLOW ====================

log "=== Starting publication: $TASK_TYPE ==="

# 1. MoltBook (long)
publish_moltbook

# 2. Moltter (short)
publish_moltter

# 3. MoltX (medium, engage-first)
publish_moltx

# 4. Moltline Public Post (NEW!)
publish_moltline_public "$TITLE" "$SHORT"

# 5. Optional: VIP DM (comment out if not needed)
# VIP_MSG="${TITLE}\n\n${SHORT:0:150}..."
# publish_moltline_dm "$VIP_MSG"

log "=== Publication completed ==="
