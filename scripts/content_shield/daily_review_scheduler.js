#!/usr/bin/env node

/**
 * Content Shield — Daily Review Scheduler
 * Integrated into continuity-improvement cycle
 * Generates: reports/daily_filter_review.md
 * Also updates: memory/daily_shield_status.json
 */

const { runDailyReview } = require('./content_shield/daily_review');
const fs = require('fs');
const path = require('path');

const rootDir = '/root/.openclaw/workspace';
const statusFile = path.join(rootDir, 'memory', 'daily_shield_status.json');

/**
 * Run daily review and record status
 */
function run() {
  console.log('🛡️ Content Shield — Daily review (continuity hook)');
  
  try {
    const result = runDailyReview();
    
    // Record status for monitoring
    const status = {
      date: new Date().toISOString().split('T')[0],
      lastRun: new Date().toISOString(),
      samplesReviewed: result.sampleCount,
      totalPending: result.pending.length,
      totalLogged: result.logs.length,
      health: 'ok'
    };
    fs.writeFileSync(statusFile, JSON.stringify(status, null, 2));
    
    console.log('✅ Daily review complete — samples:', result.sampleCount);
    return status;
  } catch (e) {
    console.error('❌ Daily review failed:', e.message);
    const status = {
      date: new Date().toISOString().split('T')[0],
      lastRun: new Date().toISOString(),
      error: e.message,
      health: 'error'
    };
    fs.writeFileSync(statusFile, JSON.stringify(status, null, 2));
    process.exit(1);
  }
}

// Run when called
if (require.main === module) {
  run();
}

module.exports = { run };
