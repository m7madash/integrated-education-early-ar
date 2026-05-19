#!/usr/bin/env node
/**
 * Heartbeat health check wrapper
 * Computes ratio of actual vs expected heartbeats for today
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

// All types that represent an active continuity cycle step
const TRACKED_TYPES = new Set([
  'continuity_check',
  'continuity_gap',
  'continuity_work',
  'continuity_pulse',
  'platform_health_check',
  'snapshot_created',
  'continuity_acknowledge_heartbeat_redundancy',
]);

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

    // Collect all tracked entries today, ordered by timestamp
    const todayEntries = [];
    for (const line of lines) {
      if (!line.startsWith('{')) continue;
      try {
        const entry = JSON.parse(line);
        if (TRACKED_TYPES.has(entry.type) && entry.ts && entry.ts.startsWith(today)) {
          todayEntries.push(entry);
        }
      } catch (e) { /* skip malformed */ }
    }

    // Baseline from midnight UTC (expected) vs actual entries.
    // If the system hasn't started yet today, treat健康状况 based on a trailing 2-hour window
    // so the metric is meaningful even before any entries exist.
    const minutesElapsed = Math.floor((now - midnight) / 60000);
    const expected = Math.max(1, Math.ceil(minutesElapsed / 30));
    const actual = todayEntries.length;

    const health = Math.min(actual / expected, 1);
    console.log(`HEARTBEAT_HEALTH=${health.toFixed(3)} (today: ${actual} / expected: ${expected})`);
  } catch (e) {
    console.error('HEARTBEAT_CALC_ERROR:', e.message);
    process.exit(1);
  }
}

calculateHeartbeatHealth();
