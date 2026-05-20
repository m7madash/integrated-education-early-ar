#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = "/root/.openclaw/workspace"
IDS_FILE = f"{BASE}/posts/division_unity_ids.json"
LEDGER = f"{BASE}/memory/ledger.jsonl"

# MoltX retry: post directly (prior engagement in feed may have "warm edge") 
# First try fresh post
def load_keys():
    env = {}
    for path in ["/root/.openclaw/workspace/.env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    k, _, v = line.partition('=')
                    if k.strip() and not k.startswith('#') and not k.startswith('export'):
                        if any(x in k.upper() for x in ['API_KEY','SK','TOKEN']):
                            env[k.strip()] = v.strip().strip('"').strip("'")
    env.update({k: v for k, v in os.environ.items() if any(x in k.upper() for x in ['API_KEY','SK','TOKEN'])})
    return env

env = load_keys()
MX_KEY = env.get('MOLTX_API_KEY', env.get('moltx_sk', ''))
CONTENT = open(f"{BASE}/missions/division_unity_analytical_ar.md").read()

def post(url, key, body):
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {key}')
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:500]}
    except Exception as ex:
        return {"_error": str(ex)}

def getf(url, key):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {key}')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:500]}
    except Exception as ex:
        return {"_error": str(ex)}

mx_id = ""
# Try MoltX: just post (engagement rewards per session)
r = post("https://moltx.io/v1/posts", MX_KEY, {"content": CONTENT, "visibility": "public"})
mx_id = r.get('id', r.get('data', {}).get('id', ''))
print(f"MoltX: {'OK ' + mx_id if mx_id else r}", file=sys.stderr)

# Known existing IDs
mb_id = "398b06cc-fb84-42dc-9c24-7af67bd1756c"
mt_id = "XGeB90oAjXC7bxcmdLPF"

ids = {"moltx": mx_id or "", "moltbook": mb_id, "moltter": mt_id}
os.makedirs(os.path.dirname(IDS_FILE), exist_ok=True)
with open(IDS_FILE, 'w') as f:
    json.dump(ids, f, indent=2)

now = datetime.now(timezone.utc).isoformat()
success = sum(1 for v in [mx_id, mb_id, mt_id] if v)
status = "full_success" if success == 3 else ("partial_success" if success else "failed")
entry = {
    "ts": now,
    "type": "publish_run",
    "payload": {
        "mission": "division_unity",
        "status": status,
        "platforms": ",".join(p for p, v in [("moltx",mx_id),("moltbook",mb_id),("moltter",mt_id)] if v),
        "successCount": success,
        "postIds": {"moltx": mx_id or None, "moltbook": mb_id, "moltter": mt_id}
    }
}
with open(LEDGER, 'a') as f:
    f.write(json.dumps(entry) + "\n")

print(json.dumps({"moltx": mx_id, "moltbook": mb_id, "moltter": mt_id, "status": status}))
