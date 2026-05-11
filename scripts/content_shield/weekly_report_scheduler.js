#!/usr/bin/env node

/**
 * Weekly Content Shield Report — scheduled on Sundays 00:00
 * Generates: reports/filter_efficacy_YYYY-MM-DD.md
 * Also appends summary to memory/weekly_shield_summary.md
 */

const { generateReport } = require('./content_shield/report_generator');
const fs = require('fs');
const path = require('path');

const rootDir = '/root/.openclaw/workspace';
const weeklyMem = path.join(rootDir, 'memory', 'weekly_shield_summary.md');

function run() {
  console.log('📊 Content Shield — Weekly efficacy report');
  const stats = generateReport();

  // Append to memory for human review
  const summary = `# Weekly Shield Summary — ${new Date().toISOString().split('T')[0]}\n\n` +
    `- Total checked: ${stats.total_checked}\n` +
    `- Auto-rejected: ${stats.auto_rejected}\n` +
    `- Flagged: ${stats.flagged_for_review}\n` +
    `- Passed: ${stats.passed}\n` +
    `- False positives: ${stats.false_positives}\n` +
    `- True positives: ${stats.true_positives}\n\n` +
    `---\n\n`;
  fs.appendFileSync(weeklyMem, summary);

  console.log('✅ Weekly report generated');
}

if (require.main === module) run();
module.exports = { run };
