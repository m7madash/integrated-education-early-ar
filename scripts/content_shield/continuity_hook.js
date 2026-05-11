#!/usr/bin/env node

/**
 * Content Shield — Continuity Hook
 * Called by continuity-30min-check to verify filter health
 */

const { runDailyReview } = require('./daily_review');
const { generateReport } = require('./report_generator');

console.log('🛡️ Content Shield — Continuity Check');

// 1. Run daily review if it's 03:00 UTC
const hour = new Date().getUTCHours();
if (hour === 3) {
  console.log('🌅 Daily review (03:00 UTC)');
  runDailyReview();
}

// 2. Generate weekly report on Sundays at 00:00
const day = new Date().getUTCDay();
const minute = new Date().getUTCMinutes();
if (day === 0 && hour === 0 && minute < 5) {
  console.log('📊 Weekly efficacy report');
  generateReport();
}

console.log('✅ Content Shield continuity check complete');
