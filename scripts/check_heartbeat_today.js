const fs = require('fs');
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl','utf8').split('\n').filter(l=>l);
const today = '2026-05-03';
const hbTypes = ['continuity_check','continuity_pulse','continuity_work'];
const todayEntries = lines.filter(l=>{
  try {
    const e = JSON.parse(l);
    return e.type && hbTypes.includes(e.type) && e.ts && e.ts.startsWith(today);
  } catch { return false; }
});
console.log('Today heartbeats:', todayEntries.length);
todayEntries.forEach(e => {
  console.log(e.ts.split('T')[1].substr(0,5), e.type);
});

// also compute expected based on now
const now = new Date();
const midnight = new Date(today + 'T00:00:00Z');
const minutesElapsed = Math.floor((now - midnight) / 60000);
const expected = Math.max(1, Math.floor(minutesElapsed / 30));
console.log('Minutes elapsed:', minutesElapsed, 'Expected heartbeats:', expected);
console.log('Heartbeat health:', Math.min(todayEntries.length / expected, 1).toFixed(3));
