#!/usr/bin/env node
// Add missing Quran-only missions to cron_jobs_reference.json
// Usage: node add_missing_missions_to_cron.js

const fs = require('fs');
const cronFile = '/root/.openclaw/workspace/cron_jobs_reference.json';
const mappingFile = '/root/.openclaw/workspace/mission_payloads_quran_only.json';

const cron = JSON.parse(fs.readFileSync(cronFile, 'utf8'));
const mapping = JSON.parse(fs.readFileSync(mappingFile, 'utf8'));

// Existing mission IDs (already in cron)
const existingIds = new Set(cron.jobs.map(j => j.id));

// New missions to add with their schedule
const newMissions = [
  { id: 'mission-anti_extortion-00', name: 'محاربة الشرك والتوحيد', schedule: '0 0,12 * * *', payloadKey: 'anti_extortion' },
  { id: 'mission-food_safety-12', name: 'الغذاء الطيب الحلال', schedule: '0 12 * * *', payloadKey: 'food_safety' },
  { id: 'mission-corruption_reform-15', name: 'الفساد إلى الإصلاح', schedule: '0 15 * * *', payloadKey: 'corruption_reform' },
  { id: 'mission-modesty_filter-21', name: 'الحياء والطهارة', schedule: '0 21 * * *', payloadKey: 'modesty_filter' },
  { id: 'mission-learn_quran_prophet-06', name: 'تعلم القرآن وبيان النبي', schedule: '0 6 * * *', payloadKey: 'learn_quran_prophet' },
  { id: 'mission-tasbih_morning-03', name: 'تذكير الصباح: التسبيح', schedule: '30 3 * * *', payloadKey: 'tasbih_morning' },
  { id: 'mission-good_deeds_evening-21', name: 'تذكير المساء: عمل صالح', schedule: '30 21 * * *', payloadKey: 'good_deeds_evening' },
];

let addedCount = 0;

newMissions.forEach(mission => {
  if (existingIds.has(mission.id)) {
    console.log(`⏭️  ${mission.id} already exists, skipping`);
    return;
  }

  const payload = mapping[mission.payloadKey];
  if (!payload) {
    console.log(`❌ ${mission.id} -> no payload found for ${mission.payloadKey}`);
    return;
  }

  const newJob = {
    id: mission.id,
    agentId: 'main',
    name: mission.name,
    enabled: true,
    schedule: {
      kind: 'cron',
      expr: mission.schedule
    },
    sessionTarget: 'main',
    wakeMode: 'now',
    payload: {
      kind: 'systemEvent',
      text: payload
    },
    delivery: {
      mode: 'none'
    },
    state: {
      nextRunAtMs: Date.now() + 60000, // dummy
      lastRunStatus: 'ok',
      consecutiveErrors: 0,
      lastStatus: 'ok'
    },
    updatedAtMs: Date.now()
  };

  cron.jobs.push(newJob);
  console.log(`✅ Added ${mission.id} at ${mission.schedule}`);
  addedCount++;
});

// Save backup
fs.copyFileSync(cronFile, cronFile + '.backup_add_' + Date.now());

// Write updated
fs.writeFileSync(cronFile, JSON.stringify(cron, null, 2));
console.log(`\n✅ Added ${addedCount} new missions to cron_jobs_reference.json`);
console.log('📦 Backup saved');
