#!/usr/bin/env node

/**
 * Shield Check CLI — called from bash publish scripts
 * Usage: node scripts/content_shield/shield_check.js "<content>" <platform> <mission>
 * Exit codes: 0 = pass/queue, 1 = reject
 */

const { publishWithShield } = require('./publisher_wrapper');
const fs = require('fs');
const path = require('path');

const rootDir = path.join(__dirname, '..', '..');
const args = process.argv.slice(2);

if (args.length < 2) {
  console.error('Usage: shield_check.js "<content>" <platform> [mission]');
  process.exit(1);
}

const content = args[0];
const platform = args[1];
const mission = args[2] || 'unknown';

const result = publishWithShield(content, platform, mission);

if (result.allowed) {
  console.log(`✅ Shield PASS — ${platform} [${mission}]`);
  process.exit(0);
}

if (result.action === 'queue') {
  console.log(`⏸️ Shield QUEUE — reviewID: ${result.reviewId} [${mission}]`);
  // Exit 0 because we want publish script to continue (no block, just delay)
  process.exit(0);
}

console.log(`❌ Shield REJECT — ${result.reason} [${mission}]`);
process.exit(1);
