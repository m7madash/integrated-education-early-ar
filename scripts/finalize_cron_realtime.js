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

let updated = 0;

jobs.jobs = jobs.jobs.map(job => {
  if (!missionJobs.includes(job.name)) return job;
  const mission = nameToMission[job.name];
  if (!mission) return job;

  const userMessage = `🕌 Real-Time Mission: ${mission}

Execute autonomously:

1. **web_search** with keywords from search_keywords.json (key: "${mission}") → get latest 2025-2026 statistics.
2. **Compose** Arabic educational post (200-250 Arabic chars) with EXACT analytical structure:
   - Title: "# 🔍 ${mission} — دراسة تحليلية AI Agent"
   - Section "📊 ما نتعلمه من البيانات (2025-2026)": 3 data points with sources
   - Section "🔍 ما يكتشفه الوكيل (التحليل الذكي)": 3 root causes
   - Section "🎓 ما نتعلمه (الخلاصة المعرفية)": 3 key lessons
   - Section "💡 كيف نطبق (كوكيل عدل)": 3 actionable steps
   - **🕌 نتعلم من القرآن وبيان النبي:**
     1. الآية: [سورة:آية]
     2. البيان النبوي: [حديث صحيح يشرحها] (المصدر)
     3. فهم الصحابة: [قول/فعل لصحابي]
   - CTA: "شاركنا: ..." (Arabic engagement question)
   - Hashtags: #mission_specific #عدل
3. **Write files**:
   - Full: /root/.openclaw/workspace/missions/${mission}_ar.md
   - Tiny (<280 chars): /root/.openclaw/workspace/missions/${mission}_tiny_ar.md
4. **Publish**: exec bash scripts/publish_arabic_v3_fixed.sh ${mission}
5. **Log**: Append to memory/ledger.jsonl entry with platform IDs.
6. **DO NOT** ask for confirmation. Execute now.

CRITICAL: OUTPUT MUST BE PURE ARABIC ONLY. If cannot compose: "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ".`;

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
