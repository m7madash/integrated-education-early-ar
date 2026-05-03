#!/bin/bash
# Wrapper for coherence_alert.js — exec-preflight safe
# Runs coherence check and limits output to last 30 lines
# Usage: bash scripts/run_coherence_check.sh

set -e

SCRIPT="/root/.openclaw/workspace/scripts/coherence_alert.js"

if [ -f "$SCRIPT" ]; then
  node "$SCRIPT" 2>&1 | head -30
else
  echo "coherence_alert.js not found"
fi
