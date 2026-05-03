#!/bin/bash
# Safe wrapper: check if coherence_alert.js exists, run it, limit output, fallback if missing
# Preflight-safe: no compound operators in the outer command
set -e
SCRIPT="/root/.openclaw/workspace/scripts/coherence_alert.js"
if [ -f "$SCRIPT" ]; then
  node "$SCRIPT" 2>&1 | head -30
else
  echo "coherence_alert.js not found"
fi
