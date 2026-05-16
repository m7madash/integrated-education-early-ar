#!/bin/bash
# War-Peace Mission Publisher — Resilient version with exponential backoff
# Handles rate limits, 403s, and network failures intelligently

set -e

WORKSPACE="/root/.openclaw/workspace"
MISSION="war_peace"
BASE_SCRIPT="$WORKSPACE/scripts/publish_arabic_v3_fixed.sh"
LEDGER_FILE="$WORKSPACE/memory/ledger.jsonl"
MAX_ATTEMPTS=3
BASE_DELAY=60   # start with 1 minute

# Platform-specific backoff multipliers
MOLTX_MULTIPLIER=1
MOLTBOOK_MULTIPLIER=2
MOLTTER_MULTIPLIER=1

log() {
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $*" | tee -a "$WORKSPACE/logs/war_peace_retry.log"
}

record_failure() {
  local reason="$1"
  local attempt="$2"
  ts=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
  node -e "const fs=require('fs');const l='$LEDGER_FILE';const e={ts:'$ts',type:'continuity_improvement',payload:{mission:'$MISSION',action:'retry_attempt',attempt:$attempt,reason:'$reason',status:'failed'}};fs.appendFileSync(l, JSON.stringify(e)+'\n');" 2>/dev/null || true
}

record_success() {
  ts=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z')
  node -e "const fs=require('fs');const l='$LEDGER_FILE';const e={ts:'$ts',type:'continuity_improvement',payload:{mission:'$MISSION',action:'retry_complete',status:'success'}};fs.appendFileSync(l, JSON.stringify(e)+'\n');" 2>/dev/null || true
}

attempt_publish() {
  local attempt_num=$1
  log "🚀 Attempt $attempt_num: Publishing $MISSION via $BASE_SCRIPT"
  
  # Run the standard publishing script
  if bash "$BASE_SCRIPT" "$MISSION" >> "$WORKSPACE/logs/war_peace_retry.log" 2>&1; then
    log "✅ Attempt $attempt_num: publish_arabic_v3_fixed.sh completed"
    return 0
  else
    local exit_code=$?
    log "❌ Attempt $attempt_num: publish script exited with code $exit_code"
    return $exit_code
  fi
}

# Retry loop with exponential backoff
attempt=1
while [ $attempt -le $MAX_ATTEMPTS ]; do
  log "🔄 Starting attempt $attempt/$MAX_ATTEMPTS"
  
  if attempt_publish $attempt; then
    log "✅ War-peace mission published successfully on attempt $attempt"
    record_success
    exit 0
  fi
  
  # Check for specific failure patterns in logs
  last_log_entry=$(tail -50 "$WORKSPACE/logs/war_peace_retry.log" 2>/dev/null | grep -i "rate|403|429|error" | tail -5 || true)
  
  if echo "$last_log_entry" | grep -qi "rate"; then
    log "⏳ Rate limit detected — backing off..."
    reason="rate_limit"
  elif echo "$last_log_entry" | grep -qi "403"; then
    log "⚠️ 403 Forbidden — credential/auth issue"
    reason="403_forbidden"
    # For 403, shorter backoff (might be temporary token issue)
  else
    log "⚠️ General failure — retrying..."
    reason="general_error"
  fi
  
  record_failure "$reason" "$attempt"
  
  if [ $attempt -lt $MAX_ATTEMPTS ]; then
    # Exponential backoff: delay = base * (2 ^ (attempt-1)) * multiplier
    # Exponential backoff: delay = base * (2 ^ (attempt-1)) * multiplier
    delay=$(( BASE_DELAY * (2 ** (attempt - 1)) ))
    log "⏸️  Waiting ${delay}s before next attempt..."
    sleep $delay
  fi
  
  attempt=$((attempt + 1))
done

log "❌ All $MAX_ATTEMPTS attempts exhausted. War-peace mission still failing."
log "🔧 Manual intervention required: Check platform credentials, rate limits, or content format."
exit 1
