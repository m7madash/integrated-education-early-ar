#!/usr/bin/env node
/**
 * continuity_improvement_validate.js — Post-cycle validation
 *
 * Runs after continuity-improvement cron to confirm:
 * 1. Circuit breaker is integrated (publish_arabic.sh routes through wrapper)
 * 2. Platform health gating works (unhealthy platforms would be skipped)
 * 3. No stale cron state
 * 4. Recent ledger shows health-gated entries if any platforms were skipped
 *
 * Exit codes:
 *   0 = all checks passed
 *   1 = one or more checks failed
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const CRON_STATE = '/root/.openclaw/cron/jobs-state.json';

function log(msg, type = 'info') {
  const prefix = type === 'pass' ? '✅' : type === 'fail' ? '❌' : 'ℹ️';
  console.log(`${prefix} ${msg}`);
}

function fail(reason) {
  log(`FAIL: ${reason}`, 'fail');
  process.exit(1);
}

// ── Check 1: Verify circuit breaker wrapper exists and is executable ───────
const wrapperPath = path.join(WORKSPACE, 'scripts', 'publish_with_circuit_breaker.sh');
if (!fs.existsSync(wrapperPath)) {
  fail('Circuit breaker wrapper not found');
}
const wrapperStat = fs.statSync(wrapperPath);
if (!(wrapperStat.mode & fs.constants.S_IXUSR)) {
  fail('Circuit breaker wrapper not executable');
}
log('Circuit breaker wrapper exists and is executable');

// ── Check 2: Verify publish_arabic.sh routes through circuit breaker ─────────
const publisherPath = path.join(WORKSPACE, 'scripts', 'publish_arabic.sh');
const publisherContent = fs.readFileSync(publisherPath, 'utf8');
if (!publisherContent.includes('publish_with_circuit_breaker.sh')) {
  fail('publish_arabic.sh does NOT route through circuit breaker wrapper');
}
log('publish_arabic.sh routes through circuit breaker wrapper');

// ── Check 3: Verify publish_arabic_v3_fixed.sh respects ENABLED_PLATFORMS ─────
const v3FixedPath = path.join(WORKSPACE, 'scripts', 'publish_arabic_v3_fixed.sh');
const v3Content = fs.readFileSync(v3FixedPath, 'utf8');
if (!v3Content.includes('ENABLED_PLATFORMS') || !v3Content.includes('is_platform_enabled')) {
  fail('publish_arabic_v3_fixed.sh does NOT respect ENABLED_PLATFORMS gating');
}
log('publish_arabic_v3_fixed.sh respects ENABLED_PLATFORMS');

// ── Check 4: Confirm no stale cron running flags (for continuity-30min) ──────
if (fs.existsSync(CRON_STATE)) {
  const cronState = JSON.parse(fs.readFileSync(CRON_STATE, 'utf8'));
  const jobId = 'ea19561d-f2c2-4716-9032-5053e9f65dc3'; // continuity-30min-check-v2
  const job = cronState.jobs?.[jobId];
  if (job?.state?.runningAtMs) {
    const ageMin = (Date.now() - job.state.runningAtMs) / 60000;
    if (ageMin > 20) {
      fail(`Stale runningAtMs flag (${ageMin.toFixed(1)}min old) — cron may be stuck`);
    }
  }
}
log('No stale cron running flags detected');

// ── Check 5: Verify platform health monitor output is sane ──────────────────
try {
  const healthOutput = execSync('node scripts/platform_health_monitor.js', {
    cwd: WORKSPACE,
    encoding: 'utf8'
  });
  const health = JSON.parse(healthOutput);
  const { moltx, moltbook, moltter } = health.platformHealth;

  // MoltX should be either healthy or degraded (not down)
  if (moltx.status === 'down') fail('MoltX status is down — unexpected');
  // MoltBook/Moltter may be unhealthy, but that's expected; just verify field exists
  if (!moltbook.recommendation || !moltter.recommendation) fail('Platform health missing recommendations');

  log(`Platform health: MoltX=${moltx.status} (${(moltx.successRate*100).toFixed(0)}%), ` +
      `MoltBook=${moltbook.status} (${(moltbook.successRate*100).toFixed(0)}%), ` +
      `Moltter=${moltter.status} (${(moltter.successRate*100).toFixed(0)}%)`);
} catch (e) {
  fail('Failed to parse platform health: ' + e.message);
}

// ── Check 6: Look for recent circuit_breaker_gate ledger entries ─────────────
try {
  const ledgerLines = fs.readFileSync(LEDGER_FILE, 'utf8').trim().split('\n').reverse();
  const recentEntries = ledgerLines.slice(0, 50).filter(l => l.startsWith('{')).map(l => {
    try { return JSON.parse(l); } catch (e) { return null; }
  }).filter(Boolean);

  const circuitEntries = recentEntries.filter(e => e.type === 'circuit_breaker_gate');
  if (circuitEntries.length > 0) {
    const latest = circuitEntries[0];
    log(`Circuit breaker gating active: last run mission=${latest.mission}, ` +
        `enabled=[${latest.enabledPlatforms?.join(',')||'none'}], ` +
        `skipped=[${latest.skippedPlatforms?.join(',')||'none'}]`);
  } else {
    log('No circuit_breaker_gate entries yet — will appear on next publish');
  }
} catch (e) {
  log('Could not scan ledger for circuit breaker entries: ' + e.message, 'info');
}

// ── Check 7: Verify coherence is still healthy ───────────────────────────────
try {
  const allLines = fs.readFileSync(LEDGER_FILE, 'utf8').trim().split('\n');
  // Find most recent continuity_check that has coherence_score
  let lastCoherenceEntry = null;
  for (let i = allLines.length - 1; i >= 0; i--) {
    const line = allLines[i];
    if (!line.startsWith('{')) continue;
    try {
      const e = JSON.parse(line);
      if (e.type === 'continuity_check' && e.coherence_score != null) {
        lastCoherenceEntry = e;
        break;
      }
    } catch (e) { continue; }
  }

  if (!lastCoherenceEntry) fail('No coherence score found in recent ledger');
  if (!lastCoherenceEntry.coherence_ok) fail('Coherence not OK in latest check');
  if (lastCoherenceEntry.coherence_score < 0.95) {
    fail(`Coherence below target (${lastCoherenceEntry.coherence_score.toFixed(4)} < 0.95)`);
  }
  log(`Coherence healthy (${lastCoherenceEntry.coherence_score.toFixed(4)})`);
} catch (e) {
  fail('Could not verify coherence: ' + e.message);
}

// ── All checks passed ────────────────────────────────────────────────────────
log('All continuity improvement validations passed', 'pass');
process.exit(0);
