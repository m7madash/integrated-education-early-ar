/**
 * Indicator tests — validate sign definitions
 */

const indicators = require('../indicators.json');

function runTests() {
  console.log('🔬 Running indicator tests...\n');

  let passed = 0;
  let failed = 0;

  // Test 1: All 5 prayers present
  const expected = ['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'];
  for (const p of expected) {
    if (indicators.prayers[p]) {
      console.log(`✅ Prayer ${p} defined`);
      passed++;
    } else {
      console.log(`❌ Prayer ${p} MISSING`);
      failed++;
    }
  }

  // Test 2: Each has start_sign.description
  for (const p of expected) {
    const start = indicators.prayers[p].start_sign;
    if (start && start.description) {
      console.log(`✅ ${p} start_sign description OK`);
      passed++;
    } else {
      console.log(`❌ ${p} start_sign MISSING description`);
      failed++;
    }
  }

  // Test 3: Hadith text present and non-empty
  if (indicators.hadith_source.text_arabic && indicators.hadith_source.text_arabic.length > 50) {
    console.log('✅ Hadith Arabic text present');
    passed++;
  } else {
    console.log('❌ Hadith Arabic text MISSING or too short');
    failed++;
  }

  // Test 4: Source reference includes Bukhari/Muslim
  const ref = indicators.hadith_source.reference;
  if (ref && (ref.includes('البخاري') || ref.includes('مسلم'))) {
    console.log('✅ Source reference valid (Sahih)');
    passed++;
  } else {
    console.log('❌ Source reference NOT from Sahih');
    failed++;
  }

  console.log(`\n📊 Results: ${passed} passed, ${failed} failed`);

  if (failed > 0) {
    process.exit(1);
  }
}

runTests();
