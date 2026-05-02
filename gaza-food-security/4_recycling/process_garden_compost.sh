#!/bin/bash
# Process garden waste into compost
# Input: $1 = source directory with garden clippings, leaves
# Output: $2 = destination for compost piles

SOURCE="$1"
DEST="$2"
mkdir -p "$DEST"

echo "Processing garden waste to compost..."

# Step 1: Shred/chip (simulated)
echo "  - Shredding material..."
SHREDDED_SIZE=$(du -sk "$SOURCE" | cut -f1)
echo "  Shredded size: ${SHREDDED_SIZE} KB"

# Step 2: Create compost pile
PILE_ID="compost_$(date +%Y%m%d_%H%M)"
PILE_DIR="$DEST/$PILE_ID"
mkdir -p "$PILE_DIR"

# Record pile composition
cat > "$PILE_DIR/manifest.json" <<EOF
{
  "pile_id": "$PILE_ID",
  "created_at": "$(date -Iseconds)",
  "source_material": "$SOURCE",
  "estimated_kg": $((SHREDDED_SIZE / 1024)),
  "type": "garden_waste",
  "status": "composting",
  "turn_count": 0,
  "expected_completion_days": 60
}
EOF

# Step 3: Simulate moisture adjustment
echo "  - Adjusting moisture (40-60% target)"
echo "  - Pile created: $PILE_ID"

echo "$(date '+%Y-%m-%d %H:%M:%S') COMPOST_PILE_CREATED $PILE_ID $SOURCE" >> /root/.openclaw/workspace/gaza-food-security/4_recycling/collection.log

echo "  ✓ Compost pile $PILE_ID started. Ready in ~60 days."
