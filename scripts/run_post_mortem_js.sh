#!/bin/bash
# Safe wrapper for post_mortem.js
# Preflight-safe: single binary invocation
set -e
SCRIPT="/root/.openclaw/workspace/scripts/post_mortem.js"
if [ -f "$SCRIPT" ]; then
  node "$SCRIPT"
else
  echo "ERROR: post_mortem.js not found"
  exit 1
fi
