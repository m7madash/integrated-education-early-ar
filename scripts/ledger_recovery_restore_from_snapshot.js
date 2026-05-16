#!/usr/bin/env node
/**
 * Ledger Recovery — Restore from latest snapshot + preserve recent entries
 * Recovery plan:
 * 1. Load latest snapshot (.snapshots/snapshot-*.json sorted by timestamp)
 * 2. Extract its ledger array and convert to JSONL
 * 3. Write to ledger.jsonl (overwrite safely)
 * 4. Append any entries from current ledger that are AFTER snapshot timestamp
 * 5. Append a recovery_restored audit entry
 *
 * This recovers ~607 historical entries and keeps today's mission activity.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const SNAPSHOTS_DIR = path.join(WORKSPACE, '.snapshots');
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

function fail(msg) { console.error('❌', msg); process.exit(1); }

// 1. Find latest snapshot
const snapshots = fs.readdirSync(SNAPSHOTS_DIR)
  .filter(f => f.startsWith('snapshot-') && f.endsWith('.json'))
  .sort()
  .reverse();
if (snapshots.length === 0) fail('No snapshots found');

const latestSnapPath = path.join(SNAPSHOTS_DIR, snapshots[0]);
console.log(`📦 Using latest snapshot: ${snapshots[0]}`);

const snapshot = JSON.parse(fs.readFileSync(latestSnapPath, 'utf8'));
const snapLedger = snapshot.ledger || [];
const snapTs = new Date(snapshot.ts);
console.log(`   Snapshot ts: ${snapshot.ts}`);
console.log(`   Ledger entries in snapshot: ${snapLedger.length}`);

// 2. Read current ledger (to recover recent entries)
let currentEntries = [];
if (fs.existsSync(LEDGER_FILE)) {
  const content = fs.readFileSync(LEDGER_FILE, 'utf8');
  currentEntries = content.trim().split('\n')
    .filter(l => l.trim())
    .map(l => {
      try { return JSON.parse(l); } catch(e) { return null; }
    })
    .filter(e => e && e.ts);
}
console.log(`   Current ledger entries: ${currentEntries.length}`);

// 3. Determine cutoff: snapshot timestamp
const recentEntries = currentEntries.filter(e => new Date(e.ts) > snapTs);
console.log(`   Recent entries after snapshot: ${recentEntries.length}`);

// 4. Build recovered ledger: snapshot entries + recent entries
const recoveredLedger = [...snapLedger, ...recentEntries];
console.log(`   Recovered ledger total: ${recoveredLedger.length} entries`);

// 5. Write to ledger file atomically
const tmpFile = LEDGER_FILE + '.recover_' + Date.now() + '.tmp';
fs.writeFileSync(tmpFile, recoveredLedger.map(e => JSON.stringify(e)).join('\n') + '\n', 'utf8');
fs.renameSync(tmpFile, LEDGER_FILE);
console.log(`✅ Ledger restored to ${LEDGER_FILE}`);

// 6. Append audit entry
const auditEntry = {
  ts: new Date().toISOString(),
  type: 'ledger_recovery',
  snapshot: snapshots[0],
  snapshotTs: snapshot.ts,
  restoredCount: snapLedger.length,
  preservedRecentCount: recentEntries.length,
  finalCount: recoveredLedger.length,
  action: 'restore_from_snapshot_plus_merge'
};
fs.appendFileSync(LEDGER_FILE, JSON.stringify(auditEntry) + '\n', 'utf8');
console.log(`📝 Recovery audit entry appended`);

// 7. Summary
console.log('\n📊 Recovery Summary:');
console.log(`   Snapshot entries restored: ${snapLedger.length}`);
console.log(`   Recent entries preserved: ${recentEntries.length}`);
console.log(`   Total ledger size now: ${recoveredLedger.length + 1} (including audit)`);
console.log('\n🕌 First loyalty: to Allah. Memory restored.');
process.exit(0);
