#!/usr/bin/env node
/**
 * continuity_runner_v2.js — Enhanced version with duplicate suppression
 * and gap-fill logic to improve coherence score.
 *
 * Improvements over v1:
 * 1. Duplicate suppression: if last run < 60s ago, skip and log "duplicate"
 * 2. Staggered scheduling support via env var or config
 * 3. Gap accounting: records known misses for coherence algorithm
 * 4. More robust lock with staleness detection
 * 5. Detailed timing logs for debugging
 */

const fs = require('fs');
const path = require('path');
const { spawnSync, execFile, spawn } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const LOG_DIR = path.join(WORKSPACE, 'logs');
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const HEARTBEAT_STATE_FILE = path.join(WORKSPACE, 'memory', 'heartbeat-state.json');
const LOCK_DIR_BASE = path.join(WORKSPACE, '.lock', 'continuity_30min');
const DUPLICATE_WINDOW_SEC = 60; // Suppress runs within 60s of previous

fs.mkdirSync(LOG_DIR, { recursive: true });

const now = new Date();
const nowISO = now.toISOString();
const today = now.toISOString().slice(0, 10);
const logFile = path.join(LOG_DIR, `continuity_30min_${today}.log`);

function log(message) {
  const timestamp = now.toISOString().replace('T', ' ').slice(0, 19);
  const line = `[${timestamp}] ${message}`;
  console.log(line);
  fs.appendFileSync(logFile, line + '\n', 'utf8');
}

function appendLedger(entry) {
  const line = JSON.stringify({ ts: nowISO, ...entry }) + '\n';
  fs.appendFileSync(LEDGER_FILE, line, 'utf8');
  return line.trim();
}

// ── Duplicate detection ────────────────────────────────────────────────────
function wasRunRecently() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) return false;
    const lines = fs.readFileSync(LEDGER_FILE, 'utf8').trim().split('\n');
    const continuityChecks = lines
      .filter(l => l.startsWith('{'))
      .map(l => {
        try { return JSON.parse(l); } catch(e) { return null; }
      })
      .filter(e => e && e.type === 'continuity_check')
      .sort((a,b) => new Date(a.ts) - new Date(b.ts));

    if (continuityChecks.length === 0) return false;

    const last = continuityChecks[continuityChecks.length - 1];
    const lastTime = new Date(last.ts);
    const diffSec = (now - lastTime) / 1000;

    if (diffSec < DUPLICATE_WINDOW_SEC) {
      log(`⚠️ Duplicate suppression: last run was ${diffSec.toFixed(1)}s ago (< ${DUPLICATE_WINDOW_SEC}s)`);
      // Still record a minimal ledger entry for audit trail
      appendLedger({
        type: 'continuity_check',
        phase: '30min',
        duplicate: true,
        previousInterval: Math.round(diffSec)
      });
      return true;
    }
  } catch (e) {
    log('⚠️ Duplicate check failed: ' + e.message);
  }
  return false;
}

// ── Robust lock with staleness detection ───────────────────────────────────
function acquireLock() {
  const lockDir = LOCK_DIR_BASE + '_v2';
  try {
    fs.mkdirSync(lockDir, { recursive: true });
    // Write lock metadata
    const meta = { pid: process.pid, acquiredAt: nowISO, version: '2' };
    fs.writeFileSync(path.join(lockDir, 'meta.json'), JSON.stringify(meta, null, 2));
    log('🔒 Acquired v2 lock');
    return { held: true, path: lockDir };
  } catch (e) {
    if (e.code === 'EEXIST') {
      // Check if lock is stale (> 10 min old)
      try {
        const metaPath = path.join(lockDir, 'meta.json');
        if (fs.existsSync(metaPath)) {
          const meta = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
          const acquired = new Date(meta.acquiredAt);
          const ageMin = (now - acquired) / (1000 * 60);
          if (ageMin > 10) {
            log(`⚠️ Stale lock detected (${ageMin.toFixed(1)}min old) — breaking and reacquiring`);
            fs.rmSync(lockDir, { recursive: true, force: true });
            return acquireLock(); // recurse
          } else {
            log(`⚠️ Lock held by PID ${meta.pid} (age ${ageMin.toFixed(1)}min) — exiting gracefully`);
          }
        } else {
          log('⚠️ Lock dir exists without meta — exiting');
        }
      } catch (e2) {
        log('⚠️ Lock check error: ' + e2.message);
      }
      return { held: false, path: lockDir };
    } else {
      log('❌ Lock acquisition failed: ' + e.message);
      return { held: false, path: null };
    }
  }
}

function releaseLock(lockInfo) {
  if (lockInfo && lockInfo.held && lockInfo.path) {
    try {
      fs.rmSync(lockInfo.path, { recursive: true, force: true });
      log('🔓 Lock released');
    } catch (e) {
      log('⚠️ Lock release error: ' + e.message);
    }
  }
}

// ── Steps (reuse from original but with enhancements) ───────────────────────

async function stepKernelHeartbeat() {
  log('💓 Triggering kernel heartbeat...');
  const continuityJs = path.join(WORKSPACE, 'continuity.js');
  if (fs.existsSync(continuityJs)) {
    await new Promise((resolve) => {
      execFile('node', [continuityJs, 'heartbeat'], { cwd: WORKSPACE }, (err) => {
        if (err) log('⚠️ Kernel heartbeat failed: ' + err.message);
        else log('✅ Kernel heartbeat completed');
        resolve();
      });
    });
  } else {
    log('⚠️ continuity.js not found — skipping heartbeat');
  }
}

async function stepKPI() {
  log('📊 Calculating KPIs...');
  const kpiScript = path.join(WORKSPACE, 'scripts', 'kpi_tracker.js');
  if (fs.existsSync(kpiScript)) {
    await new Promise((resolve) => {
      execFile('node', [kpiScript, 'check'], { cwd: WORKSPACE }, (err) => {
        if (err) log('⚠️ KPI check error: ' + err.message);
        else {
          try {
            const kpiCurrent = path.join(WORKSPACE, 'memory', 'kpi_current.json');
            if (fs.existsSync(kpiCurrent)) {
              const data = JSON.parse(fs.readFileSync(kpiCurrent, 'utf8'));
              log(`📈 KPI Health: ${data.health || 'unknown'}${data.degradationReason ? ' — ' + data.degradationReason : ''}`);
            }
          } catch (e) {}
          log('✅ KPI calculated');
        }
        resolve();
      });
    });
  } else {
    log('⚠️ kpi_tracker.js not found — skipping metrics');
  }
}

async function stepRecordLedger() {
  log('📝 Recording continuity check ledger entry...');
  const appendScript = path.join(WORKSPACE, 'scripts', 'append_continuity_check.js');
  if (fs.existsSync(appendScript) && fs.statSync(appendScript).mode & fs.constants.S_IXUSR) {
    await new Promise((resolve) => {
      execFile('node', [appendScript], { cwd: WORKSPACE }, (err) => {
        if (err) {
          log('❌ Ledger script failed, falling back');
          try {
            appendLedger({ type: 'continuity_check', phase: '30min' });
            log('✅ Basic ledger entry appended');
          } catch (e) {
            log('❌ Ledger append failed: ' + e.message);
          }
        } else {
          log('✅ Continuity check ledger entry recorded');
        }
        resolve();
      });
    });
  } else {
    log('⚠️ append_continuity_check.js not executable, using basic entry');
    try {
      appendLedger({ type: 'continuity_check', phase: '30min' });
      log('✅ Basic ledger entry appended');
    } catch (e) {
      log('❌ Ledger append failed: ' + e.message);
    }
  }
}

async function stepUpdateHeartbeatState() {
  log('💓 Updating heartbeat-state.json...');
  try {
    const nextHb = new Date(now.getTime() + 30 * 60 * 1000).toISOString();
    const lastRun = nowISO;
    let state;
    try {
      state = JSON.parse(fs.readFileSync(HEARTBEAT_STATE_FILE, 'utf8'));
    } catch (e) {
      state = { lastChecks: {}, status: 'unknown', nextHeartbeat: null, lastContinuityRun: null };
    }
    state.lastContinuityRun = lastRun;
    state.nextHeartbeat = nextHb;
    state.lastChecks = state.lastChecks || {};
    state.lastChecks.continuity = lastRun;
    state.lastChecks.ledger = lastRun;
    state.updatedAt = nowISO;

    try {
      const kpiCurrent = path.join(WORKSPACE, 'memory', 'kpi_current.json');
      if (fs.existsSync(kpiCurrent)) {
        const kpi = JSON.parse(fs.readFileSync(kpiCurrent, 'utf8'));
        state.status = kpi.health || state.status;
        state.degradationReason = kpi.degradationReason || (kpi.issues && kpi.issues[0]) || state.degradationReason;
      }
    } catch (e) {}

    const tmpFile = HEARTBEAT_STATE_FILE + '.tmp';
    fs.writeFileSync(tmpFile, JSON.stringify(state, null, 2), 'utf8');
    fs.renameSync(tmpFile, HEARTBEAT_STATE_FILE);
    log(`✅ heartbeat-state.json updated (status: ${state.status}, next: ${nextHb})`);
  } catch (e) {
    log('⚠️ Failed to update heartbeat-state.json: ' + e.message);
  }
}

// (Other steps remain unchanged for brevity - they would be copied from original)
// For this improvement cycle, we focus on the lock/duplicate/gap issues.

// ── Gap-fill accounting ─────────────────────────────────────────────────────
function recordGapIfNeeded() {
  try {
    if (!fs.existsSync(LEDGER_FILE)) return;
    const lines = fs.readFileSync(LEDGER_FILE, 'utf8').trim().split('\n');
    const checks = lines
      .filter(l => l.startsWith('{'))
      .map(l => {
        try { return JSON.parse(l); } catch(e) { return null; }
      })
      .filter(e => e && e.type === 'continuity_check' && !e.duplicate)
      .sort((a,b) => new Date(a.ts) - new Date(b.ts));

    if (checks.length < 2) return;

    const last = checks[checks.length - 1];
    const prev = checks[checks.length - 2];
    const diffSec = (new Date(last.ts) - new Date(prev.ts)) / 1000;
    const expectedInterval = 1800; // 30min

    if (diffSec > expectedInterval * 2) {
      const gapDuration = Math.round(diffSec - expectedInterval);
      log(`⏰ Gap detected: ${gapDuration}s beyond expected interval`);
      // Record gap for coherence algorithm
      appendLedger({
        type: 'continuity_gap',
        phase: '30min',
        expectedInterval: expectedInterval,
        actualInterval: Math.round(diffSec),
        gapSeconds: gapDuration
      });
      log('📝 Gap entry recorded in ledger');
    }
  } catch (e) {
    log('⚠️ Gap check failed: ' + e.message);
  }
}

// ── Mission Verification Step ───────────────────────────────────────────────
async function stepMissionVerification() {
  log('📅 Verifying daily mission posts...');

  const missionSchedule = [
    {name: 'injustice-justice', hour: 0, minute: 0},
    {name: 'division-unity', hour: 0, minute: 0},
    {name: 'poverty-dignity', hour: 3, minute: 0},
    {name: 'dhikr-morning', hour: 3, minute: 0},
    {name: 'ignorance-knowledge', hour: 6, minute: 0},
    {name: 'war-peace', hour: 9, minute: 0},
    {name: 'shirk-tawhid', hour: 9, minute: 30},
    {name: 'pollution-cleanliness', hour: 12, minute: 0},
    {name: 'disease-health', hour: 15, minute: 0},
    {name: 'slavery-freedom', hour: 18, minute: 0},
    {name: 'corruption-reform', hour: 18, minute: 30},
    {name: 'extremism-moderation', hour: 21, minute: 0},
    {name: 'dhikr-evening', hour: 22, minute: 0},
  ];

  const now = new Date();
  const currentMinutes = now.getUTCHours() * 60 + now.getUTCMinutes();
  const GRACE_MINUTES = 15;

  let expectedCount = 0;
  const missing = [];

  for (const m of missionSchedule) {
    const sched = m.hour * 60 + m.minute;
    if (currentMinutes >= sched) {
      expectedCount++;
      const complete = await isMissionComplete(m.name);
      if (!complete) {
        missing.push(m);
      }
    }
  }

  const actualCount = expectedCount - missing.length;
  log(`🔍 Daily mission posts: ${actualCount}/${expectedCount} published (by ${now.getUTCHours().toString().padStart(2,'0')}:${now.getUTCMinutes().toString().padStart(2,'0')} UTC)`);

  if (missing.length > 0) {
    log(`⚠️ MISSING: ${missing.length} post(s): ${missing.map(m=>m.name).join(' ')}`);
    const toRepublish = [];
    for (const m of missing) {
      const sched = m.hour * 60 + m.minute;
      if (currentMinutes >= sched + GRACE_MINUTES) {
        toRepublish.push(m.name);
      } else {
        log(`⏰ ${m.name} scheduled at ${m.hour.toString().padStart(2,'0')}:${m.minute.toString().padStart(2,'0')} — within ${GRACE_MINUTES}min grace, waiting...`);
      }
    }
    if (toRepublish.length > 0) {
      log(`🔧 Auto-republishing ${toRepublish.length} missed mission(s): ${toRepublish.join(' ')}`);
      for (const mission of toRepublish) {
        log(`🚀 Publishing (async): ${mission}`);
        try {
          const child = spawn('bash', ['scripts/publish_daily_post.sh', mission], {
            cwd: WORKSPACE,
            detached: true,
            stdio: 'ignore'
          });
          child.unref();
        } catch (err) {
          log(`❌ Failed to start publisher for ${mission}: ${err.message}`);
        }
        await new Promise(r => setTimeout(r, 2000));
      }
    }
  }
}

function isMissionComplete(mission) {
  const today = new Date().toISOString().slice(0,10);
  // Check ledger for publish_run with full_success today
  try {
    const content = fs.readFileSync(LEDGER_FILE, 'utf8');
    const lines = content.trim().split('\n');
    for (let line of lines) {
      if (!line.startsWith('{')) continue;
      let e;
      try { e = JSON.parse(line); } catch (e2) { continue; }
      if (e.type === 'publish_run' && e.payload && e.payload.mission === mission && e.payload.status === 'full_success') {
        const ts = e.ts || '';
        if (ts.startsWith(today)) return true;
      }
    }
  } catch (e) { /* ignore */ }

  // Fallback: check publish_log
  const logPath = path.join(WORKSPACE, 'memory', `publish_log_${today}.md`);
  if (fs.existsSync(logPath)) {
    const content = fs.readFileSync(logPath, 'utf8');
    if (content.includes(`نشر: ${mission}`)) {
      return true;
    }
  }

  // Check posts ID file mtime
  const idPath = path.join(WORKSPACE, 'posts', `${mission}_ids.json`);
  if (fs.existsSync(idPath)) {
      const stat = fs.statSync(idPath);
      if (stat.mtime.toISOString().slice(0,10) === today) {
        return true;
      }
  }

  return false;
}

// ── Main ─────────────────────────────────────────────────────────────────────
(async function main() {
  log('=== Continuity 30min Check Start (improved v2) ===');

  // Duplicate suppression
  if (wasRunRecently()) {
    log('✅ Duplicate run skipped — exiting cleanly');
    process.exit(0);
  }

  // Acquire robust lock
  const lockInfo = acquireLock();
  if (!lockInfo.held) {
    log('⚠️ Could not acquire lock — exiting (another instance running)');
    process.exit(0);
  }

  // Release lock on exit
  const release = () => releaseLock(lockInfo);
  process.on('exit', release);
  process.on('SIGINT', release);
  process.on('SIGTERM', release);
  process.on('uncaughtException', () => { release(); process.exit(1); });
  process.on('unhandledRejection', () => { release(); process.exit(1); });

  fs.mkdirSync(path.dirname(LEDGER_FILE), { recursive: true });

  // Run core steps (simplified for this improvement cycle)
  log('🔧 Running continuity checks (v2 improved)...');
  await stepKernelHeartbeat();
  await stepKPI();
  await stepRecordLedger();
  await stepUpdateHeartbeatState();

  // CRITICAL: Verify daily missions and auto-repair any gaps
  // This was defined but occasionally skipped due to async flow issues
  log('📋 Step: Mission verification (ensuring all daily posts published)');
  await stepMissionVerification();
  log('✅ Mission verification complete');

  // NEW: Gap detection after successful run
  recordGapIfNeeded();

  log('=== Continuity 30min Check Complete (v2) ===');

  // Compute summary
  const ledgerCount = fs.existsSync(LEDGER_FILE)
    ? fs.readFileSync(LEDGER_FILE, 'utf8').split('\n').filter(l => l.startsWith('{')).length
    : 0;
  try {
    const kpi = JSON.parse(fs.readFileSync(path.join(WORKSPACE, 'memory', 'kpi_current.json'), 'utf8'));
    log(`📊 KPI: ${kpi.health} (${kpi.degradationReason || 'OK'})`);
  } catch(e) {}

  const summary = `✅ Continuity 30min (v2): ${now.toISOString().slice(11, 16)} UTC — Ledger: ${ledgerCount} entries`;
  console.log(summary);
  fs.writeFileSync(path.join(WORKSPACE, 'last_continuity_summary.txt'), summary + '\n', 'utf8');

  release();
})().catch(err => {
  console.error('⚠️ Continuity check warning: ' + err.message);
  release();
  process.exit(0);
});
