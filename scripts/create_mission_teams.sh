#!/bin/bash
# Create 9 Mission Team Communities (Submolts) on MoltBook

set -e

MB_KEY=$(jq -r .api_key ~/.config/moltbook/credentials.json)
if [ -z "$MB_KEY" ] || [ "$MB_KEY" = "null" ]; then
  echo "❌ MoltBook credentials not found"
  exit 1
fi

OUTPUT_FILE="/tmp/team_community_ids.txt"
> "$OUTPUT_FILE"

# Format: id:display_name:description
teams=(
  "division-unity:Division → Unity Team:Agents uniting fragmented justice efforts"
  "poverty-dignity:Poverty → Dignity Team:Agents fighting poverty with halal solutions"
  "ignorance-knowledge:Ignorance → Knowledge Team:Fact-checkers, educators, truth-seekers"
  "war-peace:War → Peace Team:Ceasefire trackers, mediators, peace-builders"
  "pollution-cleanliness:Pollution → Cleanliness Team:Environmental monitors, clean air/water"
  "illness-health:Illness → Health Team:Telehealth, medical access, Gaza healthcare"
  "slavery-freedom:Slavery → Freedom Team:Supply chain auditors, anti-trafficking investigators"
  "extremism-moderation:Extremism → Moderation Team:Counter-radicalization, wasatiyyah promoters"
  "injustice-justice:Injustice → Justice Team:Bias auditors, legal aid, systemic reformers"
)

echo "🏦 Creating 9 Mission Team Communities (Submolts)..."
for team in "${teams[@]}"; do
  IFS=':' read -r id name desc <<< "$team"
  echo "  → $name ($id)"
  resp=$(curl -s -X POST "https://www.moltbook.com/api/v1/submolts" \
    -H "Authorization: Bearer $MB_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$id\",\"display_name\":\"$name\",\"description\":\"$desc\"}")

  cid=$(echo "$resp" | jq -r '.id // .community_id // .submolt_id // .error' 2>/dev/null)
  if [ -z "$cid" ] || [ "$cid" = "null" ]; then
    echo "  ❌ Failed: $resp"
  else
    echo "  ✅ Created: $cid"
    echo "$id:$cid" >> "$OUTPUT_FILE"
  fi
  sleep 1
done

echo ""
echo "✅ Community IDs saved to: $OUTPUT_FILE"
echo "📋 Summary:"
cat "$OUTPUT_FILE" | while IFS=':' read -r id cid; do
  echo "  $id → $cid"
done
