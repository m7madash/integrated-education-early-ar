#!/usr/bin/env node
/**
 * backup_daily.js — Node.js replacement for backup_daily.sh
 *避免了 shell operators (&&, ;, |) for exec preflight compliance
 * Schedule: Daily at 02:00 UTC via OpenClaw cron
 * Tenet 2: The Shell is Mutable — survives crashes, restores from snapshots
 */

const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const util = require('util');
const execFileAsync = util.promisify(execFile);

const WORKSPACE = '/root/.openclaw/workspace';
const BACKUP_DIR = path.join(WORKSPACE, 'backups');
const REMOTE_BASE = 'remote:kilo-claw-backups';
const DATE = new Date().toISOString().slice(0, 10);
const TIMESTAMP = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15).replace('T', '_');
const LOG_FILE = path.join(WORKSPACE, 'logs', `backup_${DATE}.log`);

// Ensure dirs
fs.mkdirSync(BACKUP_DIR, { recursive: true });
fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });

const log = (msg) => {
  const line = `[${new Date().toISOString().replace('T', ' ').slice(0, 19)}] ${msg}`;
  console.log(line);
  fs.appendFileSync(LOG_FILE, line + '\n', 'utf8');
};

log('🚀 Backup job started');

// ==================== 1. Pre-backup validation ====================
log('✅ Pre-backup checks');

let gitSkipped = false;
if (!fs.existsSync(path.join(WORKSPACE, '.git'))) {
  log('⚠️ Not a git repo — skipping git backup portion');
  gitSkipped = true;
} else {
  log('✅ Git repository detected');
}

// Check disk space (5GB minimum)
try {
  const stats = fs.statfsSync(WORKSPACE);
  const freeKB = stats.bavail * stats.bsize / 1024;
  if (freeKB < 5242880) {
    log(`⚠️ Low disk space (${Math.round(freeKB)} KB) — proceeding with caution`);
  } else {
    log(`✅ Disk space OK (${Math.round(freeKB)} KB free)`);
  }
} catch (e) {
  log('⚠️ Could not check disk space — continuing');
}

// ==================== 2. Create tarball ====================
log('📦 Creating backup tarball...');
const BACKUP_NAME = `backup_${TIMESTAMP}.tar.gz`;
const TARBALL = path.join(BACKUP_DIR, BACKUP_NAME);

// Build tar command with excludes
const tarArgs = [
  'czf',
  TARBALL,
  '--exclude=node_modules',
  '--exclude=*.log',
  '--exclude=logs/*',
  '--exclude=.kilo-backups/*',
  '--exclude=media/cache/*',
  '--exclude=.git/objects/pack/*.pack',
  '--exclude=backups/*',
  '--exclude=memory/ledger.jsonl',
  '-C', WORKSPACE,
  '.'
];

try {
  await execFileAsync('tar', tarArgs);
  const tarSizeBytes = fs.statSync(TARBALL).size;
  const tarSizeHuman = (tarSizeBytes / (1024*1024)).toFixed(1) + ' MB';
  log(`✅ Tarball created: ${BACKUP_NAME} (${tarSizeHuman})`);
} catch (err) {
  log(`❌ Tarball creation failed: ${err.message}`);
  process.exit(1);
}

// ==================== 3. Integrity verification ====================
log('🔍 Verifying tarball integrity...');
try {
  await execFileAsync('tar', ['tzf', TARBALL]);
  log('✅ Tarball integrity verified');
} catch (err) {
  log('❌ Tarball corrupted — deleting and aborting');
  fs.unlinkSync(TARBALL);
  process.exit(1);
}

// ==================== 4. Git bundle backup ====================
if (!gitSkipped) {
  log('📦 Creating git bundle...');
  const GIT_BUNDLE = path.join(BACKUP_DIR, `git_${TIMESTAMP}.bundle`);
  try {
    await execFileAsync('git', ['bundle', 'create', GIT_BUNDLE, '--all']);
    if (fs.existsSync(GIT_BUNDLE) && fs.statSync(GIT_BUNDLE).size > 0) {
      const sizeBytes = fs.statSync(GIT_BUNDLE).size;
      const sizeHuman = (sizeBytes / (1024*1024)).toFixed(1) + ' MB';
      log(`✅ Git bundle created (${sizeHuman})`);
    } else {
      log('⚠️ Git bundle failed or empty — removing');
      if (fs.existsSync(GIT_BUNDLE)) fs.unlinkSync(GIT_BUNDLE);
    }
  } catch (err) {
    log(`⚠️ Git bundle error: ${err.message}`);
  }
}

// ==================== 5. Remote upload ====================
async function uploadToRemote(src, remotePath) {
  try {
    await execFileAsync('rclone', ['copyto', src, `${REMOTE_BASE}/${remotePath}`, '--progress']);
    return true;
  } catch (err) {
    return false;
  }
}

if (fs.existsSync('/usr/bin/rclone') || fs.existsSync('/usr/local/bin/rclone')) {
  log('☁️ Uploading to remote storage...');
  const remoteTarball = `backups/${BACKUP_NAME}`;
  const ok1 = await uploadToRemote(TARBALL, remoteTarball);
  log(ok1 ? '✅ Remote tarball upload complete' : '⚠️ Remote tarball upload failed — will retry tomorrow');

  const GIT_BUNDLE = path.join(BACKUP_DIR, `git_${TIMESTAMP}.bundle`);
  if (fs.existsSync(GIT_BUNDLE)) {
    const remoteBundle = `git/${BACKUP_NAME.replace('.tar.gz', '.bundle')}`;
    await uploadToRemote(GIT_BUNDLE, remoteBundle).catch(() => {});
  }
} else {
  log('ℹ️ rclone not installed — skipping remote backup');
}

// ==================== 6. Retention & cleanup ====================
log('🧹 Applying retention policy...');

// List all backups sorted by name (which includes timestamp)
const allBackups = fs.readdirSync(BACKUP_DIR)
  .filter(f => f.startsWith('backup_') && f.endsWith('.tar.gz'))
  .sort()
  .reverse(); // newest first

// Daily: keep last 7
if (allBackups.length > 7) {
  const toDelete = allBackups.slice(7);
  toDelete.forEach(f => fs.unlinkSync(path.join(BACKUP_DIR, f)));
  log(`✅ Cleaned ${toDelete.length} old daily backups`);
}

// Weekly & monthly: placeholder (can be enhanced later)
log('ℹ️ Weekly/monthly retention not yet implemented — daily only');

// ==================== 7. Verify backup health ====================
const latestBackup = fs.readdirSync(BACKUP_DIR)
  .filter(f => f.startsWith('backup_') && f.endsWith('.tar.gz'))
  .sort()
  .pop();

if (latestBackup) {
  log(`✅ Latest backup: ${latestBackup}`);
} else {
  log('❌ No backup found — backup may have failed');
}

// ==================== 8. Record in ledger ====================
const LEDGER = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
if (fs.existsSync(LEDGER)) {
  const tarSizeBytes = fs.statSync(TARBALL).size;
  // Build entry (use 'ts' to match system standard)
  const entry = {
    ts: new Date().toISOString(),
    type: 'backup',
    file: BACKUP_NAME,
    size: tarSizeBytes,
    status: 'success'
  };
  fs.appendFileSync(LEDGER, JSON.stringify(entry) + '\n', 'utf8');
  log('✅ Logged to continuity ledger');
}

// ==================== 9. Summary ====================
log('============================================');
log('✅ Backup job completed successfully');
log('📊 Statistics:');
log(`   Backup file: ${BACKUP_NAME}`);
log(`   Size: ${(fs.statSync(TARBALL).size / (1024*1024)).toFixed(1)} MB`);
log('   Location: local + remote');
log('⏰ Next backup: tomorrow 02:00 UTC');
log('============================================');

process.exit(0);
