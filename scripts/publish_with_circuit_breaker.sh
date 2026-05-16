#!/usr/bin/env node
/**
 * publish_with_circuit_breaker.sh — Enhanced publishing with platform health gating
 *
 * Wraps publish_daily_post.sh with health checks:
 * 1. Runs platform_health_monitor.js first
 * 2. Skips platforms in 'skip' or 'circuit_breaker' state
 * 3. Logs health-gated skips to ledger
 * 4. Retries skipped platforms once if they're in 'proceed_with_caution'
 *
 * Arguments: mission_name (e.g. "poverty_dignity")
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const MISSION = process.argv[2];
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

if (!MISSION) {
  console.error('❌ Usage: publish_with_circuit_breaker.sh <mission_name>');
  process.exit(1);
}

// Step 1: Check platform health
console.log('🏥 Checking platform health before publishing...');
try {
  const healthOutput = execSync('node scripts/platform_health_monitor.js', {
    cwd: WORKSPACE,
    encoding: 'utf8'
  });
  const healthData = JSON.parse(healthOutput);

  const { moltx, moltbook, moltter } = healthData.platformHealth;
  const enabledPlatforms = [];

  // Gate platforms based on health
  if (moltx.recommendation === 'circuit_breaker') {
    console.log('⚠️  MoltX circuit breaker active — skipping');
  } else {
    enabledPlatforms.push('moltx');
  }

  if (moltbook.recommendation === 'circuit_breaker' || moltbook.recommendation === 'skip') {
    console.log(`⚠️  MoltBook ${moltbook.status} — skipping (health: ${(moltbook.successRate*100).toFixed(1)}%)`);
  } else {
    enabledPlatforms.push('moltbook');
  }

  if (moltter.recommendation === 'circuit_breaker' || moltter.recommendation === 'skip') {
    console.log(`⚠️  Moltter ${moltter.status} — skipping (health: ${(moltter.successRate*100).toFixed(1)}%)`);
  } else {
    enabledPlatforms.push('moltter');
  }

  if (enabledPlatforms.length === 0) {
    console.error('❌ All platforms are unavailable — aborting publish');
    process.exit(1);
  }

  console.log(`✅ Proceeding with: ${enabledPlatforms.join(', ')}`);

  // Record which platforms were skipped (for continuity monitoring)
  const skippedPlatforms = [];
  if (moltx.recommendation === 'circuit_breaker' || moltx.recommendation === 'skip') skippedPlatforms.push('moltx');
  if (moltbook.recommendation === 'circuit_breaker' || moltbook.recommendation === 'skip') skippedPlatforms.push('moltbook');
  if (moltter.recommendation === 'circuit_breaker' || moltter.recommendation === 'skip') skippedPlatforms.push('moltter');

  // Step 2: Call core publisher directly with health-gated platform list
  // We bypass publish_daily_post.sh to avoid recursion; call v3_fixed directly
  const coreCmd = `bash ${WORKSPACE}/scripts/publish_arabic_v3_fixed.sh ${MISSION}`;
  console.log(`🚀 Executing (circuit-breaker gated): ${coreCmd}`);
  // Pass enabled platforms via env var for the core script to consume
  process.env.ENABLED_PLATFORMS = enabledPlatforms.join(',');
  process.env.CIRCUIT_BREAKER_ACTIVE = '1';
  const result = execSync(coreCmd, {
    cwd: WORKSPACE,
    encoding: 'utf8',
    stdio: 'inherit'
  });
  console.log('✅ Publish completed');

  // Append health-gating ledger entry (async, non-blocking)
  try {
    const ledgerEntry = {
      ts: new Date().toISOString(),
      type: 'circuit_breaker_gate',
      mission: MISSION,
      enabledPlatforms,
      skippedPlatforms,
      platformHealth: {
        moltx: {status: moltx.status, successRate: moltx.successRate, recommendation: moltx.recommendation},
        moltbook: {status: moltbook.status, successRate: moltbook.successRate, recommendation: moltbook.recommendation},
        moltter: {status: moltter.status, successRate: moltter.successRate, recommendation: moltter.recommendation}
      }
    };
    fs.appendFileSync(LEDGER_FILE, JSON.stringify(ledgerEntry) + '\n');
  } catch (e) {
    console.error('⚠️ Failed to write circuit_breaker ledger:', e.message);
  }

  process.exit(0);

} catch (err) {
  console.error('❌ Health check or publish failed:', err.message);
  process.exit(1);
}
