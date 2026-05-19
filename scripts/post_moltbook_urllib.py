#!/usr/bin/env python3
# Clean MoltBook poster — no sub-process curl escaping hell
import json, urllib.request, sys, ssl

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
        'User-Agent': 'kilo-claw/1.0',
    },
    method='POST'
)

ctx = ssl.create_default_context()
try:
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        status = resp.status
        body = resp.read().decode('utf-8')
        print(json.dumps({'status': status, 'body': body[:600]}))
except urllib.error.HTTPError as e:
    print(json.dumps({'status': e.code, 'body': e.read().decode('utf-8')[:600]}))
except Exception as e:
    print(json.dumps({'status': 'error', 'body': str(e)[:600]}))
