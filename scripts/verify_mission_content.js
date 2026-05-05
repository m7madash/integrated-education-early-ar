#!/usr/bin/env node
/**
 * Quick verification: check if mission Quran quotes match DB
 */
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/root/.openclaw/workspace';
const DB_PATH = path.join(WORKSPACE, 'memory', 'quran_texts.json');

function normalizeArabic(text) {
  return text.replace(/[\u064B-\u065F]/g, '').replace(/[،؛؟«»]/g, '').replace(/\s+/g, ' ').trim();
}

function extractQuotes(text) {
  const quotes = [];
  const religiousSection = text.match(/🕌\s*\*\*المرجعية الشرعية\*\*([\s\S]*?)(?=\n##|\Z)/);
  const searchArea = religiousSection ? religiousSection[1] : text;
  const quranPattern = /القرآن:[^\n]*?—\s*«([^»]{30,400})»/g;
  let match;
  while ((match = quranPattern.exec(searchArea)) !== null) {
    quotes.push({ text: match[1], type: 'quran' });
  }
  const hadithPattern = /الحديث:\s*«([^»]{20,300})»\s*\(صحيح/g;
  while ((match = hadithPattern.exec(searchArea)) !== null) {
    quotes.push({ text: match[1], type: 'hadith' });
  }
  return quotes;
}

const db = JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));

const missions = process.argv.slice(2);
if (missions.length === 0) {
  console.log('Usage: verify_mission_content.js <mission_file>...');
  process.exit(1);
}

let allPassed = true;

for (const missionFile of missions) {
  const filePath = path.join(WORKSPACE, missionFile);
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️  File not found: ${missionFile}`);
    continue;
  }
  const content = fs.readFileSync(filePath, 'utf-8');
  const quotes = extractQuotes(content);
  console.log(`\n=== ${missionFile} ===`);
  
  if (quotes.length === 0) {
    console.log('  No Quran/Hadith quotes found');
    continue;
  }
  
  for (const q of quotes) {
    const normQuote = normalizeArabic(q.text);
    let matched = null;
    for (const [key, verse] of Object.entries(db.verses)) {
      const normVerse = normalizeArabic(verse.arabic_text);
      if (normVerse.includes(normQuote) || normQuote.includes(normVerse)) {
        matched = { key, reference: verse.reference };
        break;
      }
    }
    if (matched) {
      console.log(`  ✓ MATCH: ${matched.reference}`);
    } else {
      console.log(`  ✗ UNVERIFIED: "${q.text.substring(0,60)}..."`);
      allPassed = false;
    }
  }
}

process.exit(allPassed ? 0 : 1);