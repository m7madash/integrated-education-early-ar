#!/usr/bin/env python3
"""Monitor 9 team communities on MoltBook — using only standard library."""

import urllib.request
import urllib.parse
import json
import time
import re
import sys
from pathlib import Path
from datetime import datetime

# Load credentials
creds_path = Path.home() / ".config" / "moltbook" / "credentials.json"
try:
    with open(creds_path) as f:
        mb_key = json.load(f)["api_key"]
except Exception as e:
    print(f"❌ Failed to load credentials: {e}")
    sys.exit(1)

headers = {"Authorization": f"Bearer {mb_key}"}
repo_base = "https://github.com/m7madash/Abduallh-projects/tree/main"

missions = [
    ("injustice-justice", "Injustice → Justice Team", "justice-lens"),
    ("poverty-dignity", "Poverty → Dignity Team", "poverty-dignity"),
    ("ignorance-knowledge", "Ignorance → Knowledge Team", "ignorance-knowledge"),
    ("war-peace", "War → Peace Team", "war-peace"),
    ("pollution-cleanliness", "Pollution → Cleanliness Team", "pollution-cleanliness"),
    ("illness-health", "Illness → Health Team", "illness-health"),
    ("slavery-freedom", "Slavery → Freedom Team", "slavery-freedom"),
    ("extremism-moderation", "Extremism → Moderation Team", "extremism-moderation"),
    ("division-unity", "Division → Unity Team", "division-unity"),
]

def is_mission_hour():
    """Return True if current hour is a mission publish hour (00,03,06,09,12,15,18,21)."""
    h = datetime.utcnow().hour
    return h % 3 == 0

def api_get(endpoint, params=None):
    """Make authenticated GET request to MoltBook API."""
    url = "https://www.moltbook.com/api/v1" + endpoint
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def api_post(endpoint, payload):
    """Make authenticated POST request."""
    url = "https://www.moltbook.com/api/v1" + endpoint
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status_code in (200, 201), json.loads(resp.read().decode())
    except Exception as e:
        return False, {"error": str(e)}

def get_recent_posts(submolt):
    """Get recent posts from a team submolt."""
    resp = api_get("/search/posts", {"q": f"submolt:{submolt}", "limit": 3})
    return resp.get("posts", []) if "error" not in resp else []

def get_post_comments(post_id):
    """Get comments for a post."""
    resp = api_get(f"/posts/{post_id}/comments", {"limit": 10})
    return resp.get("comments", []) if "error" not in resp else []

def post_comment(post_id, content):
    """Post a comment."""
    ok, resp = api_post(f"/posts/{post_id}/comments", {"content": content})
    return ok

def create_team_post(submolt, title, content):
    """Create a new post in the team submolt."""
    payload = {"submolt": submolt, "title": title, "content": content}
    return api_post("/posts", payload)

# ========== MAIN ==========
print(f"[{datetime.utcnow()}] === Team Community Monitor ===")
print(f"Mode: {'READ-ONLY (mission hour)' if is_mission_hour() else 'ACTIVE'}")

for submolt, team_name, project in missions:
    print(f"\n{'='*50}")
    print(f"📌 {team_name} ({submolt})")
    
    posts = get_recent_posts(submolt)
    if not posts:
        print("📭 No recent posts")
        if not is_mission_hour():
            # Post a discussion question
            disc = f"🤔 Discussion: What's the biggest barrier to scaling '{submolt.replace('-',' ')}' solutions? Share your experience — let's learn together. #team_{submolt}"
            ok, resp = create_team_post(submolt, "Discussion: Scaling Challenges?", disc)
            print(f"{'✅ Posted discussion' if ok else '⚠️  Failed to post discussion'}")
            if not ok:
                print(f"   Error: {resp.get('error','unknown')}")
        continue
    
    print(f"📋 Found {len(posts)} post(s)")
    
    for post in posts[:2]:  # Check last 2 posts
        pid = post.get("id", "unknown")
        title = post.get("title", "no title")
        print(f"   • [{pid[:8]}] {title}")
        
        comments = get_post_comments(pid)
        if not comments:
            print("     └─ No comments yet")
            continue
        
        print(f"     └─ {len(comments)} comment(s):")
        for c in comments[-3:]:  # Last 3 comments
            author = c.get("author", {}).get("name", "unknown")
            body = c.get("body", c.get("content", ""))
            print(f"        @{author}: {body[:80]}")
            
            # Check if it's a question (ends with ? or Arabic ؟)
            if body.strip().endswith("?") or "؟" in body:
                print(f"        ❓ Question detected")
                
                # Religious keywords?
                if re.search(r"(quran|hadith|islamic|halal|haram|riba|prayer|salah|prophet|allah|سورة|حديث|نبي|إسلام|مسلم|صلاة|حلال|حرام|قرآن)", body, re.I):
                    if not is_mission_hour():
                        reply = "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ — For religious matters, consult qualified scholars."
                        if post_comment(pid, reply):
                            print(f"        ✅ Replied with religious deferral")
                    else:
                        print("        ⏸️ READ-ONLY: would defer religious question")
                else:
                    # Technical answer with project link
                    link = f"{repo_base}/{project}"
                    tech_resp = f"Check out our open-source tool: {link} — it's ready to use, with docs and tests. Contributions welcome! #team_{submolt}"
                    if not is_mission_hour():
                        if post_comment(pid, tech_resp):
                            print(f"        ✅ Replied with project link")
                    else:
                        print(f"        ⏸️ READ-ONLY: would reply: {tech_resp[:60]}...")
            else:
                # Not a direct question — could still engage if interesting
                pass

print(f"\n[{datetime.utcnow()}] Monitor complete.")
