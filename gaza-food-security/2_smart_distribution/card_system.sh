#!/bin/bash
# Smart Voucher Card System for Gaza Food Security
# Generates and manages smart cards for families

CARDS_DB="$WORKSPACE/2_smart_distribution/cards_database.json"
TRANSACTIONS_LOG="$WORKSPACE/2_smart_distribution/transactions.log"

# Initialize database if not exists
if [ ! -f "$CARDS_DB" ]; then
  echo '{"cards": []}' > "$CARDS_DB"
fi

generate_card() {
  local family_id="$1"
  local priority_score="$2"
  
  # Card number: GF-YYYYMMDD-XXXX (GF = Gaza Food)
  local card_num="GF-$(date +%Y%m%d)-$(openssl rand -hex 3 | tr '[:lower:]' '[:upper:]')"
  
  # Monthly allocation based on priority and family size
  # Base 200 NIS + 50 per child + 30 per elderly + 20 per additional adult
  # Get family data
  local family_json=$(jq ".families[] | select(.id==\"$family_id\")" "$WORKSPACE/1_assessment/families_register.json")
  local children=$(echo "$family_json" | jq '.children')
  local elderly=$(echo "$family_json" | jq '.elderly')
  local members=$(echo "$family_json" | jq '.members')
  local adults=$((members - children - elderly))
  
  local allocation=$((200 + children*50 + elderly*30 + adults*20))
  
  # Adjust by priority factor (0.5 to 1.5)
  local priority_factor=$(echo "scale=2; 0.5 + ($priority_score/15)*1.0" | bc)
  allocation=$(printf "%.0f" "$(echo "$allocation * $priority_factor" | bc)")
  
  # Create card entry
  local card_entry=$(cat <<EOF
{
  "card_number": "$card_num",
  "family_id": "$family_id",
  "priority_score": $priority_score,
  "monthly_allocation_nis": $allocation,
  "current_balance_nis": $allocation,
  "pin": "$(openssl rand -hex 2)",
  "activated_at": "$(date -Iseconds)",
  "expires_at": "$(date -Iseconds -d "+1 year")",
  "status": "active",
  "allowed_items": ["rice", "lentils", "oil", "milk_powder", "sugar", "canned_fish", "flour", "salt"],
  "transaction_count": 0
}
EOF
)
  
  # Append to database
  jq ".cards += [$card_entry]" "$CARDS_DB" > tmp.json && mv tmp.json "$CARDS_DB"
  
  echo "✅ Card generated: $card_num"
  echo "   Family: $family_id"
  echo "   Allocation: $allocation NIS/month"
  echo "   PIN: $(echo "$card_entry" | jq -r '.pin')"
  echo "   Allowed items: $(echo "$card_entry" | jq -r '.allowed_items[]')"
  
  # Log transaction
  echo "$(date -Iseconds) CARD_CREATE $card_num $family_id $allocation NIS" >> "$TRANSACTIONS_LOG"
}

activate_card() {
  local card_num="$1"
  jq ".cards[] | select(.card_number==\"$card_num\") | .status = \"active\"" "$CARDS_DB" > tmp.json && mv tmp.json "$CARDS_DB"
  echo "✅ Card $card_num activated"
}

deduct_purchase() {
  local card_num="$1"
  local item="$2"
  local quantity="$3"
  local price_per_unit="$4"
  
  # Get card
  local card=$(jq ".cards[] | select(.card_number==\"$card_num\")" "$CARDS_DB")
  if [ -z "$card" ]; then
    echo "❌ Card not found"
    return 1
  fi
  
  # Check if item allowed
  local allowed=$(echo "$card" | jq -r '.allowed_items[]')
  if ! echo "$allowed" | grep -q "^$item$"; then
    echo "❌ Item $item not allowed on this card"
    return 1
  fi
  
  # Calculate cost
  local total_cost=$(echo "$quantity * $price_per_unit" | bc)
  local current_balance=$(echo "$card" | jq -r '.current_balance_nis')
  
  if (( $(echo "$total_cost > $current_balance" | bc -l) )); then
    echo "❌ Insufficient balance: $current_balance NIS, need $total_cost NIS"
    return 1
  fi
  
  # Deduct
  local new_balance=$(echo "$current_balance - $total_cost" | bc)
  jq --arg num "$card_num" --arg nb "$new_balance" '.cards[] | select(.card_number==$num) | .current_balance_nis = ($nb|tonumber) | .transaction_count += 1' "$CARDS_DB" > tmp.json && mv tmp.json "$CARDS_DB"
  
  echo "✅ Purchased $quantity $item for $total_cost NIS. New balance: $new_balance NIS"
  echo "$(date -Iseconds) PURCHASE $card_num $item $quantity $price_per_unit $total_cost" >> "$TRANSACTIONS_LOG"
}

# CLI
case "$1" in
  generate)
    generate_card "$2" "$3"
    ;;
  activate)
    activate_card "$2"
    ;;
  deduct)
    deduct_purchase "$2" "$3" "$4" "$5"
    ;;
  *)
    echo "Usage: $0 {generate|activate|deduct} [args]"
    echo "Examples:"
    echo "  $0 generate FAM001 10   # Generate card for family FAM001 with priority 10"
    echo "  $0 activate GF-20260502-ABC123"
    echo "  $0 deduct GF-20260502-ABC123 rice 5 3.5  # 5kg rice at 3.5 NIS/kg"
    exit 1
esac
