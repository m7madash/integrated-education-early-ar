#!/bin/bash
# Wrapper for continuity.js status — exec-preflight safe
# Usage: bash scripts/run_continuity_status.sh

set -e

SCRIPT="/root/.openclaw/workspace/continuity.js"

if [ -f "$SCRIPT" ]; then
  node "$SCRIPT" status 2>&1
else
  echo "continuity.js not found"
  exit 1
fi
