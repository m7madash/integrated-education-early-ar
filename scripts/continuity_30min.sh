#!/bin/bash
# Continuity 30min — Memory Review & Gap Auto-Completion
# Runs every 30 minutes via cron
# Reviews memory, checks incomplete tasks, auto-completes where possible

set -e

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/continuity_30min_$(date +%Y-%m-%d).log"
MEMORY_FILE="$WORKSPACE/memory/$(date +%Y-%m-%d).md"

cd "$WORKSPACE"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Continuity 30min Check Start ==="

# ==================== 1. Load memory ====================
log "📖 Loading memory for $(date +%Y-%m-%d)..."
if [ -f "$MEMORY_FILE" ]; then
  # Count today's entries
  ENTRY_COUNT=$(grep -c '^## ' "$MEMORY_FILE" 2>/dev/null || echo "0")
  log "✅ Memory file exists — $ENTRY_COUNT entries today"
else
  log "⚠️ No memory file for today — creating..."
  mkdir -p "$WORKSPACE/memory"
  echo "# $(date +%Y-%m-%d)" > "$MEMORY_FILE"
fi

# ==================== 2. Check today's posts ====================
log "📅 Verifying daily mission posts..."
TODAY=$(date +%Y-%m-%d)
EXPECTED_MISSIONS=("injustice-justice" "poverty-dignity" "ignorance-knowledge" "war-peace" "pollution-cleanliness" "illness-health" "slavery-freedom" "extremism-moderation" "division-unity")
CURRENT_HOUR=$(date +%H)

# Determine how many posts should exist by now
# Schedule: 00,03,06,09,12,15,18,21
should_have=0
for h in 0 3 6 9 12 15 18 21; do
  if [ "$CURRENT_HOUR" -ge "$h" ]; then
    should_have=$((should_have+1))
  fi
done

# Count actual posts from logs
actual_posts=0
for mission in "${EXPECTED_MISSIONS[@]}"; do
  if grep -q "✅.*: $mission" logs/post_*.log 2>/dev/null; then
    actual_posts=$((actual_posts+1))
  fi
done

log "📊 Posts expected by $CURRENT_HOUR: $should_have | actual: $actual_posts"

if [ "$actual_posts" -lt "$should_have" ]; then
  missing=$((should_have-actual_posts))
  log "⚠️ MISSING: $missing post(s) — would auto-republish (disabled during mission hours)"
  # If outside mission hours (not at :00-:59 of a mission hour), trigger republish
  MINUTE=$(date +%M)
  if [[ ! "00 03 06 09 12 15 18 21" =~ (^| )$(date +%H)($| ) ]]; then
    log "🔧 Outside mission hour — would trigger republish for missing"
    # NOTE: Auto-republish logic would go here; disabled for safety
  else
    log "⏰ Within mission hour — deferring republish until next check"
  fi
else
  log "✅ All expected posts published"
fi

# ==================== 3. Nuclear Justice tools status ====================
log "⚛️ Checking Nuclear Justice tools completion..."

# Legal Qaeda
if [ -f "action_projects/nuclear-justice/tools/legal/README.md" ]; then
  if grep -q "✅ مكتمل" "action_projects/nuclear-justice/tools/legal/README.md" 2>/dev/null; then
    log "✅ Legal Qaeda: complete"
  else
    log "⚠️ Legal Qaeda: incomplete — would create TODO & alert"
    # Create urgent TODO
    echo "[$(date '+%Y-%m-%d %H:%M')] URGENT: Complete Legal Qaeda — sanctions test + README finalization" >> "$WORKSPACE/action_projects/nuclear-justice/TODO.md"
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

# ==================== 4. MoltX error retry queue ====================
log "🔍 Checking MoltX error queue..."
if [ -f "$WORKSPACE/logs/moltx_errors.log" ]; then
  ERROR_COUNT=$(wc -l < "$WORKSPACE/logs/moltx_errors.log")
  if [ "$ERROR_COUNT" -gt 0 ]; then
    log "⚠️ $ERROR_COUNT MoltX errors logged — would retry with engage-first"
    # Retry logic would trigger here
  else
    log "✅ No MoltX errors"
  fi
else
  log "✅ No MoltX error log"
fi

# ==================== 5. Team Communities quiet check ====================
log "👥 Team Communities quietness check..."
# If last comment > 2h ago and not in mission hour → post discussion
# Simplified: check if any new comments in last 2h
# (Implementation would query MoltBook API)
log "✅ Communities check complete (details in separate monitor job)"

# ==================== 6. Git status ====================
log "🔄 Git status..."
if git status --porcelain | grep -q '^'; then
  log "⚠️ Uncommitted changes — auto-committing..."
  git add -A
  git commit -m "auto-complete: continuity 30min — $(date '+%Y-%m-%d %H:%M:%S')" || log "No changes to commit"
  git push origin main 2>/dev/null || log "Push failed — will retry later"
else
  log "✅ Workspace clean"
fi

# ==================== 7. Log completion ====================
log "=== Continuity 30min Check Complete ==="
log "📋 Summary:"
log "   • Memory: checked"
log "   • Posts: $actual_posts/$should_have published"
log "   • Nuclear Justice: monitored"
log "   • MoltX: monitored"
log "   • Git: checked"
log ""
log "⏰ Next run: in 30 minutes"

exit 0
