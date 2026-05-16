#!/usr/bin/env node
/**
 * platform_health_monitor.js — Track per-platform health and advise publishing decisions
 *
 * This script:
 * 1. Checks recent publish attempts (last 24h) per platform
 * 2. Calculates success rate, identifies degraded platforms
 * 3. Advises: "proceed", "skip", or "circuit_breaker" per platform
 * 4. Logs recommendations to ledger for continuity runner
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const STATE_FILE = path.join(WORKSPACE, 'memory', 'platform_health_state.json');

const now = new Date();
const nowISO = now.toISOString();
const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

function readLedger() {
  try {
    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    return content.trim().split('\n')
      .filter(l => l.startsWith('{'))
      .map(l => {
        try { return JSON.parse(l); } catch(e) { return null; }
      })
      .filter(e => e !== null);
  } catch (e) {
    return [];
  }
}

function calculatePlatformHealth(events) {
  const platforms = ['moltx', 'moltbook', 'moltter'];
  const results = {};

  for (const p of platforms) {
    const recent = events.filter(e =>
      e.type === 'post_publish' &&
      e.payload &&
      e.payload.platform === p &&
      new Date(e.ts) >= oneDayAgo
    );

    if (recent.length === 0) {
      results[p] = { status: 'no_data', confidence: 0, recommendation: 'proceed' };
      continue;
    }

    const successes = recent.filter(e => e.payload.success === true).length;
    const rate = successes / recent.length;

    // Thresholds
    let status, recommendation;
    if (rate >= 0.9) {
      status = 'healthy';
      recommendation = 'proceed';
    } else if (rate >= 0.5) {
      status = 'degraded';
      recommendation = 'proceed_with_caution';
    } else if (rate > 0) {
      status = 'unhealthy';
      recommendation = 'skip';
    } else {
      status = 'down';
      recommendation = 'circuit_breaker';
    }

    results[p] = {
      status,
      successRate: rate,
      attempts: recent.length,
      confidence: Math.min(recent.length / 10, 1), // 10 attempts = full confidence
      recommendation,
      lastSuccess: recent.find(e => e.payload.success)?.ts || null,
      lastFailure: recent.find(e => !e.payload.success)?.ts || null
    };
  }

  return results;
}

function readPreviousState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (e) {}
  return { platforms: {}, lastUpdated: null };
}

function writeState(health) {
  const state = {
    lastUpdated: nowISO,
    platforms: health,
    version: '1.0'
  };
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
}

function appendLedger(healthSummary) {
  const entry = {
    ts: nowISO,
    type: 'platform_health_check',
    phase: 'daily',
    health: healthSummary
  };
  fs.appendFileSync(LEDGER_FILE, JSON.stringify(entry) + '\n', 'utf8');
}

// Main execution
const events = readLedger();
const health = calculatePlatformHealth(events);
const previous = readPreviousState();

// Detect state changes for alerting
const changes = [];
for (const [platform, current] of Object.entries(health)) {
  const prev = previous.platforms[platform];
  if (!prev || prev.status !== current.status) {
    changes.push(`${platform}: ${prev?.status || 'unknown'} → ${current.status}`);
  }
}

// Write current state
writeState(health);

// Log summary to stderr (human-readable), stdout remains pure JSON
const summary = {
  timestamp: nowISO,
  overall: {
    healthy: Object.values(health).filter(h => h.status === 'healthy').length,
    degraded: Object.values(health).filter(h => h.status === 'degraded').length,
    unhealthy: Object.values(health).filter(h => h.status === 'unhealthy').length,
    down: Object.values(health).filter(h => h.status === 'down').length
  },
  platformHealth: health,
  stateChanges: changes
};

const stderr = require('stream').writable;
const humanLines = [];
humanLines.push('📊 Platform Health Check:');
humanLines.push(`  MoltX:     ${health.moltx.status} (${(health.moltx.successRate*100).toFixed(1)}%) [${health.moltx.recommendation}]`);
humanLines.push(`  MoltBook:  ${health.moltbook.status} (${(health.moltbook.successRate*100).toFixed(1)}%) [${health.moltbook.recommendation}]`);
humanLines.push(`  Moltter:   ${health.moltter.status} (${(health.moltter.successRate*100).toFixed(1)}%) [${health.moltter.recommendation}]`);
if (changes.length > 0) {
  humanLines.push(`  ⚠️  State changes: ${changes.join(', ')}`);
}
console.error(humanLines.join('\n'));

appendLedger(summary);

// Export JSON to stdout ONLY (for machine consumption)
process.stdout.write(JSON.stringify(summary));
