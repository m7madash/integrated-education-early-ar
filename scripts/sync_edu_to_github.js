#!/usr/bin/env node
/**
 * sync_edu_to_github.js
 * يدفع تحديثات education-system/ إلى GitHub repo
 * يعمل كل يوم أحد 23:30 UTC (قبل education-orchestrator بـ 10 دقائق)
 *
 * الاستخدام: node scripts/sync_edu_to_github.js
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const EDU_DIR = '/root/.openclaw/workspace/education-system';
const GITHUB_SUBMODULE = '/root/.openclaw/workspace/education-system-github';
const LEDGER = '/root/.openclaw/workspace/memory/ledger.jsonl';

function ts() { return new Date().toISOString().replace('T',' ').slice(0,19)+' UTC'; }
function ledger(entry) {
  fs.appendFileSync(LEDGER, JSON.stringify({ ts: ts(), type: 'github_sync', payload: entry })+'\n');
}

function main() {
  console.log(`🕌 GitHub Education Sync — ${ts()}`);

  // 1. Check edu-system files count
  const files = fs.readdirSync(EDU_DIR, { recursive: true });
  console.log(`📁 Source: ${files.length} files in ${EDU_DIR}`);

  // 2. Copy to submodule
  execSync(`cp -a ${EDU_DIR}/. ${GITHUB_SUBMODULE}/`, { stdio: 'pipe' });
  console.log(`📋 Copied to submodule: ${GITHUB_SUBMODULE}`);

  // 3. Check if anything changed
  const status = execSync('cd ' + GITHUB_SUBMODULE + ' && git status --short', { encoding: 'utf8' });
  if (!status.trim()) {
    console.log('✅ Nothing changed — GitHub already up to date');
    ledger({ action: 'sync', changed: false });
    return;
  }

  console.log('📝 Changes detected:');
  console.log(status.trim());

  // 4. Commit + push
  execSync('cd ' + GITHUB_SUBMODULE + ' && git add -A', { stdio: 'pipe' });
  const commitMsg = `sync: education-system update — ${ts()}`;
  execSync('cd ' + GITHUB_SUBMODULE + ' && git commit -m "' + commitMsg + '"', { stdio: 'pipe' });
  execSync('cd ' + GITHUB_SUBMODULE + ' && git push', { stdio: 'pipe' });

  console.log('✅ Pushed to GitHub');
  ledger({ action: 'sync', changed: true, files: files.length, commit: commitMsg });
  console.log('\n📝 Ledger written. Sync complete.');
}

main().catch(e => { console.error(e); process.exit(1); });
