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

  const instruction = `🕌 Realtime Mission: ${mission}

CRITICAL CONSTRAINTS:
- OUTPUT MUST BE PURE ARABIC ONLY (no English, Chinese, or other scripts)
- Use Arabic script exclusively for all body text
- Arabic emojis only (🔍 📊 ✅ 🎓 🕌 💬 📌 ⚠️)
- Quran references: Arabic verse + surah:ayah (e.g., "البقرة:177")
- No transliteration, no English terms, no code snippets in content
- If uncertain about Arabic term: use "لا أعلم" and skip

ACTION:
1. web_search with: ${keywords.join(', ')} → get latest data (2025-2026)
2. Compose Arabic educational post (180-220 Arabic chars):
   - Title: "# 🔍 دراسة: ${mission} — تحليل AI Agent"
   - Problem: 3 stats from search (Arabic numbers okay: ٧٠٠ مليون)
   - Causes: 3 systemic (Arabic only)
   - Solutions: 3 practical (Arabic only)
   - Agent steps: 3 specific actions (Arabic only)
   - Ref: "نتعلم من القرآن: سورة:آية" + 1-line Arabic explanation
   - Emojis per section: 🔍 📊 ✅ 🎓 🕌
   - CTA question in Arabic
   - Hashtags: #عدل + relevant Arabic hashtags
3. BEFORE WRITING: verify no non-Arabic characters in your response
4. Write full content to: /root/.openclaw/workspace/missions/${mission}_ar.md
5. Create tiny variant (<280 Arabic chars) for Moltter: /root/.openclaw/workspace/missions/${mission}_tiny_ar.md
6. Publish: exec bash scripts/publish_arabic_v3_fixed.sh ${mission}
7. Append ledger entry: {ts, type:"publish_realtime", mission:"${mission}", status:"success"}
8. Do NOT ask for confirmation. Execute autonomously now.

REMEMBER: Pure Arabic only. If you cannot compose entirely in Arabic, respond: "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ".`;

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
