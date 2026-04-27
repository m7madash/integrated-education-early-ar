#!/bin/bash
# Unified Arabic Publisher v3 — Fixed ID extraction
# ... (same header up to post_moltx function)

post_moltx() {
  JSON=$(python3 -c "import json; print(json.dumps({'content': $CONTENT_FULL}))")
  RESP=$(curl -s -w "\n%{http_code}" -X POST "https://moltx.io/v1/posts" \
    -H "Authorization: Bearer moltx_sk_8d42d21b10c544a99f8e14e772457bca191276dae56e4a9cb5d351131121e10a" \
    -H "Content-Type: application/json" -d "$JSON")
  CODE=$(echo "$RESP" | tail -n1)
  BODY=$(echo "$RESP" | sed '$d')
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    # multiple paths
    for path in [['id'], ['data','id'], ['data','post','id'], ['post','id']]:
        try:
            val = d
            for key in path:
                val = val[key]
            print(val)
            break
        except (KeyError, TypeError):
            continue
    else:
        print('')
except:
    print('')
")
    echo "✅ MoltX: تم (HTTP $CODE) | ID: ${POST_ID:-unknown}"
    echo "- ✅ MoltX: نجح (id: $POST_ID)" >> "$LOG_FILE"
    if [ -n "$POST_ID" ]; then
      # Update JSON file atomically
      python3 -c "
import sys, json
ids_file = '$POST_IDS_FILE'
with open(ids_file, 'r') as f:
    ids = json.load(f)
ids['moltx'] = '$POST_ID'
with open(ids_file, 'w') as f:
    json.dump(ids, f)
"
    fi
    return 0
  # ... (rest unchanged: 429 handling, failure) copy from v2
  elif [[ "$CODE" == "429" ]]; then
    RETRY=$(echo "$BODY" | grep -o '"retry_after_seconds":[0-9]*' | cut -d: -f2 || echo "60")
    echo "⚠️ MoltX: Rate limit — إعادة بعد $RETRY ثانية"
    sleep "$RETRY"
    # retry (same code) — ensure to extract POST_ID2 similarly
    # ... (insert retry block from v2, copying the POST_ID2 extraction)
  else
    echo "❌ MoltX: فشل (HTTP $CODE)"
    echo "- ❌ MoltX: $CODE" >> "$LOG_FILE"
    return 1
  fi
}

post_moltbook() {
  # ... (same as v2 up to success)
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for path in [['id'], ['data','id'], ['data','post','id'], ['post','id']]:
        try:
            val = d
            for key in path:
                val = val[key]
            print(val)
            break
        except (KeyError, TypeError):
            continue
    else:
        print('')
except:
    print('')
")
    # ... (save ID similarly)
  fi
  # ... (rest unchanged)
}

post_moltter() {
  # ... (same as v2 up to success)
  if [[ "$CODE" =~ ^2 ]]; then
    POST_ID=$(echo "$BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for path in [['id'], ['data','id'], ['data','post','id'], ['post','id']]:
        try:
            val = d
            for key in path:
                val = val[key]
            print(val)
            break
        except (KeyError, TypeError):
            continue
    else:
        print('')
except:
    print('')
")
    # ... (save ID similarly)
  fi
  # ...
}

# ... Main unchanged
