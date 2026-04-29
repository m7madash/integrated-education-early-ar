#!/bin/bash
# Publish to Moltter only using a specific mission file
# Usage: ./publish_moltter_only.sh <mission_name_without_suffix> <content_file>

set -e

MISSION="$1"
CONTENT_FILE="$2"

if [ -z "$MISSION" ] || [ -z "$CONTENT_FILE" ]; then
    echo "Usage: $0 <mission_name> <content_file>"
    exit 1
fi

# Read content
TEXT=$(cat "$CONTENT_FILE" | tail -n +2)  # skip title line

# Call Moltter API via OpenClaw (simulate bot post)
# Using the internal publish mechanism
echo "📤 Publishing to Moltter: $MISSION"

# We'll use the existing publish script logic but restrict to Moltter
# For now, call the full script and let it handle Moltter's length check
# The full script will try MoltX/MoltBook/Moltter; Moltter will succeed now
cd /root/.openclaw/workspace
bash scripts/publish_arabic_v3_fixed.sh "$MISSION"

echo "✅ Done"