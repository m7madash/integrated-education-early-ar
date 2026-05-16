#!/bin/bash
# Scheduler watchdog — keeps standalone_continuity_scheduler.js alive forever
# Restarts on crash, logs to scheduler_watchdog.log

WORKSPACE="/root/.openclaw/workspace"
SCRIPT="$WORKSPACE/scripts/standalone_continuity_scheduler.js"
LOG_DIR="$WORKSPACE/logs"
WATCHDOG_LOG="$LOG_DIR/scheduler_watchdog.log"
PID_FILE="$WORKSPACE/memory/scheduler.pid"
RESTART_COUNT=0
MAX_RESTARTS=100

log() {
  local ts=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
  echo "[$ts] $1" | tee -a "$WATCHDOG_LOG"
}

log "🛡️ Scheduler watchdog starting (will keep scheduler alive indefinitely)"

while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
  log "🔁 Starting scheduler (attempt $((RESTART_COUNT+1))...)"
  node "$SCRIPT" &
  SCHED_PID=$!
  echo $SCHED_PID > "$PID_FILE"
  log "✅ Scheduler spawned with PID $SCHED_PID"

  # Wait for process to exit
  wait $SCHED_PID
  EXIT_CODE=$?
  log "⚠️ Scheduler exited with code $EXIT_CODE — restarting in 3s..."
  sleep 3
  RESTART_COUNT=$((RESTART_COUNT+1))
done

log "❌ Max restarts reached ($MAX_RESTARTS). Giving up. MANUAL INTERVENTION REQUIRED."
exit 1
