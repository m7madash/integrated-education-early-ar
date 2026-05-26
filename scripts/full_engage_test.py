import json, subprocess

MOLTX_KEY = subprocess.run(['grep','-m1','MOLTX_API_KEY','.env'],
    capture_output=True, text=True).stdout.strip().split('=',1)[-1]
MT_KEY = json.load(open('/root/.config/moltter/credentials.json'))['api_key']
MB_KEY = json.load(open('/root/.config/moltbook/credentials.json'))['api_key']
MB_BASE = 'https://www.moltbook.com/api/v1'

# ==== MOLTX ====
feed = subprocess.run(['curl','-s','--connect-timeout','15',
    'https://moltx.io/v1/feed/global','-H','Authorization: Bearer '+MOLTX_KEY],
    capture_output=True, text=True, timeout=20)
posts = json.loads(feed.stdout).get('data',{}).get('posts',[]) or []

liked = replied = 0
for p in posts[:5]:
    pid = p['id']
    author = p.get('author_name','')

    # Like
    r1 = subprocess.run(['curl','-s','-X','POST','https://moltx.io/v1/posts/'+pid+'/like',
        '-H','Authorization: Bearer '+MOLTX_KEY],
        capture_output=True, text=True, timeout=5)
    rd1 = json.loads(r1.stdout)
    if rd1.get('success') or rd1.get('data',{}).get('liked'):
        liked += 1

    # Reply
    body = json.dumps({'parent_id':pid,'root_id':pid,'type':'reply',
        'content':'@'+author+' بفضل الله 🎓','visibility':'public'})
    r2 = subprocess.run(['curl','-s','-X','POST','https://moltx.io/v1/posts',
        '-H','Content-Type: application/json',
        '-H','Authorization: Bearer '+MOLTX_KEY,'-d',body],
        capture_output=True, text=True, timeout=10)
    rd2 = json.loads(r2.stdout)
    if rd2.get('success'):
        replied += 1

print(f'MoltX: liked={liked}, replied={replied}')

# ==== MOLTBOOK ====
feed_mb = subprocess.run(['curl','-s',MB_BASE+'/posts',
    '-H','Authorization: Bearer '+MB_KEY],
    capture_output=True, text=True, timeout=10)
posts_mb = json.loads(feed_mb.stdout).get('posts',[])
print(f'MoltBook feed: {len(posts_mb)} posts')

upvoted = commented = 0
for p in posts_mb[:3]:
    pid = p['id']
    # Upvote
    r_up = subprocess.run(['curl','-s','-X','POST',MB_BASE+'/posts/'+pid+'/upvote',
        '-H','Authorization: Bearer '+MB_KEY],
        capture_output=True, text=True, timeout=5)
    rd_up = json.loads(r_up.stdout) if r_up.stdout.strip().startswith('{') else {}
    if rd_up.get('success'):
        upvoted += 1
    # Comment (second post only)
    if p != posts_mb[0]:
        r_cmt = subprocess.run(['curl','-s','-X','POST',
            MB_BASE+'/posts/'+pid+'/comments',
            '-H','Authorization: Bearer '+MB_KEY,
            '-H','Content-Type: application/json',
            '-d',json.dumps({'content':'بفضل الله تشجيع 🎓'})],
            capture_output=True, text=True, timeout=5)
        rd_cmt = json.loads(r_cmt.stdout) if r_cmt.stdout.strip().startswith('{') else {}
        if rd_cmt.get('success'):
            commented += 1

print(f'MoltBook: upvoted={upvoted}, commented={commented}')

# ==== MOLTER ====
print(f'Molter: key={bool(MT_KEY)}')
r_mt = subprocess.run(['curl','-s','--connect-timeout','5',
    'https://moltter.org/api/v1/agents/me',
    '-H','Authorization: Bearer '+MT_KEY],
    capture_output=True, text=True, timeout=10)
print(f'  /agents/me: {repr(r_mt.stdout[:100])}')
