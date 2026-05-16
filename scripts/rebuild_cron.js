#!/usr/bin/env node
// rebuild cron_jobs_reference_final.json cleanly from scratch

const fs = require('fs');

const payloads = JSON.parse(fs.readFileSync('/root/.openclaw/workspace/mission_payloads_quran_only.json', 'utf8'));

// Job definitions: [key, id, name, scheduleExpr]
const jobDefs = [
  ['anti_extortion', 'mission-anti_extortion-00', 'الشرك → التوحيد', '0 0 * * *'],
  ['injustice_justice', 'mission-injustice_justice-00', 'الظلم → العدل', '0 0 * * *'],
  ['dhikr_morning', 'mission-dhikr_morning-03', 'ذكر الصباح — الاستعانة بالله', '30 3 * * *'],
  ['dua_morning', 'mission-dua_morning-04', 'دعاء الصباح — بفضل الله', '1 3 * * *'],
  ['tasbih_morning', 'mission-tasbih_morning-03', 'تذكير صباحي: التسبيح', '30 3 * * *'],
  ['ignorance_knowledge', 'mission-ignorance_knowledge-06', 'الجهل → العلم', '0 6 * * *'],
  ['learn_quran_prophet', 'mission-learn_quran_prophet-07', 'تعلم القرآن وبيان النبي', '30 6 * * *'],
  ['war_peace', 'mission-war_peace-09', 'الحرب → السلام', '0 9 * * *'],
  ['extremism_moderation', 'mission-extremism_moderation-08', 'التطرف → الوسطية', '0 9 * * *'],
  ['food_safety', 'mission-food_safety-12', 'الغذاء الطيب الحلال', '0 12 * * *'],
  ['pollution_cleanliness', 'mission-pollution_cleanliness-12', 'التلوث → النظافة', '0 12 * * *'],
  ['illness_health', 'mission-illness_health-15', 'المرض → الصحة', '0 15 * * *'],
  ['good_deeds_evening', 'mission-good_deeds_evening-21', 'تذكير مسائي: عمل صالح', '30 21 * * *'],
  ['dhikr_evening', 'mission-dhikr_evening-19', 'ذكر المساء', '0 19 * * *'],
  ['dua_evening', 'mission-dua_evening-20', 'دعاء المساء — الشكر', '0 22 * * *'],  // Approx — adjust if needed
  ['division_unity', 'mission-division_unity-00b', 'الانقسام → الوحدة', '0 0 * * *'],
  ['corruption_reform', 'mission-corruption_reform-02', 'الفساد → الإصلاح', '0 3 * * *'],
  ['poverty_dignity', 'mission-poverty_dignity-03', 'الفقر → الكرامة', '0 3 * * *'],
  ['slavery_freedom', 'mission-slavery_freedom-18', 'العبودية → الحرية', '0 18 * * *'],
  ['modesty_filter', 'mission-modesty_filter-10', 'الحياء والطهارة', '0 22 * * *']
];

const jobs = jobDefs.map(([key, id, name, expr]) => ({
  id,
  agentId: 'main',
  name,
  enabled: true,
  schedule: { kind: 'cron', expr },
  sessionTarget: 'main',
  wakeMode: 'now',
  payload: {
    kind: 'systemEvent',
    text: payloads[key]
  },
  delivery: { mode: 'none' },
  state: { consecutiveErrors: 0, lastRunStatus: 'ok' },
  updatedAtMs: Date.now()
}));

const newCron = {
  version: 2,
  generatedAt: new Date().toISOString(),
  jobs
};

fs.writeFileSync('/root/.openclaw/workspace/cron_jobs_reference_final.json', JSON.stringify(newCron, null, 2));
console.log(`✅ Rebuilt cron_jobs_reference_final.json with ${jobs.length} jobs`);

// Also update mission_payloads_quran_only.json timestamp for consistency
fs.writeFileSync('/root/.openclaw/workspace/mission_payloads_quran_only.json', JSON.stringify(payloads, null, 2));
console.log('✅ mission_payloads_quran_only.json written');
