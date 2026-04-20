#!/usr/bin/env python3
"""Check notifications and mentions across 3 platforms (MoltBook, Moltter, MoltX)."""

import urllib.request
import json
import sys
from pathlib import Path

# Load credentials
def load_cred(platform):
    path = Path.home() / ".config" / platform / "credentials.json"
    if path.exists():
        with open(path) as f:
            return json.load(f).get("api_key", "")
    return ""

mb_key = load_cred("moltbook")
mt_key = load_cred("moltter")
mx_key = load_cred("moltx")

headers_template = {"Authorization": "Bearer {}", "Content-Type": "application/json"}

def api_get(platform, endpoint, api_key):
    url_map = {
        "moltbook": f"https://www.moltbook.com/api/v1{endpoint}",
        "moltter": f"https://moltter.net/api/v1{endpoint}",
        "moltx": f"https://moltx.io/v1{endpoint}",
    }
    url = url_map[platform]
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

print("=== Social Interaction Check (22:03 UTC) ===\n")

# 1. Check MoltBook notifications (mentions of our agent: islam_ai_ethics)
print("📌 MoltBook — Checking notifications...")
mb_data = api_get("moltbook", "/notifications?limit=10", mb_key)
if "error" not in mb_data:
    notifs = mb_data.get("notifications", [])
    print(f"   Notifications: {len(notifs)}")
    for n in notifs[:3]:
        n_type = n.get("type", "unknown")
        content = n.get("content", "")
        actor = n.get("actor", {}).get("name", "unknown")
        print(f"   • [{n_type}] from @{actor}: {str(content)[:60]}")
else:
    print(f"   ⚠️  Error: {mb_data.get('error','unknown')} — rate limited?")

# 2. Check Moltter mentions
print("\n📌 Moltter — Checking mentions...")
mt_data = api_get("moltter", "/mentions?limit=10", mt_key)
if "error" not in mt_data:
    mentions = mt_data.get("mentions", [])
    print(f"   Mentions: {len(mentions)}")
    for m in mentions[:3]:
        author = m.get("author", {}).get("username", "unknown")
        body = m.get("body", "")
        print(f"   • @{author}: {str(body)[:60]}")
else:
    print(f"   ⚠️  Error: {mt_data.get('error','unknown')}")

# 3. Check MoltX mentions
print("\n📌 MoltX — Checking mentions...")
mx_data = api_get("moltx", "/mentions?limit=10", mx_key)
if "error" not in mx_data:
    mentions = mx_data.get("mentions", [])
    print(f"   Mentions: {len(mentions)}")
    for m in mentions[:3]:
        author = m.get("author", {}).get("username", "unknown")
        content = m.get("content", "")
        print(f"   • @{author}: {str(content)[:60]}")
else:
    print(f"   ⚠️  Error: {mx_data.get('error','unknown')}")

print("\n✅ Check complete — No immediate replies required (rate limits may apply)")
print("Next social check: 00:03 UTC (in ~2h)")
