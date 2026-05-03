#!/bin/bash
# Wrapper for kpi_tracker.js check — exec-preflight safe
# Usage: bash scripts/run_kpi_check.sh

set -e

SCRIPT="/root/.openclaw/workspace/scripts/kpi_tracker.js"

if [ -f "$SCRIPT" ]; then
  node "$SCRIPT" check
else
  echo "kpi_tracker.js not found"
  exit 1
fi
