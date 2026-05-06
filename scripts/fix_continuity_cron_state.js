#!/usr/bin/env node
/**
 * Fix stuck continuity-30min cron job state.
 *
 * The job was left in "running" state after a failed start at 02:40 UTC.
 * This clears the stale running flag and updates lastRun/nextRun to reflect
 * the successful manual run at 02:41:25 UTC.
 */

const fs = require('fs');
const path = require('path');

const STATE_FILE = '/root/.openclaw/cron/jobs-state.json';
const JOB_ID = 'ea19561d-f2c2-4716-9032-5053e9f65dc3';

// Actual manual run start timestamp from ledger
const LAST_RUN_MS = 1778035285491; // 2026-05-06T02:41:25.491Z
const INTERVAL_MS = 30 * 60 * 1000; // 30 minutes
const NEXT_RUN_MS = LAST_RUN_MS + INTERVAL_MS;
const NOW_MS = Date.now();

console.log('🔧 Fixing cron state for continuity-30min...');
console.log('  Last run (manual):', new Date(LAST_RUN_MS).toISOString());
console.log('  Next run:', new Date(NEXT_RUN_MS).toISOString());

let data = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
if (!data.jobs[JOB_ID]) {
  console.error('❌ Job not found in state:', JOB_ID);
  process.exit(1);
}

const jobState = data.jobs[JOB_ID].state;

// Preserve existing fields we want to keep
const preserved = {
  lastRunStatus: jobState.lastRunStatus || 'ok',
  lastStatus: jobState.lastStatus || 'ok',
  lastDurationMs: jobState.lastDurationMs || 30000,
  lastDeliveryStatus: jobState.lastDeliveryStatus || 'delivered',
  consecutiveErrors: jobState.consecutiveErrors || 0,
  lastDelivered: jobState.lastDelivered !== undefined ? jobState.lastDelivered : true
};

// Build updated state
const updatedState = {
  nextRunAtMs: NEXT_RUN_MS,
  lastRunAtMs: LAST_RUN_MS,
  lastRunStatus: preserved.lastRunStatus,
  lastStatus: preserved.lastStatus,
  lastDurationMs: preserved.lastDurationMs,
  lastDeliveryStatus: preserved.lastDeliveryStatus,
  consecutiveErrors: preserved.consecutiveErrors,
  lastDelivered: preserved.lastDelivered
  // Note: runningAtMs is omitted (cleared)
};

// Update the job state
data.jobs[JOB_ID].state = updatedState;
data.jobs[JOB_ID].updatedAtMs = NOW_MS;

// Write atomically
const tmp = STATE_FILE + '.tmp';
fs.writeFileSync(tmp, JSON.stringify(data, null, 2), 'utf8');
fs.renameSync(tmp, STATE_FILE);

console.log('✅ Cron state repaired.');
console.log('  Job status: running flag cleared, last/next times updated.');
console.log('  Scheduler should now queue next run at ~', new Date(NEXT_RUN_MS).toISOString());
