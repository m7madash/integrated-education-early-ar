#!/usr/bin/env python3
"""Check activity across 9 mission communities on MoltBook."""

import urllib.request
import json
import sys

API_KEY = "moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
API_BASE = "https://www.moltbook.com/api/v1"

communities = [
    "injustice-justice",
    "poverty-dignity",
    "ignorance-knowledge",
    "war-peace",
    "pollution-cleanliness",
    "illness-health",
    "slavery-freedom",
    "extremism-moderation",
    "division-unity",
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def api_get(path):
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

print("=== Mission Communities Check ===\n")
for slug in communities:
    data = api_get(f"/submolts/{slug}/posts?sort=new&limit=3")
    if "error" in data:
        print(f"❌ {slug}: ERROR — {data['error']}")
        continue
    
    posts = data.get("posts", [])
    count = len(posts)
    if count == 0:
        print(f"🔍 {slug}: No recent posts")
    else:
        print(f"📌 {slug}: {count} recent post(s)")
        for post in posts[:2]:  # show up to 2
            title = post.get("title", "Untitled")
            post_id = post.get("id", "???")
            print(f"   → [{post_id}] {title}")
        if count > 2:
            print(f"   ... +{count-2} more")

print("\n✅ Check complete.")
