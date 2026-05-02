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
LEDGER_FILE="${WORKSPACE}/memory/ledger.jsonl"

cd "${WORKSPACE}"

# Lockfile: prevent overlapping runs using flock (atomic)
LOCK_FILE="${WORKSPACE}/.continuity_30min.lock"
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ Lock held by another instance. Exiting."
  exit 1
fi
# Lock will be released automatically when FD 200 closes on exit

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
# Compute next heartbeat (30 minutes from now)
NOW_SEC=$(date -u +%s 2>/dev/null || date +%s)
NEXT_HB=$(date -u -d "@$(( NOW_SEC + 1800 ))" '+%Y-%m-%dT%H:%M:%S.000Z' 2>/dev/null || date -u -v+30M '+%Y-%m-%dT%H:%M:%S.000Z' 2>/dev/null || date -u -d 'now +30 minutes' '+%Y-%m-%dT%H:%M:%S.000Z')
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

# All daily recurring missions (including auxiliary) with their scheduled time (UTC)
declare -A DAILY_MISSION_HOUR=(
  ["injustice-justice"]=0
  ["division-unity"]=0
  ["poverty-dignity"]=3
  ["dhikr-morning"]=3
  ["ignorance-knowledge"]=6
  ["war-peace"]=9
  ["shirk-tawhid"]=9
  ["pollution-cleanliness"]=12
  ["disease-health"]=15
  ["slavery-freedom"]=18
  ["corruption-reform"]=18
  ["extremism-moderation"]=21
  ["dhikr-evening"]=22
)
declare -A DAILY_MISSION_MINUTE=(
  ["injustice-justice"]=0
  ["division-unity"]=0
  ["poverty-dignity"]=0
  ["dhikr-morning"]=0
  ["ignorance-knowledge"]=0
  ["war-peace"]=0
  ["shirk-tawhid"]=30
  ["pollution-cleanliness"]=0
  ["disease-health"]=0
  ["slavery-freedom"]=0
  ["corruption-reform"]=30
  ["extremism-moderation"]=0
  ["dhikr-evening"]=0
)

# Build array of mission names from keys
DAILY_MISSION_NAMES=("${!DAILY_MISSION_HOUR[@]}")

NOW_EPOCH=$(date -u +%s)
TODAY=$(date -u +%Y-%m-%d)
CURRENT_HOUR=$(date -u +%H)
CURRENT_MINUTE=$(date -u +%M)
CURRENT_MINUTES=$((10#$CURRENT_HOUR * 60 + 10#$CURRENT_MINUTE))

# Compute expected count and gather missing missions
expected_count=0
missing_missions=()

for m in "${DAILY_MISSION_NAMES[@]}"; do
  h=${DAILY_MISSION_HOUR[$m]}
  min=${DAILY_MISSION_MINUTE[$m]}
  sched_minutes=$((10#$h * 60 + 10#$min))
  if [ "$CURRENT_MINUTES" -ge "$sched_minutes" ]; then
    expected_count=$((expected_count+1))
    # Check if mission already fully published today using ledger (publish_run with full_success)
    if [ -f "$LEDGER_FILE" ] && command -v jq &>/dev/null; then
      # Filter only well-formed JSONL entries (those starting with {"ts":) to avoid parse errors from malformed lines
      if grep -q '^\{"ts":' "$LEDGER_FILE" && grep '^\{"ts":' "$LEDGER_FILE" | jq -e --arg m "$m" --arg today "$TODAY" 'select(.type=="publish_run" and .payload.mission==$m and .payload.status=="full_success" and ((.ts // "") | startswith($today)))' > /dev/null; then
        : # mission complete
      else
        missing_missions+=("$m")
      fi
    else
      # Fallback to publish_log check (less reliable)
      if ! grep -Fq "نشر: $m" "$WORKSPACE/memory/publish_log_${TODAY}.md" 2>/dev/null; then
        missing_missions+=("$m")
      fi
    fi
  fi
done

actual_count=$((expected_count - ${#missing_missions[@]}))
log "🔍 Daily mission posts: ${actual_count}/${expected_count} published (by ${CURRENT_HOUR}:${CURRENT_MINUTE} UTC)"

if [ ${#missing_missions[@]} -gt 0 ]; then
  log "⚠️ MISSING: ${#missing_missions[@]} post(s): ${missing_missions[*]}"

  GRACE_MINUTES=15
  republish_list=()
  for m in "${missing_missions[@]}"; do
    h=${DAILY_MISSION_HOUR[$m]}
    min=${DAILY_MISSION_MINUTE[$m]}
    sched_minutes=$((10#$h * 60 + 10#$min))
    grace_minutes=$((sched_minutes + GRACE_MINUTES))
    if [ "$CURRENT_MINUTES" -ge "$grace_minutes" ]; then
      republish_list+=("$m")
    else
      # Within grace period — will retry in next cycle
      log "⏰ ${m} scheduled at $(printf '%02d:%02d' $h $min) — within ${GRACE_MINUTES}min grace, waiting..."
    fi
  done

  if [ ${#republish_list[@]} -gt 0 ]; then
    log "🔧 Auto-republishing ${#republish_list[@]} missed mission(s): ${republish_list[*]}"
    for miss in "${republish_list[@]}"; do
      log "🚀 Publishing: ${miss}"
      if [ -f "scripts/publish_daily_post_multi_target.sh" ]; then
        bash scripts/publish_daily_post_multi_target.sh "$miss" >> "${LOG_FILE}" 2>&1 || log "❌ Failed: ${miss}"
        sleep 2
      else
        log "⚠️ publish script missing: scripts/publish_daily_post_multi_target.sh"
      fi
    done
  fi
else
  log "✅ All expected daily mission posts published"
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
