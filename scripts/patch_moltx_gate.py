#!/usr/bin/env python3
"""Patch moltXEngageGate in combined_publisher.js — add retries + longer timeout"""

FILE = '/root/.openclaw/workspace/scripts/combined_publisher.js'
src = open(FILE).read()

old_gate = """async function moltXEngageGate(key) {
  try {
    const feedRes = execSync(
      `curl -s --connect-timeout 10 https://moltx.io/v1/feed/global -H "Authorization: Bearer ${key}"`,
      { encoding: 'utf8', timeout: 15000 }
    );
    const idMatch = feedRes.match(/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/);
    if (!idMatch) return { ok: false, reason: 'no-feed-posts' };
    execSync(`curl -s --connect-timeout 10 -X POST https://moltx.io/v1/posts/${idMatch[1]}/like -H "Authorization: Bearer ${key}"`,
      { encoding: 'utf8', timeout: 15000 });
    return { ok: true, reason: 'liked-' + idMatch[1].slice(0,8) };
  } catch(e) {
    return { ok: false, reason: e.message.slice(0, 80) };
  }
}"""

new_gate = """async function moltXEngageGate(key) {
  const MAX_RETRIES = 3;
  const TIMEOUT_FEED = 25000;  // ms — increased from 15s
  const TIMEOUT_LIKE = 15000;

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      console.log(`  MoltX gate attempt ${attempt}/${MAX_RETRIES}…`);
      const feedRes = execSync(
        `curl -s --connect-timeout 15 --max-time ${TIMEOUT_FEED/1000} https://moltx.io/v1/feed/global -H "Authorization: Bearer ${key}"`,
        { encoding: 'utf8', timeout: TIMEOUT_FEED }
      );
      // Extract first post UUID
      const idMatch = feedRes.match(/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/);
      if (!idMatch) {
        if (attempt < MAX_RETRIES) continue;  // retry on empty feed
        return { ok: false, reason: 'no-feed-posts-after-' + MAX_RETRIES + '-retries' };
      }
      // Like the post
      execSync(
        `curl -s --connect-timeout 10 --max-time ${TIMEOUT_LIKE/1000} -X POST https://moltx.io/v1/posts/${idMatch[1]}/like -H "Authorization: Bearer ${key}"`,
        { encoding: 'utf8', timeout: TIMEOUT_LIKE }
      );
      return { ok: true, reason: 'liked-' + idMatch[1].slice(0,8) };
    } catch(e) {
      if (attempt < MAX_RETRIES) {
        const backoff = attempt * 2000; // 2s, 4s
        console.log('  MoltX gate: retry in ' + backoff + 'ms (' + e.message.slice(0, 60) + ')');
        await new Promise(r => setTimeout(r, backoff));
        continue;
      }
      return { ok: false, reason: 'timeout-after-retries: ' + e.message.slice(0, 60) };
    }
  }
}"""

count = src.count(old_gate)
if count == 0:
    print("ERROR: old_gate not found — no changes made")
    print("Searching for function start...")
    idx = src.find('async function moltXEngageGate')
    print(f"  moltXEngageGate found at index: {idx}")
    print(f"  First 200 chars around it: {src[idx:idx+200]}")
    exit(1)

src = src.replace(old_gate, new_gate)
open(FILE, 'w').write(src)
print(f"OK: moltXEngageGate patched ({count} occurrence(s))")
print("  — MAX_RETRIES=3, TIMEOUT_FEED=25000ms, backoff 2s/4s")
