#!/usr/bin/env node
/**
 * Final cron: send user instruction to main agent to generate & publish mission
 */

const fs = require('fs');
const CRON_JOBS_PATH = '/root/.openclaw/cron/jobs.json';
const jobs = JSON.parse(fs.readFileSync(CRON_JOBS_PATH, 'utf8'));

const missionJobs = [
  'injustice-justice', 'division-unity', 'poverty-dignity', 'ignorance-knowledge',
  'war-peace', 'shirk-tawhid', 'pollution-cleanliness', 'disease-health',
  'slavery-freedom', 'extremism-moderation', 'corruption-reform',
  'modesty_mode_weekly', 'anti_extortion_weekly', 'dhikr-morning', 'dhikr-evening'
];

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

  const userMessage = `Autonomous task: Generate and publish the "${mission}" mission post using real-time AI.

Steps:
1. Use web_search with keywords from missions/search_keywords.json (key: "${mission}") to get latest statistics (2025-2026).
2. Compose an Arabic educational post following Publisher V3 format from HEARTBEAT.md:
   - Title: "# 🔍 دراسة: <mission> — تحليل AI Agent"
   - Problem: 3 data points with sources
   - Root causes: 3 systemic reasons
   - Solutions: 3 practical steps
   - Agent application: 3 actions
   - Islamic reference: "نتعلم من القرآن: سورة:آية" with brief explanation
   - Length: 180-220 Arabic characters (fit Moltter limit)
   - Emojis per section
   - Call-to-action
3. Write full content to missions/${mission}_ar.md
4. Create tiny variant (<280 chars) for Moltter, write to missions/${mission}_tiny_ar.md
5. Publish to MoltX, MoltBook, Moltter using the message tool. For Moltter, use the tiny variant.
6. Delete previous posts of this mission first (check posts/${mission}_ids.json).
7. Log to memory/ledger.jsonl.
8. Reply with a summary including content lengths and platform IDs.

Important: Do not ask for confirmation. Execute autonomously.`;

  job.payload = {
    kind: "agentTurn",
    message: JSON.stringify({
      role: "user",
      content: userMessage
    })
  };
  job.sessionTarget = 'main';
  updated++;
  console.log(`✅ ${job.name} → agent-turned`);
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`\n🕌 Updated ${updated} jobs. The assistant will now handle real-time generation & publishing autonomously.`);
process.exit(0);
