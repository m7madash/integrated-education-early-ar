#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const CURRENT = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const BACKUP = path.join(WORKSPACE, 'memory', 'ledger.jsonl.repair_2026-05-09T02-47-42.bak');
const RECOVERED = path.join(WORKSPACE, 'memory', 'ledger_recovered.jsonl');

function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

// Read backup, parse line-by-line, skip malformed
log('📦 Reading backup ledger...');
const backupLines = fs.readFileSync(BACKUP, 'utf8').split('\n');
const backupEntries = [];
let backupMalformed = 0;

for (let i = 0; i < backupLines.length; i++) {
  const line = backupLines[i].trim();
  if (!line) continue;
  try {
    const entry = JSON.parse(line);
    // Validate required fields
    if (entry.ts && entry.type) {
      backupEntries.push(entry);
    } else {
      backupMalformed++;
    }
  } catch (e) {
    backupMalformed++;
    if (backupMalformed <= 3) {
      log(`   ⚠️ Line ${i+1} malformed: ${e.message}`);
    }
  }
}
log(`   Parsed ${backupEntries.length} valid entries (${backupMalformed} malformed skipped)`);

const backupLastTs = backupEntries[backupEntries.length - 1]?.ts;
log(`   Backup ends at: ${backupLastTs}`);

// Read current ledger
log('📝 Reading current ledger...');
const currentLines = fs.readFileSync(CURRENT, 'utf8').split('\n');
const recentEntries = [];
let currentMalformed = 0;

for (let i = 0; i < currentLines.length; i++) {
  const line = currentLines[i].trim();
  if (!line) continue;
  try {
    const entry = JSON.parse(line);
    if (entry.ts && entry.type) {
      recentEntries.push(entry);
    } else {
      currentMalformed++;
    }
  } catch (e) {
    currentMalformed++;
  }
}
log(`   Parsed ${recentEntries.length} valid entries (${currentMalformed} malformed skipped)`);

// Filter recent entries that are strictly after backup's last timestamp
const filteredRecent = recentEntries.filter(e => e.ts > backupLastTs);
log(`   Recent entries after backup cutoff: ${filteredRecent.length}`);

// Merge and deduplicate
const merged = [...backupEntries, ...filteredRecent];
const seen = new Set();
const deduped = merged.filter(e => {
  const key = `${e.ts}|${e.type}|${(e.mission || '')}|${(e.platform || '')}`;
  if (seen.has(key)) return false;
  seen.add(key);
  return true;
});

if (deduped.length < merged.length) {
  log(`   Removed ${merged.length - deduped.length} duplicates`);
}

// Sort chronologically
deduped.sort((a, b) => new Date(a.ts) - new Date(b.ts));

// Write recovered ledger
const output = deduped.map(e => JSON.stringify(e)).join('\n') + '\n';
fs.writeFileSync(RECOVERED, output, 'utf8');
log(`💾 Wrote recovered ledger: ${deduped.length} entries`);

// Atomic replace
fs.copyFileSync(RECOVERED, CURRENT + '.tmp');
fs.renameSync(CURRENT + '.tmp', CURRENT);
log(`🔄 Replaced original ledger`);

// Final verification
const finalContent = fs.readFileSync(CURRENT, 'utf8');
const finalEntries = finalContent.split('\n').filter(l => l.trim()).length;
const continuityCount = finalContent.split('\n').filter(l => l.includes('"type":"continuity_check"')).length;

log(`✅ Recovery complete:`);
log(`   • Total entries: ${finalEntries}`);
log(`   • continuity_check: ${continuityCount}`);
log(`   • Date range: ${deduped[0]?.ts?.substring(0,10)} → ${deduped[deduped.length-1]?.ts?.substring(0,10)}`);

process.exit(0);
