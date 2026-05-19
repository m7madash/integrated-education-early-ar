#!/bin/bash
# Load secrets from .env — never hardcode API keys in scripts
set -a
[ -f .env ] && . .env
set +a
export MOLTX_API_KEY="${MOLTX_API_KEY:-}"
export MOLTBOOK_API_KEY="${MOLTBOOK_API_KEY:-}"
export MOLTTER_API_KEY="${MOLTTER_API_KEY:-}"
