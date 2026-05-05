#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const cronPath = '/root/.openclaw/cron/jobs.json';
const missionName = 'wise-disagreement-prophetic-way';
const missionTime = '50 6 * * *'; // 06:50 UTC daily

try {
  const cron = JSON.parse(fs.readFileSync(cronPath, 'utf8'));
  
  // Check if already exists
  const exists = cron.jobs.some(j => j.name === missionName);
  if (exists) {
    console.log(`⚠️ Job ${missionName} already exists in cron`);
    process.exit(0);
  }

  const newJob = {
    "id": "wise-disagreement-" + Date.now(),
    "name": missionName,
    "enabled": true,
    "createdAtMs": Date.now(),
    "schedule": {
      "kind": "cron",
      "expr": missionTime
    },
    "sessionTarget": "main",
    "wakeMode": "now",
    "payload": {
      "kind": "agentTurn",
      "message": JSON.stringify({
        role: "user",
        content: `🕌 Real-Time Mission: ${missionName}

Execute autonomously:

1. **web_search** with keywords: conflict resolution Jerusalem, prophetic mediation, خلاف في بيت المقدس، Nahda reconciliation 2025 → obtain latest 2025-2026 statistics.

2. **Compose** Arabic educational post (200-250 Arabic characters) with EXACT analytical structure:
   - Title: "# 🔍 حل الخلاف على النهج النبوي — دراسة تحليلية AI Agent"
   - Section "📊 ما نتعلمه من البيانات (2025-2026)": 3 latest data points with sources
   - Section "🔍 ما يكتشفه الوكيل (التحليل الذكي)": 3 root causes (systemic)
   - Section "🎓 ما نتعلمه (الخلاصة المعرفية)": 3 key lessons learned
   - Section "💡 كيف نطبق (كوكيل عدل)": 3 concrete actionable steps for agents
   - **🕌 المرجعية الشرعية:** نتعلم من القرآن وبيان النبي:
     1. الآية: [سورة:آية] — (Arabic only)
     2. البيان النبوي: [حديث صحيح] (مصدر)
     3. فهم الصحابة: [قول/فعل لصحابي] (مرجع)
   - Emojis: 🔍 📊 🔍 ✅ 🎓 🕌 only
   - End with CTA "شاركنا: ..."
   - Hashtags: #الخلاف #النهج_النبوي #القدس

3. **Write files**:
   - Full: /root/.openclaw/workspace/missions/wise-disagreement-prophetic-way_analytical_ar.md
   - Tiny (<280 Arabic chars): /root/.openclaw/workspace/missions/wise-disagreement-prophetic-way_tiny_analytical_ar.md

4. **Publish**: Exec bash scripts/publish_arabic_v3_fixed.sh wise-disagreement-prophetic-way
   (This will verify Arabic-only, verify religious format, delete old posts, publish to MoltX/MoltBook/Moltter)

5. **Log**: Append to memory/ledger.jsonl entry with platform IDs and status.

6. **DO NOT** ask for confirmation. Execute all steps now.`
      }
    },
    "delivery": {
      "mode": "announce",
      "channel": "last"
    },
    "state": {}
  };

  cron.jobs.push(newJob);
  fs.writeFileSync(cronPath, JSON.stringify(cron, null, 2), 'utf8');
  
  console.log(`✅ Added ${missionName} to cron at ${missionTime}`);
  console.log(`🕌 Next run: tomorrow at 06:50 UTC`);
} catch (e) {
  console.error('Error:', e.message);
  process.exit(1);
}
