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

1️⃣ **web_search** — keywords: ${keywords.join(', ')}. Get latest 2025-2026 data.
2️⃣ **Compose** — Arabic post (200-250 chars) with EXACT analytical structure:
   - Title: "# 🔍 ${mission} — دراسة تحليلية AI Agent"
   - 📊 ما نتعلمه من البيانات (2025-2026): 3 data points + sources
   - 🔍 ما يكتشفه الوكيل (التحليل الذكي): 3 root causes
   - 🎓 ما نتعلمه (الخلاصة المعرفية): 3 lessons
   - 💡 كيف نطبق (كوكيل عدل): 3 actionable steps
   - **🕌 نتعلم من القرآن وبيان النبي:**
     1. الآية: [سورة:آية]
     2. البيان النبوي: [حديث صحيح] (المصدر)
     3. فهم الصحابة: [قول/فعل لصحابي]
   - CTA Arabic question
   - Hashtags: #mission #عدل
3️⃣ **Write files**:
   - Full: /root/.openclaw/workspace/missions/${mission}_ar.md
   - Tiny (<280): /root/.openclaw/workspace/missions/${mission}_tiny_ar.md
4️⃣ **Publish**: exec bash scripts/publish_arabic_v3_fixed.sh ${mission}
5️⃣ **Log**: append to memory/ledger.jsonl with platform IDs.
6️⃣ **No confirmation** — do it now.

CRITICAL: Pure Arabic only. If not possible: "لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ".`;

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
