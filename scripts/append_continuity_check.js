#!/usr/bin/env node
/**
 * Append a continuity_check ledger entry with full KPI and coherence metrics.
 * Used by the 30min continuity script to record rich health data.
 */

// No need for kernel; persistence via file
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const ledgerPath = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
let kpi = null;
try {
  kpi = JSON.parse(fs.readFileSync(path.join(WORKSPACE, 'memory', 'kpi_current.json'), 'utf8'));
} catch (e) {
  // ignore, use defaults
}

// Compute coherence score using coherence_alert
let coherenceScore = 1.0;
let coherenceOk = true;
try {
  const ca = require('./coherence_alert');
  const res = ca.analyze();
  coherenceScore = res.score;
  coherenceOk = res.status === 'ok';
} catch (e) {
  coherenceOk = false;
}

// Extract platform reliability overall (may be object or number)
let platformReliability = null;
if (kpi && kpi.metrics && kpi.metrics.platformReliability) {
  if (typeof kpi.metrics.platformReliability === 'object' && kpi.metrics.platformReliability.overall !== undefined) {
    platformReliability = kpi.metrics.platformReliability.overall;
  } else if (typeof kpi.metrics.platformReliability === 'number') {
    platformReliability = kpi.metrics.platformReliability;
  }
}

// Extract heartbeatHealth and errorFrequency
const heartbeatHealth = (kpi && kpi.metrics && kpi.metrics.heartbeatHealth !== undefined) ? kpi.metrics.heartbeatHealth : null;
const errorRate = (kpi && kpi.metrics && kpi.metrics.errorFrequency !== undefined) ? kpi.metrics.errorFrequency : null;

// Build entry
const entry = {
  ts: new Date().toISOString(),
  type: 'continuity_check',
  phase: '30min',
  coherence_ok: coherenceOk,
  coherence_score: coherenceScore,
  platformReliability,
  heartbeatHealth,
  errorRate
};

// Append directly to ledger file (atomic)
try {
  fs.appendFileSync(ledgerPath, JSON.stringify(entry) + '\n');
  console.log('✅ Continuity check recorded: coherence=' + coherenceScore.toFixed(3) + ', platform=' + (platformReliability !== null ? platformReliability.toFixed(3) : 'null') + ', hb=' + (heartbeatHealth !== null ? heartbeatHealth.toFixed(3) : 'null'));
} catch (err) {
  console.error('❌ Failed to write ledger entry:', err.message);
  process.exit(1);
}

// Note: kernel metrics are not used across processes; persistence is via file.
