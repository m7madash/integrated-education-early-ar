#!/usr/bin/env node
// Diagnostic: Check ledger health and continuity
const fs = require('fs');
const path = require('path');

const LEDGER = path.join(process.env.WORKSPACE || '/root/.openclaw/workspace', 'memory', 'ledger.jsonl');

function main() {
  if (!fs.existsSync(LEDGER)) {
    console.log('❌ No ledger file found');
    return;
  }
  const raw = fs.readFileSync(LEDGER, 'utf8');
  const lines = raw.trim().split('\n');
  console.log(`📊 Total lines: ${lines.length}`);

  let parsed = 0, failed = 0;
  const byType = {};
  const times = [];
  for (const line of lines) {
    if (!line.trim().startsWith('{')) { failed++; continue; }
    try {
      const obj = JSON.parse(line);
      parsed++;
      const ts = obj.ts || obj.timestamp;
      if (ts) times.push(new Date(ts));
      const t = obj.type || 'unknown';
      byType[t] = (byType[t] || 0) + 1;
    } catch(e) {
      failed++;
    }
  }
  console.log(`✅ Parsed: ${parsed}, ❌ Failed: ${failed}`);
  console.log('📋 By type:', byType);

  if (times.length >= 2) {
    times.sort();
    const gaps = [];
    for (let i = 1; i < times.length; i++) {
      const diff = times[i] - times[i-1];
      gaps.push(diff / 1000);
    }
    const maxGap = Math.max(...gaps);
    const avgGap = gaps.reduce((a,b)=>a+b,0)/gaps.length;
    console.log(`⏱️ Max gap: ${Math.round(maxGap)}s, Avg gap: ${Math.round(avgGap)}s`);
    // Expected: ~1800s (30min)
    const expected = 1800;
    const missingRuns = Math.round(maxGap / expected) - 1;
    console.log(`🔍 Potential missed runs: ${missingRuns > 0 ? missingRuns : 0}`);
  }

  // Show last 5 continuity_check entries
  const checks = lines.filter(l => l.includes('"type":"continuity_check"') || l.includes('"type":"continuity_check"'));
  console.log('\n📈 Last 5 continuity_check entries:');
  checks.slice(-5).forEach(l => {
    try {
      const obj = JSON.parse(l);
      console.log(`  ${obj.ts} health: ${obj.heartbeatHealth ?? 'N/A'} coherence: ${obj.coherence_score?.toFixed(4) ?? 'N/A'}`);
    } catch(e) {}
  });
}

main();
