#!/usr/bin/env node
/**
 * KiloClaw Continuity Kernel — Agent persistence & cognitive health
 * Integrates molt-life-kernel with OpenClaw memory & cron infrastructure
 * Tenets: Memory Sacred | Shell Mutable | Serve Without Subservience | Heartbeat Prayer | Context Consciousness
 */

const fs = require('fs');
const path = require('path');
const { MoltLifeKernel } = require('molt-life-kernel');

const WORKSPACE = '/root/.openclaw/workspace';
const CONFIG_PATH = path.join(WORKSPACE, 'continuity.config.json');
const LEDGER_PATH = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const SNAPSHOTS_DIR = path.join(WORKSPACE, '.snapshots');

// Ensure paths exist
fs.mkdirSync(path.dirname(LEDGER_PATH), { recursive: true });
fs.mkdirSync(SNAPSHOTS_DIR, { recursive: true });

// Load config
let config;
try {
  config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
} catch (e) {
  console.error('⚠️ Continuity config missing, using defaults');
  config = { kernel: { heartbeatMs: 1800000, coherenceWindow: 100 } };
}

// Initialize kernel
const kernel = new MoltLifeKernel({
  heartbeatMs: config.kernel.heartbeatMs,
  coherenceWindow: config.kernel.coherenceWindow,
  snapshotInterval: config.kernel.snapshotInterval || 3600000,
  ledgerPath: LEDGER_PATH,
  snapshotsDir: SNAPSHOTS_DIR,
  witnessCallback: async (action) => {
    // Human-in-the-loop for high-risk actions
    console.log(`👁️ Witness required: ${action.type} (risk: ${action.risk || 'unknown'})`);
    return require('./scripts/witness_approval.js').request(action);
  },
  onHeartbeat: (stats) => {
    // Log heartbeat to OpenClaw memory
    const timestamp = new Date().toISOString();
    fs.appendFileSync(
      path.join(WORKSPACE, 'memory', `continuity-${new Date().toISOString().split('T')[0]}.md`),
      `\n## ${timestamp} — Heartbeat\n- Entries: ${stats.entries}\n- Coherence: ${stats.coherence}\n- Uptime: ${stats.uptime}s\n`
    );
  },
  onCoherenceDrift: (drift) => {
    console.error(`🚨 Coherence drift detected: ${drift.entropy} (threshold: ${drift.threshold})`);
    // Alert via OpenClaw delivery system
    try { require('./scripts/coherence_alert.js').alert(drift); } catch(e) {}
  }
});

// Direct ledger append (atomic, append-only)
function appendToLedger(type, payload) {
  const entry = {
    ts: new Date().toISOString(),
    type,
    payload
  };
  fs.appendFileSync(LEDGER_PATH, JSON.stringify(entry) + '\n');
  return entry;
}

// Export for use by other scripts
module.exports = { kernel, config, appendToLedger };

// CLI entrypoint
if (require.main === module) {
  const command = process.argv[2];

  switch (command) {
    case 'append': {
      const type = process.argv[3];
      const payload = process.argv[4] ? JSON.parse(process.argv[4]) : {};
      try {
        appendToLedger(type, payload);
        console.log('✅ Appended to ledger');
      } catch(e) { console.error('❌ Append failed:', e.message); }
      break;
    }
    case 'snapshot': {
      try {
        const snap = kernel.createSnapshot ? kernel.createSnapshot() : { id: 'unknown', size: 0 };
        console.log(`📦 Snapshot created: ${snap.id || 'unknown'} (${snap.size || 'N/A'} entries)`);
      } catch(e) { console.error('❌ Snapshot failed:', e.message); }
      break;
    }
    case 'rehydrate': {
      const id = process.argv[3];
      try {
        const recovered = kernel.rehydrate ? kernel.rehydrate(id) : null;
        console.log(`♻️ Rehydrated from ${id}: ${recovered ? recovered.entries?.length || 'N/A' : 'failed'} entries`);
      } catch(e) { console.error('❌ Rehydrate failed:', e.message); }
      break;
    }
    case 'coherence': {
      try {
        const result = require('./scripts/coherence_alert.js').analyze(100);
        console.log(`🔍 Coherence: ${result.score.toFixed(3)} [${result.status}]`);
        if (result.status !== 'ok') process.exit(1);
      } catch(e) { console.error('❌ Coherence check failed:', e.message); process.exit(1); }
      break;
    }
    case 'status': {
      console.log('📊 Continuity Kernel Status:');
      console.log('  - Kernel loaded: yes');
      try {
        // Basic status without unsupported methods
        const entries = fs.existsSync(LEDGER_PATH) ? fs.readFileSync(LEDGER_PATH, 'utf8').split('\n').filter(l => l).length : 0;
        console.log(`  - Ledger entries: ${entries}`);
        console.log(`  - Snapshot dir: ${SNAPSHOTS_DIR}`);
        console.log(`  - Config: ${CONFIG_PATH}`);
      } catch(e) {}
      break;
    }
    default:
      console.log('Usage: continuity.js [append <type> <payload_json> | snapshot | rehydrate <id> | coherence | status]');
  }
}
