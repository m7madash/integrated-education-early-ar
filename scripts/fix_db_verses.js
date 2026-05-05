#!/usr/bin/env node
/**
 * Fix DB data: 2:177 was incorrectly stored; replace with correct text
 * Also add missing 22:37
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const WORKSPACE = '/root/.openclaw/workspace';
const DB_PATH = path.join(WORKSPACE, 'memory', 'quran_texts.json');

function normalizeArabic(text) {
  return text.replace(/[\u064B-\u065F]/g, '').replace(/[،؛؟«»]/g, '').replace(/\s+/g, ' ').trim();
}

function fetchVerse(key) {
  return new Promise((resolve, reject) => {
    https.get(`https://api.quran.com/api/v4/quran/verses/uthmani?verse_key=${key}`, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const d = JSON.parse(data);
          const v = d.verses[0];
          resolve({
            surah: v.chapter_id,
            ayah: v.verse_number,
            arabic_text: v.text_uthmani
          });
        } catch(e) { reject(e); }
      });
    }).on('error', reject);
  });
}

(async () => {
  const db = JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));
  const surahNames = {
    2:'البقرة', 3:'آل عمران', 4:'النساء', 5:'المائدة', 16:'النحل',
    17:'الإسراء', 20:'طه', 22:'الحج', 49:'الحجرات', 58:'المجادلة',
    73:'المزمل', 108:'الكوثر'
  };

  // Fix 2:177
  console.log('Fetching correct 2:177...');
  const v2_177 = await fetchVerse('2:177');
  db.verses['2:177'] = {
    surah: 2,
    ayah: 177,
    reference: `${surahNames[2]}:177`,
    arabic_text: v2_177.arabic_text,
    normalized: normalizeArabic(v2_177.arabic_text),
    used_in_missions: ['poverty-dignity']
  };
  console.log('✓ Updated 2:177');

  // Add 22:37
  if (!db.verses['22:37']) {
    console.log('Fetching 22:37...');
    const v22_37 = await fetchVerse('22:37');
    db.verses['22:37'] = {
      surah: 22,
      ayah: 37,
      reference: `${surahNames[22]}:37`,
      arabic_text: v22_37.arabic_text,
      normalized: normalizeArabic(v22_37.arabic_text),
      used_in_missions: []
    };
    console.log('✓ Added 22:37');
  }

  fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
  console.log('Done. Total verses:', Object.keys(db.verses).length);
})().catch(console.error);