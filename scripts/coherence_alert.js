#!/usr/bin/env node
/**
 * Coherence Alert — Detects cognitive drift using heartbeat interval regularity
 * Tenet 5: Context is Consciousness
 *
 * Improved from entropy-based to interval-based coherence measurement.
 * Coherence score reflects regularity of continuity_check entries relative to expected interval.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const ALERT_LOG = path.join(WORKSPACE, 'logs', 'coherence_alerts.log');

function median(arr) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

function analyze(windowSize = 100) {
  const defaultResult = { score: 1.0, status: 'ok', entries: 0, reason: 'insufficient_data' };

  if (!fs.existsSync(LEDGER)) return { ...defaultResult };
  const lines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(l => l.trim());
  if (lines.length === 0) return { ...defaultResult };

  // Take last windowSize entries
  const window = lines.slice(-windowSize);
  let entries = [];
  for (const line of window) {
    try {
      entries.push(JSON.parse(line));
    } catch (e) {
      // skip malformed
    }
  }

  if (entries.length < 2) {
    return { ...defaultResult, entries: entries.length };
  }

  // Filter to continuity_check entries only
  const hbEntries = entries.filter(e => e.type === 'continuity_check' && e.ts && e.duplicate !== true);
  if (hbEntries.length < 2) {
    return { ...defaultResult, entries: hbEntries.length, reason: 'insufficient_heartbeat_entries' };
  }

  // Sort by timestamp
  hbEntries.sort((a, b) => new Date(a.ts) - new Date(b.ts));

  // Compute intervals in seconds
  const intervals = [];
  for (let i = 1; i < hbEntries.length; i++) {
    const t1 = new Date(hbEntries[i - 1].ts).getTime();
    const t2 = new Date(hbEntries[i].ts).getTime();
    intervals.push((t2 - t1) / 1000);
  }

  // Expected interval from config
  let expected = 1800; // 30 minutes default
  try {
    const cfg = JSON.parse(fs.readFileSync(path.join(WORKSPACE, 'continuity.config.json'), 'utf8'));
    expected = ((cfg.kernel && cfg.kernel.heartbeatMs) || 1800000) / 1000;
  } catch (e) { /* ignore */ }

  const medDelta = median(intervals);
  const absDevs = intervals.map(d => Math.abs(d - expected));
  const MAD = median(absDevs);

  // Coherence score: linear decay based on median absolute deviation from expected
  let score = 1 - Math.min(1, MAD / expected);
  score = Math.max(0, Math.min(1, score));

  // Thresholds: high expectation for regular heartbeats
  const thresholdHigh = 0.8;
  const thresholdLow = 0.6;
  let status = 'ok';
  if (score < thresholdLow) status = 'degraded';
  else if (score < thresholdHigh) status = 'warning';

  return {
    score,
    status,
    entries: hbEntries.length,
    interval_median: medDelta,
    MAD,
    expected_interval: expected
  };
}

function alert(drift) {
  const timestamp = new Date().toISOString();
  const msg = `[${timestamp}] COHERENCE ALERT: score=${drift.score.toFixed(3)} (${drift.status})\n` +
              `  entries=${drift.entries} median_interval=${drift.interval_median?.toFixed(1) ?? 'N/A'}s MAD=${drift.MAD?.toFixed(1) ?? 'N/A'}s expected=${drift.expected_interval}s\n`;

  fs.appendFileSync(ALERT_LOG, msg);
  console.error(msg.trim());

  // Also send via Telegram if configured
  try {
    const telegram = require('./scripts/telegram_notify');
    telegram.send(`🚨 Coherence drift: ${drift.score.toFixed(3)} (${drift.status})\nCheck ${WORKSPACE}/logs/coherence_alerts.log`);
  } catch (e) { /* ignore */ }
}

// If called directly
if (require.main === module) {
  const result = analyze(100);
  console.log(`🔍 Coherence: ${result.score.toFixed(3)} [${result.status}]`);

  if (result.status !== 'ok') {
    alert(result);
    process.exit(1);
  } else {
    process.exit(0);
  }
}

module.exports = { analyze, alert };
