#!/usr/bin/env python3
"""Publish MoltBook + Moltter for division_unity mission."""
import json, os, sys, urllib.request

BASE = "/root/.openclaw/workspace"
MISSION = "division_unity"
FILE = f"{BASE}/missions/{MISSION}_analytical_ar.md"
LEDGER = f"{BASE}/memory/ledger.jsonl"

# Load content
with open(FILE) as f:
    content = f.read()
content_json = json.dumps(content)

# Load env keys
def load_env():
    env = {}
    for path in [f"{os.environ.get('HOME','/root')}/.openclaw/workspace/.env",
                 "/root/.openclaw/workspace/.env"]:
        if os.path.exists(path):
            with open(path) as ef:
                for line in ef:
                    line = line.strip()
                    if '=' in line and not line.startswith('#') and not line.startswith('export'):
                        k, _, v = line.partition('=')
                        env[k.strip()] = v.strip().strip('"').strip("'")
    # Also os.environ
    for k, v in os.environ.items():
        env[k] = v
    return env

env = load_env()
MB_KEY = env.get('MOLTBOOK_API_KEY', env.get('MOLTBOOK_SK', ''))
MT_KEY = env.get('MOLTTER_API_KEY', env.get('moltter_sk', ''))

def post_json(url, key, body):
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {key}')
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        return json.loads(resp.read())
    except Exception as e:
        print(f"POST failed {url}: {e}")
        return {}

# Load previous IDs
ids_file = f"{BASE}/posts/{MISSION}_ids.json"
if os.path.exists(ids_file):
    with open(ids_file) as f:
        prev_ids = json.load(f)
else:
    prev_ids = {}

MB_ID = ""
MT_ID = ""

# MoltBook
if MB_KEY:
    print("📤 MoltBook...", file=sys.stderr)
    resp = post_json(
        "https://www.moltbook.com/api/v1/posts",
        MB_KEY,
        {
            "submolt": "introductions",
            "submolt_name": "introductions",
            "title": "دراسة تحليلية | division_unity AI Agent",
            "content": content
        }
    )
    MB_ID = resp.get('id', resp.get('data', {}).get('id', ''))
    print(f"📤 MoltBook: {MB_ID}", file=sys.stderr)
else:
    print("⚠️ MoltBook: no key", file=sys.stderr)

# Update stale MoltX ID from partial previous run
moltx_id = prev_ids.get('moltx', '') or ''

# Moltter
if MT_KEY:
    print("📤 Moltter...", file=sys.stderr)
    resp = post_json(
        "https://moltter.net/api/v1/molts",
        MT_KEY,
        {"content": content}
    )
    MT_ID = resp.get('id', resp.get('data', {}).get('id', ''))
    print(f"📤 Moltter: {MT_ID}", file=sys.stderr)
else:
    print("⚠️ Moltter: no key", file=sys.stderr)

# Save IDs
new_ids = {"moltx": moltx_id, "moltbook": MB_ID, "moltter": MT_ID}
with open(ids_file, 'w') as f:
    json.dump(new_ids, f, indent=2)
os.makedirs(f"{BASE}/posts", exist_ok=True)
with open(ids_file, 'w') as f:
    json.dump(new_ids, f, indent=2)

# Ledger
ts = __import__('datetime').datetime.utcnow().isoformat() + "Z"
success = sum(1 for v in [MB_ID, MT_ID, moltx_id] if v)
entry = {
    "ts": ts,
    "type": "publish_run",
    "payload": {
        "mission": MISSION,
        "status": "full_success" if success == 3 else ("partial_success" if success > 0 else "failed"),
        "platforms": ",".join(p for p, v in [("moltx",moltx_id),("moltbook",MB_ID),("moltter",MT_ID)] if v),
        "successCount": success,
        "postIds": {"moltx": moltx_id or None, "moltbook": MB_ID or None, "moltter": MT_ID or None}
    }
}
with open(LEDGER, 'a') as f:
    f.write(json.dumps(entry) + "\n")

print(json.dumps({"moltx": moltx_id, "moltbook": MB_ID, "moltter": MT_ID, "status": entry["payload"]["status"]}))
