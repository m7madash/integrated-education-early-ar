#!/usr/bin/env node

/**
 * Content Shield — Integration Hub
 * Connects filter to: publishing, social interactions, continuity
 */

const { publishWithShield } = require('./content_shield/publisher_wrapper');
const { filterContent } = require('./content_shield/filter_v3');
const { runDailyReview } = require('./content_shield/daily_review');
const { generateReport } = require('./content_shield/report_generator');
const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..');

/**
 * Hook: called before any mission publish
 * Returns: { allowed: boolean, action: 'publish'|'queue'|'reject', reason? }
 */
function beforePublish(content, platform, postId) {
  return publishWithShield(content, platform, postId);
}

/**
 * Hook: called before social interaction reply
 * Returns: { allowed: boolean, reason? } or passes through
 */
function beforeReply(replyText, platform, commentId) {
  const result = filterContent(replyText, { isReligiousContent: true });
  if (result.action === 'reject') {
    return { allowed: false, reason: result.reason, action: 'reject' };
  }
  if (result.action === 'flag_for_review') {
    // Queue for human review, don't send automatically
    const { queueForReview } = require('./content_shield/review_queue');
    queueForReview({
      content: replyText,
      category: result.category,
      reason: result.reason,
      source: platform,
      postId: commentId
    });
    return { allowed: false, action: 'queued', reviewId: result.reviewId };
  }
  return { allowed: true, action: 'send' };
}

/**
 * Continuity hook — called by continuity-30min-check
 */
function continuityCheck() {
  const hour = new Date().getUTCHours();
  const day = new Date().getUTCDay();
  const minute = new Date().getUTCMinutes();

  // Daily review at 03:00
  if (hour === 3 && minute < 5) {
    console.log('[Integrate] Daily filter review');
    runDailyReview();
  }

  // Weekly report on Sunday 00:00
  if (day === 0 && hour === 0 && minute < 5) {
    console.log('[Integrate] Weekly efficacy report');
    generateReport();
  }

  return { ran: true };
}

/**
 * Status report for monitoring
 */
function getShieldStatus() {
  const logPath = path.join(rootDir, 'reports', 'content_shield_log.jsonl');
  const pendingPath = path.join(rootDir, 'data', 'pending_reviews.jsonl');

  const logs = fs.existsSync(logPath) ? fs.readFileSync(logPath, 'utf8').trim().split('\n').filter(l => l) : [];
  const pending = fs.existsSync(pendingPath) ? fs.readFileSync(pendingPath, 'utf8').trim().split('\n').filter(l => l) : [];

  const last24h = logs.filter(l => {
    const entry = JSON.parse(l);
    const entryTime = new Date(entry.timestamp);
    const now = new Date();
    return (now - entryTime) < 24 * 60 * 60 * 1000;
  });

  return {
    total_checks: logs.length,
    last_24h: last24h.length,
    pending_reviews: pending.length,
    auto_rejected_24h: last24h.filter(l => JSON.parse(l).action === 'reject').length,
    flagged_24h: last24h.filter(l => JSON.parse(l).action === 'flag_for_review').length
  };
}

// CLI interface
if (require.main === module) {
  const cmd = process.argv[2];

  if (cmd === 'status') {
    const status = getShieldStatus();
    console.log(JSON.stringify(status, null, 2));
  } else if (cmd === 'test-publish') {
    const content = process.argv[3] || 'test';
    const platform = process.argv[4] || 'test';
    const result = beforePublish(content, platform);
    console.log('Publish check:', JSON.stringify(result, null, 2));
  } else if (cmd === 'test-reply') {
    const reply = process.argv[3] || 'test reply';
    const platform = process.argv[4] || 'test';
    const result = beforeReply(reply, platform);
    console.log('Reply check:', JSON.stringify(result, null, 2));
  } else {
    console.log('Usage: node integrate_shield.js [status|test-publish <text> <platform>|test-reply <text> <platform>|continuity]');
  }
}

module.exports = {
  beforePublish,
  beforeReply,
  continuityCheck,
  getShieldStatus
};
