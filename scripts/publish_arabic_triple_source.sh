#!/bin/bash
set -e
MISSION="$1"
BASE="/root/.openclaw/workspace"
CONFIG="$BASE/config/triple_source_curriculum_v1.json"
FILE="$BASE/missions/${MISSION}_analytical_ar.md"
TINY="$BASE/missions/${MISSION}_tiny_analytical_ar.md"
[ -z "$MISSION" ] && { echo "❌ يرجى اسم المهمة (مثال: injustice_justice)"; exit 1; }
[ -f "$FILE" ] || { echo "❌ ملف المهمة غير موجود: $FILE"; exit 1; }
echo "🕌 Starting triple-source publish for: $MISSION"
MISSION_CONFIG=$(jq -r ".topics[\"$MISSION\"] // empty" "$CONFIG" 2>/dev/null || echo "")
if [ -z "$MISSION_CONFIG" ]; then
  echo "⚠️ Mission not in triple-source config — falling back to legacy mode"
  exec "$BASE/scripts/publish_arabic_v3_fixed.sh" "$MISSION"
fi
echo "✅ Mission found in triple-source curriculum"

# ---- Build Quran section using config ----
QURAN_SURAH_LIST=$(echo "$MISSION_CONFIG" | jq -r '.quran.primary_surah[]')
QURAN_TEXT="🕌 من القرآن:\n\n"
for SURAH in $QURAN_SURAH_LIST; do
  # Check if this surah is in full_surah_include
  IS_FULL=$(echo "$MISSION_CONFIG" | jq -r ".quran.full_surah_include[]? | select(. == $SURAH)" 2>/dev/null || echo "")
  if [ -n "$IS_FULL" ]; then
    QURAN_TEXT+="**سورة ${SURAH} كاملة:**\n"
    VERSE_OUTPUT=$(node "$BASE/scripts/quran_reader.js" "$SURAH" 2>/dev/null || echo "⚠️ Surah $SURAH not found")
    QURAN_TEXT+="$VERSE_OUTPUT\n\n"
  else
    # Get selected verses for this surah (numeric comparison)
    VERSE_RANGES=$(echo "$MISSION_CONFIG" | jq -r ".quran.selected_verses[] | select(.surah == $SURAH) | .verse_range")
    if [ -n "$VERSE_RANGES" ]; then
      QURAN_TEXT+="**من سورة ${SURAH}:**\n"
      for VR in $VERSE_RANGES; do
        VERSE_OUTPUT=$(node "$BASE/scripts/quran_reader.js" "$SURAH" "$VR" 2>/dev/null || echo "⚠️ Verses $VR not found")
        QURAN_TEXT+="$VERSE_OUTPUT\n"
      done
      QURAN_TEXT+="\n"
    fi
  fi
done

# ---- Sunnah ----
SUNNAH_TEXT=""
SUNNAH_COUNT=$(echo "$MISSION_CONFIG" | jq -r '.sunnah.hadiths | length')
if [ "$SUNNAH_COUNT" -gt 0 ]; then
  SUNNAH_TEXT="📖 من السنة النبوية (صحيح البخاري/مسلم):\n\n"
  for i in $(seq 0 $((SUNNAH_COUNT-1))); do
    HADITH=$(echo "$MISSION_CONFIG" | jq -r ".sunnah.hadiths[$i] | \"\(.source) \(.book) \(.hadith_num): \(.text)\"")
    SUNNAH_TEXT+="$HADITH\n\n"
  done
fi

# ---- Sahabah ----
SAHABA_TEXT=""
SAHABA_COUNT=$(echo "$MISSION_CONFIG" | jq -r '.sahaba.consensus_items | length')
if [ "$SAHABA_COUNT" -gt 0 ]; then
  SAHABA_TEXT="👥 من إجماع الصحابة:\n\n"
  for i in $(seq 0 $((SAHABA_COUNT-1))); do
    SA=$(echo "$MISSION_CONFIG" | jq -r ".sahaba.consensus_items[$i] | \"\(.sahabi): \\\"\(.quote)\\\" — \(.source_book) — \(.context)\"")
    SAHABA_TEXT+="$SA\n\n"
  done
fi

APP_TEXT="💡 التطبيق العملي:\n— بناءً على النص القرآني والسنة النبوية وإجماع الصحابة\n— كيف نطبّق هذه القيم في أنظمتنا اليوم؟\n\n"
HASHTAGS="#${MISSION} #عدل"
cat > "$FILE" << EOF
بفضل الله

📌 الموضوع: ${MISSION} — استناداً إلى القرآن والسنة والإجماع

${QURAN_TEXT}
${SUNNAH_TEXT}${SAHABA_TEXT}${APP_TEXT}${HASHTAGS}
EOF
python3 -c "
import sys
content = open('$FILE').read()
body = content.split('بفضل الله\n\n', 1)[-1]
tiny = body[:280]
print('بفضل الله\n\n' + tiny)
" > "$TINY"
echo "✅ Post built: $FILE"
echo "🔍 Running verification..."
if ! node "$BASE/scripts/verify_full_arabic.js" "$MISSION" "$FILE" 2>/dev/null; then
  echo "❌ Verification failed: non-Arabic content"; exit 1; fi
if ! "$BASE/scripts/verify_mission_religious.sh" "$MISSION" "$FILE" 2>/dev/null; then
  echo "❌ Religious verification failed"; exit 1; fi
echo "✅ Content verified"
echo "📤 Publishing via publisher_wrapper.js..."
node "$BASE/scripts/content_shield/publisher_wrapper.js" --mission "$MISSION" --file "$FILE" --tiny "$TINY" --mode triple_source
echo "✅ Publish cycle complete"
exit 0
