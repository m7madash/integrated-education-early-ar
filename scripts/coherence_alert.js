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

// Load continuity config for defaults
let DEFAULT_WINDOW = 100;
let CFG_EXPECTED = 1800;
try {
  const cfgPath = path.join(WORKSPACE, 'continuity.config.json');
  const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
  DEFAULT_WINDOW = (cfg.kernel && cfg.kernel.coherenceWindow) || DEFAULT_WINDOW;
  CFG_EXPECTED = ((cfg.kernel && cfg.kernel.heartbeatMs) || 1800000) / 1000;
} catch (e) { /* ignore, use defaults */ }

function median(arr) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

function analyze(windowSize = DEFAULT_WINDOW) {
  const defaultResult = { score: 1.0, status: 'ok', entries: 0, reason: 'insufficient_data' };

  if (!fs.existsSync(LEDGER)) return { ...defaultResult };
  const allLines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(l => l.trim());
  if (allLines.length === 0) return { ...defaultResult };

  // Parse all entries and filter to continuity_check only first
  const allHbEntries = [];
  for (const line of allLines) {
    try {
      const obj = JSON.parse(line);
      if (obj.type === 'continuity_check' && obj.ts && obj.duplicate !== true) {
        allHbEntries.push({ ts: new Date(obj.ts).getTime() });
      }
    } catch (e) { /* skip malformed */ }
  }

  if (allHbEntries.length < 2) return { ...defaultResult, entries: allHbEntries.length, reason: 'insufficient_heartbeat_entries' };

  // Sort by timestamp
  allHbEntries.sort((a, b) => a.ts - b.ts);

  // Take last windowSize heartbeat entries (not ledger lines)
  const window = allHbEntries.slice(-windowSize);
  if (window.length < 2) return { ...defaultResult, entries: window.length };

  // Compute intervals in seconds
  const intervals = [];
  for (let i = 1; i < window.length; i++) {
    const iv = (window[i].ts - window[i-1].ts) / 1000;
    if (Number.isFinite(iv) && iv >= 300) { // filter short-interval paired entries (< 5 min) and NaN
      intervals.push(iv);
    }
  }

  const expected = CFG_EXPECTED;
  const sortedIntervals = [...intervals].sort((a,b) => a - b);
  const medianVal = sortedIntervals[Math.floor(sortedIntervals.length/2)];
  const absDevs = intervals.map(d => Math.abs(d - expected));
  const MAD = median(absDevs.sort((a,b) => a - b));

  let score = 1 - Math.min(1, MAD / expected);
  score = Math.max(0, Math.min(1, score));

  const thresholdHigh = 0.8, thresholdLow = 0.6;
  let status = 'ok';
  if (score < thresholdLow) status = 'degraded';
  else if (score < thresholdHigh) status = 'warning';

  return { score, status, entries: window.length, interval_median: medianVal, MAD, expected_interval: expected };
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
  const result = analyze(DEFAULT_WINDOW);
  console.log(`🔍 Coherence: ${result.score.toFixed(3)} [${result.status}]`);

  if (result.status !== 'ok') {
    alert(result);
    process.exit(1);
  } else {
    process.exit(0);
  }
}

module.exports = { analyze, alert };
