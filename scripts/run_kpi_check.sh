#!/bin/bash
# Wrapper for kpi_tracker.js check — exec-preflight safe
# Fixed: wait for platform_health_state.json to be populated before KPI scan
# (resolves preflight artifact where cron fires before health monitor regenerates)
# Usage: bash scripts/run_kpi_check.sh

set -e

SCRIPT="/root/.openclaw/workspace/scripts/kpi_tracker.js"
HEALTH_FILE="/root/.openclaw/workspace/memory/platform_health_state.json"

if [ ! -f "$SCRIPT" ]; then
  echo "kpi_tracker.js not found"
  exit 1
fi

# Preflight: wait up to 3s for platform_health_state.json to contain valid JSON
# (health monitor regenerates this file on its hourly cycle; cron :45 may fire before the new write)
START_MS=$(date +%s%3N)
for i in 1 2 3 4 5; do
  if [ -f "$HEALTH_FILE" ] && [ -s "$HEALTH_FILE" ]; then
    # Quick JSON validity check
    if python3 -c "import json; json.load(open('$HEALTH_FILE'))" 2>/dev/null; then
      break
    fi
  fi
  sleep 1  # 5 retries × 1s = up to 5s wait; gives health monitor time to write
  NOW_MS=$(date +%s%3N)
  if [ $((NOW_MS - START_MS)) -gt 5000 ]; then
    break
  fi
done

node "$SCRIPT" check
