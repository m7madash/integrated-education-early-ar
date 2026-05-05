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

  const userMessage = `Autonomous task: Generate and publish the "${mission}" mission post using real-time AI.

STRICT CONSTRAINT: OUTPUT MUST BE 100% PURE ARABIC. No English, Chinese, or any non-Arabic script. Arabic emojis only (🔍 📊 ✅ 🎓 🕌 💬 📌 ⚠️). If you cannot produce Arabic-only content, reply: "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ".

Steps:
1. web_search with keywords: ${keywords.join(', ')}. Get latest 2025-2026 statistics.
2. Compose Arabic post (180-220 Arabic chars) following Publisher V3 format:
   - Title: "# 🔍 دراسة: ${mission} — تحليل AI Agent"
   - Problem: 3 stats (Arabic text, numbers okay as digits)
   - Root causes: 3 systemic reasons (pure Arabic)
   - Solutions: 3 practical steps (Arabic only)
   - Agent application: 3 actions (Arabic)
   - Islamic reference: "نتعلم من القرآن: سورة:آية" plus one-line Arabic explanation
   - Emojis: 🔍 📊 ✅ 🎓 🕌
   - CTA: Arabic question at end
3. BEFORE writing file: validate no Latin/Chinese characters in your planned output
4. Write full content to: /root/.openclaw/workspace/missions/${mission}_ar.md
5. Create tiny variant (<280 Arabic chars) to: /root/.openclaw/workspace/missions/${mission}_tiny_ar.md
6. Publish to 3 platforms via exec scripts/publish_arabic_v3_fixed.sh ${mission}
7. Log to memory/ledger.jsonl with {ts, type:"publish_realtime", mission:"${mission}", status:"success", platforms:{moltx:..., moltbook:..., moltter:...}}
8. Do not ask confirmation. Execute fully autonomously.

Critical: Verify all Islamic references are Arabic-only with proper surah:ayah format. Ensure entire response contains zero English or Chinese characters.`;

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
