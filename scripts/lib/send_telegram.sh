#!/bin/bash
MESSAGE="$1"
curl -s -X POST "" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\":6275105434,\"text\":\"$MESSAGE\"}" > /dev/null 2>&1
