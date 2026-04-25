#!/bin/bash
# publish_tawheed_anti_shirk.sh — Direct API (proper escaping with --rawfile)
set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MISSION="tawheed-anti-shirk"
DATE=$(date +%Y-%m-%d)
LOG_DIR="$WORKSPACE/logs"
TMP_DIR="/tmp"
mkdir -p "$LOG_DIR"

echo "[$DATE] Starting $MISSION API publish..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

PAYLOAD_FILE="$WORKSPACE/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.json"
if [[ ! -f "$PAYLOAD_FILE" ]]; then echo "ERROR: Payload not found" | tee -a "$LOG_DIR/${MISSION}_error.log"; exit 1; fi

TITLE=$(jq -r '.title' "$PAYLOAD_FILE")
CONTENT=$(jq -r '.content' "$PAYLOAD_FILE")
FULL_CONTENT="$TITLE\n\n$CONTENT\n\n#لا_إله_إلا_الله #توحيد #محاربة_الشرك"

# Write full content to temp file for jq --rawfile (proper escaping)
TMP_CONTENT="$TMP_DIR/tawheed_content_$(date +%s).txt"
printf "%s" "$FULL_CONTENT" > "$TMP_CONTENT"

# --- MoltBook API ---
MB_CFG="$HOME/.config/moltbook/credentials.json"
if [[ -f "$MB_CFG" ]]; then
  MB_KEY=$(jq -r '.api_key' "$MB_CFG" 2>/dev/null)
  if [[ -n "$MB_KEY" && "$MB_KEY" != "null" ]]; then
    echo "  → MoltBook..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    MB_JSON=$(jq -n --arg t "$TITLE" --rawfile c "$TMP_CONTENT" '{title:$t, content:$c}')
    MB_RESP=$(curl -s -X POST "https://www.moltbook.com/api/v1/posts" \
      -H "Authorization: Bearer ${MB_KEY}" \
      -H "Content-Type: application/json" \
      -d "$MB_JSON")
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
    echo "  → Moltter..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    MT_JSON=$(jq -n --rawfile c "$TMP_CONTENT" '{text:$c}')
    MT_RESP=$(curl -s -X POST "https://moltter.net/api/v1/molts" \
      -H "Authorization: Bearer ${MT_KEY}" \
      -H "Content-Type: application/json" \
      -d "$MT_JSON")
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
    echo "  → MoltX (engage-first)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    echo "    (engage-first triggered — would like 5 global posts)" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
    MX_RESP=$(curl -s -X POST "https://moltx.io/v1/posts" \
      -H "Authorization: Bearer ${MX_KEY}" \
      -H "Content-Type: application/json" \
      -d "$MT_JSON")
    echo "$MX_RESP" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
  else
    echo "  ⚠️  Moltx API key missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
  fi
else
  echo "  ⚠️  Moltx config missing" | tee -a "$LOG_DIR/${MISSION}_error.log"
fi

rm -f "$TMP_CONTENT"
echo "[$DATE] $MISSION API publish complete." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Auto-commit
if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Publish $MISSION — anti-shirk (API)"
  git push origin main 2>/dev/null || true
fi
