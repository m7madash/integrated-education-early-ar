const fs = require('fs');
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl','utf8').trim().split('\n');
const start = new Date('2026-05-11T19:02:00Z').getTime();
const end = new Date('2026-05-11T19:05:00Z').getTime();
let count = 0;
lines.forEach(l => {
  try {
    const e = JSON.parse(l);
    const t = new Date(e.ts || e.timestamp).getTime();
    if (t >= start && t <= end) {
      console.log(e.ts, e.type);
      count++;
    }
  } catch (e) {}
});
if(count===0) console.log('No entries in window');
