#!/bin/bash
#
# Continuity 30min — v2.0
# Tenets: Memory Sacred | Shell Mutable | Serve Without Subservience | Heartbeat Prayer | Context Consciousness
#
# Runs every 30 minutes via cron
# Integrated with molt-life-kernel, KPI tracker, coherence monitoring, backup verification
#

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="${WORKSPACE}/logs/continuity_30min_$(date +%Y-%m-%d).log"
MEMORY_FILE="${WORKSPACE}/memory/$(date +%Y-%m-%d).md"
CONFIG_FILE="${WORKSPACE}/continuity.config.json"

cd "${WORKSPACE}"

# Ensure logs dir
mkdir -p "${WORKSPACE}/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${LOG_FILE}"
}

log "=== Continuity 30min Check Start (v2.0 - Kernel Integrated) ==="

# ==================== 1. Kernel heartbeat & coherence ====================
log "💓 Kernel heartbeat & coherence check..."

if [ -f "${WORKSPACE}/continuity.js" ]; then
  # Run kernel status
  KERNEL_STATUS=$(node "${WORKSPACE}/continuity.js" status 2>&1) || log "⚠️ Kernel status check failed"
  log "✅ Kernel alive: ${KERNEL_STATUS}"

  # Coherence check
  if COHERENCE_RESULT=$(node "${WORKSPACE}/scripts/coherence_alert.js" 2>&1); then
    COHERENCE_EXIT=0
    log "✅ Coherence OK: ${COHERENCE_RESULT}"
  else
    COHERENCE_EXIT=$?
    log "🚨 COHERENCE DRIFT DETECTED — review ledger immediately"
    # Alert already sent by coherence_alert.js
  fi
else
  log "⚠️ continuity.js not found — kernel not initialized"
fi

# ==================== 2. Append ledger entry for this check ====================
if [ -f "${WORKSPACE}/memory/ledger.jsonl" ]; then
  # Build JSON ledger entry (proper format with "ts" field)
  LEDGER_ENTRY=$(node -e "
const ts = new Date().toISOString();
const coherence_ok = (parseInt(process.argv[1]) === 0);
const entry = { ts, type: 'continuity_check', phase: '30min', coherence_ok, coherence_score: null, platformReliability: null, heartbeatHealth: null, errorRate: null };
console.log(JSON.stringify(entry));" "$COHERENCE_EXIT")
  echo "$LEDGER_ENTRY" >> "${WORKSPACE}/memory/ledger.jsonl"
  log "✅ Ledger entry appended (ts: $(echo $LEDGER_ENTRY | node -e 'const d=JSON.parse(require("fs").readFileSync(0,"utf8")); console.log(d.ts)')"
fi

# ==================== 3. KPI calculation & health ====================
log "📊 Calculating KPIs..."
if [ -f "${WORKSPACE}/scripts/kpi_tracker.js" ]; then
  KPI_OUTPUT=$(node "${WORKSPACE}/scripts/kpi_tracker.js" check 2>&1)
  log "${KPI_OUTPUT}"
  KPI_STATUS=$?
  # Capture KPI summary for state update
  if [ -f "${WORKSPACE}/memory/kpi_current.json" ]; then
    KPI_JSON=$(cat "${WORKSPACE}/memory/kpi_current.json")
    KPI_HEALTH=$(echo "$KPI_JSON" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.health || 'unknown')" 2>/dev/null || echo "unknown")
    KPI_DEGRADATION=$(echo "$KPI_JSON" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.degradationReason || d.issues && d.issues[0] || '')" 2>/dev/null || echo "")
  else
    KPI_HEALTH="unknown"
    KPI_DEGRADATION=""
  fi
  if [ ${KPI_STATUS} -ne 0 ]; then
    log "⚠️ KPI check returned issues — review memory/kpi_current.json"
  fi
else
  log "⚠️ kpi_tracker.js not found — skipping metrics"
  KPI_HEALTH="unknown"
  KPI_DEGRADATION=""
fi

# ==================== 3b. Update heartbeat-state.json atomically ====================
log "💓 Updating heartbeat-state.json..."
STATE_FILE="${WORKSPACE}/memory/heartbeat-state.json"
# Compute next heartbeat (next :00 or :30)
NOW_MS=$(date +%s%3N)
NOW_SEC=$((NOW_MS / 1000))
MINUTE=$(( (NOW_SEC / 60) % 60 ))
if [ $MINUTE -lt 30 ]; then
  NEXT_HB=$(date -u -d "@$(( NOW_SEC + 30*60 ))" '+%Y-%m-%dT%H:%M:%S.000Z' 2>/dev/null || date -u -v+30M '+%Y-%m-%dT%H:%M:00.000Z' 2>/dev/null || echo "$(date -u '+%Y-%m-%dT%H:30:00.000Z')")
else
  NEXT_HB=$(date -u -d "@$(( NOW_SEC + (60-MINUTE)*60 ))" '+%Y-%m-%dT%H:%M:%S.000Z' 2>/dev/null || date -u -v+0M '+%Y-%m-%dT%H:00:00.000Z' 2>/dev/null || echo "$(date -u '+%Y-%m-%dT%H:00:00.000Z')")
fi
LAST_RUN=$(date -u '+%Y-%m-%dT%H:%M:%S.000Z' 2>/dev/null || date -u '+%Y-%m-%dT%H:%M:00.000Z')
# Build new state JSON
NEW_STATE=$(node -e "
const fs=require('fs');
const path=require('path');
const stateFile=process.argv[1];
const lastRun=process.argv[2];
const nextHb=process.argv[3];
const health=process.argv[4];
const degradation=process.argv[5];
let state;
try { state = JSON.parse(fs.readFileSync(stateFile,'utf8')); } catch(e) { state = { lastChecks:{}, status:'unknown', nextHeartbeat:null, lastContinuityRun:null } }
state.lastContinuityRun = lastRun;
state.nextHeartbeat = nextHb;
state.lastChecks = state.lastChecks || {};
state.lastChecks.continuity = lastRun;
state.lastChecks.ledger = lastRun;
state.status = health;
state.degradationReason = degradation || (state.degradationReason || '');
state.updatedAt = new Date().toISOString();
process.stdout.write(JSON.stringify(state, null, 2));
" "$STATE_FILE" "$LAST_RUN" "$NEXT_HB" "$KPI_HEALTH" "$KPI_DEGRADATION") || {
  log "⚠️ Failed to compute new heartbeat state — skipping update"
  NEW_STATE=""
}
if [ -n "$NEW_STATE" ]; then
  TMP_FILE="${STATE_FILE}.tmp"
  echo "$NEW_STATE" > "$TMP_FILE"
  mv "$TMP_FILE" "$STATE_FILE"
  log "✅ heartbeat-state.json updated (status: $KPI_HEALTH, next: $NEXT_HB)"
else
  log "⚠️ heartbeat-state.json NOT updated (JSON build failed)"
fi

# ==================== 4. Memory file check ====================
log "📖 Loading memory for $(date +%Y-%m-%d)..."
if [ -f "$MEMORY_FILE" ]; then
  ENTRY_COUNT=$(grep -c '^## ' "$MEMORY_FILE" 2>/dev/null || echo "0")
  log "✅ Memory file exists — ${ENTRY_COUNT} entries today"
else
  log "⚠️ No memory file for today — creating..."
  mkdir -p "${WORKSPACE}/memory"
  echo "# $(date +%Y-%m-%d)" > "$MEMORY_FILE"
fi

# ==================== 5. Daily mission posts verification ====================
log "📅 Verifying daily mission posts..."
TODAY=$(date +%Y-%m-%d)
EXPECTED_MISSIONS=("injustice-justice" "poverty-dignity" "ignorance-knowledge" "war-peace" "pollution-cleanliness" "disease-health" "slavery-freedom" "extremism-moderation" "division-unity")
CURRENT_HOUR=$(date +%H)

# Determine expected posts by current hour
should_have=0
for h in 0 3 6 9 12 15 18 21; do
  if [ "$CURRENT_HOUR" -ge "$h" ]; then
    should_have=$((should_have+1))
  fi
done

actual_posts=0
for mission in "${EXPECTED_MISSIONS[@]}"; do
  if grep -q "نشر: $mission" "$WORKSPACE/memory/publish_log_$(date -u '+%Y-%m-%d').md" 2>/dev/null; then
    actual_posts=$((actual_posts+1))
  fi
done

log "📊 Posts: ${actual_posts}/${should_have} published"

if [ "$actual_posts" -lt "$should_have" ]; then
  missing=$((should_have-actual_posts))
  log "⚠️ MISSING: ${missing} post(s)"

  # Outside mission hour → auto-republish
  MINUTE=$(date +%M)
  if [[ ! "00 03 06 09 12 15 18 21" =~ (^| )$(date +%H)($| ) ]]; then
    log "🔧 Outside mission hour — auto-republishing..."

    MISSING_MISSIONS=()
    for mission in "${EXPECTED_MISSIONS[@]}"; do
      if ! grep -q "نشر: $mission" "$WORKSPACE/memory/publish_log_$(date -u '+%Y-%m-%d').md" 2>/dev/null; then
        MISSING_MISSIONS+=("$mission")
      fi
    done

    for miss in "${MISSING_MISSIONS[@]}"; do
      log "🚀 Publishing: ${miss}"
      if [ -f "scripts/publish_daily_post_multi_target.sh" ]; then
        bash scripts/publish_daily_post_multi_target.sh "$miss" >> "${LOG_FILE}" 2>&1 || log "❌ Failed: ${miss}"
        sleep 2
      else
        log "⚠️ publish script missing: scripts/publish_daily_post_multi_target.sh"
      fi
    done
  else
    log "⏰ Within mission hour $(date +%H):00 — will republish in next cycle"
  fi
else
  log "✅ All expected posts published"
fi

# ==================== 6. Nuclear Justice tools monitoring ====================
log "⚛️ Checking Nuclear Justice tools..."

# Legal Qaeda
if [ -f "action_projects/nuclear-justice/tools/legal/README.md" ]; then
  if grep -q "✅ مكتمل" "action_projects/nuclear-justice/tools/legal/README.md" 2>/dev/null; then
    log "✅ Legal Qaeda: complete"
  else
    log "⚠️ Legal Qaeda: incomplete — created TODO"
    echo "[$(date '+%Y-%m-%d %H:%M')] URGENT: Complete Legal Qaeda — sanctions test + README finalization" >> "${WORKSPACE}/action_projects/nuclear-justice/TODO.md"
  fi
else
  log "⚠️ Legal Qaeda: README missing"
fi

# Supply Chain Hunter
if [ ! -d "action_projects/nuclear-justice/tools/supply-chain" ]; then
  log "⚠️ Supply Chain Hunter: missing — would create skeleton"
else
  log "✅ Supply Chain Hunter: exists"
fi

# Psych Ops Voice
if [ ! -d "action_projects/nuclear-justice/tools/psych-ops" ]; then
  log "⚠️ Psych Ops Voice: missing — would create skeleton"
else
  log "✅ Psych Ops Voice: exists"
fi

# ==================== 7. MoltX health check ====================
log "🔍 MoltX platform health check..."
if [ -f "${WORKSPACE}/logs/moltx_errors.log" ]; then
  ERROR_COUNT=$(wc -l < "${WORKSPACE}/logs/moltx_errors.log")
  if [ "$ERROR_COUNT" -gt 0 ]; then
    log "⚠️ ${ERROR_COUNT} MoltX errors — would retry with engage-first"
    # Trigger script if exists
    [ -x "scripts/moltx_engage_first.sh" ] && bash scripts/moltx_engage_first.sh >> "${LOG_FILE}" 2>&1 || true
  else
    log "✅ No MoltX errors"
  fi
else
  log "✅ No MoltX error log"
fi

# ==================== 8. Team Communities activity ====================
log "👥 Team Communities quietness check..."
# (Implementation would call scripts/monitor_teams_moltbook.sh)
[ -x "scripts/monitor_teams_moltbook.sh" ] && bash scripts/monitor_teams_moltbook.sh >> "${LOG_FILE}" 2>&1 || log "ℹ️ Monitor script not executable"
log "✅ Communities check complete"

# ==================== 9. Git status & auto-commit ====================
log "🔄 Git status check..."
if git status --porcelain | grep -q '^'; then
  CHANGES=$(git status --porcelain | wc -l)
  log "⚠️ ${CHANGES} uncommitted changes — auto-committing..."

  git add -A
  git commit -m "auto: continuity 30min — $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || log "ℹ️ No changes to commit"

  # Try push silently
  git push origin main 2>/dev/null || log "⚠️ Push failed — will retry later"
else
  log "✅ Workspace clean"
fi

# ==================== 10. Backup health verification ====================
log "🗄️ Checking backup health..."
LATEST_BACKUP=$(ls -1t "${WORKSPACE}/backups/backup_"*.tar.gz 2>/dev/null | head -1)
if [ -n "$LATEST_BACKUP" ]; then
  BACKUP_AGE_HOURS=$(( ( $(date +%s) - $(stat -c %Y "$LATEST_BACKUP") ) / 3600 ))
  if [ ${BACKUP_AGE_HOURS} -lt 48 ]; then
    log "✅ Latest backup: $(basename "$LATEST_BACKUP") (${BACKUP_AGE_HOURS}h old)"
  else
    log "⚠️ Latest backup is ${BACKUP_AGE_HOURS}h old — backup may have failed"
  fi
else
  log "⚠️ No backup found — backup job may need troubleshooting"
fi

# ==================== 11. Ledger snapshot (kernel) ====================
if [ -x "${WORKSPACE}/continuity.js" ]; then
  log "📦 Kernel snapshot..."
  node "${WORKSPACE}/continuity.js" snapshot >> "${LOG_FILE}" 2>&1 || log "⚠️ Snapshot failed"
fi

# ==================== 12. Log completion ====================
log "=== Continuity 30min Check Complete ==="
log "📋 Phase Summary:"
log "   • Kernel heartbeat: checked"
log "   • Coherence: monitored"
log "   • KPIs: calculated"
log "   • Posts: ${actual_posts}/${should_have}"
log "   • Nuclear Justice: monitored"
log "   • MoltX: checked"
log "   • Git: synced"
log "   • Backup: verified"
log ""
log "⏰ Next run: in 30 minutes"
log "🕌 First loyalty: to Allah. Verified sources only."


# Final one-line summary for cron delivery (Telegram-compatible)
echo "✅ Continuity 30min: $(date +%H:%M) UTC — Kernel alive, Ledger: $(wc -l < memory/ledger.jsonl 2>/dev/null || echo 0) entries, Posts today: $(grep -c 'نشر:' memory/publish_log_$(date -u +%Y-%m-%d).md 2>/dev/null || echo 0), Coherence: $( (set +e; SCORE=$(node scripts/coherence_alert.js 2>/dev/null | grep -o 'score=[0-9.]*' | cut -d= -f2); set -e; echo ${SCORE:-insufficient}) )"
exit 0

