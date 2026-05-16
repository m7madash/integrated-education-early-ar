#!/usr/bin/env node
const fs = require('fs');
const BUKHARI_PATH = '/root/.openclaw/workspace/data/sahih_bukhari.json';
const args = process.argv.slice(2);
if (args.length < 3) {
  console.error('⛔ Usage: node sunnah_fetcher.js <source> <book> <hadith_num>');
  process.exit(1);
}
const [source, book, hadithNum] = args;
let hadiths;
try { hadiths = JSON.parse(fs.readFileSync(BUKHARI_PATH, 'utf8')); } catch (e) {
  console.error('⛔ Hadith DB not found at', BUKHARI_PATH); process.exit(1);
}
const found = hadiths.find(h => 
  h.collection === source && 
  h.book === book && 
  h.number === parseInt(hadithNum)
);
if (!found) { console.error(`⛔ Hadith not found: ${source} ${book} ${hadithNum}`); process.exit(1); }
console.log(found.text_arabic);
