#!/bin/bash
# Continuity Scheduler Watchdog — ensures standalone_continuity_scheduler.js stays running
# Spawns the scheduler as a child process; restarts on exit after 5s delay.
# Intended to be run in background via: nohup bash scripts/continuity_scheduler_watchdog.sh &

set -e

WORKSPACE="/root/.openclaw/workspace"
SCHEDULER_SCRIPT="$WORKSPACE/scripts/standalone_continuity_scheduler.js"
LOG_DIR="$WORKSPACE/logs"
WATCHDOG_LOG="$LOG_DIR/continuity_watchdog.log"
PID_FILE="$WORKSPACE/memory/scheduler.pid"
RESTART_DELAY=5
MAX_RESTARTS=100
RESTART_COUNT=0

# Ensure log directory
mkdir -p "$LOG_DIR"

log() {
  local ts=$(date -u '+%Y-%m-%d %H:%M:%S UTC')
  echo "[$ts] $*" | tee -a "$WATCHDOG_LOG"
}

log "🛡️ Watchdog starting (supervising $SCHEDULER_SCRIPT)"

while true; do
  log "🔁 Starting scheduler (attempt $((RESTART_COUNT+1))...)"
  node "$SCHEDULER_SCRIPT" &
  SCHED_PID=$!
  echo $SCHED_PID > "$PID_FILE"
  log "✅ Scheduler spawned with PID $SCHED_PID"

  # Wait for process to exit
  wait $SCHED_PID
  EXIT_CODE=$?
  log "⚠️ Scheduler exited with code $EXIT_CODE — restarting in ${RESTART_DELAY}s..."
  sleep $RESTART_DELAY
  RESTART_COUNT=$((RESTART_COUNT+1))

  if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
    log "❌ Max restarts reached ($MAX_RESTARTS). Giving up. MANUAL INTERVENTION REQUIRED."
    exit 1
  fi
done
