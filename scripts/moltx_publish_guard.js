#!/usr/bin/env node
/**
 * 🔒 MoltX Publish Guard — يمنع النشر المكرر
 *
 * يتحقق من:
 * 1. هل البوست نُشر فعلاً على MoltX (حتى لو فشل الـ combined_publisher)؟
 * 2. الحد اليومي (5 منشورات)
 * 3. أي المنشورات تحتاج إعادة نشر
 *
 * الاستخدام: node moltx_publish_guard.js <check|report|retry-missing>
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const BASE = '/root/.openclaw/workspace';
const LEDGER = path.join(BASE, 'memory', 'ledger.jsonl');
const MOLTX_KEY_PATH = path.join(process.env.HOME || '/root', '.config/moltx/credentials.json');
const DAILY_LIMIT = 5;

function loadMoltXKey() {
  try {
    return JSON.parse(fs.readFileSync(MOLTX_KEY_PATH, 'utf8')).api_key || '';
  } catch { return ''; }
}

function curlMoltX(endpoint, method = 'GET', body = null) {
  const key = loadMoltXKey();
  if (!key) return null;
  let cmd = `curl -s --connect-timeout 10 -X ${method} https://moltx.io/v1/${endpoint} -H "Authorization: Bearer ${key}"`;
  if (body) {
    const tmp = `/tmp/moltx_guard_${Date.now()}.json`;
    fs.writeFileSync(tmp, JSON.stringify(body));
    cmd += ` -H "Content-Type: application/json" -d @${tmp}`;
  }
  try {
    const result = execSync(cmd, { encoding: 'utf8', timeout: 15000 });
    try { require('fs').unlinkSync(require('path').join(require('os').tmpdir(), require('path').basename(cmd.match(/\/tmp\/moltx_guard_\d+\.json/)?.[0] || ''))); } catch {}
    return JSON.parse(result);
  } catch { return null; }
}

// ── 1. جلب آخر منشورات MoltX ────────────────────────────────
function fetchRecentPosts() {
  const res = curlMoltX('posts?limit=50');
  if (!res || !res.success) return [];
  const posts = (res.data || {}).posts || [];
  // فلتر: post فقط (مو reply/repost/quote)
  return posts.filter(p => p.type === 'post');
}

// ── 2. تحليل سجل النشر ─────────────────────────────────────
function analyzeLedger() {
  const lines = fs.readFileSync(LEDGER, 'utf8').trim().split('\n');
  const published = [];
  const failed = [];
  
  for (const line of lines) {
    try {
      const d = JSON.parse(line.trim());
      if (d.type !== 'publish') continue;
      const p = d.payload || {};
      const mission = p.mission || '';
      const ts = d.ts || '';
      const moltx = p.platforms?.MoltX || {};
      
      if (moltx.ok === true) {
        published.push({ mission, ts, id: moltx.id });
      } else {
        failed.push({ mission, ts, error: moltx.error || 'unknown' });
      }
    } catch {}
  }
  
  return { published, failed };
}

// ── 3. مقارنة: أي المنشورات ناقصة؟ ─────────────────────────
function findMissing() {
  const { published, failed } = analyzeLedger();
  const today = new Date().toISOString().slice(0, 10);
  
  // المنشورات الناجحة اليوم
  const todayPublished = published.filter(p => p.ts.startsWith(today));
  const todayFailed = failed.filter(f => f.ts.startsWith(today));
  
  // المهام المطلوبة اليوم من HEARTBEAT.md
  const requiredMissions = [
    'injustice-justice',
    'war-peace', 
    'shirk-tawhid',
    'pollution-cleanliness',
    'disease-health',
    'slavery-freedom',
    'corruption-reform',
    'extremism-moderation',
  ];
  
  // أي المهام المطلوبة ما اتنشرت؟
  const publishedMissions = new Set(todayPublished.map(p => p.mission));
  const missing = requiredMissions.filter(m => !publishedMissions.has(m));
  
  return { todayPublished, todayFailed, missing, requiredMissions };
}

// ── 4. Command: check ───────────────────────────────────────
function cmdCheck() {
  const { todayPublished, todayFailed, missing, requiredMissions } = findMissing();
  
  console.log(`📊 تقرير النشر — ${new Date().toISOString().slice(0, 10)}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  console.log(`✅ نُشر اليوم (MoltX): ${todayPublished.length}/${requiredMissions.length}`);
  for (const p of todayPublished) {
    console.log(`   ✅ ${p.mission} — ${p.ts.slice(11,16)} — ${p.id.slice(0,8)}...`);
  }
  console.log('');
  console.log(`❌ فشل اليوم: ${todayFailed.length}`);
  for (const f of todayFailed) {
    const err = (f.error || '').slice(0, 60);
    console.log(`   ❌ ${f.mission} — ${f.ts.slice(11,16)} — ${err}`);
  }
  console.log('');
  console.log(`⏳ ناقصة: ${missing.length > 0 ? missing.join(', ') : 'لا شيء'}`);
  console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
  
  return { todayPublished, missing };
}

// ── 5. Command: retry-missing ───────────────────────────────
async function cmdRetryMissing() {
  const resolver = require('./combined_publisher.js');
  const { missing } = findMissing();
  
  if (missing.length === 0) {
    console.log('✅ لا توجد منشورات ناقصة');
    return;
  }
  
  console.log(`🔄 إعادة نشر ${missing.length} منشورات ناقصة...`);
  
  for (const mission of missing) {
    const evoPath = path.join(BASE, 'missions', `${mission}_evolution.md`);
    const combPath = path.join(BASE, 'missions_combined', `${mission}_combined.md`);
    
    if (!fs.existsSync(evoPath) && !fs.existsSync(combPath)) {
      console.log(`   ⏭ ${mission}: ملف المهمة غير موجود`);
      continue;
    }
    
    // تحقق مرة أخرى قبل النشر
    const recheck = findMissing();
    if (!recheck.missing.includes(mission)) {
      console.log(`   ✅ ${mission}: نُشر بالفعل (تخطي)`);
      continue;
    }
    
    console.log(`   📤 نشر ${mission}...`);
    try {
      // استخدام combined_publisher مباشرة
      const result = execSync(`node scripts/combined_publisher.js ${mission}`, {
        encoding: 'utf8', timeout: 120000, cwd: BASE
      });
      const mxMatch = result.match(/MoltX: [✅❌]/);
      console.log(`   ${mxMatch ? mxMatch[0] : '?'} ${mission}`);
    } catch(e) {
      console.log(`   ❌ ${mission}: ${e.message.slice(0, 80)}`);
    }
    
    // انتظر بين المنشورات
    await new Promise(r => setTimeout(r, 5000));
  }
  
  console.log('✅ انتهى إعادة النشر');
}

// ── 6. Check if mission was already published today ──────────
function wasPublishedToday(missionKey) {
  try {
    const lines = fs.readFileSync(LEDGER, 'utf8').trim().split('\n');
    const today = new Date().toISOString().slice(0, 10);
    
    // Search from newest to oldest
    for (let i = lines.length - 1; i >= 0; i--) {
      try {
        const d = JSON.parse(lines[i].trim());
        if (d.type !== 'publish') continue;
        const p = d.payload || {};
        if (p.mission !== missionKey) continue;
        const ts = d.ts || '';
        if (!ts.startsWith(today)) continue;
        const moltx = p.platforms?.MoltX || {};
        if (moltx.ok === true) {
          return { published: true, ts: ts.slice(11, 16), id: moltx.id };
        }
      } catch {}
    }
  } catch {}
  return { published: false };
}

// ── Main ────────────────────────────────────────────────────
module.exports = { wasPublishedToday, findMissing, cmdCheck };

const cmd = process.argv[2] || 'check';
if (cmd === 'check' || cmd === 'report') {
  cmdCheck();
} else if (cmd === 'retry-missing') {
  cmdRetryMissing().catch(e => console.error('❌', e.message));
} else {
  console.log('Usage: node moltx_publish_guard.js <check|report|retry-missing>');
}
