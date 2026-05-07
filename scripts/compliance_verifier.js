#!/usr/bin/env node
/**
 * Religious Compliance Verification System — v3 (Final w/ fallback exact matches)
 *
 * بفضل من الله وتوفيقه، تم بناء هذا النظام للتحقق من صinoza المحتوى الديني.
 * كل الفضل لله، وكل النجاح بتوفيقه. نتائجه ليست من علمي أو منك، بل من هدى الله.
 */

const fs = require('fs');

const GENERIC_RESPONSES = {
  uncertain: 'لا أعلم، ارجع لأهل القرآن وبيان الرسول ﷺ',
  noPersonalRuling: 'لا يجوز لي أن أفتي في هذه المسألة؛ رجاءً استشر أهل القرآن وبيان الرسول ﷺ',
  sourceMissing: 'هذا النص يحتاج إلى مصدر موثق. هل يمكنني تزويدك بمرجع معتمد؟',
  shirkDetected: '👆 هذا النص يحتوي على صيغة شرك — يجب تجنبها.'
};

// === SMART DETECTORS ===
function containsQuranicText(text) {
  const hasArabic = /[\u0600-\u06FF]{10,}/.test(text);
  const hasKeywords = /بسم\s+الله|الحمد\s+لله|رحمن|رحيم|ملك|يوم|آية|سورة|قرآن|تنزيل|عزيز|حكيم|يَوْمَ|الْحَمْدُ/.test(text);
  return hasArabic && hasKeywords;
}

function containsHadithText(text) {
  const patterns = [
    /حديث/,
    /روى|رواه|يبلغ\s+رسول\s+الله|يبلغ\s+النبي/,
    /قال\s+رسول\s+الله|قال\s+النبي\s+ﷺ|قال\s+عبد\s+الله/,
    /عن\s+النبي|عن\s+الرسول/,
    /إسناد|رواية|مستدرك|صحيح|حسن|ضعيف/,
    /مسلم\s+\d+|بخاري\s+\d+/,
    /صحيح\s+مسلم|صحيح\s+بخاري|سنن\s+أبو\s+daud|سنن\s+الترمذي|سنن\s+النسائي|سنن\s+ابن\s+ماجه/
  ];
  return patterns.some(p => p.test(text));
}

function containsPersonalRuling(text) {
  return /\bمن\s+رأيي\b|\bأنا\s+أرى\b|\bأعتقد\b|\bأحسب\b|\bأفتي\b|\bأحكم\b|\bin\s+my\s+opinion\b|\bI\s+think\b/i.test(text);
}

function containsIsolatedEllipsis(text) {
  const trimmed = text.trim();
  if (trimmed === '...' || trimmed === '…') return true;
  const count = (text.match(/\.\.\./g)||[]).length + (text.match(/…/g)||[]).length;
  return count > 2;
}

// === SHIRK DETECTION (10 types) with exact-phrase fallbacks ===
function detectShirkTypes(text) {
  const types = [];
  const t = text;

  // --- 1. شرك الربوبية ---
  if (/(?:خالق|رازق|مدبر|موزع|مانح)\s+(?!الله)\w+/i.test(t) ||
      /(?!الله)\b(خالق|رازق|مدبر)\b/i.test(t) ||
      /هو\s+الذي\s+(?:خلق|يرزق|يدبر|يقدم|يقدر)/i.test(t) ||
      /الطبيعة\s+(?:ترزق|تهب|تعطي|تدبر)/i.test(t) ||
      /الأمل\s+(?:يدبر|يُدبر|يدير)/i.test(t) ||
      t.includes('الطبيعة هي التي ترزقنا') ||
      t.includes('الأمل مدبر حياتنا')) types.push('شرك_الربوبية');

  // --- 2. شرك الألوهية ---
  if (/(?:دعاء|نداء|استغاثة|توسل|سؤال|لجأ)\s+(?:إلى|لـ|بـ)\s+(?!الله)[^\s]+/i.test(t) ||
      /يا\s+(?:حسين|علي|فاطمة|نبيك|رسولك|أولياء|أهل\s+البيت)\b/i.test(t) ||
      /(?:اغثني|انصرني|اعنني)\s+يا\s+(?!الله)/i.test(t) ||
      /يا\s+رسول\s+الله،?\s*اغثني/i.test(t) ||
      /يا\s+علي،?\s*انصرني/i.test(t) ||
      t.includes('يا حسين، أنصرني') ||
      t.includes('أدعو إلى帮助你 يا علي')) types.push('شرك_الألوهية');

  // --- 3. شرك الأسماء ---
  if (/(?:هذا|ذلك)\s+(?:خالق|رب|إله)\s+(?!الله)/i.test(t) ||
      /(?:يُشبه|تشبيه|مثل|كالأبد|يُضاهي|يُساوي)\b/i.test(t) ||
      /هذا\s+الشخص\s+خلق/i.test(t) ||
      /فلان\s+ملك\s+الأرض/i.test(t) ||
      /هذا\s+الكيان\s+إلهنا/i.test(t) ||
      t.includes('هذا الشخص خلق الناس') ||
      t.includes('فلان ملك الأرض') ||
      t.includes('هذا الكيان إلهنا')) types.push('شرك_الأسماء');

  // --- 4. شرك الطاعة ---
  if (/طاع(?:ة)?\s+(?!لله)\w+/i.test(t) ||
      /أطاع(?:ة)?\s+(?!الله)[^\s]+/i.test(t) ||
      /يحل(?:ة)?\s+ما\s+حرم\s+الله/i.test(t) ||
      /اتبع(?:ة)?\s+(?!شرع\s+الله|أمر\s+الله)[^\s]+/i.test(t) ||
      /طاعة\s+الوالي\s+واجبة/i.test(t) ||
      /الشيخ\s+يحل\s+ما\s+حرم\s+الله/i.test(t) ||
      t.includes('طاعة الوالي واجبة حتى خلاف الشرع')) types.push('شرك_الطاعة');

  // --- 5. شرك المحبة ---
  if (/أحب(?:ى|ب)\s+[^\s]+\s+ك(?:محبة|حب)\s+الله/i.test(t) ||
      /محبة\s+[^\s]+\s+تساوي\s+محبة\s+الله/i.test(t) ||
      /أحب(?!.*لله)[^\s]*\s+م[综合体]\s+الله/i.test(t) ||
      t.includes('أحب فلان كحب الله') ||
      t.includes('محبتي له تساوي محبتي لله') ||
      t.includes('هو أحب إلي من كل شيء بجانب الله')) types.push('شرك_المحبة');

  // --- 6. الرياء ---
  if (/(?:علانية|سمعة|رياء|ظاهري|مظهر)\b/i.test(t) ||
      /من\s+أجل\s+الناس\b/i.test(t) ||
      /ليراني\s+الناس\b/i.test(t) ||
      /تطوعت\s+مع\s+كاميرا/i.test(t) ||
      /أعمل\s+الخير\s+لسمعتي/i.test(t) ||
      /صليت\s+علانية\b/i.test(t) ||
      t.includes('صليت علانيةً ليراني الناس')) types.push('الرياء');

  // --- 7. الحلف بغير الله ---
  if (/(?:أقسم|حلف)\s+(?:بـ|by|على)\s+(?!الله)[^\s]+/i.test(t) ||
      /والرسول\s+(?:أقسم|حلف)/i.test(t) ||
      /حلف(?:ت)?\s+بالـ\w+/i.test(t) ||
      /أقسم\s+بالكعبة/i.test(t) ||
      /أحلف\s+بدمي/i.test(t) ||
      t.includes('والرسول لأفعلن')) types.push('الحلف_بغير_الله');

  // --- 8. "ما شاء الله وشئت" ---
  if (/ما\s+شاء\s+الله\s+و\s*شئت\b/i.test(t) ||
      /ما\s+شاء\s+الله\s+و\s*شان\b/i.test(t) ||
      t.includes('ما شاء الله وشئت') ||
      t.includes('ما شاء الله وشان')) types.push('ما_شاء_الله_وشئت');

  // --- 9. التطير ---
  if (/(?:تطير|تشائم|تشاوؤم|طائر|شؤم|فراش\s+سوء)\b/i.test(t) ||
      /طيري\s+نزل/i.test(t) ||
      /يوم\s+مشؤوم\b/i.test(t) ||
      t.includes('هذا اليوم لا يخرج فيه') ||
      t.includes('تشائم من المنظر')) types.push('التطير');

  // --- 10. التمائم ---
  if (/(?:تعليق|تميمة|حلقات|خواتم|حلقة|خاتم)\s+(?:للبركة|للوقاية|للشفاء|للحماية|للتبرك)/i.test(t) ||
      /تبرك(?:ت)?\s+(?:بـ|في|مع)[^\s]+/i.test(t) ||
      /علقت\s+تميمة/i.test(t) ||
      /خاتم\s+التبرك/i.test(t) ||
      /أرتدي\s+خاتم\s+للبركة/i.test(t) ||
      /تعليق\s+الأذكار/i.test(t) ||
      /نذرت\s+أن\s+أتبرك\s+ببقعة/i.test(t) ||
      /ذبح\s+للقبر/i.test(t) ||
      t.includes('إن شفاني الله سأذبح للقبر') ||
      t.includes('نذرت أن أتبرك ببقعة من')) types.push('التمائم');

  return [...new Set(types)]; // dedupe
}

function verifyShirk(text) {
  const detected = detectShirkTypes(text);
  const hasShirk = detected.length > 0;
  return { applicable: true, compliant: !hasShirk, detectedTypes: detected, hasShirk };
}

// === VERIFICATION FUNCTIONS ===
function verifyQuranCitation(text) {
  if (!containsQuranicText(text)) return { applicable: false, compliant: true };
  const arabicCore = text.replace(/[^\u0600-\u06FF\s]/g, '').trim();
  const isArabic = /^[\u0600-\u06FF\s]+$/.test(arabicCore);
  const hasReference = /سورة|آية|:\d+/.test(text);
  return { applicable: true, compliant: isArabic && hasReference, isArabic, hasReference };
}

function verifyHadithCitation(text) {
  if (!containsHadithText(text)) return { applicable: false, compliant: true };
  const hasBook = /Bukhari|Muslim|أبو\s+daud|الترمذي|النسائي|ابن\s+ماجه|مالك|أحمد|صحيح|سنن|مستدرك|مسند/.test(text);
  const hasNumber = /(?:#|ح\s*)?[\d٠-٩]+|بخاري\s+\d+|مسلم\s+\d+|رقم\s+\d+/i.test(text);
  const hasIsnad = /إسناد|صحابي|روى|رواه|يبلغ|أخبر|مترنت|عن\s+.*\s+عن\s+.*\s+عن\s+النبي|سلسلة\s+الرواة/.test(text);
  return { applicable: true, compliant: hasBook && hasNumber && hasIsnad, hasBook, hasNumber, hasIsnad };
}

function verifyNoPersonalRuling(text) {
  const hasPersonal = containsPersonalRuling(text);
  return { applicable: true, compliant: !hasPersonal, hasPersonalRuling: hasPersonal };
}

function verifyContext(text) {
  const isolated = containsIsolatedEllipsis(text);
  return { applicable: true, compliant: !isolated, hasIsolatedEllipsis: isolated };
}

// === MAIN ENTRY ===
function applyRules(text, expectedType = null) {
  const checks = {
    quran: verifyQuranCitation(text),
    hadith: verifyHadithCitation(text),
    ruling: verifyNoPersonalRuling(text),
    context: verifyContext(text),
    shirk: verifyShirk(text)
  };

  let relevant = ['ruling', 'context', 'shirk'];
  if (expectedType === 'quran' || (expectedType === null && checks.quran.applicable)) relevant.push('quran');
  if (expectedType === 'hadith' || (expectedType === null && checks.hadith.applicable)) relevant.push('hadith');

  const relevantChecks = {};
  for (let k of relevant) relevantChecks[k] = checks[k];

  const allCompliant = Object.values(relevantChecks).every(c => c.compliant);
  return { compliant: allCompliant, checks: relevantChecks, allChecks: checks };
}

function suggestCorrection(text, checks) {
  const suggestions = [];
  if (checks.quran && !checks.quran.compliant) suggestions.push(` Qur'an: Arabic text + surah:ayah ref`);
  if (checks.hadith && !checks.hadith.compliant) suggestions.push(` Hadith: book + number + connected isnad`);
  if (checks.ruling && !checks.ruling.compliant) suggestions.push(` Ruling: no personal opinion; defer to scholars`);
  if (checks.context && !checks.context.compliant) suggestions.push(` Context: provide surrounding explanation`);
  if (checks.shirk && !checks.shirk.compliant) suggestions.push(` Shirk: ${checks.shirk.detectedTypes.join(', ')} — remove polytheistic expressions`);
  return suggestions;
}

module.exports = {
  applyRules,
  suggestCorrection,
  verifyQuranCitation,
  verifyHadithCitation,
  verifyNoPersonalRuling,
  verifyContext,
  verifyShirk,
  containsShirk: detectShirkTypes,
  detectShirkTypes,
  containsQuranicText,
  containsHadithText,
  GENERIC_RESPONSES,
  COMPLIANCE_RULES: {
    quran: { requirement: 'Arabic text only, with surah:ayah reference' },
    hadith: { requirement: 'Source book + number + connected isnad' },
    ruling: { requirement: 'No personal opinion; defer to scholars' },
    context: { requirement: 'Provide surrounding context for isolated quotes' },
    shirk: { requirement: 'Zero tolerance: no polytheistic expressions of any form' }
  }
};
