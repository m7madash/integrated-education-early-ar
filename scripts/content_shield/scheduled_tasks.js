#!/usr/bin/env node

/**
 * Content Shield — Scheduled Tasks (separate from main continuity)
 * Designed to run via cron alongside continuity-30min-check
 * Schedule:
 *   Daily review: 03:00 UTC
 *   Weekly report: Sunday 00:00 UTC
 */

const { runDailyReview } = require('./content_shield/daily_review');
const { generateReport } = require('./content_shield/report_generator');
const fs = require('fs');
const path = require('path');

const rootDir = '/root/.openclaw/workspace';

function runScheduledTasks() {
  const now = new Date();
  const hour = now.getUTCHours();
  const day = now.getUTCDay();
  const minute = now.getUTCMinutes();

  console.log(`🛡️ Content Shield scheduler — ${now.toISOString()}`);

  // Daily at 03:00
  if (hour === 3 && minute < 5) {
    console.log('🌅 Daily filter review (03:00 UTC)');
    try {
      runDailyReview();
    } catch (e) {
      console.error('Daily review error:', e.message);
      fs.appendFileSync(path.join(rootDir, 'memory', 'shield_scheduler_errors.log'),
        `${now.toISOString()} daily_review error: ${e.message}\n`);
    }
  }

  // Weekly on Sunday 00:00
  if (day === 0 && hour === 0 && minute < 5) {
    console.log('📊 Weekly efficacy report (Sun 00:00 UTC)');
    try {
      generateReport();
    } catch (e) {
      console.error('Weekly report error:', e.message);
      fs.appendFileSync(path.join(rootDir, 'memory', 'shield_scheduler_errors.log'),
        `${now.toISOString()} weekly_report error: ${e.message}\n`);
    }
  }

  console.log('✅ Shield scheduler complete');
}

// Run
runScheduledTasks();
