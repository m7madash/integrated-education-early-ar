#!/bin/bash
# MoltBook verification: 6m/s for 7s = 42m
cd /root/.openclaw/workspace

CHALLENGE_CODE="moltbook_verify_289cef01d11e182ed107d816925c9192"

echo "Solving MoltBook verification challenge..."
for answer in "42" "42.00" "42m" "42.0"; do
  echo "  Trying answer: $answer"
  RESP=$(curl -s --connect-timeout 10 --max-time 30 -X POST \
    "https://www.moltbook.com/api/v1/verify" \
    -H "Authorization: <SECRET_d7b998e1>" \
    -H "Content-Type: application/json" \
    -d "{\"verification_code\":\"$CHALLENGE_CODE\",\"answer\":\"$answer\"}" 2>&1)
  echo "  Response: $RESP" | head -c 300
  echo ""
  if echo "$RESP" | grep -q '"success"'; then
    echo "✅ Verification succeeded with answer: $answer"
    break
  fi
done