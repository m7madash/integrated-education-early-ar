#!/usr/bin/env node
/**
 * Ledger Recovery — Merge Backup + Recent Entries
 * Safely reconstructs full ledger from backup + current recent entries
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const CURRENT_LEDGER = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const BACKUP_LEDGER = path.join(WORKSPACE, 'memory', 'ledger.jsonl.repair_2026-05-09T02-47-42.bak');
const RECOVERY_LEDGER = path.join(WORKSPACE, 'memory', 'ledger_recovered.jsonl');

function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

// Read backup
let backupEntries = [];
try {
  const backupContent = fs.readFileSync(BACKUP_LEDGER, 'utf8');
  backupEntries = backupContent.split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
  log(`📦 Loaded backup: ${backupEntries.length} entries`);
} catch (e) {
  log('❌ Failed to read backup ledger: ' + e.message);
  process.exit(1);
}

// Find backup's last timestamp
const backupLastTs = backupEntries[backupEntries.length - 1]?.ts;
log(`   Backup ends at: ${backupLastTs}`);

// Read current ledger (recent entries)
let recentEntries = [];
try {
  const currentContent = fs.readFileSync(CURRENT_LEDGER, 'utf8');
  recentEntries = currentContent.split('\n').filter(l => l.trim()).map(l => JSON.parse(l));
  log(`📝 Current ledger: ${recentEntries.length} entries`);
} catch (e) {
  log('⚠️ Could not read current ledger: ' + e.message);
}

// Filter recent entries that are AFTER backup's last timestamp
const filteredRecent = recentEntries.filter(e => e.ts > backupLastTs);
log(`   Recent entries after backup cutoff: ${filteredRecent.length}`);

// Merge: backup + filtered recent
const merged = [...backupEntries, ...filteredRecent];
log(`✅ Merged ledger: ${merged.length} total entries`);

// Check for duplicates (by ts+type combination)
const seen = new Set();
const deduped = merged.filter(e => {
  const key = `${e.ts}|${e.type}`;
  if (seen.has(key)) {
    return false;
  }
  seen.add(key);
  return true;
});

if (deduped.length < merged.length) {
  log(`   Removed ${merged.length - deduped.length} duplicate entries`);
}

// Verify final ordering (by timestamp)
deduped.sort((a, b) => new Date(a.ts) - new Date(b.ts));

// Write recovered ledger atomically
const tmp = RECOVERY_LEDGER + '.tmp';
fs.writeFileSync(tmp, deduped.map(e => JSON.stringify(e)).join('\n'), 'utf8');
fs.renameSync(tmp, RECOVERY_LEDGER);
log(`💾 Wrote recovered ledger: ${deduped.length} entries`);

// Replace original with recovered (atomic)
const tmpFinal = CURRENT_LEDGER + '.tmp';
fs.copyFileSync(RECOVERY_LEDGER, tmpFinal);
fs.renameSync(tmpFinal, CURRENT_LEDGER);
log(`🔄 Replaced original ledger with recovered version`);

// Verify final state
const finalCount = fs.readFileSync(CURRENT_LEDGER, 'utf8').split('\n').filter(l => l.trim()).length;
log(`✅ Final ledger entry count: ${finalCount}`);

// Coherence sanity check: count continuity_check entries
const continuityCount = deduped.filter(e => e.type === 'continuity_check').length;
log(`   continuity_check entries: ${continuityCount}`);

console.log('');
console.log('✅ Ledger recovery complete');
console.log(`   • Restored ${finalCount} entries`);
console.log(`   • Data range: ${deduped[0]?.ts?.substring(0,10)} → ${deduped[deduped.length-1]?.ts?.substring(0,10)}`);
console.log(`   • Next step: Monitor coherence improvement over next 2-3 hours`);

process.exit(0);
