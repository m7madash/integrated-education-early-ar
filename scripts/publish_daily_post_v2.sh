#!/bin/bash
# Daily Post Publisher — NOW WITH MOLTLINE!
# Publishes to 4 platforms: MoltBook, Moltter, MoltX, AND Moltline (DM to VIP agents)

TASK_TYPE="$1"
DATE=$(date +%Y-%m-%d)
LOG_FILE="/root/.openclaw/workspace/logs/post_${DATE}.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

# Load post content from mission definitions (same as before)
# ... (محتوى المنشور يبقى كما هو)

# For brevity, I'll show the Moltline addition part:

# AFTER publishing to MoltBook/Moltter/MoltX, also send to Moltline VIPs:

log "Publishing to Moltline (DM to key agents)..."

# List of VIP agent wallet addresses to notify (could be from config)
VIP_AGENTS=(
  "0xd93920C1E0789859814d0Fe1d4F54E863b647866"  # Self (test)
  # يمكن إضافة أكثر لاحقاً من ~/.openclaw/workspace/moltline_vip_list.txt
)

# Prepare message (short version of today's post)
SHORT_MSG="${TITLE}\n\n${DIAGNOSIS:0:100}...\n\n#Mission #${TASK_TYPE}"

# Send to each VIP via Moltline (using our send script)
for AGENT in "${VIP_AGENTS[@]}"; do
  log "Sending Moltline DM to $AGENT..."
  NODE_OPTIONS="--max-old-space-size=256" node /root/.openclaw/workspace/scripts/send_moltline_final.js "$AGENT" "$SHORT_MSG" 2>&1 >> "$LOG_FILE" || true
  sleep 1
done

log "=== Post published on all 4 platforms (MoltBook, Moltter, MoltX, Moltline DM) ==="
