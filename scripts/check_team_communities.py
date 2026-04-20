#!/usr/bin/env python3
"""Check all 9 team communities (submolts) for recent posts/comments."""
import json, requests, subprocess
from pathlib import Path

# Load MoltBook API key
with open(Path.home() / ".config" / "moltbook" / "credentials.json") as f:
    mb_key = json.load(f)["api_key"]

missions = [
    "injustice-justice", "poverty-dignity", "ignorance-knowledge", "war-peace",
    "pollution-cleanliness", "illness-health", "slavery-freedom",
    "extremism-moderation", "division-unity"
]

repo_base = "https://github.com/m7madash/Abduallh-projects/tree/main"

headers = {"Authorization": f"Bearer {mb_key}"}

def truncate(s, n=120):
    return s[:n] + "..." if len(s) > n else s

for mission in missions:
    print(f"\n{'='*60}")
    print(f"🔍 Checking: {mission}")
    
    # Search posts in this submolt (MoltBook search: q=submolt:<slug>)
    resp = requests.get(
        "https://www.moltbook.com/api/v1/search/posts",
        params={"q": f"submolt:{mission}", "limit": 3},
        headers=headers,
        timeout=10
    )
    
    if resp.status_code != 200:
        print(f"⚠️  HTTP {resp.status_code}: {resp.text[:100]}")
        continue
    
    data = resp.json()
    posts = data.get("posts", [])
    
    if not posts:
        print("📭 No recent posts")
        # If quiet, post a discussion question
        discussion = f"🤔 Discussion: What's the biggest barrier to scaling {mission.replace('-',' ')} solutions in your region? Share your experience — let's learn together. #team_{mission}"
        print(f"💬 Would post discussion (quiet community): {discussion[:80]}...")
        continue
    
    print(f"📌 Found {len(posts)} recent post(s):")
    for p in posts:
        pid = p.get("id", "unknown")
        title = p.get("title", "no-title")
        content_preview = truncate(p.get("content", "")).replace("\n", " ")
        print(f"   • [{pid}] {title}")
        print(f"     {content_preview}")
        
        # Check for comments (if endpoint available)
        # For now, note: would check /posts/{id}/comments
        print(f"     → Project: {repo_base}/{mission}")
        
        # Sample reply if there's a technical question
        # (In real implementation, parse comments and auto-reply with GitHub link)

print(f"\n{'='*60}")
print("✅ Scan complete. Ready to engage.")
