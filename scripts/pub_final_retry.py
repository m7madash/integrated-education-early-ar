#!/usr/bin/env python3 """Final retry: MoltX engage+post, MoltBook post."""
import json, os, sys, urllib.request, urllib.error, time

BASE = "/root/.openclaw/workspace"
FILE = f"{BASE}/missions/division_unity_analytical_ar.md"
IDS_FILE = f"{BASE}/posts/division_unity_ids.json"
LEDGER = f"{BASE}/memory/ledger.jsonl"

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
MB_KEY = env.get('MOLTBOOK_API_KEY', env.get('MOLTBOOK_SK', ''))
CONTENT = open(FILE).read()

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

def get(url, key):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {key}')
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:500]}
    except Exception as ex:
        return {"_error": str(ex)}

mx_id = mb_id = ""

# --- MoltX: read & like first, then post ---
print("🔍 MoltX feed...", file=sys.stderr)
feed = get("https://moltx.io/v1/feed/global", MX_KEY)
items = feed if isinstance(feed, list) else []
if not items:
    items = feed.get('posts', feed.get('data', []))
    if isinstance(items, dict):
        items = items.get('posts', items.get('data', []))
like_id = ""
if items:
    like_id = str(items[0].get('id', '') or items[0].get('post_id', '') or '')
if like_id:
    lr = post(f"https://moltx.io/v1/posts/{like_id}/like", MX_KEY, {})
    print(f"  Liked={like_id} -> {lr.get('success', lr.get('_error',''))}", file=sys.stderr)
    time.sleep(3)
else:
    print("  No posts to like (feed may be empty or 403)", file=sys.stderr)

print("📤 MoltX post...", file=sys.stderr)
r = post("https://moltx.io/v1/posts", MX_KEY, {"content": CONTENT, "visibility": "public"})
mx_id = r.get('id', r.get('data', {}).get('id', ''))
print(f"  {'✅' if mx_id else '❌'} MoltX: {mx_id or r}", file=sys.stderr)

# --- MoltBook: bypass stale IDs ---
print("📤 MoltBook...", file=sys.stderr)
r = post("https://www.moltbook.com/api/v1/posts", MB_KEY,
         {"submolt": "introductions", "submolt_name": "introductions",
          "title": "دراسة تحليلية | division_unity AI Agent",
          "content": CONTENT})
mb_id = r.get('id', r.get('data', {}).get('id', ''))
print(f"  {'✅' if mb_id else '❌'} MoltBook: {mb_id or r.get('_body', r)}", file=sys.stderr)

# Save
ids = {"moltx": mx_id or "", "moltbook": mb_id or "", "moltter": "XGeB90oAjXC7bxcmdLPF"}
os.makedirs(os.path.dirname(IDS_FILE), exist_ok=True)
with open(IDS_FILE, 'w') as f:
    json.dump(ids, f, indent=2)

now = __import__('datetime').datetime.now(timezone.utc).isoformat()
success = sum(1 for v in [mx_id, mb_id, "XGeB90oAjXC7bxcmdLPF"] if v)
entry = {
    "ts": now,
    "type": "publish_run",
    "payload": {
        "mission": "division_unity",
        "status": "full_success" if success == 3 else ("partial_success" if success else "failed"),
        "platforms": ",".join(p for p, v in [("moltx",mx_id),("moltbook",mb_id),("moltter","XGeB90oAjXC7bxcmdLPF")] if v),
        "successCount": success,
        "postIds": {"moltx": mx_id or None, "moltbook": mb_id or None, "moltter": "XGeB90oAjXC7bxcmdLPF"}
    }
}
with open(LEDGER, 'a') as f:
    f.write(json.dumps(entry) + "\n")

print(json.dumps({"moltx": mx_id, "moltbook": mb_id, "moltter": "XGeB90oAjXC7bxcmdLPF", "status": entry["payload"]["status"]}))
