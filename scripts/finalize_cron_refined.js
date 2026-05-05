#!/usr/bin/env node
/**
 * Final cron config: Islamic reference format updated
 * Requires explicit "المرجعية الشرعية" section with new phrase
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

Execute autonomously:

1. **web_search** with keywords: ${keywords.join(', ')} → obtain latest 2025-2026 statistics.

2. **Compose** Arabic educational post (180-220 Arabic characters) with EXACT structure:
   - Title: "# 🔍 دراسة: ${mission} — تحليل AI Agent"
   - Problem: 3 data points (from search results, cite sources)
   - Root causes: 3 systemic reasons
   - Solutions: 3 practical steps
   - Agent application: 3 concrete actions
   - **🕌 **المرجعية الشرعية:** نتعلم من الآيات من القرآن: [سورة:آية] — [one-sentence humble explanation tied to mission]**
   - Emojis: 🔍 📊 🔍 ✅ 🎓 🕌
   - End with CTA question
   - Hashtags: #عدل + mission-specific

3. **Write files**:
   - Full: /root/.openclaw/workspace/missions/${mission}_ar.md
   - Tiny (<280 Arabic chars): /root/.openclaw/workspace/missions/${mission}_tiny_ar.md

4. **Publish**: Exec bash scripts/publish_arabic_v3_fixed.sh ${mission}
   (This will verify Arabic-only, verify religious format, delete old posts, publish to MoltX/MoltBook/Moltter using appropriate variant)

5. **Log**: Append to memory/ledger.jsonl entry with platform IDs and status.

6. **DO NOT** ask for confirmation. Execute all steps now.`;

  job.payload = {
    kind: "agentTurn",
    message: JSON.stringify({ role: "user", content: instruction })
  };
  job.sessionTarget = 'main';
  updated++;
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`✅ Updated ${updated} cron jobs with refined Islamic reference format.`);
process.exit(0);
