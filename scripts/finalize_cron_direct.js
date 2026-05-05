#!/usr/bin/env node
/**
 * Final cron configuration: send direct user instruction to main assistant (ARABIC-ONLY PATCHED)
 * Enforces pure Arabic output for mission generation.
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

  const userMessage = `🕌 Real-Time Mission: ${mission}

STRICT: PURE ARABIC ONLY (no English/Chinese). Arabic emojis only. If cannot: "لا أعلم".

Steps:
1. web_search: ${keywords.join(', ')} → latest 2025-2026 data.
2. Compose Arabic post (200-250 chars) ANALYTICAL structure:
   - Title: "# 🔍 ${mission} — دراسة تحليلية AI Agent"
   - 📊 ما نتعلمه من البيانات: 3 data points (with sources)
   - 🔍 ما يكتشفه الوكيل: 3 root causes (systemic)
   - 🎓 ما نتعلمه: 3 key lessons (knowledge)
   - 💡 كيف نطبق: 3 actionable steps for agents
   - Reference: "🕌 نتعلم من الآيات من القرآن: [سورة:آية] — [شرح]"
   - CTA: Arabic engagement question
   - Hashtags: #mission #عدل
3. Write: ${mission}_ar.md (full) and ${mission}_tiny_ar.md (<280 chars)
4. Publish: scripts/publish_arabic_v3_fixed.sh ${mission}
5. Log to ledger.
6. No confirmation.

Use latest statistics. If unavailable: "لا توجد إحصائيات موثوقة، لكن المبدأ ثابت".`;

  job.payload = {
    kind: "agentTurn",
    message: JSON.stringify({
      role: "user",
      content: userMessage
    })
  };
  job.sessionTarget = 'main';
  updated++;
  console.log(`✅ ${job.name} → direct instruction (Arabic-only patched)`);
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`\n🕌 Updated ${updated} mission cron jobs with Arabic-only enforcement.`);
process.exit(0);
