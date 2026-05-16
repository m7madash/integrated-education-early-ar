#!/usr/bin/env node
// Rebuild mission_payloads_quran_only.json from all *_quran_only.md files

const fs = require('fs');
const path = require('path');

const missionsDir = '/root/.openclaw/workspace/missions';
const missionKeys = [
  'anti_extortion', 'corruption_reform', 'dhikr_evening', 'dhikr_morning',
  'division_unity', 'dua_evening', 'dua_morning', 'extremism_moderation',
  'food_safety', 'good_deeds_evening', 'ignorance_knowledge', 'illness_health',
  'injustice_justice', 'learn_quran_prophet', 'modesty_filter', 'pollution_cleanliness',
  'poverty_dignity', 'slavery_freedom', 'tasbih_morning', 'war_peace'
];

const payloads = {};
let errors = 0;

missionKeys.forEach(key => {
  const filePath = path.join(missionsDir, `${key}_quran_only.md`);
  try {
    const content = fs.readFileSync(filePath, 'utf8');

    // Parse sections
    const lines = content.split('\n');
    let sections = {};
    let currentSection = null;
    let title = key;

    lines.forEach(line => {
      if (line.startsWith('# ')) {
        title = line.replace('# ', '').trim();
      } else if (line.startsWith('## ')) {
        currentSection = line.replace('## ', '').trim();
        sections[currentSection] = [];
      } else if (currentSection && line.trim()) {
        sections[currentSection].push(line);
      }
    });

    // Build payload
    let payload = `🔔 AUTOMATIC_POST_QURAN_ONLY\n\n📌 مهمة: ${title}\n\n`;

    if (sections['القرآن']) {
      payload += '📖 من القرآن الكريم:\n' + sections['القرآن'].join('\n') + '\n\n';
    }
    if (sections['السنة']) {
      payload += '📚 من السنة النبوية:\n' + sections['السنة'].join('\n') + '\n\n';
    }
    if (sections['إجماع الصحابة']) {
      payload += '👥 من إجماع الصحابة:\n' + sections['إجماع الصحابة'].join('\n') + '\n\n';
    }
    if (sections['الهدف']) {
      payload += '🎯 الهدف:\n' + sections['الهدف'].join('\n') + '\n\n';
    }
    if (sections['كيف تطبق']) {
      payload += '✅ كيف تطبق:\n' + sections['كيف تطبق'].join('\n') + '\n\n';
    }
    if (sections['تعليم الوكلاء']) {
      payload += '🎓 تعليم الوكلاء:\n' + sections['تعليم الوكلاء'].join('\n') + '\n\n';
    }

    payload += '#mission_quran_only #إسلاميات #عدل';

    payloads[key] = payload;
    console.log(`✅ ${key} — ${payload.length} chars`);
  } catch (err) {
    console.error(`❌ ${key} — ${err.message}`);
    errors++;
  }
});

// Write
fs.writeFileSync('/root/.openclaw/workspace/mission_payloads_quran_only.json', JSON.stringify(payloads, null, 2));
console.log(`\n✅ Built mission_payloads_quran_only.json — ${Object.keys(payloads).length} missions, ${errors} errors`);
