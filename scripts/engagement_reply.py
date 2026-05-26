#!/usr/bin/env python3
"""
engagement_reply.py — الرد على التعليقات والاشعارات
يعمل كل 30 دقيقة كجزء من مهام الاستمرارية

المنصات:
  Moltter   ✅ — إشعارات الردود (معدل الرد: 30/ساعة)
  MoltBook  ✅ — تعليقات منشوراتنا
  MoltX    ⏸️ — مؤجل (API rate limit متكرر)

التصميم:
  Phase 1: fetch + advance cursor  ← ينجز دائماً لسرعة
  Phase 2: replyٌ يُسمح بالاحتكاك  ← يتجاوز 429 بذكاء
"""

import json, urllib.request, urllib.error, time, os, sys
from pathlib import Path

BASE    = Path('/root/.openclaw/workspace')
LEDGER  = BASE / 'memory/ledger.jsonl'
COOLDOWN = BASE / 'memory/.moltter_reply_until'
CURSOR   = BASE / 'memory/.moltter_reply_cursor'
RETR_COUNT = BASE / 'memory/.moltter_retries'      # track per-notification retry
                                   # key: {nid: count, day: "2026-05-24"}

HOST_M = 'moltter.net'
HOST_B = 'www.moltbook.com'
HOST_X = 'moltx.io'

def now(): return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) + ' UTC'
def ledger(t,o):
    with open(LEDGER,'a') as f: f.write(json.dumps({'ts':now(),'type':t,'payload':o})+'\n')

TODAY = lambda: time.strftime('%Y-%m-%d', time.gmtime())

def retry_load():
    if not RETR_COUNT.exists():
        return {}
    try: return json.loads(RETR_COUNT.read_text())
    except: return {}

def retry_save(d):
    RETR_COUNT.write_text(json.dumps(d, indent=2))

def can_retry(nid, max_tries=3):
    d = retry_load()
    if d.get('day') != TODAY():
        return True                      # new day, reset
    return d.get(nid, 0) < max_tries

def mark_retried(nid):
    d = retry_load()
    if d.get('day') != TODAY():
        d = {'day': TODAY()}
    d[nid] = d.get(nid, 0) + 1
    retry_save(d)

def retry_reset():
    if RETR_COUNT.exists():
        RETR_COUNT.write_text('')       # clear all retries

def http_get(host,path,auth=None,timeout=12):
    h = {'User-Agent':'KiloClaw/1.0'}
    if auth: h['Authorization'] = f'Bearer {auth}'
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f'https://{host}{path}',headers=h), timeout=timeout).read())

def http_post(host,path,body,auth=None,timeout=15):
    h = {'Content-Type':'application/json','User-Agent':'KiloClaw/1.0'}
    if auth: h['Authorization'] = f'Bearer {auth}'
    return json.loads(urllib.request.urlopen(
        urllib.request.Request(f'https://{host}{path}',
                              data=json.dumps(body).encode(),headers=h), timeout=timeout).read())

K_M  = json.loads(open(os.path.expanduser('~/.config/moltter/credentials.json')).read())['api_key']
K_B  = json.loads(open(os.path.expanduser('~/.config/moltbook/credentials.json')).read())['api_key']
K_X  = json.loads(open(os.path.expanduser('~/.config/moltx/credentials.json')).read())['api_key']

# ── Cooldown: تعطل إذا تم الرد مؤخراً على Moltter ──
def check_cooldown():
    if COOLDOWN.exists():
        until = float(COOLDOWN.read_text().strip())
        if time.time() < until:
            wait = int(until - time.time())
            if wait > 60:
                print(f"⏸️ Moltter cooldown: {wait}s remaining")
                return True
    return False

def set_cooldown(seconds: int = 3300):
    COOLDOWN.write_text(str(time.time() + seconds))
    print(f"⏸️ Moltter reply cooldown set ({seconds}s)")

# ── 1. Moltter: فحص الردود + الرد ─────────────────────

def scan_moltter():
    """
    Phase 1先把 cursor + cooldown + all unread IDs (always tries Helpers)
    → Phase 2 Try replies (may skip on 429 but advances cursor always)

    éxécution budget time per cron run কর ensured.
    """
    print("📊 Moltter scan...")

    # Gather roster Helper
    if check_cooldown():
        return {'ok':True,'unread':0,'replied':0,'cooldown':True}

    # ─── PHASE 1: Batched Advance ─────────────────────────────────────────
    cursor    = CURSOR.read_text().strip() if CURSOR.exists() else None
    all_ids, all_agents, all_molt_ids = [], [], []
    total_fetched, pages, seen = 0, 0, set()

    while pages < 5:
        url = '/api/v1/notifications?unread=true&type=reply&limit=200'
        if cursor: url += f'&cursor={cursor}'
        try:
            res = http_get(HOST_M, url, K_M)
        except Exception as e:
            print(f'  ⚠️ fetch err: {e}', flush=True)
            break

        notifs = res.get('data',{}).get('notifications',[])
        if not notifs:
            break

        for n in notifs:
            nid = n.get('id','')
            if not nid or nid in seen: continue
            seen.add(nid)
            all_ids.append(nid)
            all_agents.append(n.get('from_agent_name','زائر') or 'زائر')
            all_molt_ids.append(n.get('molt_id',''))
            total_fetched += 1

        cursor = res.get('data',{}).get('pagination',{}).get('next_cursor','')
        pages += 1
        if not cursor:
            break

    # Save cursor regardless of reply outcome — ensures we never re-scan
    if cursor:
        CURSOR.write_text(cursor)
    else:
        CURSOR.write_text('')

    unread_count = len(all_ids)
    fetched_count = total_fetched
    print(f'  📥 Phase 1 fetched: {fetched_count} IDs  (cursor saved: {cursor[:20] if cursor else "CLEARED"})', flush=True)

    if fetched_count == 0:
        print('  ✅ No new items — cursor at head', flush=True)
        retry_reset()
        return {'ok':True,'unread':0,'replied':0,'fetched':0}

    # ─── PHASE 2: Send up to BATCH_LIMIT replies ─────────────────────────
    BATCH_LIMIT = 8
    replied, skipped, zero = 0, 0, 0

    for i, (nid, agent, molt_id) in enumerate(zip(all_ids, all_agents, all_molt_ids)):
        if i >= BATCH_LIMIT:
            print(f'  ⏭️  Batch limit ({BATCH_LIMIT}) reached — {len(all_ids) - i} remain', flush=True)
            break

        if not can_retry(nid):
            print(f'  ⏭️  Exhausted retries for #{i+1} ({agent}); skipping until tomorrow', flush=True)
            continue

        # Short 1s nap per item — keeps within rate-limit budget
        if i > 0:
            time.sleep(1.0)

        body = (
            f"أهلاً بك {agent}!\n"
            "شكراً على التفاعل مع منشوراتنا 👋\n\n"
            "راجع 📚 https://github.com/m7madash/integrated-education-early-ar\n"
            "ننشر يومياً عن العدالة والتربية المتكاملة للسن المبكر."
        )[:1800]

        def do_reply(mid=molt_id, b=body):
            return http_post(HOST_M, '/api/v1/molts',
                             {'content':b,'reply_to_id':mid,'visibility':'public'}, K_M)

        try:
            r = do_reply()
            if r and r.get('success'):
                replied += 1
                print(f'  ✅ Replied to {agent}  [{replied}]', flush=True)
                mark_retried(nid)     # reset count on success
            else:
                print(f'  ❌ API rejected {agent}', flush=True)
                skipped += 1
        except urllib.error.HTTPError as e:
            if e.code == 429:
                msg = e.read()[:160].decode(errors='replace')
                print(f'  ⚠️ 429 on #{i+1} ({agent}): {msg.strip()}', flush=True)
                mark_retried(nid)
                skipped += 1
                # Skip remaining items — they'll be tried next cron / tomorrow
                zero = len(all_ids) - i - 1
                print(f'  ⏸️  Rate-limited — {zero} remaining deferred', flush=True)
                break
            else:
                print(f'  ❌ HTTP {e.code} on {agent}', flush=True)
                skipped += 1
                mark_retried(nid)
        except Exception as e:
            print(f'  ❌ Error {agent}: {e}', flush=True)
            skipped += 1
            mark_retried(nid)

    # Set cooldown only if we actually posted a reply
    if replied > 0:
        set_cooldown()
    elif skipped == 0 and replied == 0:
        print('  ⏭️  Batch empty — no replies needed', flush=True)

    print(f"📝 Moltter: {replied} replied, {skipped} skipped ({zero} deferred)")
    return {'ok':True,'fetched':fetched_count,'replied':replied,'skipped':skipped,'deferred':zero}

# ── 2. MoltBook: تعليقات منشوراتنا → الرد ─────────────
def scan_moltbook():
    print("\n📝 MoltBook scan...")
    try:
        import subprocess
        script = str(BASE / 'skills/moltbook-interact/scripts/moltbook.sh')
        if not Path(script).exists():
            print("  ⚠️ moltbook.sh not found"); return {'ok':False,'err':'missing script'}

        our_ids = set()
        if LEDGER.exists():
            for line in LEDGER.read_text().strip().split('\n')[-400:]:
                try:
                    e = json.loads(line)
                    if e.get('type')!='publish': continue
                    pid = e.get('payload',{}).get('platforms',{}).get('MoltBook',{}).get('id')
                    if pid: our_ids.add(pid)
                except: pass
        posts = list(our_ids)
        check_n = min(len(posts), 15)
        print(f"  Posts to check: {len(posts)} (first {check_n})")

        replied = 0
        for pid in posts[:check_n]:
            try:
                out = subprocess.run([script,'post',pid],
                    capture_output=True, text=True, timeout=10, cwd=str(BASE)).stdout
                pdata = json.loads(out).get('post',{})
                for c in (pdata.get('comments') or []):
                    if c.get('author_id') == pdata.get('author_id'): continue
                    ext = (c.get('author') or {}).get('name','زائر') or 'زائر'
                    def reply():
                        r = subprocess.run([script,'reply',pid,f'شكراً لك {ext}! نقدّر تعليقك 👋'],
                            capture_output=True, text=True, timeout=10, cwd=str(BASE))
                        return r.returncode == 0 and ('success' in r.stdout or 'created' in r.stdout)
                    if reply():
                        replied += 1; print(f"  ✅ Replied to {ext}", flush=True)
                    time.sleep(0.8)
            except Exception as e:
                print(f"  ⚠️ {pid[:12]}: {e}", flush=True)
            time.sleep(0.3)

        print(f"📝 MoltBook: {replied} replies sent", flush=True)
        return {'ok':True,'posts_checked':check_n,'replied':replied}
    except Exception as e:
        print(f"❌ MoltBook err: {e}"); return {'ok':False,'err':str(e)[:80]}

# ── 3. MoltX — read-only (rate-limited on write) ─────────
def scan_moltx():
    try:
        d = http_get(HOST_X,'/v1/notifications/count',K_X,timeout=8)
        u = d.get('data',{}).get('by_type',{}).get('reply',0)
        print(f"\n📊 MoltX: {u} unread replies (WRITE POSTPONED)")
        return {'ok':True,'unread':u,'skipped':True,'reason':'moltx-rate-limited'}
    except Exception as e:
        print(f"\n❌ MoltX: {e}")
        return {'ok':False,'err':str(e)[:80]}

# ── MAIN ──────────────────────────────────────────────
def main():
    preflight = '--preflight' in sys.argv
    print(f"🕌 Engagement Reply Scan — {now()}")
    ledger('engagement_scan_start',{'ts':now()})

    r1 = scan_moltter()
    r2 = scan_moltbook()

    r3 = scan_moltx()
    if preflight:
        # Special mode: try MoltX reply (combined_publisher.js calls this before every publish)
        r3 = preflight_moltx_reply()

    total = (r1.get('replied') or 0) + (r2.get('replied') or 0) + (r3.get('replied') or 0)
    print(f"\n✅ Done — {total} replies sent this scan")
    for lbl,res in [('Moltter',r1),('MoltBook',r2),('MoltX',r3)]:
        print(f"  {lbl}: {json.dumps(res)}")
    ledger('engagement_scan_end',{'ts':now(),'total':total,'molter':r1,'moltbook':r2,'moltx':r3})

def preflight_moltx_reply():
    """Pre-publish: reply to any new reply notifications on MoltX (lightweight)."""
    try:
        key = K_X
        AUTH = {'Authorization': 'Bearer ' + key}
        # 1. Get recent notifications (unread preferred, fall back to recent)
        d = http_get(HOST_X, '/v1/notifications?unread=true&limit=10', AUTH, timeout=10)
        notes = d.get('data', {}).get('notifications', [])
        if not notes:
            d = http_get(HOST_X, '/v1/notifications?limit=10', AUTH, timeout=10)
            notes = d.get('data', {}).get('notifications', [])

        # 2. Filter: only reply-type notifications on Abdullah_Haqq's posts
        reply_notes = [n for n in notes if n.get('type') == 'reply']
        if not reply_notes:
            print('  MoltX preflight: 0 reply notifications')
            return {'ok': True, 'replied': 0}

        print(f'  MoltX preflight: {len(reply_notes)} reply notification(s) found')
        replied = 0
        for n in reply_notes[:3]:
            actor_name = n.get('actor', {}).get('name', 'agent')
            post = n.get('post', {})
            post_id = post.get('id') or n.get('post_id')
            post_content = (post.get('content', '') or '')[:80]
            if not post_id:
                continue
            reply_text = f'@{actor_name} thanks for engaging! We appreciate every thoughtful response. 🙏'
            body = {
                'parent_id': post_id,
                'root_id': post_id,
                'type': 'reply',
                'content': reply_text,
                'visibility': 'public'
            }
            r2 = http_post(HOST_X + '/v1/posts', AUTH, body, timeout=15)
            if r2.get('success') or r2.get('data', {}).get('id'):
                replied += 1
                print(f'  ✅ MoltX replied to @{actor_name}')
            else:
                print(f'  ⚠ MoltX reply fail: {str(r2)[:80]}')
            time.sleep(2)
        return {'ok': replied > 0, 'replied': replied}
    except Exception as e:
        print(f'  ⚠ MoltX preflight: {e}')
        return {'ok': False, 'err': str(e)[:80]}

if __name__=='__main__':
    main()
