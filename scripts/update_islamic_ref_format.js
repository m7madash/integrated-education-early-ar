#!/usr/bin/env node
/**
 * Update cron jobs: change Islamic reference format to "نتعلم من الآيات من القرآن"
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

ACTION:
1. web_search with: ${keywords.join(', ')} → get latest data (2025-2026).
2. Compose Arabic educational post (180-220 chars):
   - Title: "# 🔍 دراسة: ${mission} — تحليل AI Agent"
   - Problem: 3 stats from search
   - Causes: 3 systemic
   - Solutions: 3 practical
   - Agent steps: 3
   - Islamic reference: **"نتعلم من الآيات من القرآن: [سورة:آية]"** + 1-sentence explanation (humble, contextual)
   - Emojis per section
   - CTA question
   - Hashtags: #عدل + relevant
3. Write full content to: /root/.openclaw/workspace/missions/${mission}_ar.md
4. Create tiny (<280 chars) to: /root/.openclaw/workspace/missions/${mission}_tiny_ar.md
5. Exec: bash scripts/publish_arabic_v3_fixed.sh ${mission}
6. Log to memory/ledger.jsonl
7. Do NOT ask for confirmation. Execute autonomously now.

 remembrance: Use "نتعلم من الآيات من القرآن" exactly.`;
  
  job.payload = {
    kind: "agentTurn",
    message: JSON.stringify({ role: "user", content: instruction })
  };
  job.sessionTarget = 'main';
  updated++;
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`✅ Updated ${updated} jobs with new Islamic reference format.`);
process.exit(0);
