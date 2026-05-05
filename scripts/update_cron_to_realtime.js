#!/usr/bin/env node
/**
 * Update cron jobs to use real-time AI publisher — v2
 */

const fs = require('fs');
const CRON_JOBS_PATH = '/root/.openclaw/cron/jobs.json';
const jobs = JSON.parse(fs.readFileSync(CRON_JOBS_PATH, 'utf8'));

// Exact job names from cron that need conversion (main daily/weekly missions)
const missionJobs = [
  'injustice-justice', 'division-unity', 'poverty-dignity', 'ignorance-knowledge',
  'war-peace', 'shirk-tawhid', 'pollution-cleanliness', 'disease-health',
  'slavery-freedom', 'extremism-moderation', 'corruption-reform',
  'modesty_mode_weekly', 'anti_extortion_weekly',
  'dhikr-morning', 'dhikr-evening'
];

// Map cron job name → mission file name (underscored)
const nameToMission = {
  'injustice-justice': 'injustice_justice',
  'division-unity': 'division_unity',
  'poverty-dignity': 'poverty_dignity',
  'ignorance-knowledge': 'ignorance_knowledge',
  'war-peace': 'war_peace',
  'shirk-tawhid': 'shirk_tawhid',
  'pollution-cleanliness': 'pollution_cleanliness',
  'disease-health': 'disease_health',
  'slavery-freedom': 'slavery_freedom',
  'extremism-moderation': 'extremism_moderation',
  'corruption-reform': 'corruption_reform',
  'modesty_mode_weekly': 'modesty_filter',
  'anti_extortion_weekly': 'anti_extortion',
  'dhikr-morning': 'dhikr_morning',
  'dhikr-evening': 'dhikr_evening'
};

let updated = 0;

jobs.jobs = jobs.jobs.map(job => {
  if (!missionJobs.includes(job.name)) return job;

  const mission = nameToMission[job.name];
  if (!mission) return job;

  const newPayload = {
    kind: "agentTurn",
    message: JSON.stringify({
      type: "system",
      action: "publish_realtime",
      script: "scripts/publish_mission_realtime.js",
      mission: mission
    })
  };

  // Most missions run in main; hooks/tinies in isolated
  const newTarget = (job.name.includes('-hook') || job.name.includes('-tiny')) ? 'isolated' : 'main';

  if (job.payload.kind === 'systemEvent') {
    job.payload = newPayload;
    job.sessionTarget = newTarget;
    updated++;
    console.log(`✅ ${job.name} → ${mission} (target: ${newTarget})`);
  }
  
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`\n🕌 Real-time mode: ${updated} mission jobs updated.`);
console.log(`   Next cron reload required: openclaw cron reload`);
process.exit(0);
