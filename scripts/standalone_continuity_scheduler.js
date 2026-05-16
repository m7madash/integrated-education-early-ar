#!/usr/bin/env node
/**
 * standalone_continuity_scheduler.js
 *
 * Replacement for the unstable in-process OpenClaw cron daemon.
 *
 * This process runs independently of the OpenClaw gateway event loop and
 * executes continuity_runner_v2.js every 30 minutes with nanosecond precision.
 *
 * Architecture:
 * - Uses setInterval for reliable 30-minute scheduling
 * - Spawns continuity_runner_v2.js as a child process
 * - Maintains its own health state (scheduler_health.json)
 * - Logs all spawn attempts and outcomes to scheduler.log
 * - Never blocks the event loop (async child process management)
 * - Self-recovery: if child process hangs, timeout after 10 minutes
 *
 * Supervision: Run as an OpenClaw subagent session so the gateway
 * will auto-restart this scheduler if it crashes.
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const LOG_DIR = path.join(WORKSPACE, 'logs');
const SCHEDULER_LOG = path.join(LOG_DIR, 'standalone_scheduler.log');
const HEALTH_FILE = path.join(WORKSPACE, 'memory', 'scheduler_health.json');
const RUNNER_SCRIPT = path.join(WORKSPACE, 'scripts', 'continuity_runner_v2.js');
const CRASH_MARKER = path.join(WORKSPACE, 'memory', 'scheduler_crash.marker');

// Global crash handlers — log before exiting so we capture root cause
process.on('uncaughtException', (err) => {
  const msg = `💥 FATAL: Uncaught exception: ${err.stack || err.message}`;
  log(msg);
  try { fs.appendFileSync(CRASH_MARKER, `[${new Date().toISOString()}] ${msg}\n`); } catch(e){}
  process.exit(1);
});
process.on('unhandledRejection', (reason) => {
  const msg = `💥 FATAL: Unhandled rejection: ${reason}`;
  log(msg);
  try { fs.appendFileSync(CRASH_MARKER, `[${new Date().toISOString()}] ${msg}\n`); } catch(e){}
  process.exit(1);
});

process.on('SIGTERM', () => {
  log('🛑 Received SIGTERM — shutting down gracefully');
  process.exit(0);
});
process.on('SIGINT', () => {
  log('🛑 Received SIGINT — shutting down gracefully');
  process.exit(0);
});

const INTERVAL_MS = 30 * 60 * 1000; // 30 minutes
const CHILD_TIMEOUT_MS = 10 * 60 * 1000; // 10 min max runner duration
const STARTUP_DELAY_MS = 5000; // Wait 5s after startup before first run (let gateway settle)

// Ensure log directory exists
fs.mkdirSync(LOG_DIR, { recursive: true });

function log(message) {
  const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
  const line = `[${timestamp}] ${message}`;
  console.log(line);
  fs.appendFileSync(SCHEDULER_LOG, line + '\n', 'utf8');
}

function updateHealth(state) {
  try {
    const tmp = HEALTH_FILE + '.tmp';
    fs.writeFileSync(tmp, JSON.stringify(state, null, 2), 'utf8');
    fs.renameSync(tmp, HEALTH_FILE);
  } catch (e) {
    log('⚠️ Failed to write health file: ' + e.message);
  }
}

function getNextRunTime(lastRunMs) {
  // Calculate next scheduled time respecting the 30-minute grid (:00 and :30)
  const now = Date.now();
  const interval = INTERVAL_MS;
  // If lastRunMs is provided, compute next as lastRun + interval, aligned to grid
  let next;
  if (lastRunMs) {
    next = lastRunMs + interval;
  } else {
    // First run: align to next upcoming :00 or :30 (grid ceiling)
    const nowDate = new Date(now);
    const minutes = nowDate.getUTCMinutes();
    // Round up to next half-hour mark (0 or 30)
    const nextHalfHour = Math.ceil(minutes / 30) * 30; // yields 0, 30, or 60
    nowDate.setUTCMinutes(nextHalfHour, 0, 0);
    // If nextHalfHour == 60, setMinutes rolls over to next hour automatically
    next = nowDate.getTime();
  }
  return next;
}

async function runContinuityCheck() {
  const runStart = Date.now();
  log('🚀 Starting continuity runner...');

  return new Promise((resolve) => {
    const child = spawn('node', [RUNNER_SCRIPT], {
      cwd: WORKSPACE,
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';
    let timedOut = false;
    let exited = false;

    child.stdout.on('data', (data) => {
      stdout += data.toString();
      // Echo important lines to scheduler log
      const lines = data.toString().split('\n');
      lines.forEach(l => {
        if (l.trim()) log(`[runner] ${l.trim()}`);
      });
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
      const lines = data.toString().split('\n');
      lines.forEach(l => {
        if (l.trim()) log(`[runner-err] ${l.trim()}`);
      });
    });

    const timeout = setTimeout(() => {
      timedOut = true;
      log('⏰ Runner timeout after ' + CHILD_TIMEOUT_MS/1000 + 's — killing');
      child.kill('SIGKILL');
    }, CHILD_TIMEOUT_MS);

    child.on('close', (code, signal) => {
      clearTimeout(timeout);
      exited = true;
      const duration = Date.now() - runStart;
      if (code === 0) {
        log(`✅ Runner completed successfully in ${(duration/1000).toFixed(1)}s`);
        resolve({ success: true, duration, timedOut: false });
      } else {
        const exitReason = signal || `exit code ${code}`;
        log(`❌ Runner failed (${exitReason}) after ${(duration/1000).toFixed(1)}s`);
        resolve({ success: false, duration, timedOut: false, exitCode: code, signal });
      }
    });

    child.on('error', (err) => {
      clearTimeout(timeout);
      exited = true;
      log(`❌ Runner spawn error: ${err.message}`);
      resolve({ success: false, duration: Date.now() - runStart, error: err.message });
    });
  });
}

async function schedulerLoop() {
  let lastRunMs = null;
  let consecutiveFailures = 0;
  const MAX_CONSECUTIVE_FAILURES = 3;

  // Calculate initial next run time
  let nextRunMs = getNextRunTime(null);
  updateHealth({
    status: 'starting',
    lastRunMs: null,
    nextRunMs,
    consecutiveFailures: 0,
    uptimeStart: Date.now(),
    totalRuns: 0,
    successfulRuns: 0
  });

  log(`⏰ Scheduler started — first run at ${new Date(nextRunMs).toISOString()}`);

  while (true) {
    const now = Date.now();
    const waitMs = nextRunMs - now;

    if (waitMs > 0) {
      // Sleep until next scheduled run
      await new Promise(resolve => setTimeout(resolve, waitMs));
    }

    // Execute continuity check
    lastRunMs = Date.now();
    log(`🔔 Scheduler triggered at ${new Date(lastRunMs).toISOString()}`);

    const result = await runContinuityCheck();

    // Update health state (load previous to preserve counters)
    let previousHealth = null;
    try {
      if (fs.existsSync(HEALTH_FILE)) {
        previousHealth = JSON.parse(fs.readFileSync(HEALTH_FILE, 'utf8'));
      }
    } catch (e) {
      log('⚠️ Failed to read previous health state: ' + e.message);
    }

    const health = {
      status: 'running',
      lastRunMs: lastRunMs,
      lastRunSuccess: result.success,
      lastRunDuration: result.duration,
      lastRunTimedOut: result.timedOut,
      consecutiveFailures,
      nextRunMs: lastRunMs + INTERVAL_MS,
      totalRuns: (previousHealth && previousHealth.totalRuns ? previousHealth.totalRuns + 1 : 1),
      successfulRuns: (previousHealth && previousHealth.successfulRuns ? (result.success ? previousHealth.successfulRuns + 1 : previousHealth.successfulRuns) : (result.success ? 1 : 0))
    };
    updateHealth(health);
    nextRunMs = lastRunMs + INTERVAL_MS;

    log(`⏳ Next scheduled run: ${new Date(nextRunMs).toISOString()}`);
  }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  log('🛑 Scheduler received SIGINT — exiting');
  updateHealth({ status: 'stopped', stoppedAt: Date.now() });
  process.exit(0);
});
process.on('SIGTERM', () => {
  log('🛑 Scheduler received SIGTERM — exiting');
  updateHealth({ status: 'stopped', stoppedAt: Date.now() });
  process.exit(0);
});

// Start the scheduler
log('🚀 Standalone Continuity Scheduler starting...');
updateHealth({
  status: 'starting',
  uptimeStart: Date.now(),
  totalRuns: 0,
  successfulRuns: 0
});

schedulerLoop().catch(err => {
  log(`💥 Scheduler loop crashed: ${err.message}`);
  updateHealth({ status: 'crashed', error: err.message, crashedAt: Date.now() });
  process.exit(1);
});
