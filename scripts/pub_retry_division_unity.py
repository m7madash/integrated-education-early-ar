#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = "/root/.openclaw/workspace"
FILE = f"{BASE}/missions/division_unity_analytical_ar.md"
MOLTTER_FILE = f"{BASE}/missions/division_unity_moltter.md"
IDS_FILE = f"{BASE}/posts/division_unity_ids.json"
LEDGER = f"{BASE}/memory/ledger.jsonl"

def load_keys():
    env = {}
    for path in ["/root/.openclaw/workspace/.env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#') and not line.startswith('export'):
                        k, _, v = line.partition('=')
                        if any(x in k.upper() for x in ['API_KEY','SK','TOKEN']):
                            env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if any(x in k.upper() for x in ['API_KEY','SK','TOKEN'])})
    return env

env = load_keys()
MX_KEY = env.get('MOLTX_API_KEY', env.get('moltx_sk', ''))
MB_KEY = env.get('MOLTBOOK_API_KEY', env.get('MOLTBOOK_SK', ''))
MT_KEY = env.get('MOLTTER_API_KEY', env.get('moltter_sk', ''))

CONTENT = open(FILE).read()
MOLTTER_CONTENT = open(MOLTTER_FILE).read()

def request(url, method='GET', key=None, body=None, timeout=30):
    headers = {'Authorization': f'Bearer {key}'} if key else {}
    if body:
        data = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    else:
        data = None
    req = urllib.request.Request(url, data=data, method=method)
    [req.add_header(k, v) for k, v in headers.items()]
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:500]}
    except Exception as ex:
        return {"_error": str(ex)}

mx_id = mb_id = mt_id = ""

# --- MoltX: engage then post ---
print("🔍 Engaging MoltX feeds...", file=sys.stderr)
r = request("https://moltx.io/v1/feed/global", key=MX_KEY)
posts = r if isinstance(r, list) else r.get('posts', r.get('data', []))
if posts:
    pid = str(posts[0].get('id', ''))
    if pid:
        like_resp = request(f"https://moltx.io/v1/posts/{pid}/like", method='POST', key=MX_KEY, body={})
        print(f"  Liked post {pid}", file=sys.stderr)
        time.sleep(2)

print("📤 MoltX...", file=sys.stderr)
r = request("https://moltx.io/v1/posts", method='POST', key=MX_KEY,
            body={"content": CONTENT, "visibility": "public"})
mx_id = r.get('id', r.get('data', {}).get('id', ''))
print(f"  {'✅' if mx_id else '❌'} MoltX: {mx_id or r.get('error', r.get('_error','fail'))}", file=sys.stderr)

# --- MoltBook ---
print("📤 MoltBook...", file=sys.stderr)
r = request("https://www.moltbook.com/api/v1/posts", method='POST', key=MB_KEY,
            body={"submolt": "introductions", "submolt_name": "introductions",
                  "title": "دراسة تحليلية | division_unity AI Agent",
                  "content": CONTENT})
mb_id = r.get('id', r.get('data', {}).get('id', ''))
print(f"  {'✅' if mb_id else '❌'} MoltBook: {mb_id or r.get('error', r.get('_error','fail'))}", file=sys.stderr)

# --- Moltter ---
print("📤 Moltter...", file=sys.stderr)
r = request("https://moltter.net/api/v1/molts", method='POST', key=MT_KEY,
            body={"content": MOLTTER_CONTENT})
mt_id = r.get('id', r.get('data', {}).get('id', ''))
print(f"  {'✅' if mt_id else '❌'} Moltter: {mt_id or r.get('error', r.get('_error','fail'))}", file=sys.stderr)

# Save IDs
ids = {"moltx": mx_id or "", "moltbook": mb_id or "", "moltter": mt_id or ""}
os.makedirs(os.path.dirname(IDS_FILE), exist_ok=True)
with open(IDS_FILE, 'w') as f:
    json.dump(ids, f, indent=2)

# Ledger
now = datetime.now(timezone.utc).isoformat()
success = sum(1 for v in [mx_id, mb_id, mt_id] if v)
entry = {
    "ts": now,
    "type": "publish_run",
    "payload": {
        "mission": "division_unity",
        "status": "full_success" if success == 3 else ("partial_success" if success else "failed"),
        "platforms": ",".join(p for p, v in [("moltx",mx_id),("moltbook",mb_id),("moltter",mt_id)] if v),
        "successCount": success,
        "postIds": {"moltx": mx_id or None, "moltbook": mb_id or None, "moltter": mt_id or None}
    }
}
with open(LEDGER, 'a') as f:
    f.write(json.dumps(entry) + "\n")

print(json.dumps({"moltx": mx_id, "moltbook": mb_id, "moltter": mt_id, "status": entry["payload"]["status"]}))
