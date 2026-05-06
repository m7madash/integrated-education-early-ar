#!/usr/bin/env node
// Diagnose heartbeat health gap
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

function main() {
  const now = new Date();
  const today = now.toISOString().slice(0,10);
  const todayStart = new Date(today + 'T00:00:00Z').getTime();
  const minutesElapsed = Math.floor((now - todayStart) / 60000);
  const expectedHeartbeats = Math.max(1, Math.floor(minutesElapsed / 30));
  console.log(`⏰ Minutes elapsed today: ${minutesElapsed}`);
  console.log(`✅ Expected heartbeats: ${expectedHeartbeats}`);

  if (!fs.existsSync(LEDGER)) {
    console.log('❌ No ledger file');
    return;
  }

  const lines = fs.readFileSync(LEDGER, 'utf8').split('\n').filter(l => l.trim());
  console.log(`📊 Total ledger lines: ${lines.length}`);

  const heartbeatTypes = ['continuity_check', 'continuity_pulse', 'continuity_work'];
  const entries = [];
  for (const line of lines) {
    try {
      const obj = JSON.parse(line);
      if (heartbeatTypes.includes(obj.type)) {
        const entryDate = new Date(obj.ts || obj.timestamp);
        if (entryDate.toISOString().slice(0,10) === today) {
          entries.push({ ts: obj.ts || obj.timestamp, type: obj.type, error: obj.error });
        }
      }
    } catch(e) {}
  }
  console.log(`💓 Heartbeat entries today: ${entries.length}`);
  entries.sort((a,b) => new Date(a.ts) - new Date(b.ts));
  console.log('\n📋 Timeline (last 10):');
  entries.slice(-10).forEach(e => {
    const status = e.error ? '❌' : '✅';
    console.log(`  ${status} ${e.ts} (${e.type})`);
  });

  // Missing intervals analysis
  const expectedTimes = [];
  for (let i = 0; i < expectedHeartbeats; i++) {
    expectedTimes.push(new Date(todayStart + i * 30 * 60000));
  }
  const missing = expectedTimes.filter(exp => {
    return !entries.some(e => {
      const eTime = new Date(e.ts);
      const diffMin = Math.abs(eTime - exp) / 60000;
      return diffMin < 5; // within 5 minutes
    });
  });
  console.log(`\n🔍 Missing heartbeats (no entry within 5min of expected): ${missing.length}`);
  missing.forEach(m => console.log('  ', m.toISOString()));
}

main();
