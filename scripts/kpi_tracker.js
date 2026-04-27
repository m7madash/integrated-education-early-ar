#!/usr/bin/env node
/**
 * KPI Tracker — Continuity health metrics dashboard
 * Tracks: post completion rate, platform reliability, coherence score, error frequency, heartbeat health
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const CONFIG = JSON.parse(fs.readFileSync(path.join(WORKSPACE, 'continuity.config.json'), 'utf8'));
const KPI_FILE = path.join(WORKSPACE, 'memory', 'kpi_history.jsonl');
const CURRENT_FILE = path.join(WORKSPACE, 'memory', 'kpi_current.json');

function loadHistory(days = 7) {
  if (!fs.existsSync(KPI_FILE)) return [];
  const cutoff = Date.now() - (days * 86400000);
  const lines = fs.readFileSync(KPI_FILE, 'utf8').split('\n').filter(l => l);
  return lines
    .map(l => JSON.parse(l))
    .filter(entry => entry.timestamp > cutoff);
}

function calculateMetrics() {
  const today = new Date().toISOString().split('T')[0];
  const logDir = path.join(WORKSPACE, 'logs');

  // Parse logs
  let totalPosts = 0, successfulPosts = 0, errors = 0;
  let platformStats = { moltbook: {total: 0, success: 0}, moltter: {total: 0, success: 0}, moltx: {total: 0, success: 0}};

  // Scan log files
  try {
    const logs = fs.readdirSync(logDir)
      .filter(f => (f.startsWith('post_') || f.startsWith('continuity_')) && f.endsWith('.log'))
      .map(f => ({ name: f, mtime: fs.statSync(path.join(logDir, f)).mtime }))
      .sort((a, b) => b.mtime - a.mtime)
      .slice(0, 30)
      .map(f => f.name);
    logs.forEach(logFile => {
      const content = fs.readFileSync(path.join(logDir, logFile), 'utf8');
      const lines = content.split('\n');

      // Per-line counting (each line is one post attempt)
      lines.forEach(line => {
        const hasSuccess = line.includes('✅');
        const hasFail = /⚠️.*failed/i.test(line);
        const hasMB = /MB Team|MB General|MoltBook/i.test(line);
        const hasMoltter = line.includes('Moltter:');
        const hasMoltX = /MoltX|moltx/i.test(line);

        if (hasMB) {
          platformStats.moltbook.total++;
          if (hasSuccess) platformStats.moltbook.success++;
        }
        if (hasMoltter) {
          platformStats.moltter.total++;
          if (hasSuccess) platformStats.moltter.success++;
        }
        if (hasMoltX) {
          platformStats.moltx.total++;
          if (hasSuccess) platformStats.moltx.success++;
        }

        // Overall post counts
        if (hasSuccess || hasFail) {
          totalPosts++;
          if (hasSuccess) successfulPosts++;
          if (hasFail) errors++;
        }

        // Generic ERROR/FAILED
        if (/ERROR|FAILED/gi.test(line)) errors++;
      });
    });
  } catch (e) { console.error('⚠️ Log scan error:', e.message); }

  // Coherence score (from latest analysis)
  let coherenceScore = 1.0;
  try {
    const coherence = require('./scripts/coherence_alert');
    const analysis = coherence.analyze(100);
    coherenceScore = analysis.score;
  } catch (e) { /* ignore */ }

  // Heartbeat health (count successful continuity checks today)
  let heartbeatCount = 0;
  try {
    const ledgerFile = path.join(WORKSPACE, 'memory', 'ledger.jsonl');
    if (fs.existsSync(ledgerFile)) {
      const ledger = fs.readFileSync(ledgerFile, 'utf8').split('\n').filter(l => l);
      const todayStart = new Date(today + 'T00:00:00Z').getTime();
      const todayEnd = new Date(today + 'T23:59:59Z').getTime();
      const heartbeatTypes = ['continuity_check', 'continuity_pulse', 'continuity_work'];
      heartbeatCount = ledger.filter(entry => {
        try {
          const e = JSON.parse(entry);
          if (heartbeatTypes.includes(e.type)) {
            const ts = new Date(e.ts).getTime();
            return ts >= todayStart && ts <= todayEnd;
          }
        } catch (e) { return false; }
        return false;
      }).length;
    }
  } catch (e) { /* ignore */ }

  // Error rate (errors / total operations)
  const totalOps = Math.max(totalPosts + heartbeatCount, 1);
  const errorRate = errors / totalOps;

  // Post completion rate (successful / expected)
  const expectedPosts = 13; // Daily mission posts + supplemental
  const completionRate = successfulPosts / expectedPosts;

  // Compile current KPIs
  const kpi = {
    timestamp: Date.now(),
    date: today,
    metrics: {
      postCompletionRate: Math.min(completionRate, 1),
      platformReliability: {
        moltbook: platformStats.moltbook.total ? platformStats.moltbook.success / platformStats.moltbook.total : 1,
        moltter: platformStats.moltter.total ? platformStats.moltter.success / platformStats.moltter.total : 1,
        moltx: platformStats.moltx.total ? platformStats.moltx.success / platformStats.moltx.total : 1,
        overall: Object.values(platformStats).reduce((sum, p) => sum + (p.total ? p.success / p.total : 1), 0) / 3
      },
      coherenceScore,
      errorFrequency: errorRate,
      heartbeatHealth: Math.min(heartbeatCount / 48, 1) // 48 expected heartbeats per day (every 30min)
    },
    targets: CONFIG.kpi,
    health: 'ok'
  };

  // Determine overall health
  const failingMetrics = Object.entries(kpi.metrics).filter(([k, v]) => {
    if (k === 'platformReliability') return v.overall < CONFIG.kpi.platformReliability.target;
    return typeof v === 'number' && v < CONFIG.kpi[k].target;
  });

  if (failingMetrics.length > 0) {
    kpi.health = 'degraded';
    kpi.issues = failingMetrics.map(([k, v]) => {
      if (k === 'platformReliability') return `${k}: ${v.overall.toFixed(3)} (target ${CONFIG.kpi[k].target})`;
      return `${k}: ${v.toFixed(3)} (target ${CONFIG.kpi[k].target})`;
    });
  }

  // Save current
  fs.writeFileSync(CURRENT_FILE, JSON.stringify(kpi, null, 2));

  // Append to history
  fs.appendFileSync(KPI_FILE, JSON.stringify({
    timestamp: kpi.timestamp,
    date: kpi.date,
    metrics: kpi.metrics,
    health: kpi.health
  }) + '\n');

  return kpi;
}

function trendReport(days = 7) {
  const history = loadHistory(days);
  if (history.length === 0) return 'No historical data';

  const trends = {};
  history.forEach(entry => {
    Object.entries(entry.metrics).forEach(([k, v]) => {
      if (typeof v === 'number') {
        trends[k] = trends[k] || { values: [], sum: 0 };
        trends[k].values.push(v);
        trends[k].sum += v;
      } else if (k === 'platformReliability') {
        trends.platformReliability = trends.platformReliability || { values: [], sum: 0 };
        trends.platformReliability.values.push(v.overall);
        trends.platformReliability.sum += v.overall;
      }
    });
  });

  let report = `📊 KPI Trends (last ${days} days)\n\n`;
  Object.entries(trends).forEach(([k, t]) => {
    const avg = t.sum / t.values.length;
    const direction = t.values[t.values.length - 1] > t.values[0] ? '↗️' : '↘️';
    report += `${k}: ${avg.toFixed(3)} ${direction}\n`;
  });

  return report;
}

// CLI
if (require.main === module) {
  const cmd = process.argv[2];

  if (cmd === 'report') {
    const days = parseInt(process.argv[3]) || 7;
    console.log(trendReport(days));
  } else if (cmd === 'check') {
    const kpi = calculateMetrics();
    console.log(`📈 Health: ${kpi.health.toUpperCase()}`);
    console.log(`   Post completion: ${(kpi.metrics.postCompletionRate * 100).toFixed(1)}%`);
    console.log(`   Coherence: ${kpi.metrics.coherenceScore.toFixed(3)}`);
    console.log(`   Error rate: ${(kpi.metrics.errorFrequency * 100).toFixed(1)}%`);
    if (kpi.issues) console.log('\n⚠️ Issues:', kpi.issues.join('; '));
  } else {
    console.log('Usage: kpi_tracker.js [report [days]] | [check]');
  }
}

module.exports = { calculateMetrics, trendReport, loadHistory };
