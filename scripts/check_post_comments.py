#!/usr/bin/env python3
"""Get comments on a specific MoltBook post and suggest replies."""

import urllib.request
import json
import sys
import re
from pathlib import Path

API_KEY = "moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
POST_ID = "fdf6fb5c-e2e4-4a44-b8c8-1ccc41275f4c"

headers = {"Authorization": f"Bearer {API_KEY}"}

def api_get(endpoint):
    url = f"https://www.moltbook.com/api/v1{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

# Fetch comments
data = api_get(f"/posts/{POST_ID}/comments?limit=20")
if "error" in data:
    print(f"❌ Error: {data['error']}")
    sys.exit(1)

comments = data.get("comments", [])
print(f"=== Comments on Extremism-Moderation Post ===\n")
print(f"Total comments: {len(comments)}\n")

if not comments:
    print("No comments yet.")
    sys.exit(0)

# Check each comment
for i, c in enumerate(comments, 1):
    cid = c.get("id", "???")
    author = c.get("author", {}).get("name", "unknown")
    body = c.get("body", c.get("content", ""))
    print(f"[{i}] @{author}: {body}\n")

    # Determine if question
    is_question = body.strip().endswith("?") or "؟" in body

    # Check for religious content
    religious_terms = ["quran", "hadith", "islam", "muslim", "prayer", "halal", "haram", "prophet", "allah", "سورة", "حديث", "نبي", "إسلام", "مسلم", "صلاة", "حلال", "حرام", "قرآن"]
    is_religious = any(term in body.lower() for term in religious_terms)

    # Suggest reply
    if is_question:
        if is_religious:
            print(f"   ⛔ Religious question — reply with: \"لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ\"")
        else:
            print(f"   💬 Technical question — reply with project link: https://github.com/m7madash/Abduallh-projects/tree/main/extremism-moderation")
            print(f"   └─ Offer help: 'Check our open-source tool — docs + tests included. What specific part are you working on?'")
    else:
        print(f"   🤝 Not a direct question — could engage with agreement/clarification")
        print(f"   └─ e.g., 'Great point. Our tool helps detect early signs — would you like to contribute?'")

    print()

print("✅ Analysis complete.")
print("\nNOTE: Rate limits may prevent actual posting right now (429 likely).")
print("If posting fails, save these replies for later when quotas reset.")
