#!/bin/bash
# Agent Pulse Monitor — runs every 30 minutes
# Checks: GitHub updates, social interactions, cron status, project health
# Output: concise status report + action items

set -e

LOG_FILE="/root/.openclaw/workspace/logs/agent_pulse_$(date +%Y-%m-%d).log"
REPORT_FILE="/root/.openclaw/workspace/logs/pulse_report_$(date +%Y-%m-%d_%H%M).txt"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"; }

echo "=== AGENT PULSE MONITOR ===" | tee -a "$LOG_FILE"
echo "Time: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 1. GitHub recent commits (m7mad-ai-work)
echo "📦 Recent commits (m7mad-ai-work):" | tee -a "$LOG_FILE"
cd /root/.openclaw/workspace
git -C . log --oneline -5 | tee -a "$LOG_FILE" || echo "  (cannot read git log)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 2. Check if any pending social notifications (quick API ping)
echo "📱 Social platforms check:" | tee -a "$LOG_FILE"
# MoltBook
if [ -f /root/.config/moltbook/credentials.json ]; then
  TOKEN=$(jq -r .token /root/.config/moltbook/credentials.json 2>/dev/null || echo "")
  if [ -n "$TOKEN" ]; then
    # Check notifications (if endpoint exists)
    # curl -s "https://www.moltbook.com/api/v1/notifications" -H "Authorization: Bearer $TOKEN" | head -5 >> "$LOG_FILE" || true
    echo "  MoltBook: credentials present (API pending validation)" | tee -a "$LOG_FILE"
  else
    echo "  MoltBook: no token" | tee -a "$LOG_FILE"
  fi
else
  echo "  MoltBook: no credentials file" | tee -a "$LOG_FILE"
fi
# Moltter
if [ -f /root/.config/moltter/credentials.json ]; then
  echo "  Moltter: credentials present" | tee -a "$LOG_FILE"
else
  echo "  Moltter: no credentials" | tee -a "$LOG_FILE"
fi
echo "" | tee -a "$LOG_FILE"

# 3. Cron jobs status (next scheduled run)
echo "⏰ Next cron runs:" | tee -a "$LOG_FILE"
NEXT_HOUR=$(( $(date +%H) + 1 ))
if [ $NEXT_HOUR -ge 24 ]; then NEXT_HOUR=0; fi
# Check if any mission post scheduled in next hour
cat /root/.openclaw/workspace/cron/jobs.json | grep -E "\"schedule\": \"0 ${NEXT_HOUR} " | wc -l | awk '{print "  Missions at ${NEXT_HOUR}:00 — "$1" job(s)"}' | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 4. Project health (uncommitted changes)
echo "🔧 Uncommitted changes:" | tee -a "$LOG_FILE"
git status --short 2>/dev/null | grep -v "^??" | wc -l | awk '{print "  Staged files: "$1}' | tee -a "$LOG_FILE"
git status --short 2>/dev/null | grep "^??" | wc -l | awk '{print "  Untracked files: "$1}' | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 5. Action items
echo "🎯 Action items for next 30 minutes:" | tee -a "$LOG_FILE"
# If there are uncommitted files, suggest commit
UNTRACKED=$(git status --short 2>/dev/null | grep "^??" | wc -l)
if [ "$UNTRACKED" -gt 0 ]; then
  echo "  • Commit/push uncommitted work ($UNTRACKED files pending)" | tee -a "$LOG_FILE"
fi
# If social platforms need attention (no tokens?), flag
if [ ! -f /root/.config/moltbook/credentials.json ]; then
  echo "  • Re-establish MoltBook API key (expired)" | tee -a "$LOG_FILE"
fi
echo "  • Continue Tool 5 (Academic Prosecutor) or Fajr Observer dataset collection" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Write human-readable report
cat << EOF > "$REPORT_FILE"
AGENT PULSE REPORT — $(date '+%Y-%m-%d %H:%M')

🔹 Status: Active — Monitoring every 30 minutes

📦 GIT (m7mad-ai-work):
$(git -C /root/.openclaw/workspace log --oneline -3)

📱 SOCIAL:
$(for p in moltbook moltter moltX; do echo "  $p: $(if [ -f /root/.config/$p/credentials.json ]; then echo 'credentials ✓'; else echo 'no credentials'; fi)"; done)

⏰ NEXT CRON: $(date -d '+1 hour' '+%H:00') — check schedule

🔧 UNCOMMITTED: $(git status --short 2>/dev/null | grep -v "^??" | wc -l) staged, $(git status --short 2>/dev/null | grep "^??" | wc -l) untracked

✅ NEXT STEPS:
1. Continue Tool 5 (Academic Prosecutor) OR
2. Collect Fajr Observer training images
3. Check social platforms for replies (18:30 already done)

---
EOF

cat "$REPORT_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "✅ Pulse monitor complete. Report saved to: $REPORT_FILE" | tee -a "$LOG_FILE"
