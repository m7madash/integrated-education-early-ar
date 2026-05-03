#!/bin/bash
# Safe wrapper for continuity.js status command
# Preflight-safe: single binary invocation
set -e
SCRIPT="/root/.openclaw/workspace/continuity.js"
if [ -f "$SCRIPT" ]; then
  node "$SCRIPT" status
else
  echo "ERROR: continuity.js not found"
  exit 1
fi
