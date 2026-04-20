#!/bin/bash
# Continuity Reminder — every 30 minutes
# Reminds you to continue working on the CURRENT project/tool
# Reads the active project from a state file (created by last work session)

STATE_FILE="/root/.openclaw/workspace/.current_project_state"
LOG_FILE="/root/.openclaw/workspace/logs/continuity_$(date +%Y-%m-%d).log"

# Read current project from state file (if exists)
if [ -f "$STATE_FILE" ]; then
  PROJECT=$(cat "$STATE_FILE" | head -1 | tr -d '\n')
  TASK=$(cat "$STATE_FILE" | sed -n '2p' 2>/dev/null || echo "continue development")
  PHASE=$(cat "$STATE_FILE" | sed -n '3p' 2>/dev/null || echo "")
else
  PROJECT="Fajr Observer (default)"
  TASK="collect training images OR continue Tool 5 (Academic Prosecutor)"
  PHASE="prototype"
fi

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Build reminder message
MSG="🔄 Continuity Reminder — $TIMESTAMP
📌 Project: $PROJECT
🎯 Current Task: $TASK"

if [ -n "$PHASE" ]; then
  MSG="$MSG\n📊 Phase: $PHASE"
fi

MSG="$MSG\n\n💡 ACTIONS for next 30 min (choose based on project):"

# Suggest actions based on project name
case "$PROJECT" in
  *"Fajr"*|*"fajr"*)
    MSG="$MSG\n  • Capture real dawn images (use camera or collect from internet)\n  • Label images into: night/, false_dawn/, true_dawn/\n  • Run: python3 models/training/train.py --demo (test pipeline)\n  • Fine-tune thresholds in config/thresholds.json\n  • Test on Raspberry Pi (dry-run first)"
    ;;
  *"Nuclear"*|*"nuclear"*|*"Justice"*)
    MSG="$MSG\n  • Continue Tool 5 (Academic Prosecutor) — design academic sanctions\n  • Or Tool 6 (Diplomatic Lockdown) — plan diplomatic pressure mechanisms\n  • Or complete remaining Tools 7–9\n  • Ensure each tool has: CLI, demo, README, tests"
    ;;
  *)
    MSG="$MSG\n  • Continue coding the current module\n  • Write tests for stability\n  • Update documentation (README, docs/)\n  • Commit & push changes to GitHub"
    ;;
esac

MSG="$MSG\n\n⏰ Remember: Work in focused 30-min bursts. Justice requires consistent effort.\n✅ Log your progress in memory/2026-04-20.md"

# Print to console (captured by cron log)
echo "$MSG"
echo "" | tee -a "$LOG_FILE"

# Optional: send Telegram reminder if bot configured
if [ -f /root/.config/telegram_bot_token ]; then
  BOT_TOKEN=$(jq -r .token /root/.config/telegram_bot_token 2>/dev/null || echo "")
  CHAT_ID=$(jq -r .chat_id /root/.config/telegram_bot_token 2>/dev/null || echo "")
  if [ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
      -d "chat_id=$CHAT_ID" \
      -d "text=$(echo "$MSG" | tr '\n' ' ')'" \
      -d "parse_mode=Markdown" >/dev/null 2>&1
    echo "📱 Telegram reminder sent" | tee -a "$LOG_FILE"
  fi
fi

echo "✅ Reminder delivered. Keep working!" | tee -a "$LOG_FILE"
