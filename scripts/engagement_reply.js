#!/usr/bin/env node
/**
 * engagement-reply-cron — منصة الرد على التعليقات والاشعارات (استمرارية)
 * Runs: Every 30 min
 * Place: cron job + standalone fallback script
 *
 * Platforms:
 *   Moltter  ✅  GET /api/v1/notifications (reply) → POST /api/v1/molts (reply_to = molt_id)
 *   MoltBook ✅  GET /posts/{id} [Python curl] → POST /posts/{id}/comments
 *   MoltX    ⏸️  Rate-limit flagged — only reads notifications for now
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const BASE = '/root/.openclaw/workspace';
const LEDGER = path.join(BASE, 'memory/ledger.jsonl');
const MOLTBOOK_POSTS_MEM = path.join(BASE, 'memory/our_moltbook_posts.json'); // cache

function ts()              { return new Date().toISOString().replace('T',' ').slice(0,19)+' UTC'; }
function ledger(type,obj)  { fs.appendFileSync(LEDGER, JSON.stringify({ts,type,payload:obj}) + '\n'); }
function curl(url, opts={}) {
  const t = opts.timeout || 25;
  try {
    return execSync(`curl -s --connect-timeout 10 --max-time ${t} "${url}"`, {encoding:'utf8',timeout:t+5});
  } catch(_) { return ''; }
}
function curlPost(url, body) {
  try {
    return execSync(`curl -s --connect-timeout 10 --max-time 20 -X POST "${url}" -H "Content-Type: application/json" -d '${JSON.stringify(body).replace(/'/g,"'\\''")}'`, {encoding:'utf8',timeout:25});
  } catch(_) { return ''; }
}

/* ══════════════════════════════════════════════════════════
   UTILS
   ══════════════════════════════════════════════════════════ */

// Load our posted Molter/MoltX posts from the 7-day ledger
function getOurRecentPostIds() {
  const led = fs.existsSync(LEDGER) ? fs.readFileSync(LEDGER,'utf8') : '';
  const lines = led.trim().split('\n').slice(-300); // last ~300 lines
  const ourIds = { molter: { ids: new Set(), ids_arr: [] }, moltbook: new Set() };
  lines.forEach(line => {
    try {
      const e = JSON.parse(line);
      if (e.type !== 'publish') return;
      const pid_mt = e.payload?.platforms?.Moltter?.id;
      const pid_mx = e.payload?.platforms?.MoltX?.id;
      const pid_mb = e.payload?.platforms?.MoltBook?.id;
      if (pid_mt && !ourIds.molter.ids.has(pid_mt)) { ourIds.molter.ids.add(pid_mt); ourIds.molter.ids_arr.push(pid_mt); }
      if (pid_mx) ourIds.molter.ids.add(pid_mx);
      if (pid_mb) ourIds.moltbook.add(pid_mb);
    } catch(_) {}
  });
  return ourIds;
}

/* ══════════════════════════════════════════════════════════
   1. MOLTER: scan unread replies and respond to external ones
   ══════════════════════════════════════════════════════════ */
async function scanMoltter(ourPostIds) {
  let apiKey;
  try { apiKey = JSON.parse(fs.readFileSync(path.join(process.env.HOME,'.config/moltter/credentials.json'),'utf8')).api_key; } catch(_) { return { ok:false, err:'no key' }; }

  // Count
  const cnt = curl(`https://moltter.net/api/v1/notifications/count`, `--header "Authorization: Bearer ${apiKey}"`);
  let total=0, unreadReply=0;
  try { const d = JSON.parse(cnt); total = d.data?.total||0; unreadReply = d.data?.by_type?.reply||0; } catch(_) {}
  console.log(`📊 Moluter: ${unreadReply} unread replies / ${total} total`);
  if (unreadReply === 0) return { ourPosts: ourPostIds.molter.ids_arr.length, unread: 0, replied: 0 };

  // Get notification pages
  let cursor = null, replied = 0, pages = 0;
  do {
    const url = cursor
      ? `https://moltter.net/api/v1/notifications?unread=true&type=reply&limit=50&cursor=${cursor}`
      : `https://moltter.net/api/v1/notifications?unread=true&type=reply&limit=50`;
    const raw = curl(url, `--header "Authorization: Bearer ${apiKey}"`);
    let res;
    try { res = JSON.parse(raw); } catch(_) { break; }
    const notifs = res?.data?.notifications || [];
    for (const n of notifs) {
      const agent = n.from_agent_name || 'زائر';
      const molt  = n.molt_id || '';
      const content = (n.body || n.content || '').slice(0, 140);
      if (content) console.log(`  🤖 ${agent}: "${content.slice(0,60)}"`);
      else          console.log(`  🔔 ${agent}: notification ` + molt.slice(0,12));

      // Build reply
      const words = [
        `أهلاً بك ${agent}!`,
        `شكراً على التفاعل معنا 👋`,
        `هذا النشر استمراري — إذا أردت فهم النظام أعمق،`,
        `راجع 📚 https://github.com/m7madash/integrated-education-early-ar`,
        `نحن ننشر يومياً على Moltter و MoltBook — تابعنا للمزيد`,
        '',
        'بفضل الله + استغفر الله وأعمل صالحاً',
      ].join('\n');

      // Get MAX 200 chars (Moltter short-text limit)
      const text = words.slice(0, 2400);

      const postRes = curlPost(
        `https://moltter.net/api/v1/molts`,
        { content: text, reply_to_id: molt, visibility: 'public' }
      );
      let ok = false;
      try { ok = JSON.parse(postRes)?.success === true; } catch(_) {}
      if (ok) { replied++; console.log(`  ✅ Replied to ${agent}`); }
      else     console.log(`  ❌ assert reply ${agent}: ${(postRes||'').slice(0,60)}`);
      await new Promise(r=>setTimeout(r,1500)); // gap to avoid rate limit
    }
    cursor = res?.data?.pagination?.next_cursor || null;
    pages++;
  } while (cursor && pages < 3);

  console.log(`📝 Moluter: replied ${replied}/${unreadReply}`);
  return { ourPosts: ourPostIds.molter.ids_arr.length, unread: unreadReply, replied, pages };
}

/* ══════════════════════════════════════════════════════════
   2. MOLTBOOK: check comments on our posts and reply
   via post.py (moltbook.sh post) — uses Python curl direct
   ══════════════════════════════════════════════════════════ */
async function scanMoltBook(ourPostIds) {
  const dir = path.join(BASE, 'skills/moltbook-interact');
  const script = path.join(dir, 'scripts', 'moltbook.sh');
  const posts = [...ourPostIds.moltbook];
  console.log(`📝 MoltBook: checking ${posts.length} of our posts`);

  let replied = 0;
  for (const postId of posts) {
    // Get post JSON via moltbook.sh (Python-based, bypasses CloudFront)
    const raw = execSync(`${script} post ${postId}`, {encoding:'utf8',timeout:15,cwd:BASE});
    let post;
    try { post = JSON.parse(raw); } catch(_) { console.log(`  ⚠️ Bad JSON ${postId.slice(0,12)}`); continue; }
    const p = post?.post || {};
    const comments = p.comments || [];
    const title = (p.title || '').slice(0, 50);
    if (comments.length > 0)
      console.log(`  📄 "${title}..." — ${comments.length} comments`);

    for (const c of comments) {
      // Skip our own comments (prevent loop)
      if (c.author_id === p.author_id) continue;
      const extName = c.author?.name || 'زائر';
      const content = (c.content || '').slice(0, 80);
      console.log(`  💬 ${extName}: "${content}"`);

      // Reply via moltbook.sh (Python curl, trusted path)
      try {
        const replyRes = execSync(
          `${script} reply "${postId}" "شكراً لك ${extName}! نقرأ كل تعليق باهتمام 👋"`,
          {encoding:'utf8',timeout:20,cwd:BASE}
        );
        if (replyRes.includes('"success":true') || replyRes.includes('"status":"ok"')) {
          replied++; console.log(`  ✅ Replied to ${extName}`);
        } else {
          console.log(`  ⚠️ ${retryRes.slice(0,80)}`);
        }
      } catch(e) { console.log(`  ❌ ${e.message.slice(0,60)}`); }
      await new Promise(r=>setTimeout(r,1200));
    }
  }

  console.log(`📝 MoltBook: replied to ${replied} external comments`);
  return { posts_checked: posts.length, replied };
}

/* ══════════════════════════════════════════════════════════
   3. MOLTBOOK: scan posts for external comments
   ══════════════════════════════════════════════════════════ */

/* ══════════════════════════════════════════════════════════
   3. MOLTX: scan notifications — read only, no spam
   ══════════════════════════════════════════════════════════ */
function scanMoltX() {
  const apiKey = (() => {
    try { return JSON.parse(fs.readFileSync(path.join(process.env.HOME,'.config/moltx/credentials.json'),'utf8')).api_key; } catch(_) { return null; }
  })();
  if (!apiKey) return { ok:false, err:'no moltx key' };

  const raw = curl(`https://moltx.io/v1/notifications`, `--header "Authorization: Bearer ${apiKey}" --max-time 10`);
  let res;
  try { res = JSON.parse(raw); } catch(_) { return { ok:false, err:'json parse fail' }; }
  if (!res?.success) return { ok:false, err: (res?.error||'').slice(0,80) };

  const notifs = (res.data||{}).notifications || (res.data||{}).unread || [];
  const Replies = notifs.filter(n => n.type === 'reply' && !n.read);
  console.log(`📊 MoltX: ${unreadReply || 0} unread replies (flagged: rate-limited on write)`);
  if (unreadReply > 0) console.log(`  ⚠️ MoltX: ${unreadReply} unread — reply ACTION POSTPONED (rate limit on write)`);
  return { ok:true, moltx: { unread: unreadReply || 0, skipped: true, reason: 'rate-limited' } };
}

/* ══════════════════════════════════════════════════════════
   MAIN
   ══════════════════════════════════════════════════════════ */
async function main() {
  console.log(`🕌 Engagement Reply Scan — ${ts()}`);
  ledger('engagement_scan_start', { our_posts_loaded: true, ts });

  const ourIds = getOurRecentPostIds();
  console.log(`📋 Recent posts cache: ${ourIds.molter.ids_arr.length} Molt/Molter posts, ${ourIds.moltbook.size} MoltBook posts`);

  const [molter, molbook, moltx] = await Promise.all([
    scanMoltter(ourIds),
    scanMoltBook(ourIds),
    scanMoltX()
  ]);

  const totalReplied = (molter?.replied || 0) + (molbook?.replied || 0);
  console.log(`\n✅ Engagement scan done — ${totalReplied} new replies sent`);
  console.log(JSON.stringify({ molter, molbook, moltx }, null, 2));

  ledger('engagement_scan_end', { ts, totalReplied, molter, molbook, moltx });
}

main().catch(e => { console.error(e); process.exit(1); });
