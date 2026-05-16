const fs = require('fs');
const path = require('path');

const LEDGER = '/root/.openclaw/workspace/memory/ledger.jsonl';
const WINDOW_LINES = 50; // window size in ledger lines, not entries
const EXPECTED = 1800;

// Read last WINDOW_LINES lines
const allLines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(l => l.trim());
const windowLines = allLines.slice(-WINDOW_LINES);
console.log(`Using last ${WINDOW_LINES} ledger lines (of ${allLines.length} total)`);

// Parse entries
const entries = [];
for (const line of windowLines) {
  try {
    const obj = JSON.parse(line);
    if (obj.type === 'continuity_check' && obj.ts && obj.duplicate !== true) {
      entries.push({ ts: new Date(obj.ts).getTime() });
    }
  } catch (e) {}
}

console.log(`Found ${entries.length} continuity_check entries in window`);

if (entries.length < 2) {
  console.log('Insufficient data');
  process.exit(0);
}

// Sort
entries.sort((a,b) => a.ts - b.ts);

// Intervals
const intervals = [];
for (let i = 1; i < entries.length; i++) {
  intervals.push((entries[i].ts - entries[i-1].ts) / 1000);
}

// Stats
const sorted = [...intervals].sort((a,b)=>a-b);
const median = sorted[Math.floor(sorted.length/2)];
const absDevs = intervals.map(d => Math.abs(d - EXPECTED));
const MAD = absDevs.sort((a,b)=>a-b)[Math.floor(absDevs.length/2)];
const score = Math.max(0, Math.min(1, 1 - Math.min(1, MAD/EXPECTED)));

console.log('\nIntervals:');
intervals.forEach((d,i) => console.log(`  ${i+1}: ${d.toFixed(1)}s`));

console.log(`\nmedian=${median.toFixed(1)}s, MAD=${MAD.toFixed(1)}s, score=${score.toFixed(4)}`);

// Show which entries are in window
console.log('\nEntries:');
entries.forEach((e,i) => console.log(`  ${i+1}: ${new Date(e.ts).toISOString()}`));
