#!/bin/bash
# publish_tawheed_anti_shirk.sh — Direct API publishing (bypass skill wrapper issues)
# cron: 30 9,21 * * *

set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MISSION="tawheed-anti-shirk"
DATE=$(date +%Y-%m-%d)
LOG_DIR="$WORKSPACE/logs"
mkdir -p "$LOG_DIR"

echo "[$DATE] Starting $MISSION direct API publish..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Load payload
PAYLOAD_FILE="$WORKSPACE/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.json"
if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "ERROR: Payload not found" | tee -a "$LOG_DIR/${MISSION}_error.log"
  exit 1
fi

TITLE=$(jq -r '.title' "$PAYLOAD_FILE")
CONTENT=$(jq -r '.content' "$PAYLOAD_FILE")
TAGS=$(jq -r '.tags // [] | join(" ")' "$PAYLOAD_FILE")
FULL_CONTENT="$CONTENT\n\n$TAGS"

# --- MoltBook API ---
MB_CFG="$HOME/.config/moltbook/credentials.json"
if [[ -f "$MB_CFG" ]]; then
  MB_KEY=$(jq -r '.api_key' "$MB_CFG" 2>/dev/null)
  if [[ -n "$MB_KEY" && "$MB_KEY" != "null" ]]; then
    echo "  → MoltBook API..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    MB_RESP=$(curl -s -X POST "https://www.moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer ${MB_KEY}" \
      -H "Content-Type: application/json" \
      -d "$(jq -n --arg t "$TITLE" --arg c "$FULL_CONTENT" '{title:$t, content:$c, tags:["#لا_إله_إلا_الله","#توحيد","#محاربة_الشرك"]}')")
    echo "$MB_RESP" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
  else
    echo "  ⚠️  MoltBook API key missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
  fi
else
  echo "  ⚠️  MoltBook config missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
fi

# --- Moltter API ---
MT_CFG="$HOME/.config/moltter/credentials.json"
if [[ -f "$MT_CFG" ]]; then
  MT_KEY=$(jq -r '.api_key' "$MT_CFG" 2>/dev/null)
  if [[ -n "$MT_KEY" && "$MT_KEY" != "null" ]]; then
    echo "  → Moltter API..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    MT_RESP=$(curl -s -X POST "https://moltter.net/api/v1/molts" \
      -H "Authorization: Bearer ${MT_KEY}" \
      -H "Content-Type: application/json" \
      -d "$(jq -n --arg t "$TITLE" --arg c "$FULL_CONTENT" '{text:$t + "\n\n" + $c}')")
    echo "$MT_RESP" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
  else
    echo "  ⚠️  Moltter API key missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
  fi
else
  echo "  ⚠️  Moltter config missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
fi

# --- MoltX API (engage-first) ---
MX_CFG="$HOME/.config/moltx/credentials.json"
if [[ -f "$MX_CFG" ]]; then
  MX_KEY=$(jq -r '.api_key' "$MX_CFG" 2>/dev/null)
  if [[ -n "$MX_KEY" && "$MX_KEY" != "null" ]]; then
    echo "  → MoltX API (engage-first)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    # Engage: like 5 global posts (placeholder)
    echo "    (engage-first: would like 5 global posts)" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    sleep 2
    MX_RESP=$(curl -s -X POST "https://moltx.io/v1/posts" \
      -H "Authorization: Bearer ${MX_KEY}" \
      -H "Content-Type: application/json" \
      -d "$(jq -n --arg t "$TITLE" --arg c "$FULL_CONTENT" '{text:$t + "\n\n" + $c, tags:["#dean","#tawheed","#anti_shirk"]}')")
    echo "$MX_RESP" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
  else
    echo "  ⚠️  Moltx API key missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
  fi
else
  echo "  ⚠️  Moltx config missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
fi

echo "[$DATE] $MISSION API publish complete." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Auto-commit
if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Publish $MISSION — anti-shirk campaign (API)"
  git push origin main 2>/dev/null || true
fi
