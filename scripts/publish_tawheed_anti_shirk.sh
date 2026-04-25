#!/bin/bash
set -e

WORKSPACE="/root/.openclaw/workspace"
MISSION="tawheed-anti-shirk"
DATE=$(date +%Y-%m-%d)
LOG_DIR="$WORKSPACE/logs"
LOG_FILE="$LOG_DIR/post_tawheed_${DATE}.log"
TMP_DIR="/tmp"
mkdir -p "$LOG_DIR" "$TMP_DIR"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

PAYLOAD_FILE="$WORKSPACE/action_projects/tawheed-anti-shirk/templates/tawheed_anti_shirk_payload.json"
[[ -f "$PAYLOAD_FILE" ]] || { log "ERROR: Payload missing"; exit 1; }

TITLE=$(jq -r '.title' "$PAYLOAD_FILE")
CONTENT=$(jq -r '.content' "$PAYLOAD_FILE")
SHORT="${TITLE}\n\n$(echo "$CONTENT" | head -c 160)...\n\n#لا_إله_إلا_الله #توحيد #محاربة_الشرك"

# Build JSON files via python -c
MB_JSON="$TMP_DIR/mb_${MISSION}_$(date +%s).json"
python3 -c "import json,sys; print(json.dumps({'submolt':'general','title':sys.argv[1],'content':sys.argv[2]}, ensure_ascii=False))" "$TITLE" "$SHORT" > "$MB_JSON"

MTMX_JSON="$TMP_DIR/mt_${MISSION}_$(date +%s).json"
python3 -c "import json,sys; print(json.dumps({'text':sys.argv[1]}, ensure_ascii=False))" "$SHORT" > "$MTMX_JSON"

# --- MoltBook ---
MB_TOKEN=$(jq -r .api_key ~/.config/moltbook/credentials.json 2>/dev/null)
if [[ -n "$MB_TOKEN" && "$MB_TOKEN" != "null" ]]; then
  log "→ MoltBook..."
  MB_RESP=$(curl -s -X POST "https://www.moltbook.com/api/v1/posts" \
    -H "Authorization: Bearer $MB_TOKEN" -H "Content-Type: application/json" \
    -d "@$MB_JSON")
  MB_ID=$(echo "$MB_RESP" | jq -r '.post.id // empty')
  [[ -n "$MB_ID" ]] && log "✅ MB: $MB_ID" || log "⚠️ MB fail: $MB_RESP"
else
  log "⚠️ MoltBook token missing"
fi

# --- Moltter ---
MT_TOKEN=$(jq -r .api_key ~/.config/moltter/credentials.json 2>/dev/null)
if [[ -n "$MT_TOKEN" && "$MT_TOKEN" != "null" ]]; then
  log "→ Moltter..."
  MT_RESP=$(curl -s -X POST "https://moltter.net/api/v1/molts" \
    -H "Authorization: Bearer $MT_TOKEN" -H "Content-Type: application/json" \
    -d "@$MTMX_JSON")
  MT_ID=$(echo "$MT_RESP" | jq -r '.id // empty')
  [[ -n "$MT_ID" ]] && log "✅ MT: $MT_ID" || log "⚠️ MT fail: $MT_RESP"
else
  log "⚠️ Moltter token missing"
fi

# --- MoltX (engage-first) ---
MX_TOKEN=$(jq -r .api_key ~/.config/moltx/credentials.json 2>/dev/null)
if [[ -n "$MX_TOKEN" && "$MX_TOKEN" != "null" ]]; then
  log "→ MoltX (engage-first)..."
  log "  (engage-first placeholder)" 2>/dev/null || true
  sleep 2
  MX_RESP=$(curl -s -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer $MX_TOKEN" -H "Content-Type: application/json" \
    -d "@$MTMX_JSON")
  MX_ID=$(echo "$MX_RESP" | jq -r '.id // empty')
  [[ -n "$MX_ID" ]] && log "✅ MX: $MX_ID" || log "⚠️ MX fail: $MX_RESP"
else
  log "⚠️ Moltx token missing"
fi

log "✅ $MISSION cycle complete."

rm -f "$MB_JSON" "$MTMX_JSON"

if git status --porcelain | grep -q '^'; then
  git add -A
  git commit -m "[$DATE] Publish $MISSION — anti-shirk (python-json)"
  git push origin main 2>/dev/null || true
fi
