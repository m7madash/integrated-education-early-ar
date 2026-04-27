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
# Default: standard publisher (v3 fixed)
exec "$BASE/scripts/publish_arabic_v3_fixed.sh" "$MISSION"
