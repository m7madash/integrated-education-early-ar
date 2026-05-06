#!/usr/bin/env node
/**
 * continuity_work.js — Node.js implementation of continuity_work.sh
 * Exec-safe replacement (no shell operators, no $(...), no bash)
 *
 * Runs every 2 hours as part of continuity-improvement cron.
 * Performs system review, sync check, backup verification, improvement logging.
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const WORKSPACE = '/root/.openclaw/workspace';
const LOG_FILE = path.join(WORKSPACE, 'memory', `continuity_work_${new Date().toISOString().slice(0,10)}.md`);
const LEDGER_FILE = path.join(WORKSPACE, 'memory', 'ledger.jsonl');

function log(message) {
  const now = new Date();
  const timestamp = now.toISOString().replace('T', ' ').slice(0, 19);
  const line = `[${timestamp}] ${message}`;
  console.log(line);
  // Append to log file
  try {
    fs.appendFileSync(LOG_FILE, line + '\n', 'utf8');
  } catch (e) {
    // ignore
  }
}

function appendLedger(type, payload) {
  const ts = new Date().toISOString().replace('Z', '.000Z');
  const entry = { ts, type, payload };
  fs.appendFileSync(LEDGER_FILE, JSON.stringify(entry) + '\n', 'utf8');
}

// Start
log('=== Continuity Work: improvement cycle ===');
appendLedger('continuity_work_start', { phase: 'improvement_cycle' });

// 1. Weekly review trigger (if Sunday)
const dayOfWeek = parseInt(new Date().getUTCDay()); // 0 = Sunday, 6 = Saturday
if (dayOfWeek === 0) { // Sunday
  log('🔄 Sunday: weekly review required');
  log('📌 Actions: update MEMORY.md, review missions, update cron if needed');
} else {
  log(`📅 Day ${dayOfWeek} — weekly review not due today`);
}

// 2. Project sync (Abdullah projects ↔ m7mad-ai-work)
log('🔄 Checking project sync status...');
const abdullahDir = '/root/Abdullah_projects';
const m7madDir = '/root/m7mad-ai-work';
let syncStatus = 'unknown';
if (fs.existsSync(abdullahDir) && fs.existsSync(m7madDir)) {
  log('✅ Both project directories exist. sync would: identify shared dependencies, resolve conflicts, align priorities.');
  // Check if they are git repos
  try {
    const abdullahGit = path.join(abdullahDir, '.git');
    const m7madGit = path.join(m7madDir, '.git');
    if (fs.existsSync(abdullahGit) && fs.existsSync(m7madGit)) {
      log('✅ Both are git repositories — ready for sync');
    } else {
      log('⚠️ One or both directories are not git repos');
    }
  } catch (e) {
    log('⚠️ Could not verify git status: ' + e.message);
  }
} else {
  log('⚠️ One or more project directories missing');
  if (!fs.existsSync(abdullahDir)) log(`   — ${abdullahDir} not found`);
  if (!fs.existsSync(m7madDir)) log(`   — ${m7madDir} not found`);
}

// 3. Backup verification
log('🔄 Verifying backups...');
try {
  const backupsDir = path.join(WORKSPACE, 'backups');
  if (fs.existsSync(backupsDir)) {
    const backupFiles = fs.readdirSync(backupsDir)
      .filter(f => f.startsWith('backup_') && f.endsWith('.tar.gz'))
      .sort()
      .reverse();
    if (backupFiles.length > 0) {
      const latest = backupFiles[0];
      const latestPath = path.join(backupsDir, latest);
      const stats = fs.statSync(latestPath);
      const ageHours = Math.floor((Date.now() - stats.mtimeMs) / (1000 * 60 * 60));
      if (ageHours < 48) {
        log(`✅ Latest backup: ${latest} (${ageHours}h old)`);
      } else {
        log(`⚠️ Latest backup is ${ageHours}h old — backup may have failed`);
      }
    } else {
      log('⚠️ No backup files found in backups/ directory');
    }
  } else {
    log('⚠️ backups/ directory does not exist');
  }
} catch (e) {
  log('⚠️ Backup check error: ' + e.message);
}

// 4. Improvement log — scan recent ledger for notable events
log('🔄 Logging improvements from recent activity...');
try {
  const lines = fs.readFileSync(LEDGER_FILE, 'utf8').trim().split('\n');
  const recent = lines.slice(-100); // last 100 entries
  let improvements = [];
  recent.forEach(line => {
    try {
      const e = JSON.parse(line);
      if (e.type === 'continuity_improvement') {
        improvements.push(e);
      }
    } catch (err) { /* ignore */ }
  });
  if (improvements.length > 0) {
    log(`📈 Found ${improvements.length} continuity_improvement entries in recent ledger`);
    // Could summarize here
  } else {
    log('ℹ️ No recent continuity_improvement entries');
  }
} catch (e) {
  log('⚠️ Could not scan ledger: ' + e.message);
}

// 4b. Watchdog: Detect missed continuity_30min checks and trigger recovery
log('👁️ Watchdog: checking continuity_30min job health...');
try {
  const ledgerContent = fs.readFileSync(LEDGER_FILE, 'utf8');
  const entries = ledgerContent.trim().split('\n').filter(l => l.trim());
  let lastCheckTime = null;
  // Scan from end backwards for last non-duplicate continuity_check
  for (let i = entries.length - 1; i >= 0; i--) {
    try {
      const entry = JSON.parse(entries[i]);
      if (entry.type === 'continuity_check' && !entry.duplicate) {
        lastCheckTime = new Date(entry.ts);
        break;
      }
    } catch(e) {}
  }
  if (lastCheckTime) {
    const now = new Date();
    const minutesSince = Math.floor((now - lastCheckTime) / (1000 * 60));
    log(`⏱️ Last continuity_check: ${minutesSince} minutes ago`);
    if (minutesSince > 60) {
      log('⚠️ WATCHDOG ALERT: continuity_30min_check missed multiple runs!');
      log('🚀 Triggering recovery continuity check (spawning runner)...');
      const runnerPath = path.join(WORKSPACE, 'scripts', 'continuity_runner_v2.js');
      const result = spawnSync('node', [runnerPath], { cwd: WORKSPACE, encoding: 'utf8', timeout: 300000 }); // 5min timeout
      if (result.status === 0) {
        log('✅ Recovery continuity check completed successfully');
        // Also record in ledger
        appendLedger('watchdog_recovery', { triggered: true, reason: 'missed_runs', minutesSince });
      } else {
        log('❌ Recovery continuity check failed (exit ' + result.status + ')');
        if (result.stderr) log('stderr: ' + result.stderr.slice(0,200));
      }
    } else {
      log('✅ Continuity_30min is within acceptable window');
    }
  } else {
    log('⚠️ No continuity_check entries found — system may be just starting');
  }
} catch (e) {
  log('⚠️ Watchdog check error: ' + e.message);
}

// 5. System health check
log('🔄 System health check...');
try {
  // Disk space
  const df = spawnSync('df', ['-h', WORKSPACE], { encoding: 'utf8' });
  if (df.status === 0) {
    const output = df.stdout.trim().split('\n')[1];
    const parts = output.split(/\s+/);
    const usage = parts[4] || 'unknown';
    log(`💽 Disk usage: ${usage} (${parts[3]} used of ${parts[2]})`);
    if (usage.includes('%')) {
      const pct = parseInt(usage);
      if (pct > 90) {
        log('⚠️ Disk usage high (>90%) — consider cleanup');
      } else {
        log('✅ Disk space adequate');
      }
    }
  } else {
    log('⚠️ df command failed');
  }

  // Cron status — check if continuity-30min job is enabled
  try {
    const cronJobs = JSON.parse(fs.readFileSync('/root/.openclaw/cron/jobs.json', 'utf8'));
    const continuityJobs = cronJobs.jobs.filter(j => j.name.includes('continuity'));
    log(`⏰ Cron jobs (continuity): ${continuityJobs.length} found`);
    continuityJobs.forEach(j => {
      const status = j.enabled ? '✅ enabled' : '❌ disabled';
      log(`   — ${j.name} [${status}] schedule: ${j.schedule.expr}`);
    });
  } catch (e) {
    log('⚠️ Could not read cron jobs: ' + e.message);
  }

  // Connectivity: ping the gateway
  try {
    const ping = spawnSync('curl', ['-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://127.0.0.1:3001/status'], { encoding: 'utf8', timeout: 5000 });
    if (ping.status === 0 && ping.stdout.trim() === '200') {
      log('✅ Gateway (OpenClaw) reachable on localhost:3001');
    } else {
      log('⚠️ Gateway check returned: ' + (ping.stdout || 'no response'));
    }
  } catch (e) {
    log('⚠️ Gateway connectivity check failed (gateway may be down): ' + e.message);
  }

  // Memory files check
  const today = new Date().toISOString().slice(0,10);
  const memFile = path.join(WORKSPACE, 'memory', `${today}.md`);
  try {
    if (fs.existsSync(memFile)) {
      const stats = fs.statSync(memFile);
      log(`✅ Memory file for today (${today}) exists — ${stats.size} bytes`);
    } else {
      log('⚠️ No memory file for today yet');
    }
  } catch (e) {
    log('⚠️ Memory file check failed: ' + e.message);
  }

} catch (e) {
  log('⚠️ Health check encountered error: ' + e.message);
}

// Completion
log('✅ Continuity work cycle complete.');
appendLedger('continuity_work', { phase: 'improvement_cycle', status: 'completed' });

// Minimal output for cron
console.log('');
console.log(`✅ Continuity-improvement work: review, sync, backup, health check complete.`);
console.log(`   Log: ${LOG_FILE}`);
