#!/bin/bash
# Wrapper for post_mortem.js — exec-preflight safe
# Usage: bash scripts/run_post_mortem.sh

set -e

SCRIPT="/root/.openclaw/workspace/scripts/post_mortem.js"

if [ -f "$SCRIPT" ]; then
  node "$SCRIPT" 2>&1
else
  echo "post_mortem.js not found"
  exit 1
fi
