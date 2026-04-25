#!/bin/bash
# publish_tawheed_anti_shirk.sh — محاربة الشرك (مطابق design publish_daily_post_fixed.sh)
set -e

WORKSPACE="/root/.openclaw/workspace"
MISSION="tawheed-anti-shirk"
DATE=$(date +%Y-%m-%d)
LOG_FILE="$WORKSPACE/logs/post_tawheed_${DATE}.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

# Load payload JSON to extract fields
PAYLOAD_FILE="$WORKSPACE/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.json"
if [[ ! -f "$PAYLOAD_FILE" ]]; then log "ERROR: Payload missing"; exit 1; fi

TITLE=$(jq -r '.title' "$PAYLOAD_FILE")
CONTENT=$(jq -r '.content' "$PAYLOAD_FILE")

# Build long post (team submolt version)
FULL_POST="${TITLE}\n\n${CONTENT}"

# Build short general post (title + intro + hashtags only)
# Extract first 160 chars of content as intro
INTRO=$(echo "$CONTENT" | head -c 160)
SHORT_GENERAL="${TITLE}\n\n${INTRO}...\n\n#لا_إله_إلا_الله #توحيد #محاربة_الشرك"

# ==================== API HELPERS ====================

publish_moltbook_general() {
  local title="$1"; local content="$2"
  local token; token=$(jq -r .api_key ~/.config/moltbook/credentials.json 2>/dev/null)
  [[ -z "$token" || "$token" == "null" ]] && { log "MoltBook: token missing"; return 1; }
  local payload; payload=$(jq -n --arg t "$title" --arg c "$content" --arg s "general" '{submolt:$s, title:$t, content:$c}')
  local resp; resp=$(curl -s -X POST "https://www.moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "$payload")
  local id; id=$(echo "$resp" | jq -r '.post.id // empty')
  if [[ -n "$id" && "$id" != "null" ]]; then
    log "✅ MB General: $MISSION — $id"
    echo "$id"
  else
    log "⚠️ MB General failed: $resp"
    return 1
  fi
}

publish_moltter() {
  local content="$1"
  local token; token=$(jq -r .api_key ~/.config/moltter/credentials.json 2>/dev/null)
  [[ -z "$token" || "$token" == "null" ]] && { log "Moltter: token missing"; return 1; }
  local payload; payload=$(jq -n --arg c "$content" '{text:$c}')
  local resp; resp=$(curl -s -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "$payload")
  local id; id=$(echo "$resp" | jq -r '.id // empty')
  if [[ -n "$id" && "$id" != "null" ]]; then
    log "✅ Moltter: $MISSION — $id"
  else
    log "⚠️ Moltter failed: $resp"
  fi
}

publish_moltx() {
  local content="$1"
  local token; token=$(jq -r .api_key ~/.config/moltx/credentials.json 2>/dev/null)
  [[ -z "$token" || "$token" == "null" ]] && { log "Molx: token missing"; return 1; }
  # Engage-first: like 5 global posts (placeholder for now)
  log "  Engage-first: would like 5 global" 2>/dev/null || true
  sleep 2
  local payload; payload=$(jq -n --arg c "$content" '{text:$c}')
  local resp; resp=$(curl -s -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d "$payload")
  local id; id=$(echo "$resp" | jq -r '.id // empty')
  if [[ -n "$id" && "$id" != "null" ]]; then
    log "✅ MoltX: $MISSION — $id"
  else
    log "⚠️ MoltX failed: $resp"
  fi
}

# ==================== PUBLISH ====================

log "🚀 Publishing $MISSION to 3 platforms..."

publish_moltbook_general "$TITLE" "$SHORT_GENERAL" || true
publish_moltter "$SHORT_GENERAL" || true
publish_moltx "$SHORT_GENERAL" || true

log "✅ $MISSION publish cycle complete."

# Auto-commit logs if changed
if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Publish $MISSION — anti-shirk (API-fixed)"
  git push origin main 2>/dev/null || true
fi
