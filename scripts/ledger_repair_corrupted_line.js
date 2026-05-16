#!/usr/bin/env node
/**
 * Ledger repair — fix corruption on 2026-05-11 and restore from backup
 *
 * Issues found:
 * 1. Line 2 contains two JSON objects concatenated: ...}}{"ts":...
 * 2. Ledger truncated to 8 entries, missing 600+ historical entries
 *
 * Fix:
 * 1. Split the malformed line into two separate lines
 * 2. Merge with latest backup (ledger.jsonl.repair_2026-05-10T18-47-46.bak)
 * 3. Deduplicate and sort chronologically
 * 4. Atomic replace
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const CURRENT = path.join(MEMORY_DIR, 'ledger.jsonl');
const BACKUP = path.join(MEMORY_DIR, 'ledger.jsonl.repair_2026-05-10T18-47-46.bak');
const RECOVERED = path.join(MEMORY_DIR, 'ledger_recovered.jsonl');

function log(msg) {
  const ts = new Date().toISOString();
  console.log(`[${ts}] ${msg}`);
}

// Read current ledger
log('📖 Reading current ledger...');
const currentRaw = fs.readFileSync(CURRENT, 'utf8');
const currentLines = currentRaw.split('\n').filter(l => l.trim());
log(`   Current entries: ${currentLines.length} lines`);

// Fix line 2 (index 1) if it contains concatenated JSON objects
let repairedLines = [];
for (let i = 0; i < currentLines.length; i++) {
  const line = currentLines[i];
  // Check for concatenated objects: ...}}{"ts":
  if (line.includes('}}{"ts":')) {
    log(`🔧 Splitting concatenated JSON on line ${i+1}`);
    const splitIdx = line.indexOf('}}{"ts":');
    const firstPart = line.substring(0, splitIdx + 2); // include closing }}
    const secondPart = line.substring(splitIdx + 2); // rest starting with {"ts":
    // Validate both parts
    try {
      const first = JSON.parse(firstPart);
      repairedLines.push(firstPart);
      log(`   ✅ First object: ${first.ts} ${first.type}`);
    } catch(e) {
      log(`   ❌ First part invalid: ${e.message}`);
      repairedLines.push(line); // keep original if can't parse
      continue;
    }
    try {
      const second = JSON.parse(secondPart);
      repairedLines.push(secondPart);
      log(`   ✅ Second object: ${second.ts} ${second.type}`);
    } catch(e) {
      log(`   ❌ Second part invalid: ${e.message} — keeping as raw`);
      // If second part is invalid, it might be truncated; try to recover
      // Look for next valid entry in subsequent lines
      repairedLines.push(line);
    }
  } else {
    repairedLines.push(line);
  }
}

log(`✅ After repair: ${repairedLines.length} lines`);

// Parse all lines into objects
const parseValid = (lines) => {
  const entries = [];
  for (const line of lines) {
    try {
      const obj = JSON.parse(line);
      if (obj.ts && obj.type) entries.push(obj);
    } catch(e) {
      console.log(`   ⚠️ Skipping malformed line: ${e.message}`);
    }
  }
  return entries;
};

const currentEntries = parseValid(repairedLines);
log(`✅ Valid current entries: ${currentEntries.length}`);

// Read backup ledger
log('📦 Reading backup ledger...');
const backupRaw = fs.readFileSync(BACKUP, 'utf8');
const backupLines = backupRaw.split('\n').filter(l => l.trim());
const backupEntries = parseValid(backupLines);
log(`   Backup entries: ${backupEntries.length}`);

// Get timestamp of latest backup entry
const backupLastTs = backupEntries[backupEntries.length - 1]?.ts;
log(`   Backup latest: ${backupLastTs}`);

// Filter current entries that are strictly after backup
const newEntries = currentEntries.filter(e => e.ts > backupLastTs);
log(`   New entries after backup: ${newEntries.length}`);

// Merge
const merged = [...backupEntries, ...newEntries];
log(`   Merged total (before dedup): ${merged.length}`);

// Deduplicate by ts+type+mission+platform key
const seen = new Set();
const deduped = [];
for (const e of merged) {
  const key = `${e.ts}|${e.type}|${e.mission || ''}|${e.platform || ''}`;
  if (!seen.has(key)) {
    seen.add(key);
    deduped.push(e);
  }
}
log(`   After dedup: ${deduped.length} (removed ${merged.length - deduped.length} duplicates)`);

// Sort chronologically
deduped.sort((a, b) => new Date(a.ts) - new Date(b.ts));

// Write to recovered file
const output = deduped.map(e => JSON.stringify(e)).join('\n') + '\n';
fs.writeFileSync(RECOVERED, output, 'utf8');
log(`💾 Wrote recovered ledger: ${deduped.length} entries`);

// Atomic replace current ledger
fs.copyFileSync(RECOVERED, CURRENT + '.tmp');
fs.renameSync(CURRENT + '.tmp', CURRENT);
log(`🔄 Replaced ${CURRENT}`);

// Summary
const continuityChecks = deduped.filter(e => e.type === 'continuity_check').length;
log('✅ Recovery complete:');
log(`   • Total entries: ${deduped.length}`);
log(`   • continuity_check entries: ${continuityChecks}`);
log(`   • Date range: ${deduped[0]?.ts?.substring(0,10)} → ${deduped[deduped.length-1]?.ts?.substring(0,10)}`);
log(`   • Recent entries preserved: ${newEntries.length}`);

// Exit
process.exit(0);
