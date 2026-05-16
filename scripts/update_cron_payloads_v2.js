#!/usr/bin/env node
// Update payloads in cron_jobs_reference_final.json from mission_payloads_quran_only.json

const fs = require('fs');
const path = require('path');

const cronPath = '/root/.openclaw/workspace/cron_jobs_reference_final.json';
const payloadsPath = '/root/.openclaw/workspace/mission_payloads_quran_only.json';

const cronData = JSON.parse(fs.readFileSync(cronPath, 'utf8'));
const payloadsData = JSON.parse(fs.readFileSync(payloadsPath, 'utf8'));

let updated = 0;
let skipped = 0;

cronData.jobs.forEach(job => {
  // Extract mission key: e.g., "mission-anti_extortion-00" -> "anti_extortion"
  const parts = job.id.split('-');
  if (parts.length >= 2) {
    const missionKey = parts[1]; // anti_extortion, corruption_reform, etc.

    if (payloadsData[missionKey]) {
      // Find the mission file that matches this key (with _quran_only suffix check)
      const expectedPayload = payloadsData[missionKey];

      // Update the payload.text only
      if (job.payload && job.payload.kind === 'systemEvent') {
        job.payload.text = expectedPayload;
        job.updatedAtMs = Date.now();
        updated++;
        console.log(`✅ ${job.id} (${missionKey}) — payload updated`);
      } else {
        console.log(`⚠️ ${job.id} — unexpected payload structure, skipped`);
        skipped++;
      }
    } else {
      console.log(`❌ ${job.id} (${missionKey}) — no payload found in mapping`);
      skipped++;
    }
  } else {
    console.log(`⚠️ ${job.id} — malformed ID`);
    skipped++;
  }
});

// Write back
fs.writeFileSync(cronPath, JSON.stringify(cronData, null, 2));
console.log(`\n📝 Updated ${updated} jobs, skipped ${skipped}`);
console.log(`🕐 New timestamp: ${new Date().toISOString()}`);
