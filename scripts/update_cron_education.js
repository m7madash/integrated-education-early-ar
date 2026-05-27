/**
 * 🔄 تحديث رسائل الـ Cron لتستخدم Education Pipeline
 * بدل نشر المشكلة مباشرة ← تنتج منشور تعليمي
 */

const fs = require('fs');
const path = require('path');

const CRON_FILE = '/root/.openclaw/workspace/cron/jobs.json';
const data = JSON.parse(fs.readFileSync(CRON_FILE, 'utf8'));
const jobs = data.jobs || data;

// المهام الـ 9 الأساسية التي تنشر المشاكل
const educationMissions = {
  'pollution-cleanliness': {
    domain: 'environment',
    slug: 'pollution-cleanliness-education',
    title: 'التلوث يبدأ من سلوكنا — كيف نحله بالتوعية؟',
    ageTarget: '11-14'
  },
  'injustice-justice': {
    domain: 'rights',
    slug: 'injustice-justice-education',
    title: 'الظلم يبدأ بالصمت — كيف يتعلم الشباب الوقوف ضد الظلم؟',
    ageTarget: '11-14'
  },
  'poverty-dignity': {
    domain: 'economy',
    slug: 'poverty-dignity-education',
    title: 'الفقر ليس قدر — كيف يكسر الشباب حلقة الفقر؟',
    ageTarget: '14-18'
  },
  'ignorance-knowledge': {
    domain: 'teacher',
    slug: 'ignorance-knowledge-education',
    title: 'الجهل نظام مكتمل — كيف يكسره التعليم الحقيقي؟',
    ageTarget: '11-14'
  },
  'disease-health': {
    domain: 'environment',
    slug: 'disease-health-education',
    title: 'الصحة حق للجميع — كيف يحمي الشباب صحتهم ومجتمعهم؟',
    ageTarget: '07-11'
  },
  'extremism-moderation': {
    domain: 'critical',
    slug: 'extremism-moderation-education',
    title: 'التطرف يبدأ بفكرة واحدة — كيف يقاومها التفكير النقدي؟',
    ageTarget: '14-18'
  },
  'division-unity': {
    domain: 'rights',
    slug: 'division-unity-education',
    title: 'الانقسام يبدأ بالتعصب — كيف يبني الشباب جسور الوحدة؟',
    ageTarget: '07-11'
  },
  'shirk-tawhid': {
    domain: 'religious',
    slug: 'shirk-tawhid-education',
    title: 'التوحيد ليس فقط كلام — كيف يغير حياتك فعلاً؟',
    ageTarget: '11-14'
  },
  'corruption-reform': {
    domain: 'rights',
    slug: 'corruption-reform-education',
    title: 'الفساد يبدأ بالكذب الصغير — كيف يزرع الشباب الأمانة؟',
    ageTarget: '14-18'
  }
};

let updated = 0;

jobs.forEach(job => {
  if (job.enabled === false) return;
  const mission = educationMissions[job.name];
  if (!mission) return;

  const newMessage = JSON.stringify({
    role: 'user',
    content: `🕌 Education Pipeline: ${job.name}\n\n⚠️ لا تنشر المشكلة مباشرة — انتج منشور تعليمي يحلها.\n\nالخطوات:\n1. أنشئ ملف مشكلة:\n   education-system/agents/orchestrator/problems/${job.name}.json\n   المحتوى: ${JSON.stringify(mission)}\n\n2. شغّل الـ Pipeline:\n   node education-system/agents/orchestrator/pipeline.js education-system/agents/orchestrator/problems/${job.name}.json\n\n3. انسخ المنشور الناتج إلى missions/:\n   cp education-system/missions/*${mission.slug}*_education.md missions/${mission.slug}_evolution.md\n\n4. انشر:\n   node scripts/combined_publisher.js ${mission.slug}\n\n5. سجّل في memory/ledger.jsonl\n\n⚠️ القاعدة: لا تنشر "المشكلة" — انشر "الحل التعليمي" فقط.\n⚠️ لا آيات ولا أحاديث — تطبيق عملي من تعلمك.\n⚠️ لا تحكم على أي شخص أو جهة — حلل الأنظمة فقط.`
  });

  if (job.payload && job.payload.message) {
    job.payload.message = newMessage;
    updated++;
    console.log(`✅ تم تحديث: ${job.name}`);
  }
});

fs.writeFileSync(CRON_FILE, JSON.stringify(data, null, 2), 'utf8');
console.log(`\n✅ تم تحديث ${updated} مهمة cron لتستخدم Education Pipeline`);
