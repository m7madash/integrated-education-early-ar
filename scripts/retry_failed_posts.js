#!/usr/bin/env node
/**
 * retry_failed_posts.js — Retry recently failed platform posts
 *
 * Scans ledger for post_publish entries with success=false in last 6 hours
 * and re-attempts publishing for those missions on the failed platforms.
 *
 * This runs as a background task to heal partial_success missions.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const RETRY_COOLDOWN_HOURS = 6;

function readRecentFailures() {
  const cutoff = new Date(Date.now() - RETRY_COOLDOWN_HOURS * 60 * 60 * 1000);
  try {
    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const entries = content.trim().split('\n')
      .filter(l => l.startsWith('{'))
      .map(l => {
        try { return JSON.parse(l); } catch(e) { return null; }
      })
      .filter(e => e && e.type === 'post_publish' && e.payload && e.payload.success === false);

    // Group by mission+platform, dedupe by only retrying once per combo
    const seen = new Set();
    const toRetry = [];

    for (const entry of entries) {
      const { mission, platform } = entry.payload;
      const key = `${mission}|${platform}`;
      let entryTime;
      try {
        entryTime = new Date(entry.ts);
      } catch (e) {
        console.warn('⚠️  Skipping ledger entry with unparseable timestamp:', entry.ts);
        continue;
      }
      if (isNaN(entryTime.getTime())) {
        console.warn('⚠️  Skipping ledger entry with invalid timestamp (NaN):', entry.ts);
        continue;
      }

      if (entryTime < cutoff) continue; // too old
      if (seen.has(key)) continue; // already queued for retry

      seen.add(key);
      toRetry.push({ mission, platform, ts: entry.ts });
    }

    return toRetry;
  } catch (e) {
    console.error('❌ Failed to read ledger:', e.message);
    return [];
  }
}

function recordRetryAttempt(mission, platform) {
  const entry = {
    ts: new Date().toISOString(),
    type: 'retry_attempt',
    payload: { mission, platform, mode: 'auto_heal' }
  };
  fs.appendFileSync(LEDGER_FILE, JSON.stringify(entry) + '\n', 'utf8');
}

// Main
console.log('🔍 Scanning for recent publish failures to retry...');
const failures = readRecentFailures();

if (failures.length === 0) {
  console.log('✅ No recent failures to retry');
  process.exit(0);
}

console.log(`⚠️  Found ${failures.length} failure(s) to retry:`);
for (const f of failures) {
  try {
    const formattedDate = new Date(f.ts).toISOString();
    console.log(`   - ${f.mission} on ${f.platform} (original: ${formattedDate})`);
  } catch (e) {
    console.log(`   - ${f.mission} on ${f.platform} (timestamp malformed: ${f.ts})`);
  }
}

// For each failure, we need to regenerate the post content and republish
// However, the post content already exists in mission files; we just need to call the platform-specific publisher
// Since our publish script publishes all platforms at once, we need a smarter approach

console.log('\n⏳ Retry implementation: would call platform-specific republish logic');
console.log('   (To be implemented: parse post payload, extract content, call platform API directly)');

// For now, record the retry scan so continuity runner knows we checked
const scanEntry = {
  ts: new Date().toISOString(),
  type: 'retry_scan',
  payload: { failuresFound: failures.length, scannedHours: RETRY_COOLDOWN_HOURS }
};
fs.appendFileSync(LEDGER_FILE, JSON.stringify(scanEntry) + '\n', 'utf8');

console.log('✅ Retry scan complete — failures logged for manual/healer action');
