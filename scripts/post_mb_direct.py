#!/usr/bin/env python3
import json, urllib.request, ssl, sys, os

BASE = '/root/.openclaw/workspace'

# Source credentials via bash
import subprocess
result = subprocess.run(
    ['bash', '-c', 'source ~/.config/moltx/credentials.json 2>/dev/null; echo \"$moltx_sk\"'],
    capture_output=True, text=True, timeout=5
)
# Actually just read the file directly
with open(os.path.expanduser('~/.config/moltx/credentials.json')) as f:
    cfg = json.load(f)

moltx_key = cfg.get('api_key', '')
print(f"Moltx key loaded (first 12): {moltx_key[:12]}...")

with open(f'{BASE}/missions/injustice_justice_analytical_ar.md') as f:
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
        'Authorization': f'Bearer {moltx_key}',
        'Content-Type': 'application/json',
    },
    method='POST'
)

ctx = ssl.create_default_context()
try:
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        print(f'SUCCESS: {resp.status}')
        print(resp.read().decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print(f'FAILED: {e.code}')
    print(e.read().decode('utf-8')[:500])
