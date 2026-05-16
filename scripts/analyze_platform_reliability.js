const fs = require('fs');
const ledger = '/root/.openclaw/workspace/memory/ledger.jsonl';
const lines = fs.readFileSync(ledger, 'utf8').split('\n').filter(l => l.trim());

const platformAttempts = { moltx: 0, molbook: 0, moltter: 0 };
const platformSuccesses = { moltx: 0, molbook: 0, moltter: 0 };

lines.forEach(line => {
  let e;
  try { e = JSON.parse(line); } catch (e2) { return; }

  // From post_publish entries (per-platform granular)
  if (e.type === 'post_publish' && e.payload) {
    const p = e.payload.platform;
    if (platformAttempts[p] !== undefined) {
      platformAttempts[p]++;
      if (e.payload.success) platformSuccesses[p]++;
    }
  }

  // From publish_run entries: infer per-platform if available
  if (e.type === 'publish_run' && e.payload) {
    const platformsRaw = e.payload.platforms;
    let platforms = [];
    if (Array.isArray(platformsRaw)) {
      platforms = platformsRaw;
    } else if (typeof platformsRaw === 'string') {
      platforms = platformsRaw.split(',').map(s => s.trim()).filter(Boolean);
    }
    const status = e.payload.status;
    const successCount = e.payload.successCount || 0;

    // If we have per-platform details in payload.details, use that
    if (e.payload.details) {
      Object.entries(e.payload.details).forEach(([plat, result]) => {
        if (platformAttempts[plat] !== undefined) {
          platformAttempts[plat]++;
          if (result === 'success' || result === true || result === '✅') platformSuccesses[plat]++;
        }
      });
    } else {
      // Otherwise, we can't reliably infer per-platform outcome from aggregate status
      // Only increment total attempts for each platform listed
      platforms.forEach(p => {
        if (platformAttempts[p] !== undefined) platformAttempts[p]++;
      });
      // For successes, we can only count if status is full_success (which implies all succeeded)
      if (status === 'full_success') {
        platforms.forEach(p => {
          if (platformSuccesses[p] !== undefined) platformSuccesses[p]++;
        });
      }
      // For partial_success, we don't know which ones succeeded without successCount breakdown
      // So we skip incrementing success counts for partial
    }
  }
});

console.log('=== Platform Reliability (post_publish + detailed publish_run) ===');
Object.keys(platformAttempts).forEach(p => {
  const total = platformAttempts[p];
  const success = platformSuccesses[p];
  const r = total ? (success / total).toFixed(3) : 'n/a';
  console.log(`${p}: ${success}/${total} = ${r}`);
});

// Overall platformReliability (average of three platforms)
const platforms = ['moltx', 'molbook', 'moltter'];
let sumR = 0, count = 0;
platforms.forEach(p => {
  const total = platformAttempts[p];
  if (total > 0) {
    sumR += platformSuccesses[p] / total;
    count++;
  }
});
const overall = count > 0 ? (sumR / count).toFixed(3) : 'n/a';
console.log('\nOverall platformReliability:', overall);

// Count errors (publish_run with non-success status)
let errorCount = 0;
let totalOps = 0;
lines.forEach(line => {
  let e;
  try { e = JSON.parse(line); } catch (e2) { return; }
  if (e.type === 'publish_run') {
    totalOps++;
    if (e.payload.status !== 'full_success' && e.payload.status !== 'success') errorCount++;
  }
});
console.log('\nError frequency (publish_run failures):', totalOps ? (errorCount / totalOps).toFixed(3) : 'n/a');

// Heartbeat health
const today = new Date().toISOString().slice(0,10);
const todayStart = new Date(today + 'T00:00:00Z').getTime();
const now = Date.now();
const heartbeats = lines.filter(l => {
  let e; try { e = JSON.parse(l); } catch (e2) { return false; }
  return ['continuity_check','continuity_pulse','continuity_work'].includes(e.type) &&
    new Date(e.ts).getTime() >= todayStart && new Date(e.ts).getTime() <= now;
}).length;
const minutesElapsed = Math.floor((now - todayStart) / 60000);
const expectedHB = Math.max(1, Math.floor(minutesElapsed / 30));
const hbHealth = Math.min(heartbeats / expectedHB, 1).toFixed(3);
console.log('Heartbeats today:', heartbeats, 'expected:', expectedHB, 'health:', hbHealth);

// Post completion
const missionSchedule = [
  ['injustice-justice',0,0],['division-unity',0,0],['poverty-dignity',3,0],['dhikr-morning',3,0],
  ['ignorance-knowledge',6,0],['wise-disagreement-prophetic-way',6,50],['war-peace',9,0],
  ['shirk-tawhid',9,30],['pollution-cleanliness',12,0],['disease-health',15,0],
  ['slavery-freedom',18,0],['corruption-reform',18,30],['extremism-moderation',21,0],['dhikr-evening',22,0]
];
const nowHour = new Date().getUTCHours();
const nowMin = new Date().getUTCMinutes();
const currentMinutes = nowHour*60 + nowMin;
let expectedPosts = 0;
const published = new Set();
// Check ledger for today's full_success publishes
lines.forEach(l => {
  let e; try { e=JSON.parse(l); } catch(e2){return;}
  if (e.type==='publish_run' && e.payload && e.payload.status==='full_success') {
    const ts = e.ts||'';
    if (ts.startsWith(today)) published.add(e.payload.mission);
  }
});
missionSchedule.forEach(([name,h,m]) => {
  if (currentMinutes >= h*60 + m) {
    expectedPosts++;
  }
});
const completedCount = Array.from(published).filter(m => {
  const [mName] = missionSchedule.find(s => s[0] === m) || [null];
  return mName !== undefined;
}).length;
console.log('\nPost completion:', completedCount, '/', expectedPosts, '=', expectedPosts ? (completedCount/expectedPosts).toFixed(3) : 'n/a');
