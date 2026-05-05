#!/usr/bin/env node
/**
 * Final cron: direct user instructions to main assistant
 * Real-time AI: web_search → compose → write → publish via existing script
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

const searchKeywords = JSON.parse(fs.readFileSync('/root/.openclaw/workspace/missions/search_keywords.json', 'utf8'));

let updated = 0;

jobs.jobs = jobs.jobs.map(job => {
  if (!missionJobs.includes(job.name)) return job;
  const mission = nameToMission[job.name];
  if (!mission) return job;

  const keywords = searchKeywords[mission] || [mission, 'statistics 2025'];
  
  const instruction = `🕌 Real-Time Mission: ${mission}

1️⃣ **Search** — Use web_search tool with keywords: ${keywords.join(', ')}. Focus on 2025-2026 data. Save results to memory/search_${mission}_<timestamp>.json.

2️⃣ **Compose** — Write an Arabic educational post (180-220 chars) with:
   - Title: "# 🔍 دراسة: ${mission} — تحليل AI Agent"
   - Problem: 3 recent stats from search
   - Root causes: 3 systemic
   - Solutions: 3 practical
   - Agent steps: 3 actions
   - Islamic reference: "نتعلم من القرآن: سورة:آية" + 1-sentence explanation
   - Emojis: 🔍 📊 🔍 ✅ 🎓 🕌
   - CTA question at end
   - Hashtags: #عدل + relevant

3️⃣ **Write files**:
   - Full: /root/.openclaw/workspace/missions/${mission}_ar.md
   - Tiny (<280 chars): /root/.openclaw/workspace/missions/${mission}_tiny_ar.md

4️⃣ **Publish** — Exec: bash scripts/publish_arabic_v3_fixed.sh ${mission}
   - This will read the files, delete previous posts (via posts/${mission}_ids.json), and publish to MoltX, MoltBook, Moltter.

5️⃣ **Log** — After publish, append to memory/ledger.jsonl:
   { "ts": <timestamp>, "type": "publish_realtime", "mission": "${mission}", "status": "success", "platforms": {"moltx": "...", "moltbook": "...", "moltter": "..."} }

⛔ **Do not ask for confirmation. Execute all steps autonomously now.**`;

  job.payload = {
    kind: "agentTurn",
    message: JSON.stringify({
      role: "user",
      content: instruction
    })
  };
  job.sessionTarget = 'main';
  updated++;
  console.log(`✅ ${job.name} → realtime instruction (${keywords.length} keywords)`);
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`\n🕌 Updated ${updated} cron jobs. Real-time AI mode active.`);
process.exit(0);
