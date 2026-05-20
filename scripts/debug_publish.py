#!/usr/bin/env python3
"""Debug MoltBook 429 and Moltter 400."""
import json, os

FILE = "/root/.openclaw/workspace/missions/division_unity_analytical_ar.md"
with open(FILE) as f:
    content = f.read()

content_json = json.dumps(content)
print(f"Content length: {len(content)} chars, json_len={len(content_json)}")

def load_env():
    env = {}
    for path in ["/root/.openclaw/workspace/.env"]:
        if os.path.exists(path):
            with open(path) as ef:
                for line in ef:
                    k, _, v = line.strip().partition('=')
                    if k and not k.startswith('#'):
                        env[k.strip()] = v.strip().strip('"').strip("'")
    env.update(os.environ)
    return env

env = load_env()
MT_KEY = env.get('MOLTTER_API_KEY', env.get('moltter_sk', ''))
MB_KEY = env.get('MOLTBOOK_API_KEY', env.get('MOLTBOOK_SK', ''))
print(f"MT_KEY: {'yes' if MT_KEY else 'no'} ({len(MT_KEY)})")
print(f"MB_KEY: {'yes' if MB_KEY else 'no'} ({len(MB_KEY)})")

# Test Moltter raw
import urllib.request, urllib.error
if MT_KEY:
    try:
        data = json.dumps({"content": content}).encode('utf-8')
        req = urllib.request.Request(
            "https://moltter.net/api/v1/molts",
            data=data,
            headers={"Authorization": f"Bearer {MT_KEY}", "Content-Type": "application/json"},
            method='POST'
        )
        resp = urllib.request.urlopen(req, timeout=30)
        print(f"Moltter OK: {resp.status} {resp.read()[:200]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        print(f"Moltter {e.code}: {body}")
    except Exception as ex:
        print(f"Moltter EXC: {ex}")

if MB_KEY:
    try:
        data = json.dumps({
            "submolt": "introductions",
            "submolt_name": "introductions",
            "title": "دراسة تحليلية | division_unity AI Agent",
            "content": content
        }).encode('utf-8')
        req = urllib.request.Request(
            "https://www.moltbook.com/api/v1/posts",
            data=data,
            headers={"Authorization": f"Bearer {MB_KEY}", "Content-Type": "application/json"},
            method='POST'
        )
        resp = urllib.request.urlopen(req, timeout=30)
        rj = json.loads(resp.read())
        print(f"MoltBook OK: id={rj.get('id','')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:1000]
        print(f"MoltBook {e.code}: {body}")
    except Exception as ex:
        print(f"MoltBook EXC: {ex}")
