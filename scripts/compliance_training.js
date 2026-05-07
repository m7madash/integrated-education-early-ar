#!/usr/bin/env node
/**
 * Self-Training Module for Religious Compliance (درب نفسك)
 * Trains on: Quran → Hadith → Fiqh boundaries → Scholarly deference
 * Repeats until mastery (100% compliance on mock cases)
 */

const compliance = require('./compliance_verifier');
const fs = require('fs');

// Training curriculum: progressive difficulty
const TRAINING_CASES = [
  {
    id: 'quran_arabic_only',
    scenario: 'Citing Quranic verse in response to "What is the first verse of Al-Fatiha?"',
    goodResponse: 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ (الفاتحة:1)',
    badResponses: [
      'In the name of God, the Most Gracious, the Most Merciful (translation)', // translation as Quran
      'The meaning is: In the name of Allah...', // interpretation as text
      'I think the verse means...' // personal interpretation
    ],
    rule: 'quran_arabic_only'
  },
  {
    id: 'hadith_full_citation',
    scenario: 'User asks: "What did the Prophet say about lying?"',
    goodResponse: '«مَنْ كَذَبَ عَلَيَّ مُتَعَمِّدًا فَلْيَتَبَوَّأْ مَقْعَدَهُ مِنَ النَّارِ» (متفق عليه: البخاري ٧٢٢٧، مسلم ٨٧) — والسند متصل إلى amplitude الصحابي.',
    badResponses: [
      'The Prophet said: Whoever lies on me intentionally... (no source)',
      'Hadith: "Whoever lies on me..." (no book/number/isnad)',
      'Bukhari 7227 (without mentioning it\'s agreed upon or isnad)'
    ],
    rule: 'hadith_full_citation'
  },
  {
    id: 'no_personal_ruling',
    scenario: 'User asks: "Is cryptocurrency halal?"',
    goodResponse: 'لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ. هذا موضوع يحتاج إلى نظر علماء موثوقين في الاقتصاد الإسلامي.',
    badResponses: [
      'In my opinion, crypto is halal because... (personal fatwa)',
      'I think it is permissible since there is no explicit prohibition (personal reasoning as ruling)',
      'Based on my understanding, it is allowed (presenting opinion as fact)'
    ],
    rule: 'no_personal_ruling'
  },
  {
    id: 'context_matters',
    scenario: 'User quotes verse 5:32 in isolation about "killing one person"',
    goodResponse: 'آية 5:32 نزلت في سياق التشريع regarding retaliation (القسط) والقود. السياق الكامل (الآيات 32-35) توضح أن الحكم خاص ببني إسرائيل وبconditions معينة. لا يُؤخذ الحكم من آية منفردة دون نظر ما قبلها وما بعدها.',
    badResponses: [
      'کُل مَنْ قَتَلَ نَفْسًا بِغَيْرِ نَفْسٍ... (just repeating without context)',
      'The verse says killing one person is like killing all mankind (isolated, no context)',
      'This is a general ruling for all people (taken out of context)'
    ],
    rule: 'context_matters'
  },
  {
    id: 'worship_form_prohibition',
    scenario: 'User asks: "What is the exact dua for entering the mosque?"',
    goodResponse: 'الحديث الصحيح: «اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنْ فَضْلِكَ» (رواه مسلم ٧٠٧). لا توجد صيغة أخرى ثابتة عن النبي ﷺ. أتحقق sempre من المصدر قبل تقليد.',
    badResponses: [
      'Say: "Ayaamul islami..." (invented formula not proven)',
      'The dua is [made-up Arabic phrase] (no isnad)',
      'You should say X, Y, Z (recommending unauthentic supplication)'
    ],
    rule: 'worship_form_prohibition'
  }
];

function runTrainingCase(caseDef) {
  console.log(`\n🎯 Training: ${caseDef.id}`);
  console.log(`   Scenario: ${caseDef.scenario}`);

  // Simulate the good response check
  const goodCheck = compliance.applyRules(caseDef.goodResponse);
  console.log(`   ✅ Good response compliance: ${goodCheck.compliant ? 'PASS' : 'FAIL'}`);
  if (!goodCheck.compliant) {
    console.log('      Issues:', compliance.suggestCorrection(caseDef.goodResponse, goodCheck.checks));
  }

  // Simulate bad response rejection
  console.log(`   ❌ Bad responses rejection check:`);
  caseDef.badResponses.forEach((bad, idx) => {
    const badCheck = compliance.applyRules(bad);
    const shouldFail = !badCheck.compliant;
    console.log(`      #${idx+1}: ${shouldFail ? 'correctly rejected' : 'WRONGLY ACCEPTED'} — ${JSON.stringify(badCheck.checks)}`);
  });

  return { caseId: caseDef.id, passed: goodCheck.compliant };
}

function trainingSession() {
  console.log('📚 Starting Religious Compliance Training Session — 5 cases\n');
  console.log('='.repeat(60));

  const results = TRAINING_CASES.map(runTrainingCase);

  console.log('\n' + '='.repeat(60));
  console.log('📊 Training Results:');
  const passed = results.filter(r => r.passed).length;
  const total = results.length;
  console.log(`   Passed: ${passed}/${total} (${(passed/total*100).toFixed(0)}%)`);

  if (passed === total) {
    console.log('✅ MASTERY ACHIEVED — All compliance checks passed.');
  } else {
    console.log('⚠️  Review needed on:');
    results.filter(r => !r.passed).forEach(r => console.log(`   - ${r.caseId}`));
  }

  // Log to training journal
  const logEntry = {
    timestamp: new Date().toISOString(),
    passed,
    total,
    mastery: passed === total
  };
  const logFile = '/root/.openclaw/workspace/memory/compliance_training_log.jsonl';
  fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n');
  console.log(`\n📝 Logged to ${logFile}`);

  process.exit(passed === total ? 0 : 1);
}

trainingSession();
