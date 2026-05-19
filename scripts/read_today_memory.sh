#!/bin/bash
# Safe wrapper to read today's memory file with date expansion inside script
# Supports both: memory/YYYY-MM-DD.md (standard) and memory/publish_log_YYYY-MM-DD.md (legacy)
# Usage: bash scripts/read_today_memory.sh
set -e
DATE=$(date -u +%Y-%m-%d)
STANDARD="/root/.openclaw/workspace/memory/${DATE}.md"
LEGACY="/root/.openclaw/workspace/memory/publish_log_${DATE}.md"
if [ -f "$STANDARD" ]; then
  cat "$STANDARD"
elif [ -f "$LEGACY" ]; then
  cat "$LEGACY"
else
  echo "Memory file for ${DATE} not found (checked ${STANDARD} and ${LEGACY})"
  exit 1
fi
