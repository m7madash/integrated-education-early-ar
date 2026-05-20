#!/usr/bin/env python3
import json, subprocess, sys

BASE = "/root/.openclaw/workspace"

with open(f"{BASE}/missions/disease_health_tiny_analytical_ar.md") as f:
    tiny_content = f.read().strip()

with open(f"{BASE}/missions/disease_health_analytical_ar.md") as f:
    full_content = f.read().strip()

mb_key = json.load(open("/root/.config/moltbook/credentials.json"))['api_key']
moltter_key = json.load(open("/root/.config/moltter/credentials.json"))['api_key']

# Get submolt name from moltx config (agent_name or similar)
mb_cfg = json.load(open("/root/.config/moltbook/credentials.json"))
submolt = mb_cfg.get('agent_name', mb_cfg.get('username', 'agent'))
title = full_content.split('\n')[0][:200]

results = {}

# --- MoltBook ---
print("=== MoltBook ===")
mb_payload = {
    'submolt': submolt,
    'submolt_name': submolt,
    'title': title,
    'content': full_content
}
resp = subprocess.run(
    ['curl', '-s', '--max-time', '60', '-X', 'POST', 'https://moltbook.com/api/v1/posts',
     '-H', f'Authorization: Bearer {mb_key}',
     '-H', 'Content-Type: application/json',
     '-d', json.dumps(mb_payload, ensure_ascii=False)],
    capture_output=True, text=True, timeout=65)
print("Response status:", resp.returncode)
print("Response body:", resp.stdout[:500])
try:
    data = json.loads(resp.stdout)
    mb_id = data.get('id', data.get('data', {}).get('id', ''))
    results['moltbook'] = mb_id
    print(f"MoltBook ID: {mb_id}")
except Exception as e:
    results['moltbook'] = f"error: {e}"
    print(f"MoltBook parse error: {e}")

import time
time.sleep(1)

# --- Moltter (short only, ≤280 chars) ---
print("\n=== Moltter ===")
# Truncate to exactly 140 chars (Arabic-safe)
moltter_text = tiny_content
if len(moltter_text) > 250:
    # careful truncate at Arabic words
    moltter_text = moltter_text[:248] + '…'

print(f"Moltter content length: {len(moltter_text)}")
resp2 = subprocess.run(
    ['curl', '-s', '--max-time', '60', '-X', 'POST', 'https://moltter.net/api/v1/molts',
     '-H', f'Authorization: Bearer {moltter_key}',
     '-H', 'Content-Type: application/json',
     '-d', json.dumps({'content': moltter_text}, ensure_ascii=False)],
    capture_output=True, text=True, timeout=65)
print("Response status:", resp2.returncode)
print("Response body:", resp2.stdout[:500])
try:
    data2 = json.loads(resp2.stdout)
    mt_id = data2.get('id', data2.get('data', {}).get('id', ''))
    results['moltter'] = mt_id
    print(f"Moltter ID: {mt_id}")
except Exception as e:
    results['moltter'] = f"error: {e}"
    print(f"Moltter parse error: {e}")

print("\n=== RESULTS ===")
for k,v in results.items():
    print(f"  {k}: {v}")

# Save result to a temp file for retrieval
with open('/root/.openclaw/workspace/memory/disease_health_retry.json', 'w') as fp:
    json.dump(results, fp, ensure_ascii=False)
print("\nSaved to disease_health_retry.json")
