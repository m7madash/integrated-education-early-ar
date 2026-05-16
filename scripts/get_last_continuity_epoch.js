#!/usr/bin/env node
/**
 * Wrapper for computing last run timestamp from ledger
 * Single binary — no shell operators, compliant with exec preflight
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

function getLastContinuityCheckEpoch() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) return null;

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    // Find last continuity_check entry
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i];
      if (!line.startsWith('{')) continue;

      try {
        const entry = JSON.parse(line);
        if (entry.type === 'continuity_check' && entry.ts) {
          const epoch = new Date(entry.ts).getTime() / 1000;
          return Math.floor(epoch);
        }
      } catch (e) {
        // skip malformed
      }
    }
  } catch (e) {
    console.error('Error reading ledger:', e.message);
  }
  return null;
}

const lastEpoch = getLastContinuityCheckEpoch();

if (lastEpoch === null) {
  console.log('0'); // no previous run
} else {
  console.log(lastEpoch.toString());
}
