#!/usr/bin/env node
// Update cron_jobs_reference.json with Quran-only mission payloads
// Usage: node update_cron_payloads.js

const fs = require('fs');
const path = require('path');

const cronFile = '/root/.openclaw/workspace/cron_jobs_reference.json';
const mappingFile = '/root/.openclaw/workspace/mission_payloads_quran_only.json';

// Load data
const cron = JSON.parse(fs.readFileSync(cronFile, 'utf8'));
const mapping = JSON.parse(fs.readFileSync(mappingFile, 'utf8'));

console.log('Loaded cron jobs:', cron.jobs.length);
console.log('Loaded mission payloads:', Object.keys(mapping).length);

// Mapping from cron job ID base to mission file key
const jobToMission = {
  'mission-injustice-justice-00': 'injustice_justice',
  'mission-poverty-dignity-03': 'poverty_dignity',
  'mission-ignorance-knowledge-06': 'ignorance_knowledge',
  'mission-war-peace-09': 'war_peace',
  'mission-anti_extortion-21': 'anti_extortion',
  'mission-food_safety-12': 'food_safety',
  'mission-illness-health-15': 'illness_health',
  'mission-pollution-cleanliness-12': 'pollution_cleanliness',
  'mission-extremism-moderation-21': 'extremism_moderation',
  'mission-division-unity-00b': 'division_unity',
  'mission-slavery-freedom-18': 'slavery_freedom',
  'mission-corruption_reform-24': 'corruption_reform',
  'mission-modesty_filter-00': 'modesty_filter',
  'mission-learn_quran_prophet': 'learn_quran_prophet',
  'mission-dhikr_morning-03': 'dhikr_morning',
  'mission-dhikr_evening-19': 'dhikr_evening',
  'mission-dua_morning-03': 'dua_morning',
  'mission-dua_evening-19': 'dua_evening',
  'mission-tasbih_morning': 'tasbih_morning',
  'mission-good_deeds_evening': 'good_deeds_evening',
  'mission-anti_extortion-00': 'anti_extortion',
};

let updatedCount = 0;
let skippedCount = 0;

cron.jobs.forEach(job => {
  const missionKey = jobToMission[job.id];
  if (missionKey && mapping[missionKey]) {
    const oldLength = job.payload.text.length;
    job.payload.text = mapping[missionKey];
    const newLength = job.payload.text.length;
    console.log(`✅ ${job.id} -> ${missionKey} (${oldLength} -> ${newLength} chars)`);
    updatedCount++;
  } else {
    // console.log(`⏭️  ${job.id} -> no mapping, skipping`);
    skippedCount++;
  }
});

console.log(`\n✅ Updated: ${updatedCount} jobs`);
console.log(`⏭️  Skipped: ${skippedCount} jobs (non-mission or no mapping)`);

// Backup original
fs.copyFileSync(cronFile, cronFile + '.backup_quran_only_' + Date.now());
console.log('📦 Backup saved:', cronFile + '.backup_quran_only_' + Date.now());

// Write updated
fs.writeFileSync(cronFile, JSON.stringify(cron, null, 2));
console.log('✅ cron_jobs_reference.json updated successfully!');
