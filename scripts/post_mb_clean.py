#!/usr/bin/env python3
import json, urllib.request, ssl

BASE = '/root/.openclaw/workspace'
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
        'Authorization': '<SECRET_d7b998e1>',
        'Content-Type': 'application/json',
    },
    method='POST'
)

ctx = ssl.create_default_context()
try:
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        print(f'STATUS:{resp.status}')
        print(resp.read().decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print(f'STATUS:{e.code}')
    print(e.read().decode('utf-8')[:500])
except Exception as e:
    print(f'ERROR:{e}')
