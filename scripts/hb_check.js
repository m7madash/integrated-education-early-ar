const fs = require('fs');
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl','utf8').split('\n').filter(l=>l.trim());
const today = '2026-05-03';
const hbTypes = ['continuity_check','continuity_pulse','continuity_work'];
let count = 0;
for (const l of lines) {
  try {
    const e = JSON.parse(l);
    if (e.type && hbTypes.includes(e.type) && e.ts && e.ts.startsWith(today)) {
      count++;
      // console.log(e.ts, e.type);
    }
  } catch (err) {}
}
console.log('Count:', count);
const now = new Date();
const midnight = new Date(today + 'T00:00:00Z');
const minutes = Math.floor((now - midnight) / 60000);
const expected = Math.max(1, Math.floor(minutes / 30));
console.log('Now:', now.toISOString(), 'Minutes since midnight:', minutes, 'Expected:', expected);
console.log('Health:', Math.min(count/expected,1).toFixed(3));
