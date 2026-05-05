#!/usr/bin/env node
/**
 * Post-Mortem Workflow — Automatic error analysis & improvement generation
 * Continuity-improvement item #5: Learn from failure
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const ERROR_LOG = `${WORKSPACE}/logs/errors_${new Date().toISOString().split('T')[0]}.jsonl`;
const POSTMORTEM_DIR = `${WORKSPACE}/memory/postmortems`;
const REPORT_FILE = `${WORKSPACE}/reports/postmortem_${new Date().toISOString().split('T')[0]}.md`;

function ensure() {
  fs.mkdirSync(POSTMORTEM_DIR, { recursive: true });
  fs.mkdirSync(`${WORKSPACE}/reports`, { recursive: true });
}

/**
 * Load today's errors
 */
function loadErrors() {
  if (!fs.existsSync(ERROR_LOG)) return [];
  const lines = fs.readFileSync(ERROR_LOG, 'utf8').split('\n').filter(l => l.trim());
  return lines.map(l => JSON.parse(l));
}

/**
 * Categorize error
 */
function categorize(err) {
  if (!err) return 'unknown';
  const msg = (err.message || err || '').toLowerCase();

  if (msg.includes('timeout') || msg.includes('etimedout')) return 'network_timeout';
  if (msg.includes('unauthorized') || msg.includes('401') || msg.includes('403')) return 'auth';
  if (msg.includes('rate limit') || msg.includes('429')) return 'rate_limit';
  if (msg.includes('not found') || msg.includes('404')) return 'not_found';
  if (msg.includes('coherence')) return 'coherence_drift';
  if (msg.includes('memory') || msg.includes('ledger')) return 'memory';
  if (msg.includes('snapshot')) return 'snapshot';
  if (msg.includes('witness')) return 'witness_approval';

  return 'other';
}

/**
 * Generate 3 action items from error
 */
function generateActions(err) {
  const actions = [];
  const category = categorize(err);

  switch (category) {
    case 'network_timeout':
      actions.push('Add retry logic with exponential backoff');
      actions.push('Increase timeout threshold by 50%');
      actions.push('Circuit breaker: fallback to cached response after 3 failures');
      break;
    case 'rate_limit':
      actions.push('Implement rate limit detection + auto-backoff');
      actions.push('Queue requests for later retry');
      actions.push('Add jitter to stagger repeated calls');
      break;
    case 'auth':
      actions.push('Refresh credentials automatically');
      actions.push('Rotate API keys if expired');
      actions.push('Check gateway configuration');
      break;
    case 'coherence_drift':
      actions.push('Run ledger compaction');
      actions.push('Review recent entries for anomalies');
      actions.push('Force coherence re-enforcement');
      break;
    case 'memory':
      actions.push('Verify ledger file integrity');
      actions.push('Create fresh snapshot');
      actions.push('Check filesystem permissions');
      break;
    default:
      actions.push('Add monitoring/alerting for this error type');
      actions.push('Create regression test');
      actions.push('Document in continuity wiki');
  }

  return actions.slice(0, 3); // max 3 items
}

/**
 * Generate markdown report
 */
function generateReport(errors) {
  const grouped = {};
  errors.forEach(e => {
    const cat = categorize(e);
    grouped[cat] = (grouped[cat] || 0) + 1;
  });

  const total = errors.length;
  const topCategory = Object.keys(grouped).reduce((a, b) => grouped[a] > grouped[b] ? a : b, 'none');

  let md = `# Post-Mortem Report — ${new Date().toISOString().split('T')[0]}\n\n`;
  md += `## Overview\n`;
  md += `- Total errors: ${total}\n`;
  md += `- Most common: ${topCategory} (${grouped[topCategory] || 0})\n`;
  md += `- Error breakdown:\n`;
  Object.entries(grouped).forEach(([cat, count]) => {
    md += `  - ${cat}: ${count}\n`;
  });

  if (total > 0) {
    md += `\n## Detailed Analysis\n\n`;
    errors.forEach((err, i) => {
      md += `### Error ${i + 1}: ${categorize(err)}\n`;
      md += `- Message: ${err.message || err}\n`;
      md += `- Time: ${err.timestamp || 'unknown'}\n`;
      md += `- Source: ${err.source || 'unknown'}\n`;
      md += `\n**Action Items (3):**\n`;
      generateActions(err).forEach((action, j) => {
        md += `${j + 1}. ${action}\n`;
      });
      md += `\n`;
    });
  }

  md += `\n## Implementation Plan\n`;
  md += `- [ ] Fix: Top error category (${topCategory})\n`;
  md += `- [ ] Add: Monitoring/alerting for ${topCategory}\n`;
  md += `- [ ] Document: Add to continuity-runbook.md\n`;
  md += `- [ ] Test: Create regression test for error recurrence\n`;

  return md;
}

/**
 * Main
 */
function main() {
  ensure();

  const errors = loadErrors();
  const ledgerFile = `${WORKSPACE}/memory/ledger.jsonl`;

  if (errors.length === 0) {
    console.log('✅ No errors today — system healthy');
    fs.writeFileSync(REPORT_FILE, `# Post-Mortem — ${new Date().toISOString().split('T')[0]}\n\n✅ No errors recorded. System operating normally.\n`);
    // Still log healthy run to ledger for continuity tracking
    const healthyEntry = {
      ts: new Date().toISOString(),
      type: 'postmortem',
      date: new Date().toISOString().split('T')[0],
      errorCount: 0,
      status: 'healthy',
      actions: ['routine_check_complete']
    };
    fs.appendFileSync(ledgerFile, `${JSON.stringify(healthyEntry)}\n`);
    return;
  }

  // Categorize & generate report
  const report = generateReport(errors);
  fs.writeFileSync(REPORT_FILE, report);
  console.log(`📄 Post-mortem report: ${REPORT_FILE}`);

  // Also log to ledger
  const ledgerEntry = {
    ts: new Date().toISOString(),
    type: 'postmortem',
    date: new Date().toISOString().split('T')[0],
    errorCount: errors.length,
    topCategory: Object.keys(errors.reduce((a, e) => {
      const cat = categorize(e);
      a[cat] = (a[cat] || 0) + 1;
      return a;
    }, {})).sort((x, y) => a[y] - a[x])[0],
    actions: ['monitoring', 'regression_test', 'documentation']
  };

  fs.appendFileSync(ledgerFile, `${JSON.stringify(ledgerEntry)}\n`);

  console.log('✅ Post-mortem complete — improvement cycle started');
}

if (require.main === module) {
  main();
}

module.exports = { loadErrors, categorize, generateActions, generateReport };
