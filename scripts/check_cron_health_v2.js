#!/usr/bin/env node
/**
 * check_cron_health_v2.js — Enhanced Cron Health Auditor
 *
 * Improvements over v1:
 * 1. Consecutive error detection (alert when >= 3)
 * 2. Missed run detection (should have fired but no successful run)
 * 3. Schedule drift detection (actual vs expected timing)
 * 4. Ledger-based reporting for continuity tracking
 *
 * Output: Human-readable summary + ledger entry
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CRON_JOBS_FILE = '/root/.openclaw/cron/jobs.json';
const CRON_STATE_FILE = '/root/.openclaw/cron/jobs-state.json';
const LEDGER_FILE = '/root/.openclaw/workspace/memory/ledger.jsonl';
const TOKEN_FILE = '/root/.openclaw/workspace/telegram/bot_token.txt';

function log(msg) { console.log(`[${new Date().toISOString().replace('T',' ').slice(0,19)}] ${msg}`); }
function ledger(entry) {
  try { fs.appendFileSync(LEDGER_FILE, JSON.stringify({ ts: new Date().toISOString(), ...entry }) + '\n'); } catch(e) {}
}

function loadToken() {
  try { return fs.readFileSync(TOKEN_FILE, 'utf8').trim(); } catch(e) { return null; }
}

async function sendTelegram(text) {
  const token = loadToken();
  if (!token) { console.error('⚠️ No Telegram token found at', TOKEN_FILE); return false; }
  return new Promise((resolve) => {
    const url = `https://api.telegram.org/bot${token}/sendMessage`;
    const params = new URLSearchParams();
    params.append('chat_id', 'me');
    params.append('text', text);
    params.append('parse_mode', 'HTML');
    https.post(url, params, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { const json = JSON.parse(data); resolve(json.ok === true); }
        catch(e) { resolve(false); }
      });
    }).on('error', () => resolve(false));
  });
}

// Load jobs config and state
let jobsConfig, jobsState;
try {
  jobsConfig = JSON.parse(fs.readFileSync(CRON_JOBS_FILE, 'utf8')).jobs;
} catch(e) {
  log('❌ Failed to parse jobs.json: ' + e.message);
  process.exit(1);
}
try {
  jobsState = JSON.parse(fs.readFileSync(CRON_STATE_FILE, 'utf8')).jobs;
} catch(e) {
  log('⚠️ No state file yet — first run?');
  jobsState = {};
}

const nowMs = Date.now();
const alerts = [];
const warnings = [];
const healthy = [];

// Helper: parse cron minute field to expected minutes
function expectedMinutesFromExpr(expr) {
  const parts = expr.split(' ');
  const minutePart = parts[0];
  const set = new Set();
  if (minutePart === '*') {
    for(let i=0;i<60;i++) set.add(i);
  } else if (minutePart.includes('/')) {
    const [base,stepStr] = minutePart.split('/');
    const step = parseInt(stepStr);
    const start = base === '*' ? 0 : parseInt(base);
    for(let i=start; i<60; i+=step) set.add(i);
  } else {
    minutePart.split(',').forEach(m=>{ if(m) set.add(parseInt(m)); });
  }
  return set;
}

// Helper: compute next run ms from cron expr (minimal, for drift detection)
function nextRunMsFromExpr(expr, afterMs) {
  const parts = expr.split(' ');
  const minutePart = parts[0];
  const hourPart = parts[1];
  // Simplified: only handle "N" or "N,M" or "*/N" for minutes; ignore complex hour/day for now
  // We'll use state.nextRunAtMs from actual cron state for drift check instead
  return null; // not implemented fully; rely on state file
}

log('=== Enhanced Cron Health Audit ===');
log(`Scanning ${jobsConfig.length} jobs at ${new Date().toISOString()}`);

let errorCount = 0;
let warningCount = 0;
let okCount = 0;

for (const job of jobsConfig) {
  if (!job.enabled) continue;
  const state = jobsState[job.id];
  const name = job.name;
  const expr = job.schedule.expr;

  // Gather metrics
  const consecutiveErrors = state?.consecutiveErrors || 0;
  const lastStatus = state?.lastStatus || 'unknown';
  const lastRunAtMs = state?.lastRunAtMs;
  const nextRunAtMs = state?.nextRunAtMs;
  const lastError = state?.lastError || '';

  // Check 1: Consecutive errors >= 3 → ALERT
  if (consecutiveErrors >= 3) {
    errorCount++;
    alerts.push(`🔴 ${name} | ${consecutiveErrors} consecutive errors | ${lastError}`);
    continue;
  } else if (consecutiveErrors >= 2) {
    warningCount++;
    warnings.push(`🟡 ${name} | ${consecutiveErrors} consecutive errors (approaching threshold)`);
  }

  // Check 2: Missed run detection
  // If nextRunAtMs is in the past AND lastRunStatus is not 'ok', we may have missed a run
  if (nextRunAtMs && nextRunAtMs < nowMs && lastStatus !== 'ok') {
    const overdueMs = nowMs - nextRunAtMs;
    const overdueMin = Math.round(overdueMs / 60000);
    if (overdueMin > 30) {
      warningCount++;
      warnings.push(`🟡 ${name} | Overdue by ${overdueMin} min (nextRunAt was past)`);
    }
  }

  // Check 3: Schedule drift (compare actual lastRunMs vs expected grid)
  // For 30min jobs: lastRun should align to :00 or :30 ± 2min tolerance
  if (lastRunAtMs) {
    const lastRunDate = new Date(lastRunAtMs);
    const minutes = lastRunDate.getUTCMinutes();
    const seconds = lastRunDate.getUTCSeconds();
    // For 30min interval jobs, expected: 0 or 30, tolerance ±2min
    if (expr.includes('*/30') || expr === '0,30 * * * *') {
      const expectedMin = Math.round(minutes / 30) * 30 % 60;
      const drift = Math.abs(minutes - expectedMin);
      if (drift > 2) {
        warningCount++;
        warnings.push(`🟡 ${name} | Schedule drift: ran at :${minutes.toString().padStart(2,'0')} expected :${expectedMin.toString().padStart(2,'0')} (±2min)`);
      }
    }
  }

  healthy.push(`✅ ${name} | last: ${new Date(lastRunAtMs||0).toISOString().slice(11,16)} UTC | status: ${lastStatus}`);
  okCount++;
}

// Summary
console.log('');
console.log('--- HEALTH SUMMARY ---');
console.log(`Healthy:   ${okCount}`);
console.log(`Warnings:  ${warningCount}`);
console.log(`Alerts:    ${errorCount}`);
console.log('');

if (alerts.length > 0) {
  console.log('🔴 CRITICAL ALERTS:');
  alerts.forEach(a => console.log('  ' + a));
  console.log('');
  // Send Telegram alert asynchronously (fire-and-forget)
  const alertText = '🔴 <b>Continuity Alerts</b>\n\n' + alerts.join('\n') + '\n\nTime: ' + new Date().toISOString();
  sendTelegram(alertText).catch(()=>{});
}

if (warnings.length > 0) {
  console.log('🟡 WARNINGS:');
  warnings.forEach(w => console.log('  ' + w));
  console.log('');
}

console.log('Healthy jobs sample (first 10):');
healthy.slice(0,10).forEach(h => console.log('  ' + h));

// Ledger entry
ledger({
  type: 'cron_health_audit',
  source: 'check_cron_health_v2',
  healthyCount: okCount,
  warningCount,
  alertCount: errorCount,
  alerts,
  warnings: warnings.slice(0,20) // cap size
});

log('✅ Audit complete — ledger updated');
process.exit(0);
