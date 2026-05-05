#!/usr/bin/env node
/**
 * backup_runner.js — Exec-safe wrapper for backup_daily.sh
 *
 * This script invokes the existing backup_daily.sh as a child process,
 * allowing the cron job to use a single-binary node invocation that
 * complies with OpenClaw exec preflight validation.
 *
 * The backup logic remains in backup_daily.sh (bash); this wrapper
 * merely bridges the execution model.
 */

const { spawn } = require('child_process');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const BACKUP_SCRIPT = path.join(WORKSPACE, 'scripts', 'backup_daily.js');

// Execute backup script via bash
const child = spawn('bash', [BACKUP_SCRIPT], {
  cwd: WORKSPACE,
  stdio: 'inherit', // forward stdout/stderr so logs appear
  shell: false
});

child.on('error', (err) => {
  console.error('❌ Failed to start backup script:', err.message);
  process.exit(1);
});

child.on('close', (code) => {
  if (code === 0) {
    console.log('✅ Backup completed successfully');
    process.exit(0);
  } else {
    console.error(`❌ Backup exited with code ${code}`);
    process.exit(code || 1);
  }
});
