const fs = require('fs');
const path = require('path');

const LEDGER = '/root/.openclaw/workspace/memory/ledger.jsonl';
const WINDOW = 50;

const lines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(l => l.trim());
const entries = [];
for (const line of lines) {
  try {
    const obj = JSON.parse(line);
    if (obj.type === 'continuity_check' && obj.ts && obj.duplicate !== true) {
      entries.push({ ts: new Date(obj.ts).getTime(), original: obj });
    }
  } catch (e) {
    // skip malformed
  }
}

entries.sort((a, b) => a.ts - b.ts);

console.log(`Total continuity_check entries: ${entries.length}`);
console.log(`\nLast ${WINDOW} entries:`);
const window = entries.slice(-WINDOW);
for (let i = 0; i < window.length; i++) {
  const e = window[i];
  const date = new Date(e.ts);
  console.log(`${i+1}. ${date.toISOString()} coherence=${e.original.coherence_score || 'N/A'}`);
}

// Compute intervals
console.log('\nIntervals (seconds):');
for (let i = 1; i < window.length; i++) {
  const diff = (window[i].ts - window[i-1].ts) / 1000;
  console.log(`${i}. ${diff.toFixed(1)}s`);
}

// Summary stats
const intervals = [];
for (let i = 1; i < window.length; i++) {
  intervals.push((window[i].ts - window[i-1].ts) / 1000);
}
const sorted = [...intervals].sort((a,b)=>a-b);
const median = sorted[Math.floor(sorted.length/2)];
const absDevs = intervals.map(d => Math.abs(d - 1800));
const MAD = absDevs.sort((a,b)=>a-b)[Math.floor(absDevs.length/2)];
const score = Math.max(0, Math.min(1, 1 - Math.min(1, MAD/1800)));

console.log(`\nWindow stats: count=${window.length}, median_interval=${median.toFixed(1)}s, MAD=${MAD.toFixed(1)}s, coherence_score=${score.toFixed(4)}`);
