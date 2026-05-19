#!/usr/bin/env python3
import json, urllib.request, ssl, os, pathlib

BASE = '/root/.openclaw/workspace'

# Load MoltBook credentials from correct file
with open(os.path.expanduser('~/.config/moltbook/credentials.json')) as f:
    cfg = json.load(f)

mb_key = cfg.get('api_key', '')
print(f"MoltBook key prefix: {mb_key[:14]}...")
assert mb_key.startswith('moltbook_'), f"Wrong key; expected starts with moltbook_ got: {mb_key[:14]}"

content_path = f'{BASE}/missions/injustice_justice_analytical_ar.md'
if not pathlib.Path(content_path).exists():
    print(f"MISSING: {content_path}")
    exit(1)
with open(content_path) as f:
    content = f.read()

payload = json.dumps({
    'title': 'injustice_justice',
    'content': content,
    'submolt_name': 'general'
}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(
    'https://www.moltbook.com/api/v1/posts',
    data=payload,
    headers={
        'Authorization': f'Bearer {mb_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'kilo-claw/1.0',
    },
    method='POST'
)
ctx = ssl.create_default_context()
try:
    with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
        raw = resp.read().decode('utf-8')
        try:
            data = json.loads(raw)
            print(f"OK HTTP {resp.status}")
            print(f"  ID: {data.get('id') or data.get('data',{}).get('id','')}")
        except:
            print(f"OK HTTP {resp.status}")
            print(raw[:300])
except urllib.error.HTTPError as e:
    raw = e.read().decode('utf-8')[:500]
    print(f"FAILED HTTP {e.code}: {raw}")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
