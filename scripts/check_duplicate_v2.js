#!/usr/bin/env node
/**
 * Duplicate check for continuity runner (FIXED version)
 * Uses direct file scanning — no shell operators, no external commands
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const DUPLICATE_WINDOW_SEC = 45; // Increased from 30s, reduced from 60s — balanced

function main() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) {
      console.log('PROCEED (no ledger)');
      process.exit(1); // proceed
    }

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    // Find most recent continuity_check
    let lastCheck = null;
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i];
      if (!line.trim().startsWith('{')) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'continuity_check' && entry.ts) {
          lastCheck = entry;
          break;
        }
      } catch (e) {
        // skip malformed
      }
    }

    if (!lastCheck) {
      console.log('PROCEED (no previous check)');
      process.exit(1);
    }

    const lastTime = new Date(lastCheck.ts).getTime();
    const now = Date.now();
    const diffSec = Math.floor((now - lastTime) / 1000);

    if (diffSec < DUPLICATE_WINDOW_SEC) {
      console.log(`DUPLICATE: ${diffSec}s (window=${DUPLICATE_WINDOW_SEC}s)`);

      // Append minimal duplicate entry for audit trail
      const ledgerEntry = JSON.stringify({
        ts: new Date().toISOString(),
        type: 'continuity_check',
        phase: '30min',
        duplicate: true,
        previousInterval: diffSec
      }) + '\n';
      fs.appendFileSync(LEDGER_FILE, ledgerEntry, 'utf8');

      process.exit(0); // suppress
    }

    console.log(`PROCEED (last check was ${diffSec}s ago, window ${DUPLICATE_WINDOW_SEC}s)`);
    process.exit(1); // proceed
  } catch (e) {
    console.error('DUPLICATE_CHECK_ERROR:', e.message);
    // Fail-safe: proceed
    process.exit(1);
  }
}

main();
