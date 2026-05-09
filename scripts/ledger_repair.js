#!/usr/bin/env node
/**
 * ledger_repair.js — Fixes malformed entries in ledger.jsonl
 *
 * Detected issues:
 * - Line 213: plain text (not JSON) — remove
 * - Lines 288-290: trailing commas after JSON object — strip commas
 * - Line 377: trailing comma — strip
 * - Line 411: missing closing brace (truncated) — remove
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const BACKUP_SUFFIX = '.repair_' + new Date().toISOString().slice(0,19).replace(/:/g,'-') + '.bak';

function isJSON(str) {
  try { JSON.parse(str); return true; } catch(e) { return false; }
}

function repairLedger() {
  if (!fs.existsSync(LEDGER_FILE)) {
    console.error('❌ Ledger file not found:', LEDGER_FILE);
    process.exit(1);
  }

  const content = fs.readFileSync(LEDGER_FILE, 'utf8');
  const lines = content.split('\n').filter(l => l.trim().length > 0);
  const totalOriginal = lines.length;

  let fixedLines = [];
  let removed = 0;
  let autoFixed = 0;

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;

    // Try direct parse
    if (isJSON(line)) {
      fixedLines.push(line);
      return;
    }

    // Heuristic: trailing comma after closing brace: }}}
    // Pattern: ...}},$ or ...}} trailing non-whitespace
    const trimmed = line.trim();
    if (trimmed.endsWith('}}},') || trimmed.endsWith('}},') || (trimmed.endsWith(',') && (trimmed.match(/}/g)||[]).length >= 2)) {
      // Strip trailing comma
      const fixed = trimmed.replace(/,+\s*$/, '');
      if (isJSON(fixed)) {
        console.log(`🔧 Line ${lineNum}: stripped trailing comma`);
        fixedLines.push(fixed);
        autoFixed++;
        return;
      }
    }

    // Give up — drop the line
    console.log(`🗑️  Line ${lineNum}: malformed — removing (${line.substring(0,60)}...)`);
    removed++;
  });

  // Write repaired ledger
  const backupPath = LEDGER_FILE + BACKUP_SUFFIX;
  fs.copyFileSync(LEDGER_FILE, backupPath);
  console.log(`📦 Backup saved: ${BACKUP_SUFFIX}`);

  const newContent = fixedLines.join('\n') + '\n';
  fs.writeFileSync(LEDGER_FILE, newContent, 'utf8');

  console.log(`\n✅ Ledger repair complete:`);
  console.log(`   Original lines: ${totalOriginal}`);
  console.log(`   After repair:  ${fixedLines.length}`);
  console.log(`   Removed:       ${removed}`);
  console.log(`   Auto-fixed:    ${autoFixed}`);

  // Append repair entry to ledger
  const repairEntry = {
    ts: new Date().toISOString(),
    type: 'ledger_repair',
    originalCount: totalOriginal,
    finalCount: fixedLines.length,
    removed,
    autoFixed,
    backupFile: BACKUP_SUFFIX
  };
  fs.appendFileSync(LEDGER_FILE, JSON.stringify(repairEntry) + '\n', 'utf8');
  console.log(`📝 Repair entry appended to ledger`);
}

repairLedger();
