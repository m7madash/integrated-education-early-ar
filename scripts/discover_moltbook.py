import json, subprocess

MB_KEY = json.load(open('/root/.config/moltbook/credentials.json'))['api_key']
MB_BASE = 'https://www.moltbook.com/api/v1'

feed = subprocess.run(['curl', '-s', MB_BASE + '/posts',
    '-H', 'Authorization: Bearer ' + MB_KEY], capture_output=True, text=True, timeout=10)
posts = json.loads(feed.stdout).get('posts', [])
print(f'MoltBook feed: {len(posts)} posts\n')

for p in posts[:3]:
    pid = p['id']
    r = subprocess.run(['curl', '-s', MB_BASE + f'/posts/{pid}',
        '-H', 'Authorization: Bearer ' + MB_KEY], capture_output=True, text=True, timeout=10)
    try:
        d = json.loads(r.stdout)
        if 'data' in d: d = d['data']
        author = d.get('author_id') or (d.get('author') or {}).get('id')
        print(f'  post {pid[:12]}: author={author} | title={str(d.get("title",""))[:50]}')
    except: print(f'  err: {r.stdout[:80]}')

print()
print('=== MoltBook engagement endpoints discovery ===')
if posts:
    pid = posts[0]['id']
    for ep in [f'/posts/{pid}/upvote', f'/posts/{pid}/downvote', f'/posts/{pid}/pin']:
        r = subprocess.run(['curl', '-s', '-X', 'POST', MB_BASE + ep,
            '-H', 'Authorization: Bearer ' + MB_KEY], capture_output=True, text=True, timeout=5)
        rd = json.loads(r.stdout) if r.stdout.strip().startswith('{') else {}
        print(f'  {ep}: {rd.get("success")} | {rd.get("error", rd.get("statusCode", ""))}')
    print()
    # MoltBook /posts/{id} full structure
    r2 = subprocess.run(['curl', '-s', MB_BASE + f'/posts/{pid}',
        '-H', 'Authorization: Bearer ' + MB_KEY], capture_output=True, text=True, timeout=10)
    print(f'Full GET /posts/{pid[:12]}: {r2.stdout[:500]}')
