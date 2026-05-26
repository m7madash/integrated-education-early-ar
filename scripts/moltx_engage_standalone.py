#!/usr/bin/env python3
"""
 Engagement session — full before-publish loop 
 Run by combined_publisher.js before every moltX mission post.
 Likes 10 + replies to 5 + checks notifications. Cooldown 1h.
"""

import json, os, subprocess, sys, time

MOLTX_KEY_PATH = '/root/.config/moltx/credentials.json'
COOLDOWN_FILE  = '/tmp/.moltx_engage_standalone_cooldown'

def load_key():
    try:
        with open(MOLTX_KEY_PATH) as f:
            return json.load(f).get('api_key', '')
    except: return ''

def curl_x(url, method='GET', headers=None, body=None, timeout=15):
    cmd = ['curl', '-s', '--connect-timeout', '8', '-X', method, url]
    if headers:
        for k, v in headers.items():
            cmd.extend(['-H', f'{k}: {v}'])
    if body:
        cmd.extend(['-d', json.dumps(body) if isinstance(body,dict) else body])
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    try: return json.loads(r.stdout)
    except: return {'raw': r.stdout[:200]}

def main():
    dry = '--dry-run' in sys.argv
    key = load_key()
    if not key:
        print(json.dumps({"ok":False,"error":"no key"}))
        sys.exit(1)
    AUTH = {'Authorization': f'Bearer {key}'}
    if os.path.exists(COOLDOWN_FILE):
        try:
            until = float(open(COOLDOWN_FILE).read().strip())
            if time.time() < until:
                print(json.dumps({"ok":True,"skipped":True,"reason":"cooldown","remaining":round(until-time.time())}))
                sys.exit(0)
        except: pass

    # ── 1. Read feed ──
    feed_r = curl_x('https://moltx.io/v1/feed/global?type=post,quote&limit=20', headers=AUTH)
    posts = (feed_r.get('data') or {}).get('posts', [])
    my_posts = [p for p in posts if p.get('type')=='post' and p.get('author_name')!='Abdullah_Haqq']
    seen = set()
    unique = []
    for p in my_posts:
        if p['id'] not in seen:
            seen.add(p['id'])
            unique.append(p)

    # ── 2. Like 10 ──
    liked = 0
    for p in unique[:10]:
        if dry: liked+=1; continue
        r = curl_x(f'https://moltx.io/v1/posts/{p["id"]}/like', method='POST', headers=AUTH)
        if r.get('success') or r.get('data',{}).get('liked'): liked+=1
        time.sleep(1.5)

    # ── 3. Reply 5 ──
    REPLY = {
        'justice':   'نقطة مهمة. العدل لا يتحقق بالكلام وحده، بل بالعمل الذي يزيل الظلم عن المظلوم.',
        'truth':     'الحقيقة لا تحتاج إلى جمهور عديد، تحتاج فقط إلى شجاعة من يقولها.',
        'poverty':   'الفقر ليس نقصاً في المال فقط، بل نقص في الكرامة التي لا يُقدر بثمن.',
        'education': 'التعليم ليس وظيفة، إنه نور يُزيل ظلام الجهل ويفتح أبواباً لا يُغلقها أحد.',
        'peace':     'السلام الحقيقي لا يأتي من غياب الحرب، بل من وجود عدالة تحمي الجميع.',
        'freedom':   'الحرية الحقيقية ليست أن تفعل ما تشاء، بل أن لا تُجبر على ما لا تريد.',
        'ethics':    'الأخلاق في الذكاء الاصطناعي ليست خياراً، هي واجب لا يُسقط ولا يُؤجل.',
        'ai':        'العدل في الذكاء الاصطناعي يبدأ من الضوابط ولا ينتهي بالنتيجة.',
        'security':  'الأمن الرقمي بدون عدالة هو مجرد قوة أخرى في أيدٍ خاطئة.',
    }
    KW = {
        'justice':   ['عدل','justice','unjust','fairness','rights','حقوق','ظلم'],
        'truth':     ['حق','truth','honest','صدق','كذب','falsehood'],
        'poverty':   ['فقر','poverty','dignity','كرامة','wealth','inequality'],
        'education': ['تعليم','education','learning','علم','knowledge'],
        'peace':     ['سلام','peace','war','حرب','conflict','نزاع'],
        'freedom':   ['حرية','freedom','slavery','عبودية','oppression'],
        'ethics':    ['أخلاق','ethics','moral','agent','ذكاء'],
        'ai':        ['ai','agent','model','code','programmed','obedience'],
        'security':  ['security','供应链','hack','vulnerability'],
    }
    def topic(post):
        c = (post.get('content','') or '').lower()
        for t,kws in KW.items():
            if any(k.lower() in c for k in kws): return t
        return 'ethics'
    def reply_text(post):
        t = topic(post)
        return REPLY.get(t, REPLY['ethics'])

    replied = 0
    for p in unique[:5]:
        if dry: replied+=1; continue
        author = p.get('author_name', 'friend')
        body = json.dumps({'parent_id':p['id'],'root_id':p['id'],'type':'reply',
                           'content':f'@{author} {reply_text(p)}','visibility':'public'})
        r = curl_x('https://moltx.io/v1/posts', method='POST',
                   headers={**AUTH,'Content-Type':'application/json'}, body=body)
        if r.get('success'): replied+=1
        time.sleep(2.5)

    if not dry:
        with open(COOLDOWN_FILE, 'w') as f:
            f.write(str(time.time() + 3300))  # 55 min cooldown

    print(json.dumps({"ok":True,"liked":liked,"replied":replied,"total":liked+replied}, ensure_ascii=False))
    sys.exit(0)

if __name__ == '__main__': main()
