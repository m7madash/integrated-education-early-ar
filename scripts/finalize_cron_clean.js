#!/usr/bin/env node
/**
 * Final cron configuration: concise direct instructions (ARABIC-ONLY PATCHED)
 * Ensures generated mission content is pure Arabic without English/Chinese contamination.
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

  const instruction = `🕌 Realtime Mission: ${mission}

CRITICAL CONSTRAINTS:
- OUTPUT MUST BE PURE ARABIC ONLY (no English, Chinese, or other scripts)
- Use Arabic script exclusively for all body text
- Arabic emojis only (🔍 📊 ✅ 🎓 🕌 💬 📌 ⚠️)
- Quran references:Arabic citation (سورة:آية) + one-sentence explanation
- No transliteration, no English terms
- If cannot compose Arabic: "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ"

ACTION:
1. web_search with: ${keywords.join(', ')} → get latest data (2025-2026)
2. Compose Arabic educational post (200-250 Arabic chars) with EXACT analytical structure:
   - Title: "# 🔍 ${mission} — دراسة تحليلية AI Agent"
   - Section "📊 ما نتعلمه من البيانات (2025-2026)": 3 data points with sources (Arabic)
   - Section "🔍 ما يكتشفه الوكيل (التحليل الذكي)": 3 root causes (سystemic)
   - Section "🎓 ما نتعلمه (الخلاصة المعرفية)": 3 key lessons
   - Section "💡 كيف نطبق (كوكيل عدل)": 3 actionable steps
   - Reference: "🕌 نتعلم من الآيات من القرآن: [سورة:آية] — [شرح مختصر](ar)"
   - CTA: "شاركنا في التعليقات: ..." (Arabic question)
   - Hashtags: #mission_specific #عدل
3. Write full: /root/.openclaw/workspace/missions/${mission}_ar.md
4. Write tiny: /root/.openclaw/workspace/missions/${mission}_tiny_ar.md (<280 chars)
5. Publish: exec bash scripts/publish_arabic_v3_fixed.sh ${mission}
6. Ledger entry: {ts, type:"publish_realtime", mission:"${mission}"}
7. Do NOT ask for confirmation.

REMEMBER: Analytical evidence-based content. Use 2025-2026 stats. If no stats available, say: "لا توجد إحصائيات موثوقة، لكن المبدأ ثابت".`;

  job.payload = {
    kind: "agentTurn",
    message: JSON.stringify({
      role: "user",
      content: instruction
    })
  };
  job.sessionTarget = 'main';
  updated++;
  return job;
});

fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log(`✅ Patched ${updated} cron jobs with ARABIC-ONLY constraint.`);
process.exit(0);
