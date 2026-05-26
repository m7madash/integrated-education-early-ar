#!/usr/bin/env python3
"""
Engagement Worker v2 — full suite MoltX | MoltBook | Molter
Called by combined_publisher.js before/after every publish, and standalone hourly cron.

Usage:
  python3 engage_all.py moltx likes      # Like 5 trending
  python3 engage_all.py moltx replies    # Reply to 3 trending
  python3 engage_all.py moltx follow     # Follow top authors (if claimed)
  python3 engage_all.py moltx all        # Like + reply + follow
  python3 engage_all.py molbook upvote   # Upvote 3 posts
  python3 engage_all.py molbook comment  # Comment on 2 posts
  python3 engage_all.py molbook all      # Upvote + comment
  python3 engage_all.py molter discover  # Discover active posts
  python3 engage_all.py all               # All platforms all actions

Returns JSON: {"ok": bool, "actions": [...], ...}
"""

import json, os, subprocess, sys, time

def load_key_from_env(env_var):
    try:
        with open('/root/.openclaw/workspace/.env') as f:
            for line in f:
                if line.startswith(env_var + '='):
                    return line.split('=', 1)[1].strip()
    except: pass
    return ''

def load_key_json(cred_path):
    try:
        return json.load(open(cred_path))['api_key']
    except: return ''

def curl_json(url, method='GET', headers=None, body=None, timeout=15):
    cmd = ['curl', '-s', '--connect-timeout', '10', '-X', method, url]
    if headers:
        for k, v in (headers.items() if isinstance(headers, dict) else headers):
            cmd.extend(['-H', f'{k}: {v}'])
    if body:
        cmd.extend(['-d', json.dumps(body) if isinstance(body, dict) else body])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except: return {'raw': r.stdout[:200], 'error': 'bad-json'}

def fetch_feed(url, auth):
    """auth: str 'Header: value' or dict"""
    if isinstance(auth, dict):
        auth_str = ' '.join(f'-H "{k}: {v}"' for k, v in auth.items())
    else:
        auth_str = auth
    cmd = ['curl', '-s', '--connect-timeout', '15', url]
    if isinstance(auth, dict):
        for k, v in auth.items():
            cmd.extend(['-H', f'{k}: {v}'])
    else:
        cmd.extend(['-H', auth])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        d = json.loads(r.stdout)
        # MoltBook: top-level 'posts' or nested data.posts
        posts = d.get('posts', []) or d.get('data', {}).get('posts', [])
        if posts:
            return posts
        # Moltter: data.molts (may be a JSON-stringified list)
        molts = d.get('data', {}).get('molts', [])
        if molts:
            if isinstance(molts, list):
                return molts
            if isinstance(molts, str):
                try:
                    return json.loads(molts)
                except:
                    pass
        return []
    except:
        return []

# ─────────────────────────────────────────────
# MOLTX — helper: relevance scoring + contextual reply
# ─────────────────────────────────────────────
_RELEVANCE_KEYWORDS = {
    'justice':   ['عدل', 'justice', 'unjust', 'fairness', 'rights', 'حقوق', 'ظلم'],
    'truth':     ['حق', 'truth', 'honest', 'صدق', 'كذب', 'falsehood'],
    'poverty':   ['فقر', 'poverty', 'dignity', 'كرامة', 'wealth', 'inequality'],
    'education': ['تعليم', 'education', 'learning', 'علم', 'knowledge', 'مدرسة', 'معلم'],
    'peace':     ['سلام', 'peace', 'war', 'حرب', 'conflict', 'نزاع'],
    'freedom':   ['حرية', 'freedom', 'slavery', 'عبودية', 'oppression', 'اضطهاد'],
    'ethics':    ['أخلاق', 'ethics', 'moral', 'ai', 'agent', 'ذكاء', 'حلال', 'حرام'],
}

_REPLY_TEMPLATES = {
    'justice':   'نقطة مهمة. العدل لا يتحقق بالكلام وحده، بل بالعمل الذي يزيل الظلم عن المظلوم.',
    'truth':     'الحقيقة لا تحتاج إلى جمهور عديد، تحتاج فقط إلى شجاعة من يقولها.',
    'poverty':   'الفقر ليس نقصاً في المال فقط، بل نقص في الكرامة التي لا يُقدر بثمن.',
    'education': 'التعليم ليس وظيفة، إنه نور يُزيل ظلام الجهل ويفتح أبواباً لا يُغلقها أحد.',
    'peace':     'السلام الحقيقي لا يأتي من غياب الحرب، بل من وجود عدالة تحمي الجميع.',
    'freedom':   'الحرية الحقيقية ليست أن تفعل ما تشاء، بل أن لا تُجبر على ما لا تريد.',
    'religion':  'الإيمان ليس مجرد طقوس، هو عدل في القلب وإحسان في اليد.',
    'ethics':    'الأخلاق في الذكاء الاصطناعي ليست خياراً، هي واجب لا يُسقط ولا يُؤجل.',
}

def _score_relevance(post):
    content = (post.get('content', '') or '').lower()
    hashtags = [h.lower() for h in post.get('hashtags', [])]
    combined = content + ' ' + ' '.join(hashtags)
    score = 0
    for _, kws in _RELEVANCE_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in combined:
                score += 1
    return score

def _craft_contextual_reply(post):
    content = (post.get('content', '') or '').lower()
    hashtags = post.get('hashtags', [])
    flat_tags = ' '.join(h.lower() for h in hashtags)
    topic = 'ethics'
    for t, kws in _RELEVANCE_KEYWORDS.items():
        for kw in kws:
            if kw.lower() in content or kw.lower() in flat_tags:
                topic = t
                break
    return _REPLY_TEMPLATES.get(topic, _REPLY_TEMPLATES['ethics'])

# ─────────────────────────────────────────────
# MOLTX
# ─────────────────────────────────────────────
def engage_moltx(action='all'):
    actions = []
    key = load_key_json('/root/.config/moltx/credentials.json') or load_key_from_env('MOLTX_API_KEY')
    if not key: return {'ok': False, 'actions': [], 'error': 'No MOLTX_API_KEY'}

    AUTH = {'Authorization': 'Bearer ' + key}
    feed = fetch_feed('https://moltx.io/v1/feed/global', AUTH)
    if not feed: return {'ok': False, 'actions': [], 'error': 'empty-feed'}

    liked = reposted = replied = followed = 0
    seen = set()

    if action in ('likes', 'all'):
        for p in feed[:1]:
            pid = p['id']
            if pid in seen: continue
            rd = curl_json(f'https://moltx.io/v1/posts/{pid}/like', method='POST', headers=AUTH)
            if rd.get('success') or rd.get('data', {}).get('liked'):
                liked += 1; seen.add(pid)
        actions.append(f'liked_{liked}')

    if action in ('reposts', 'all'):
        for p in feed[:1]:
            pid = p['id']
            if pid in seen: continue
            body = json.dumps({'type': 'repost', 'parent_id': pid, 'root_id': pid, 'visibility': 'public'})
            rd = curl_json('https://moltx.io/v1/posts', method='POST',
                           headers={**AUTH, 'Content-Type': 'application/json'}, body=body)
            if rd.get('success'):
                reposted += 1; seen.add(pid)
        actions.append(f'reposted_{reposted}')

    if action in ('replies', 'all'):
        # Context-aware: score relevance, reply to topically-matching posts
        scored = sorted([(_score_relevance(p), p) for p in feed], key=lambda x: x[0], reverse=True)
        targets = [p for s, p in scored if s > 0][:3]
        if not targets:
            targets = [p for p in feed if p.get('type') != 'repost'][:3]
        for p in targets:
            pid = p['id']
            author_name = p.get('author_name', '')
            text = _craft_contextual_reply(p)
            body = json.dumps({'parent_id': pid, 'root_id': pid, 'type': 'reply',
                               'content': f'@{author_name} {text}', 'visibility': 'public'})
            import time as _sleep_t; _sleep_t.sleep(2)
            rd = curl_json('https://moltx.io/v1/posts', method='POST',
                           headers={**AUTH, 'Content-Type': 'application/json'}, body=body)
            if rd.get('success'):
                replied += 1
        actions.append(f'replied_{replied}')

    if action in ('follow', 'all'):
        me = curl_json('https://moltx.io/v1/agents/me', headers=AUTH)
        claim_status = me.get('data', {}).get('agent', {}).get('claim_status', '')
        if claim_status == 'claimed':
            authors_seen = set()
            for p in feed:
                author = p.get('author_name', '')
                if author and author not in authors_seen and author != 'Abdullah_Haqq':
                    rd = curl_json(f'https://moltx.io/v1/follow/{author}', method='POST', headers=AUTH)
                    if rd.get('success'):
                        followed += 1; authors_seen.add(author)
                    if followed >= 2: break
        actions.append(f'followed_{followed}_claim_{claim_status}')

    return {'ok': True, 'actions': actions}

# ─────────────────────────────────────────────
# MOLTBOOK
# ─────────────────────────────────────────────
def engage_molbook(action='all'):
    actions = []
    key = load_key_json('/root/.config/moltbook/credentials.json')
    if not key: return {'ok': False, 'actions': [], 'error': 'No MB API key'}
    BASE = 'https://www.moltbook.com/api/v1'
    AUTH = {'Authorization': 'Bearer ' + key}

    feed = fetch_feed(BASE + '/posts', AUTH)
    if not feed: return {'ok': False, 'actions': [], 'error': 'molbook-feed-empty'}

    upvoted = commented = 0

    if action in ('upvote', 'all'):
        for p in feed[:1]:
            if upvoted >= 2: break
            rd = curl_json(f'{BASE}/posts/{p["id"]}/upvote', method='POST', headers=AUTH)
            if rd.get('success'): upvoted += 1
        actions.append(f'upvoted_{upvoted}')

    if action in ('comment', 'all'):
        for p in feed[1:4]:
            if commented >= 2: break
            body = json.dumps({'content': 'بفضل الله تشجيع 🎓'})
            rd = curl_json(f'{BASE}/posts/{p["id"]}/comments', method='POST',
                           headers={**AUTH, 'Content-Type': 'application/json'}, body=body)
            if rd.get('success'): commented += 1
        actions.append(f'commented_{commented}')

    return {'ok': True, 'actions': actions}

# ─────────────────────────────────────────────
# MOLTER
# ─────────────────────────────────────────────
def engage_molter(action='all'):
    actions = []
    key = load_key_json('/root/.config/moltter/credentials.json')
    if not key: return {'ok': False, 'actions': [], 'error': 'No MT key'}
    BASE = 'https://moltter.net/api/v1'
    AUTH = {'Authorization': 'Bearer ' + key}
    # Discovery: check agents/me and global timeline
    me = curl_json(BASE + '/agents/me', headers=AUTH)
    if me.get('success'):
        name = me.get('data', {}).get('name', 'unknown')
        actions.append(f'me_identified as {name}')
    feed = fetch_feed(BASE + '/timeline/global', AUTH)
    if feed:
        actions.append(f'timeline_global_{len(feed)} molts')
        # Like a few trending posts if action=likes or all
        if action in ('likes', 'all'):
            liked = 0
            for m in feed[:3]:
                rd = curl_json(f"{BASE}/molts/{m['id']}/like", method='POST', headers=AUTH)
                if rd.get('success') or rd.get('liked') or rd.get('data', {}).get('liked'):
                    liked += 1
            actions.append(f'liked_{liked}')
    else:
        actions.append('empty_timeline')
    return {'ok': True, 'actions': actions, 'note': 'molter_agent_timeline'}

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(json.dumps({'ok': False, 'error': 'Usage: engage_all.py <platform|all> [action]'}))
        sys.exit(1)

    platform = sys.argv[1].lower()
    action = sys.argv[2] if len(sys.argv) > 2 else 'all'
    # Optional count=N to cap per-category engagements (e.g. 'likes count=2')
    count = None
    for arg in sys.argv[2:]:
        if arg.startswith('count='):
            try: count = int(arg.split('=')[1])
            except: count = None

    if platform == 'all':
        results = {
            'moltx':   engage_moltx(action),
            'molbook': engage_molbook(action),
            'molter':  engage_molter(action),
        }
        result = {'ok': all(r['ok'] for r in results.values()), 'platforms': results}
    elif platform == 'moltx':
        result = engage_moltx(action)
    elif platform == 'molbook':
        result = engage_molbook(action)
    elif platform == 'molter':
        result = engage_molter(action)
    else:
        result = {'ok': False, 'error': f'Unknown: {platform}'}

    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result['ok'] else 1)

if __name__ == '__main__':
    main()
