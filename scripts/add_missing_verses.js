#!/usr/bin/env node
/**
 * Add missing Quran verses to quran_texts.json
 * Fetches verified text from quran.com API (uthmani script)
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
            key,
            surah: v.chapter_id,
            ayah: v.verse_number,
            arabic_text: v.text_uthmani
          });
        } catch(e) { reject(e); }
      });
    }).on('error', reject);
  });
}

  const surahNames = {
    1:'الفاتحة',2:'البقرة',3:'آل عمران',4:'النساء',5:'المائدة',
    6:'الأنعام',7:'الأعراف',8:'الأنفال',9:'التوبة',10:'يونس',
    11:'هود',12:'يوسف',13:'الرعد',14:'إبراهيم',15:'الحجر',
    16:'النحل',17:'الإسراء',18:'الكهف',19:'مريم',20:'طه',
    21:'الأنبياء',22:'الحج',23:'المؤمنون',24:'النور',25:'الفرقان',
    26:'الشعراء',27:'النمل',28:'القصص',29:'العنكبوت',30:'الروم',
    31:'لقمان',32:'السجدة',33:'الأحزاب',34:'سبأ',35:'فاطر',
    36:'يس',37:'الصافات',38:'ص',39:'الزمر',40:'غافر',
    41:'فصلت',42:'الشورى',43:'الزخرف',44:'الدخان',45:'الجاثية',
    46:'الأحقاف',47:'محمد',48:'الفتح',49:'الحجرات',50:'ق',
    51:'الذاريات',52:'الطور',53:'النجم',54:'القمر',55:'الرحمن',
    56:'الواقعة',57:'الحديد',58:'المجادلة',59:'الحشر',60:'الممتحنة',
    61:'الصف',62:'الجمعة',63:'المنافقون',64:'التغابن',65:'الطلاق',
    66:'تحريم',67:'الملك',68:'القلم',69:'الحاقة',70:'المعارج',
    71:'نوح',72:'الجن',73:'المزمل',74:'المدثر',75:'القيامة',
    76:'الإنسان',77:'المرسلات',78:'النبأ',79:'النازعات',80:'عبس',
    81:'التكوير',82:'الإنفطار',83:'المطففين',84:'الانشقاق',85:'البروج',
    86:'الطارق',87:'الأعلى',88:'الغاشية',89:'الفجر',90:'البلد',
    91:'الشمس',92:'الليل',93:'الضحى',94:'الشرح',95:'التين',
    96:'العلق',97:'القدر',98:'البينة',99:'الزلزال',100:'العاديات',
    101:'القارعة',102:'التكاثر',103:'العصر',104:'الهمزة',105:'الفيل',
    106:'قريش',107:'الماعون',108:'الكوثر',109:'الكافرون',110:'النصر',
    111:'المسد',112:'الإخلاص',113:'الفلق',114:'الناس'
  };

  (async () => {
    const db = JSON.parse(fs.readFileSync(DB_PATH, 'utf-8'));
    const missingKeys = [
      '3:191', '17:70', '108:1', '22:46', '2:197',
      '17:36', '4:48', '4:116', '73:8', '58:14'
    ];

    for (const key of missingKeys) {
      if (db.verses[key]) {
        console.log(`✓ ${key} already exists`);
        continue;
      }
      try {
        const v = await fetchVerse(key);
        const entry = {
          surah: v.surah,
          ayah: v.ayah,
          reference: `${surahNames[v.surah]}:${v.ayah}`,
          arabic_text: v.arabic_text,
          normalized: normalizeArabic(v.arabic_text),
          used_in_missions: []
        };
        db.verses[key] = entry;
        console.log(`✓ Added ${key} (${entry.reference})`);
      } catch(e) {
        console.error(`✗ Failed ${key}:`, e.message);
      }
    }

    fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
    console.log('DB updated - total verses:', Object.keys(db.verses).length);
  })().catch(console.error);