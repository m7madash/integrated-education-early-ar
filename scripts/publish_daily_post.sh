#!/bin/bash
# publish_daily_post.sh — Unified mission publisher
# Calls publish_arabic.sh with the correct mission name
# Ensures consistent naming and logging

set -e

WORKSPACE="/root/.openclaw/workspace"
MISSION="$1"

if [ -z "$MISSION" ]; then
  echo "Usage: $0 <mission-name>"
  echo "Available missions:"
  ls -1 "${WORKSPACE}/missions/"*_ar.md | xargs -I{} basename {} | sed 's/_ar.md//' | sort
  exit 1
fi

MISSION_FILE="${WORKSPACE}/missions/${MISSION}_analytical_ar.md"
# Fallback for legacy non-analytical missions
if [ ! -f "$MISSION_FILE" ]; then
  MISSION_FILE="${WORKSPACE}/missions/${MISSION}_ar.md"
fi

if [ ! -f "$MISSION_FILE" ]; then
  echo "❌ Mission file not found: $MISSION_FILE"
  echo "Available missions:"
  ls -1 "${WORKSPACE}/missions/"*_ar.md | xargs -I{} basename {} | sed 's/_ar.md//' | sort
  exit 1
fi

echo "🔄 Publishing mission: $MISSION"
"${WORKSPACE}/scripts/publish_arabic.sh" "$MISSION"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Mission published successfully: $MISSION"
else
  echo "⚠️ Mission publish returned exit code: $EXIT_CODE"
fi

exit $EXIT_CODE
