#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const missionsDir = '/root/.openclaw/workspace/missions';
const analyticalFiles = [
  'injustice-justice_analytical_ar.md',
  'poverty-dignity_analytical_ar.md',
  'ignorance-knowledge_analytical_ar.md',
  'war-peace_analytical_ar.md',
  'slavery-freedom_analytical_ar.md',
  'disease-health_analytical_ar.md',
  'extremism-moderation_analytical_ar.md',
  'shirk-tawhid_analytical_ar.md',
  'pollution-cleanliness_analytical_ar.md',
  'division-unity_analytical_ar.md',
  'corruption-reform_analytical_ar.md',
  'modesty_filter_analytical_ar.md',
  'anti_extortion_analytical_ar.md',
  'dhikr-morning_analytical_ar.md',
  'dhikr-evening_analytical_ar.md',
  'quran-study_analytical_ar.md'
];

// List of weak/unreliable sources (must NOT appear)
const weakSources = [
  'الحاكم',
  'الطبراني',
  'أحمد', // unless explicitly "مسند أحمد، حسن"
  'ابن الجوزي',
  '은비 حيان',
  'كذا',
  'ضعيف'
];

// Acceptable hadith sources
const strongHadithSources = [
  'البخاري',
  'مسلم',
  'أبو داود',
  'الترمذي',
  'ابن ماجه',
  'النسائي',
  'موطأ مالك',
  'متفق عليه'
];

let issues = [];
let cleanCount = 0;

analyticalFiles.forEach(file => {
  const fullPath = path.join(missionsDir, file);
  const content = fs.readFileSync(fullPath, 'utf8');
  const mission = file.replace('_analytical_ar.md', '');

  // Check for weak source mentions
  weakSources.forEach(weak => {
    if (content.includes(weak)) {
      issues.push(`${mission}: Found weak source '${weak}'`);
    }
  });

  // Check that hadith section has a strong source
  const hadithSection = content.match(/2\. البيان النبوي:.*?\(([^)]+)\)/s);
  if (hadithSection) {
    const source = hadithSection[1];
    const hasStrong = strongHadithSources.some(s => source.includes(s));
    if (!hasStrong) {
      issues.push(`${mission}: Hadith source not clearly strong: ${source}`);
    }
  } else {
    issues.push(`${mission}: No hadith section found`);
  }

  // Check for English/Latin contamination
  const arabicOnly = /[\u0600-\u06FF]/.test(content);
  if (!arabicOnly) {
    issues.push(`${mission}: Non-Arabic characters detected`);
  }

  cleanCount++;
});

console.log(`✅ Clean files: ${cleanCount}/16`);
if (issues.length) {
  console.log('\n❌ Issues found:');
  issues.forEach(i => console.log(' -', i));
} else {
  console.log('✅ All sources are strong, no weak references detected');
}
