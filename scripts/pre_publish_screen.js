#!/usr/bin/env node
/**
 * pre_publish_screen.js — Pre-Publish Religious Content Gate
 * Scans a mission file before publication. Exits non-zero if any
 * Quranic verse citation, hadith collection name, or structural religious
 * reference block is found.
 *
 * Design decisions:
 *  - Bracket-format citations [سورة X:Y], [البقرة:168] etc. → blocked
 *  - Hadith-collection names (صحيح البخاري, سنن الترمذي…) → blocked
 *  - Structural markers (القرآن:, الحديث:, المرجعية الشرعية) → blocked
 *  - Bare Arabic surah-name:ayah refs (النور:30) → blocked via whitelist
 *  - «...» arabic guillemets → NOT blocked (too many FALSE positives in
 *    editorial Arabic: "«لا إله إلا الله»", "«invalid_id»", CSS class names,
 *    label formatting — none are actual religious citations; the brackets
 *    above already catch real citation syntax. Removing «...» gate 2026-05-17.)
 *
 * Usage:  node scripts/pre_publish_screen.js <mission-name>
 * Returns: 0 = clean, 1 = blocked, 2 = file missing
 */

const fs = require('fs');
const path = require('path');

const MISSION = process.argv[2];
const BASE = '/root/.openclaw/workspace';
const FILE = path.join(BASE, 'missions', `${MISSION}_analytical_ar.md`);

const BLOCKED = [
  /\[سورة\s+\w+:\s*\d+\]/gi,    // [سورة النور: 30]
  /\[.*:\d+\]/gi,                // [البقرة:168], [Foo:123] etc.
  /صحيح\s*(البخاري|مسلم)/gi,    // صحيح البخاري / صحيح مسلم
  /سنن\s*(الترمذي|ابن ماجة)/gi,
  /مسند\s*(أحمد)/gi,
  /موطأ\s*(مالك)/gi,
  /أبو\s+داود/gi,
  /النسائي/gi,
  /ابن\s+ماجة/gi,
  /متفق\s+عليه/gi,
  /القرآن:/gi,                  // structural heading prefix
  /الحديث:/gi,                  // structural heading prefix
  /المرجعية\s+الشرعية/gi,       // reference-section header
];

// ========== QURAN VERSE REFERENCE GUARD ==========
// Detects bare inline Quranic refs like النور:30, البقرة:168 without brackets.
// Uses a whitelist of Quran surah names to avoid FPs from data tables.
// Update SURAH_NAMES when a new real surah ref is added to mission files.
const SURAH_NAMES = [
  'الفاتحة','البقرة','آل عمران','النساء','المائدة','الأنعام','الأعراف','الأنفال',
  'التوبة','يونس','هود','يوسف','الرعد','إبراهيم','الحجر','النحل','الإسراء',
  'الكهف','مريم','طه','الأنبياء','الحج','المؤمنون','النور','الفرقان','الشعراء',
  'النمل','القصص','العنكبوت','الروم','لقمان','السجدة','الأحزاب','سبأ','فاطر',
  'يس','الصافات','ص','الزمر','غافر','فصلت','الشورى','الزخرف','الدخان','الجاثية',
  'الأحقاف','محمد','الفتح','الحجرات','ق','الذاريات','الطور','النجم','القمر',
  'الرحمن','الواقعة','الحديد','المجادلة','الحشر','الممتحنة','الصف','الجمعة',
  'المنافقون','التغابن','الطلاق','التحريم','الملك','القلم','الحاقة','المعارج',
  'نوح','الجن','المزمل','المدثر','القيامة','الإنسان','المرسلات','النبأ','النازعات',
  'عبس','التكوير','الانفطار','المطففين','الانشقاق','البروج','الطارق','الأعلى',
  'الغاشية','الفجر','البلد','الشمس','الليل','الضحى','الشرح','التين','العلق',
  'القدر','البينة','الزلزلة','العاديات','القارعة','التكاثر','العصر','الهمزة',
  'الفيل','قريش','ماعون','الكوثر','الكافرون','النصر','المسد',
];
const SURAH_PAT = new RegExp(SURAH_NAMES.map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'g');

function checkSurahRefs(content) {
  const found = [];
  // inline or standalone: [punct/space] + surah-name + colon + verse-number
  // Does NOT match data-table hits like "البيانات: 7" (البيانات not in list)
  const bareRef = /(?:^|[\s\u00A0\u202F،؛.!؟()\[\-])([\u0600-\u06FF]{2,15})\s*:\s*(\d+)/g;
  let m;
  while ((m = bareRef.exec(content)) !== null) {
    const word = m[1].trim();
    SURAH_PAT.lastIndex = 0;
    if (SURAH_PAT.test(word)) {
      found.push(`${word}:${m[2]}`);
    }
  }
  SURAH_PAT.lastIndex = 0;
  return found;
}

function screen(content) {
  const hits = [];
  for (const pat of BLOCKED) {
    const matches = content.match(pat);
    if (matches) {
      for (const m of matches) {
        if (!hits.includes(m)) hits.push(m);
      }
    }
  }
  // Run surah verse ref whitelist guard
  hits.push(...checkSurahRefs(content));
  return hits;
}

if (!MISSION) {
  console.error('Usage: node pre_publish_screen.js <mission>');
  process.exit(2);
}

if (!fs.existsSync(FILE)) {
  console.error(`File not found: ${FILE}`);
  process.exit(2);
}

const content = fs.readFileSync(FILE, 'utf8');
const hits = screen(content);

if (hits.length === 0) {
  console.log(`Clean: ${MISSION} — no blocked references found`);
  process.exit(0);
} else {
  console.error(`BLOCKED: ${MISSION} — ${hits.length} violation(s):`);
  for (const h of hits) {
    console.error(`   -> "${h}"`);
  }
  process.exit(1);
}
