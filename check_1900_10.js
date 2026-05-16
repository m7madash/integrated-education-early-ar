const fs = require('fs');
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl','utf8').trim().split('\n');
const start = new Date('2026-05-11T19:00:00Z').getTime();
const end = new Date('2026-05-11T19:10:00Z').getTime();
let found = false;
lines.forEach(l => {
  try {
    const e = JSON.parse(l);
    const t = new Date(e.ts || e.timestamp).getTime();
    if (t >= start && t <= end) {
      console.log(e.ts, e.type);
      found = true;
    }
  } catch (e) {}
});
if (!found) console.log('No entries between 19:00-19:10');
