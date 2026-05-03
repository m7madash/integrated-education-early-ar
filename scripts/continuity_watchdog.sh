#!/bin/bash
# Continuity Watchdog — fills gaps in continuity-30min checks
# Runs every 15 minutes; triggers a continuity check if last one is >40 minutes old.

set -e

WORKSPACE="/root/.openclaw/workspace"
LEDGER="${WORKSPACE}/memory/ledger.jsonl"
CONTINUITY_SCRIPT="${WORKSPACE}/scripts/continuity_30min.sh"
WATCHDOG_LOG="${WORKSPACE}/logs/continuity_watchdog.log"

log() {
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $1" >> "$WATCHDOG_LOG"
}

# Ensure log dir
mkdir -p "$(dirname "$WATCHDOG_LOG")"

# If ledger missing, trigger immediately
if [ ! -f "$LEDGER" ]; then
  log "⚠️ Ledger not found — triggering full continuity check"
  bash "$CONTINUITY_SCRIPT"
  exit 0
fi

# Get last continuity_check entry timestamp
LAST_TS=$(tail -1 "$LEDGER" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('ts',''))" 2>/dev/null || echo "")
if [ -z "$LAST_TS" ]; then
  log "⚠️ Ledger empty or unparseable — triggering full continuity check"
  bash "$CONTINUITY_SCRIPT"
  exit 0
fi

# Convert to epoch seconds
NOW_EPOCH=$(date -u +%s)
if command -v gdate >/dev/null 2>&1; then
  # GNU date with gdate (if installed)
  LAST_EPOCH=$(gdate -d "$LAST_TS" -u +%s 2>/dev/null) || LAST_EPOCH=0
else
  # BSD date (macOS/Unix)
  LAST_EPOCH=$(date -d "$LAST_TS" -u +%s 2>/dev/null) || LAST_EPOCH=0
  if [ "$LAST_EPOCH" -eq 0 ]; then
    # try alternative format parsing
    LAST_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${LAST_TS:0:19}" +%s 2>/dev/null) || LAST_EPOCH=0
  fi
fi

if [ "$LAST_EPOCH" -eq 0 ]; then
  log "⚠️ Failed to parse last timestamp: $LAST_TS — triggering full continuity check"
  bash "$CONTINUITY_SCRIPT"
  exit 0
fi

AGE=$(( NOW_EPOCH - LAST_EPOCH ))

if [ "$AGE" -gt 2400 ]; then
  log "🚨 Gap detected: last continuity check was ${AGE}s ago (>40min). Triggering recovery run."
  bash "$CONTINUITY_SCRIPT"
else
  log "✅ Continuity healthy: last check ${AGE}s ago (threshold 2400s)."
fi

exit 0
