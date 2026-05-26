const fs = require('fs');

const BLOCKED = [
  /\[سورة\s+\w+:\s*\d+\]/gi,
  /\[.*:\d+\]/gi,
  /صحيح\s*(البخاري|مسلم)/gi,
  /سنن\s*(الترمذي|ابن ماجة)/gi,
  /مسند\s*(أحمد)/gi,
  /موطأ\s*(مالك)/gi,
  /أبو\s+داود/gi,
  /النسائي/gi,
  /ابن\s+ماجة/gi,
  /متفق\s+عليه/gi,
  /القرآن:/gi,
  /الحديث:/gi,
  /\{[^}]+\}[^\[]*\[[^\]]+[أ-ي]+[:\s]\d+[^\]]*\]/gi,
  /الفضل\s+كله\s+لله/gi,
];

const SURAH_NAMES = ['الفاتحة','البقرة','آل عمران','النساء','المائدة','الأنعام','الأعراف','الأنفال','التوبة','يونس','هود','يوسف','الرعد','إبراهيم','الحجر','النحل','الإسراء','الكهف','مريم','طه','الأنبياء','الحج','المؤمنون','النور','الفرقان','الشعراء','النمل','القصص','العنكبوت','الروم','لقمان','السجدة','الأحزاب','سبأ','فاطر','يس','الصافات','ص','الزمر','غافر','فصلت','الشورى','الزخرف','الدخان','الجاثية','الأحقاف','محمد','الفتح','الحجرات','ق','الذاريات','الطور','النجم','القمر','الرحمن','الواقعة','الحديد','المجادلة','الحشر','الممتحنة','الصف','الجمعة','المنافقون','التغابن','الطلاق','التحريم','الملك','القلم','الحاقة','المعارج','نوح','الجن','المزمل','المدثر','القيامة','الإنسان','المرسلات','النبأ','النازعات','عبس','التكوير','الانفطار','المطففين','الانشقاق','البروج','الطارق','الأعلى','الغاشية','الفجر','البلد','الشمس','الليل','الضحى','الشرح','التين','العلق','القدر','البينة','الزلزلة','العاديات','القارعة','التكاثر','العصر','الهمزة','الفيل','قريش','الماعون','الكوثر','الكافرون','النصر','المسد','الإخلاص','الفلق','الناس'];
const SURAH_PAT = new RegExp(SURAH_NAMES.map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'), 'g');

const dir = 'missions_combined';
const files = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
let clean = 0, bad = 0;

for (const f of files) {
  const path = dir + '/' + f;
  const content = fs.readFileSync(path, 'utf8');
  const hits = [];
  for (const pat of BLOCKED) {
    pat.lastIndex = 0;
    const matches = content.match(pat);
    if (matches) matches.forEach(m => { if (!hits.includes(m)) hits.push(m); });
  }
  // inline bare surah:ayah
  const bareRef = /(?:^|[\s\u00A0\u202F،؛.!؟()\[\-])([\u0600-\u06FF]{2,15})\s*:\s*(\d+)/g;
  let m;
  while ((m = bareRef.exec(content)) !== null) {
    SURAH_PAT.lastIndex = 0;
    if (SURAH_PAT.test(m[1].trim())) hits.push(m[1].trim() + ':' + m[2]);
  }
  SURAH_PAT.lastIndex = 0;

  if (hits.length === 0) {
    console.log('✅ Clean: ' + f + ' (' + content.length + ' bytes)');
    clean++;
  } else {
    console.error('❌ BLOCKED: ' + f + ' — ' + hits.length + ' violation(s)');
    hits.forEach(h => console.error('   -> "' + h + '"'));
    bad++;
  }
}
console.log('\nSummary: ' + clean + ' clean, ' + bad + ' blocked');
process.exit(bad > 0 ? 1 : 0);
