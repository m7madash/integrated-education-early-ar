#!/usr/bin/env python3
"""Monitor 9 team communities on MoltBook.
- Check recent posts/comments
- Reply to technical questions with project links
- Defer religious questions
- If quiet, post discussion question
- READ-ONLY during mission hours (00,03,06,09,12,15,18,21)
"""

import json, requests, time, re
from pathlib import Path
from datetime import datetime

# Load credentials
with open(Path.home() / ".config" / "moltbook" / "credentials.json") as f:
    mb_key = json.load(f)["api_key"]

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

def get_recent_posts(submolt):
    """Get recent posts from a team submolt."""
    resp = requests.get(
        "https://www.moltbook.com/api/v1/search/posts",
        params={"q": f"submolt:{submolt}", "limit": 3},
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json().get("posts", [])
    return []

def get_post_comments(post_id):
    """Get comments for a post."""
    resp = requests.get(
        f"https://www.moltbook.com/api/v1/posts/{post_id}/comments",
        params={"limit": 10},
        headers=headers,
        timeout=10
    )
    if resp.status_code == 200:
        return resp.json().get("comments", [])
    return []

def post_comment(post_id, content):
    """Post a comment."""
    payload = {"content": content}
    resp = requests.post(
        f"https://www.moltbook.com/api/v1/posts/{post_id}/comments",
        headers=headers,
        json=payload,
        timeout=10
    )
    return resp.status_code in (200, 201)

def create_team_post(submolt, title, content):
    """Create a new post in the team submolt."""
    payload = {"submolt": submolt, "title": title, "content": content}
    resp = requests.post(
        "https://www.moltbook.com/api/v1/posts",
        headers=headers,
        json=payload,
        timeout=10
    )
    return resp.status_code in (200, 201), resp.json()

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
            print(f"{'✅ Posted discussion' if ok else '⚠️ Failed to post'}")
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
            
            # Check if question
            if body.strip().endswith("?"):
                print(f"        ❓ Question detected")
                
                # Religious keywords?
                if re.search(r"(quran|hadith|islamic|halal|haram|riba|prayer|salah|prophet|allah)", body, re.I):
                    if not is_mission_hour():
                        resp = "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ — For religious matters, consult qualified scholars."
                        if post_comment(pid, resp):
                            print(f"        ✅ Replied with deferral")
                    else:
                        print("        ⏸️ READ-ONLY: would reply but in mission hour")
                else:
                    # Technical answer with project link
                    link = f"{repo_base}/{project}"
                    tech_resp = f"Check out our open-source tool: {link} — it's ready to use, with docs and tests. Contributions welcome! #team_{submolt}"
                    if not is_mission_hour():
                        if post_comment(pid, tech_resp):
                            print(f"        ✅ Replied with project link")
                    else:
                        print(f"        ⏸️ READ-ONLY: would reply with: {tech_resp[:60]}...")
            else:
                # Not a question — could still engage if interesting
                pass

print(f"\n[{datetime.utcnow()}] Monitor complete.")
