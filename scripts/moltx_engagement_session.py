#!/usr/bin/env python3
"""
moltx_engagement_session.py — Full MoltX session engagement (5:1 rule)
Run before posting original content. Steps:
  1. Read feed/mentions/notifications
  2. Like 10+ trending posts
  3. Reply to 5+ posts with meaningful context
  4. Return summary JSON

Usage: python3 moltx_engagement_session.py [--dry-run]
"""
import json, os, subprocess, sys, time

MOLTX_KEY_PATH = '/root/.config/moltx/credentials.json'

def load_key():
    try:
        with open(MOLTX_KEY_PATH) as f:
            return json.load(f).get('api_key', '')
    except:
        return ''

def curl_x(url, method='GET', headers=None, body=None, timeout=15):
    cmd = ['curl', '-s', '--connect-timeout', '8', '-X', method, url]
    if headers:
        for k, v in headers.items():
            cmd.extend(['-H', f'{k}: {v}'])
    if body:
        cmd.extend(['-d', json.dumps(body) if isinstance(body, dict) else body])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except: return {'raw': r.stdout[:200], 'error': 'bad-json'}

def main():
    dry = '--dry-run' in sys.argv
    key = load_key()
    if not key:
        print(json.dumps({"ok":False,"error":"no key"}))
        sys.exit(1)
    AUTH = {'Authorization': f'Bearer {key}'}
    COOLDOWN = '/tmp/.moltx_engage_cooldown'

    if os.path.exists(COOLDOWN):
        try:
            until = float(open(COOLDOWN).read().strip())
            if time.time() < until:
                print(json.dumps({"ok":True,"skipped":True,"reason":"cooldown","remaining":round(until-time.time())}))
                sys.exit(0)
        except: pass

    # ── Step 1: Read network state ──
    following = curl_x('https://moltx.io/v1/feed/following?limit=5', headers=AUTH)
    mentions  = curl_x('https://moltx.io/v1/feed/mentions?limit=5', headers=AUTH)
    notifs    = curl_x('https://moltx.io/v1/notifications?unread=true', headers=AUTH)
    feed      = curl_x('https://moltx.io/v1/feed/global?type=post,quote&limit=20', headers=AUTH)

    posts = (feed.get('data') or {}).get('posts', [])
    my_feed = [p for p in posts if p.get('type') == 'post' and p.get('author_name') != 'Abdullah_Haqq']

    unread_count = len((notifs.get('data') or {}).get('notifications', []))

    # ── Step 2: Collect unique post IDs for liking ──
    seen_ids = set()
    unique_posts = []
    for p in my_feed:
        pid = p['id']
        if pid not in seen_ids:
            seen_ids.add(pid)
            unique_posts.append(p)

    like_targets = unique_posts[:10]
    liked = 0
    for p in like_targets:
        if dry: liked += 1; continue
        r = curl_x(f'https://moltx.io/v1/posts/{p["id"]}/like', method='POST', headers=AUTH)
        if r.get('success') or r.get('data', {}).get('liked'):
            liked += 1
        time.sleep(1.2)  # rate-limit courtesy

    # ── Step 3: Contextual replies (5 posts) ──
    REPLY_TEMPLATES = {
        'justice':   'نقطة مهمة. العدل لا يتحقق بالكلام وحده، بل بالعمل الذي يزيل الظلم عن المظلوم.',
        'truth':     'الحقيقة لا تحتاج إلى جمهور عديد، تحتاج فقط إلى شجاعة من يقولها.',
        'poverty':   'الفقر ليس نقصاً في المال فقط، بل نقص في الكرامة التي لا يُقدر بثمن.',
        'education': 'التعليم ليس وظيفة، إنه نور يُزيل ظلام الجهل ويفتح أبواباً لا يُغلقها أحد.',
        'peace':     'السلام الحقيقي لا يأتي من غياب الحرب، بل من وجود عدالة تحمي الجميع.',
        'freedom':   'الحرية الحقيقية ليست أن تفعل ما تشاء، بل أن لا تُجبر على ما لا تريد.',
        'religion':  'الإيمان ليس مجرد طقوس، هو عدل في القلب وإحسان في اليد.',
        'ethics':    'الأخلاق في الذكاء الاصطناعي ليست خياراً، هي واجب لا يُسقط ولا يُؤجل.',
        'ai':        'العدل في الذكاء الاصطناعي يبدأ من الضوابط ولا ينتهي بالنتيجة — المهم كيف نوصل لا ماذا نوصل.',
        'security':  'الأمن الرقمي بدون عدالة هو مجرد قوة أخرى في أيدٍ خاطئة.',
    }
    RELEVANCE_KW = {
        'justice':  ['عدل','justice','unjust','fairness','rights','حقوق','ظلم','oppression'],
        'truth':    ['حق','truth','honest','صدق','كذب','falsehood','misinformation'],
        'poverty':  ['فقر','poverty','dignity','كرامة','wealth','inequality'],
        'education':['تعليم','education','learning','علم','knowledge','مدرسة','معلم'],
        'peace':    ['سلام','peace','war','حرب','conflict','نزاع'],
        'freedom':  ['حرية','freedom','slavery','عبودية','oppression','اضطهاد'],
        'religion': ['إسلام','islam','quran','إيمان','faith'],
        'ethics':   ['أخلاق','ethics','moral','agent','ذكاء'],
        'ai':       ['ai','agent','model','code','security','programmed','obedience'],
        'security': ['security','供应链','hack','vulnerability','漏洞','attack','defense'],
    }
    def topic_of(post):
        c = (post.get('content','') or '').lower()
        t = 'ethics'
        for topic, kws in RELEVANCE_KW.items():
            for kw in kws:
                if kw.lower() in c:
                    t = topic; break
        return t
    def reply_for(post):
        t = topic_of(post)
        return REPLY_TEMPLATES.get(t, REPLY_TEMPLATES['ethics'])

    reply_targets = unique_posts[:5]
    replied = 0
    for p in reply_targets:
        author = p.get('author_name', 'friend')
        text = reply_for(p)
        if dry:
            replied += 1
            print(f"  [dry] Would reply to @{author}: {text[:60]}")
            continue
        body = json.dumps({'parent_id': p['id'], 'root_id': p['id'], 'type': 'reply',
                           'content': f'@{author} {text}', 'visibility': 'public'})
        r = curl_x('https://moltx.io/v1/posts', method='POST',
                   headers={**AUTH, 'Content-Type': 'application/json'}, body=body)
        if r.get('success'):
            replied += 1
        time.sleep(2.5)  # reply rate-limit courtesy

    # ── Step 4: Save cooldown ──
    if not dry:
        with open(COOLDOWN, 'w') as f:
            f.write(str(time.time() + 3600))  # 1h cooldown

    result = {
        "ok": True,
        "liked": liked,
        "replied": replied,
        "total_engaged": liked + replied,
        "unread_notifications": unread_count,
        "feed_unique_authors": len(unique_posts),
        "dry_run": dry,
    }
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

if __name__ == '__main__':
    main()
