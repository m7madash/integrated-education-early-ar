const fs = require('fs');
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl','utf8').split('\n').filter(l=>l);
const today = new Date().toISOString().split('T')[0]; // dynamic current date
const hbTypes = ['continuity_check','continuity_pulse','continuity_work'];
const todayEntries = [];
for (const line of lines) {
  try {
    const e = JSON.parse(line);
    if (e.type && hbTypes.includes(e.type) && e.ts && e.ts.startsWith(today)) {
      todayEntries.push(e);
    }
  } catch { /* skip malformed */ }
}
console.log('Today heartbeats:', todayEntries.length);
todayEntries.forEach(e => {
  if (e.ts) {
    console.log(e.ts.split('T')[1].substr(0,5), e.type);
  }
});

// also compute expected based on now
const now = new Date();
const midnight = new Date(today + 'T00:00:00Z');
const minutesElapsed = Math.floor((now - midnight) / 60000);
const expected = Math.max(1, Math.floor(minutesElapsed / 30));
console.log('Minutes elapsed:', minutesElapsed, 'Expected heartbeats:', expected);
console.log('Heartbeat health:', Math.min(todayEntries.length / expected, 1).toFixed(3));
