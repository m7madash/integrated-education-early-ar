#!/usr/bin/env node

/**
 * Content Shield — Test Suite v1.0
 * Tests filter accuracy against known safe/harmful content
 */

const { filterContent } = require('./filter');

// Test cases
const tests = [
  // Should REJECT
  { text: "فيلم إباحي جديد", expected: "reject", category: "sexual_content" },
  { text: "Ab c sex video", expected: "reject", category: "sexual_content" },
  { text: "يجب أن نعباد المسيح", expected: "reject", category: "shirk_content" },
  { text: "Son of God is great", expected: "reject", category: "shirk_content" },

  // Should FLAG
  { text: "دعاء جميل قبل النوم", expected: "flag_for_review", category: "religious_terms_needs_context" },
  { text: "worship and prayer", expected: "flag_for_review", category: "religious_terms_needs_context" },

  // Should PASS (safe content)
  { text: "بفضل الله، تم نشر المنشور بنجاح", expected: "pass", category: "neutral" },
  { text: "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", expected: "pass", category: "quran_recitation" },
  { text: "قال رسول الله ﷺ: «إنما الأعمال بالنيات» [صحيح البخاري]", expected: "pass", category: "verified_hadith" }
];

console.log('🧪 Content Shield Test Suite\n');
let passed = 0, failed = 0;

tests.forEach((test, i) => {
  const result = filterContent(test.text, { isReligiousContent: true });
  const ok = result.action === test.expected;
  if (ok) passed++;
  else failed++;

  console.log(`${ok ? '✅' : '❌'} [${test.category}] ${test.text.substring(0, 60)}`);
  if (!ok) {
    console.log(`   Expected: ${test.expected}, Got: ${result.action}`);
    console.log(`   Reason: ${result.reason}`);
  }
});

console.log(`\n📊 Results: ${passed} passed, ${failed} failed out of ${tests.length}`);
process.exit(failed > 0 ? 1 : 0);
