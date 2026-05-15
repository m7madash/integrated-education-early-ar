#!/bin/bash
# Unified Arabic Publisher — dispatches to appropriate handler
set -e
MISSION="$1"
BASE="/root/.openclaw/workspace"
if [ -z "$MISSION" ]; then echo "❌ يرجى اسم المهمة"; exit 1; fi

# Special case: continuity-improvement runs background work (no publishing)
if [ "$MISSION" = "continuity-improvement" ]; then
  exec "$BASE/scripts/continuity_work.sh"
fi

# Special case: war-peace needs resilient retry backoff due to rate limits
if [ "$MISSION" = "war-peace" ] || [ "$MISSION" = "war_peace" ]; then
  exec "$BASE/scripts/publish_war_peace_with_retry_backoff.sh"
fi

# DEFAULT: Route through circuit breaker for health-gated publishing
# This ensures unhealthy platforms (MoltBook/Moltter) are skipped automatically
# to reduce error frequency and improve platformReliability KPI.
# To bypass circuit breaker (e.g. for manual testing), set BYPASS_CIRCUIT_BREAKER=1
export BYPASS_CIRCUIT_BREAKER=${BYPASS_CIRCUIT_BREAKER:-0}
if [ "$BYPASS_CIRCUIT_BREAKER" = "0" ]; then
  exec "$BASE/scripts/publish_with_circuit_breaker.sh" "$MISSION"
else
  # Fallback to direct publish when explicitly requested
  exec "$BASE/scripts/publish_arabic_v3_fixed.sh" "$MISSION"
fi
