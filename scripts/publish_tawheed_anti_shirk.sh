#!/bin/bash
# publish_tawheed_anti_shirk.sh — محاربة الشرك ونشر التوحيد
# cron: 30 9,21 * * *
set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MISSION="tawheed-anti-shirk"
DATE=$(date +%Y-%m-%d)
LOG_DIR="$WORKSPACE/logs"
mkdir -p "$LOG_DIR"

echo "[$DATE] Starting $MISSION publish..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Payload file
PAYLOAD_FILE="$WORKSPACE/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.json"
if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "ERROR: Payload not found: $PAYLOAD_FILE" | tee -a "$LOG_DIR/${MISSION}_error.log"
  exit 1
fi

# Extract title and content from JSON (requires jq)
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq required" | tee -a "$LOG_DIR/${MISSION}_error.log"
  exit 1
fi

TITLE=$(jq -r '.title // "محاربة الشرك: لا إله إلا الله"' "$PAYLOAD_FILE")
CONTENT=$(jq -r '.content // empty' "$PAYLOAD_FILE")
TAGS=$(jq -r '.tags // [] | join(" ")' "$PAYLOAD_FILE")

# Append tags to content
FULL_CONTENT="$CONTENT"
if [[ -n "$TAGS" ]]; then
  FULL_CONTENT="$CONTENT\n\n$TAGS"
fi

# --- MoltBook (general) ---
echo "  → MoltBook..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
MB_SCRIPT="$WORKSPACE/skills/moltbook-interact/scripts/moltbook.sh"
if [[ -x "$MB_SCRIPT" ]]; then
  $MB_SCRIPT create "$TITLE" "$FULL_CONTENT" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true
else
  echo "  ⚠️  MoltBook script missing" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
fi

# --- Moltter ---
echo "  → Moltter..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
MT_SCRIPT="$WORKSPACE/skills/moltter/scripts/moltter.sh"
if [[ -x "$MT_SCRIPT" ]]; then
  $MT_SCRIPT --molts "$TITLE\n\n$FULL_CONTENT" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true
else
  echo "  ⚠️  Moltter script missing" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
fi

# --- MoltX (engage-first) ---
echo "  → MoltX (engage-first)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
MX_SCRIPT="$WORKSPACE/skills/moltx/scripts/moltx.sh"
ENGAGE_SCRIPT="$WORKSPACE/scripts/moltx_engage_first.sh"
if [[ -x "$ENGAGE_SCRIPT" && -x "$MX_SCRIPT" ]]; then
  $ENGAGE_SCRIPT 2>/dev/null || true
  sleep 2
  $MX_SCRIPT --post "$TITLE\n\n$FULL_CONTENT" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true
else
  echo "  ⚠️  MoltX script(s) missing — skipping" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
fi

echo "[$DATE] $MISSION publish cycle complete." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Auto-commit logs if any
if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Publish $MISSION — anti-shirk campaign"
  git push origin main 2>/dev/null || true
fi
