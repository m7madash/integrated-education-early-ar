#!/usr/bin/env node

/**
 * Full Arabic Religious Content Verification (Simplified)
 * Direct text matching against verified Quran/Hadith databases
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';

function normalizeArabic(text) {
  return text.replace(/[\u064B-\u065F]/g, '').replace(/[،؛؟«»]/g, '').replace(/\s+/g, ' ').trim();
}

function loadDB(filename) {
  const filepath = path.join(WORKSPACE, 'memory', filename);
  return JSON.parse(fs.readFileSync(filepath, 'utf-8'));
}

function extractQuotes(text) {
  const quotes = [];
  
  // Only look in religious section
  const religiousSection = text.match(/🕌\s*\*\*المرجعية الشرعية\*\*([\s\S]*?)(?=\n##|\Z)/);
  const searchArea = religiousSection ? religiousSection[1] : text;
  
  // Pattern: Quran with explicit Arabic quote
  // Example: القرآن: البقرة:205 — «وَإِذَا تَوَلَّىٰ سَعَىٰ...»
  const quranPattern = /القرآن:[^\n]*?—\s*«([^»]{30,400})»/g;
  let match;
  while ((match = quranPattern.exec(searchArea)) !== null) {
    quotes.push({ text: match[1], type: 'quran' });
  }
  
  // Pattern: Hadith with explicit Arabic quote + grade
  const hadithPattern = /الحديث:\s*«([^»]{20,300})»\s*\(صحيح/g;
  while ((match = hadithPattern.exec(searchArea)) !== null) {
    quotes.push({ text: match[1], type: 'hadith' });
  }
  
  return quotes;
}

function verifyAgainstDB(quote, quranDB, hadithDB) {
  const normQuote = normalizeArabic(quote.text);
  
  if (quote.type === 'quran') {
    for (const [key, verse] of Object.entries(quranDB.verses)) {
      const normVerse = normalizeArabic(verse.arabic_text);
      if (normVerse.includes(normQuote) || normQuote.includes(normVerse) || similarity(normVerse, normQuote) > 0.7) {
        return { verified: true, reference: verse.reference, type: 'quran' };
      }
    }
  } else if (quote.type === 'hadith') {
    for (const h of hadithDB.hadiths) {
      const normHadith = normalizeArabic(h.arabic_text);
      if (normHadith.includes(normQuote) || normQuote.includes(normHadith) || similarity(normHadith, normQuote) > 0.6) {
        return { verified: true, reference: h.reference, type: 'hadith' };
      }
    }
  }
  
  return { verified: false };
}

function similarity(a, b) {
  const setA = new Set(a.split(''));
  const setB = new Set(b.split(''));
  const intersection = new Set([...setA].filter(x => setB.has(x)));
  const union = new Set([...setA, ...setB]);
  return intersection.size / union.size;
}

function verify(mission, content) {
  console.log(`🔍 Verifying ${mission}...`);
  
  const quranDB = loadDB('quran_texts.json');
  const hadithDB = loadDB('hadith_texts.json');
  const quotes = extractQuotes(content);
  
  if (quotes.length === 0) {
    return { status: 'pass', reason: 'No Quran/Hadith quotes found' };
  }
  
  let passed = 0, failed = 0;
  for (const q of quotes) {
    const result = verifyAgainstDB(q, quranDB, hadithDB);
    if (result.verified) {
      passed++;
    } else {
      failed++;
      console.log(`   ❌ Unverified ${q.type}: "${q.text.substring(0, 40)}..."`);
    }
  }
  
  if (failed > 0) {
    return { status: 'flag', passed, failed, message: `${failed} quote(s) unverified` };
  }
  return { status: 'pass', passed, failed: 0 };
}

// CLI
if (require.main === module) {
  const [mission, file] = process.argv.slice(2);
  const content = fs.readFileSync(file, 'utf-8');
  const result = verify(mission, content);
  console.log(`📊 ${result.status.toUpperCase()}: ${result.passed} verified, ${result.failed || 0} failed`);
  
  // Log
  const logDir = path.join(WORKSPACE, 'memory', 'verification_logs');
  if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
  fs.writeFileSync(path.join(logDir, `full_verify_${mission}_${Date.now()}.json`), JSON.stringify({ ts: new Date().toISOString(), mission, result }, null, 2));
  
  process.exit(result.status === 'flag' ? 1 : 0);
}
