#!/usr/bin/env node
/**
 * Coherence Alert — Detects cognitive drift using Shannon entropy analysis
 * Tenet 5: Context is Consciousness
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const ALERT_LOG = path.join(WORKSPACE, 'logs', 'coherence_alerts.log');

function shannonEntropy(entries) {
  // Calculate entropy of entry types to detect unusual patterns
  const counts = {};
  entries.forEach(e => { counts[e.type] = (counts[e.type] || 0) + 1; });
  const total = entries.length;
  let entropy = 0;
  Object.values(counts).forEach(c => {
    const p = c / total;
    entropy -= p * Math.log2(p);
  });
  return entropy;
}

function analyze(windowSize = 100) {
  if (!fs.existsSync(LEDGER)) return { score: 1.0, status: 'ok', entries: 0 };

  const lines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(l => l.trim());
  const window = lines.slice(-windowSize);
  const entries = window.map(l => JSON.parse(l));

  const entropy = shannonEntropy(entries);
  const maxEntropy = Math.log2(Math.max(...Object.values(
    entries.reduce((a, e) => { a[e.type] = (a[e.type] || 0) + 1; return a; }, {})
  ) || 1));

  // Normalize score: lower entropy = more coherent (consistent patterns)
  // Higher entropy = more random/drifting
  const score = maxEntropy > 0 ? 1 - (entropy / maxEntropy) : 1;

  const threshold = 0.6; // Minimum acceptable coherence
  const status = score >= threshold ? 'ok' : 'degraded';

  return { score, status, entropy, threshold, entries: entries.length };
}

function alert(drift) {
  const timestamp = new Date().toISOString();
  const msg = `[${timestamp}] COHERENCE ALERT: score=${drift.score.toFixed(3)} (${drift.status})\n` +
              `  entropy=${drift.entropy.toFixed(3)} threshold=${drift.threshold}\n` +
              `  Recent types: ${JSON.stringify(drift.recentTypes)}\n`;

  fs.appendFileSync(ALERT_LOG, msg);
  console.error(msg.trim());

  // Also send via Telegram if configured
  try {
    const telegram = require('./scripts/telegram_notify');
    telegram.send(`🚨 Coherence drift detected: ${drift.score.toFixed(3)}\nCheck ${WORKSPACE}/logs/coherence_alerts.log`);
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
