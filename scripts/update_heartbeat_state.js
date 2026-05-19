#!/usr/bin/env node
/**
 * Heartbeat state updater — recomputes health ratio and updates heartbeat-state.json
 * Single binary — no shell operators, no pipelines
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const STATE_FILE = path.join(WORKSPACE, 'memory', 'heartbeat-state.json');

function computeHeartbeatHealth() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) return { health: 0, actual: 0, expected: 1 };

    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');

    const today = new Date().toISOString().split('T')[0];
    let actual = 0;

    for (const line of lines) {
      if (!line.startsWith('{')) continue;
      try {
        const e = JSON.parse(line);
        if (e.ts && e.ts.startsWith(today)) {
          actual++;
        }
      } catch (err) {
        // skip
      }
    }

    const now = Date.now();
    const midnight = new Date(today + 'T00:00:00Z').getTime();
    const minutesElapsed = Math.floor((now - midnight) / 60000);
    const expected = Math.max(1, Math.ceil(minutesElapsed / 30));

    const health = Math.min(actual / expected, 1);

    return { health, actual, expected };
  } catch (e) {
    return { health: 0, actual: 0, expected: 1, error: e.message };
  }
}

function updateState() {
  const hb = computeHeartbeatHealth();
  const now = new Date();
  const lastRun = now.toISOString();
  const nextHb = new Date(now.getTime() + 30 * 60 * 1000).toISOString();

  let state = { lastChecks: {}, status: 'unknown', nextHeartbeat: null, lastContinuityRun: null };
  if (fs.existsSync(STATE_FILE)) {
    try {
      state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    } catch (e) {
      // keep defaults
    }
  }

  state.lastContinuityRun = lastRun;
  state.nextHeartbeat = nextHb;
  state.lastChecks = state.lastChecks || {};
  state.lastChecks.continuity = lastRun;
  state.lastChecks.ledger = lastRun;

  // Determine status from health (0–1 float)
  if (hb.health >= 0.95) {
    state.status = 'ok';
    state.degradationReason = '';
  } else if (hb.health >= 0.5) {
    state.status = 'degraded';
    state.degradationReason = `heartbeat_ratio_${Math.round(hb.health*100)}pct`;
  } else {
    state.status = 'critical';
    state.degradationReason = `heartbeat_ratio_${Math.round(hb.health*100)}pct`;
  }

  state.heartbeatHealth = hb.health;
  state.lastHeartbeatCount = { actual: hb.actual, expected: hb.expected };
  state.updatedAt = new Date().toISOString();

  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');

  console.log(`HEARTBEAT_STATE_UPDATED: status=${state.status}, health=${hb.health.toFixed(3)}, ${hb.actual}/${hb.expected} runs today, next=${nextHb}`);
}

updateState();
