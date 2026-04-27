#!/bin/bash
# Add all 13 daily posts + continuity checks to OpenClaw cron

add_job() {
  local name="$1"
  local cron="$2"
  local mission="$3"
  local tags="$4"
  
  openclaw cron add \
    --name "$name" \
    --cron "$cron" \
    --message "{\"type\":\"system-event\",\"payload\":{\"action\":\"publish_post\",\"mission\":\"$mission\",\"tags\":[$tags]}}" \
    --announce \
    --disabled false
}

# 13 daily posts (all at 00:00 UTC for batch; actual times will be scheduled)
add_job "poverty-dignity" "0 3 * * *" "poverty-dignity" "\"#الكرامة_الاقتصادية\",\"#مكافحة_الفقر\""
add_job "ignorance-knowledge" "0 6 * * *" "ignorance-knowledge" "\"#العلم_الموثق\",\"#محاربة_التضليل\""
add_job "war-peace" "0 9 * * *" "war-peace" "\"#السلام_العادل\",\"#حل_الصراعات\""
add_job "shirk-tawhid" "30 9 * * *" "shirk-tawhid" "\"#التوحيد_الصحيح\",\"#لا_إله_إلا_الله\""
add_job "pollution-cleanliness" "0 12 * * *" "pollution-cleanliness" "\"#النظافة_البيئية\",\"#الاستخلاف_الأرضي\""
add_job "disease-health" "0 15 * * *" "disease-health" "\"#الصحة_للجميع\",\"#الوقاية_خير\""
add_job "slavery-freedom" "0 18 * * *" "slavery-freedom" "\"#الحرية_للجميع\",\"#إنهاء_العبودية\""
add_job "extremism-moderation" "0 21 * * *" "extremism-moderation" "\"#الوسطية_الإسلامية\",\"#التوازن_الفكري\""
add_job "division-unity" "0 0 * * *" "division-unity" "\"#الوحدة_الإسلامية\",\"#لم_الشمل\""

# Internal checks
add_job "connectivity-check" "30 19 * * *" "connectivity_check" "\"#مراقبة_الاتصال\",\"#ضمان_الجودة\""
add_job "dhikr-evening" "0 20 * * *" "dhikr_evening" "\"#تسبيح_مسائي\",\"#أسماء_الله_الحسنى\""
add_job "dhikr-morning" "0 4 * * *" "dhikr_morning" "\"#تسبيح_صباحي\",\"#أسماء_الله_الحسنى\""

echo "✅ Done adding jobs"
