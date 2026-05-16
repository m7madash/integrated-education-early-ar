#!/usr/bin/env node
// Update cron_jobs_reference_final.json payloads from mission_payloads_quran_only.json

const fs = require('fs');

const cronPath = '/root/.openclaw/workspace/cron_jobs_reference_final.json';
const payloadsPath = '/root/.openclaw/workspace/mission_payloads_quran_only.json';

const cronData = JSON.parse(fs.readFileSync(cronPath, 'utf8'));
const payloads = JSON.parse(fs.readFileSync(payloadsPath, 'utf8'));

let updated = 0;
let skipped = 0;

cronData.jobs.forEach(job => {
  const match = job.id.match(/^mission-([a-z_]+)-\d+$/);
  if (match) {
    const key = match[1];
    if (payloads[key]) {
      job.payload.text = payloads[key];
      job.updatedAtMs = Date.now();
      updated++;
      console.log(`✅ ${job.id} → ${key}`);
    } else {
      console.log(`❌ ${job.id} — no payload for key: ${key}`);
      skipped++;
    }
  } else {
    console.log(`⚠️ ${job.id} — malformed ID`);
    skipped++;
  }
});

fs.writeFileSync(cronPath, JSON.stringify(cronData, null, 2));
console.log(`\n📝 Updated ${updated} jobs, skipped ${skipped}`);
console.log(`🕐 Timestamp: ${new Date().toISOString()}`);
