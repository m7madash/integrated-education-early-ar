#!/bin/bash
# Publish Revive Sunnah mission (evolutionary curriculum)
# Usage: ./publish_revive_sunnah.sh

set -e

BASE="/root/.openclaw/workspace"
cd "$BASE"

# 1. Generate next sunnah mission via engine
echo "🔧 Generating next revive_sunnah mission..."
node "$BASE/scripts/revive_sunnah_engine.js"

# 2. Find the latest generated mission file
MISSION_FILE=$(ls -t missions/revive_sunnah_cycle*.md 2>/dev/null | head -1)
if [ -z "$MISSION_FILE" ]; then
  echo "❌ No revive_sunnah mission found"
  exit 1
fi

MISSION_BASE=$(basename "$MISSION_FILE" .md)
echo "📄 Mission: $MISSION_BASE"

# 3. Load content
RAW_FULL=$(cat "$BASE/missions/${MISSION_BASE}.md")

# 4. Content Shield filter (same as main publisher)
if ! node "$BASE/scripts/content_shield/shield_check.js" "$RAW_FULL" "multi" "$MISSION_BASE" 2>/dev/null; then
  echo "❌ Shield REJECT — abort publish"
  exit 1
fi

# Load tokens from OpenClaw config (best effort)
CONFIG_FILE="$BASE/openclaw.json"
MOLTX_TOKEN=""
if [ -f "$CONFIG_FILE" ]; then
  MOLTX_TOKEN=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('plugins',{}).get('config',{}).get('moltx',{}).get('token',''))" 2>/dev/null || echo "")
else
  echo "⚠️ Config not found: $CONFIG_FILE"
fi

if [ -z "$MOLTX_TOKEN" ]; then
  echo "⚠️ MOLTX_TOKEN missing — skipping MoltX publish (will retry later)"
  echo "   Set MOLTX_TOKEN in openclaw.json or environment"
  # Still succeed (non-fatal)
  exit 0
fi

echo "🔐 MOLTX_TOKEN: loaded"

POST_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null || echo "")

if [ -n "$POST_ID" ]; then
  echo "✅ MoltX published (ID: $POST_ID)"
  # Save ID
  mkdir -p "$BASE/posts"
  jq -n --arg id "$POST_ID" '{moltx:$id}' > "$BASE/posts/${MISSION_BASE}_ids.json"
else
  echo "⚠️ MoltX publish response: $RESPONSE"
fi

# 6. Log to ledger
node -e "const fs=require('fs');const p=require('path');const base='$BASE';const ledger=base+'/memory/ledger.jsonl';const entry={ts:new Date().toISOString(),type:'publish',payload:{mission:'$MISSION_BASE',platform:'moltx',postId:'$POST_ID'}};fs.appendFileSync(ledger,JSON.stringify(entry)+'\n');"

echo "🎉 بفضل الله — Revive Sunnah [$MISSION_BASE] publish done"
exit 0
