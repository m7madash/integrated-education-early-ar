#!/usr/bin/env node
/**
 * cron_exec.js — Mission runner used by cron systemEvent in main session
 * Usage: node cron_exec.js <mission-id> [--agent <name>]
 *
 * Supports all mission types:
 *   combined    → combined_publisher.js <id>
 *   education   → combined_publisher.js <id>
 *   biweekly    → generate + publish lesson
 *   istiqamah   → isitqamah engine + publish
 *   engagement  → engagement_reply.py
 *   github-sync → sync_edu_to_github.js
 *
 * All output logged to ledger, stdout for cron delivery.
 */
const { execSync } = require('child_process');
const BASE = '/root/.openclaw/workspace';
const LEDGER = `${BASE}/memory/ledger.jsonl`;

function ts() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
}
function ledger(type, payload) {
  const line = JSON.stringify({ ts: ts(), type, ...payload });
  require('fs').appendFileSync(LEDGER, line + '\n');
}

const RUNNERS = {
  runCombined(id) {
    const p = execSync(`node scripts/combined_publisher.js ${id}`, {
      encoding: 'utf8', timeout: 90000, cwd: BASE
    });
    const m = p.match(/(full_success|partial_success|ok|failed)/i);
    return { ok: !!m, run: 'combined', detail: m ? m[1] : 'unknown' };
  },
  runBiweekly() {
    const p = execSync('node scripts/generate_biweekly_lesson.js', {
      encoding: 'utf8', timeout: 60000, cwd: BASE
    });
    return { ok: true, run: 'biweekly', detail: 'generated' };
  },
  runIstiqamah() {
    const p = execSync('node scripts/istiqamah_engine.js', {
      encoding: 'utf8', timeout: 60000, cwd: BASE
    });
    return { ok: true, run: 'istiqamah', detail: 'scanned' };
  },
  runEngagement() {
    const p = execSync('python3 scripts/engagement_reply.py', {
      encoding: 'utf8', timeout: 60000, cwd: BASE
    });
    return { ok: true, run: 'engagement', detail: 'scanned' };
  },
  runGithubSync() {
    const p = execSync('node scripts/sync_edu_to_github.js', {
      encoding: 'utf8', timeout: 120000, cwd: BASE
    });
    return { ok: true, run: 'github-sync', detail: 'synced' };
  },
};

function main() {
  const [, , missionId, ...extra] = process.argv;
  if (!missionId) {
    console.error('Usage: node cron_exec.js <mission-id>');
    process.exit(1);
  }

  ledger('cron_exec_start', { mission: missionId });

  // Determine runner
  let runner = null;
  if (missionId === 'istighfar-reminder'
      || missionId === 'istiqamah-dhikr-reminder') {
    runner = RUNNERS.runIstiqamah;
  } else if (missionId === 'engagement-reply-scan'
             || missionId === 'engagement-scan') {
    runner = RUNNERS.runEngagement;
  } else if (missionId === 'github-sync'
             || missionId === 'edu-github-sync') {
    runner = RUNNERS.runGithubSync;
  } else if (missionId === 'biweekly-file-lesson'
             || missionId === 'file-lesson') {
    runner = RUNNERS.runBiweekly;
  } else {
    // Default: combined publisher
    runner = () => RUNNERS.runCombined(missionId);
  }

  try {
    const result = runner();
    ledger('cron_exec_end', { mission: missionId, ...result });
    console.log(`✅ [cron_exec] ${missionId}: ${result.detail}`);
    process.exit(0);
  } catch (e) {
    ledger('cron_exec_end', { mission: missionId, ok: false, err: String(e).slice(0, 200) });
    console.error(`❌ [cron_exec] ${missionId}: ${e.message.slice(0, 100)}`);
    process.exit(1);
  }
}

main();
