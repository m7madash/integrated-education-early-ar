#!/usr/bin/env node
/**
 * Heartbeat health check wrapper
 * Computes ratio of actual vs expected heartbeats for today
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

function calculateHeartbeatHealth() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) {
      console.log('HEARTBEAT_HEALTH=0.000 (no ledger)');
      return;
    }

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    const today = new Date().toISOString().split('T')[0];
    const now = new Date();
    const midnight = new Date(today + 'T00:00:00Z');
    const minutesElapsed = Math.floor((now - midnight) / 60000);

    // Expected heartbeats: at least one every 30min, so ceil(minutes/30)
    const expected = Math.max(1, Math.ceil(minutesElapsed / 30));

    // Count today's continuity_check entries
    let actual = 0;
    for (const line of lines) {
      if (!line.startsWith('{')) continue;
      try {
        const entry = JSON.parse(line);
        if (entry.type === 'continuity_check' && entry.ts && entry.ts.startsWith(today)) {
          actual++;
        }
      } catch (e) {
        // skip malformed
      }
    }

    const health = Math.min(actual / expected, 1);
    console.log(`HEARTBEAT_HEALTH=${health.toFixed(3)} (today: ${actual} / expected: ${expected})`);
  } catch (e) {
    console.error('HEARTBEAT_CALC_ERROR:', e.message);
    process.exit(1);
  }
}

calculateHeartbeatHealth();
