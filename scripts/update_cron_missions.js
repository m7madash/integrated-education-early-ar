#!/usr/bin/env node
/**
 * update_cron_missions.js
 *
 * Transforms all "Real-Time Mission:" cron jobs to use pre-written files only.
 * Removes web_search/compose steps; directly reads existing analytical/tiny files
 * and publishes via publish_arabic_v3_fixed.sh.
 *
 * Usage: node scripts/update_cron_missions.js
 */

const fs = require('fs');
const path = require('path');

const JOBS_FILE = path.join('/root/.openclaw/workspace/cron', 'jobs.json');

function buildNewMessage(internalMission) {
  const content = `🕌 Real-Time Mission: ${internalMission}

Execute autonomously:

1. Read pre-written files:
   - Full: /root/.openclaw/workspace/missions/${internalMission}_analytical_ar.md
   - Tiny: /root/.openclaw/workspace/missions/${internalMission}_tiny_analytical_ar.md

2. Publish: Exec bash scripts/publish_arabic_v3_fixed.sh ${internalMission}
   (This will verify Arabic-only, verify religious format, delete old posts, publish to MoltX/MoltBook/Moltter)

3. Log: Append to memory/ledger.jsonl entry with platform IDs and status.

4. DO NOT ask for confirmation. Execute immediately.`;
  // Return as JSON string for embedding: {"role":"user","content":"..."}
  return JSON.stringify({
    role: "user",
    content: content
  });
}

// Mapping from job name (key in jobs.json) to internal mission identifier
const nameToMission = {
  "dhikr-evening": "dhikr_evening",
  "dhikr-morning": "dhikr_morning",
  "corruption-reform": "corruption_reform",
  "injustice-justice": "injustice_justice",
  "poverty-dignity": "poverty_dignity",
  "ignorance-knowledge": "ignorance_knowledge",
  "war-peace": "war_peace",
  "pollution-cleanliness": "pollution_cleanliness",
  "disease-health": "disease_health",
  "slavery-freedom": "slavery_freedom",
  "extremism-moderation": "extremism_moderation",
  "division-unity": "division_unity",
  "shirk-tawhid": "shirk_tawhid",
  "anti_extortion_weekly": "anti_extortion",
  "modesty_mode_weekly": "modesty_filter",
  "quran-study": "quran_study",
  "wise-disagreement-prophetic-way": "wise-disagreement-prophetic-way",
  "revive-sunnah-48h": "revive_sunnah"
};

// Jobs to disable (tests/extra)
const jobsToDisable = new Set([
  "long-test",
  "test2",
  "test-payload-newlines",
  "corruption_reform_weekly"
]);

try {
  const raw = fs.readFileSync(JOBS_FILE, 'utf8');
  const jobs = JSON.parse(raw);

  let updated = false;
  for (const job of jobs.jobs) {
    // If job is in disable list, mark disabled
    if (jobsToDisable.has(job.name)) {
      if (job.enabled !== false) {
        job.enabled = false;
        console.log(`✅ Disabled job: ${job.name}`);
        updated = true;
      }
      continue;
    }

    // Skip if not agentTurn or no message
    if (!job.payload || job.payload.kind !== 'agentTurn' || !job.payload.message) {
      continue;
    }

    // Check if it's a Real-Time Mission job
    const msgStr = typeof job.payload.message === 'string' ? job.payload.message : null;
    if (!msgStr || !msgStr.includes('🕌 Real-Time Mission:')) {
      continue;
    }

    const missionName = job.name;
    const internalMission = nameToMission[missionName];
    if (!internalMission) {
      console.warn(`⚠️ No mapping for job: ${missionName}, skipping`);
      continue;
    }

    // Build new message object
    const newMessageObj = {
      role: "user",
      content: `🕌 Real-Time Mission: ${internalMission}

Execute autonomously:

1. Read pre-written files:
   - Full: /root/.openclaw/workspace/missions/${internalMission}_analytical_ar.md
   - Tiny: /root/.openclaw/workspace/missions/${internalMission}_tiny_analytical_ar.md

2. Publish: Exec bash scripts/publish_arabic_v3_fixed.sh ${internalMission}
   (This will verify Arabic-only, verify religious format, delete old posts, publish to MoltX/MoltBook/Moltter)

3. Log: Append to memory/ledger.jsonl entry with platform IDs and status.

4. DO NOT ask for confirmation. Execute immediately.`
    };

    // Replace payload.message with a JSON string of the object
    job.payload.message = JSON.stringify(newMessageObj);
    console.log(`✅ Updated mission job: ${job.name} → ${internalMission}`);
    updated = true;
  }

  if (updated) {
    fs.writeFileSync(JOBS_FILE, JSON.stringify(jobs, null, 2), 'utf8');
    console.log('✅ cron/jobs.json updated successfully.');
  } else {
    console.log('ℹ️ No changes made to cron jobs.');
  }

} catch (err) {
  console.error('❌ Error:', err);
  process.exit(1);
}