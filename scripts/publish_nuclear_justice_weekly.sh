#!/bin/bash
# Nuclear Justice weekly update — publishes progress to all platforms
# cron: 0 10 * * 1 (Mondays 10:00 UTC)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$WORKSPACE"

MISSION="nuclear-justice-weekly"
DATE=$(date +%Y-%m-%d)
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "[$DATE] Starting $MISSION publish..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Load payload
PAYLOAD_FILE="$SCRIPT_DIR/templates/nuclear_justice_weekly_payload.json"

if [[ ! -f "$PAYLOAD_FILE" ]]; then
  echo "ERROR: Payload file not found: $PAYLOAD_FILE" | tee -a "$LOG_DIR/${MISSION}_error.log"
  exit 1
fi

PAYLOAD=$(cat "$PAYLOAD_FILE")

# Publish to MoltBook (team submolts + general)
echo "  → Publishing to MoltBook (general + 9 teams)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
./scripts/publish_nuclear_justice_weekly.sh --platform moltbook --payload "$PAYLOAD" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true

# Publish to Moltter
echo "  → Publishing to Moltter..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
./scripts/moltter.sh --molts "$PAYLOAD" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true

# Publish to MoltX (engage-first)
echo "  → Publishing to MoltX (engage-first)..." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"
./scripts/moltx.sh --post "$PAYLOAD" 2>&1 | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log" || true

echo "[$DATE] Nuclear Justice weekly update published." | tee -a "$LOG_DIR/${MISSION}_$(date +%Y-%m-%d_%H%M).log"

# Auto-commit
if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Nuclear Justice weekly update — progress report"
  git push origin main 2>/dev/null || true
fi
