const fs = require('fs');
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl', 'utf8')
  .split('\n')
  .filter(l => l.trim() && l.includes('continuity_check'));

const entries = [];
for (const line of lines) {
  try {
    const d = JSON.parse(line);
    if (d.ts && d.coherence_score !== undefined) {
      entries.push({ ts: new Date(d.ts), score: d.coherence_score });
    }
  } catch (e) { /* skip bad lines */ }
}

// Sort by timestamp
entries.sort((a,b) => a.ts - b.ts);

// Show only last 30 entries (last 15 hours approx)
const recent = entries.slice(-30);

console.log('=== Recent Continuity Check Gaps (last 30 runs) ===\n');
for (let i = 1; i < recent.length; i++) {
  const diffMs = recent[i].ts - recent[i-1].ts;
  const diffMin = diffMs / 60000;
  const expectedMin = 30;
  const gap = diffMs - (expectedMin * 60000);
  const status = gap > 60*60000 ? '⚠️ MISSED' : (gap > 5*60000 ? '🟡 LATE' : '✅ OK');
  console.log(`${recent[i-1].ts.toISOString()} -> ${recent[i].ts.toISOString()}`);
  console.log(`  Interval: ${diffMin.toFixed(1)}min | Gap: ${(gap/60000).toFixed(1)}min | Coherence: ${recent[i].score.toFixed(4)} | ${status}`);
  console.log();
}
