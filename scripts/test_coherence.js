#!/usr/bin/env node
// Wrapper to test coherence
const { analyze } = require('/root/.openclaw/workspace/scripts/coherence_alert');
const result = analyze(100);
console.log(`🔍 Coherence: ${result.score.toFixed(3)} [${result.status}]`);
console.log(`  Entries: ${result.entries}, Distinct types: ${result.distinctTypes || 'N/A'}`);
if (result.reason) console.log(`  Note: ${result.reason}`);
process.exit(result.status === 'ok' ? 0 : 1);
