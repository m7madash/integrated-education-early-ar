#!/usr/bin/env node

/**
 * Daily Content Shield Review — Checks 5 random filtered items from past 24h
 * Runs as part of continuity-improvement cycle
 */

const fs = require('fs');
const path = require('path');

const logPath = path.join(__dirname, '..', 'reports', 'content_shield_log.jsonl');
const pendingPath = path.join(__dirname, '..', 'data', 'pending_reviews.jsonl');
const outputReport = path.join(__dirname, '..', 'reports', 'daily_filter_review.md');

/**
 * Get logs from last 24h
 */
function getRecentLogs() {
  if (!fs.existsSync(logPath)) return [];
  const lines = fs.readFileSync(logPath, 'utf8').trim().split('\n');
  const oneDayAgo = new Date();
  oneDayAgo.setDate(oneDayAgo.getDate() - 1);

  return lines.map(l => JSON.parse(l)).filter(entry => {
    const entryDate = new Date(entry.timestamp);
    return entryDate > oneDayAgo;
  });
}

/**
 * Get pending reviews
 */
function getPending() {
  if (!fs.existsSync(pendingPath)) return [];
  return fs.readFileSync(pendingPath, 'utf8').trim().split('\n')
    .filter(l => l.trim())
    .map(l => JSON.parse(l));
}

/**
 * Generate daily review report
 */
function runDailyReview() {
  const logs = getRecentLogs();
  const pending = getPending();

  // Pick 5 random items from flagged/pending
  const interesting = pending.filter(p => p.category !== 'trivial_content').slice(0, 5);

  const report = `# Daily Content Shield Review — ${new Date().toISOString().split('T')[0]}

## Quick Stats (24h)

- **Total filtered:** ${logs.length}
- **Auto-rejected:** ${logs.filter(l => l.action === 'reject').length}
- **Flagged for review:** ${logs.filter(l => l.action === 'flag_for_review').length}
- **Passed:** ${logs.filter(l => l.action === 'pass').length}
- **Pending human decisions:** ${pending.length}

## Sample for Quick Review (5 items)

${interesting.map((item, idx) => `
### ${idx + 1}. [${item.category}]
${item.content.substring(0, 200)}...

**Reason:** ${item.reason}
**Source:** ${item.source}
**ID:** ${item.id}

**Decision needed:**
- ✅ Approve (allow)
- ❌ Reject (block)
- ⏸️ Skip (keep pending)

`).join('')}

## Notes

- Review these items to ensure filter accuracy
- Adjust rules in `config/content_filter_rules.json` if false positives appear
- Add exceptions to `config/islamic_guardrails.json` for verified religious content

---

🕌 *All success is by Allah's favour — we maintain justice in content.*

*Generated automatically by continuity-improvement cycle.*
`;

  fs.writeFileSync(outputReport, report);
  console.log(`📄 Daily filter review: ${outputReport}`);

  return { logs, pending, sampleCount: interesting.length };
}

// Run
if (require.main === module) {
  const stats = runDailyReview();
  console.log('Daily review complete:', JSON.stringify(stats, null, 2));
}

module.exports = { runDailyReview };
