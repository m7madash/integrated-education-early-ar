#!/usr/bin/env node
/**
 * add_heartbeat_redundancy_job.js
 *
 * Adds a separate cron job to update heartbeat state independently
 * of the continuity runner. This provides redundancy: if the runner
 * fails, heartbeat state still gets refreshed every 30min.
 *
 * Schedule: 15,45 * * * * (offset from main runner which runs 0,30)
 */

const fs = require('fs');
const path = require('path');

const CRON_JOBS_FILE = '/root/.openclaw/cron/jobs.json';

function log(msg) { console.log(`[${new Date().toISOString().replace('T',' ').slice(0,19)}] ${msg}`); }

function main() {
  // Read current jobs
  let data;
  try {
    data = JSON.parse(fs.readFileSync(CRON_JOBS_FILE, 'utf8'));
  } catch(e) {
    log('❌ Cannot read cron jobs: ' + e.message);
    process.exit(1);
  }
  if (!data.jobs) data.jobs = [];

  // Check if already exists
  const exists = data.jobs.some(j => j.name === 'heartbeat-redundancy');
  if (exists) {
    log('✅ heartbeat-redundancy job already exists — skipping');
    process.exit(0);
  }

  // Generate a UUID v4-like id
  const uuid = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = Math.random()*16|0, v = c === 'x' ? r : (r&0x3|0x8);
    return v.toString(16);
  });
  const newId = uuid();

  const nowMs = Date.now();
  const newJob = {
    "id": newId,
    "name": "heartbeat-redundancy",
    "description": "Independent heartbeat state updater (redundant to continuity runner)",
    "enabled": true,
    "createdAtMs": nowMs,
    "schedule": {
      "kind": "cron",
      "expr": "15,45 * * * *"
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "payload": {
      "kind": "agentTurn",
      "message": "{\"type\":\"system\",\"action\":\"heartbeat_update\",\"script\":\"scripts/update_heartbeat_state.js\"}"
    },
    "agentId": "main",
    "delivery": { "mode": "none" },
    "state": {}
  };

  data.jobs.push(newJob);
  fs.writeFileSync(CRON_JOBS_FILE, JSON.stringify(data, null, 2), 'utf8');
  log(`✅ Added heartbeat-redundancy job (id=${newId})`);
  log(`   Schedule: 15,45 * * * * (offset from main runner)`);
  log('ℹ️ Cron will pick up change on next cycle or after gateway reload');
  process.exit(0);
}

main();
