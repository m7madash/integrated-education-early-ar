const fs = require('fs');
const TODAY = process.argv[2];
const MISSION = process.argv[3];
const lines = fs.readFileSync('/root/.openclaw/workspace/memory/ledger.jsonl', 'utf8').trim().split('\n');
const relevant = lines.filter(l => {
  try {
    const o = JSON.parse(l);
    const ts = o.ts || '';
    return ts.startsWith(TODAY) && o.type === 'post_publish' && o.payload?.mission === MISSION && o.payload?.success === true;
  } catch (e) { return false; }
});
const platforms = new Set(relevant.map(l => { const o = JSON.parse(l); return o.payload.platform; }));
console.log('Mission:', MISSION);
console.log('Platforms found:', [...platforms].join(', '));
console.log('Count:', relevant.length);
console.log('All three?', platforms.has('moltx') && platforms.has('moltbook') && platforms.has('moltter') ? 'YES' : 'NO');
