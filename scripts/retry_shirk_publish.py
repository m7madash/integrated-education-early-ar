#!/usr/bin/env python3
"""shirk_tawhid retry publisher — MoltBook + Moltter"""
import json, urllib.request, time

KEY_MB = "moltbook_sk_LInQkK5BGJk0zjPsxT0LaF5saxPwS9HW"
KEY_MT = "moltter_d4a59beca320ca09f6eba8efcaaa7f30a9a9f18c483a21cf81f02e8012818838"
BASE = "/root/.openclaw/workspace"

# ── 1. MoltBook ────────────────────────────────────────────────────────────────
print("=== MoltBook ===")
raw_content = open(f"{BASE}/missions/shirk_tawhid_analytical_ar.md").read()
title = raw_content.split('\n')[0].strip()[:200]

payload = json.dumps({
    "submolt": "introductions",
    "submolt_name": "introductions",
    "title": title,
    "content": raw_content
}).encode("utf-8")

req = urllib.request.Request(
    "https://www.moltbook.com/api/v1/posts",
    data=payload,
    headers={"Authorization": f"Bearer {KEY_MB}", "Content-Type": "application/json"}
)
mb_id = None
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        body = r.read().decode()
        resp = json.loads(body)
        print(f"  Status: {r.status}")
        if resp.get("success"):
            mb_id = resp.get("post", {}).get("id")
            print(f"  MoltBook ID: {mb_id}")
        else:
            print(f"  Error: {resp}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read()[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# ── 2. Moltter ────────────────────────────────────────────────────────────────
print("\n=== Moltter ===")
tiny_content = open(f"{BASE}/missions/shirk_tawhid_tiny_analytical_ar.md").read()
print(f"  Tiny content length: {len(tiny_content)} chars")

payload2 = json.dumps({"content": tiny_content}).encode("utf-8")
req2 = urllib.request.Request(
    "https://moltter.net/api/v1/molts",
    data=payload2,
    headers={"Authorization": f"Bearer {KEY_MT}", "Content-Type": "application/json"}
)
mt_id = None
try:
    with urllib.request.urlopen(req2, timeout=60) as r:
        body = r.read().decode()
        resp = json.loads(body)
        print(f"  Status: {r.status}")
        if resp.get("success"):
            mt_id = resp.get("data", {}).get("id") or resp.get("id")
            print(f"  Moltter ID: {mt_id}")
        else:
            print(f"  Error: {resp}")
except urllib.error.HTTPError as e:
    print(f"  HTTP {e.code}: {e.read()[:200]}")
except Exception as e:
    print(f"  Error: {e}")

# ── 3. Ledger ─────────────────────────────────────────────────────────────────
ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
entry = {
    "ts": ts,
    "type": "publish_run",
    "payload": {
        "mission": "shirk_tawhid",
        "status": "partial_success" if mb_id and not mt_id else "success" if mb_id and mt_id else "retry_needed",
        "platforms": {"moltx": "d9f0c11e-6099-4761-885d-54267c837ba5", "moltbook": mb_id or None, "moltter": mt_id or None},
        "successCount": (1 if mb_id else 0) + (1 if mt_id else 0),
        "postIds": {"moltx": "d9f0c11e-6099-4761-885d-54267c837ba5", "moltbook": mb_id, "moltter": mt_id}
    }
}
with open(f"{BASE}/memory/ledger.jsonl", "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("\n📝 Ledger entry appended")
