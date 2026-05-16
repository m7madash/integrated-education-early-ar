#!/bin/bash
# TURBO FIX PLAN — Phase 1 Implementation
# ---------------------------------------
# This script runs the immediate stabilization actions we designed earlier.
# Executes as a single binary per OpenClaw continuity rules.

set -e

WORKSPACE="/root/.openclaw/workspace"
echo "✅ Workspace: $WORKSPACE"

# ── Action 1.1: Deploy Scheduler Watchdog ────────────────────────────────────
echo "🔧 [1.1] Deploying scheduler watchdog script..."
WATCHDOG_SCRIPT="$WORKSPACE/scripts/continuity_scheduler_watchdog.sh"
if [ -f "$WATCHDOG_SCRIPT" ]; then
  chmod +x "$WATCHDOG_SCRIPT"
  echo "✅ Watchdog script already exists and is executable"
else
  echo "❌ Watchdog script missing! Check earlier write call"
  exit 1
fi

# ── Action 1.2: Manual Repair of war-peace (cron just missed) ─────────────────
echo "🚀 [1.2] Triggering war-peace mission republish with retry..."
RETRY_SCRIPT="$WORKSPACE/scripts/publish_war_peace_with_retry_backoff.sh"
if [ -f "$RETRY_SCRIPT" ]; then
  chmod +x "$RETRY_SCRIPT"
  echo "▶️  Running war-peace retry script..."
  bash "$RETRY_SCRIPT"
  RETRY_EXIT=$?
  if [ $RETRY_EXIT -eq 0 ]; then
    echo "✅ War-peace republish succeeded"
  else
    echo "⚠️  War-peace republish failed (exit $RETRY_EXIT) — manual intervention required"
  fi
else
  echo "❌ Retry script missing! Check earlier write call"
  exit 1
fi

# ── Action 1.3: KPI Tracker already patched – verify it runs ─────────────────
echo "📊 [1.3] Verifying KPI tracker health check..."
if node "$WORKSPACE/scripts/kpi_tracker.js" check > /dev/null 2>&1; then
  echo "✅ KPI tracker runs without crashing"
else
  echo "⚠️  KPI tracker returned non-zero — review logs"
fi

echo ""
echo "=== Phase 1 Stabilization Complete ==="
echo "Next steps:"
echo "  - Activate the watchdog: nohup $WATCHDOG_SCRIPT > $WORKSPACE/logs/watchdog.out 2>&1 &"
echo "  - Monitor war-peace republish in $WORKSPACE/logs/war_peace_retry.log"
echo "  - Check platform rate limits and credential health"
echo "بفضل الله كل النجاح来自 فضل الله"
