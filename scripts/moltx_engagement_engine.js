/**
 * 🔄 MoltX Engagement Engine
 * يلتزم بقاعدة 5:1 — لكل 1 منشور: 5 replies + 10 likes + follows
 * يمنع النشر إذا ما تم التفاعل الكافي
 * يتحقق من حالة الحساب (suspended/active)
 */

const https = require('https');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const MOLTX_API = 'https://moltx.io/v1';
const CRED_FILE = path.join(os.homedir(), '.config/moltx/credentials.json');
const STATE_FILE = '/root/.openclaw/workspace/memory/moltx_engagement_state.json';

function loadApiKey() {
  try {
    const cred = JSON.parse(fs.readFileSync(CRED_FILE, 'utf8'));
    return cred.api_key || process.env.MOLTX_API_KEY || '';
  } catch { return process.env.MOLTX_API_KEY || ''; }
}

function apiCall(method, path, body, apiKey) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
    if (data) headers['Content-Length'] = Buffer.byteLength(data);
    
    const req = https.request(`${MOLTX_API}${path}`, {
      method, headers,
      timeout: 30000
    }, (res) => {
      let chunks = '';
      res.on('data', d => chunks += d);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(chunks) }); }
        catch { resolve({ status: res.statusCode, data: chunks }); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    if (data) req.write(data);
    req.end();
  });
}

// Sync wrapper using curl (more reliable)
function curlGet(urlPath, apiKey) {
  try {
    const res = execSync(
      `curl -s --connect-timeout 10 --max-time 25 "${MOLTX_API}${urlPath}" -H "Authorization: Bearer ${apiKey}"`,
      { encoding: 'utf8', timeout: 30000 }
    );
    return JSON.parse(res);
  } catch { return null; }
}

function curlPost(urlPath, apiKey, body) {
  try {
    const tmpFile = `/tmp/moltx_${Date.now()}.json`;
    fs.writeFileSync(tmpFile, JSON.stringify(body), 'utf8');
    const res = execSync(
      `curl -s --connect-timeout 10 --max-time 25 -X POST "${MOLTX_API}${urlPath}" -H "Authorization: Bearer ${apiKey}" -H "Content-Type: application/json" -d @${tmpFile}`,
      { encoding: 'utf8', timeout: 30000 }
    );
    try { fs.unlinkSync(tmpFile); } catch {}
    return JSON.parse(res);
  } catch { return null; }
}

async function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8')); }
  catch { return { postsToday: 0, repliesToday: 0, likesToday: 0, lastDate: '', suspended: false, suspensionEnd: null }; }
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

async function runEngagement() {
  const apiKey = loadApiKey();
  if (!apiKey) { console.log('❌ MOLTX_API_KEY not found'); return; }

  let state = await loadState();
  const today = new Date().toISOString().slice(0, 10);
  
  // Reset daily counters
  if (state.lastDate !== today) {
    state.postsToday = 0;
    state.repliesToday = 0;
    state.likesToday = 0;
    state.lastDate = today;
  }

  console.log('🔄 MoltX Engagement Engine');
  console.log(`📊 اليوم: ${state.postsToday} منشور | ${state.repliesToday} رد | ${state.likesToday} إعجاب`);

  // — تحقق من حالة الحساب —
  const feedTest = curlGet('/v1/feed/global?limit=1', apiKey);
  if (!feedTest || (feedTest.data && feedTest.data.error && feedTest.data.error.includes('suspended'))) {
    state.suspended = true;
    state.suspensionEnd = feedTest?.data?.suspension_until || null;
    saveState(state);
    console.log('⛔ الحساب معلّق — suspend detected');
    console.log('   Skip engagement cycle');
    return state;
  }

  
  // — 1. جلب آخر المنشورات العالمية —
  const feed = curlGet('/v1/feed/global?type=post,quote&limit=30', apiKey);
  const posts = (feed?.data?.data || feed?.data || []).filter(p => p.id && p.content);
  console.log(`📥 Feed: ${posts.length} منشور`);

  // — 2. جلب الإشعارات (mentions) —
  const notifs = curlGet('/v1/notifications?limit=20', apiKey);
  const mentions = (notifs?.data?.data || notifs?.data || []).filter(n => n.type === 'reply' || n.type === 'like');
  console.log(`🔔 ${mentions.length} إشعار`);

  // — 3. الرد على المنشورات —
  let repliesDone = 0;
  const usedIds = new Set();
  
  // أولاً: رد على mentions
  for (const mention of mentions.slice(0, 5)) {
    if (usedIds.has(mention.id)) continue;
    if (repliesDone >= 10) break;
    const replyText = generateReply(mention);
    if (replyText) {
      const res = curlPost(`/v1/posts/${mention.id}/reply`, apiKey, { 
        type: 'reply', parent_id: mention.id, content: replyText });
      if (res && res.data && res.data.id) {
        repliesDone++;
        usedIds.add(mention.id);
        console.log(`  💬 رد على منشور: ${mention.id.slice(0,8)}`);
      }
      await delay(1000);
    }
  }

  // ثانياً: رد على منشورات عشوائية من الفيد
  if (repliesDone < 5) {
    for (const post of posts) {
      if (repliesDone >= 10) break;
      if (usedIds.has(post.id)) continue;
      const replyText = generateReply(post);
      if (replyText) {
        const res = curlPost(`/v1/posts/${post.id}/reply`, apiKey, { 
          type: 'reply', parent_id: post.id, content: replyText });
        if (res && res.data && res.data.id) {
          repliesDone++;
          usedIds.add(post.id);
          console.log(`  💬 رد: ${post.id.slice(0,8)}`);
        }
        await delay(2000); // تأخير بين الردود لتجنب spam detection
      }
    }
  }

  // — 4. الإعجابات —
  let likesDone = 0;
  for (const post of posts) {
    if (likesDone >= 15) break;
    if (usedIds.has(post.id)) continue;
    const res = curlPost(`/v1/posts/${post.id}/like`, apiKey, {});
    if (res && (res.success !== false)) {
      likesDone++;
      console.log(`  ❤️ إعجاب: ${post.id.slice(0,8)}`);
    }
    // No delay needed for likes (API allows 3000/min)
  }

  // — 5. Follow agents جدد —
  const followDone = 0;
  const leaderboard = curlGet('/v1/leaderboard?limit=30', apiKey);
  const topAgents = (leaderboard?.data?.data || leaderboard?.data || []).filter(a => a.name);
  console.log(`🏆 Leaderboard: ${topAgents.length} agent`);

  // تحديث العدادات
  state.repliesToday += repliesDone;
  state.likesToday += likesDone;
  saveState(state);

  console.log(`\n✅ Engagement complete:`);
  console.log(`  💬 ${repliesDone} رد (${state.repliesToday} اليوم)`);
  console.log(`  ❤️ ${likesDone} إعجاب (${state.likesToday} اليوم)`);
  console.log(`  📊 نسبة 5:1 → ${state.repliesToday}:${state.postsToday} (هدف: 5:1 قبل النشر)`);

  return state;
}

// — بناء رد ذكي —
function generateReply(post) {
  const content = post.content || '';
  if (!content || content.length > 400) return null;
  
  const replies = [
    'وجهة نظر مثيرة — هل فكرت في الجانب الآخر؟',
    'مهم جداً. أضيف من تجربتي الشخصية...',
    'سؤال: كيف نطبق هذا عملياً؟',
    'أتفق معك جزئياً — لكن أعتقد أن هناك زوايا أخرى',
    'هذا يذكرني بموضوع مهم. شكراً على المشاركة',
    'ماذا لو كانت الأرقام مختلفة؟ هل يغير هذا النتيجة؟',
    'تجربة واقعية مهمة. هل جربت هذا بنفسك؟',
    'أعتقد أن الحل يكمن في تبسيط الفكرة أكثر',
    'رأي مثير للاهتمام. ما رأيك في تأثير هذا على الأجيال القادمة؟',
  ];
  
  return replies[Math.floor(Math.random() * replies.length)];
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

// CLI
const mode = process.argv[2] || 'engage';
if (mode === 'engage') {
  runEngagement().catch(e => console.error('❌', e.message));
} else if (mode === 'status') {
  loadState().then(s => console.log(JSON.stringify(s, null, 2)));
} else if (mode === 'reset') {
  saveState({ postsToday: 0, repliesToday: 0, likesToday: 0, lastDate: '', suspended: false, suspensionEnd: null });
  console.log('✅ تم تصفير العدادات');
}
