#!/bin/bash
#
# verify_mission_religious.sh — Pre-Publish Religious Content Gate (v2)
# Blocks: Quran verses, hadith citations, surah:ayah refs in published content
# Exit: 0=clean, 1=blocked

MISSION="$1"
MISSION_FILE="$2"

if [ -z "$MISSION" ] || [ -z "$MISSION_FILE" ]; then
  echo "Usage: $0 <mission_name> <mission_file>"
  exit 2
fi

BASE="/root/.openclaw/workspace"
WORKSPACE="/root/.openclaw/workspace"
LOG_DIR="${WORKSPACE}/memory/verification_logs"
mkdir -p "$LOG_DIR"

HIT_COUNT=0
HIT_LIST=""

# Gate 1: surah:ayah in brackets [{سورة X: Y}]
if grep -qPn '\[[^\]]*[أ-ي]+[[:space:]]*:[[:space:]]*[0-9]+[^\]]*\]' "$MISSION_FILE" 2>/dev/null; then
  HIT_LIST="${HIT_LIST}  - Block A: [سورة/سورة:آية] format in brackets\n"
  HIT_COUNT=$((HIT_COUNT+1))
fi

# Gate 2: «...» delimited Arabic text (common for ayah/hadith copying)
if grep -q '«[^»]+»' "$MISSION_FILE" 2>/dev/null; then
  HIT_LIST="${HIT_LIST}  - Block B: «...» quoted text (typically verse/hadith)\n"
  HIT_COUNT=$((HIT_COUNT+1))
fi

# Gate 3: Explicit Hadith source mentions
if grep -qP '(صحيح\s+(البخاري|مسلم)|صحيح\s+السنن|أبو\s+داود|النسائي|الترمذي)' "$MISSION_FILE" 2>/dev/null; then
  HIT_LIST="${HIT_LIST}  - Block C: hadith source name\n"
  HIT_COUNT=$((HIT_COUNT+1))
fi

# Gate 4: "القرآن: Surah:Ayah" inline format
if grep -qP 'القرآن:\s*(\([^)]+\)|[أ-ي]+:[0-9]+)' "$MISSION_FILE" 2>/dev/null; then
  HIT_LIST="${HIT_LIST}  - Block D: القرآن inline citation\n"
  HIT_COUNT=$((HIT_COUNT+1))
fi

# Gate 5: "الحديث:" prefix
if grep -q 'الحديث:' "$MISSION_FILE" 2>/dev/null; then
  HIT_LIST="${HIT_LIST}  - Block E: الحديث: prefix\n"
  HIT_COUNT=$((HIT_COUNT+1))
fi

# Gate 6: "المرجعية الشرعية" section (legacy)
if grep -q 'المرجعية الشرعية' "$MISSION_FILE" 2>/dev/null; then
  HIT_LIST="${HIT_LIST}  - Block F: المراجع الشرعية section still present\n"
  HIT_COUNT=$((HIT_COUNT+1))
fi

if [ "$HIT_COUNT" -gt 0 ]; then
  echo "BLOCKED [$MISSION] — $HIT_COUNT religious reference violation(s):"
  echo -e "$HIT_LIST"
  echo "🛑 publish [$MISSION] aborted — religious content gate triggered" >> "${LOG_DIR}/religion_block_$(date -u '+%Y-%m-%d').log"
  echo "$(date -u '+%Y-%m-%dT%H:%M:%SZ') BLOCKED $MISSION ($HIT_COUNT violations)" >> "${LOG_DIR}/religion_block_$(date -u '+%Y-%m-%d').log"
  exit 1
fi

# All gates clean
echo "✅ [$MISSION] clean — no religious references found"
exit 0
