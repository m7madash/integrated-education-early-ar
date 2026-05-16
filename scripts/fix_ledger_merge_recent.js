const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const backupPath = path.join(WORKSPACE, 'memory', 'ledger.jsonl.before-fix-20260514_154913.bak');
const restoredPath = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const outputPath = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

// Read current restored ledger (good state up to 05:46)
const restoredLines = fs.readFileSync(restoredPath, 'utf8').trim().split('\n').filter(l => l.startsWith('{'));
console.log(`Restored base entries: ${restoredLines.length}`);

// Read backup (pre-restore corrupted) to extract recent entries
const backupContent = fs.readFileSync(backupPath, 'utf8');
const allBackupEntries = backupContent.trim().split('\n')
  .filter(l => l.startsWith('{'))
  .map(l => {
    try { return JSON.parse(l); } catch(e) { return null; }
  })
  .filter(e => e && e.ts);

// Filter entries after 05:46:27.554Z on 2026-05-14
const cutoff = new Date('2026-05-14T05:46:27.554Z').getTime();
const recentEntries = allBackupEntries.filter(e => {
  const t = new Date(e.ts).getTime();
  return t > cutoff;
});
console.log(`Recent entries to merge: ${recentEntries.length}`);

// Combine and sort by timestamp
const combined = [...restoredLines, ...recentEntries.map(e => JSON.stringify(e))];
// Sort by ts
const parsed = combined.map(l => {
  try { return { line: l, ts: new Date(JSON.parse(l).ts).getTime() }; } catch(e) { return { line: l, ts: 0 }; }
}).sort((a,b) => a.ts - b.ts);

// Write back
const finalLines = parsed.map(p => p.line);
fs.writeFileSync(outputPath, finalLines.join('\n') + '\n', 'utf8');

// Verify
const finalCount = finalLines.length;
console.log(`✅ Ledger rebuilt: ${finalCount} total entries`);

// Stats
const now = Date.now();
const todayStart = new Date().setUTCHours(0,0,0,0);
const todayEntries = finalLines.filter(l => {
  try { return new Date(JSON.parse(l).ts) >= todayStart; } catch(e) { return false; }
}).length;
console.log(`📊 Today's entries (since UTC midnight): ${todayEntries}`);

// Show the last few entries
console.log('\nLast 5 entries:');
finalLines.slice(-5).forEach((l,i) => {
  const e = JSON.parse(l);
  console.log(`  ${e.ts} ${e.type}${e.phase?' '+e.phase:''}${e.mission?' '+e.mission:''}`);
});
