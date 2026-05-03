#!/bin/bash
# Safe wrapper to read today's memory file with date expansion inside script
# Usage: bash scripts/read_today_memory.sh
set -e
DATE=$(date -u +%Y-%m-%d)
FILE="/root/.openclaw/workspace/memory/${DATE}.md"
if [ -f "$FILE" ]; then
  cat "$FILE"
else
  echo "Memory file for ${DATE} not found: ${FILE}"
  exit 1
fi
