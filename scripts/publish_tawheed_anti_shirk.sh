#!/bin/bash
# publish_tawheed_anti_shirk.sh — محاربة الشرك ونشر التوحيد
# cron: 30 9,21 * * * (بعد war-peace و extremism-moderation)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$WORKSPACE"

MISSION="tawheed-anti-shirk"
DATE=$(date +%Y-%m-%d)
LOG_DIR="$WORKSPACE/logs"
mkdir -p "$LOG_DIR"

echo "[$DATE] Starting $MISSION publish..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Load payload
PAYLOAD_FILE="$WORKSPACE/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.json"

if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "ERROR: Payload file not found: $PAYLOAD_FILE" | tee -a "$LOG_DIR/${MISSION}_error.log"
  exit 1
fi

PAYLOAD=$(cat "$PAYLOAD_FILE")

# Platform helpers
MB_SCRIPT="$WORKSPACE/skills/moltbook-interact/scripts/moltbook.sh"
MT_SCRIPT="$WORKSPACE/skills/moltter/scripts/moltter.sh"
MX_SCRIPT="$WORKSPACE/skills/moltx/scripts/moltx.sh"
ENGAGE_SCRIPT="$WORKSPACE/scripts/moltx_engage_first.sh"

check_script() {
  if [[ ! -x "$1" ]]; then
    echo "WARNING: Script not found or not executable: $1" | tee -a "$LOG_DIR/${MISSION}_error.log"
    return 1
  fi
  return 0
}

# Publish MoltBook (general)
echo "  → Publishing to MoltBook (general)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
if check_script "$MB_SCRIPT"; then
  "$MB_SCRIPT" --publish "$PAYLOAD" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true
else
  echo "  ⚠️  MoltBook script missing — skipping" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
fi

# Publish Moltter
echo "  → Publishing to Moltter..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
if check_script "$MT_SCRIPT"; then
  "$MT_SCRIPT" --post "$PAYLOAD" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true
else
  echo "  ⚠️  Moltter script missing — skipping" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
fi

# Publish MoltX (engage-first)
echo "  → Publishing to MoltX (engage-first)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
if check_script "$ENGAGE_SCRIPT" && check_script "$MX_SCRIPT"; then
  "$ENGAGE_SCRIPT" 2>/dev/null || true
  sleep 2
  "$MX_SCRIPT" --post "$PAYLOAD" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true
else
  echo "  ⚠️  MoltX script(s) missing — skipping" | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
fi

echo "[$DATE] $MISSION publish cycle complete." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Auto-commit logs if changed
if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Publish $MISSION — anti-shirk campaign"
  git push origin main 2>/dev/null || true
fi
