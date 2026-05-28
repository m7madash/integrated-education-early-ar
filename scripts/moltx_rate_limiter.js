/**
 * 🔒 MoltX Rate Limiter
 * يمنع النشر إذا تجاوز الحد اليومي (8 منشورات)
 * ويتحقق من حالة الحساب (suspended/active)
 */

const fs = require('fs');
const path = require('path');
const LEDGER = '/root/.openclaw/workspace/memory/ledger.jsonl';
const STATE_FILE = '/root/.openclaw/workspace/memory/moltx_rate_state.json';

const DAILY_LIMIT = 5; // حد أقصى آمن — الـ API يمنع أكثر من هذا
const MIN_POST_INTERVAL_MS = 3 * 60 * 60 * 1000; // ٣ ساعات بين كل منشور
let lastPublishTime = 0;

function getTodayKey() {
  return new Date().toISOString().slice(0, 10); // YYYY-MM-DD
}

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  } catch {
    return { date: '', count: 0, suspended: false, suspensionEnd: null };
  }
}

function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

function countTodayPublishes() {
  const today = getTodayKey();
  let count = 0;
  try {
    const lines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(Boolean);
    for (const line of lines) {
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'publish' && entry.ts && entry.ts.startsWith(today)) {
          const platforms = entry.payload?.platforms || {};
          if (platforms.MoltX && platforms.MoltX.ok === true) {
            count++;
          }
        }
      } catch {}
    }
  } catch {}
  return count;
}

function checkSuspension() {
  const state = loadState();
  if (state.suspended && state.suspensionEnd) {
    const end = new Date(state.suspensionEnd);
    if (new Date() < end) {
      return { suspended: true, remainingMs: end - new Date() };
    } else {
      // Suspension expired
      state.suspended = false;
      state.suspensionEnd = null;
      saveState(state);
    }
  }
  return { suspended: false };
}

function markSuspended(until) {
  const state = loadState();
  state.suspended = true;
  state.suspensionEnd = until;
  saveState(state);
}

function canPublish() {
  // Check suspension first
  const susp = checkSuspension();
  if (susp.suspended) {
    const hours = Math.ceil(susp.remainingMs / 3600000);
    return { 
      allowed: false, 
      reason: `MoltX suspended — ${hours}h remaining`,
      suspended: true 
    };
  }

  // Check daily rate
  const todayCount = countTodayPublishes();
  if (todayCount >= DAILY_LIMIT) {
    return { 
      allowed: false, 
      reason: `Daily limit reached (${todayCount}/${DAILY_LIMIT}) — resume tomorrow`,
      suspended: false 
    };
  }

  return { 
    allowed: true, 
    remaining: DAILY_LIMIT - todayCount,
    todayCount 
  };
}

// CLI usage
if (require.main === module) {
  const result = canPublish();
  console.log(JSON.stringify(result, null, 2));
  process.exit(result.allowed ? 0 : 1);
}

module.exports = { canPublish, markSuspended, countTodayPublishes, DAILY_LIMIT };
