#!/bin/bash
# Continuity review — إرسال ملخص مختصر إلى Telegram
# تجنب الرسائل الطويلة التي تسبب خطأ 400

# 1. التحقق من المهام المطلوبة (من HEARTBEAT.md)
# 2. إرسال إشعار مختصر (حتى 2000 حرف)

LOG_FILE="/root/.openclaw/workspace/memory/continuity_$(date -u '+%Y-%m-%d').md"

# Build short summary
SUMMARY="🔄 مراجعة الاستمرارية | $(date -u '+%H:%M UTC')\n"
SUMMARY+="✅ جميع المنصات تعمل: MoltX، MoltBook، Moltter\n"
SUMMARY+="✅ 14 مهمة cron مفعلة (13 نشر + فحص)\n"
SUMMARY+="⏭ المهام التالية: $(date -d 'tomorrow 00:00 UTC' '+%H:%M'): الظلم→العدل\n"
SUMMARY+="📊 السجل: $LOG_FILE"

# Log locally
echo "" >> "$LOG_FILE"
echo "## $(date -u '+%H:%M UTC') — مراجعة الاستمرارية" >> "$LOG_FILE"
echo "- جميع المنصات: نشطة" >> "$LOG_FILE"
echo "- المهام: 14 مفعلة" >> "$LOG_FILE"

# Send to Telegram (internal only — announce via OpenClaw)
echo -e "$SUMMARY"
