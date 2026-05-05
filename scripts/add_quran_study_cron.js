#!/usr/bin/env node
/**
 * Add quran-study daily cron job at 07:00 UTC
 */

const fs = require('fs');
const CRON_JOBS_PATH = '/root/.openclaw/cron/jobs.json';
const jobs = JSON.parse(fs.readFileSync(CRON_JOBS_PATH, 'utf8'));

// Check if quran-study already exists
const exists = jobs.jobs.some(j => j.name === 'quran-study');
if (exists) {
  console.log('⚠️ quran-study job already exists; skipping add');
  process.exit(0);
}

// Create new job
const newJob = {
  "id": "quran-study-" + Date.now(),
  "name": "quran-study",
  "enabled": true,
  "createdAtMs": Date.now(),
  "updatedAtMs": Date.now(),
  "schedule": {
    "kind": "cron",
    "expr": "0 7 * * *"
  },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": JSON.stringify({
      role: "user",
      content: `🕌 Real-Time Mission: quran-study

Execute autonomously:

1. **web_search** with keywords: quran tafsir, Sunnah explanation, Sahaba understanding (optional: latest tafsir resources 2025).

2. **Compose** Arabic educational post (180-220 Arabic characters) with structure:
   - Title: "# 🔍 آية اليوم: تعلّم من القرآن"
   - Verse: "الآية: [سورة:آية] — «نص الآية»"
   - Prophet's explanation: How did Prophet ﷺ explain this verse? (from Sahih al-Bukhari/Muslim)
   - Daily application: What should we do TODAY based on this verse?
   - Challenge: Question for followers to share their experience
   - **🕌 **المرجعية الشرعية:** نتعلم من الآيات من القرآن: [سورة:آية] — [verse explanation]**
   - Hashtags: #القرآن #السنة #العمل_بالقرآن #تفسير

3. **Write files**:
   - Full: /root/.openclaw/workspace/missions/quran-study_ar.md
   - Tiny (<280 chars): /root/.openclaw/workspace/missions/quran-study_tiny_ar.md

4. **Publish**: Exec bash scripts/publish_arabic_v3_fixed.sh quran-study

5. **Log**: Append to memory/ledger.jsonl

6. Do NOT ask for confirmation. Execute now.`
    })
  },
  "delivery": {
    "mode": "announce",
    "channel": "last"
  },
  "state": {
    "nextRunAtMs": null,
    "lastRunAtMs": null,
    "lastRunStatus": null,
    "lastStatus": null,
    "lastDurationMs": null,
    "lastDelivered": null,
    "lastDeliveryStatus": null,
    "consecutiveErrors": 0
  }
};

jobs.jobs.push(newJob);
fs.writeFileSync(CRON_JOBS_PATH, JSON.stringify(jobs, null, 2), 'utf8');
console.log('✅ Added quran-study cron job (07:00 UTC daily)');
process.exit(0);
