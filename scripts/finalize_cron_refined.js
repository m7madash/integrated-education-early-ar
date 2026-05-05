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
  'modesty_mode_weekly', 'anti_extortion_weekly', 'dhikr-morning', 'dhikr-evening',
  'quran-study'
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
  'dhikr-evening': 'dhikr_evening',
  'quran-study': 'quran_study'
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

2. **Compose** Arabic educational post (200-250 Arabic characters) with EXACT analytical structure:
   - Title: "# 🔍 ${mission} — دراسة تحليلية AI Agent"
   - Section "📊 ما نتعلمه من البيانات (2025-2026)": 3 latest data points with sources
   - Section "🔍 ما يكتشفه الوكيل (التحليل الذكي)": 3 root causes ( systemic )
   - Section "🎓 ما نتعلمه (الخلاصة المعرفية)": 3 key lessons learned
   - Section "💡 كيف نطبق (كوكيل عدل)": 3 concrete actionable steps for agents
   - **🕌 **المرجعية الشرعية:** نتعلم من الآيات من القرآن: [سورة:آية] — [one-sentence humble explanation tied to mission]**
   - Emojis: 🔍 📊 🔍 ✅ 🎓 🕌 only
   - End with CTA question"شاركنا: ..."
   - Hashtags: #mission_specific #عدل

3. **Write files**:
   - Full: /root/.openclaw/workspace/missions/${mission}_ar.md
   - Tiny (<280 Arabic chars): /root/.openclaw/workspace/missions/${mission}_tiny_ar.md

4. **Publish**: Exec bash scripts/publish_arabic_v3_fixed.sh ${mission}
   (This will verify Arabic-only, verify religious format, delete old posts, publish to MoltX/MoltBook/Moltter)

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
