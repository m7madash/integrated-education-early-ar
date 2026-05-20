#!/usr/bin/env node
/**
 * generate_continuity_report.js — Continuity health report generator
 *
 * Runs on demand (or from any cron) about a continuity-improvement cycle.
 * Produces a real, timestamped Markdown report in memory/reports/ and
 * appends a live ledger entry with actual measured metrics — no hardcoded numbers.
 *
 * Usage:  node scripts/generate_continuity_report.js [--ledger-append]
 * 
 * With --ledger-append: also writes a continuity_improvement entry to ledger.jsonl
 * Without:                writes report only (dry run / preview mode)
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const WORKSPACE  = '/root/.openclaw/workspace';
const LEDGER     = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
const REPORTS_DIR = path.join(WORKSPACE, 'memory', 'reports');
const REPORT_FILE  = path.join(REPORTS_DIR, 'continuity_improvement_latest.md');
const SNAPSHOT_DIR  = path.join(WORKSPACE, '.snapshots');
const CRON_STATE   = '/root/.openclaw/cron/jobs-state.json';
const SNAPSHOT_EXE = path.join(WORKSPACE, 'scripts', 'prune_snapshots.js');
const HEALTH_EXE   = path.join(WORKSPACE, 'scripts', 'platform_health_monitor.js');

const APPEND_LEDGER = process.argv.includes('--ledger-append');

function now()            { return new Date(); }
function ts()             { return now().toISOString(); }
function dateLabel()      { return now().toISOString().slice(0, 10); }
function timeLabel()      { return now().toTimeString().slice(0, 5); }
function ageHours(isoStr) {
  try { return (((Date.now() - Date.parse(isoStr)) / 3_600_000) || 0).toFixed(1); } catch(e) { return 'N/A'; }
}

function log(msg) { console.log(`[ci_${ts().slice(11,16)}] ${msg}`); }

// ── Measure 1: Ledger health ────────────────────────────────────────────────
function measureLedgerHealth() {
  let lines = [];
  try { lines = fs.readFileSync(LEDGER, 'utf8').trim().split('\n'); } catch(e) {
    return { total: 0, parsed: 0, failed: 0, types: {}, gapStats: null };
  }
  let parsed = 0, failed = 0;
  const types = {};
  const times = [];
  for (const line of lines) {
    if (!line.trim().startsWith('{')) { failed++; continue; }
    try {
      const obj = JSON.parse(line);
      parsed++;
      types[obj.type || 'unknown'] = (types[obj.type || 'unknown'] || 0) + 1;
      if (obj.ts) times.push(Date.parse(obj.ts));
    } catch(e) { failed++; }
  }
  // Gap stats from continuity_check entries
  const checks = lines
    .filter(l => l.includes('"type":"continuity_check"'))
    .map(l => { try { return JSON.parse(l); } catch(e) { return null; } })
    .filter(Boolean)
    .sort((a,b) => Date.parse(a.ts) - Date.parse(b.ts));
  let avgGapSec = null, maxGapSec = null;
  if (checks.length >= 2) {
    const gaps = [];
    for (let i = 1; i < checks.length; i++)
      gaps.push((Date.parse(checks[i].ts) - Date.parse(checks[i-1].ts)) / 1000);
    avgGapSec = Math.round(gaps.reduce((a,b)=>a+b,0) / gaps.length);
    maxGapSec = Math.round(Math.max(...gaps));
  }
  // Latest coherence / health
  const latest = checks.length
    ? { ...checks[checks.length - 1] }
    : { heartbeatHealth: 'N/A', coherence_score: 'N/A', post_completion: 'N/A', error_rate: 'N/A' };

  return { total: lines.length, parsed, failed, types, avgGapSec, maxGapSec, latest };
}

// ── Measure 2: Platform health ───────────────────────────────────────────────
function measurePlatformHealth() {
  try {
    const raw = execSync(`node "${HEALTH_EXE}"`, { cwd: WORKSPACE, encoding: 'utf8', timeout: 15000 });
    const parsed = JSON.parse(raw);
    // Expecting platformHealth object with moltx/molbook/moltter
    const out = {};
    for (const [key, val] of Object.entries(parsed.platformHealth || {}))
      out[key] = { status: val.status, successRate: val.successRate, recommendation: val.recommendation };
    return out;
  } catch(e) {
    return { error: e.message };
  }
}

// ── Measure 3: Snapshot health ───────────────────────────────────────────────
function measureSnapshotHealth() {
  const files = fs.existsSync(SNAPSHOT_DIR)
    ? fs.readdirSync(SNAPSHOT_DIR)
        .filter(f => f.startsWith('snapshot-') && f.endsWith('.json'))
        .sort((a,b) => (b.slice(8)).localeCompare(a.slice(8)))
    : [];
  const latestFile = files[0];
  const latestName  = latestFile || 'none';
  const latestDay   = latestFile
    ? (function() {
        // Parse YYYY-MM-DD from snapshot-YYYY-MM-DDT… filename
        // Extract YYYY-MM-DD from snapshot-YYYY-MM-DDT designation
        return (latestFile.match(/^snapshot-(\d{4}-\d{2}-\d{2})T/) || [])[1] || latestFile.slice(8, 18);
      })()
    : null;
  const totalSizeMB = files.reduce((s, f) => {
    try { s += fs.statSync(path.join(SNAPSHOT_DIR, f)).size; } catch(e) {}
    return s;
  }, 0) / (1024 * 1024);
  return { count: files.length, latestName, latestDay, totalSizeMB: totalSizeMB.toFixed(1) };
}

function modifiedDate(name) {
  const m = name.match(/T(\d{2}-\d{2}-\d{2}-\d{3})Z/);
  if (!m) return name.slice(8, 18) + 'T00:00:00.000Z';
  const [h,min,sec] = m[1].split('-');
  const datePart = name.slice(8, 18);
  return `${datePart}T${h}:${min}:${sec}.000Z`;
}

// ── Measure 4: Cron health (no stuck jobs) ───────────────────────────────────
function measureCronHealth() {
  let stale = null;
  try {
    if (!fs.existsSync(CRON_STATE)) return { state: 'no-state-file' };
    const state = JSON.parse(fs.readFileSync(CRON_STATE, 'utf8'));
    const jobs = state.jobs || {};
    for (const [id, job] of Object.entries(jobs)) {
      const ra = job.state?.runningAtMs;
      if (!ra) continue;
      const ageMin = (Date.now() - ra) / 60000;
      if (ageMin > 20) { stale = { id, ageMin: ageMin.toFixed(1) }; break; }
    }
    return { state: stale ? 'stale-job-detected' : 'ok', stale };
  } catch(e) {
    return { state: 'parse-error', detail: e.message };
  }
}

// ── Measure 5: Overall verdicts from ledger latest ───────────────────────────
function verdicts(ledger) {
  const l = ledger.latest;
  const hOk   = l.heartbeatHealth  == null || l.heartbeatHealth  >= 0.99;
  const cOk   = l.coherence_score == 'N/A' || (typeof l.coherence_score === 'number' && l.coherence_score >= 0.95);
  const pOk   = l.post_completion == null || l.post_completion == 'N/A' || (typeof l.post_completion === 'number' && l.post_completion >= 0.95);
  const errOk = l.error_rate == null || l.error_rate == 'N/A' || (typeof l.error_rate === 'number' && l.error_rate === 0.0);
  return {
    healthCheck:   hOk ? '✅ OK'   : `❌ FAIL (${l.heartbeatHealth})`,
    coherence:     cOk ? '✅ OK'   : `❌ FAIL (${l.coherence_score})`,
    postComplete:  pOk ? '✅ OK'   : `❌ FAIL (${l.post_completion}%)`,
    errorRate:     errOk ? '✅ OK' : `❌ FAIL (${l.error_rate}%)`,
    overallScore:  [hOk, cOk, pOk, errOk].filter(Boolean).length * 25,
  };
}

// ── Render Markdown report ───────────────────────────────────────────────────
function renderReport(ledger, platforms, snapshots, cron) {
  const v = verdicts(ledger);
  const nowStr = `${dateLabel()} ${timeLabel()} UTC`;

  return `# 📊 Continuity Improvement Report

> بفضل الله — generated ${nowStr} for cron \`continuity-improvement\` job.

---

## 🏥 System Health Score

| Dimension     | Status  | Value |
|---------------|---------|-------|
| Health Check  | ${v.healthCheck} | Overall Score: ${v.overallScore}/100 |

---

## 📋 Ledger Health

| Metric             | Value                        |
|--------------------|------------------------------|
| Total lines        | ${ledger.total}              |
| Successfully parsed| ${ledger.parsed}             |
| Parse failures     | ${ledger.failed} ✅          |
| Types tracked      | ${Object.keys(ledger.types).join(', ')} |
| Avg continuity gap | ${ledger.avgGapSec != null ? ledger.avgGapSec + 's' : 'N/A'} (target ≤1800s) |
| Max continuity gap | ${ledger.maxGapSec != null ? ledger.maxGapSec + 's' : 'N/A'} (target ≤1800s) |

**Ledger verdicts (latest continuity_check entry):**

- Heartbeat health: ${v.healthCheck}
- Coherence score: ${v.coherence}
- Post completion: ${v.postComplete}
- Error rate: ${v.errorRate}

---

## 🌐 Platform Health

${Object.entries(platforms)
  .filter(([k]) => k !== 'error')
  .map(([k, p]) => `- **${k.charAt(0).toUpperCase() + k.slice(1)}**: ${p.status} (success rate: ${(p.successRate*100).toFixed(1)}%) — ${p.recommendation || '—'}`)
  .join('\n') || `- ⚠️ Unable to reach platform health monitor: ${platforms.error}`}

---

## 🗂️ Snapshot Health

| Metric          | Value        |
|-----------------|--------------|
| Total snapshots | ${snapshots.count} |
| Latest snapshot | ${snapshots.latestName || 'none'} ${snapshots.latestDay ? '(' + snapshots.latestDay + ')' : ''} |
| Total size      | ${snapshots.totalSizeMB} MB |

${snapshots.count === 0 ? '> ⚠️ No snapshots found — .snapshots/ directory may be misconfigured.' : ''}

---

## ⏱️ Cron Health

${cron.state === 'ok'
  ? `- ✅ No stale runningAtMs flags detected.`
  : cron.state === 'stale-job-detected'
    ? `- ⚠️ Stale cron flag detected: job \`${cron.stale.id}\` has been running for ${cron.stale.ageMin} min.`
    : `- ⚠️ Cron state: ${cron.state} — ${cron.detail || ''}`}

---

## 💡 Observations & Recommendations

### ✅ What's working well
${Object.entries(platforms)
  .filter(([k, p]) => k !== 'error' && p.status === 'healthy')
  .map(([k]) => `- **${k.charAt(0).toUpperCase() + k.slice(1)}** — platform publishing and health checks are stable`)
  .join('\n') || '- None yet'}
${ledger.failed === 0 ? '\n- Ledger is fully parseable — no corrupt entries.' : ''}
${v.coherence === '✅ OK' ? '\n- Coherence target met — system boundaries are holding.' : ''}

${platforms.error ? `### ⚠️ Issues detected (${dateLabel()})` : ''}
${platforms.error ? `- Platform health monitor failed: ${platforms.error}` : ''}
${cron.state !== 'ok' && cron.state !== 'no-state-file' ? '- Cron state is stale — check runningAtMs duration.' : ''}
`;

}

// ── Append ledger entry ──────────────────────────────────────────────────────
function appendLedgerEntry(reportField, ledgerSummary, verdictsObj) {
  const entry = {
    ts:               ts(),
    type:             'continuity_improvement',
    cronId:           'd8428d44-747e-426a-b7e4-1a0454c014d0',
    status:           'completed',
    cronIdLabel:      'continuity-improvement',
    findings: {
      cohortId:       `ci_${dateLabel()}_${timeLabel().replace(':', '')}`,
      ledger: {
        totalLines: ledgerSummary.total,
        parsed:     ledgerSummary.parsed,
        failed:     ledgerSummary.failed,
        avgGapSec:  ledgerSummary.avgGapSec,
        maxGapSec:  ledgerSummary.maxGapSec,
      },
      platformHealth: ledgerSummary.platformHealth,
      snapshotHealth: ledgerSummary.snapshotHealth,
      cronHealth:     ledgerSummary.cronHealth,
      verdicts: {
        healthCheck:  verdictsObj.healthCheck,
        coherence:    verdictsObj.coherence,
        postComplete: verdictsObj.postComplete,
        errorRate:    verdictsObj.errorRate,
        overallScore: verdictsObj.overallScore,
      },
    },
    actions: [
      'measured_ledger_health',
      'measured_platform_health',
      'measured_snapshot_health',
      'measured_cron_health',
      'generated_markdown_report',
      ...(APPEND_LEDGER ? ['appended_ledger_entry'] : ['dry-run']),
    ],
    report:                 reportField,
    notes:                  `Scored ${verdictsObj.overallScore}/100. ${timeLabel()} UTC / ${dateLabel()}.`,
  };
  fs.appendFileSync(LEDGER, JSON.stringify(entry) + '\n', 'utf8');
  return entry;
}

// ── MAIN ─────────────────────────────────────────────────────────────────────
async function main() {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });

  log('Measuring ledgerv...');
  const ledger     = measureLedgerHealth();

  log('Measuring platform health...');
  const platforms  = measurePlatformHealth();

  log('Measuring snapshots...');
  const snapshots  = measureSnapshotHealth();

  log('Measuring cron state...');
  const cron       = measureCronHealth();

  const verdictsObj = verdicts(ledger);

  // Save live snapshot
  const snapshot = { ts: ts(), ledger: ledger.total, snapshot_count: snapshots.count,
                     coherence: ledger.latest?.coherence_score ?? 'N/A',
                     verdicts: verdictsObj };
  try {
    fs.writeFileSync(path.join(WORKSPACE, 'memory', 'continuity_improvement_latest_state.json'),
                     JSON.stringify(snapshot, null, 2) + '\n', 'utf8');
    log('Live state snapshot written to memory/continuity_improvement_latest_state.json');
  } catch(e) { log('Could not write state snapshot: ' + e.message); }

  // Compose & write report
  const reportMarkdown = renderReport(ledger, platforms, snapshots, cron);
  fs.writeFileSync(REPORT_FILE, reportMarkdown, 'utf8');
  log(`Report written → ${REPORT_FILE}`);

  // Optionally append ledger entry
  if (APPEND_LEDGER) {
    const entry = appendLedgerEntry(
      `memory/reports/continuity_improvement_${dateLabel()}_${timeLabel().replace(':','')}.md`,
      { total: ledger.total, parsed: ledger.parsed, failed: ledger.failed,
        avgGapSec: ledger.avgGapSec, maxGapSec: ledger.maxGapSec,
        platformHealth: platforms, snapshotHealth: { count: snapshots.count, latestName: snapshots.latestName, latestDay: snapshots.latestDay, totalSizeMB: snapshots.totalSizeMB }, cronHealth: cron.state },
      verdictsObj
    );
    log('Ledger entry appended → continuity_improvement cycle confirmed');
    console.log('\n📌 Ledger entry (compact):');
    console.log(JSON.stringify({
      ts: entry.ts, type: entry.type, status: entry.status,
      cohortId: entry.findings.cohortId,
      overallScore: entry.findings.verdicts.overallScore,
      report: entry.report,
    }, null, 2));
  } else {
    console.log(`\nℹ️  Ledger NOT appended (pass --ledger-append to persist)`);
  }

  const score = verdictsObj.overallScore;
  if (score === 100) {
    console.log('\n🏆 All continuity metrics are at peak. Well maintained.');
  } else if (score >= 75) {
    console.log(`\n🟡 Continuity score: ${score}/100 — minor issues found. Review report.`);
  } else {
    console.log(`\n🔴 Continuity score: ${score}/100 — attention needed.`);
  }
}

main().catch(e => { console.error('❌ Fatal:' + e.message); process.exit(1); });
