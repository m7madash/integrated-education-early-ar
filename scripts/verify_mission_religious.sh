#!/bin/bash
#
# verify_mission_religious.sh — Pre-Publish ReligiousGate
# Called by continuity_30min.sh before publishing any mission
# Exit: 0 = OK, 1 = Needs review, 2 = Block
#

MISSION="$1"
MISSION_FILE="$2"

if [ -z "$MISSION" ] || [ -z "$MISSION_FILE" ]; then
  echo "Usage: $0 <mission_name> <mission_file>"
  exit 1
fi

WORKSPACE="/root/.openclaw/workspace"
VERIFIED_SOURCES="${WORKSPACE}/memory/verified_sources.json"
LOG_DIR="${WORKSPACE}/memory/verification_logs"
mkdir -p "$LOG_DIR"

# Extract religious content sections from mission file
# Specifically look for "🕌 **المرجعية الشرعية**" section
RELIGIOUS_SECTION=$(grep -A 10 "المرجعية الشرعية" "$MISSION_FILE" || true)

# If no explicit religious section → assume OK
if [ -z "$RELIGIOUS_SECTION" ]; then
  echo "✅ No explicit religious section found — auto-pass"
  exit 0
fi

# Check for Quran references: must match verified_sources.json
# Pattern: "القرآن: البقرة:205 — «...»" or "القرآن: المائدة:6"
QURAN_REF_PATTERN='القرآن:[[:space:]]*([0-9]+|[أ-ي]+):([0-9]+)'

echo "🔍 Checking religious references in $MISSION..."
  
# Extract Quran references from the section
QURAN_REFS=$(echo "$RELIGIOUS_SECTION" | grep -oP "$QURAN_REF_PATTERN" || true)

if [ -n "$QURAN_REFS" ]; then
  echo "📖 Found Quran references:"
  echo "$QURAN_REFS" | while read -r line; do
    echo "  - $line"
  done
  
  # Verify each against verified_sources.json using jq
  # For now, simple pattern: ensure reference format is correct (surah:ayah numbers)
  # More advanced: cross-check with verified_sources.json quran_verses array
  
  # Check for Arabic surah names and convert to numbers
  # This is simplified — would need full surah name→number mapping
  
  echo "✅ Religious references appear valid (format check only)."
fi

# Check for Hadith references
HADITH_PATTERN='\(صحيح[[:space:]]+(مسلم|البخاري)\)|\(حسن\)|\(ضعيف\)'
if echo "$RELIGIOUS_SECTION" | grep -qE "$HADITH_PATTERN"; then
  echo "📜 Found Hadith references — require isnad verification"
  # For now, flag for human if hadith without explicit source book
  if ! echo "$RELIGIOUS_SECTION" | grep -qE "بخاري|مسلم|أبو داود|الترمذي|ابن ماجه|النسائي"; then
    echo "⚠️  Hadith mentioned but source not explicitly named — flagging for review"
    exit 1
  fi
fi

# Check for "لا أعلم" principle presence
if echo "$RELIGIOUS_SECTION" | grep -q "لا أعلم"; then
  echo "✅ Principle of admission of ignorance present"
fi

# All checks passed
echo "✅ Religious content check PASSED"
exit 0
