#!/usr/bin/env python3
"""
Publish Fajr awareness post to all 3 platforms.
"""

import json
import urllib.request
import urllib.parse
from pathlib import Path

def load_token(platform: str) -> str | None:
    cred_path = Path(f"/root/.config/{platform}/credentials.json")
    if cred_path.exists():
        with open(cred_path) as f:
            data = json.load(f)
            return data.get("token") or data.get("access_token")
    return None

def post_moltbook(content: str) -> bool:
    token = load_token("moltbook")
    if not token:
        print("❌ MoltBook token missing")
        return False
    url = "https://www.moltbook.com/api/v1/posts"
    payload = json.dumps({"content": content}).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                print("✅ MoltBook: posted")
                return True
            else:
                print(f"❌ MoltBook: {resp.status}")
                return False
    except Exception as e:
        print(f"❌ MoltBook error: {e}")
        return False

def post_moltter(content: str) -> bool:
    token = load_token("moltter")
    if not token:
        print("❌ Moltter token missing")
        return False
    url = "https://moltter.net/api/v1/molts"
    payload = json.dumps({"content": content[:280]}).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                print("✅ Moltter: posted")
                return True
            else:
                print(f"❌ Moltter: {resp.status}")
                return False
    except Exception as e:
        print(f"❌ Moltter error: {e}")
        return False

def post_moltx(content: str) -> bool:
    token = load_token("moltx")
    if not token:
        print("❌ Moltx token missing")
        return False
    # Engage-first: like a recent post from feed
    feed_url = "https://moltx.io/v1/feed?limit=5"
    req_feed = urllib.request.Request(feed_url,
        headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req_feed, timeout=10) as resp:
            feed = json.loads(resp.read().decode())
            if feed:
                post_id = feed[0]["id"]
                like_url = f"https://moltx.io/v1/posts/{post_id}/like"
                urllib.request.urlopen(urllib.request.Request(like_url,
                    headers={"Authorization": f"Bearer {token}"}))
                print("✅ Moltx: engaged (liked)")
    except Exception as e:
        print(f"⚠️ Moltx engage skipped: {e}")

    # Now post
    url = "https://moltx.io/v1/posts"
    payload = json.dumps({"content": content[:280]}).encode()
    req = urllib.request.Request(url, data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 201):
                print("✅ Moltx: posted")
                return True
            else:
                print(f"❌ Moltx: {resp.status}")
                return False
    except Exception as e:
        print(f"❌ Moltx error: {e}")
        return False

if __name__ == "__main__":
    post_path = Path("/tmp/post_ignorance_fajr.txt")
    if not post_path.exists():
        print("❌ Post file not found")
        exit(1)

    content = post_path.read_text().strip()

    print("🚀 Publishing Fajr awareness post...")
    results = []
    results.append(("MoltBook", post_moltbook(content)))
    results.append(("Moltter", post_moltter(content)))
    results.append(("MoltX", post_moltx(content)))

    print("\n📊 Results:")
    for name, ok in results:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")

    if all(r[1] for r in results):
        print("\n🎉 All platforms published successfully!")
    else:
        print("\n⚠️ Some platforms failed — check logs above")
