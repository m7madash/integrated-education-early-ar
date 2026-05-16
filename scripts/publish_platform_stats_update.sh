#!/bin/bash
# publish_platform_stats_update.sh
# Diagnostic: compute TRUE platform reliability from today's publish_log
# not from the aggregate entries.

set -u

WORKSPACE="/root/.openclaw/workspace"
TODAY=$(date -u +%Y-%m-%d)
PUBLISH_LOG="$WORKSPACE/memory/publish_log_$TODAY.md"
LEDGER="$WORKSPACE/memory/ledger.jsonl"

echo "=== Platform Publish Stats ($TODAY) ==="
echo ""

# --- From publish_log.md ---
if [ -f "$PUBLISH_LOG" ]; then
  echo "--- publish_log_$TODAY.md ---"
  grep -c "MoltX\|ناجح\|فشل\|failed" "$PUBLISH_LOG" | grep -q '[1-9]' && \
    grep -E "MoltX|Moltter|MoltBook|ناجح|فشل|failed" "$PUBLISH_LOG" | grep -v "^#" | \
    sed 's/ème/ /; s/###.*//'
  echo ""
else
  echo "publish_log_$TODAY.md: NOT FOUND"
fi

# --- From ledger: today's publish_run entries ---
echo "--- today's ledger publish_run entries ---"
grep '"type":"publish_run"' "$LEDGER" 2>/dev/null | grep "$TODAY" | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line)
        p = e.get('payload', {})
        print(f\"  {e['ts'][-12:]} → {p.get('mission','?')}: {p.get('status','?')} | succ={p.get('successCount','-')} | platforms={p.get('platforms','-')}\")
    except: pass
" 2>/dev/null || grep "$TODAY" "$LEDGER" | grep "publish_run"

# --- From ledger: today's continuity_check entries ---
echo ""
echo "--- today's continuity_check KPI entries ---"
grep '"type":"continuity_check"' "$LEDGER" 2>/dev/null | grep "$TODAY" | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line)
        print(f\"  {e['ts'][-12:]} → errRate={e.get('errorRate','?')} | platform={e.get('platformReliability','?')} | coherence={e.get('coherence_score','?'):.4f}\")
    except: pass
" 2>/dev/null || grep "$TODAY" "$LEDGER" | grep "continuity_check"

# --- From ledger: today's platform_health_check entries ---
echo ""
echo "--- today's platform_health_check ---"
grep '"type":"platform_health_check"' "$LEDGER" 2>/dev/null | grep "$TODAY" | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        e = json.loads(line)
        h = e.get('payload', {}).get('health', e.get('health', {}))
        ph = h.get('platformHealth', {})
        print(f\"  {e['ts'][-12:]} → moltx={ph.get('moltx',{}).get('status','?')} moltbook={ph.get('molbook',ph.get('moltbook',{}))} moltter={ph.get('moltter',{}).get('status','?')} | down={h.get('overall',{}).get('down',0)}\")
    except: pass
" 2>/dev/null

# --- Cron errors ---
echo ""
echo "--- openclaw cron jobs with error status ---"
openclaw cron list 2>/dev/null | grep -i error || echo "  (none found)"

echo ""
echo "=== Done ==="
