#!/usr/bin/env node

/**
 * Content Shield — Review Queue Manager
 * Handles flagged content, notifies reviewers, tracks decisions
 */

const fs = require('fs');
const path = require('path');

const pendingPath = path.join(__dirname, '..', 'data', 'pending_reviews.jsonl');
const decisionsPath = path.join(__dirname, '..', 'reviews', 'decisions.jsonl');

/**
 * Add item to review queue
 */
function queueForReview(item) {
  const entry = {
    id: generateId(),
    timestamp: new Date().toISOString(),
    content: item.content,
    category: item.category,
    reason: item.reason,
    source: item.source || 'unknown', // moltter, moltbook, etc.
    postId: item.postId || null,
    reviewer: null,
    decision: null,
    decisionAt: null
  };

  fs.appendFileSync(pendingPath, JSON.stringify(entry) + '\n');
  console.log(`📝 Queued for review: [${item.category}] ${entry.id}`);
  return entry.id;
}

/**
 * Get all pending items (for human review dashboard)
 */
function getPendingReviews() {
  if (!fs.existsSync(pendingPath)) return [];
  const lines = fs.readFileSync(pendingPath, 'utf8').trim().split('\n');
  return lines.map(line => JSON.parse(line)).filter(item => !item.decision);
}

/**
 * Record human decision
 */
function recordDecision(reviewId, decision, reviewer, note = '') {
  const now = new Date().toISOString();

  // Update pending
  let lines = fs.readFileSync(pendingPath, 'utf8').trim().split('\n');
  let updated = false;
  lines = lines.map(line => {
    const item = JSON.parse(line);
    if (item.id === reviewId) {
      item.decision = decision;
      item.reviewer = reviewer;
      item.decisionAt = now;
      item.note = note;
      updated = true;
    }
    return JSON.stringify(item);
  });
  fs.writeFileSync(pendingPath, lines.join('\n'));

  // Append to decisions log
  const decisionRecord = { reviewId, decision, reviewer, note, decidedAt: now };
  fs.appendFileSync(decisionsPath, JSON.stringify(decisionRecord) + '\n');

  console.log(`✅ Decision recorded: ${reviewId} → ${decision} by ${reviewer}`);
}

/**
 * Summary report for notifications
 */
function generatePendingSummary() {
  const pending = getPendingReviews();
  const byCategory = {};
  pending.forEach(item => {
    byCategory[item.category] = (byCategory[item.category] || 0) + 1;
  });

  return {
    total: pending.length,
    byCategory,
    oldest: pending.length ? pending[0].timestamp : null
  };
}

function generateId() {
  return 'rev_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

// CLI
if (require.main === module) {
  const cmd = process.argv[2];

  if (cmd === 'queue') {
    const content = process.argv[3];
    const category = process.argv[4] || 'uncategorized';
    queueForReview({ content, category, reason: 'manual flag' });
  } else if (cmd === 'list') {
    console.log(JSON.stringify(getPendingReviews(), null, 2));
  } else if (cmd === 'summary') {
    console.log(JSON.stringify(generatePendingSummary(), null, 2));
  } else {
    console.log('Usage: node review_queue.js [queue <text> <category> | list | summary]');
  }
}

module.exports = { queueForReview, getPendingReviews, recordDecision, generatePendingSummary };
