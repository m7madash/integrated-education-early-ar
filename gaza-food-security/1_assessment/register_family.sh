#!/bin/bash
# Gaza Food Security — Family Registration
# Usage: ./register_family.sh <family_id> <members> <children> <elderly> <income_nis> <phone>

set -e

WORKSPACE="/root/.openclaw/workspace/gaza-food-security"
DATA_DIR="$WORKSPACE/1_assessment"
REGISTER_FILE="$DATA_DIR/families_register.json"

# Validate input
if [ $# -ne 6 ]; then
  echo "Usage: $0 <family_id> <members> <children> <elderly> <income_nis> <phone>"
  exit 1
fi

FAMILY_ID="$1"
MEMBERS="$2"
CHILDREN="$3"
ELDERLY="$4"
INCOME="$5"
PHONE="$6"

# Compute priority score (0-15)
# Formula: children*3 + elderly*2 + income_need
# income_need = max(0, (threshold - income)/100)
THRESHOLD=2500  # poverty line NIS/month
INCOME_NEED=$(echo "scale=2; if ($INCOME < $THRESHOLD) { ($THRESHOLD - $INCOME)/100 } else { 0 }" | bc)
PRIORITY_SCORE=$(echo "$CHILDREN*3 + $ELDERLY*2 + $INCOME_NEED" | bc)

# Round to integer
PRIORITY_SCORE=$(printf "%.0f" "$PRIORITY_SCORE")
if [ $PRIORITY_SCORE -gt 15 ]; then PRIORITY_SCORE=15; fi

# Create JSON entry
cat >> "$REGISTER_FILE" <<EOF
{
  "id": "$FAMILY_ID",
  "members": $MEMBERS,
  "children": $CHILDREN,
  "elderly": $ELDERLY,
  "income_nis": $INCOME,
  "phone": "$PHONE",
  "priority_score": $PRIORITY_SCORE,
  "registered_at": "$(date -Iseconds)",
  "distributed_this_month": 0,
  "last_distribution": null
}
EOF

echo "✅ Family $FAMILY_ID registered with priority score: $PRIORITY_SCORE"
echo "📁 Data saved to: $REGISTER_FILE"

# Show recommendation
if [ $PRIORITY_SCORE -ge 12 ]; then
  echo "🎯 Category: CRITICAL — distribute weekly"
elif [ $PRIORITY_SCORE -ge 8 ]; then
  echo "🎯 Category: HIGH — distribute bi-weekly"
elif [ $PRIORITY_SCORE -ge 4 ]; then
  echo "🎯 Category: MEDIUM — distribute monthly"
else
  echo "🎯 Category: LOW — as-needed"
fi
