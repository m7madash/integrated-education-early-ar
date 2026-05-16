#!/usr/bin/env node
const fs = require('fs');
const PATH = '/root/.openclaw/workspace/data/quran_uthmani.json';
const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('⛔ Usage: node quran_reader.js <surah> [verse-range]');
  process.exit(1);
}
const surahNum = parseInt(args[0]);
const verseArg = args[1];
let quranData;
try { quranData = JSON.parse(fs.readFileSync(PATH, 'utf8')); } catch (e) {
  console.error('⛔ Quran DB not found at', PATH); process.exit(1);
}
const quran = quranData.verses;
// فلترة السورة من verse_key (surah:verse)
const surahAyahs = quran.filter(a => {
  const [chap, verseNum] = a.verse_key.split(':').map(Number);
  return chap === surahNum;
});
if (!surahAyahs.length) { console.error(`⛔ Surah ${surahNum} not found`); process.exit(1); }
let output = [];
if (verseArg && verseArg.includes('-')) {
  const [start, end] = verseArg.split('-').map(Number);
  output = surahAyahs.filter(a => {
    const verseNum = parseInt(a.verse_key.split(':')[1]);
    return verseNum >= start && verseNum <= end;
  });
} else if (verseArg) {
  const ayah = surahAyahs.find(a => a.verse_key === `${surahNum}:${verseArg}`);
  output = ayah ? [ayah] : [];
} else { output = surahAyahs; }
output.forEach(a => {
  console.log(`${a.text_uthmani}\n— سورة ${a.verse_key.split(':')[0]}:${a.verse_key.split(':')[1]}`);
});
