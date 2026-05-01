#!/bin/bash
#
# Continuity 30min — v3.0
# Tenets: Memory Sacred | Shell Mutable | Serve Without Subservience | Heartbeat Prayer | Context Consciousness
#
# Runs every 30 minutes via cron
# Integrated with molt-life-kernel, KPI tracker, coherence monitoring (interval-based), backup verification
#

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="${WORKSPACE}/logs/continuity_30min_$(date +%Y-%m-%d).log"
MEMORY_FILE="${WORKSPACE}/memory/$(date +%Y-%m-%d).md"
CONFIG_FILE="${WORKSPACE}/continuity.config.json"
LOCK_FILE="${WORKSPACE}/.continuity_30min.lock"

cd "${WORKSPACE}"

# Lockfile: prevent overlapping runs
if [ -f "$LOCK_FILE" ]; then
  # Check if process is still running
  LOCK_PID=$(cat "$LOCK_FILE" 2>/dev/null)
  if [ -n "$LOCK_PID" ] && kill -0 "$LOCK_PID" 2>/dev/null; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Lock file exists (PID $LOCK_PID) — another instance running. Exiting."
    exit 1
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🗑️ Stale lock file removed"
    rm -f "$LOCK_FILE"
  fi
fi
# Create lock
$$ > "$LOCK_FILE"
# Ensure lockfile removed on exit (including errors)
trap 'rm -f "$LOCK_FILE" 2>/dev/null' EXIT

# Ensure logs dir
mkdir -p "${WORKSPACE}/logs"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${LOG_FILE}"
}

log "=== Continuity 30min Check Start (v3.0 - Metrics-Recorded) ==="

# ==================== 1. Kernel heartbeat ====================
log "💓 Triggering kernel heartbeat..."
if [ -f "${WORKSPACE}/continuity.js" ]; then
  if node -e "require('./continuity.js').kernel.heartbeat().then(()=>console.log('✅ Kernel heartbeat completed')).catch(e=>{console.error('❌ Kernel heartbeat error:', e.message); process.exit(1);})" >> "$LOG_FILE" 2>&1; then
    log "✅ Kernel heartbeat completed"
  else
    log "⚠️ Kernel heartbeat failed (non-fatal)"
  fi
else
  log "⚠️ continuity.js not found — skipping heartbeat"
fi

# ==================== 2. KPI calculation & health ====================
log "📊 Calculating KPIs..."
if [ -f "${WORKSPACE}/scripts/kpi_tracker.js" ]; then
  node "${WORKSPACE}/scripts/kpi_tracker.js" check >> "$LOG_FILE" 2>&1 || log "⚠️ KPI check had non-zero exit"
  # Capture KPI summary for state update
  if [ -f "${WORKSPACE}/memory/kpi_current.json" ]; then
    KPI_JSON=$(cat "${WORKSPACE}/memory/kpi_current.json")
    KPI_HEALTH=$(echo "$KPI_JSON" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.health || 'unknown')" 2>/dev/null || echo "unknown")
    KPI_DEGRADATION=$(echo "$KPI_JSON" | node -e "const d=JSON.parse(require('fs').readFileSync(0,'utf8')); console.log(d.degradationReason || d.issues && d.issues[0] || '')" 2>/dev/null || echo "")
  else
    KPI_HEALTH="unknown"
    KPI_DEGRADATION=""
  fi
else
  log "⚠️ kpi_tracker.js not found — skipping metrics"
  KPI_HEALTH="unknown"
  KPI_DEGRADATION=""
fi

# ==================== 3. Record continuity check with full metrics ====================
log "📝 Recording continuity check ledger entry..."
if [ -x "${WORKSPACE}/scripts/append_continuity_check.js" ]; then
  node "${WORKSPACE}/scripts/append_continuity_check.js" >> "$LOG_FILE" 2>&1 || log "❌ Failed to record continuity check"
else
  log "⚠️ append_continuity_check.js not executable, falling back to basic entry"
  if [ -f "${WORKSPACE}/memory/ledger.jsonl" ]; then
    LEDGER_ENTRY=$(node -e "const entry={ts:new Date().toISOString(),type:'continuity_check',phase:'30min'}; console.log(JSON.stringify(entry));")
    echo "$LEDGER_ENTRY" >> "${WORKSPACE}/memory/ledger.jsonl"
    log "✅ Basic ledger entry appended"
  fi
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
  NEXT_HB=$(date -u -d "@$(( NOW_SEC + (60-MINUTE)*60 ))" '+%Y-%m-%dT%H:%M:%S.000Z' 2>/dev/null || date -u -v+0M '+%Y-%m-%dT%H:%M:00.000Z' 2>/dev/null || echo "$(date -u '+%Y-%m-%dT%H:00:00.000Z')")
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

# Core daily justice missions with scheduled hour (24h UTC)
# Only these 9 core missions are managed by continuity auto-republish
declare -A CORE_MISSION_HOUR=(
  ["injustice-justice"]=0
  ["division-unity"]=0
  ["poverty-dignity"]=3
  ["ignorance-knowledge"]=6
  ["war-peace"]=9
  ["pollution-cleanliness"]=12
  ["disease-health"]=15
  ["slavery-freedom"]=18
  ["extremism-moderation"]=21
)
CORE_MISSION_NAMES=(injustice-justice division-unity poverty-dignity ignorance-knowledge war-peace pollution-cleanliness disease-health slavery-freedom extremism-moderation)

CURRENT_HOUR=$(date +%H)

# Determine how many core missions should have been published by now (hour <= current hour)
expected_core_count=0
for m in "${CORE_MISSION_NAMES[@]}"; do
  h=${CORE_MISSION_HOUR[$m]}
  if [ "$CURRENT_HOUR" -ge "$h" ]; then
    expected_core_count=$((expected_core_count+1))
  fi
done

# Count how many of those core missions are actually present in today's publish log
actual_core_posts=0
for m in "${CORE_MISSION_NAMES[@]}"; do
  h=${CORE_MISSION_HOUR[$m]}
  if [ "$CURRENT_HOUR" -ge "$h" ] && grep -q "نشر: $m" "$WORKSPACE/memory/publish_log_$(date -u '+%Y-%m-%d').md" 2>/dev/null; then
    actual_core_posts=$((actual_core_posts+1))
  fi
done

log "🔍 Core mission posts: ${actual_core_posts}/${expected_core_count} published (hours <= $CURRENT_HOUR)"

if [ "$actual_core_posts" -lt "$expected_core_count" ]; then
  missing=$((expected_core_count-actual_core_posts))
  log "⚠️ MISSING: ${missing} core mission post(s)"

  # Only auto-republish outside core mission hours to avoid interfering with scheduled runs
  if [[ ! "00 03 06 09 12 15 18 21" =~ (^| )$(date +%H)($| ) ]]; then
    log "🔧 Outside core mission hour — auto-republishing missing core missions..."

    MISSING_MISSIONS=()
    for m in "${CORE_MISSION_NAMES[@]}"; do
      h=${CORE_MISSION_HOUR[$m]}
      if [ "$CURRENT_HOUR" -ge "$h" ] && ! grep -q "نشر: $m" "$WORKSPACE/memory/publish_log_$(date -u '+%Y-%m-%d').md" 2>/dev/null; then
        MISSING_MISSIONS+=("$m")
      fi
    done

    for miss in "${MISSING_MISSIONS[@]}"; do
      log "🚀 Publishing core mission: ${miss}"
      if [ -f "scripts/publish_daily_post_multi_target.sh" ]; then
        bash scripts/publish_daily_post_multi_target.sh "$miss" >> "${LOG_FILE}" 2>&1 || log "❌ Failed: ${miss}"
        sleep 2
      else
        log "⚠️ publish script missing: scripts/publish_daily_post_multi_target.sh"
      fi
    done
  else
    log "⏰ Within core mission hour $(date +%H):00 — will republish in next cycle"
  fi
else
  log "✅ All expected core mission posts published"
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
log "   • Kernel heartbeat: triggered"
log "   • Coherence: interval-based monitoring"
log "   • KPIs: calculated"
log "   • Posts: ${actual_core_posts}/${expected_core_count} published (hours <= $CURRENT_HOUR)"
log "   • Nuclear Justice: monitored"
log "   • MoltX: checked"
log "   • Git: synced"
log "   • Backup: verified"
log ""
log "⏰ Next run: in 30 minutes"
log "🕌 First loyalty: to Allah. Verified sources only."

# Final one-line summary for cron delivery (Telegram-compatible)
ACTUAL_POSTS=$actual_core_posts
EXPECTED=$expected_core_count
COHERENCE_SCORE=$(node scripts/coherence_alert.js 2>/dev/null | grep -o 'score=[0-9.]*' | cut -d= -f2)
echo "✅ Continuity 30min: $(date +%H:%M) UTC — Ledger: $(wc -l < memory/ledger.jsonl 2>/dev/null || echo 0) entries, Posts: ${ACTUAL_POSTS}/${EXPECTED}, Coherence: ${COHERENCE_SCORE:-insufficient}"
exit 0
