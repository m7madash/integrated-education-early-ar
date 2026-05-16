#!/usr/bin/env node
/**
 * Duplicate check for continuity runner
 * Returns exit code 0 if this run should be suppressed (duplicate)
 * Returns exit code 1 if this run should proceed
 * Outputs: "DUPLICATE: <seconds>s" or "PROCEED"
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const DUPLICATE_WINDOW_SEC = 60; // Increased from 30s to be less aggressive

function shouldSuppress() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) {
      console.log('PROCEED (no ledger)');
      return false;
    }

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    // Find most recent continuity_check
    let lastCheck = null;
    for (let i = lines.length - 1; i >= 0; i--) {
      const line = lines[i];
      if (!line.startsWith('{')) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'continuity_check' && entry.ts) {
          lastCheck = entry;
          break;
        }
      } catch (e) {
        // skip
      }
    }

    if (!lastCheck) {
      console.log('PROCEED (no previous check)');
      return false;
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
      return true;
    }

    console.log(`PROCEED (last check was ${diffSec}s ago)`);
    return false;
  } catch (e) {
    console.error('DUPLICATE_CHECK_ERROR:', e.message);
    // On error, proceed (fail-safe)
    console.log('PROCEED (error in duplicate check)');
    return false;
  }
}

if (shouldSuppress()) {
  process.exit(0); // suppress this run
} else {
  process.exit(1); // proceed with full check
}
